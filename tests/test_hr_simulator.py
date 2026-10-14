"""Tester for isolert, syntetisk HR-simulator (ingen nettverk eller ekte HR-data)."""
import json
from pathlib import Path

import pytest

from src.kunstpixel.hr_simulator.engine import (
    create_proposal,
    decide_proposal,
    detect_conflicts,
    list_hr_cases,
    load_scenario,
    pool_candidates,
    suggest_actions,
)

ROOT = Path(__file__).resolve().parents[1] / "05_data/hr_simulator/scenarios"


@pytest.fixture
def busy_day():
    conn = load_scenario(ROOT / "HR-001.json")
    yield conn
    conn.close()


def test_scenario_one_has_two_staffing_conflicts(busy_day):
    found = detect_conflicts(busy_day)
    assert len(found) == 2
    assert {f["kind"] for f in found} == {"overlap", "staff_shortage"}
    assert next(x for x in found if x["kind"] == "overlap")["person_id"] == "EMP-02"
    shortage = next(x for x in found if x["kind"] == "staff_shortage")
    assert shortage["activity_id"] == "A-EVENING"
    assert shortage["skill"] == "vertskap"
    assert shortage["missing"] == 1


def test_move_requires_decision_and_solves_overlap(busy_day):
    create_proposal(
        busy_day, "P-MOVE", "move_activity",
        {"activity_id": "A-MOUNT", "new_start": "2026-10-15T12:00",
         "new_end": "2026-10-15T15:00"},
        "Flytt montering etter skolebesøket",
    )
    assert len(detect_conflicts(busy_day)) == 2
    decide_proposal(busy_day, "P-MOVE", "approved", "LEDER-01", "director", "Kompetanse og kapasitet kontrollert")
    assert len(detect_conflicts(busy_day)) == 1
    assert busy_day.execute("SELECT status FROM proposals WHERE id='P-MOVE'").fetchone()[0] == "approved"
    assert busy_day.execute("SELECT count(*) FROM decision_log").fetchone()[0] == 1


def test_rejection_does_not_change_assignment(busy_day):
    create_proposal(
        busy_day, "P-NO", "move_activity",
        {"activity_id": "A-MOUNT", "new_start": "2026-10-15T12:00",
         "new_end": "2026-10-15T15:00"}, "Alternativ",
    )
    decide_proposal(busy_day, "P-NO", "rejected", "LEDER-01", "director", "Utstilling haster")
    assert len(detect_conflicts(busy_day)) == 2
    assert busy_day.execute("SELECT starts_at FROM activities WHERE id='A-MOUNT'").fetchone()[0].endswith("11:00")


def test_approval_cannot_be_reused_or_given_by_unapproved_role(busy_day):
    create_proposal(
        busy_day, "P-A", "move_activity",
        {"activity_id": "A-MOUNT", "new_start": "2026-10-15T12:00",
         "new_end": "2026-10-15T15:00"}, "Flytt",
    )
    with pytest.raises(PermissionError):
        decide_proposal(busy_day, "P-A", "approved", "USER", "agent", "Prøv")
    assert len(detect_conflicts(busy_day)) == 2
    decide_proposal(busy_day, "P-A", "approved", "LEDER-01", "director", "OK")
    with pytest.raises(ValueError):
        decide_proposal(busy_day, "P-A", "approved", "LEDER-01", "director", "På nytt")


def test_rental_pool_distinguishes_agency_and_internal(busy_day):
    candidates = {x["person_id"]: x for x in pool_candidates(busy_day, "A-EVENING", "vertskap")}
    assert candidates["POOL-01"]["status"] == "review_required"  # Godkjent i demo er ikke nok
    assert candidates["POOL-02"]["status"] == "blocked"
    assert candidates["POOL-03"]["status"] == "unavailable"
    create_proposal(
        busy_day, "P-RENT", "assign_pool",
        {"activity_id": "A-EVENING", "person_id": "POOL-01", "skill": "vertskap"},
        "Foreslå innleie til kveldsvakt",
    )
    with pytest.raises(ValueError):
        decide_proposal(busy_day, "P-RENT", "approved", "HR-01", "hr", "Ingen vurdert hjemmel")
    assert busy_day.execute("SELECT status FROM proposals WHERE id='P-RENT'").fetchone()[0] == "pending"


def test_rental_approval_only_after_explicit_simulation_checks(busy_day):
    # I en faktisk HR-løsning må både hjemmel, registerstatus, avtaler og likebehandling dokumenteres.
    busy_day.execute(
        """UPDATE rental_requests SET legal_basis='vikariat',
           legal_basis_confirmed=1, equal_treatment_reviewed=1 WHERE id='R-001'"""
    )
    busy_day.commit()
    candidates = {x["person_id"]: x for x in pool_candidates(busy_day, "A-EVENING", "vertskap")}
    assert candidates["POOL-01"]["status"] == "eligible"
    create_proposal(
        busy_day, "P-RENT-OK", "assign_pool",
        {"activity_id": "A-EVENING", "person_id": "POOL-01", "skill": "vertskap"}, "Innleie etter manuell kontroll",
    )
    decide_proposal(busy_day, "P-RENT-OK", "approved", "HR-01", "hr", "Fiktiv øvelse")
    assert [x["kind"] for x in detect_conflicts(busy_day)] == ["overlap"]


def test_sensitive_hr_case_is_only_visible_to_hr():
    conn = load_scenario(ROOT / "HR-002.json")
    try:
        assert not detect_conflicts(conn)
        assert list_hr_cases(conn, "employee") == []
        masked = list_hr_cases(conn, "director")
        assert masked == [{"id": "CASE-001", "state": "restricted"}]
        cases = list_hr_cases(conn, "hr")
        assert "senvakter" in cases[0]["title"]
        assert "Ingen av opplysningene er verifisert" in cases[0]["summary"]
    finally:
        conn.close()


def test_hr_followup_is_factfinding_not_auto_judgment():
    conn = load_scenario(ROOT / "HR-002.json")
    try:
        create_proposal(
            conn, "P-CASE", "hr_followup", {"case_id": "CASE-001"},
            "Innhent syn fra begge parter og kontroller grunnlaget",
        )
        with pytest.raises(PermissionError):
            decide_proposal(conn, "P-CASE", "approved", "LEDER-01", "director", "OK")
        decide_proposal(conn, "P-CASE", "approved", "HR-01", "hr", "Åpne faktaundersøkelse")
        assert list_hr_cases(conn, "hr")[0]["state"] == "factfinding"
    finally:
        conn.close()


def test_realistic_contact_data_rejected(tmp_path):
    scenario = json.loads((ROOT / "HR-002.json").read_text(encoding="utf-8"))
    scenario["persons"][0]["email"] = "example@gmail.com"
    path = tmp_path / "unsafe.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")
    with pytest.raises(ValueError, match="fiktive"):
        load_scenario(path)


def test_suggestions_are_generated_but_not_applied(busy_day):
    suggestions = suggest_actions(busy_day)
    assert [s["kind"] for s in suggestions] == ["move_activity", "assign_pool"]
    assert suggestions[0]["payload"] == {
        "activity_id": "A-MOUNT",
        "new_start": "2026-10-15T12:00",
        "new_end": "2026-10-15T15:00",
    }
    assert suggestions[1]["candidate_status"] == "review_required"
    assert len(detect_conflicts(busy_day)) == 2
    assert busy_day.execute("SELECT count(*) FROM proposals").fetchone()[0] == 0


def test_hr_scenario_suggests_factfinding_only():
    conn = load_scenario(ROOT / "HR-002.json")
    try:
        suggestions = suggest_actions(conn)
        assert len(suggestions) == 1
        assert suggestions[0]["kind"] == "hr_followup"
        assert suggestions[0]["requires_approval"] == "hr"
        assert suggestions[0]["confidential"] is True
    finally:
        conn.close()


def test_hr003_staff_shortage_pool_and_confidential_case():
    conn = load_scenario(ROOT / "HR-003.json")
    try:
        conflicts = detect_conflicts(conn)
        assert len(conflicts) == 1
        assert conflicts[0]["kind"] == "staff_shortage"
        assert conflicts[0]["activity_id"] == "A-SCHOOL"
        assert conflicts[0]["skill"] == "formidling"
        pool = {p["person_id"]: p for p in pool_candidates(conn, "A-SCHOOL", "formidling")}
        assert pool["POOL-04"]["status"] == "eligible"
        assert pool["POOL-05"]["status"] == "review_required"
        assert list_hr_cases(conn, "director") == [{"id": "CASE-002", "state": "restricted"}]
        assert len(list_hr_cases(conn, "hr")) == 1
        proposals = suggest_actions(conn)
        assert len(proposals) == 2
        assert proposals[0]["kind"] == "assign_pool"
        assert proposals[0]["payload"]["person_id"] == "POOL-04"
        assert proposals[1]["kind"] == "hr_followup"
    finally:
        conn.close()


def test_hr003_internal_pool_assignment_needs_hr_approval():
    conn = load_scenario(ROOT / "HR-003.json")
    try:
        create_proposal(
            conn, "P-INTERNAL", "assign_pool",
            {"activity_id": "A-SCHOOL", "person_id": "POOL-04", "skill": "formidling"},
            "Bruk intern ekstravakt med riktig kompetanse",
        )
        with pytest.raises(PermissionError):
            decide_proposal(conn, "P-INTERNAL", "approved", "LEDER-01", "director", "Ikke HR")
        assert len(detect_conflicts(conn)) == 1
        decide_proposal(conn, "P-INTERNAL", "approved", "HR-01", "hr", "Gjennomgått fiktive kontraktsvilkår")
        assert detect_conflicts(conn) == []
    finally:
        conn.close()
