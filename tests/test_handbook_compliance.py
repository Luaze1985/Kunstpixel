"""Test suite for Aura Kunstmuseum Virksomhetshåndbøker (To-lags arkitektur).

Verifies:
1. Existence and completeness of the 4 markdown handbooks.
2. Database table `handbok_oppslag` structure and record counts.
3. Query accuracy with keyword, handbook code, and role filtering.
4. FastMCP tool `lookup_handbook` functionality.
5. Museumsvert agent integration with handbook queries.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
import pytest

from src.kunstpixel.core.config import get_db_path
from src.kunstpixel.core.db import query_handbook
from src.kunstpixel.core.mcp_server import lookup_handbook
from src.kunstpixel.core.agent import MuseumsvertAgent

ROOT = Path(__file__).resolve().parents[1]
HANDBOKER_DIR = ROOT / "04_knowledge" / "01_governance" / "handboker"


def test_handbook_markdown_files_exist():
    """Verify all 4 handbook markdown documents exist and have content."""
    expected_files = [
        "01_personalhandbok.md",
        "02_hms_sikkerhetshandbok.md",
        "03_drifts_kvalitetshandbok.md",
        "04_leder_beredskapshandbok.md",
    ]
    for fn in expected_files:
        path = HANDBOKER_DIR / fn
        assert path.exists(), f"Mangler håndbokfil: {fn}"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 1000, f"Håndbokfilen {fn} er for kort"
        assert "## Kapittel 1:" in content
        assert "## Kapittel 10:" in content


def test_database_table_handbok_oppslag():
    """Verify handbok_oppslag table exists in museum.db with indexed records."""
    db_path = get_db_path()
    conn = sqlite3.connect(f"file:{db_path.resolve().as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        count = cur.execute("SELECT count(*) FROM handbok_oppslag").fetchone()[0]
        assert count >= 60, f"Forventet minst 60 indekserte punkter, fant {count}"

        koder = [r[0] for r in cur.execute("SELECT DISTINCT handbok_kode FROM handbok_oppslag").fetchall()]
        assert "PERSONAL" in koder
        assert "HMS_SIKKERHET" in koder
        assert "DRIFT_KVALITET" in koder
        assert "LEDER_BEREDSKAP" in koder
    finally:
        conn.close()


def test_query_personal_sick_leave_rules():
    """Query handbook for sick leave (egenmelding) and verify legal basis."""
    res = query_handbook(query="egenmelding", handbok="PERSONAL")
    assert len(res) > 0
    top = res[0]
    assert "PERSONAL" in top["handbok_kode"]
    assert any("Folketrygdloven" in r["lovhjemmel"] or "Folketrygdloven" in r["innhold"] for r in res)
    assert any("egenmelding" in r["innhold"].lower() for r in res)


def test_query_rest_hours_aml():
    """Query handbook for 11h daily rest / hviletid under AML."""
    res = query_handbook(query="11 timer hviletid", handbok="PERSONAL")
    assert len(res) > 0
    match = any("11 timer" in r["innhold"] and "AML" in (r["lovhjemmel"] or r["innhold"]) for r in res)
    assert match, "Fant ikke 11-timers hviletidsregel i Personalhåndboken"


def test_query_hms_lifting_and_ergonomics():
    """Query HMS handbook for maximum lifting weight and STAMI standing limits."""
    res_lift = query_handbook(query="15 kg", handbok="HMS_SIKKERHET")
    assert len(res_lift) > 0
    assert any("15 kg" in r["innhold"] for r in res_lift)

    res_stami = query_handbook(query="ståtid rotasjon", handbok="HMS_SIKKERHET")
    assert len(res_stami) > 0
    assert any("90 minutter" in r["innhold"] or "2 timer" in r["innhold"] for r in res_stami)


def test_query_hms_art_evacuation_rvr():
    """Query HMS handbook for Restverdiredning (RVR) and Munch's Skrik."""
    res = query_handbook(query="restverdiredning skrik", handbok="HMS_SIKKERHET")
    assert len(res) > 0
    top = res[0]
    assert "RVR" in top["innhold"] or "kunstevakuering" in top["avsnitt_tittel"].lower()
    assert "Skrik" in top["innhold"] or "Edvard Munch" in top["innhold"]


def test_query_drift_food_hygiene_and_allergens():
    """Query Drift handbook for cafe food hygiene HACCP and mandatory allergens."""
    res = query_handbook(query="haccp kjøleskap", handbok="DRIFT_KVALITET")
    assert len(res) > 0
    assert any("+4" in r["innhold"] for r in res)

    res_allergen = query_handbook(query="14 allergener", handbok="DRIFT_KVALITET")
    assert len(res_allergen) > 0
    assert any("14" in r["innhold"] for r in res_allergen)


def test_query_leader_whistleblowing_and_procurement():
    """Query Leader handbook for whistleblowing (AML § 2 A) and procurement thresholds."""
    res_wb = query_handbook(query="varsling gjengjeldelse", handbok="LEDER_BEREDSKAP")
    assert len(res_wb) > 0
    assert any("gjengjeldelse" in r["innhold"] for r in res_wb)

    res_proc = query_handbook(query="terskelverdier anskaffelser doffin", handbok="LEDER_BEREDSKAP")
    assert len(res_proc) > 0
    assert any("100 000" in r["innhold"] or "Doffin" in r["innhold"] for r in res_proc)


def test_fastmcp_lookup_handbook_tool():
    """Test FastMCP tool lookup_handbook directly."""
    tool_res = lookup_handbook(query="brannalarm rømning", handbok="HMS_SIKKERHET", limit=3)
    assert isinstance(tool_res, list)
    assert len(tool_res) > 0
    assert any("brann" in r["innhold"].lower() for r in tool_res)


def test_museumsvert_agent_handbook_interaction():
    """Test that MuseumsvertAgent answers queries regarding handbooks accurately."""
    agent = MuseumsvertAgent()
    resp = agent.handle_message("Hva er regelen for egenmelding i håndboken?")
    assert resp.category == "handbok"
    assert "lookup_handbook" in resp.tools_used
    assert "Personalhåndbok" in resp.text or "SOP" in resp.text
    assert "Folketrygdloven" in resp.text or "egenmelding" in resp.text.lower()


def test_sop_routines_exist_and_indexed():
    """Verify that SOP-001 through SOP-004 are present on disk and in database."""
    sops_dir = ROOT / "04_knowledge" / "02_sops"
    for s_name in ["SOP-001_rutine_varsling.md", "SOP-002_rutine_ferie.md", "SOP-003_rutine_fravaer_og_sykefravar.md", "SOP-004_rutine_vaktbytte.md"]:
        assert (sops_dir / s_name).exists(), f"Mangler SOP-fil: {s_name}"

    sop_records = query_handbook(handbok="RUTINER_SOP", limit=20)
    assert len(sop_records) >= 12, f"Forventet minst 12 indekserte SOP-punkter, fant {len(sop_records)}"


def test_sop_queries_whistleblowing_and_sick_leave():
    """Verify precise lookups on SOP rules."""
    wb = query_handbook(query="saksbehandling trinn", handbok="SOP")
    assert len(wb) > 0
    assert any("Trinn 1" in r["innhold"] for r in wb)

    sick = query_handbook(query="oppfølgingsplan dialogmøte", handbok="SOP")
    assert len(sick) > 0
    assert any("Uke 4" in r["innhold"] and "Uke 7" in r["innhold"] for r in sick)
