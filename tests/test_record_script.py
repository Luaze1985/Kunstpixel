"""H4: opptaksskriptet. Testes uten nettverk selv om maskinen har legitimasjon (klienten byttes ut)."""

import sys

import pytest

import tests.record_intern_cassettes as rec


class DeadLLM:
    """Etterligner en klient uten legitimasjon: hvert kall feiler før noe sendes."""

    name = "dead"
    locality = "external"
    calls = 0
    tokens_in = 0
    tokens_out = 0

    def __init__(self, *a, **k):
        pass

    def complete(self, request):
        raise TypeError("Could not resolve authentication method")


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(rec, "CASSETTE", tmp_path / "kassett.json")
    monkeypatch.setattr(rec, "SUMMARY", tmp_path / "oppsummering.json")
    return tmp_path


def run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["record_intern_cassettes.py", *args])
    return rec.main()


def test_dry_run_prints_plan_and_cost_cap_and_calls_nothing(isolated, monkeypatch, capsys):
    monkeypatch.setattr(rec, "AnthropicLLM", lambda *a, **k: pytest.fail("klienten skal ikke lages ved tørrkjøring"))
    assert run(monkeypatch, "--dry-run") == 0
    out = capsys.readouterr().out
    assert "claude-opus-5-5" in out and "150 000 tokens" in out and "Tørrkjøring" in out
    assert not list(isolated.iterdir())


def test_plan_counts_only_questions_that_reach_the_model():
    n = rec.plan_calls()
    assert 20 <= n < len(rec.questions())  # hilsen, injeksjon og ukjente emner når aldri modellen


def test_cost_cap_and_model_can_be_set_on_the_command_line(isolated, monkeypatch, capsys):
    assert run(monkeypatch, "--dry-run", "--budget", "40000", "--model", "claude-haiku-5-5") == 0
    out = capsys.readouterr().out
    assert "40 000 tokens" in out and "claude-haiku-5-5" in out and "0.02 USD" in out


def test_unknown_model_price_is_flagged_not_guessed(isolated, monkeypatch, capsys):
    run(monkeypatch, "--dry-run", "--model", "noe-ukjent")
    assert "Pris for modellen er ukjent" in capsys.readouterr().out


def test_stops_at_first_failed_call_and_saves_nothing(isolated, monkeypatch, capsys):
    monkeypatch.setattr(rec, "AnthropicLLM", DeadLLM)
    assert run(monkeypatch, "--yes") == 2
    out = capsys.readouterr().out
    assert "Første modellkall feilet" in out and "Ingenting lagret" in out
    assert not list(isolated.iterdir())  # ingen kassett, ingen villedende oppsummering


def test_asks_before_sending_and_aborts_on_anything_but_yes(isolated, monkeypatch, capsys):
    monkeypatch.setattr(rec, "AnthropicLLM", DeadLLM)
    monkeypatch.setattr("builtins.input", lambda prompt="": "nei")
    assert run(monkeypatch) == 1
    assert "Avbrutt" in capsys.readouterr().out
    assert not list(isolated.iterdir())


def test_client_creation_failure_is_reported_not_raised(isolated, monkeypatch, capsys):
    def boom(*a, **k):
        raise RuntimeError("Installer valgfri avhengighet")

    monkeypatch.setattr(rec, "AnthropicLLM", boom)
    assert run(monkeypatch, "--yes") == 2
    assert "Kan ikke starte klienten" in capsys.readouterr().out
