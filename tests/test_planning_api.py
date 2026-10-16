from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from src.kunstpixel.hr_simulator.api import create_app


def client(tmp_path):
    return TestClient(create_app(tmp_path / "state.sqlite3"))


def test_contact_yes_is_not_assignment_and_survives_restart(tmp_path):
    app = client(tmp_path)
    url = "/api/planning/weeks/2026-10-12?workspace=work"
    before = app.get(url).json()
    aid = "W1-4-event"
    pid = "EMP-08"
    response = app.post("/api/planning/contacts", json={"workspace": "work", "activity_id": aid,
                        "person_id": pid, "status": "ja", "expected_version": before["version"]})
    assert response.status_code == 200
    after = client(tmp_path).get(url).json()
    assert after["contacts"][f"{aid}:{pid}"]["status"] == "ja"
    assert not any(a["activity_id"] == aid and a["person_id"] == pid for a in after["assignments"])


def test_stale_version_is_conflict_and_demo_reset_is_isolated(tmp_path):
    app = client(tmp_path)
    initial = app.get("/api/planning/weeks/2026-10-12?workspace=work").json()
    body = {"workspace": "work", "activity_id": "W1-4-event", "person_id": "EMP-08",
            "status": "forespurt", "expected_version": initial["version"]}
    assert app.post("/api/planning/contacts", json=body).status_code == 200
    assert app.post("/api/planning/contacts", json=body).status_code == 409
    demo = app.get("/api/planning/weeks/2026-10-12?workspace=demo:HR-001").json()
    demo_body = {**body, "workspace": "demo:HR-001", "status": "ja", "expected_version": demo["version"]}
    assert app.post("/api/planning/contacts", json=demo_body).status_code == 200
    assert app.post("/api/planning/demo/scenarios/HR-001/reset", headers={"X-Kunstpixel-Action": "demo-reset"}).status_code == 200
    reset = app.get("/api/planning/weeks/2026-10-12?workspace=demo:HR-001").json()
    work = app.get("/api/planning/weeks/2026-10-12?workspace=work").json()
    assert reset["contacts"][f"W1-4-event:EMP-08"]["status"] == "forespurt"
    assert work["contacts"][f"W1-4-event:EMP-08"]["status"] == "forespurt"


def test_proposal_decision_is_persisted(tmp_path):
    app = client(tmp_path)
    response = app.post("/api/planning/proposals", json={"workspace": "work", "week_start": "2026-10-12", "source": "simulated"})
    assert response.status_code == 200, response.text
    proposal = response.json()
    assert proposal["changes"]
    first = proposal["changes"][0]
    result = app.post(f"/api/planning/proposals/{proposal['id']}/decisions", json={
        "workspace": "work", "fact_id": first["fact_id"], "decision": "approved",
        "rationale": "Øvelsesbeslutning", "expected_version": proposal["base_version"]})
    assert result.status_code == 200, result.text
    after = client(tmp_path).get("/api/planning/weeks/2026-10-12?workspace=work").json()
    assert any(a["fact_id"] == first["fact_id"] for a in after["assignments"])
    saved = client(tmp_path).get("/api/planning/proposals/latest?workspace=work&week_start=2026-10-12").json()
    assert saved["decisions"][first["fact_id"]]["decision"] == "approved"
    assert app.post(f"/api/planning/proposals/{proposal['id']}/decisions", json={
        "workspace": "work", "fact_id": first["fact_id"], "decision": "approved",
        "rationale": "igjen", "expected_version": after["version"]}).status_code == 409


def test_openai_requires_explicit_config_and_does_not_change_plan(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("KUNSTPIXEL_OPENAI_MODEL", raising=False)
    app = client(tmp_path)
    before = app.get("/api/planning/weeks/2026-10-12").json()
    response = app.post("/api/planning/proposals", json={"workspace": "work", "week_start": "2026-10-12", "source": "openai"})
    assert response.status_code == 503
    after = app.get("/api/planning/weeks/2026-10-12").json()
    assert after["version"] == before["version"]


def test_demo_mode_exposes_distinct_legacy_scenarios_without_personnel_cases(tmp_path):
    app = client(tmp_path)
    one = app.get("/api/planning/demo/scenarios/HR-001").json()
    two = app.get("/api/planning/demo/scenarios/HR-002").json()
    assert one["title"] != two["title"]
    assert one["synthetic"] is True
    assert "hr_cases" not in one


def test_withdrawal_preserves_agreed_shift_until_explicit_decision(tmp_path):
    app = client(tmp_path)
    url = "/api/planning/weeks/2026-10-12?workspace=work"
    before = app.get(url).json()
    agreed = next(a for a in before["assignments"] if a["agreed"])
    response = app.post("/api/planning/contacts", json={"workspace": "work", "activity_id": agreed["activity_id"],
        "person_id": agreed["person_id"], "status": "trukket", "expected_version": before["version"]})
    assert response.status_code == 200
    after = app.get(url).json()
    assert any(a["fact_id"] == agreed["fact_id"] for a in after["assignments"])
    assert any(g["activity_id"] == agreed["activity_id"] and g["skill"] == agreed["skill"] for g in after["checks"]["uncovered"])
    proposal = app.post("/api/planning/proposals", json={"workspace": "work", "week_start": "2026-10-12", "source": "simulated"}).json()
    removal = next(c for c in proposal["changes"] if c["action"] == "remove" and c["fact_id"] == agreed["fact_id"])
    decision = app.post(f"/api/planning/proposals/{proposal['id']}/decisions", json={"workspace": "work",
        "fact_id": removal["fact_id"], "decision": "approved", "rationale": "Avmelding kontrollert", "expected_version": after["version"]})
    assert decision.status_code == 200, decision.text
    assert not any(a["fact_id"] == agreed["fact_id"] for a in app.get(url).json()["assignments"])


def test_approved_shift_in_next_week_is_used_for_candidate_check(tmp_path):
    app = client(tmp_path)
    week2 = app.get("/api/planning/weeks/2026-10-19?workspace=work").json()
    # Den lokale kilden inneholder alle fire ukene, men en godkjent endring må også bli synlig i nabouken.
    proposal = app.post("/api/planning/proposals", json={"workspace": "work", "week_start": "2026-10-19", "source": "simulated"}).json()
    if not proposal["changes"]:
        return
    first = next(c for c in proposal["changes"] if c["action"] == "assign")
    result = app.post(f"/api/planning/proposals/{proposal['id']}/decisions", json={"workspace": "work",
        "fact_id": first["fact_id"], "decision": "approved", "rationale": "Test", "expected_version": week2["version"]})
    assert result.status_code == 200, result.text
    store = app.app.state.planning_store
    week1 = store._week_context("work", "2026-10-12")
    assert any(a.fact_id == first["fact_id"] for a in week1.adjacent_assignments)


def test_demo_scenarios_start_with_distinct_week_states(tmp_path):
    app = client(tmp_path)
    states = [app.get(f"/api/planning/weeks/2026-10-12?workspace=demo:HR-00{i}").json() for i in range(1, 4)]
    signatures = [(s["assignments"], s["contacts"]) for s in states]
    assert len({str(x) for x in signatures}) == 3


def test_demo_reset_requires_explicit_request_header(tmp_path):
    app = client(tmp_path)
    assert app.post("/api/planning/demo/scenarios/HR-001/reset").status_code == 403
