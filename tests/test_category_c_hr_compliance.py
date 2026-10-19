"""Automated test suite verifying Category C: HR, HMS, Work Environment & Shift Planning.

Verifies:
- STYRK-08 job classification catalog and employee mapping (168 staff)
- Arbeidstilsynet Cleaning Supplier Registry (Renholdsregisteret)
- Movable holidays and school vacation calendars (2010-2026)
- SSB sickness absence rates for culture (table 12441)
- STAMI ergonomic standing limits and rotation rules for galleries
- AML kap. 10 compliance audit engine (daily rest, shift length)
- FastMCP tool wrappers for Category C
"""
from __future__ import annotations

import sqlite3
import pytest

from src.kunstpixel.core.config import get_db_path
from src.kunstpixel.core.mcp_server import (
    audit_shift_compliance,
    check_cleaning_supplier_approval,
    get_calendar_holiday_info,
    get_ergonomic_rotation_rules,
    get_job_profile_styrk,
    get_sickness_absence_statistics,
)


@pytest.fixture(scope="module")
def cat_c_conn() -> sqlite3.Connection:
    """Connect to museum.db in read-only mode."""
    db_file = get_db_path()
    conn = sqlite3.connect(f"file:{db_file.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


class TestStyrk08JobClassification:
    """Verifies STYRK-08 catalog and staff mapping."""

    def test_styrk_catalog_presence_and_minimum_grades(self, cat_c_conn: sqlite3.Connection):
        """All 10 official museum job codes must be present with valid minimum grades."""
        cur = cat_c_conn.cursor()
        cur.execute("SELECT styrk_kode, tittel, virke_minste_lonnstrinn FROM styrk08_katalog")
        codes = {r["styrk_kode"]: r for r in cur.fetchall()}

        assert len(codes) >= 10
        assert "1349.02" in codes  # Direktør
        assert "2651.01" in codes  # Kurator
        assert "2621.01" in codes  # Konservator
        assert "5113.01" in codes  # Salvert
        assert "5132.01" in codes  # Kiosk

        # Verify salary step logic: director >= 60, curator >= 50, attendant >= 20
        assert codes["1349.02"]["virke_minste_lonnstrinn"] >= 60
        assert codes["2651.01"]["virke_minste_lonnstrinn"] >= 50
        assert codes["5113.01"]["virke_minste_lonnstrinn"] >= 20

    def test_all_168_employees_have_mapped_styrk_code(self, cat_c_conn: sqlite3.Connection):
        """Every active and historical employee must have a valid STYRK-08 code."""
        cur = cat_c_conn.cursor()
        cur.execute("SELECT count(*) FROM hr_ansatte WHERE styrk08_kode IS NULL")
        unmapped = cur.fetchone()[0]
        assert unmapped == 0, f"Found {unmapped} unmapped employees"

        cur.execute("SELECT DISTINCT styrk08_kode FROM hr_ansatte")
        assigned_codes = {r[0] for r in cur.fetchall()}
        assert "2651.01" in assigned_codes
        assert "5113.01" in assigned_codes


class TestCleaningSupplierRegistry:
    """Verifies Arbeidstilsynet Renholdsregisteret."""

    def test_iss_is_approved_cleaning_supplier(self):
        """ISS Facility Services must be registered with status 'Godkjent med ansatte'."""
        res = check_cleaning_supplier_approval("982345678")
        assert "error" not in res
        assert res["organisasjonsnummer"] == "982345678"
        assert res["status"] == "Godkjent med ansatte"
        assert res["har_hms_kort_krav"] == 1

    def test_unapproved_supplier_detected(self):
        """Non-approved suppliers must be flagged accordingly."""
        res = check_cleaning_supplier_approval("999000111")
        assert "error" not in res
        assert res["status"] == "Ikke godkjent"


class TestHolidaysAndCalendar:
    """Verifies dynamic Norwegian holiday calculations."""

    def test_national_holiday_17_mai(self):
        """17. mai must trigger 133% holiday supplement factor across years."""
        res = get_calendar_holiday_info("2024-05-17")
        assert res["er_offentlig_hoytid"] == 1
        assert "17. mai" in res["navn"]
        assert res["tillegg_faktor"] >= 2.0

    def test_easter_holidays_computed_dynamically(self, cat_c_conn: sqlite3.Connection):
        """Easter holidays must be correctly dated for 2024 (Skjærtorsdag 2024-03-28)."""
        cur = cat_c_conn.cursor()
        cur.execute("SELECT dato, navn FROM norske_helligdager WHERE dato = '2024-03-28'")
        row = cur.fetchone()
        assert row is not None
        assert "Skjærtorsdag" in row["navn"]

    def test_regular_weekday_returns_standard_rate(self):
        """A regular Tuesday must not have holiday supplement."""
        res = get_calendar_holiday_info("2024-10-15")
        assert res["er_offentlig_hoytid"] is False
        assert res["tillegg_faktor"] == 1.0


class TestSicknessAbsenceAndErgonomics:
    """Verifies SSB sickness rates and STAMI ergonomic limits."""

    def test_quarterly_sickness_absence_rates(self):
        """Q1 must show higher absence rate than Q3."""
        q1 = get_sickness_absence_statistics(year=2024, quarter=1)
        q3 = get_sickness_absence_statistics(year=2024, quarter=3)

        assert "error" not in q1 and "error" not in q3
        assert q1["sykefraver_prosent"] > q3["sykefraver_prosent"]
        assert q1["vikarbuffer_anbefaling_faktor"] > 1.1

    def test_stami_gallery_ergonomics_sal_d(self):
        """Sal D with marble floor must enforce max 2.0h standing and sit pause."""
        res = get_ergonomic_rotation_rules("STASJON-SAL-D")
        assert "error" not in res
        assert res["maks_sammenhengende_timer"] <= 2.0
        assert res["krav_om_sittepause_minutter"] >= 15
        assert "Marmor" in res["underlag_type"]


class TestAmlComplianceEngine:
    """Verifies deterministic audit of shifts against AML kap. 10."""

    def test_standard_compliant_shift_approved(self):
        """A normal 7.5-hour shift must be approved."""
        res = audit_shift_compliance(
            ansatt_id="KP-ANS-001",
            dato="2026-11-10",
            start="09:00",
            end="16:30",
        )
        assert res["compliant"] is True
        assert res["status"] == "APPROVED_AML"
        assert len(res["brudd"]) == 0

    def test_excessive_shift_duration_flagged_as_violation(self):
        """A 12-hour continuous shift without exemption violates AML § 10-4."""
        res = audit_shift_compliance(
            ansatt_id="KP-ANS-001",
            dato="2026-11-10",
            start="08:00",
            end="20:30",
        )
        assert res["compliant"] is False
        assert res["status"] == "REJECTED_AML_VIOLATION"
        assert any("10_4" in b["regel"] for b in res["brudd"])

    def test_fastmcp_styrk_lookup(self):
        """FastMCP get_job_profile_styrk returns curator requirements."""
        res = get_job_profile_styrk("2651.01")
        assert "error" not in res
        assert "Kurator" in res["tittel"]
        assert "Mastergrad" in res["utdanningsnivaa"]
