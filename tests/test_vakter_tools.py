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


def test_vaktplan_viser_databasefelt() -> None:
    vakter = query_shifts_on_date("2026-10-20")
    assert vakter
    for v in vakter:
        assert v["timer"] > 0 and v["navn"] and v["ansatt_id"].startswith("KP-ANS-")
        if "start" in v:
            assert v["start"] < v["slutt"]


def test_hvem_har_vakt_gir_ansatte_med_vakt() -> None:
    r = query_staff_on_shift("2026-10-19")
    assert r["antall_med_vakt"] == len(r["vakter"]) > 0


def test_ugyldig_dato_avvises() -> None:
    with pytest.raises(ValueError):
        query_shifts_on_date("19.10.2026")


def test_arbeidstid_beregner_timer() -> None:
    r = query_working_hours("2026-09")
    assert r["antall_ansatte"] > 0 and r["timer_totalt"] > 0
    assert len(r["ansatte"]) > 0


def test_vaktkostnad_paa_museum_db() -> None:
    r = query_shift_cost("2026-09")
    assert r["kostnad_nok_totalt"] > 0
    assert sum(a["vakter"] for a in r["avdelinger"]) >= 0


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


# --- Mot en database bygget av build_museum_db.py (temp-fil, museum.db røres ikke) ---


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("bygg") / "museum.db"
    bygg(db)
    return db


def test_bygget_db_har_syntetisk_merkede_klokkeslett(bygget_db: Path) -> None:
    vakter = query_shifts_on_date("2026-10-20", db_path=bygget_db)
    assert vakter and all(v["start"] < v["slutt"] for v in vakter)
    assert all(v["klokkeslett_datakilde"].startswith("syntetisk") for v in vakter)


def test_bygget_db_gir_hvem_er_paa_jobb(bygget_db: Path) -> None:
    morgen = query_staff_on_shift("2026-10-19", "06:00", db_path=bygget_db)
    midt = query_staff_on_shift("2026-10-19", "12:00", db_path=bygget_db)
    assert "mangler" not in midt
    assert morgen["antall_pa_jobb"] == 0
    forventet = [v for v in midt["vakter"] if v["start"] <= "12:00" < v["slutt"]]
    assert midt["antall_pa_jobb"] == len(forventet) > 0


def test_bygget_db_beregner_overtid_mot_grenser(bygget_db: Path) -> None:
    r = query_working_hours("2026-09", db_path=bygget_db)
    assert "mangler" not in r
    assert r["grenser"]["ukenorm_timer"]["verdi"] == 37.5
    assert r["grenser"]["ukenorm_timer"]["datakilde"].startswith("syntetisk")
    assert all("overtid_timer" in a for a in r["ansatte"])


def test_bygget_db_bruker_kveldssats_for_timer_etter_grensen(bygget_db: Path) -> None:
    r = query_shift_cost("2026-09", db_path=bygget_db)
    assert sum(a["kveldstimer"] for a in r["avdelinger"]) > 0
    assert "Kveldssats er ikke brukt" not in r.get("mangler", "")


def test_bygget_db_tariff_dekker_alle_trinn_og_ingen_mangler(bygget_db: Path) -> None:
    """T1 (G2): Tariff trinn 66-86 gjør at vakter_uten_tariff == 0."""
    r = query_shift_cost("2026-09", db_path=bygget_db)
    assert r["vakter_uten_tariff"] == 0
    assert "ikke kostnadsberegnet" not in r.get("mangler", "")


def test_bygget_db_eget_fravaer_uten_kollisjon_og_innenfor_ssb(bygget_db: Path) -> None:
    """T2 (G3): hr_fravaer gir kvartalsrapport med 0 vaktkollisjoner og diff under 1.5 pp fra SSB."""
    from src.kunstpixel.core.db import query_absence_report
    r = query_absence_report(2025, 2, db_path=bygget_db)
    assert "mangler" not in r
    assert r["aktive_ansatte"] > 0
    assert r["sykedager_totalt"] > 0
    assert r["ssb_sammenligning"]
    ssb_p = r["ssb_sammenligning"]["sykefraver_prosent"]
    assert abs(r["egen_prosent"] - ssb_p) <= 1.5


def test_bygget_db_roller_og_sporsmal_tabeller(bygget_db: Path) -> None:
    """T3 (G5): roller og rolle_sporsmal finnes og list_roles() returnerer rollene A-L."""
    from src.kunstpixel.core.db import query_roles
    roles = query_roles(db_path=bygget_db)
    assert len(roles) == 12
    codes = {r["kode"] for r in roles}
    assert "K" in codes and "L" in codes
    hr_role = next(r for r in roles if r["kode"] == "K")
    assert hr_role["trigger"] == "/hr"
    assert len(hr_role["sporsmal"]) >= 4


def test_bygget_db_rapport_regler_med_fallback(bygget_db: Path) -> None:
    """T4 (G4): rapport_regler har regler og fallback per sporsmal_id."""
    from src.kunstpixel.core.db import query_report_rules
    for sporsmal_id in ["vakt-i-dag", "vaktplan", "arbeidstid", "sykefravaer", "utstilling", "vaktkostnad"]:
        regler = query_report_rules(sporsmal_id, db_path=bygget_db)
        assert len(regler) >= 2
        assert any(r["operator"] == "fallback" for r in regler)
        assert all(r["vurdering"] and r["forslag"] for r in regler)


def test_bygget_db_overtid_oppstaar(bygget_db: Path) -> None:
    """T5 (G6): arkiv_hr_vakt_justering gjør at overtid_timer_totalt > 0."""
    r = query_working_hours("2026-09", db_path=bygget_db)
    assert r["overtid_timer_totalt"] > 0
    assert r["antall_med_overtid"] > 0


def test_bygget_db_felles_sannhet_ansatte_kobling(bygget_db: Path) -> None:
    """G10: hr_people har ansatt_id som refererer til hr_ansatte."""
    import sqlite3
    con = sqlite3.connect(bygget_db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        r = con.execute("SELECT id, name, ansatt_id FROM hr_people WHERE id='E101'").fetchone()
        assert r[0] == "E101"
        assert r[2] and r[2].startswith("KP-ANS-")
        # Bekreft at ansatt_id finnes i hr_ansatte
        navn = con.execute("SELECT navn FROM hr_ansatte WHERE ansatt_id=?", (r[2],)).fetchone()[0]
        assert navn
    finally:
        con.close()

