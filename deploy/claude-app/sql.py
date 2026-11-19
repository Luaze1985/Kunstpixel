"""Én lesende SQL-spørring mot museum.db i skill-pakken kunstpixel-demo.

Virker alene (ingen import fra Kunstpixel-repoet), så det kan kjøres i Claude-appens kodemiljø.
Tre sperrer: filen åpnes skrivebeskyttet (mode=ro, immutable=1), bare én SELECT/WITH tas imot,
og SQLite-autorisasjonen avviser alt som ikke er lesing (også PRAGMA og ATTACH).

Bruk:
    python3 scripts/sql.py "SELECT count(*) FROM hr_ansatte"
    python3 scripts/sql.py --maks 50 "SELECT * FROM hr_vakter WHERE dato = '2026-11-13'"
    python3 scripts/sql.py --tabeller
    python3 scripts/sql.py --kolonner hr_vakter
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "museum.db"
LOV = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, getattr(sqlite3, "SQLITE_RECURSIVE", 33)}


# Tabellinfo (--kolonner) leses med pragma_table_info, som SQLite regner som PRAGMA. Bare den slippes gjennom.
LESE_PRAGMA = {"table_info", "table_xinfo"}


def _tillat(handling: int, a1, a2, *_) -> int:
    if handling in LOV or (handling == sqlite3.SQLITE_PRAGMA and str(a1).lower() in LESE_PRAGMA):
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def _koble() -> sqlite3.Connection:
    con = sqlite3.connect(DB.as_uri() + "?mode=ro&immutable=1", uri=True)
    con.set_authorizer(_tillat)
    return con


def kjor(sql: str) -> tuple[list[str], list[tuple]]:
    ren = sql.strip().rstrip(";").strip()
    if not re.match(r"(?is)^(select|with)\b", ren):
        raise PermissionError("bare én SELECT eller WITH er lov")
    if ";" in re.sub(r"'(?:[^']|'')*'", "", ren):
        raise PermissionError("bare én spørring om gangen")
    with _koble() as con:
        cur = con.execute(ren)
        return [d[0] for d in cur.description or []], cur.fetchall()


def _skriv(kolonner: list[str], rader: list[tuple], maks: int) -> None:
    if not rader:
        print("(0 rader)")
        return
    print("\t".join(kolonner))
    for r in rader[:maks]:
        print("\t".join("" if v is None else str(v) for v in r))
    if len(rader) > maks:
        print(f"({len(rader)} rader, viser {maks}. Bruk --maks eller en snevrere spørring.)")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Lesende SQL mot museum.db")
    p.add_argument("sql", nargs="?", help="én SELECT- eller WITH-spørring")
    p.add_argument("--maks", type=int, default=200, help="maks rader som vises (standard 200)")
    p.add_argument("--tabeller", action="store_true", help="vis alle tabeller med antall rader")
    p.add_argument("--kolonner", metavar="TABELL", help="vis kolonnene i en tabell")
    a = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # æøå riktig også i Windows-konsollen
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        if a.tabeller:
            _, navn = kjor("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
            rader = [(n, kjor(f'SELECT count(*) FROM "{n}"')[1][0][0]) for (n,) in navn]
            _skriv(["tabell", "rader"], rader, 1000)
        elif a.kolonner:
            k, r = kjor("SELECT name, type FROM pragma_table_info(?)".replace("?", "'" + a.kolonner.replace("'", "''") + "'"))
            _skriv(k, r, 1000)
        elif a.sql:
            _skriv(*kjor(a.sql), a.maks)
        else:
            p.print_help()
            return 2
    except (PermissionError, sqlite3.Error) as feil:
        print(f"AVVIST: {feil}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
