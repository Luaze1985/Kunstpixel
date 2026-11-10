"""Én sannhet for personer (revisjonsfunn 1): navnet lagres bare i hr_ansatte.

Testene bygger til en midlertidig database, slik at de ikke er avhengige av at museum.db er bygget på nytt.
"""

from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path

import pytest

from src.kunstpixel.core import hrdemo

SEED = Path(__file__).resolve().parents[1] / "05_data" / "hr_demo" / "seed.json"


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("en_sannhet") / "museum.db"
    bygg(db)
    return db


@pytest.fixture(scope="module")
def register(bygget_db: Path) -> dict[str, str]:
    """person-id -> navn, slik personalregisteret har det."""
    con = sqlite3.connect(bygget_db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return dict(con.execute("SELECT p.id, a.navn FROM hr_people p JOIN hr_ansatte a USING(ansatt_id)"))
    finally:
        con.close()


def test_hr_people_har_ikke_egen_navnekolonne(bygget_db: Path) -> None:
    con = sqlite3.connect(bygget_db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        kolonner = {r[1] for r in con.execute("PRAGMA table_info(hr_people)")}
    finally:
        con.close()
    assert "name" not in kolonner
    assert "ansatt_id" in kolonner


def test_demo_navn_kommer_fra_hr_ansatte(bygget_db: Path) -> None:
    assert hrdemo.get_person("E101", db_path=bygget_db)["name"] == "Jonas Berg"


def test_alle_12_er_koblet_til_registeret(register: dict[str, str]) -> None:
    assert len(register) == 12
    assert all(navn.strip() for navn in register.values())


def test_ingen_vei_gir_annet_navn_enn_registeret(bygget_db: Path, register: dict[str, str]) -> None:
    folk = hrdemo.list_people(db_path=bygget_db)
    assert {p["id"]: p["name"] for p in folk} == register
    kandidater = hrdemo.candidates("2026-11-07", db_path=bygget_db)["people"]
    assert {p["id"]: p["name"] for p in kandidater} == register
    talt = hrdemo.count_skill("kasse", "2026-11-07", bygget_db)["people"]
    assert talt and all(p["name"] == register[p["id"]] for p in talt)


def test_seed_har_ansatt_id_og_ikke_navn() -> None:
    folk = json.loads(SEED.read_text(encoding="utf-8"))["people"]
    assert len(folk) == 12
    assert not [p["id"] for p in folk if "name" in p]
    assert all(p["ansatt_id"].startswith("KP-ANS-") for p in folk)


def test_seed_med_navn_avvises() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    seed = copy.deepcopy(seed)
    seed["people"][0]["name"] = "Ada Nord"
    with pytest.raises(ValueError, match="hr_ansatte"):
        hrdemo.validate_seed(seed)


def test_seed_uten_ansatt_id_avvises() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    del seed["people"][0]["ansatt_id"]
    with pytest.raises(ValueError, match="ansatt_id"):
        hrdemo.validate_seed(seed)
