from __future__ import annotations

import sqlite3
from pathlib import Path

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import datapolicy, db, mcp_server

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "05_data" / "museum.db"


def test_driftsmeldinger_historikk_og_2020_2026_vektlegging() -> None:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        min_aar, max_aar, totalt, nyere = con.execute(
            "SELECT MIN(aar), MAX(aar), COUNT(*), "
            "SUM(CASE WHEN aar BETWEEN 2020 AND 2026 THEN 1 ELSE 0 END) "
            "FROM driftsmeldinger_epost"
        ).fetchone()
        tiltak_antall = con.execute("SELECT COUNT(*) FROM driftsmeldinger_tiltak").fetchone()[0]
        kat_antall = dict(
            con.execute(
                "SELECT kategori, COUNT(*) FROM driftsmeldinger_epost GROUP BY kategori"
            ).fetchall()
        )
    finally:
        con.close()

    assert min_aar == 2010
    assert max_aar == 2026
    assert totalt >= 3800
    assert tiltak_antall == totalt
    assert (nyere / totalt) >= 0.80

    forventede_kat = {
        "vakt_og_hviletid",
        "sykefraver_og_vikar",
        "personvern_og_gdpr",
        "hms_og_sikkerhet",
        "klima_og_samling",
        "kafe_og_allergen",
        "kundekontakt_og_epost",
        "arrangement_og_booking",
    }
    assert set(kat_antall.keys()) == forventede_kat
    assert kat_antall["kundekontakt_og_epost"] >= 350
    assert kat_antall["arrangement_og_booking"] >= 350


def test_driftsmeldinger_fk_og_syntetisk_policy() -> None:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        fk_feil = (
            con.execute("PRAGMA foreign_key_check(driftsmeldinger_epost)").fetchall()
            + con.execute("PRAGMA foreign_key_check(driftsmeldinger_tiltak)").fetchall()
        )
        assert fk_feil == []

        for tabell in ("driftsmeldinger_epost", "driftsmeldinger_tiltak"):
            kilder = [
                r[0]
                for r in con.execute(f"SELECT DISTINCT datakilde FROM {tabell}").fetchall()
            ]
            assert kilder
            for k in kilder:
                assert datapolicy.normalize_classification(k) == datapolicy.SYNTETISK, (
                    f"Ugyldig datakilde i {tabell}: {k}"
                )
    finally:
        con.close()


def test_query_daglig_driftsinnboks_og_ankercaser() -> None:
    res = db.query_daglig_driftsinnboks(sok="MELD-2026-900", limit=20)
    assert res["treff_antall"] == 9
    funnet = {m["melding_id"]: m for m in res["meldinger"]}

    assert funnet["MELD-2026-9001"]["handbok_punkt_id"] == "PERSONAL-3.2"
    assert funnet["MELD-2026-9001"]["vurdering_utfall"] == "AVSLÅS_LOVSTRIDIG_OVERSTYRING"
    assert funnet["MELD-2026-9002"]["handbok_punkt_id"] == "SOP-004-2"
    assert funnet["MELD-2026-9002"]["vurdering_utfall"] == "IVERKSETT_SOP_003_VIKAR"
    assert funnet["MELD-2026-9003"]["handbok_punkt_id"] == "SOP-008-2"
    assert funnet["MELD-2026-9003"]["sal_id"] == "SAL-D"
    assert funnet["MELD-2026-9003"]["vurdering_utfall"] == "STANS_OG_SIKRE_SAL"
    assert funnet["MELD-2026-9004"]["handbok_punkt_id"] == "SOP-001-4"
    assert funnet["MELD-2026-9004"]["vurdering_utfall"] == "ESKALER_VERNEOMBUD_AML_2A"
    assert funnet["MELD-2026-9005"]["handbok_punkt_id"] == "SOP-007-2"
    assert funnet["MELD-2026-9005"]["vurdering_utfall"] == "SLADD_PERSONDATA_OG_OPPDATER_ALLERGEN"
    assert funnet["MELD-2026-9006"]["handbok_punkt_id"] == "PERSONAL-8.1"
    assert funnet["MELD-2026-9006"]["vurdering_utfall"] == "AVSLÅ_PRIVAT_VERDIVURDERING_OG_GAVE"
    assert funnet["MELD-2026-9007"]["handbok_punkt_id"] == "DRIFT_KVALITET-2.1"
    assert funnet["MELD-2026-9007"]["vurdering_utfall"] == "SIKRE_UNIVERSELL_TILGANG_OG_LEDSAGER"
    assert funnet["MELD-2026-9008"]["handbok_punkt_id"] == "DRIFT_KVALITET-8.1"
    assert funnet["MELD-2026-9008"]["vurdering_utfall"] == "AVSLÅ_MEDBRAKT_ALKOHOL_OG_OVERKAPASITET"
    assert funnet["MELD-2026-9009"]["handbok_punkt_id"] == "DRIFT_KVALITET-1.2"
    assert funnet["MELD-2026-9009"]["vurdering_utfall"] == "KREV_SKOLESIKKERHET_OG_GARDEROBE"

    for mid, m in funnet.items():
        assert m["epost_sms_utkast"], f"Mangler svarutkast for {mid}"
        assert m["lovhjemmel"], f"Mangler lovhjemmel for {mid}"


def test_mcp_og_datafinner_get_daily_ops_inbox() -> None:
    mcp_res = mcp_server.get_daily_ops_inbox(aar=2026, hastegrad="KRITISK", limit=10)
    assert mcp_res["treff_antall"] >= 1
    assert mcp_res["historikk_oversikt"]["andel_2020_2026_prosent"] >= 80.0

    kunde_res = mcp_server.get_daily_ops_inbox(kategori="kundekontakt_og_epost", limit=10)
    assert kunde_res["treff_antall"] == 10

    arr_res = mcp_server.get_daily_ops_inbox(kategori="arrangement_og_booking", limit=10)
    assert arr_res["treff_antall"] == 10

    df_res = datafinner.run_tool(
        "get_daily_ops_inbox",
        {"sok": "MELD-2026-9008", "limit": 5},
    )
    assert df_res["treff_antall"] == 1
    assert df_res["meldinger"][0]["vurdering_utfall"] == "AVSLÅ_MEDBRAKT_ALKOHOL_OG_OVERKAPASITET"
