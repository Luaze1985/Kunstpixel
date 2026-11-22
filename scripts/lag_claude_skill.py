"""Bygg skill-pakken kunstpixel-demo.zip til Claude-appen (DECISIONS C1–C5).

Pakken har museum.db, et lesende SQL-skript, definisjonene fra skillen kunstpixel-data og en liste
over kjente hull som regnes fra databasen ved hver bygging. Lars laster den opp selv i claude.ai
(Customize > Skills > Upload a skill). Guide: docs/GUIDE-claude-appen.md.

Bruk:
    py -3.13 scripts/lag_claude_skill.py                 # skriver .scratch/claude-app/kunstpixel-demo.zip
    py -3.13 scripts/lag_claude_skill.py --ut C:\\temp   # annen mappe
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAVN = "kunstpixel-demo"
DB = ROOT / "05_data" / "museum.db"
MAL = ROOT / "deploy" / "claude-app"
REFERANSER = ROOT / ".claude" / "skills" / "kunstpixel-data" / "references"
MAKS_UKOMPRIMERT = 30 * 1024 * 1024  # grensen i Anthropics skill-dokumentasjon
FAST_TID = (2026, 1, 1, 0, 0, 0)  # samme tidsstempel i zip-en hver gang

# Tidsserier og datokolonnen deres. Rekkefølgen er rekkefølgen i tabellen i kjente-hull.md.
TIDSSERIER = [
    ("dagsbesok", "dato"), ("besok_tilfredshet", "dato"), ("anmeldelser", "dato"), ("kafe_varesalg", "dato"),
    ("driftsmeldinger_epost", "dato"), ("avvik_hms_drift", "dato"), ("hr_vakter", "dato"), ("hr_fravaer", "fra"),
]


def _tall(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def kjente_hull(con: sqlite3.Connection, idag: date) -> str:
    """Hullene regnes fra databasen, så lista følger med når databasen bygges på nytt."""
    d = idag.isoformat()
    linjer = [
        "# Kjente hull i dataene",
        "",
        f"Regnet fra `data/museum.db` da pakken ble bygget ({d}). Dette er kjent og med vilje eller ikke rettet ennå.",
        "Når et svar berøres, si det i én setning. Finn gjerne flere hull selv med SQL, og si hva du fant.",
        "",
        "## Hvor langt tidsseriene går",
        "",
        "| Tabell | Fra | Til | Rader etter byggedato |",
        "|---|---|---|---|",
    ]
    for tabell, kol in TIDSSERIER:
        fra, til, etter = con.execute(
            f"SELECT min({kol}), max({kol}), sum({kol} > ?) FROM {tabell}", (d,)).fetchone()
        linjer.append(f"| `{tabell}` | {fra} | {til} | {_tall(etter or 0)} |")
    fremtid = con.execute("SELECT count(*), coalesce(sum(besok_totalt), 0) FROM dagsbesok WHERE dato > ?", (d,)).fetchone()
    over9 = con.execute("SELECT count(*) FROM hr_vakter WHERE timer > 9").fetchone()[0]
    navn = con.execute("SELECT count(*) FROM (SELECT navn FROM hr_ansatte GROUP BY navn HAVING count(*) > 1)").fetchone()[0]
    linjer += [
        "",
        "Mangler en kilde tall for perioden et spørsmål gjelder, si at kilden ikke dekker perioden, ikke at tallet er 0.",
        "",
        "## Plan etter i dag",
        "",
        f"- `dagsbesok` har {_tall(fremtid[0])} dager etter byggedato med til sammen {_tall(fremtid[1])} besøk. Det er plan,",
        "  ikke fakta. «I år» og «hittil» teller bare til og med i dag.",
        "- `hr_vakter`, `hr_fravaer`, arrangementer, kafésalg, tilfredshet og anmeldelser har også rader etter i dag",
        "  (plan og syntetisk framskriving).",
        "",
        "## Vakter",
        "",
        f"- {_tall(over9)} vakter er over 9 timer. De er overtid (Lars 2026-11-22): `overtid_timer` = timer over 9,",
        "  og kostnaden har 40 % overtidstillegg for de timene (AML § 10-6).",
        "- 66 vakter har en `timer`-verdi som avviker fra slutt − start − 0,5. Alle er vaktene over 9 timer.",
        "  Bruk alltid kolonnen `timer`.",
        "- 7 kjente brudd på hviletid (under 11 timer fri mellom to vakter) er bevart med vilje som testcaser.",
        "",
        "## Økonomi",
        "",
        "- `driftsregnskap` har lønn fra vaktene (5000) og billettinntekt fra `dagsbesok` (3000) (Lars 2026-11-22).",
        "  `kafe_varesalg` finnes bare for 2024–2026. Før 2024 er kafésalget (3100) h5-tallet fordelt jevnt på",
        "  12 måneder, ikke dagsdata.",
        "- I `h5_historikk_2010_2026` er besøk, billett, kafé, inntekter, kostnader, resultat og årsverk regnet fra",
        "  driftsregnskapet, `dagsbesok` og vaktene. `betalende_besokende` og `snittpris_kr` er ikke regnet om og",
        "  stemmer ikke med billettinntekten. Kildefilene til h5 (CSV og `historikk_tall.yaml`) har fortsatt de gamle tallene.",
        "",
        "## Personer",
        "",
        f"- {navn} navn deles av to ansatte. Slå alltid opp på `ansatt_id`.",
        "- `KP-ANS-155` har ingen personalmappe, med vilje.",
        "- `hr_people` (E101–E112) har noen steder en annen stilling enn `hr_ansatte`. Bruk `hr_ansatte` for navn og stilling.",
        "",
        "## Frister som bare er forslag",
        "",
        "- Retur av innlån når utstillingen slutter, og tilstandskontroll hver 12. måned, er forslag Lars ikke har",
        "  bekreftet. Si det hvis du regner slike frister.",
        "",
    ]
    return "\n".join(linjer)


def _legg_til(z: zipfile.ZipFile, navn: str, data: bytes) -> None:
    info = zipfile.ZipInfo(f"{NAVN}/{navn}", date_time=FAST_TID)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data)


def bygg(ut: Path, idag: date | None = None) -> Path:
    idag = idag or date.today()
    with sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True) as con:
        hull = kjente_hull(con, idag)
    filer: list[tuple[str, bytes]] = [
        ("SKILL.md", (MAL / "SKILL.md").read_bytes()),
        ("scripts/sql.py", (MAL / "sql.py").read_bytes()),
        ("data/museum.db", DB.read_bytes()),
        ("references/kjente-hull.md", hull.encode("utf-8")),
    ]
    for f in sorted(REFERANSER.rglob("*.md")):
        filer.append(("references/" + f.relative_to(REFERANSER).as_posix(), f.read_bytes()))
    ukomprimert = sum(len(b) for _, b in filer)
    if ukomprimert >= MAKS_UKOMPRIMERT:
        raise SystemExit(f"STOPP: pakken er {ukomprimert / 1e6:.1f} MB ukomprimert, over grensen på 30 MB.")
    ut.mkdir(parents=True, exist_ok=True)
    zipfil = ut / f"{NAVN}.zip"
    with zipfile.ZipFile(zipfil, "w") as z:
        for navn, data in sorted(filer):
            _legg_til(z, navn, data)
    print(f"OK: {zipfil}")
    print(f"    {len(filer)} filer, {ukomprimert / 1e6:.1f} MB ukomprimert, {zipfil.stat().st_size / 1e6:.1f} MB zip.")
    return zipfil


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Bygg skill-pakken til Claude-appen")
    p.add_argument("--ut", type=Path, default=ROOT / ".scratch" / "claude-app", help="mappe for zip-filen")
    a = p.parse_args(argv)
    bygg(a.ut)
    return 0


if __name__ == "__main__":
    sys.exit(main())
