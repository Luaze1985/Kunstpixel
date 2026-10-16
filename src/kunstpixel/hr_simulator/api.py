"""Lokal API-prosess for fiktiv bemanningsplanlegging."""
from __future__ import annotations

from pathlib import Path
import json
import os
from typing import Literal

from fastapi import FastAPI, Request, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .context import load_planning_context
from .store import PlanningStore, StateError, SCENARIOS

ROOT = Path(__file__).resolve().parents[3]


class ContactInput(BaseModel):
    workspace: str
    activity_id: str
    person_id: str
    status: Literal["ikke_kontaktet", "forespurt", "ja", "nei", "trukket"]
    expected_version: int


class ProposalInput(BaseModel):
    workspace: str
    week_start: str
    source: Literal["simulated", "openai"]


class DecisionInput(BaseModel):
    workspace: str
    fact_id: str
    decision: Literal["approved", "rejected"]
    rationale: str
    expected_version: int


def create_app(state_path: Path | None = None) -> FastAPI:
    data = load_planning_context(ROOT / "05_data/hr_simulator/planning_week.json")
    store = PlanningStore(state_path or ROOT / "05_data/hr_simulator/local_state.sqlite3", data)
    app = FastAPI(title="Kunstpixel museumsuke", docs_url="/api/docs")
    app.state.planning_store = store

    @app.exception_handler(StateError)
    async def state_error(_request: Request, exc: StateError):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=exc.status, content={"code": exc.code, "message": exc.message, "details": {}})

    @app.get("/api/planning/weeks")
    def weeks():
        return {"weeks": [w.isoformat() for w in data.weeks]}

    @app.get("/api/planning/sources")
    def sources():
        path = ROOT / "04_knowledge/04_domain/projects/hr_simulator/kilder.json"
        return {"sources": json.loads(path.read_text(encoding="utf-8"))}

    @app.get("/api/planning/weeks/{week_start}")
    def get_week(week_start: str, workspace: str = "work"):
        return store.snapshot(workspace, week_start)

    @app.get("/api/planning/activities/{activity_id}/candidates")
    def get_candidates(activity_id: str, workspace: str = "work"):
        return store.candidates(workspace, activity_id)

    @app.post("/api/planning/contacts")
    def post_contact(body: ContactInput):
        return store.record_contact(body.workspace, body.activity_id, body.person_id, body.status, body.expected_version)

    @app.post("/api/planning/proposals")
    def post_proposal(body: ProposalInput):
        if body.source == "openai":
            model = os.environ.get("KUNSTPIXEL_OPENAI_MODEL", "").strip()
            if not os.environ.get("OPENAI_API_KEY") or not model:
                raise StateError("model_not_configured", "OpenAI API-nøkkel og modellnavn må settes på serveren", 503)
            return store.create_proposal(body.workspace, body.week_start, body.source, model=model)
        return store.create_proposal(body.workspace, body.week_start, body.source)

    @app.get("/api/planning/proposals/latest")
    def latest_proposal(workspace: str = "work", week_start: str = ""):
        return store.latest_proposal(workspace, week_start)

    @app.get("/api/planning/model")
    def model_status():
        model = os.environ.get("KUNSTPIXEL_OPENAI_MODEL", "").strip()
        return {"configured": bool(model and os.environ.get("OPENAI_API_KEY")), "model": model or None}

    @app.post("/api/planning/proposals/{proposal_id}/decisions")
    def post_decision(proposal_id: str, body: DecisionInput):
        return store.decide(proposal_id, body.workspace, body.fact_id, body.decision, body.rationale, body.expected_version)

    @app.get("/api/planning/demo/scenarios")
    def demo_scenarios():
        return {"scenarios": [scenario_preview(s) for s in sorted(SCENARIOS)]}

    def scenario_preview(scenario_id: str):
        if scenario_id not in SCENARIOS:
            raise StateError("unknown_scenario", "Ukjent demoscenario", 404)
        path = ROOT / "05_data/hr_simulator/scenarios" / f"{scenario_id}.json"
        scenario = json.loads(path.read_text(encoding="utf-8"))
        overlay = json.loads((ROOT / "05_data/hr_simulator/demo_seed.json").read_text(encoding="utf-8"))[scenario_id]
        return {"id": scenario_id, "title": scenario["title"], "description": scenario["description"],
                "synthetic": scenario["synthetic"], "legacy_date": scenario.get("date"),
                "week_mapping": overlay["mapping"],
                "activities": [{"title": a["title"], "requirements": a["requirements"]} for a in scenario["activities"]]}

    @app.get("/api/planning/demo/scenarios/{scenario_id}")
    def get_demo_scenario(scenario_id: str):
        return scenario_preview(scenario_id)

    @app.post("/api/planning/demo/scenarios/{scenario_id}/reset")
    def reset(scenario_id: str, x_kunstpixel_action: str | None = Header(default=None)):
        if x_kunstpixel_action != "demo-reset":
            raise StateError("missing_action_header", "Demo-reset krever handling fra lokal arbeidsflate", 403)
        return store.reset_demo(scenario_id)

    web = Path(__file__).parent / "web"
    app.mount("/static", StaticFiles(directory=web), name="static")

    @app.get("/")
    def index():
        return FileResponse(web / "index.html")

    return app
