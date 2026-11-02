"""Leser eksisterende (syntetiske) ansatte, dagsbesøk og hendelser fra museum.db.

Alt åpnes skrivebeskyttet (`mode=ro`). Kundegeneratoren bruker dette for å
koble kundedata til ekte ansatt-ID-er og navn.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path
from typing import NamedTuple


class Ansatt(NamedTuple):
    ansatt_id: str
    navn: str
    avdeling: str
    stilling: str
    ansatt_fra: date
    ansatt_til: date | None
    epost: str


def _koble_ro(museum_db: Path) -> sqlite3.Connection:
    if not Path(museum_db).is_file():
        raise FileNotFoundError(f"Fant ikke museum.db: {museum_db}")
    conn = sqlite3.connect(f"file:{Path(museum_db).resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def hent_ansatte(museum_db: Path) -> list[Ansatt]:
    """Alle ansatte i hr_ansatte, sortert på ansatt_id."""
    with closing(_koble_ro(museum_db)) as conn:
        rader = conn.execute(
            "SELECT ansatt_id, navn, avdeling, stilling, ansatt_fra, ansatt_til, epost "
            "FROM hr_ansatte ORDER BY ansatt_id"
        ).fetchall()
    return [
        Ansatt(
            r["ansatt_id"], r["navn"], r["avdeling"], r["stilling"],
            date.fromisoformat(r["ansatt_fra"]),
            date.fromisoformat(r["ansatt_til"]) if r["ansatt_til"] else None,
            r["epost"],
        )
        for r in rader
    ]


def aktive_paa(ansatte: list[Ansatt], dato: date, avdelinger: set[str] | None = None) -> list[Ansatt]:
    """Ansatte som var i jobb på datoen, eventuelt bare i gitte avdelinger."""
    return [
        a for a in ansatte
        if a.ansatt_fra <= dato
        and (a.ansatt_til is None or a.ansatt_til >= dato)
        and (avdelinger is None or a.avdeling in avdelinger)
    ]


def del_navn(navn: str) -> tuple[str, str]:
    """Del ved første mellomrom: fornavn, resten er etternavn."""
    fornavn, _, etternavn = navn.partition(" ")
    return fornavn, etternavn


def hent_dagsbesok(museum_db: Path, fra: date, til: date) -> dict[date, tuple[int, bool]]:
    """Besøk totalt og om museet var åpent, per dag i perioden."""
    with closing(_koble_ro(museum_db)) as conn:
        rader = conn.execute(
            "SELECT dato, besok_totalt, er_aapent FROM dagsbesok WHERE dato BETWEEN ? AND ? ORDER BY dato",
            (fra.isoformat(), til.isoformat()),
        ).fetchall()
    return {date.fromisoformat(r["dato"]): (int(r["besok_totalt"]), bool(r["er_aapent"])) for r in rader}


def hent_hendelser(museum_db: Path) -> list[dict]:
    """Alle hendelser (arrangementer) i museum.db."""
    with closing(_koble_ro(museum_db)) as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM hendelser ORDER BY dato, id")]


def hent_billettpriser(museum_db: Path, fra: date, til: date) -> dict[date, int]:
    """Voksenpris for billett per dag (fra dagsbesok)."""
    with closing(_koble_ro(museum_db)) as conn:
        rader = conn.execute(
            "SELECT dato, pris_voksen FROM dagsbesok WHERE dato BETWEEN ? AND ?", (fra.isoformat(), til.isoformat())
        ).fetchall()
    return {date.fromisoformat(r["dato"]): int(r["pris_voksen"]) for r in rader}


def hent_faq_vekter(museum_db: Path) -> dict[str, int]:
    """Hvor ofte hver kategori spørres om (sum av publikum_faq.hyppighet per kategori)."""
    with closing(_koble_ro(museum_db)) as conn:
        return {
            r["kategori"]: int(r["n"])
            for r in conn.execute("SELECT kategori, SUM(hyppighet) AS n FROM publikum_faq GROUP BY kategori")
        }
