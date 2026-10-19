"""Tester for vaktverktøyene: hvem er på jobb, vaktplan, overtid og vaktkostnad.

Mot museum.db sjekkes form og utledet start/slutt. Overtid og kostnad testes også mot en
liten temp-database, siden de syntetiske vaktene i museum.db aldri gir overtid.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.kunstpixel.core.db import (
    query_overtime,
    query_shift_cost,
    query_shifts_on_date,
    query_staff_on_duty,
    validate_read_only_query,
)


def test_vaktplan_har_utledet_start_og_slutt() -> None:
    vakter = query_shifts_on_date("2026-10-20")
    assert vakter
    for v in vakter:
        assert v["start"] < v["slutt"]
        assert v["start"] == "09:30" and v["slutt"] == "17:00"  # 7,5 t, dagrolle (ADR 009)
        assert v["navn"] and v["ansatt_id"].startswith("KP-ANS-")


def test_hvem_er_paa_jobb_folger_klokkeslett() -> None:
    midt = query_staff_on_duty("2026-10-19T12:00")
    for_aapning = query_staff_on_duty("2026-10-19T08:00")
    assert midt["antall_pa_jobb"] == midt["antall_vakter_i_dag"] > 0
    assert for_aapning["antall_pa_jobb"] == 0


def test_ugyldig_dato_avvises() -> None:
    with pytest.raises(ValueError):
        query_shifts_on_date("19.10.2026")


def test_vaktkostnad_paa_museum_db() -> None:
    r = query_shift_cost("2026-09")
    assert r["kostnad_nok_totalt"] > 0
    assert r["vakter_uten_tariff"] >= 0
    assert sum(a["vakter"] for a in r["avdelinger"]) > r["vakter_uten_tariff"]


@pytest.fixture()
def mini_db(tmp_path: Path) -> Path:
    db = tmp_path / "mini.db"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE hr_ansatte (ansatt_id TEXT PRIMARY KEY, navn TEXT, avdeling TEXT, stilling TEXT,
            telefon TEXT, epost TEXT, kontor_sal TEXT, lonnstrinn_virke INTEGER);
        CREATE TABLE hr_vakter (vakt_id TEXT PRIMARY KEY, ansatt_id TEXT, aar TEXT, maaned TEXT, dato TEXT,
            stasjon TEXT, avdeling TEXT, rolle TEXT, timer REAL, utstilling_id TEXT);
        CREATE TABLE virke_tariff (lonnstrinn INTEGER PRIMARY KEY, timesats_ordinar REAL, timesats_kveld REAL,
            timesats_helg REAL, timesats_helligdag REAL);
        CREATE TABLE norske_helligdager (dato TEXT PRIMARY KEY);
        INSERT INTO hr_ansatte VALUES ('A1','Kari','Drift','Vert','1','k@x','S1',30), ('A2','Ola','Drift','Vert','2','o@x','S1',99);
        INSERT INTO virke_tariff VALUES (30, 100, 150, 200, 300);
        INSERT INTO norske_helligdager VALUES ('2026-05-01');
        -- Kari: uke 19 (4.-8. mai) 5 x 8,5 t = 42,5 t -> 5 t ukeovertid; 10 t én dag -> 1 t døgnovertid
        INSERT INTO hr_vakter VALUES
            ('V1','A1','2026','05','2026-05-04','S','Drift','Vert',8.5,NULL),
            ('V2','A1','2026','05','2026-05-05','S','Drift','Vert',8.5,NULL),
            ('V3','A1','2026','05','2026-05-06','S','Drift','Vert',8.5,NULL),
            ('V4','A1','2026','05','2026-05-07','S','Drift','Vert',8.5,NULL),
            ('V5','A1','2026','05','2026-05-08','S','Drift','Vert',8.5,NULL),
            ('V6','A1','2026','05','2026-05-12','S','Drift','Kveldsvert',10.0,NULL),
            ('V7','A1','2026','05','2026-05-01','S','Drift','Vert',2.0,NULL),
            ('V8','A1','2026','05','2026-05-02','S','Drift','Vert',1.0,NULL),
            ('V9','A2','2026','05','2026-05-04','S','Drift','Vert',7.5,NULL);
        """
    )
    con.commit()
    con.close()
    return db


def test_overtid_regnes_per_uke_og_dogn(mini_db: Path) -> None:
    r = query_overtime("2026-05", db_path=mini_db)
    kari = next(a for a in r["ansatte"] if a["ansatt_id"] == "A1")
    assert kari["ukeovertid_timer"] == 5.0
    assert kari["dognovertid_timer"] == 1.0
    assert kari["overtid_timer"] == 5.0
    assert r["antall_med_overtid"] == 1


def test_vaktkostnad_velger_riktig_sats(mini_db: Path) -> None:
    r = query_shift_cost("2026-05", db_path=mini_db)
    # helligdag 1. mai 2 t x 300, lørdag 2. mai 1 t x 200, kveld 10 t x 150, 5 dagvakter 42,5 t x 100
    assert r["kostnad_nok_totalt"] == 600 + 200 + 1500 + 4250
    assert r["vakter_uten_tariff"] == 1  # Ola har trinn 99


def test_kveldsrolle_slutter_kl_22(mini_db: Path) -> None:
    vakter = query_shifts_on_date("2026-05-12", db_path=mini_db)
    assert (vakter[0]["start"], vakter[0]["slutt"]) == ("12:00", "22:00")


def test_sporringene_er_lesende() -> None:
    from src.kunstpixel.core import db

    for sql in (db.VAKT_KOLONNER_SQL,):
        validate_read_only_query("SELECT " + sql + " FROM hr_vakter v JOIN hr_ansatte a USING(ansatt_id)")
