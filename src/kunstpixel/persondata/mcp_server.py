"""Åpen MCP-server for syntetiske kundedata i Kunstpixel (fase 1).

Fase 1 har ingen tilgangssperrer: alle verktøy kan lese alt i persondata.db,
og `museum.db` er koblet på som `museum`, slik at spørringer kan slå sammen
kundedata med `museum.hr_ansatte`. Det eneste som er sperret er skriving:
begge databasene åpnes skrivebeskyttet, og `sporring` godtar bare SELECT/WITH.

Start: py -3.13 src/persondata_mcp.py
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.kunstpixel.core.config import get_db_path
from src.kunstpixel.core.db import validate_read_only_query
from src.kunstpixel.persondata import config

KLASSIFISERING = "syntetisk"
MAKS_RADER = 5000

mcp = FastMCP("Kunstpixel-persondata")


def _persondata_sti() -> Path:
    return Path(os.environ.get("KUNSTPIXEL_PERSONDATA_DB") or config.STANDARD_DB_STI)


def _uri(sti: Path) -> str:
    return f"file:{sti.resolve().as_posix()}?mode=ro"


@contextmanager
def _koble() -> Iterator[sqlite3.Connection]:
    sti = _persondata_sti()
    if not sti.is_file():
        raise FileNotFoundError(
            f"Fant ikke {sti}. Kjør først: py -3.13 -m src.kunstpixel.persondata.generer"
        )
    with closing(sqlite3.connect(_uri(sti), uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("ATTACH DATABASE ? AS museum", (_uri(get_db_path()),))
        yield conn


def _svar(**innhold: Any) -> dict:
    return {"klassifisering": KLASSIFISERING, **innhold}


def _tabeller(conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in conn.execute("SELECT name FROM main.sqlite_master WHERE type='table' ORDER BY name")]


@mcp.tool()
def list_tabeller() -> dict:
    """List alle tabeller i kundedatabasen med antall rader. Tabeller fra museum.db nås som museum.<tabell>."""
    with _koble() as conn:
        return _svar(tabeller=[
            {"tabell": t, "antall": conn.execute(f'SELECT COUNT(*) FROM main."{t}"').fetchone()[0]}
            for t in _tabeller(conn)
        ])


@mcp.tool()
def beskriv_tabell(tabell: str) -> dict:
    """Vis kolonnene og tre eksempelrader for en tabell i kundedatabasen."""
    with _koble() as conn:
        if tabell not in _tabeller(conn):
            raise ValueError(f"Ukjent tabell: {tabell}")
        kolonner = [{"navn": r["name"], "type": r["type"]} for r in conn.execute(f'PRAGMA main.table_info("{tabell}")')]
        eksempler = [dict(r) for r in conn.execute(f'SELECT * FROM main."{tabell}" LIMIT 3')]
    return _svar(tabell=tabell, kolonner=kolonner, eksempler=eksempler)


@mcp.tool()
def sporring(sql: str, limit: int = 200) -> dict:
    """Kjør en fri SELECT-spørring mot kundedatabasen (og museum.<tabell>).

    Bare SELECT og WITH er tillatt. Maks 5000 rader.
    Eksempel: SELECT type, COUNT(*) FROM medlemskap GROUP BY type
    """
    validate_read_only_query(sql)
    limit = max(1, min(int(limit), MAKS_RADER))
    with _koble() as conn:
        cur = conn.execute(sql)
        rader = cur.fetchmany(limit + 1)
        kolonner = [d[0] for d in cur.description] if cur.description else []
    return _svar(kolonner=kolonner, rader=[list(r) for r in rader[:limit]], avkortet=len(rader) > limit)


@mcp.tool()
def innsyn_kontakt(kontakt_id: str) -> dict:
    """Alt som er lagret om én kontakt: medlemskap, fordelsbruk, gavekort, påmeldinger og henvendelser."""
    with _koble() as conn:
        kontakt = conn.execute("SELECT * FROM kontakter WHERE kontakt_id = ?", (kontakt_id,)).fetchone()
        if kontakt is None:
            return _svar(funnet=False)

        def hent(sql: str, *param: Any) -> list[dict]:
            return [dict(r) for r in conn.execute(sql, param)]

        return _svar(
            funnet=True,
            kontakt=dict(kontakt),
            medlemskap=hent("SELECT * FROM medlemskap WHERE kontakt_id = ? ORDER BY startdato", kontakt_id),
            fordel_bruk=hent(
                "SELECT f.* FROM fordel_bruk f JOIN medlemskap m USING (medlemskap_id) "
                "WHERE m.kontakt_id = ? ORDER BY f.dato", kontakt_id,
            ),
            medlemsbesok=hent(
                "SELECT b.* FROM medlemsbesok b JOIN medlemskap m USING (medlemskap_id) "
                "WHERE m.kontakt_id = ? ORDER BY b.dato", kontakt_id,
            ),
            gavekort=hent(
                "SELECT * FROM gavekort WHERE kjoper_kontakt_id = ? OR mottaker_kontakt_id = ? ORDER BY utstedt",
                kontakt_id, kontakt_id,
            ),
            pameldinger=hent("SELECT * FROM pameldinger WHERE kontakt_id = ? ORDER BY registrert", kontakt_id),
            henvendelser=hent("SELECT * FROM henvendelser WHERE kontakt_id = ? ORDER BY tidspunkt", kontakt_id),
        )


@mcp.tool()
def gavekort_saldo(kode: str) -> dict:
    """Saldo for et gavekort (kode på formen GK-XXXX-XXXX)."""
    with _koble() as conn:
        g = conn.execute(
            "SELECT g.gavekort_id, g.belop, g.gyldig_til, k.fornavn || ' ' || k.etternavn AS kjoper "
            "FROM gavekort g JOIN kontakter k ON k.kontakt_id = g.kjoper_kontakt_id WHERE g.kode = ?",
            (kode,),
        ).fetchone()
        if g is None:
            return _svar(funnet=False)
        brukt = conn.execute(
            "SELECT COALESCE(SUM(belop), 0) FROM gavekort_bruk WHERE gavekort_id = ?", (g["gavekort_id"],)
        ).fetchone()[0]
    return _svar(
        funnet=True, belop=g["belop"], brukt=round(brukt, 2), saldo=round(g["belop"] - brukt, 2),
        gyldig_til=g["gyldig_til"], kjoper=g["kjoper"],
    )
