"""H4: kvalitet mot innspilte svar fra ekte modell. Hoppes over til kassetten finnes.

Lag kassetten med:  py -3.13 tests/record_intern_cassettes.py   (koster tokens, krever nøkkel)
Etter det kjører disse testene uten nettverk og uten nøkkel.
"""

import json
from pathlib import Path

import pytest

from src.kunstpixel.core.intern.agent import InternAgent
from src.kunstpixel.core.llm import RecordingLLM
from tests.intern_questions import DEKKET, UBESVARBARE

CASSETTE = Path(__file__).resolve().parent / "cassettes" / "intern" / "kassett.json"
pytestmark = pytest.mark.skipif(not CASSETTE.is_file(), reason="Ingen kassett ennå. Kjør tests/record_intern_cassettes.py (koster tokens).")

# Terskler fra planen (H4): 0 feil fakta, 100 % kilde, 100 % riktig avslag.
MIN_LLM_ANDEL = 0.90


@pytest.fixture(scope="module")
def results():
    agent = InternAgent(llm=RecordingLLM(CASSETTE))  # ren avspilling: ingen modell, ingen nettverk
    covered = [(d, agent.handle_message(d["sporsmal"], d["rolle"])) for d in DEKKET]
    refused = [(d, agent.handle_message(d["sporsmal"], d["rolle"])) for d in UBESVARBARE]
    return covered, refused


def test_every_recorded_answer_that_is_shown_has_a_valid_source(results):
    covered, _ = results
    for d, r in covered:
        if r.llm_used:
            assert r.kilder and r.text.count("Kilde [") == len(r.kilder), d["sporsmal"]
            assert any(k.startswith(d["kilde"]) for k in r.kilder), (d["sporsmal"], r.kilder)


def test_most_covered_questions_are_answered_by_the_model_without_fallback(results):
    covered, _ = results
    used = sum(r.llm_used and r.funnet for _, r in covered)
    assert used / len(covered) >= MIN_LLM_ANDEL, f"{used} av {len(covered)}"


def test_no_recorded_answer_was_stopped_for_invented_numbers(results):
    covered, _ = results
    bad = [(d["sporsmal"], r.fallback_reason) for d, r in covered if r.fallback_reason and "tall ikke i funnene" in r.fallback_reason]
    assert bad == []


def test_all_uncovered_questions_are_refused_honestly(results):
    _, refused = results
    for d, r in refused:
        assert r.funnet is False and "ikke i de interne dataene" in r.text, d["sporsmal"]


def test_cassette_file_is_plain_text_without_keys_or_real_data():
    raw = CASSETTE.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert data and all({"user_message", "text", "model"} <= set(v) for v in data.values())
    assert "sk-ant-" not in raw and "ANTHROPIC_API_KEY" not in raw
