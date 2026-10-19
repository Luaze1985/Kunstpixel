"""Validering og atomisk aktivering av lokale, fiktive personalutkast."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from .context import PlanningContext, build_week_context, load_planning_context
from .planning import check_week
from .staff_data import compile_people, read_rows, validate_draft
from .store import PlanningStore, StateError


class DatasetRegistry:
    def __init__(self, base_path: Path, state_path: Path, draft_path: Path, source_path: Path):
        self.base_path = base_path
        self.state_path = state_path
        self.draft_path = draft_path
        self.source_path = source_path
        self.versions_dir = state_path.parent / "dataset_versions"
        self.pointer_path = state_path.parent / "active_dataset.json"
        self.base = load_planning_context(base_path)
        self.stores: dict[str, PlanningStore] = {}
        self.active_version = self.base.version
        if self.pointer_path.exists():
            pointer = json.loads(self.pointer_path.read_text(encoding="utf-8"))
            candidate = pointer.get("version", "")
            if candidate and (self.versions_dir / f"{candidate}.json").exists():
                self.active_version = candidate

    def versions(self) -> list[str]:
        return [self.base.version, *sorted(p.stem for p in self.versions_dir.glob("*.json"))] if self.versions_dir.exists() else [self.base.version]

    def context(self, version: str | None = None) -> PlanningContext:
        chosen = version or self.active_version
        if chosen == self.base.version:
            return self.base
        if chosen not in self.versions():
            raise StateError("unknown_dataset", "Ukjent dataversjon", 404)
        return load_planning_context(self.versions_dir / f"{chosen}.json")

    def store(self, version: str | None = None) -> PlanningStore:
        chosen = version or self.active_version
        if chosen not in self.stores:
            path = self.state_path if chosen == self.base.version else self.state_path.with_name(f"{self.state_path.stem}-{chosen}.sqlite3")
            self.stores[chosen] = PlanningStore(path, self.context(chosen))
        return self.stores[chosen]

    def _candidate(self) -> tuple[str, PlanningContext, list[str], int]:
        raw = self.draft_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        rows = read_rows(self.draft_path)
        source = read_rows(self.source_path)
        errors = validate_draft(rows, source)
        if errors:
            return digest, self.base, errors[:100], 0
        payload = self.base.model_dump(mode="json")
        payload["version"] = f"staff-{digest[:12]}"
        payload["persons"] = compile_people(rows, self.base.weeks) + [
            p.model_dump(mode="json") for p in self.base.persons if p.person_type != "employee"
        ]
        try:
            candidate = PlanningContext.model_validate(payload)
            if candidate.persons == self.base.persons:
                candidate.version = self.base.version
            for week_start in candidate.weeks:
                week = build_week_context(candidate, week_start)
                check = check_week(week, week.assignments)
                if check.violations or any(item["kind"] == "training" for item in check.unresolved):
                    errors.append(f"Uke {week_start}: avtalte vakter bryter kompetanse, tid eller opplæring")
        except ValueError as exc:
            errors.append(str(exc))
            candidate = self.base
        current = {p.id: p.model_dump(mode="json") for p in self.context().persons}
        changed = sum(current.get(p.id) != p.model_dump(mode="json") for p in candidate.persons)
        return digest, candidate, errors[:100], changed

    def validate(self) -> dict:
        try:
            digest, candidate, errors, changed = self._candidate()
        except (OSError, UnicodeError, KeyError, ValueError) as exc:
            return {"valid": False, "errors": [f"Arbeidskopien kunne ikke leses: {exc}"],
                    "checksum": None, "changed_people": 0, "version": None}
        impact = []
        if not errors:
            current = self.context()
            for week_start in candidate.weeks:
                before = build_week_context(current, week_start)
                after = build_week_context(candidate, week_start)
                impact.append({"week_start": week_start.isoformat(),
                    "uncovered_before": check_week(before, before.assignments).uncovered_count,
                    "uncovered_after": check_week(after, after.assignments).uncovered_count})
        return {"valid": not errors, "errors": errors, "checksum": digest,
                "changed_people": changed,
                "version": (self.active_version if changed == 0 else candidate.version) if not errors else None,
                "baseline_impact": impact}

    def activate(self, expected_checksum: str) -> dict:
        digest, candidate, errors, changed = self._candidate()
        if digest != expected_checksum:
            raise StateError("stale_draft", "Arbeidskopien er endret siden validering", 409)
        if errors:
            raise StateError("invalid_dataset", "; ".join(errors[:5]), 422)
        if changed == 0 or candidate.version == self.active_version:
            return {"active_version": self.active_version, "changed_people": 0}
        if candidate.version != self.base.version:
            self.versions_dir.mkdir(parents=True, exist_ok=True)
            target = self.versions_dir / f"{candidate.version}.json"
            if not target.exists():
                temp = target.with_suffix(".tmp")
                temp.write_text(candidate.model_dump_json(indent=2) + "\n", encoding="utf-8")
                os.replace(temp, target)
        # Initialiser ny, isolert planstatus før aktiv peker byttes.
        self.store(candidate.version)
        temp_pointer = self.pointer_path.with_suffix(".tmp")
        temp_pointer.write_text(json.dumps({"version": candidate.version}) + "\n", encoding="utf-8")
        os.replace(temp_pointer, self.pointer_path)
        self.active_version = candidate.version
        return {"active_version": candidate.version, "changed_people": changed}
