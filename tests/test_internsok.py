"""Fasit for internsøket (docs/specs/internside-oppslagsverk.md, «Internsøk», oppgave 03).

Søket skal finne det interne på tvers av håndbøker, tabeller og dokumenter, og aldri personer,
fravær eller varsler. Testene bygger en midlertidig database og leser filene i prosjektet.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import oppslag

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("internsok") / "museum.db"
    bygg(db)
    return db


def _koder(res: dict) -> set[str]:
    return {g["kode"] for g in res["grupper"]}


def test_tomt_sporsmal_gir_beskjed_ikke_feil() -> None:
    res = oppslag.sok_internt("   ")
    assert res["status"] == "tomt_sporsmal" and res["grupper"] == []


def test_tullsporsmal_gir_ingen_kilde(bygget_db: Path) -> None:
    res = oppslag.sok_internt("zxqvw blorft", db_path=bygget_db)
    assert res["status"] == "ingen_kilde" and res["antall"] == 0


def test_sok_gir_treff_fra_flere_kilder_med_kilde_pa_hvert(bygget_db: Path) -> None:
    res = oppslag.sok_internt("hviletid vakt", db_path=bygget_db)
    assert res["status"] == "ok"
    assert "handbok" in _koder(res)
    assert len(_koder(res)) >= 3, "søket skal gå på tvers av håndbøker og interne tabeller"
    for g in res["grupper"]:
        for t in g["treff"]:
            assert t["id"] and t["tittel"], "hvert treff skal ha id og tittel så det kan spores til kilden"


def test_henvendelser_viser_aldri_varsler_helse_eller_person(bygget_db: Path) -> None:
    sendt = json.dumps(
        [oppslag.sok_internt(q, db_path=bygget_db, limit=50) for q in ("varsling", "sykefravær", "tilrettelegging", "vaktbytte", "permisjon")],
        ensure_ascii=False,
    )
    assert "CASE-013" not in sendt and "CASE-012" not in sendt
    assert "KP-ANS-" not in sendt, "ansatt-ID skal aldri sendes ut"


def test_ingen_personopplysninger_fra_ansattregisteret(bygget_db: Path) -> None:
    sendt = json.dumps(oppslag.sok_internt("Henrik Faye-Lund museumsdirektør", db_path=bygget_db, limit=50), ensure_ascii=False)
    assert "henrik.fayelund" not in sendt and "+47 981" not in sendt


def test_filsok_finner_interne_dokumenter() -> None:
    filer = oppslag.sok_filer(
        "alenearbeid", ROOT, datafinner.MAPPER, datafinner.FILTYPER, datafinner.MAKS_FILSTORRELSE, limit=100
    )
    assert any(f["id"].startswith("05_data/governance/") for f in filer)


def test_datafinner_har_internsok_og_handboksoppslag() -> None:
    assert "sok_internt" in datafinner.VERKTOY
    assert datafinner.VERKTOY["lookup_handbook"][1] == {"query", "handbok", "role", "limit"}
    res = datafinner.run_tool("sok_internt", {"query": "alenearbeid"})
    assert res["status"] == "ok" and "dokumenter" in _koder(res)


def test_oppslagssiden_er_nabar_og_setter_innhold_med_textcontent() -> None:
    assert "/oppslag.html" in datafinner.ASSETS
    side = (ROOT / "src" / "kunstpixel" / "adapters" / "datafinner" / "oppslag.html").read_text(encoding="utf-8")
    assert "af.css" in side and "innerHTML" not in side
    forside = (ROOT / "src" / "kunstpixel" / "adapters" / "datafinner" / "index.html").read_text(encoding="utf-8")
    assert "/oppslag.html" in forside
