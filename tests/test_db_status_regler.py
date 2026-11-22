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
                 "timer, klokkeslett_datakilde, overtid_timer) SELECT 'VAKT-TEST', ansatt_id, aar, maaned, dato, start, "
                 "slutt, stasjon, avdeling, rolle, timer, klokkeslett_datakilde, overtid_timer FROM hr_vakter "
                 "WHERE vakt_id = ?", (vakt_id,))
    assert f"{vakt_id}/VAKT-TEST" in _nye(kopi)["samme person på to vakter samtidig"]


def test_for_kort_hviletid_meldes_som_nytt_brudd(kopi: sqlite3.Connection) -> None:
    # Kveldsvakt til 23:30 dagen før en eksisterende dagvakt: under 11 t hvile før dagvakten.
    vakt_id, *_ = _en_vakt(kopi)
    kopi.execute("INSERT INTO hr_vakter (vakt_id, ansatt_id, aar, maaned, dato, start, slutt, stasjon, avdeling, rolle, "
                 "timer, klokkeslett_datakilde, overtid_timer) SELECT 'VAKT-KVELD', ansatt_id, aar, maaned, "
                 "date(dato, '-1 day'), '20:00', '23:30', stasjon, avdeling, rolle, 3.5, klokkeslett_datakilde, 0 "
                 "FROM hr_vakter WHERE vakt_id = ?", (vakt_id,))
    assert vakt_id in _nye(kopi)["for kort hviletid mellom vakter"]


DOGNMAKS_REGEL = "vakter over døgnmaks uten riktig overtid"


def test_bygget_har_overtid_pa_alle_lange_vakter(kopi: sqlite3.Connection) -> None:
    """Lars 2026-11-22: vakter over døgnmaks er overtid. Bygget skal gi 0 brudd, ikke en advarsel."""
    regel = next(r for r in port.regelbrudd(kopi) if r[0] == DOGNMAKS_REGEL)
    assert regel[2] == [] and regel[3] == []


def test_lang_vakt_uten_overtid_meldes(kopi: sqlite3.Connection) -> None:
    vakt_id = kopi.execute("SELECT vakt_id FROM hr_vakter WHERE overtid_timer > 0 ORDER BY vakt_id LIMIT 1").fetchone()[0]
    kopi.execute("UPDATE hr_vakter SET overtid_timer = 0 WHERE vakt_id = ?", (vakt_id,))
    assert _nye(kopi)[DOGNMAKS_REGEL] == [vakt_id]


def test_tracer_kostnad_regner_med_overtidstillegg(bygget_db: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """P4d: rå SQL og query_shift_cost skal gi samme kostnad, også med 40 % overtidstillegg."""
    con = sqlite3.connect(bygget_db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        port.resultater.clear()
        port.sjekk_tracer(con, bygget_db)
    finally:
        con.close()
    p4d = next(r for r in port.resultater if r[0] == "P4d tracer kostnad")
    assert p4d[1] == port.OK, p4d
    assert "overtid" in p4d[2]


def test_kort_vakt_med_overtid_meldes(kopi: sqlite3.Connection) -> None:
    vakt_id, *_ = _en_vakt(kopi)
    kopi.execute("UPDATE hr_vakter SET overtid_timer = 1 WHERE vakt_id = ? AND timer <= 9", (vakt_id,))
    assert vakt_id in _nye(kopi)[DOGNMAKS_REGEL]
