"""Ende-til-ende kontroll av det versjonerte, fiktive persongrunnlaget."""
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from src.kunstpixel.hr_simulator.api import create_app
from src.kunstpixel.hr_simulator.staff_data import read_rows, write_rows


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "05_data/hr_simulator/redigeringsbord/UTKAST-ansatte-kandidater.csv"


def client(tmp_path):
    draft = tmp_path / "staff.csv"
    shutil.copyfile(DRAFT, draft)
    return TestClient(create_app(tmp_path / "state.sqlite3", draft)), draft


def test_all_archive_people_are_searchable_but_only_active_can_staff(tmp_path):
    app, _ = client(tmp_path)
    all_people = app.get("/api/planning/people?query=KP-ANS&page_size=100").json()
    active = app.get("/api/planning/people?status=active&page_size=100").json()
    historical = app.get("/api/planning/people?status=historical&page_size=100").json()
    assert all_people["total"] == 168
    assert active["total"] == 65
    assert historical["total"] == 103
    old = historical["people"][0]
    candidates = app.get("/api/planning/activities/W1-1-event/candidates").json()["candidates"]
    relevant = [c for c in candidates if c["person_id"] == old["id"]]
    assert relevant and all(not c["eligible"] for c in relevant)
    assert all("ikke ansatt" in c["reason"] for c in relevant)
    snap = app.get("/api/planning/weeks/2026-10-12").json()
    blocked_contact = app.post("/api/planning/contacts", json={"workspace":"work",
        "activity_id":"W1-1-event", "person_id":old["id"], "status":"forespurt",
        "expected_version":snap["version"]})
    assert blocked_contact.status_code == 422
    assert all(p["field_sources"]["skills"] == "fiktiv stillingsmapping:v1" for p in active["people"])
    cross_skill = next(c for c in candidates if c["person_id"] == "KP-ANS-134" and c["skill"] == "formidling")
    assert not cross_skill["eligible"] and "opplæring" in cross_skill["reason"]


def test_scenarios_use_archive_ids_and_keep_independent_state(tmp_path):
    app, _ = client(tmp_path)
    states = [app.get(f"/api/planning/weeks/2026-10-12?workspace=demo:HR-00{i}").json() for i in range(1, 4)]
    assert len({str((x["assignments"], x["contacts"])) for x in states}) == 3
    assert [x["checks"]["uncovered_count"] for x in states] == [5, 4, 5]
    assert states[0]["contacts"]["W1-0-fixed:KP-ANS-006"]["status"] == "trukket"
    assert states[1]["contacts"]["W1-4-event:KP-ANS-134"]["status"] == "nei"
    assert states[2]["contacts"]["W1-1-event:KP-ANS-018"]["status"] == "trukket"
    assert all(a["person_id"].startswith("KP-ANS-") for state in states for a in state["assignments"])
    work = app.get("/api/planning/weeks/2026-10-12?workspace=work").json()
    one = states[0]
    change = app.post("/api/planning/contacts", json={"workspace":"demo:HR-001",
        "activity_id":"W1-4-event", "person_id":"KP-ANS-134", "status":"ja",
        "expected_version":one["version"]})
    assert change.status_code == 200
    assert app.get("/api/planning/weeks/2026-10-12?workspace=work").json()["version"] == work["version"]
    assert app.post("/api/planning/demo/scenarios/HR-001/reset",
                    headers={"X-Kunstpixel-Action":"demo-reset"}).status_code == 200
    assert app.get("/api/planning/weeks/2026-10-12?workspace=demo:HR-001").json()["version"] == 1


def test_invalid_draft_cannot_activate_and_valid_version_preserves_old_status(tmp_path):
    app, draft = client(tmp_path)
    base = app.get("/api/planning/datasets").json()["active_version"]
    initial = app.get("/api/planning/weeks/2026-10-12").json()
    contact = app.post("/api/planning/contacts", json={"workspace":"work",
        "activity_id":"W1-4-event", "person_id":"KP-ANS-134", "status":"ja",
        "expected_version":initial["version"]})
    assert contact.status_code == 200
    rows = read_rows(draft)
    rows[1]["ansatt_id"] = rows[0]["ansatt_id"]
    write_rows(draft, rows)
    bad = app.post("/api/planning/datasets/validate", json={}).json()
    assert not bad["valid"]
    assert app.post("/api/planning/datasets/activate", json={"expected_checksum":bad["checksum"]}).status_code == 422
    assert app.get("/api/planning/datasets").json()["active_version"] == base

    rows[1]["ansatt_id"] = "KP-ANS-002"
    editable = next(r for r in rows if r["ansatt_id"] == "KP-ANS-140")
    editable["training"] = ""
    write_rows(draft, rows)
    ready = app.post("/api/planning/datasets/validate", json={}).json()
    assert ready["valid"] and ready["changed_people"] == 1
    with draft.open("a", encoding="utf-8") as handle:
        handle.write("\n")
    assert app.post("/api/planning/datasets/activate", json={"expected_checksum":ready["checksum"]}).status_code == 409
    write_rows(draft, rows)
    ready = app.post("/api/planning/datasets/validate", json={}).json()
    activated = app.post("/api/planning/datasets/activate", json={"expected_checksum":ready["checksum"]})
    assert activated.status_code == 200, activated.text
    new_version = activated.json()["active_version"]
    assert new_version != base
    assert app.get("/api/planning/weeks/2026-10-12").json()["version"] == 1
    updated = app.get("/api/planning/people?query=KP-ANS-140").json()["people"][0]
    assert updated["field_sources"]["training"] == "redigert fiktiv arbeidskopi"
    old = app.get(f"/api/planning/weeks/2026-10-12?dataset_version={base}").json()
    assert old["contacts"]["W1-4-event:KP-ANS-134"]["status"] == "ja"
    restarted = TestClient(create_app(tmp_path / "state.sqlite3", draft))
    assert restarted.get("/api/planning/datasets").json()["active_version"] == new_version
    assert restarted.get(f"/api/planning/weeks/2026-10-12?dataset_version={base}").json()["version"] == 2


def test_unchanged_draft_is_noop_and_reverting_restores_base_version(tmp_path):
    app, draft = client(tmp_path)
    base = app.get("/api/planning/datasets").json()["active_version"]
    unchanged = app.post("/api/planning/datasets/validate", json={}).json()
    assert unchanged["valid"] and unchanged["changed_people"] == 0
    assert unchanged["version"] == base
    assert app.post("/api/planning/datasets/activate",
                    json={"expected_checksum":unchanged["checksum"]}).json()["active_version"] == base
    rows = read_rows(draft)
    person = next(row for row in rows if row["ansatt_id"] == "KP-ANS-140")
    original_training = person["training"]
    person["training"] = ""
    write_rows(draft, rows)
    changed = app.post("/api/planning/datasets/validate", json={}).json()
    new = app.post("/api/planning/datasets/activate",
                   json={"expected_checksum":changed["checksum"]}).json()["active_version"]
    assert new != base
    person["training"] = original_training
    write_rows(draft, rows)
    reverted = app.post("/api/planning/datasets/validate", json={}).json()
    assert reverted["version"] == base
    assert app.post("/api/planning/datasets/activate",
                    json={"expected_checksum":reverted["checksum"]}).json()["active_version"] == base
    assert app.get("/api/planning/datasets").json()["versions"] == [base, new]
