"""Bemanning: hvilke kurs en stasjon krever, og (oppgave 08–09) hvem som er egnet.

Alt leses fra museum.db med mode=ro. Dataene er syntetiske.
"""

from __future__ import annotations

from pathlib import Path

from src.kunstpixel.core import db


def krav(stasjon: str, db_path: Path | str | None = None) -> list[str]:
    """skill_code-ene stasjonen krever, sortert. Tom liste hvis stasjonen er ukjent."""
    with db.get_db_connection(db_path) as con:
        rader = con.execute(
            "SELECT skill_code FROM stasjon_krav WHERE stasjon = ? ORDER BY skill_code", (stasjon,)
        ).fetchall()
    return [r[0] for r in rader]
