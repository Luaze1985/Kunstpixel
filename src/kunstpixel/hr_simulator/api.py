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
from .datasets import DatasetRegistry
from .store import PlanningStore, StateError, SCENARIOS

ROOT = Path(__file__).resolve().parents[3]


class ContactInput(BaseModel):
    workspace: str
    activity_id: str
    person_id: str
    status: Literal["ikke_kontaktet", "forespurt", "ja", "nei", "trukket"]
    expected_version: int
    dataset_version: str | None = None


class ProposalInput(BaseModel):
    workspace: str
    week_start: str
    source: Literal["simulated", "openai"]
    dataset_version: str | None = None


class DecisionInput(BaseModel):
    workspace: str
    fact_id: str
    decision: Literal["approved", "rejected"]
    rationale: str
    expected_version: int
    dataset_version: str | None = None


class ActivationInput(BaseModel):
    expected_checksum: str


def create_app(state_path: Path | None = None, draft_path: Path | None = None, ai_state_path: Path | None = None) -> FastAPI:
    base = ROOT / "05_data/hr_simulator"
    registry = DatasetRegistry(base / "planning_week.json",
        state_path or base / "local_state_v2.sqlite3",
        draft_path or base / "redigeringsbord/UTKAST-ansatte-kandidater.csv",
        base / "staff_source.csv")
    app = FastAPI(title="Kunstpixel museumsuke", docs_url="/api/docs")
    app.state.planning_store = registry.store()
    app.state.datasets = registry
    from .ai_registry import AIRegistry
    from .ai_api import create_router
    ai_path = ai_state_path or (state_path.parent if state_path else base) / "ai_observations.sqlite3"
    app.include_router(create_router(AIRegistry(base, ai_path)))

    @app.exception_handler(StateError)
    async def state_error(_request: Request, exc: StateError):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=exc.status, content={"code": exc.code, "message": exc.message, "details": {}})

    @app.get("/api/planning/weeks")
    def weeks():
        return {"weeks": [w.isoformat() for w in registry.context().weeks]}

    @app.get("/api/planning/datasets")
    def datasets():
        return {"active_version": registry.active_version, "versions": registry.versions()}

    @app.post("/api/planning/datasets/validate")
    def validate_dataset():
        return registry.validate()

    @app.post("/api/planning/datasets/activate")
    def activate_dataset(body: ActivationInput):
        result = registry.activate(body.expected_checksum)
        app.state.planning_store = registry.store()
        return result

    @app.get("/api/planning/people")
    def people(query: str = "", status: str = "all", page: int = 1, page_size: int = 20,
               week_start: str | None = None,
               dataset_version: str | None = None):
        if status not in {"all", "active", "historical"} or page < 1 or not 1 <= page_size <= 100:
            raise StateError("invalid_filter", "Ugyldig personfilter", 422)
        context = registry.context(dataset_version)
        if week_start and week_start not in {w.isoformat() for w in context.weeks}:
            raise StateError("unknown_week", "Ukjent uke", 404)
        day = __import__("datetime").date.fromisoformat(week_start) if week_start else context.weeks[0]
        employees = [p for p in context.persons if p.person_type == "employee"]
        matched = []
        for p in employees:
            active = (p.employment_start is None or p.employment_start <= day) and (p.employment_end is None or day <= p.employment_end)
            if status == "active" and not active or status == "historical" and active:
                continue
            if query.casefold() not in f"{p.id} {p.name} {p.title} {p.department}".casefold():
                continue
            matched.append({"id": p.id, "name": p.name, "title": p.title,
                            "department": p.department, "active": active,
                            "employment_start": p.employment_start, "employment_end": p.employment_end,
                            "skills": p.skills, "training": p.training,
                            "field_sources": p.field_sources})
        start = (page - 1) * page_size
        return {"total": len(matched), "page": page, "people": matched[start:start + page_size]}

    @app.get("/api/planning/data-quality")
    def data_quality():
        path = base / "archive_quality.json"
        return json.loads(path.read_text(encoding="utf-8"))

    @app.get("/api/planning/sources")
    def sources():
        path = ROOT / "04_knowledge/04_domain/projects/hr_simulator/kilder.json"
        return {"sources": json.loads(path.read_text(encoding="utf-8"))}

    @app.get("/api/planning/weeks/{week_start}")
    def get_week(week_start: str, workspace: str = "work", dataset_version: str | None = None):
        return registry.store(dataset_version).snapshot(workspace, week_start)

    @app.get("/api/planning/activities/{activity_id}/candidates")
    def get_candidates(activity_id: str, workspace: str = "work", dataset_version: str | None = None):
        return registry.store(dataset_version).candidates(workspace, activity_id)

    @app.post("/api/planning/contacts")
    def post_contact(body: ContactInput):
        return registry.store(body.dataset_version).record_contact(body.workspace, body.activity_id, body.person_id, body.status, body.expected_version)

    @app.post("/api/planning/proposals")
    def post_proposal(body: ProposalInput):
        if body.source == "openai":
            model = os.environ.get("KUNSTPIXEL_OPENAI_MODEL", "").strip()
            if not os.environ.get("OPENAI_API_KEY") or not model:
                raise StateError("model_not_configured", "OpenAI API-nøkkel og modellnavn må settes på serveren", 503)
            return registry.store(body.dataset_version).create_proposal(body.workspace, body.week_start, body.source, model=model)
        return registry.store(body.dataset_version).create_proposal(body.workspace, body.week_start, body.source)

    @app.get("/api/planning/proposals/latest")
    def latest_proposal(workspace: str = "work", week_start: str = "", dataset_version: str | None = None):
        return registry.store(dataset_version).latest_proposal(workspace, week_start)

    @app.get("/api/planning/model")
    def model_status():
        model = os.environ.get("KUNSTPIXEL_OPENAI_MODEL", "").strip()
        return {"configured": bool(model and os.environ.get("OPENAI_API_KEY")), "model": model or None}

    @app.post("/api/planning/proposals/{proposal_id}/decisions")
    def post_decision(proposal_id: str, body: DecisionInput):
        return registry.store(body.dataset_version).decide(proposal_id, body.workspace, body.fact_id, body.decision, body.rationale, body.expected_version)

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
    def reset(scenario_id: str, x_kunstpixel_action: str | None = Header(default=None), dataset_version: str | None = None):
        if x_kunstpixel_action != "demo-reset":
            raise StateError("missing_action_header", "Demo-reset krever handling fra lokal arbeidsflate", 403)
        return registry.store(dataset_version).reset_demo(scenario_id)

    web = Path(__file__).parent / "web"
    app.mount("/static", StaticFiles(directory=web), name="static")

    @app.get("/")
    def index():
        return FileResponse(web / "index.html")

    return app
