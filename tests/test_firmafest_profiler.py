"""Tester for Kunstprofil-appen til firmafesten (02_deliverables/firmafest_kunstprofil)."""

import importlib.util
import itertools
import json
import sqlite3
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parent.parent / "02_deliverables" / "firmafest_kunstprofil"


@pytest.fixture(scope="module")
def bygg():
    spec = importlib.util.spec_from_file_location("bygg_data", APP_DIR / "bygg_data.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture(scope="module")
def artister(bygg):
    return bygg.hent_artister()


def test_alle_kunstnere_med_verk_er_med(artister, db_conn):
    med_verk = {
        r["kunstner_id"] for r in db_conn.execute("SELECT DISTINCT kunstner_id FROM verk")
    }
    assert {a["id"] for a in artister} == med_verk


def test_alt_i_appen_finnes_i_databasen(artister, db_conn):
    for a in artister:
        k = db_conn.execute("SELECT navn FROM kunstnere WHERE id = ?", (a["id"],)).fetchone()
        assert k is not None and k["navn"] == a["navn"]
        v = db_conn.execute(
            "SELECT tittel, kunstner_id FROM verk WHERE id = ?", (a["verk"]["id"],)
        ).fetchone()
        assert v is not None
        assert v["tittel"] == a["verk"]["tittel"]
        assert v["kunstner_id"] == a["id"]


def test_poeng_peker_kun_til_kunstnere_i_appen(bygg, artister):
    gyldige = {a["id"] for a in artister}
    for q in bygg.QUESTIONS:
        assert len(q["valg"]) == 4
        for valg in q["valg"]:
            assert set(valg["poeng"]) <= gyldige


def test_hver_kunstner_kan_vinne(bygg, artister):
    vinnere = {
        bygg.finn_profil(list(kombo))
        for kombo in itertools.product(range(4), repeat=len(bygg.QUESTIONS))
    }
    assert vinnere == {a["id"] for a in artister}


def test_ingen_kunstner_dominerer(bygg):
    antall: dict[int, int] = {}
    kombinasjoner = list(itertools.product(range(4), repeat=len(bygg.QUESTIONS)))
    for kombo in kombinasjoner:
        vinner = bygg.finn_profil(list(kombo))
        antall[vinner] = antall.get(vinner, 0) + 1
    assert max(antall.values()) / len(kombinasjoner) < 0.20
    assert min(antall.values()) / len(kombinasjoner) > 0.02


def test_profiler_json_er_oppdatert(bygg, artister):
    lagret = json.loads((APP_DIR / "profiler.json").read_text(encoding="utf-8"))
    # JSON gjør heltallsnøkler om til tekst, så sammenlign etter en runde gjennom JSON
    forventet = json.loads(
        json.dumps({"artister": artister, "spoersmaal": bygg.QUESTIONS}, ensure_ascii=False)
    )
    assert lagret == forventet


def test_html_inneholder_dataene():
    for navn in ("index.html", "kunstprofil_artifact.html"):
        tekst = (APP_DIR / navn).read_text(encoding="utf-8")
        assert "/*PROFILER_JSON*/" not in tekst
        assert "Theodor Kittelsen" in tekst
        assert "Anna-Eva Bergman" in tekst
