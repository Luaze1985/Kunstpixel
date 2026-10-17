from datetime import date
from pathlib import Path

import pytest

from src.kunstpixel.hr_simulator.context import Activity, Assignment, Contact, build_week_context, load_planning_context
from src.kunstpixel.hr_simulator.planning import check_week, candidate_status, propose_week, evaluate_proposal


@pytest.fixture
def week():
    root = Path(__file__).resolve().parents[1]
    data = load_planning_context(root / "05_data/hr_simulator/planning_week.json")
    return build_week_context(data, date(2026, 10, 12))


def test_missing_roles_are_visible_and_simulated_proposal_keeps_agreed_shifts(week):
    before = check_week(week, week.assignments)
    assert before.uncovered
    proposal = propose_week(week, week.assignments)
    assert proposal.source == "simulated"
    assert all(c["action"] == "assign" for c in proposal.changes)
    assert {a.fact_id for a in week.assignments}.issubset({a.fact_id for a in proposal.assignments})
    assert proposal.review.uncovered_count <= len(before.uncovered)


def test_one_person_cannot_fill_simultaneous_separate_roles(week):
    activity = next(a for a in week.activities if a.id == "W1-1-event")
    same = [Assignment(activity_id=activity.id, person_id="KP-ANS-134", skill="vertskap", agreed=False, fact_id="X1"),
            Assignment(activity_id=activity.id, person_id="KP-ANS-134", skill="formidling", agreed=False, fact_id="X2")]
    review = check_week(week, [*week.assignments, *same])
    assert any(i["kind"] == "overlap" for i in review.violations)


def test_unknown_training_is_unresolved_not_qualified(week):
    candidate = candidate_status(week, week.assignments, "W1-4-event", "POOL-01", "vertskap")
    assert candidate["eligible"] is False
    assert "opplæring" in candidate["reason"]


def test_confirmed_contact_is_preferred_for_new_shift(week):
    from datetime import datetime
    week.contacts.append(Contact(activity_id="W1-1-event", person_id="KP-ANS-006", status="ja",
                                 recorded_at=datetime(2026, 10, 12, 9), fact_id="TEST-JA"))
    proposal = propose_week(week, week.assignments)
    school_host = next(c for c in proposal.changes if c["activity_id"] == "W1-1-event" and c["skill"] == "vertskap")
    assert school_host["person_id"] == "KP-ANS-006"


def test_proposal_cannot_move_fixed_event_time(week):
    proposal = propose_week(week, week.assignments)
    proposal.changes.append({"action": "move", "activity_id": "W1-4-event", "starts_at": "2026-10-16T18:00"})
    with pytest.raises(ValueError):
        evaluate_proposal(week, week.assignments, proposal)


def test_rest_is_checked_across_week_boundary(week):
    from datetime import datetime
    sunday = Activity(id="SUNDAY", title="Søndag kveld", kind="event", starts_at=datetime(2026, 10, 18, 20),
                      ends_at=datetime(2026, 10, 18, 23), work_start=datetime(2026, 10, 18, 19, 30),
                      work_end=datetime(2026, 10, 18, 23, 30), requirements={"vertskap": 1},
                      source_ids=["K-OLJE"], synthetic=True)
    monday = Activity(id="MONDAY", title="Mandag morgen", kind="fixed", starts_at=datetime(2026, 10, 19, 8),
                      ends_at=datetime(2026, 10, 19, 12), work_start=datetime(2026, 10, 19, 7, 30),
                      work_end=datetime(2026, 10, 19, 12, 30), requirements={"vertskap": 1},
                      source_ids=["K-OLJE"], synthetic=True)
    week.activities.append(sunday)
    week.adjacent_activities.append(monday)
    week.adjacent_assignments.append(Assignment(activity_id="MONDAY", person_id="KP-ANS-006", skill="vertskap", agreed=True, fact_id="MON"))
    result = check_week(week, [*week.assignments, Assignment(activity_id="SUNDAY", person_id="KP-ANS-006", skill="vertskap", agreed=False, fact_id="SUN")])
    assert any(x["kind"] == "rest" and "MONDAY" in x["activities"] for x in result.unresolved)


def test_untrained_existing_shift_does_not_hide_need(week):
    from datetime import datetime
    activity = next(a for a in week.activities if a.id == "W1-1-event")
    person = next(p for p in week.persons if p.id == "KP-ANS-006")
    person.training["vertskap"] = False
    existing = Assignment(activity_id=activity.id, person_id=person.id, skill="vertskap", agreed=True, fact_id="BAD-TRAINING")
    proposal = propose_week(week, [*week.assignments, existing])
    assert any(c["action"] == "assign" and c["activity_id"] == activity.id and c["skill"] == "vertskap" for c in proposal.changes)


def test_overstaffed_proposal_is_rejected(week):
    proposal = propose_week(week, week.assignments)
    proposed = next(a for a in proposal.assignments if not a.agreed)
    other = next(p for p in week.persons if p.id != proposed.person_id and proposed.skill in p.skills and p.training.get(proposed.skill))
    extra = Assignment(activity_id=proposed.activity_id, person_id=other.id, skill=proposed.skill, agreed=False, fact_id="EXTRA")
    proposal.assignments.append(extra)
    proposal.changes.append({"action": "assign", "activity_id": extra.activity_id, "person_id": extra.person_id,
                             "skill": extra.skill, "fact_id": extra.fact_id})
    with pytest.raises(ValueError):
        evaluate_proposal(week, week.assignments, proposal)


def test_first_week_boundary_without_monday_activity(week):
    week.activities = [a for a in week.activities if a.starts_at.date() > week.week_start]
    review = check_week(week, [a for a in week.assignments if a.activity_id in {x.id for x in week.activities}])
    assert any(i["kind"] == "history_boundary" for i in review.unresolved)
    week.activities = []
    assert check_week(week, []).uncovered_count == 0
