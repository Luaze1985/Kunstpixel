"""Fiktive ukeplandata må være konsistente før de brukes til forslag."""
import json
from pathlib import Path

import pytest

from src.kunstpixel.hr_simulator.context import load_planning_context, build_week_context

DATA = Path(__file__).resolve().parents[1] / "05_data/hr_simulator/planning_week.json"


def test_four_contiguous_weeks_and_preparation_time():
    context = load_planning_context(DATA)
    assert len(context.weeks) == 4
    week = build_week_context(context, context.weeks[0])
    assert week.activities
    assert any(a.work_start < a.starts_at for a in week.activities)
    assert any(a.work_end > a.ends_at for a in week.activities)


def test_real_contact_and_unknown_references_are_rejected(tmp_path):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    data["persons"][0]["email"] = "real@example.com"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_planning_context(path)
    data["persons"][0]["email"] = "safe@example.invalid"
    data["activities"][0]["source_ids"] = ["UNKNOWN"]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_planning_context(path)


def test_unknown_training_is_not_promoted_to_completed():
    context = load_planning_context(DATA)
    person = next(p for p in context.persons if p.id == "POOL-01")
    assert person.training.get("vertskap") is None


def test_source_registry_is_authoritative(tmp_path):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    data["source_ids"].append("UNKNOWN")
    path = tmp_path / "unknown-source.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_planning_context(path)


def test_contract_capacity_is_preserved_from_original_synthetic_persons():
    context = load_planning_context(DATA)
    sara = next(p for p in context.persons if p.id == "EMP-04")
    assert sara.position_percent == 80
