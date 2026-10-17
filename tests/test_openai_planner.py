from datetime import date
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.kunstpixel.hr_simulator.context import build_week_context, load_planning_context
from src.kunstpixel.hr_simulator.openai_planner import ModelChoice, ModelOutput, ModelProposalError, generate_week_proposal


class FakeResponses:
    def __init__(self, output):
        self.output = output
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.output, usage=SimpleNamespace(input_tokens=20, output_tokens=15))


def week():
    root = Path(__file__).resolve().parents[1]
    data = load_planning_context(root / "05_data/hr_simulator/planning_week.json")
    return build_week_context(data, date(2026, 10, 12))


def test_model_proposal_is_validated_and_does_not_assign_directly():
    w = week()
    output = ModelOutput(choices=[ModelChoice(activity_id="W1-1-event", person_id="KP-ANS-006",
                         skill="vertskap", reason="Dokumentert kapasitet", source_ids=["K-TEKNISK-PROGRAM"])],
                         rationale="Beholder avtalte vakter", missing_information=[])
    responses = FakeResponses(output)
    proposal = generate_week_proposal(w, w.assignments, model="test-model", client=SimpleNamespace(responses=responses))
    assert proposal.changes[0]["person_id"] == "KP-ANS-006"
    assert proposal.source == "openai"
    assert len(w.assignments) == 4  # gjeldende kontekst ble ikke mutert
    assert responses.calls[0]["text_format"] is ModelOutput
    sent = json.loads(responses.calls[0]["input"][1]["content"])
    assert "persons" not in sent and "shifts" not in sent
    assert len(sent["shortlist"]["W1-1-event:vertskap"]) <= 5
    assert "KP-ANS-006" in {c["person_id"] for c in sent["shortlist"]["W1-1-event:vertskap"]}


@pytest.mark.parametrize("person_id,source_ids", [("UKJENT", ["K-OLJE"]), ("KP-ANS-006", ["OPPDIKTET"])])
def test_unknown_person_or_source_is_rejected(person_id, source_ids):
    w = week()
    output = ModelOutput(choices=[ModelChoice(activity_id="W1-1-event", person_id=person_id,
                         skill="vertskap", reason="Påstand", source_ids=source_ids)],
                         rationale="Forslag", missing_information=[])
    with pytest.raises(ModelProposalError):
        generate_week_proposal(w, w.assignments, model="test-model", client=SimpleNamespace(responses=FakeResponses(output)))


def test_refusal_keeps_current_plan_unchanged():
    w = week()
    before = list(w.assignments)
    with pytest.raises(ModelProposalError):
        generate_week_proposal(w, w.assignments, model="test-model", client=SimpleNamespace(responses=FakeResponses(None)))
    assert w.assignments == before


def test_model_free_text_is_not_presented_as_verified_fact():
    w = week()
    claim = "Personen har skriftlig akseptert en ekstravakt"
    output = ModelOutput(choices=[ModelChoice(activity_id="W1-1-event", person_id="KP-ANS-006",
                         skill="vertskap", reason=claim, source_ids=["K-TEKNISK-PROGRAM"])],
                         rationale=claim, missing_information=[claim])
    proposal = generate_week_proposal(w, w.assignments, model="test-model", client=SimpleNamespace(responses=FakeResponses(output)))
    assert claim not in proposal.changes[0]["reason"]
    assert claim not in proposal.rationale
    assert claim not in proposal.missing_information
