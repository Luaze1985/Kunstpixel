"""Syntetisk driftsregnskap per måned 2010-01 til 2026-12 (Ø1, Lars 2026-11-22: vaktene og dagsdataene er fasit).

Leser et ferdig bygg av museum.db (vakter, dagsbesøk, kafésalg, innleie) og h5-kilden
(`05_data/h5_historikk_2010_2026.csv`), og skriver `05_data/driftsregnskap.csv`.
Kontoene følger NS 4102. Alle beløp er hele kroner og positive. Et beløp på 0 får ingen rad.

Regler (ingen tilfeldighet):
- 5000 Lønn = vaktlønn for måneden, samme kode som `query_shift_cost` (med 40 % overtidstillegg), avrundet til kr.
- 5400 Arbeidsgiveravgift = 14,1 % av 5000.
- 3000 Billettinntekter = sum `dagsbesok.inntekt_nok`.
- 3100 Kafésalg = sum `kafe_varesalg.omsetning_nok`. Kafésalget finnes bare for 2024–2026. For årene før
  brukes h5 `kafeinntekter_tkr` fordelt jevnt på 12 måneder (agentens valg 2026-11-22, ikke bekreftet av Lars).
- 4000 Varekjøp kafé = 35 % av 3100.
- 6700 Innleie og honorarer = sum `hr_innleie.totalbelop_nok`, i måneden for `periode_fra`.
- 3400 Offentlige tilskudd og 3900 Andre inntekter = h5 `tilskudd_tkr` og `andre_inntekter_tkr` fordelt jevnt på
  12 måneder. Desember får resten, så året går opp i kronen.

Fritt nivå (fra `random.Random("kunstpixel-driftsregnskap-v1")`): startnivået i 2010 for 6300, 6340, 6600, 6800
og 7500. Deretter er det regler: lik sum hver måned i året og 3 % prisvekst per år. 6340 har i tillegg fast
sesongprofil (høyere vinter) og strømkrisen 2022–2023.

Kjøres med (bygger et midlertidig museum.db, rører aldri 05_data/museum.db):
    py -3.13 src/kunstpixel/data/regnskap_builder.py
    py -3.13 src/kunstpixel/data/regnskap_builder.py --db <ferdig bygg> --til <mappe>
"""

from __future__ import annotations

import argparse
import csv
import random
import sqlite3
import sys
import tempfile
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "05_data"
H5_HISTORIKK_CSV = DATA_DIR / "h5_historikk_2010_2026.csv"
FILNAVN = "driftsregnskap.csv"
DATAKILDE = "syntetisk (regnskap_builder)"
FRA_AAR, TIL_AAR = 2010, 2026
KOLONNER = ["maaned", "konto", "kontonavn", "belop_nok", "datakilde"]

KONTOER = {
    "3000": "Billettinntekter",
    "3100": "Kafésalg",
    "3400": "Offentlige tilskudd",
    "3900": "Andre inntekter",
    "4000": "Varekjøp kafé",
    "5000": "Lønn",
    "5400": "Arbeidsgiveravgift",
    "6300": "Husleie",
    "6340": "Lys og varme (strøm)",
    "6600": "Reparasjon og vedlikehold",
    "6700": "Innleie og honorarer",
    "6800": "Kontor og IT",
    "7500": "Forsikring",
}
AGA_PROMILLE = 141  # 14,1 %
VAREKOST_KAFE_PROSENT = 35
PRISVEKST = 0.03
# Strøm: andel av snittmåneden, januar til desember (snitt 1,0).
STROM_SESONG = (1.55, 1.45, 1.25, 1.0, 0.75, 0.55, 0.5, 0.55, 0.75, 1.0, 1.25, 1.4)
STROM_KRISE = {2022: 2.4, 2023: 1.7}


def maaneder() -> list[str]:
    return [f"{a}-{m:02d}" for a in range(FRA_AAR, TIL_AAR + 1) for m in range(1, 13)]


def kr(belop: float) -> int:
    """Avrund til hele kroner, halv opp (samme hver gang, ingen banker-avrunding)."""
    return int(Decimal(str(round(belop, 2))).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def vaktlonn_kr(maaned: str, db_path: Path | str) -> int:
    """Konto 5000: vaktlønn fra query_shift_cost. Stopper hvis noen vakter mangler tariffsats."""
    from src.kunstpixel.core.db import query_shift_cost

    svar = query_shift_cost(maaned, db_path)
    if svar["vakter_uten_tariff"]:
        raise ValueError(f"{maaned}: {svar['vakter_uten_tariff']} vakter mangler tariffsats, så lønnen blir for lav")
    return kr(svar["kostnad_nok_totalt"])


def fordel_paa_12(total: int) -> list[int]:
    """Jevn fordeling. Desember får resten, så summen går opp i kronen."""
    del_ = total // 12
    return [del_] * 11 + [total - 11 * del_]


def les_h5() -> dict[int, dict]:
    if not H5_HISTORIKK_CSV.is_file():
        raise FileNotFoundError(f"Mangler h5-kilden: {H5_HISTORIKK_CSV}")
    with open(H5_HISTORIKK_CSV, encoding="utf-8", newline="") as f:
        return {int(r["ar"]): r for r in csv.DictReader(f)}


def _per_maaned(con: sqlite3.Connection, sql: str) -> dict[str, float]:
    return {m: v for m, v in con.execute(sql)}


def lag_rader(db_path: Path | str) -> list[dict]:
    """Alle rader i driftsregnskapet, sortert på (maaned, konto)."""
    db_path = Path(db_path)
    h5 = les_h5()
    con = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        billett = _per_maaned(con, "SELECT substr(dato, 1, 7), SUM(inntekt_nok) FROM dagsbesok GROUP BY 1")
        kafe = _per_maaned(con, "SELECT substr(dato, 1, 7), SUM(omsetning_nok) FROM kafe_varesalg GROUP BY 1")
        innleie = _per_maaned(con, "SELECT substr(periode_fra, 1, 7), SUM(totalbelop_nok) FROM hr_innleie GROUP BY 1")
    finally:
        con.close()

    kafe_aar = defaultdict(int)
    for m in kafe:
        kafe_aar[int(m[:4])] += 1
    halve = {a: n for a, n in kafe_aar.items() if n != 12}
    if halve:
        raise ValueError(f"Kafésalget dekker bare deler av året: {halve}. Velg regel for delvise år først.")

    rng = random.Random("kunstpixel-driftsregnskap-v1")
    # Fritt nivå: månedsbeløp i 2010, trukket i fast rekkefølge.
    start = {
        "6300": rng.randrange(95_000, 105_001, 500),
        "6340": rng.randrange(28_000, 34_001, 500),
        "6600": rng.randrange(22_000, 28_001, 500),
        "6800": rng.randrange(18_000, 24_001, 500),
        "7500": rng.randrange(9_000, 12_001, 500),
    }

    belop: dict[tuple[str, str], int] = {}
    for aar in range(FRA_AAR, TIL_AAR + 1):
        rad_h5 = h5[aar]
        tilskudd = fordel_paa_12(int(rad_h5["tilskudd_tkr"]) * 1000)
        andre = fordel_paa_12(int(rad_h5["andre_inntekter_tkr"]) * 1000)
        kafe_h5 = fordel_paa_12(int(rad_h5["kafeinntekter_tkr"]) * 1000)
        vekst = (1 + PRISVEKST) ** (aar - FRA_AAR)
        for i in range(12):
            m = f"{aar}-{i + 1:02d}"
            lonn = vaktlonn_kr(m, db_path)
            kafesalg = kr(kafe[m]) if aar in kafe_aar else kafe_h5[i]
            belop[(m, "3000")] = int(billett.get(m, 0))
            belop[(m, "3100")] = kafesalg
            belop[(m, "3400")] = tilskudd[i]
            belop[(m, "3900")] = andre[i]
            belop[(m, "4000")] = (kafesalg * VAREKOST_KAFE_PROSENT + 50) // 100
            belop[(m, "5000")] = lonn
            belop[(m, "5400")] = (lonn * AGA_PROMILLE + 500) // 1000
            belop[(m, "6700")] = int(innleie.get(m, 0))
            for konto in ("6300", "6600", "6800", "7500"):
                belop[(m, konto)] = kr(start[konto] * vekst)
            belop[(m, "6340")] = kr(start["6340"] * vekst * STROM_SESONG[i] * STROM_KRISE.get(aar, 1.0))

    return [
        {"maaned": m, "konto": k, "kontonavn": KONTOER[k], "belop_nok": b, "datakilde": DATAKILDE}
        for (m, k), b in sorted(belop.items())
        if b > 0
    ]


def skriv_csv(db_path: Path | str, til: Path | str = DATA_DIR) -> Path:
    til = Path(til)
    til.mkdir(parents=True, exist_ok=True)
    ut = til / FILNAVN
    rader = lag_rader(db_path)
    with open(ut, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KOLONNER, lineterminator="\n")
        w.writeheader()
        w.writerows(rader)
    return ut


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, help="Ferdig bygg å lese. Uten denne bygges et midlertidig museum.db.")
    parser.add_argument("--til", type=Path, default=DATA_DIR, help="Mappe for driftsregnskap.csv (standard 05_data)")
    args = parser.parse_args(argv)
    if args.db:
        ut = skriv_csv(args.db, args.til)
    else:
        from src.kunstpixel.data.build_museum_db import bygg

        with tempfile.TemporaryDirectory(prefix="kunstpixel-regnskap-") as tmp:
            tmp_db = Path(tmp) / "museum.db"
            bygg(tmp_db, med_driftsregnskap=False)  # regnskapet lages av bygget, så det kan ikke lese seg selv
            ut = skriv_csv(tmp_db, args.til)
    print(f"Skrevet: {ut}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
