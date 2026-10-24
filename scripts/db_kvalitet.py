"""Databasekvalitet i klartekst (0 tokens, deterministisk, bare lesing).

Sjekker 05_data/museum.db slik den ligger nå, og forklarer hvert funn på vanlig norsk:
hva det betyr og hva du eventuelt gjør. Åpnes automatisk av VS Code (.vscode/tasks.json).

Kjøres med:
    py -3.13 scripts/db_kvalitet.py              # sjekk museum.db
    py -3.13 scripts/db_kvalitet.py --db <sti>   # sjekk en annen database
    py -3.13 scripts/db_kvalitet.py --uten-bygg  # hopp over «er den bygget fra gjeldende kode?» (sparer 3 s)

Exit 0 = ingen feil (advarsler kan finnes). Exit 1 = minst én feil.
Databasen åpnes alltid med mode=ro. Skriptet bygger ingenting til museum.db.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import db_status_gate as port

from src.kunstpixel.data import build_museum_db as bygger

OK, ADVARSEL, FEIL = port.OK, port.ADVARSEL, port.FEIL

# Hvert funn: hva det betyr (BETYR) og hva du gjør (GJOR). Nøkkelen er regelnavnet i db_status_gate.
FORKLARING: dict[str, tuple[str, str]] = {
    "vakt på dag med eget fravær": (
        "Noen står på vakt en dag de er sykmeldt eller har egenmelding.",
        "Rett vakten eller fraværet i datafilene (05_data/*.csv) og bygg databasen på nytt.",
    ),
    "vakt utenfor ansettelsesperioden": (
        "Noen har en vakt før de ble ansatt eller etter at de sluttet.",
        "Rett datoene i datafilene og bygg på nytt.",
    ),
    "samme person på to vakter samtidig": (
        "En ansatt er satt opp på to vakter som overlapper i tid.",
        "Fjern den ene vakten i datafilene og bygg på nytt.",
    ),
    "for kort hviletid mellom vakter": (
        "Noen har mindre enn 11 timer fri mellom to vakter. Det er ulovlig etter arbeidsmiljøloven § 10-8.",
        "Rett vaktene i datagenerator eller datafil og bygg på nytt. Kjente tilfeller står i KJENTE_BRUDD i db_status_gate.py.",
    ),
    "kurs som utløper før det er tatt": (
        "Et kurs har utløpsdato før datoen det ble tatt. Det er umulig.",
        "Rett datoene i 05_data/mock_ansatt_kompetanser.csv og bygg på nytt.",
    ),
    "fravær som slutter før det begynner": (
        "Et fravær har sluttdato før startdato.",
        "Rett datoene i 05_data/arkiv_hr_fravaer.csv og bygg på nytt.",
    ),
    "vakter over døgnmaks (overtid eller feil?)": (
        "Vakter lengre enn 9 timer. Loven tillater det som overtid, men dataene merker dem ikke som overtid.",
        "Du må avgjøre: er de overtid (merk dem), eller en datafeil (rett dem)? Maskinen kan ikke velge.",
    ),
}

NIVAIKON = {OK: "[ OK ]", ADVARSEL: "[ OBS ]", FEIL: "[FEIL ]"}

# Hvilken fil du rette i når en sjekk slår til. Brukes til Problems-panelet i VS Code (klikk på funnet = åpner filen).
BYGGESKRIPT = "src/kunstpixel/data/build_museum_db.py"
FIL_FOR_FUNN: dict[str, str] = {
    "Databasen er hel": BYGGESKRIPT,
    "Riktig skjemaversjon": BYGGESKRIPT,
    "Filen er urørt": "05_data/museum.db.sha256",
    "Bygget fra gjeldende kode": BYGGESKRIPT,
    "Alt er merket syntetisk": BYGGESKRIPT,
    "vakt på dag med eget fravær": "05_data/arkiv_hr_fravaer.csv",
    "vakt utenfor ansettelsesperioden": "05_data/arkiv_hr_vakt_klokkeslett.csv",
    "samme person på to vakter samtidig": "05_data/arkiv_hr_vakt_klokkeslett.csv",
    "for kort hviletid mellom vakter": "05_data/arkiv_hr_vakt_klokkeslett.csv",
    "kurs som utløper før det er tatt": "05_data/mock_ansatt_kompetanser.csv",
    "fravær som slutter før det begynner": "05_data/arkiv_hr_fravaer.csv",
    "vakter over døgnmaks (overtid eller feil?)": "05_data/arkiv_hr_vakt_klokkeslett.csv",
}


def problemlinjer(resultat: list[tuple[str, str, str, str]]) -> list[str]:
    """Én linje per funn som ikke er OK: PROBLEM|error/warning|fil|linje|melding. VS Code leser dem inn i Problems-panelet."""
    linjer = []
    for navn, niva, hva, tiltak in resultat:
        if niva == OK:
            continue
        melding = " ".join(f"{navn}: {hva} Gjør dette: {tiltak}".split())
        linjer.append(f"PROBLEM|{'error' if niva == FEIL else 'warning'}|{FIL_FOR_FUNN.get(navn, BYGGESKRIPT)}|1|{melding}")
    return linjer


def _ro(sti: Path) -> sqlite3.Connection:
    return sqlite3.connect(sti.resolve().as_uri() + "?mode=ro", uri=True)


def sjekk_integritet(con: sqlite3.Connection) -> tuple[str, str, str]:
    integ = con.execute("PRAGMA integrity_check").fetchone()[0]
    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    if integ == "ok" and not fk:
        return OK, "Databasen er hel og alle koblinger mellom tabeller peker på noe som finnes.", ""
    return (FEIL, f"Databasen har skade eller {len(fk)} brutte koblinger mellom tabeller.",
            "Bygg databasen på nytt. Hjelper det ikke, si fra til den som drifter.")


def sjekk_skjemaversjon(con: sqlite3.Connection) -> tuple[str, str, str]:
    versjon = con.execute("PRAGMA user_version").fetchone()[0]
    if versjon == bygger.SKJEMAVERSJON:
        return OK, f"Databasen har samme skjemaversjon ({versjon}) som koden.", ""
    return (FEIL, f"Databasen har versjon {versjon}, men koden forventer {bygger.SKJEMAVERSJON}. "
                  "Nye tabeller eller kolonner mangler.",
            "Bygg databasen: py -3.13 src/kunstpixel/data/build_museum_db.py")


def sjekk_sha(sti: Path) -> tuple[str, str, str]:
    sha_fil = sti.with_name("museum.db.sha256")
    if not sha_fil.is_file() or sti.name != "museum.db":
        return OK, "Ingen sha256-fil å sammenligne med for denne databasen.", ""
    forventet = sha_fil.read_text(encoding="utf-8").split()[0]
    faktisk = bygger.sha256(sti)
    if forventet == faktisk:
        return OK, "Databasefilen er uendret siden den ble bygget (fingeravtrykket stemmer).", ""
    return (FEIL, "Databasefilen er endret etter at den ble bygget (fingeravtrykket stemmer ikke).",
            "Noen har rørt filen direkte. Bygg på nytt, og endre bare datafilene, aldri databasen.")


def sjekk_bygget_fra_gjeldende(sti: Path) -> tuple[str, str, str]:
    with tempfile.TemporaryDirectory(prefix="kunstpixel-kvalitet-") as t:
        ny = Path(t) / "museum.db"
        bygger.bygg(ny)
        like = bygger.sha256(ny) == bygger.sha256(sti)
    if like:
        return OK, "Databasen er identisk med det som bygges fra gjeldende kode og datafiler.", ""
    return (ADVARSEL, "Databasen er ikke lik det som bygges fra gjeldende kode og datafiler. "
                      "Noen har endret kode eller data uten å bygge på nytt.",
            "Bygg på nytt: py -3.13 src/kunstpixel/data/build_museum_db.py")


def sjekk_merking(con: sqlite3.Connection) -> tuple[str, str, str]:
    port.resultater.clear()
    with contextlib.redirect_stdout(io.StringIO()):  # statusporten skriver sine egne linjer, dem vil vi ikke ha her
        port.sjekk_merking(con)
    _, niva, detalj = port.resultater[-1]
    if niva == OK:
        return OK, f"Alle data er merket som syntetiske ({detalj}).", ""
    return (FEIL, f"Noe er ikke merket som syntetisk: {detalj}",
            "Alle nye data skal ha datakilde som starter med «syntetisk» (AGENTS.md §7).")


def sjekk_regler(con: sqlite3.Connection) -> list[tuple[str, str, str, str]]:
    ut = []
    for navn, niva, nye, kjente in port.regelbrudd(con):
        betyr, gjor = FORKLARING.get(navn, ("(ingen forklaring skrevet for denne regelen)", "Se db_status_gate.py."))
        if nye:
            ut.append((navn, niva, f"{len(nye)} brudd. {betyr} Eksempler: {', '.join(nye[:3])}.", gjor))
        elif kjente:
            ut.append((navn, ADVARSEL, f"{len(kjente)} kjente brudd, ingen nye. {betyr}", gjor))
        else:
            ut.append((navn, OK, "Ingen brudd.", ""))
    return ut


def kjor(sti: Path, med_bygg: bool = True) -> list[tuple[str, str, str, str]]:
    """Alle sjekker som (navn, nivå, hva, tiltak). Brukes av skriptet og av testene."""
    con = _ro(sti)
    try:
        resultat = [
            ("Databasen er hel", *sjekk_integritet(con)),
            ("Riktig skjemaversjon", *sjekk_skjemaversjon(con)),
            ("Filen er urørt", *sjekk_sha(sti)),
            ("Alt er merket syntetisk", *sjekk_merking(con)),
            *sjekk_regler(con),
        ]
    finally:
        con.close()
    if med_bygg:
        resultat.insert(3, ("Bygget fra gjeldende kode", *sjekk_bygget_fra_gjeldende(sti)))
    return resultat


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=bygger.OUT_DB)
    ap.add_argument("--uten-bygg", action="store_true")
    ap.add_argument("--problems", action="store_true", help="skriv også PROBLEM-linjer til Problems-panelet i VS Code")
    args = ap.parse_args()
    if not args.db.is_file():
        print(f"Fant ikke databasen: {args.db}\nBygg den: py -3.13 src/kunstpixel/data/build_museum_db.py")
        return 1

    resultat = kjor(args.db, med_bygg=not args.uten_bygg)
    feil = [r for r in resultat if r[1] == FEIL]
    obs = [r for r in resultat if r[1] == ADVARSEL]

    print(f"DATABASEKVALITET  {args.db}")
    print("=" * 70)
    if feil:
        print(f"RESULTAT: {len(feil)} FEIL må rettes før databasen kan brukes. {len(obs)} ting å se på.")
    elif obs:
        print(f"RESULTAT: I orden, men {len(obs)} ting du bør ta stilling til.")
    else:
        print("RESULTAT: Alt er i orden.")
    print("=" * 70)
    for navn, niva, hva, tiltak in resultat:
        print(f"\n{NIVAIKON[niva]} {navn}")
        print(f"         {hva}")
        if tiltak and niva != OK:
            print(f"         Gjør dette: {tiltak}")
    print()
    if args.problems:
        for linje in problemlinjer(resultat):
            print(linje)
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(main())
