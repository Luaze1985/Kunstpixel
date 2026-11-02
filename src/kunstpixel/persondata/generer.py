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
import random
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
    finnes = [p for p in [sti] if p.exists()]
    if csv_dir is not None and csv_dir.is_dir():
        finnes += sorted(csv_dir.glob("*.csv"))
    if finnes and not overskriv:
        raise FileExistsError(
            f"{finnes[0]} finnes fra før. Kjør med --overskriv hvis du vil erstatte den "
            "(manuelle endringer i CSV-filene går da tapt, bruk --fra-csv for å beholde dem)."
        )


def _skriv_database(sti: Path, tabeller: dict[str, list[dict]]) -> dict[str, int]:
    sti.parent.mkdir(parents=True, exist_ok=True)
    if sti.exists():
        sti.unlink()
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
    return {navn: len(tabeller[navn]) for navn in TABELLREKKEFOLGE}


def _skriv_csv(csv_dir: Path, sti: Path) -> None:
    csv_dir.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(sti)) as conn:
        for navn in TABELLREKKEFOLGE:
            cur = conn.execute(f'SELECT * FROM "{navn}" ORDER BY rowid')
            with open(csv_dir / f"{navn}.csv", "w", encoding=CSV_KODING, newline="") as f:
                w = csv.writer(f, delimiter=CSV_SKILLETEGN)
                w.writerow([d[0] for d in cur.description])
                w.writerows(["" if v is None else v for v in rad] for rad in cur)


def _les_csv(csv_dir: Path) -> dict[str, list[dict]]:
    tabeller = {}
    for navn in TABELLREKKEFOLGE:
        with open(csv_dir / f"{navn}.csv", encoding=CSV_KODING, newline="") as f:
            tabeller[navn] = [
                {k: (None if v == "" else v) for k, v in rad.items()}
                for rad in csv.DictReader(f, delimiter=CSV_SKILLETEGN)
            ]
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
    except FileExistsError as e:
        raise SystemExit(f"Avbrutt: {e}") from None
    for navn, n in antall.items():
        print(f"{navn:<24}{n:>8}")
    print(f"{'totalt':<24}{sum(antall.values()):>8}")
    print(f"Database: {a.sti}")
    if not a.fra_csv:
        print(f"CSV-filer: {a.csv_dir}")


if __name__ == "__main__":
    main()
