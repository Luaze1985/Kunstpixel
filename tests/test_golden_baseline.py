"""Fase 0: regelbasert agent skal gi nøyaktig de gyldne svarene (regresjonsanker)."""

import json
from pathlib import Path

import pytest

from tests.canonical_questions import CANONICAL_QUESTIONS

GOLDEN_PATH = Path(__file__).resolve().parent / "golden" / "regelbasert" / "golden.json"


def _golden() -> list[dict]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def test_golden_covers_all_canonical_questions():
    assert [g["question"] for g in _golden()] == CANONICAL_QUESTIONS


@pytest.mark.parametrize("entry", _golden(), ids=lambda e: (e["question"] or "<tom>")[:40])
def test_rule_based_agent_matches_golden(agent_instance, entry):
    r = agent_instance.handle_message(entry["question"])
    assert r.text == entry["text"]
    assert r.category == entry["category"]
    assert r.tools_used == entry["tools_used"]
    assert r.artworks_referenced == entry["artworks_referenced"]
    assert r.rooms_referenced == entry["rooms_referenced"]

