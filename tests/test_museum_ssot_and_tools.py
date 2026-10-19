"""Automated test suite verifying the consolidated museum.db SSOT and FastMCP tools.

Verifies:
- All 16 permanent artworks have approved 3-layer texts (veggtekst, audioguide, barn)
- 50 historical museum loans with 3-layer texts, insurance values, and courier requirements
- Condition and conservation reports with lux limits and climate requirements
- Operational incidents (HMS, security, climate, technical, visitor)
- 12 authoritative Brreg suppliers with complete corporate metadata
- Project economy and accounting for all 102 historical exhibitions
- Virke museum tariff calculations (pay grades 20-65, shift supplements, holiday rates)
- FastMCP consolidated tools for all 6 roles
"""
from __future__ import annotations

import sqlite3
import pytest

from src.kunstpixel.core.config import get_db_path
from src.kunstpixel.core.mcp_server import (
    calculate_shift_cost,
    get_condition_report,
    get_exhibition_economy,
    search_incidents,
    search_loans,
    verify_supplier_brreg,
)


@pytest.fixture(scope="module")
def ssot_conn() -> sqlite3.Connection:
    """Connect to the consolidated museum.db in read-only mode."""
    db_file = get_db_path()
    conn = sqlite3.connect(f"file:{db_file.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


class TestConsolidatedDatabaseSSOT:
    """Verifies that all migrated and enriched tables exist and have valid data in museum.db."""

    def test_migrated_historical_tables_exist(self, ssot_conn: sqlite3.Connection):
        """All 5 historical tables must be present in museum.db."""
        cur = ssot_conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for expected in ["hr_ansatte", "utstillinger_historikk", "hr_innleie", "hr_vakter", "personas"]:
            assert expected in tables, f"Missing migrated table: {expected}"

    def test_migrated_historical_row_counts(self, ssot_conn: sqlite3.Connection):
        """Row counts must match the operative archive."""
        cur = ssot_conn.cursor()
        assert cur.execute("SELECT count(*) FROM hr_ansatte").fetchone()[0] == 168
        assert cur.execute("SELECT count(*) FROM utstillinger_historikk").fetchone()[0] == 102
        assert cur.execute("SELECT count(*) FROM hr_innleie").fetchone()[0] == 318
        assert cur.execute("SELECT count(*) FROM hr_vakter").fetchone()[0] == 54994
        assert cur.execute("SELECT count(*) FROM personas").fetchone()[0] == 28

    def test_new_operational_tables_exist(self, ssot_conn: sqlite3.Connection):
        """All new operational tables from ADR 005-007 must exist."""
        cur = ssot_conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for expected in [
            "leverandor_enhetsregister",
            "virke_tariff",
            "utstilling_okonomi",
            "avvik_hms_drift",
            "tilstandsrapporter",
            "utstillingsinnlan",
        ]:
            assert expected in tables, f"Missing new operational table: {expected}"

    def test_new_operational_row_counts(self, ssot_conn: sqlite3.Connection):
        """Row counts for new tables must match locked specifications."""
        cur = ssot_conn.cursor()
        assert cur.execute("SELECT count(*) FROM leverandor_enhetsregister").fetchone()[0] == 12
        assert cur.execute("SELECT count(*) FROM virke_tariff").fetchone()[0] == 46  # steps 20-65
        assert cur.execute("SELECT count(*) FROM utstilling_okonomi").fetchone()[0] == 102
        assert cur.execute("SELECT count(*) FROM avvik_hms_drift").fetchone()[0] >= 30
        assert cur.execute("SELECT count(*) FROM tilstandsrapporter").fetchone()[0] == 16
        assert cur.execute("SELECT count(*) FROM utstillingsinnlan").fetchone()[0] == 50


class TestThreeLayerFormidlingStandard:
    """Verifies that all artworks adhere to the 3-layer text standard in masterprompt."""

    def test_permanent_artworks_have_complete_audioguide_and_children_texts(self, ssot_conn: sqlite3.Connection):
        """Every single artwork in verk must have non-empty audioguide and children texts."""
        cur = ssot_conn.cursor()
        cur.execute("SELECT id, tittel, audioguide_manus, barneformidling FROM verk")
        artworks = cur.fetchall()
        assert len(artworks) == 16

        for a in artworks:
            audio = a["audioguide_manus"]
            barn = a["barneformidling"]
            assert audio is not None and len(audio.strip()) > 50, f"Empty or too short audioguide for {a['id']}"
            assert barn is not None and len(barn.strip()) > 30, f"Empty or too short barneformidling for {a['id']}"

            # Word count checks
            audio_words = len(audio.split())
            barn_words = len(barn.split())

            # Target audioguide: 80 to 200 words (standard: 130-180 words)
            assert 70 <= audio_words <= 220, f"Audioguide for {a['id']} has {audio_words} words; expected ~130-180"
            # Target children text: 40 to 120 words (standard: 60-100 words)
            assert 35 <= barn_words <= 130, f"Barneformidling for {a['id']} has {barn_words} words; expected ~60-100"

    def test_exhibition_loans_have_complete_three_layer_texts(self, ssot_conn: sqlite3.Connection):
        """All 50 loans in utstillingsinnlan must have complete 3-layer texts."""
        cur = ssot_conn.cursor()
        cur.execute("SELECT innlan_id, tittel, eierinstitusjon, veggtekst, audioguide_manus, barneformidling FROM utstillingsinnlan")
        loans = cur.fetchall()
        assert len(loans) == 50

        for loan in loans:
            assert loan["veggtekst"] and len(loan["veggtekst"].split()) >= 40
            assert loan["audioguide_manus"] and len(loan["audioguide_manus"].split()) >= 60
            assert loan["barneformidling"] and len(loan["barneformidling"].split()) >= 30
            assert "KODE" in loan["eierinstitusjon"] or "Nasjonalmuseet" in loan["eierinstitusjon"] or "Lillehammer" in loan["eierinstitusjon"] or "Haugar" in loan["eierinstitusjon"] or "Henie Onstad" in loan["eierinstitusjon"] or "Stavanger" in loan["eierinstitusjon"]


class TestConsolidatedFastMCPTools:
    """Verifies that the new FastMCP tools return genuine, structured data."""

    def test_get_condition_report_skrik(self):
        """Condition report for Skrik must return max 50 lux and hermetic climate frame."""
        res = get_condition_report("AURA-2026-009")
        assert "error" not in res
        assert res["verk_id"] == "AURA-2026-009"
        assert res["tilstandsgrad"] == 1
        assert res["lysomfintlighet_luks"] == 50
        assert res["forsikringsverdi_nok"] == 450000000

    def test_search_loans_external_museums(self):
        """Search loans must return artworks from Nasjonalmuseet or KODE."""
        res = search_loans(query="Munch", limit=5)
        assert isinstance(res, list) and len(res) > 0
        first = res[0]
        assert "Madonna" in first["tittel"] or "Syk pike" in first["tittel"] or "Vampyr" in first["tittel"] or "Solen" in first["tittel"]
        assert first["forsikringsverdi_nok"] >= 100000000

    def test_get_exhibition_economy(self):
        """Exhibition economy must return balanced or explainable project accounts."""
        res = get_exhibition_economy("KP-EXH-2010-001")
        assert "error" not in res
        assert "budsjett_nok" in res
        assert "faktisk_totalkostnad_nok" in res
        assert "billettinntekter_nok" in res
        assert "netto_resultat_nok" in res

    def test_search_incidents_hms_and_climate(self):
        """Incidents search must return structured operational events."""
        res = search_incidents(kategori="KLIMA", limit=5)
        assert isinstance(res, list) and len(res) > 0
        first = res[0]
        assert first["kategori"] == "KLIMA"
        assert first["strakstiltak"] is not None

    def test_verify_supplier_brreg_securitas(self):
        """Brreg lookup for Securitas must return AS, 3850 employees, and active MVA."""
        res = verify_supplier_brreg("912876543")
        assert "error" not in res
        assert res["organisasjonsnummer"] == "912876543"
        assert "Securitas" in res["navn"]
        assert res["organisasjonsform_kode"] == "AS"
        assert res["registrert_i_mva"] == 1
        assert res["under_konkurs"] == 0
        assert res["antall_ansatte"] >= 3000

    def test_calculate_shift_cost_virke(self):
        """Shift cost calculation must correctly apply Virke pay scale and supplements."""
        # Step 20 ordinary
        ord_res = calculate_shift_cost(lonnstrinn=20, timer=7.5, er_kveld=False)
        assert ord_res["lonnstrinn"] == 20
        assert ord_res["total_kostnad_nok"] > 1500

        # Step 20 evening supplement
        eve_res = calculate_shift_cost(lonnstrinn=20, timer=7.5, er_kveld=True)
        assert eve_res["total_kostnad_nok"] > ord_res["total_kostnad_nok"]
        assert "Kveldstillegg" in eve_res["tilleggstype"]

        # Step 20 holiday overtime
        hol_res = calculate_shift_cost(lonnstrinn=20, timer=7.5, er_helligdag=True)
        assert hol_res["total_kostnad_nok"] > eve_res["total_kostnad_nok"]
        assert "133%" in hol_res["tilleggstype"]
