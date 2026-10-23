"""Tester for de interne organisasjonstabellene og verktøyene som leser dem.

Alt testes mot en temp-bygget database (build_museum_db.bygg) eller en liten temp-database.
05_data/museum.db røres ikke og trenger ikke være bygget på nytt.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from src.kunstpixel.core.db import (
    INTERN_KATEGORIER,
    query_employee_skills,
    query_internal_requests,
)


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("intern-org") / "museum.db"
    bygg(db)
    return db


def _rad(db: Path, sql: str, *params):
    con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def _antall_varsler(db: Path) -> int:
    return _rad(db, "SELECT count(*) FROM interne_henvendelser WHERE kategori = 'varsling'")[0][0]


def test_bygget_returnerer_antall_og_har_fremmednokler(tmp_path: Path) -> None:
    from src.kunstpixel.data.build_museum_db import bygg

    info = bygg(tmp_path / "x.db")
    assert info["org_ferdigheter"] == 14
    assert info["org_kompetanse"] == 596
    assert info["interne_henvendelser"] == 60
    assert info["hms_avvik_tekst"] == 40
    con = sqlite3.connect(tmp_path / "x.db")
    try:
        for tabell, til in (("org_ansatt_kompetanse", {"hr_ansatte", "org_ferdigheter"}),
                            ("interne_henvendelser", {"hr_ansatte"})):
            assert {r[2] for r in con.execute(f"PRAGMA foreign_key_list('{tabell}')")} == til
    finally:
        con.close()


def test_bygget_avviser_henvendelse_med_ukjent_ansatt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Brutte referanser skal stoppe bygget, ikke slippe stille gjennom."""
    from src.kunstpixel.data import build_museum_db as bygger

    kilde = bygger.INTERNE_HENVENDELSER_CSV.read_text(encoding="utf-8").replace("KP-ANS-164", "KP-ANS-999", 1)
    ødelagt = tmp_path / "henv.csv"
    ødelagt.write_text(kilde, encoding="utf-8")
    monkeypatch.setattr(bygger, "INTERNE_HENVENDELSER_CSV", ødelagt)
    with pytest.raises(ValueError, match="fk_brudd"):
        bygger.bygg(tmp_path / "y.db")


def test_kompetansekort_gir_navn_og_samsvarer_med_raa_sql(bygget_db: Path) -> None:
    r = query_employee_skills("KP-ANS-001", "2026-11-07", db_path=bygget_db)
    assert r["navn"] == "Henrik Faye-Lund" and r["avdeling"] == "Ledelse"
    raa = _rad(bygget_db, "SELECT count(*) FROM org_ansatt_kompetanse WHERE ansatt_id = 'KP-ANS-001'")[0][0]
    assert r["antall"] == len(r["kompetanser"]) == raa > 0
    assert r["antall_gyldige"] == sum(k["gyldig_na"] for k in r["kompetanser"])
    assert r["datakilde"].startswith("syntetisk")


def test_kompetansekort_godtar_liten_bokstav_og_mellomrom(bygget_db: Path) -> None:
    assert query_employee_skills(" kp-ans-001 ", db_path=bygget_db)["ansatt_id"] == "KP-ANS-001"


def test_gyldighet_folger_as_of_og_ikke_lagret_status(bygget_db: Path) -> None:
    ansatt, skill, til = _rad(
        bygget_db,
        "SELECT ansatt_id, skill_code, gyldig_til FROM org_ansatt_kompetanse "
        "WHERE gyldig_til IS NOT NULL AND status = 'gyldig' ORDER BY ansatt_id, skill_code LIMIT 1",
    )[0]

    def gyldig(as_of: str) -> bool:
        kort = query_employee_skills(ansatt, as_of, db_path=bygget_db)
        return next(k for k in kort["kompetanser"] if k["skill_code"] == skill)["gyldig_na"]

    assert gyldig(til) is True            # siste gyldige dag
    assert gyldig("2099-01-01") is False  # lagret_status sier fortsatt «gyldig»
    kort = query_employee_skills(ansatt, "2099-01-01", db_path=bygget_db)
    assert next(k for k in kort["kompetanser"] if k["skill_code"] == skill)["lagret_status"] == "gyldig"


def test_kompetanse_uten_utlop_er_gyldig_etter_sertifisering(bygget_db: Path) -> None:
    ansatt, skill, sert = _rad(
        bygget_db,
        "SELECT ansatt_id, skill_code, sertifisert_dato FROM org_ansatt_kompetanse WHERE gyldig_til IS NULL LIMIT 1",
    )[0]
    kort = query_employee_skills(ansatt, "2099-01-01", db_path=bygget_db)
    assert next(k for k in kort["kompetanser"] if k["skill_code"] == skill)["gyldig_na"] is True
    for_tidlig = query_employee_skills(ansatt, "1999-01-01", db_path=bygget_db)
    assert next(k for k in for_tidlig["kompetanser"] if k["skill_code"] == skill)["gyldig_na"] is False


def test_ukjent_ansatt_og_ugyldig_dato(bygget_db: Path) -> None:
    assert "mangler" in query_employee_skills("KP-ANS-999", db_path=bygget_db)
    with pytest.raises(ValueError):
        query_employee_skills("KP-ANS-001", "23.10.2026", db_path=bygget_db)


def test_henvendelser_filtrerer_pa_kategori_og_sorterer_nyeste_forst(bygget_db: Path) -> None:
    r = query_internal_requests("vaktbytte", limit=100, db_path=bygget_db)
    raa = _rad(bygget_db, "SELECT count(*) FROM interne_henvendelser WHERE kategori = 'vaktbytte'")[0][0]
    assert r["antall"] == raa == len(r["henvendelser"]) > 0
    assert all(h["kategori"] == "vaktbytte" and h["navn"] for h in r["henvendelser"])
    tider = [h["dato_tid"] for h in r["henvendelser"]]
    assert tider == sorted(tider, reverse=True)


def test_henvendelser_begrenser_antall(bygget_db: Path) -> None:
    assert query_internal_requests(limit=5, db_path=bygget_db)["antall"] == 5
    assert query_internal_requests(limit=0, db_path=bygget_db)["antall"] == 1
    assert query_internal_requests(limit=10_000, db_path=bygget_db)["antall"] == 60


def test_ukjent_kategori_avvises(bygget_db: Path) -> None:
    with pytest.raises(ValueError, match="Ukjent kategori"):
        query_internal_requests("hemmelig'; DROP TABLE hr_ansatte;--", db_path=bygget_db)


def test_varsler_skjermer_identitet_og_fritekst(bygget_db: Path) -> None:
    r = query_internal_requests("varsling", limit=100, db_path=bygget_db)
    assert r["antall"] == _antall_varsler(bygget_db) > 0
    for h in r["henvendelser"]:
        assert h["ansatt_id"] is None and h["navn"] is None and h["avdeling"] is None and h["fritekst"] is None
        assert len(h["dato_tid"]) == 10  # bare dato, ikke klokkeslett
        assert h["skjermet"] and h["case_ref"] == "CASE-013"
    # Hverken ID eller navn til noen som varslet skal finnes noe sted i svaret.
    avsendere = _rad(
        bygget_db,
        "SELECT h.ansatt_id, a.navn FROM interne_henvendelser h JOIN hr_ansatte a USING(ansatt_id) WHERE h.kategori = 'varsling'",
    )
    tekst = json.dumps(r, ensure_ascii=False)
    assert all(ident not in tekst and navn not in tekst for ident, navn in avsendere)


def test_varsler_er_skjermet_ogsa_uten_kategorifilter(bygget_db: Path) -> None:
    r = query_internal_requests(limit=100, db_path=bygget_db)
    varsler = [h for h in r["henvendelser"] if h["kategori"] == "varsling"]
    assert len(varsler) == _antall_varsler(bygget_db) and all(h["fritekst"] is None and h["navn"] is None for h in varsler)


def test_ansatt_oppslag_avslorer_ikke_varsler(bygget_db: Path) -> None:
    ident = _rad(bygget_db, "SELECT ansatt_id FROM interne_henvendelser WHERE kategori = 'varsling' LIMIT 1")[0][0]
    for kategori in (None, "varsling"):
        r = query_internal_requests(kategori, ansatt_id=ident, db_path=bygget_db)
        assert all(h["kategori"] != "varsling" for h in r["henvendelser"])
    assert query_internal_requests("varsling", ansatt_id=ident, db_path=bygget_db)["antall"] == 0


def test_alle_kategorier_finnes_i_dataene(bygget_db: Path) -> None:
    for kategori in INTERN_KATEGORIER:
        assert query_internal_requests(kategori, db_path=bygget_db)["antall"] > 0


@pytest.fixture()
def mini_db(tmp_path: Path) -> Path:
    db = tmp_path / "mini.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE hr_ansatte (ansatt_id TEXT PRIMARY KEY, navn TEXT, avdeling TEXT, stilling TEXT)")
    con.commit()
    con.close()
    return db


def test_uten_tabeller_sier_verktoyene_mangler(mini_db: Path) -> None:
    assert "mangler" in query_employee_skills("KP-ANS-001", db_path=mini_db)
    assert "mangler" in query_internal_requests(db_path=mini_db)


def test_verktoyene_er_registrert_i_mcp_men_ikke_i_datafinner() -> None:
    from src.kunstpixel.adapters import datafinner
    from src.kunstpixel.core import mcp_server

    assert callable(mcp_server.get_employee_skills) and callable(mcp_server.search_internal_requests)
    # Interne personsaker skal ikke ut i det åpne API-et eller demokopien.
    assert not {"get_employee_skills", "search_internal_requests"} & set(datafinner.VERKTOY)
