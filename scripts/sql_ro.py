"""Kjør én lesende SQL-spørring mot museum.db og skriv svaret som tabell.

Kontrollørens eneste vei inn i databasen (DECISIONS L7). Bruker samme sperre som
MCP-laget (bare SELECT/WITH, sperrede ord) og åpner filen med mode=ro.

Bruk:
    py -3.13 scripts/sql_ro.py "SELECT count(*) FROM verk"
    py -3.13 scripts/sql_ro.py --maks 50 "SELECT * FROM hr_vakter WHERE dato = '2026-11-13'"
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.db import execute_read_query


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Lesende SQL mot museum.db")
    p.add_argument("sql", help="én SELECT- eller WITH-spørring")
    p.add_argument("--maks", type=int, default=200, help="maks rader som vises (standard 200)")
    a = p.parse_args(argv)

    try:
        rader = execute_read_query(a.sql)
    except (PermissionError, sqlite3.Error) as feil:
        print(f"AVVIST: {feil}", file=sys.stderr)
        return 1

    if not rader:
        print("(0 rader)")
        return 0
    print("\t".join(rader[0].keys()))
    for rad in rader[: a.maks]:
        print("\t".join("" if v is None else str(v) for v in rad))
    if len(rader) > a.maks:
        print(f"... {len(rader) - a.maks} rader til (bruk --maks)")
    print(f"({len(rader)} rader)")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
