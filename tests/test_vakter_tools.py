"""Tester for vaktverktøyene: hvem har vakt, vaktplan, arbeidstid og vaktkostnad.

Verktøyene skal bare vise det som står i museum.db: ingen utledede klokkeslett og ingen
overtidsgrense som ikke finnes i databasen. Logikken testes også mot en liten temp-database.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.kunstpixel.core.db import (
    VAKT_KOLONNER_SQL,
    query_shift_cost,
    query_shifts_on_date,
    query_staff_on_shift,
    query_working_hours,
    validate_read_only_query,
)


def test_vaktplan_viser_bare_databasefelt() -> None:
    vakter = query_shifts_on_date("2026-10-20")
    assert vakter
    for v in vakter:
        assert "start" not in v and "slutt" not in v
        assert v["timer"] > 0 and v["navn"] and v["ansatt_id"].startswith("KP-ANS-")


def test_hvem_har_vakt_sier_fra_om_manglende_klokkeslett() -> None:
    r = query_staff_on_shift("2026-10-19")
    assert r["antall_med_vakt"] == len(r["vakter"]) > 0
    assert "Klokkeslett" in r["mangler"]


def test_ugyldig_dato_avvises() -> None:
    with pytest.raises(ValueError):
        query_shifts_on_date("19.10.2026")


def test_arbeidstid_beregner_ikke_overtid() -> None:
    r = query_working_hours("2026-09")
    assert r["antall_ansatte"] > 0 and r["timer_totalt"] > 0
    assert all("overtid_timer" not in a for a in r["ansatte"])
    assert "Overtidsgrensen" in r["mangler"]


def test_vaktkostnad_paa_museum_db() -> None:
    r = query_shift_cost("2026-09")
    assert r["kostnad_nok_totalt"] > 0
    assert sum(a["vakter"] for a in r["avdelinger"]) > r["vakter_uten_tariff"] >= 0


@pytest.fixture()
def mini_db(tmp_path: Path) -> Path:
    db = tmp_path / "mini.db"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE hr_ansatte (ansatt_id TEXT PRIMARY KEY, navn TEXT, avdeling TEXT, stilling TEXT,
            telefon TEXT, epost TEXT, kontor_sal TEXT, stillingsprosent REAL, lonnstrinn_virke INTEGER);
        CREATE TABLE hr_vakter (vakt_id TEXT PRIMARY KEY, ansatt_id TEXT, aar TEXT, maaned TEXT, dato TEXT,
            stasjon TEXT, avdeling TEXT, rolle TEXT, timer REAL, utstilling_id TEXT);
        CREATE TABLE virke_tariff (lonnstrinn INTEGER PRIMARY KEY, timesats_ordinar REAL, timesats_kveld REAL,
            timesats_helg REAL, timesats_helligdag REAL);
        CREATE TABLE norske_helligdager (dato TEXT PRIMARY KEY);
        INSERT INTO hr_ansatte VALUES ('A1','Kari','Drift','Vert','1','k@x','S1',100,30),
                                      ('A2','Ola','Drift','Vert','2','o@x','S1',100,99);
        INSERT INTO virke_tariff VALUES (30, 100, 150, 200, 300);
        INSERT INTO norske_helligdager VALUES ('2026-05-01');
        INSERT INTO hr_vakter VALUES
            ('V1','A1','2026','05','2026-05-04','S','Drift','Vert',8.5,NULL),
            ('V2','A1','2026','05','2026-05-05','S','Drift','Vert',8.5,NULL),
            ('V3','A1','2026','05','2026-05-12','S','Drift','Kveldsvert',10.0,NULL),
            ('V4','A1','2026','05','2026-05-01','S','Drift','Vert',2.0,NULL),
            ('V5','A1','2026','05','2026-05-02','S','Drift','Vert',1.0,NULL),
            ('V6','A2','2026','05','2026-05-04','S','Drift','Vert',7.5,NULL);
        """
    )
    con.commit()
    con.close()
    return db


def test_arbeidstid_summerer_fra_databasen(mini_db: Path) -> None:
    r = query_working_hours("2026-05", db_path=mini_db)
    kari = next(a for a in r["ansatte"] if a["ansatt_id"] == "A1")
    assert kari["timer_totalt"] == 30.0
    assert kari["antall_vakter"] == 5
    assert kari["hoyeste_dognsum"] == 10.0
    assert kari["hoyeste_ukesum"] == 17.0  # 4.-5. mai, samme uke


def test_vaktkostnad_bruker_satser_fra_databasen(mini_db: Path) -> None:
    r = query_shift_cost("2026-05", db_path=mini_db)
    # helligdag 2 t x 300, lørdag 1 t x 200, resten ordinær 27 t x 100 (ingen kveldssats uten klokkeslett)
    assert r["kostnad_nok_totalt"] == 600 + 200 + 2700
    assert r["vakter_uten_tariff"] == 1  # Ola har trinn 99, som ikke finnes i virke_tariff


def test_sporringene_er_lesende() -> None:
    validate_read_only_query("SELECT " + VAKT_KOLONNER_SQL + " FROM hr_vakter v JOIN hr_ansatte a USING(ansatt_id)")
