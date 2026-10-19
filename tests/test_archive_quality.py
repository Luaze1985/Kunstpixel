"""Automated regression and quality gates for the historical archive,

legacy baseline preservation, quality system, and database integrity.
"""
from __future__ import annotations

import csv
import sqlite3
from datetime import date
from pathlib import Path
import pytest
import yaml
from src.kunstpixel.data.audit_hr_archive import audit, read_csv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "05_data"
LEGACY_SHIFTS = DATA / "arkiv" / "arkiv_hr_vakt_historikk_legacy_stresstest.csv"
OPERATIVE_SHIFTS = DATA / "arkiv_hr_vakt_historikk.csv"
GOVERNANCE = ROOT / "04_knowledge" / "01_governance"
ROUTINES = ROOT / "04_knowledge" / "04_domain" / "projects" / "hr_simulator" / "museumsrutiner.md"


def test_legacy_baseline_identified():
    """Verify that the preserved legacy archive catches the 36 impossible persondays (>24h) and 4759 over-13h days."""
    if not LEGACY_SHIFTS.exists():
        pytest.skip("Legacy archive not found")
    as_of = date(2026, 10, 17)
    counts, findings = audit(DATA, as_of, shifts_path=LEGACY_SHIFTS)
    assert counts["vakter"] == 48298

    over_24 = [f for f in findings if f["type"] == "over_24_timer_per_dag"]
    assert len(over_24) == 36
    assert all(f["grad"] == "feil" for f in over_24)

    over_13 = [f for f in findings if f["type"] == "over_13_timer_per_dag"]
    assert len(over_13) == 4759
    assert all(f["grad"] == "kontroll" for f in over_13)


def test_operative_archive_counts_and_zero_violations():
    """Verify that the operative archive has zero daily hours violations and clean counts."""
    as_of = date(2026, 10, 17)
    counts, findings = audit(DATA, as_of, shifts_path=OPERATIVE_SHIFTS)
    assert counts["ansatte"] == 168
    assert counts["vakter"] == 54994
    assert counts["innleie"] == 318
    assert counts["utstillinger"] == 102

    # Zero AML daily violations in active archive
    over_24 = [f for f in findings if f["type"] == "over_24_timer_per_dag"]
    assert len(over_24) == 0

    over_13 = [f for f in findings if f["type"] == "over_13_timer_per_dag"]
    assert len(over_13) == 0

    # Only future shifts flagged as info
    future = [f for f in findings if f["type"] == "fremtidig_vakt"]
    assert len(future) == 662
    assert len(findings) == 662


def test_operative_archive_monday_rules_and_no_sal_f():
    """Verify that operative shifts have no public stations on Mondays and no Sal F."""
    shifts = read_csv(OPERATIVE_SHIFTS)
    for s in shifts:
        # Check no Sal F
        assert "Sal F" not in s["stasjon"], f"Invalid station {s['stasjon']} in shift {s['vakt_id']}"
        # Check Monday rule
        shift_date = date.fromisoformat(s["dato"])
        if shift_date.weekday() == 0:
            assert s["stasjon"] in (
                "Magasin 1 (Klimastyrt lager)",
                "Vaktrom / Sikkerhetssentral",
            ), f"Public station {s['stasjon']} staffed on closed Monday {s['dato']}"


def test_calendar_blackout_eliminated():
    """Verify that shifts are properly scheduled on days 29, 30, and 31."""
    shifts = read_csv(OPERATIVE_SHIFTS)
    days = {date.fromisoformat(s["dato"]).day for s in shifts}
    assert 29 in days
    assert 30 in days
    assert 31 in days

    day_counts = {29: 0, 30: 0, 31: 0}
    for s in shifts:
        d = date.fromisoformat(s["dato"]).day
        if d in day_counts:
            day_counts[d] += 1

    assert day_counts[29] > 1000
    assert day_counts[30] > 1000
    assert day_counts[31] > 500


def test_working_copy_classification():
    """Verify that vakter_arbeidskopi.csv categorizes operative shifts into clean statuses."""
    work_copy = DATA / "kvalitetskontroll_hr" / "vakter_arbeidskopi.csv"
    if not work_copy.exists():
        pytest.skip("vakter_arbeidskopi.csv not generated yet")
    with work_copy.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        statuses = {row["kontrollstatus"] for row in reader}
    # Operative archive has 0 errors/review flags
    assert "ingen_funn_i_disse_reglene" in statuses
    assert "planlagt_fremtidig" in statuses
    assert "sperret" not in statuses
    assert "manuell_kontroll" not in statuses


def test_governance_thresholds_harmonized():
    """Verify that KVALITETS_OG_STYRINGSSYSTEM.md and hms_arbeidsmiljo.yaml share 15kg and 80-guest limits."""
    yaml_path = DATA / "governance" / "hms_arbeidsmiljo.yaml"
    md_path = GOVERNANCE / "KVALITETS_OG_STYRINGSSYSTEM.md"
    yaml_text = yaml_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")

    # 15 kg lifting limit for 1 person
    assert "Maks 15 kg" in yaml_text
    assert "Maks 15 kg for én person" in md_text

    # 80 guests limit for lone work
    assert "> 80 gjester" in yaml_text
    assert "> 80 gjester" in md_text


def test_museum_db_rooms_invariance():
    """Verify that museum.db only has the 6 authorized rooms and 0 foreign key violations."""
    db_path = DATA / "museum.db"
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = con.cursor()

    # Foreign key check
    fk_errors = cur.execute("PRAGMA foreign_key_check").fetchall()
    assert len(fk_errors) == 0

    # Authorized rooms
    rooms = [r[0] for r in cur.execute("SELECT id FROM saler ORDER BY id").fetchall()]
    assert rooms == ["MAG-1", "SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E"]

    # No Sal F exists in museum.db
    assert "SAL-F" not in rooms

    # All artworks are in authorized rooms or magazine
    orphan_rooms = cur.execute(
        "SELECT count(*) FROM verk WHERE sal_id NOT IN (SELECT id FROM saler)"
    ).fetchone()[0]
    assert orphan_rooms == 0


def test_national_hms_guidance_loaded():
    """Verify that hms_veiledning_nasjonal.yaml is valid YAML and contains >= 300 Q&As."""
    hms_yaml = GOVERNANCE / "hms_veiledning_nasjonal.yaml"
    assert hms_yaml.exists()
    with hms_yaml.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["antall_oppslag"] == 344
    assert len(data["oppslag"]) == 344
    assert all("sporsmal" in item and "detaljert_veiledning" in item for item in data["oppslag"])


def test_museum_routines_exist():
    """Verify that museumsrutiner.md defines rules R-01 through R-08 and 90min stone floor rule."""
    assert ROUTINES.exists()
    text = ROUTINES.read_text(encoding="utf-8")
    for rule in ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08"]:
        assert rule in text
    assert "90 minutter" in text
