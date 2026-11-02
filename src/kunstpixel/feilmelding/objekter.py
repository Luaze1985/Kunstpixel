"""Objektene man kan melde feil på, og originalen de kommer fra.

Bare typene i OBJEKTTYPER kan velges. Begge databasene åpnes skrivebeskyttet.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from src.kunstpixel.core.config import get_db_path
from src.kunstpixel.persondata import config as pd_config

# type -> (database, tabell, id-kolonne, SQL-uttrykk for visningsnavn, kilde)
OBJEKTTYPER: dict[str, tuple[str, str, str, str, str]] = {
    "kontakt": ("persondata", "kontakter", "kontakt_id", "fornavn || ' ' || etternavn", "05_data/persondata/csv/kontakter.csv"),
    "medlemskap": ("persondata", "medlemskap", "medlemskap_id", "type || ', fra ' || startdato", "05_data/persondata/csv/medlemskap.csv"),
    "gavekort": ("persondata", "gavekort", "kode", "belop || ' kr, utstedt ' || utstedt", "05_data/persondata/csv/gavekort.csv"),
    "arrangement": ("persondata", "arrangementer", "arrangement_id", "tittel || ' (' || dato || ')'", "05_data/persondata/csv/arrangementer.csv"),
    "pamelding": ("persondata", "pameldinger", "pamelding_id", "arrangement_id || ', ' || registrert", "05_data/persondata/csv/pameldinger.csv"),
    "skolebestilling": ("persondata", "skolebestillinger", "bestilling_id", "skole || ' (' || dato || ')'", "05_data/persondata/csv/skolebestillinger.csv"),
    "utleie": ("persondata", "utleie", "foresporsel_id", "kontaktperson || ' (' || dato || ')'", "05_data/persondata/csv/utleie.csv"),
    "henvendelse": ("persondata", "henvendelser", "henvendelse_id", "kategori || ': ' || substr(fritekst, 1, 50)", "05_data/persondata/csv/henvendelser.csv"),
    "ansatt": ("museum", "hr_ansatte", "ansatt_id", "navn || ', ' || stilling", "05_data/museum.db (hr_ansatte)"),
    "vakt": ("museum", "hr_vakter", "vakt_id", "dato || ' ' || start || '–' || slutt || ', ' || stasjon", "05_data/museum.db (hr_vakter)"),
    "verk": ("museum", "verk", "id", "tittel", "05_data/museum.db (verk)"),
    "kunstner": ("museum", "kunstnere", "id", "navn", "05_data/museum.db (kunstnere)"),
    "hendelse": ("museum", "hendelser", "id", "tittel || ' (' || dato || ')'", "05_data/museum.db (hendelser)"),
    "utstilling": ("museum", "utstillinger", "id", "tittel", "05_data/museum.db (utstillinger)"),
    "dagsbesok": ("museum", "dagsbesok", "dato", "dato || ': ' || besok_totalt || ' besøk'", "05_data/museum.db (dagsbesok)"),
    "arsoversikt": ("museum", "h5_historikk_2010_2026", "ar", "ar || ': ' || tema", "05_data/h5_historikk_2010_2026.csv (laget av src/kunstpixel/core/intern/leveranse.py)"),
}

NAVN = {
    "kontakt": "Kunde/kontakt", "medlemskap": "Medlemskap", "gavekort": "Gavekort", "arrangement": "Arrangement",
    "pamelding": "Påmelding", "skolebestilling": "Skolebestilling", "utleie": "Utleie", "henvendelse": "Henvendelse",
    "ansatt": "Ansatt", "vakt": "Vakt", "verk": "Kunstverk", "kunstner": "Kunstner", "hendelse": "Hendelse",
    "utstilling": "Utstilling", "dagsbesok": "Dagsbesøk", "arsoversikt": "Årsoversikt",
}


def _sti(database: str) -> Path:
    if database == "persondata":
        return Path(os.environ.get("KUNSTPIXEL_PERSONDATA_DB") or pd_config.STANDARD_DB_STI)
    return get_db_path()


def _koble(database: str) -> sqlite3.Connection:
    sti = _sti(database)
    if not sti.is_file():
        raise FileNotFoundError(f"Fant ikke {sti}.")
    conn = sqlite3.connect(f"file:{sti.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _type(objekttype: str) -> tuple[str, str, str, str, str]:
    if objekttype not in OBJEKTTYPER:
        raise ValueError(f"Ukjent objekttype: {objekttype}")
    return OBJEKTTYPER[objekttype]


def objekttyper() -> list[dict]:
    """Typene man kan velge, med om databasen deres finnes."""
    return [
        {"type": t, "navn": NAVN[t], "gruppe": "Kundedata" if v[0] == "persondata" else "Museum", "tilgjengelig": _sti(v[0]).is_file()}
        for t, v in OBJEKTTYPER.items()
    ]


def list_objekter(objekttype: str, sok: str = "", limit: int = 50) -> list[dict]:
    """Objekter av en type, filtrert på ID eller visningsnavn."""
    database, tabell, idkol, visning, _ = _type(objekttype)
    limit = max(1, min(int(limit), 200))
    with closing(_koble(database)) as conn:
        rader = conn.execute(
            f'SELECT CAST("{idkol}" AS TEXT) AS id, {visning} AS visning FROM "{tabell}" '
            f'WHERE CAST("{idkol}" AS TEXT) LIKE :s OR ({visning}) LIKE :s ORDER BY "{idkol}" LIMIT :n',
            {"s": f"%{sok}%", "n": limit},
        ).fetchall()
    return [{"id": r["id"], "visning": r["visning"]} for r in rader]


def hent_objekt(objekttype: str, objekt_id: str) -> dict | None:
    """Originalraden slik den står i databasen nå, med hvor den kommer fra."""
    database, tabell, idkol, visning, kilde = _type(objekttype)
    with closing(_koble(database)) as conn:
        rad = conn.execute(
            f'SELECT *, {visning} AS __visning FROM "{tabell}" WHERE CAST("{idkol}" AS TEXT) = ?', (str(objekt_id),)
        ).fetchone()
    if rad is None:
        return None
    felt = {k: rad[k] for k in rad.keys() if k != "__visning"}
    return {"type": objekttype, "id": str(objekt_id), "visning": rad["__visning"], "kilde": kilde, "tabell": tabell, "felt": felt}


def alle_ansatte() -> list[dict]:
    with closing(_koble("museum")) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT ansatt_id, navn, avdeling, stilling, ansatt_fra, ansatt_til FROM hr_ansatte ORDER BY navn"
        )]


def aktive_ansatte(dato: date) -> list[dict]:
    """Ansatte som er i jobb på datoen. Bare de kan melde feil den dagen."""
    d = dato.isoformat()
    return [a for a in alle_ansatte() if a["ansatt_fra"] <= d and (a["ansatt_til"] is None or a["ansatt_til"] >= d)]
