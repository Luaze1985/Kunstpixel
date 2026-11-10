"""Merking av syntetiske data (revisjonsfunn 12) og kopiene av ansattlisten (revisjonsfunn 10).

Datapolicyen godtar bare `syntetisk` eller `syntetisk (<kilde>)`. Alt annet regnes som ekte,
så testen bruker den samme funksjonen som policyen, ikke en løsere `startswith`.
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import pytest

from src.kunstpixel.core.datapolicy import SYNTETISK, normalize_classification

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "05_data"
# hr_ansatte er sannheten. Disse filene er kopier, og navnene skal stemme så lenge de finnes.
KOPIER = ["arkiv_hr_ansatte.csv", "ansatte_168_komplett_personvern_trondheim.csv"]


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("datakilde") / "museum.db"
    bygg(db)
    return db


def _ro(db: Path) -> sqlite3.Connection:
    return sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)


def test_alle_datakilder_i_databasen_godtas_av_policyen(bygget_db: Path) -> None:
    con = _ro(bygget_db)
    feil: dict[str, list[str]] = {}
    try:
        tabeller = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for t in tabeller:
            if "datakilde" not in {r[1] for r in con.execute(f'PRAGMA table_info("{t}")')}:
                continue
            verdier = [r[0] for r in con.execute(f'SELECT DISTINCT datakilde FROM "{t}"')]
            ugyldige = [v for v in verdier if normalize_classification(v) != SYNTETISK]
            if ugyldige:
                feil[t] = ugyldige
    finally:
        con.close()
    assert not feil, f"Datakilder policyen regner som ekte: {feil}"


def test_personalmapper_csv_godtas_av_policyen() -> None:
    with (DATA / "arkiv_hr_personalmapper.csv").open(encoding="utf-8", newline="") as f:
        verdier = {r["datakilde"] for r in csv.DictReader(f)}
    assert verdier
    assert all(normalize_classification(v) == SYNTETISK for v in verdier), verdier


def _avvik(fasit: dict[str, str], kopi: dict[str, str]) -> list[str]:
    return sorted(k for k in fasit.keys() | kopi.keys() if fasit.get(k) != kopi.get(k))


def test_avvik_finner_ulikt_navn_og_manglende_person() -> None:
    assert _avvik({"A": "Per", "B": "Kari"}, {"A": "Pål"}) == ["A", "B"]
    assert _avvik({"A": "Per"}, {"A": "Per"}) == []


@pytest.mark.parametrize("fil", KOPIER)
def test_kopier_av_ansattlisten_stemmer_med_hr_ansatte(bygget_db: Path, fil: str) -> None:
    con = _ro(bygget_db)
    try:
        fasit = dict(con.execute("SELECT ansatt_id, navn FROM hr_ansatte"))
    finally:
        con.close()
    with (DATA / fil).open(encoding="utf-8", newline="") as f:
        kopi = {r["ansatt_id"]: r["navn"] for r in csv.DictReader(f)}
    assert len(fasit) == 168
    assert not _avvik(fasit, kopi), f"{fil} avviker fra hr_ansatte"
