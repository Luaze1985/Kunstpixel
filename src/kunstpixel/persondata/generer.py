"""Bygger persondata.db med syntetiske kundedata for Kunstpixel.

To måter:
- Generer fra innstillingene (standard). Skriver både databasen og én CSV per tabell.
- `--fra-csv`: bygger databasen fra CSV-filene. Bruk dette etter at du har
  justert data for hånd i en CSV, så endringene dine blir med.

Eksempler (Windows/PowerShell):
    py -3.13 -m src.kunstpixel.persondata.generer
    py -3.13 -m src.kunstpixel.persondata.generer --overskriv
    py -3.13 -m src.kunstpixel.persondata.generer --fra-csv --overskriv
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from faker import Faker

from src.kunstpixel.persondata import ansattkilde, config
from src.kunstpixel.persondata.kunder import generer_kunder

CSV_SKILLETEGN = ";"  # norsk Excel bruker semikolon
CSV_KODING = "utf-8-sig"  # BOM gjør at Excel viser æøå riktig

# Rekkefølgen tar hensyn til fremmednøkler.
TABELLREKKEFOLGE = [
    "medlemskapstyper", "fordeler", "medlemskapstype_fordel", "kontakter", "medlemskap",
    "medlemsbesok", "fordel_bruk", "gavekort", "gavekort_bruk", "arrangementer",
    "pameldinger", "skolebestillinger", "utleie", "henvendelser",
]


DATOKOLONNER = {
    "opprettet", "samtykke_dato", "trukket_dato", "siste_aktivitet", "startdato", "sluttdato",
    "dato", "utstedt", "gyldig_til", "registrert",
}
_ISO_DATO = re.compile(r"\d{4}-\d{2}-\d{2}")
_ISO_TID = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
_TELEFON = re.compile(r"0\d{7}")


class CsvFeil(ValueError):
    """En verdi i en CSV-fil har feil format. Meldingen sier fil, rad og kolonne."""


def _katalog() -> dict[str, list[dict]]:
    dk = config.DATAKILDE
    return {
        "medlemskapstyper": [
            {"type": t, "aarspris": v["aarspris"], "datakilde": dk} for t, v in config.MEDLEMSKAPSTYPER.items()
        ],
        "fordeler": [
            {"fordel": f, "beskrivelse": v["beskrivelse"], "datakilde": dk} for f, v in config.FORDELER.items()
        ],
        "medlemskapstype_fordel": [
            {"type": t, "fordel": f, "datakilde": dk} for f, v in config.FORDELER.items() for t in v["typer"]
        ],
    }


def _sjekk_overskriving(sti: Path, csv_dir: Path | None, overskriv: bool) -> None:
    if overskriv:
        return
    csv_finnes = csv_dir is not None and csv_dir.is_dir() and any(csv_dir.glob("*.csv"))
    if csv_finnes and not sti.exists():
        raise FileExistsError(
            f"CSV-filene i {csv_dir} finnes allerede, men databasen mangler. "
            "Bygg databasen fra dem med --fra-csv. "
            "(Bruk --overskriv bare hvis du vil lage alle data på nytt; endringer i CSV-ene går da tapt.)"
        )
    if sti.exists():
        hint = (
            "Kjør med --overskriv for å lage alle data på nytt (endringer i CSV-ene går da tapt), "
            "eller --fra-csv --overskriv for å bygge databasen fra CSV-ene."
            if csv_dir is not None
            else "Kjør med --overskriv for å erstatte den."
        )
        raise FileExistsError(f"{sti} finnes fra før. {hint}")
    if csv_finnes:
        raise FileExistsError(f"CSV-filene i {csv_dir} finnes fra før. Kjør med --overskriv for å erstatte dem.")


def _skriv_database(sti: Path, tabeller: dict[str, list[dict]]) -> dict[str, int]:
    """Bygg i en midlertidig fil og bytt den inn først når alt har gått bra."""
    sti.parent.mkdir(parents=True, exist_ok=True)
    tmp = sti.with_name(sti.name + ".tmp")
    if tmp.exists():
        tmp.unlink()
    try:
        _fyll(tmp, tabeller)
    except BaseException:
        if tmp.exists():
            tmp.unlink()
        raise
    os.replace(tmp, sti)
    return {navn: len(tabeller[navn]) for navn in TABELLREKKEFOLGE}


def _fyll(sti: Path, tabeller: dict[str, list[dict]]) -> None:
    with closing(sqlite3.connect(sti)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(config.SCHEMA_STI.read_text(encoding="utf-8"))
        with conn:
            for navn in TABELLREKKEFOLGE:
                rader = tabeller[navn]
                kolonner = [r[1] for r in conn.execute(f'PRAGMA table_info("{navn}")')]
                plass = ", ".join("?" for _ in kolonner)
                conn.executemany(
                    f'INSERT INTO "{navn}" ({", ".join(kolonner)}) VALUES ({plass})',
                    ([r.get(k) for k in kolonner] for r in rader),
                )


def _skriv_csv(csv_dir: Path, sti: Path) -> None:
    csv_dir.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(sti)) as conn:
        for navn in TABELLREKKEFOLGE:
            cur = conn.execute(f'SELECT * FROM "{navn}" ORDER BY rowid')
            with open(csv_dir / f"{navn}.csv", "w", encoding=CSV_KODING, newline="") as f:
                w = csv.writer(f, delimiter=CSV_SKILLETEGN)
                w.writerow([d[0] for d in cur.description])
                w.writerows(["" if v is None else v for v in rad] for rad in cur)


def _kolonnetyper() -> dict[str, dict[str, tuple[str, bool]]]:
    """tabell -> kolonne -> (deklarert type, NOT NULL)."""
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.executescript(config.SCHEMA_STI.read_text(encoding="utf-8"))
        return {
            t: {r[1]: (r[2].upper(), bool(r[3]) or bool(r[5])) for r in conn.execute(f'PRAGMA table_info("{t}")')}
            for t in TABELLREKKEFOLGE
        }


def _konverter(fil: str, radnr: int, kolonne: str, verdi: str | None, type_: str, paakrevd: bool):
    def feil(hva: str) -> CsvFeil:
        return CsvFeil(f"{fil}, rad {radnr}, kolonne '{kolonne}': {hva} (verdi: {verdi!r})")

    if verdi is None or verdi.strip() == "":
        if paakrevd:
            raise feil("mangler verdi")
        return None
    verdi = verdi.strip()
    if type_ == "INTEGER":
        try:
            return int(verdi)
        except ValueError:
            raise feil("må være et heltall") from None
    if type_ == "REAL":
        try:
            return float(verdi.replace(",", "."))
        except ValueError:
            raise feil("må være et tall") from None
    if kolonne == "tidspunkt" and not _ISO_TID.fullmatch(verdi):
        raise feil("må ha formen ÅÅÅÅ-MM-DDTtt:mm (Excel kan ha endret datoformatet)")
    if kolonne in DATOKOLONNER and not _ISO_DATO.fullmatch(verdi):
        raise feil("må ha formen ÅÅÅÅ-MM-DD (Excel kan ha endret datoformatet)")
    if kolonne == "telefon" and not _TELEFON.fullmatch(verdi):
        raise feil("må være 8 siffer som starter med 0 (Excel kan ha fjernet nullen)")
    return verdi


def _les_csv(csv_dir: Path) -> dict[str, list[dict]]:
    typer = _kolonnetyper()
    tabeller = {}
    for navn in TABELLREKKEFOLGE:
        fil = f"{navn}.csv"
        try:
            with open(csv_dir / fil, encoding=CSV_KODING, newline="") as f:
                rader = list(csv.DictReader(f, delimiter=CSV_SKILLETEGN))
        except UnicodeDecodeError:
            raise CsvFeil(f"{fil} er ikke lagret som UTF-8. Lagre den i Excel som «CSV UTF-8 (semikolondelt)».") from None
        ut = []
        for radnr, rad in enumerate(rader, start=2):
            ekstra = [v for v in (rad.pop(None, None) or []) if (v or "").strip()]
            if ekstra:
                raise CsvFeil(f"{fil}, rad {radnr}: flere felt enn kolonner ({ekstra!r}). Står det et semikolon i en tekst?")
            if all((v or "").strip() == "" for v in rad.values()):
                continue  # tom rad, typisk fra Excel
            ut.append({
                k: _konverter(fil, radnr, k, rad.get(k), *typer[navn][k])
                for k in typer[navn]
            })
        tabeller[navn] = ut
    return tabeller


def bygg_database(
    sti: Path = config.STANDARD_DB_STI,
    museum_db: Path = config.MUSEUM_DB_STI,
    seed: int = config.STANDARD_SEED,
    skala: str = "full",
    overskriv: bool = False,
    csv_dir: Path | None = config.CSV_DIR,
) -> dict[str, int]:
    """Generer kundedata fra innstillingene, skriv databasen og (valgfritt) CSV-filer."""
    if skala not in config.SKALAER:
        raise ValueError(f"Ukjent skala '{skala}'. Gyldige: {', '.join(config.SKALAER)}")
    sti = Path(sti)
    _sjekk_overskriving(sti, csv_dir, overskriv)
    fake = Faker("no_NO")
    fake.seed_instance(seed)
    tabeller = generer_kunder(
        random.Random(seed),
        fake,
        ansattkilde.hent_ansatte(museum_db),
        ansattkilde.hent_dagsbesok(museum_db, config.KUNDER_START, config.REFERANSEDATO),
        ansattkilde.hent_hendelser(museum_db),
        faktor=config.SKALAER[skala],
    )
    tabeller.update(_katalog())
    antall = _skriv_database(sti, tabeller)
    if csv_dir is not None:
        _skriv_csv(Path(csv_dir), sti)
    return antall


def bygg_fra_csv(
    sti: Path = config.STANDARD_DB_STI, csv_dir: Path = config.CSV_DIR, overskriv: bool = False
) -> dict[str, int]:
    """Bygg databasen fra CSV-filene (bevarer manuelle endringer)."""
    sti = Path(sti)
    _sjekk_overskriving(sti, None, overskriv)
    return _skriv_database(sti, _les_csv(Path(csv_dir)))


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Bygg syntetiske kundedata for Kunstpixel.")
    p.add_argument("--sti", type=Path, default=config.STANDARD_DB_STI, help="hvor databasen skrives")
    p.add_argument("--csv-dir", type=Path, default=config.CSV_DIR, help="mappe for CSV-filene")
    p.add_argument("--seed", type=int, default=config.STANDARD_SEED)
    p.add_argument("--skala", choices=sorted(config.SKALAER), default="full")
    p.add_argument("--overskriv", action="store_true", help="erstatt eksisterende database/CSV")
    p.add_argument("--fra-csv", action="store_true", help="bygg databasen fra CSV-filene")
    a = p.parse_args(argv)
    try:
        if a.fra_csv:
            antall = bygg_fra_csv(a.sti, a.csv_dir, a.overskriv)
        else:
            antall = bygg_database(a.sti, seed=a.seed, skala=a.skala, overskriv=a.overskriv, csv_dir=a.csv_dir)
    except (FileExistsError, CsvFeil, ValueError) as e:
        raise SystemExit(f"Avbrutt: {e}") from None
    except sqlite3.IntegrityError as e:
        raise SystemExit(f"Avbrutt: dataene bryter en regel i databasen ({e}). Den gamle databasen er urørt.") from None
    for navn, n in antall.items():
        print(f"{navn:<24}{n:>8}")
    print(f"{'totalt':<24}{sum(antall.values()):>8}")
    print(f"Database: {a.sti}")
    if not a.fra_csv:
        print(f"CSV-filer: {a.csv_dir}")


if __name__ == "__main__":
    main()
