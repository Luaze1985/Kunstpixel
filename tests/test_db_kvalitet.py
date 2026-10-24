"""Tester for scripts/db_kvalitet.py (databasekvalitet i klartekst)."""

from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import db_kvalitet as kvalitet
import db_status_gate as port


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("kvalitet") / "museum.db"
    bygg(db)
    return db


def test_alle_regler_har_forklaring_pa_norsk() -> None:
    mangler = [navn for navn, _, _ in port.REGLER if navn not in kvalitet.FORKLARING]
    assert not mangler, f"regler uten forklaring: {mangler}"
    for navn, (betyr, gjor) in kvalitet.FORKLARING.items():
        assert betyr.strip() and gjor.strip(), navn


def test_ren_database_gir_ingen_feil(bygget_db: Path) -> None:
    resultat = kvalitet.kjor(bygget_db, med_bygg=False)
    assert [r for r in resultat if r[1] == kvalitet.FEIL] == []
    assert {r[0] for r in resultat} >= {"Databasen er hel", "Riktig skjemaversjon", "Alt er merket syntetisk"}


def test_ny_feil_i_data_gir_feil_med_forklaring(bygget_db: Path, tmp_path: Path) -> None:
    kopi = tmp_path / "museum.db"
    shutil.copyfile(bygget_db, kopi)
    con = sqlite3.connect(kopi)
    con.execute("INSERT INTO hr_fravaer (fravaer_id, ansatt_id, fra, til, type, datakilde) "
                "SELECT 'TEST-1', ansatt_id, dato, dato, 'egenmelding', 'syntetisk (test)' FROM hr_vakter LIMIT 1")
    con.commit()
    con.close()
    feil = [r for r in kvalitet.kjor(kopi, med_bygg=False) if r[1] == kvalitet.FEIL]
    assert [r[0] for r in feil] == ["vakt på dag med eget fravær"]
    navn, _, hva, tiltak = feil[0]
    assert "sykmeldt" in hva and "bygg" in tiltak.lower()


def test_gammel_skjemaversjon_meldes_med_tiltak(bygget_db: Path, tmp_path: Path) -> None:
    kopi = tmp_path / "museum.db"
    shutil.copyfile(bygget_db, kopi)
    con = sqlite3.connect(kopi)
    con.execute("PRAGMA user_version = 3")
    con.commit()
    con.close()
    niva, hva, tiltak = kvalitet.sjekk_skjemaversjon(kvalitet._ro(kopi))
    assert niva == kvalitet.FEIL and "versjon 3" in hva and "build_museum_db.py" in tiltak


def test_endret_fil_oppdages_via_sha(bygget_db: Path, tmp_path: Path) -> None:
    kopi = tmp_path / "museum.db"
    shutil.copyfile(bygget_db, kopi)
    (tmp_path / "museum.db.sha256").write_text("0" * 64 + "  museum.db\n", encoding="utf-8")
    assert kvalitet.sjekk_sha(kopi)[0] == kvalitet.FEIL


def test_manglende_database_gir_exit_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["db_kvalitet.py", "--db", str(tmp_path / "finnes_ikke.db")])
    assert kvalitet.main() == 1
