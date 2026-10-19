"""Isolert lokal SQLite-state for ukeplanøvelsen."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from .context import Assignment, Contact, PlanningContext, build_week_context
from .planning import candidate_status, check_week, propose_week

SCENARIOS = {"HR-001", "HR-002", "HR-003"}


class StateError(Exception):
    def __init__(self, code: str, message: str, status: int):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


def valid_workspace(workspace: str) -> str:
    if workspace != "work" and workspace not in {f"demo:{s}" for s in SCENARIOS}:
        raise StateError("unknown_workspace", "Ukjent arbeidsområde", 404)
    return workspace


class PlanningStore:
    def __init__(self, path: Path, context: PlanningContext):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.context = context
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS workspace_state (
                    workspace TEXT PRIMARY KEY, version INTEGER NOT NULL,
                    assignments_json TEXT NOT NULL, contacts_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY, workspace TEXT NOT NULL, week_start TEXT NOT NULL,
                    base_version INTEGER NOT NULL, payload_json TEXT NOT NULL,
                    decisions_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL,
                    event_json TEXT NOT NULL, recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def _seed(self, db, workspace):
        contacts = {f"{c.activity_id}:{c.person_id}": c.model_dump(mode="json") for c in self.context.contacts}
        if workspace.startswith("demo:"):
            overlays = json.loads((Path(__file__).resolve().parents[3] / "05_data/hr_simulator/demo_seed.json").read_text(encoding="utf-8"))
            for entry in overlays[workspace.split(":", 1)[1]]["contacts"]:
                contacts[f"{entry['activity_id']}:{entry['person_id']}"] = entry
        db.execute("INSERT OR IGNORE INTO workspace_state VALUES(?,?,?,?)", (
            workspace, 1,
            json.dumps([a.model_dump(mode="json") for a in self.context.assignments]),
            json.dumps(contacts),
        ))

    def _state(self, db, workspace):
        valid_workspace(workspace)
        self._seed(db, workspace)
        return db.execute("SELECT * FROM workspace_state WHERE workspace=?", (workspace,)).fetchone()

    def _context_for_state(self, row, week_start):
        week = build_week_context(self.context, __import__("datetime").date.fromisoformat(week_start))
        assignments = [Assignment.model_validate(a) for a in json.loads(row["assignments_json"])]
        ids = {a.id for a in week.activities}
        week.assignments = [a for a in assignments if a.activity_id in ids]
        week.adjacent_assignments = [a for a in assignments if a.activity_id not in ids]
        week.contacts = [Contact.model_validate(c) for c in json.loads(row["contacts_json"]).values()
                         if c["activity_id"] in ids]
        return week

    def _week_context(self, workspace: str, week_start: str):
        with self._connect() as db:
            row = self._state(db, workspace)
            return self._context_for_state(row, week_start)

    def snapshot(self, workspace: str, week_start: str):
        try:
            week = build_week_context(self.context, __import__("datetime").date.fromisoformat(week_start))
        except ValueError as exc:
            raise StateError("unknown_week", "Ukjent uke", 404) from exc
        with self._connect() as db:
            row = self._state(db, workspace)
            week = self._context_for_state(row, week_start)
            contacts = json.loads(row["contacts_json"])
        selected = week.assignments
        check = check_week(week, selected)
        activities = []
        for activity in week.activities:
            gaps = [g for g in check.uncovered if g["activity_id"] == activity.id]
            activities.append({**activity.model_dump(mode="json"), "status": "udekket" if gaps else "dekket",
                               "uncovered": gaps, "next_action": "Finn kvalifisert kandidat" if gaps else "Kontroller oppmøte"})
        return {"workspace": workspace, "week_start": week_start, "version": row["version"],
                "context_version": self.context.version, "activities": activities,
                "assignments": [a.model_dump(mode="json") for a in selected],
                "contacts": {key: value for key, value in contacts.items() if value["activity_id"] in {a.id for a in week.activities}},
                "checks": check.as_dict(), "next_action": "Behandle udekkede roller" if check.uncovered else "Kontroller plan og kontaktstatus"}

    def candidates(self, workspace: str, activity_id: str):
        valid_workspace(workspace)
        activity = next((a for a in self.context.activities if a.id == activity_id), None)
        if activity is None:
            raise StateError("unknown_activity", "Ukjent aktivitet", 404)
        week = self._week_context(workspace, next(w.isoformat() for w in self.context.weeks if w <= activity.starts_at.date() < w + __import__("datetime").timedelta(days=7)))
        snap = self.snapshot(workspace, week.week_start.isoformat())
        assigned = [Assignment.model_validate(a) for a in snap["assignments"]]
        return {"activity_id": activity_id, "candidates": [candidate_status(week, assigned, activity_id, p.id, skill)
                for skill in activity.requirements for p in week.persons]}

    def record_contact(self, workspace: str, activity_id: str, person_id: str, status: str, expected_version: int):
        valid_workspace(workspace)
        if status not in {"ikke_kontaktet", "forespurt", "ja", "nei", "trukket"}:
            raise StateError("invalid_status", "Ukjent kontaktstatus", 422)
        activity = next((a for a in self.context.activities if a.id == activity_id), None)
        person = next((p for p in self.context.persons if p.id == person_id), None)
        if activity is None or person is None:
            raise StateError("unknown_reference", "Ukjent aktivitet eller person", 404)
        if (person.employment_start and activity.starts_at.date() < person.employment_start or
                person.employment_end and activity.starts_at.date() > person.employment_end):
            raise StateError("historical_person", "Tidligere ansatt kan ikke kontaktes for en demovakt", 422)
        from datetime import datetime
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._state(db, workspace)
            if row["version"] != expected_version:
                raise StateError("stale_version", "Planen er endret. Hent den på nytt.", 409)
            contacts = json.loads(row["contacts_json"])
            key = f"{activity_id}:{person_id}"
            contacts[key] = {"activity_id": activity_id, "person_id": person_id, "status": status,
                             "recorded_at": datetime.now().isoformat(timespec="seconds"), "fact_id": f"C-{uuid4().hex[:12]}"}
            db.execute("UPDATE workspace_state SET version=version+1, contacts_json=? WHERE workspace=?",
                       (json.dumps(contacts), workspace))
            db.execute("INSERT INTO audit(workspace,event_json) VALUES(?,?)", (workspace, json.dumps({"kind": "contact", **contacts[key]})))
        return {"version": expected_version + 1, "status": status}

    def create_proposal(self, workspace: str, week_start: str, source: str, model: str | None = None):
        if source not in {"simulated", "openai"}:
            raise StateError("unsupported_source", "Ukjent forslagstype", 422)
        snap = self.snapshot(workspace, week_start)
        week = self._week_context(workspace, week_start)
        current = [Assignment.model_validate(a) for a in snap["assignments"]]
        if source == "openai":
            from .openai_planner import ModelProposalError, generate_week_proposal
            try:
                proposal = generate_week_proposal(week, current, model=model or "")
            except ModelProposalError as exc:
                raise StateError("model_proposal_failed", str(exc), 422) from exc
        else:
            proposal = propose_week(week, current)
        payload = {"id": uuid4().hex, "workspace": workspace, "week_start": week_start,
                   "base_version": snap["version"], "source": source, "context_version": proposal.context_version,
                   "rationale": proposal.rationale, "source_ids": proposal.source_ids,
                   "missing_information": proposal.missing_information, "changes": proposal.changes,
                   "review": proposal.review.as_dict(), "model": proposal.model, "usage": proposal.usage}
        with self._connect() as db:
            db.execute("INSERT INTO proposals VALUES(?,?,?,?,?,?)", (payload["id"], workspace, week_start,
                       snap["version"], json.dumps(payload), "{}"))
        return {**payload, "decisions": {}}

    def latest_proposal(self, workspace: str, week_start: str):
        self.snapshot(workspace, week_start)
        with self._connect() as db:
            row = db.execute("SELECT * FROM proposals WHERE workspace=? AND week_start=? ORDER BY rowid DESC LIMIT 1",
                             (workspace, week_start)).fetchone()
        if row is None:
            return {"proposal": None}
        return {**json.loads(row["payload_json"]), "base_version": row["base_version"],
                "decisions": json.loads(row["decisions_json"])}

    def decide(self, proposal_id: str, workspace: str, fact_id: str, decision: str, rationale: str, expected_version: int):
        valid_workspace(workspace)
        if decision not in {"approved", "rejected"} or not rationale.strip():
            raise StateError("invalid_decision", "Beslutning og begrunnelse kreves", 422)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._state(db, workspace)
            prop = db.execute("SELECT * FROM proposals WHERE id=? AND workspace=?", (proposal_id, workspace)).fetchone()
            if prop is None:
                raise StateError("unknown_proposal", "Ukjent forslag", 404)
            if row["version"] != expected_version or prop["base_version"] != expected_version:
                raise StateError("stale_version", "Planen er endret. Hent nytt forslag.", 409)
            payload = json.loads(prop["payload_json"])
            decisions = json.loads(prop["decisions_json"])
            change = next((c for c in payload["changes"] if c["fact_id"] == fact_id), None)
            if change is None:
                raise StateError("unknown_change", "Ukjent endring", 404)
            if fact_id in decisions:
                raise StateError("already_decided", "Endringen er allerede behandlet", 409)
            assignments = json.loads(row["assignments_json"])
            if decision == "approved" and change["action"] == "remove":
                target = next((a for a in assignments if a["fact_id"] == fact_id), None)
                contacts = json.loads(row["contacts_json"])
                contact = contacts.get(f"{change['activity_id']}:{change['person_id']}", {})
                if target is None or contact.get("status") not in {"nei", "trukket"}:
                    raise StateError("invalid_removal", "Avmelding eller vakt mangler", 422)
                assignments.remove(target)
            elif decision == "approved":
                activity = next(a for a in self.context.activities if a.id == change["activity_id"])
                week_start = next(w for w in self.context.weeks if w <= activity.starts_at.date() < w + __import__("datetime").timedelta(days=7))
                week = self._context_for_state(row, week_start.isoformat())
                selected = week.assignments
                cand = candidate_status(week, selected, change["activity_id"], change["person_id"], change["skill"])
                if not cand["eligible"]:
                    raise StateError("blocked_candidate", cand["reason"], 422)
                new_assignment = {"activity_id": change["activity_id"], "person_id": change["person_id"],
                                  "skill": change["skill"], "agreed": False, "fact_id": fact_id}
                review = check_week(week, [*selected, Assignment.model_validate(new_assignment)])
                if review.violations:
                    raise StateError("invalid_plan", "Endringen gir harde brudd", 422)
                assignments.append(new_assignment)
            decisions[fact_id] = {"decision": decision, "rationale": rationale}
            db.execute("UPDATE workspace_state SET version=version+1, assignments_json=? WHERE workspace=?",
                       (json.dumps(assignments), workspace))
            db.execute("UPDATE proposals SET base_version=?, decisions_json=? WHERE id=?",
                       (expected_version + 1, json.dumps(decisions), proposal_id))
            db.execute("INSERT INTO audit(workspace,event_json) VALUES(?,?)", (workspace, json.dumps({"kind": "decision", "proposal_id": proposal_id,
                                                                                  "fact_id": fact_id, "decision": decision, "rationale": rationale})))
        return {"version": expected_version + 1, "decisions": decisions}

    def reset_demo(self, scenario_id: str):
        if scenario_id not in SCENARIOS:
            raise StateError("unknown_scenario", "Ukjent demoscenario", 404)
        workspace = f"demo:{scenario_id}"
        with self._connect() as db:
            db.execute("DELETE FROM proposals WHERE workspace=?", (workspace,))
            db.execute("DELETE FROM workspace_state WHERE workspace=?", (workspace,))
            db.execute("DELETE FROM audit WHERE workspace=?", (workspace,))
            self._seed(db, workspace)
        return {"workspace": workspace, "reset": True}
