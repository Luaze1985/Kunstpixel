"""Beslutning 2026-10-27: lokal modell brukes ikke pt. H6 (lokal modell) og H7 (ekte HR-data) er på vent.

Disse testene gjør beslutningen håndhevbar: det finnes ingen vei til en lokal modell, og ekte data kan derfor
ikke behandles av noen modell. Fjern testene først når eier har besluttet å ta H6 i bruk.
"""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest

import src.kunstpixel.core.llm as llm_module
from src.kunstpixel.adapters import chat_hub, intern_hub
from src.kunstpixel.core.datapolicy import EKTE, POLICY_REASON, SYNTETISK
from src.kunstpixel.core.intern.agent import InternAgent
from src.kunstpixel.core.intern.data import DEFAULT_SOURCES, InternData, SourceSpec
from src.kunstpixel.core.llm import AnthropicLLM, FakeLLM, build_llm

ROOT = Path(__file__).resolve().parent.parent
Q = "Hvor lenge kan museumsverter stå sammenhengende?"


@pytest.mark.parametrize("kind", ["local", "lokal", "lmstudio", "lm-studio", "ollama", "gguf", "hf", "huggingface", "LOCAL"])
def test_build_llm_refuses_every_local_backend_name(kind):
    with pytest.raises(ValueError):
        build_llm(kind)


def test_only_off_fake_and_anthropic_are_known_backends():
    assert build_llm("off") is None and build_llm("") is None
    assert isinstance(build_llm("fake"), FakeLLM)
    for kind in ("local", "ollama"):
        with pytest.raises(ValueError, match="off, fake eller anthropic"):
            build_llm(kind)


def test_there_is_no_local_model_class_and_no_local_runtime_is_referenced_in_the_sources():
    assert not hasattr(llm_module, "LocalLLM")
    forbidden = re.compile(r"LocalLLM|lmstudio|lm studio|ollama|llama\.cpp|llama_cpp|localhost:1234|127\.0\.0\.1:1234|11434|gguf", re.I)
    treff = []
    for p in (ROOT / "src").rglob("*.py"):
        if forbidden.search(p.read_text(encoding="utf-8", errors="ignore")):
            treff.append(str(p.relative_to(ROOT)))
    assert treff == [], treff


@pytest.mark.parametrize("hub", [chat_hub, intern_hub], ids=["offentlig chat", "intern chat"])
def test_hubs_fall_back_to_rule_based_when_a_local_backend_is_requested(hub, monkeypatch, capsys):
    monkeypatch.setenv("KUNSTPIXEL_LLM", "local")
    agent = hub.create_agent()
    assert agent.llm is None
    assert "regelbasert" in capsys.readouterr().out


def real_hms() -> InternData:
    specs = tuple(SourceSpec(s.path, s.tema, EKTE if s.tema == "hms" else SYNTETISK, s.tilgang, s.kind) for s in DEFAULT_SOURCES)
    return InternData(sources=specs)


def test_real_data_reaches_no_available_model_and_the_real_client_is_never_called():
    """De eneste modellene som finnes er eksterne. Med ekte data skal ingen av dem kalles."""
    kall = []
    klient = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: kall.append(kw)))
    for llm in (AnthropicLLM(client=klient), FakeLLM(), FakeLLM(name="som-ser-lokal-ut")):
        r = InternAgent(data=real_hms(), llm=llm).handle_message(Q, "museumsvert")
        assert r.llm_used is False and r.fallback_reason == POLICY_REASON and r.klassifisering == EKTE
    assert kall == []


def test_no_available_backend_declares_itself_local():
    assert AnthropicLLM.locality == "external"
    assert FakeLLM().locality == "external"  # krever eksplisitt locality="local" i en test
    assert build_llm("fake").locality == "external"


def test_project_rules_and_plan_state_the_decision():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = (ROOT / "01_inbox" / "llm_testplan.md").read_text(encoding="utf-8")
    assert "Lokal modell brukes ikke pt" in agents
    assert re.search(r"H6[^|\n]*\|[^|\n]*På vent", plan) and re.search(r"H7[^|\n]*\|[^|\n]*På vent", plan)
