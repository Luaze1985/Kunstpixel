"""Tester for forretningsreglene i statusporten (P6). Beviser at reglene slår til, ikke bare at de gir 0.

Hver test plasserer ett brudd i en temp-kopi av bygget (aldri 05_data/museum.db) og sjekker at
riktig regel melder det som nytt brudd.
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import db_status_gate as port


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("regler") / "museum.db"
    bygg(db)
    return db


@pytest.fixture()
def kopi(bygget_db: Path, tmp_path: Path):
    sti = tmp_path / "kopi.db"
    shutil.copyfile(bygget_db, sti)
    con = sqlite3.connect(sti)
    yield con
    con.close()


def _nye(con: sqlite3.Connection) -> dict[str, list[str]]:
    return {navn: nye for navn, _, nye, _ in port.regelbrudd(con)}


def test_bygget_har_ingen_nye_brudd_pa_harde_regler(kopi: sqlite3.Connection) -> None:
    harde = {navn: nye for navn, niva, nye, _ in port.regelbrudd(kopi) if niva == port.FEIL}
    assert all(not nye for nye in harde.values()), harde


def test_kjente_hviletidsbrudd_finnes_fortsatt(kopi: sqlite3.Connection) -> None:
    kjente = {navn: k for navn, _, _, k in port.regelbrudd(kopi)}
    assert set(kjente["for kort hviletid mellom vakter"]) == port.KJENTE_BRUDD["for kort hviletid mellom vakter"], \
        "er de kjente bruddene rettet i dataene? Fjern dem da fra KJENTE_BRUDD"


def _en_vakt(con: sqlite3.Connection) -> tuple:
    return con.execute("SELECT vakt_id, ansatt_id, dato, start, slutt FROM hr_vakter WHERE aar = '2026' "
                       "ORDER BY vakt_id LIMIT 1").fetchone()


def test_vakt_pa_fravaersdag_meldes(kopi: sqlite3.Connection) -> None:
    vakt_id, ansatt_id, dato, *_ = _en_vakt(kopi)
    kopi.execute("INSERT INTO hr_fravaer (fravaer_id, ansatt_id, fra, til, type, datakilde) "
                 "VALUES ('TEST-1', ?, ?, ?, 'egenmelding', 'syntetisk (test)')", (ansatt_id, dato, dato))
    assert vakt_id in _nye(kopi)["vakt på dag med eget fravær"]


def test_overlappende_vakter_meldes(kopi: sqlite3.Connection) -> None:
    vakt_id, ansatt_id, dato, start, slutt = _en_vakt(kopi)
    kopi.execute("INSERT INTO hr_vakter (vakt_id, ansatt_id, aar, maaned, dato, start, slutt, stasjon, avdeling, rolle, "
                 "timer, klokkeslett_datakilde) SELECT 'VAKT-TEST', ansatt_id, aar, maaned, dato, start, slutt, stasjon, "
                 "avdeling, rolle, timer, klokkeslett_datakilde FROM hr_vakter WHERE vakt_id = ?", (vakt_id,))
    assert f"{vakt_id}/VAKT-TEST" in _nye(kopi)["samme person på to vakter samtidig"]


def test_for_kort_hviletid_meldes_som_nytt_brudd(kopi: sqlite3.Connection) -> None:
    # Kveldsvakt til 23:30 dagen før en eksisterende dagvakt: under 11 t hvile før dagvakten.
    vakt_id, *_ = _en_vakt(kopi)
    kopi.execute("INSERT INTO hr_vakter (vakt_id, ansatt_id, aar, maaned, dato, start, slutt, stasjon, avdeling, rolle, "
                 "timer, klokkeslett_datakilde) SELECT 'VAKT-KVELD', ansatt_id, aar, maaned, date(dato, '-1 day'), "
                 "'20:00', '23:30', stasjon, avdeling, rolle, 3.5, klokkeslett_datakilde FROM hr_vakter WHERE vakt_id = ?",
                 (vakt_id,))
    assert vakt_id in _nye(kopi)["for kort hviletid mellom vakter"]
