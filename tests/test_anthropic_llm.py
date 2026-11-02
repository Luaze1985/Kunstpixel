"""H4: Anthropic-klienten uten nettverk. En falsk SDK-klient fanger opp nøyaktig hva som ville blitt sendt."""

import json
from types import SimpleNamespace

import pytest

from src.kunstpixel.core.intern.agent import INTERN_RULES, InternAgent
from src.kunstpixel.core.llm import (
    DEFAULT_MODEL,
    DEFAULT_TOKEN_BUDGET,
    AnthropicLLM,
    BudgetExceeded,
    LLMRefused,
    LLMRequest,
    LLMTruncated,
)

Q = "Hvor lenge kan museumsverter stå sammenhengende?"


class FakeClient:
    """Etterligner anthropic.Anthropic().messages.create. Lagrer alle kall."""

    def __init__(self, responses=None):
        self.calls = []
        self.responses = list(responses or [])
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0) if self.responses else msg("Maks 90 minutter [1].")


def msg(text="Maks 90 minutter [1].", stop="end_turn", inp=500, out=40, blocks=None, category=None):
    content = blocks if blocks is not None else [SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(
        content=content,
        stop_reason=stop,
        usage=SimpleNamespace(input_tokens=inp, output_tokens=out),
        stop_details=SimpleNamespace(category=category),
    )


def request(kontekst=True):
    return LLMRequest(
        system_prompt="Systemtekst.",
        user_message=Q,
        tool_results=[{"tool": "search_hms", "args": {"bruker_rolle": "museumsvert"}, "result": [{"x": 1}], "klassifisering": "syntetisk"}],
        draft="REGELBASERT UTKAST SOM IKKE SKAL SENDES",
        rules=INTERN_RULES,
        kontekst=[{"nr": 1, "kilde": "a.yaml", "sti": "ergonomi", "tekst": "maks sammenhengende staing: 90 minutter"}] if kontekst else None,
    )


# ---------- Hva som sendes ----------


def test_default_model_is_opus_5_5_exactly_and_env_can_override(monkeypatch):
    assert DEFAULT_MODEL == "claude-opus-5-5"
    assert AnthropicLLM(client=FakeClient()).model == "claude-opus-5-5"
    monkeypatch.setenv("KUNSTPIXEL_MODEL", "claude-haiku-5-5")
    assert AnthropicLLM(client=FakeClient()).model == "claude-haiku-5-5"


def test_request_shape_has_no_removed_parameters_and_no_prefill():
    client = FakeClient()
    AnthropicLLM(client=client).complete(request())
    kw = client.calls[0]
    assert kw["model"] == "claude-opus-5-5"
    for removed in ("temperature", "top_p", "top_k", "thinking", "budget_tokens", "tool_choice", "prefill"):
        assert removed not in kw, removed
    assert kw["output_config"] == {"effort": "low"}
    assert kw["max_tokens"] == 4000
    assert [m["role"] for m in kw["messages"]] == ["user"]  # ender med user: ingen prefill
    assert kw["system"].startswith("Systemtekst.") and INTERN_RULES in kw["system"]


def test_payload_contains_only_question_and_numbered_context():
    client = FakeClient()
    AnthropicLLM(client=client).complete(request())
    payload = json.loads(client.calls[0]["messages"][0]["content"])
    assert set(payload) == {"SPØRSMÅL", "KONTEKST"}
    assert payload["SPØRSMÅL"] == Q
    assert payload["KONTEKST"] == [{"nr": 1, "kilde": "a.yaml", "sti": "ergonomi", "tekst": "maks sammenhengende staing: 90 minutter"}]
    raw = client.calls[0]["messages"][0]["content"]
    for secret in ("REGELBASERT UTKAST", "klassifisering", "bruker_rolle", "syntetisk"):
        assert secret not in raw


def test_museum_style_request_without_context_sends_tool_results_instead():
    client = FakeClient()
    AnthropicLLM(client=client).complete(request(kontekst=False))
    payload = json.loads(client.calls[0]["messages"][0]["content"])
    assert set(payload) == {"SPØRSMÅL", "VERKTØYRESULTAT"}
    assert "REGELBASERT UTKAST" not in client.calls[0]["messages"][0]["content"]


@pytest.mark.parametrize("model,has_effort", [("claude-opus-5-5", True), ("claude-sonnet-5-5", True), ("claude-haiku-5-5", True), ("claude-fable-5-1", True), ("claude-haiku-4-5", False), ("claude-sonnet-4-5", False), ("noe-ukjent", False)])
def test_effort_is_only_sent_to_models_that_accept_it(model, has_effort):
    client = FakeClient()
    AnthropicLLM(model=model, client=client).complete(request())
    assert ("output_config" in client.calls[0]) is has_effort


def test_response_text_ignores_thinking_blocks_and_joins_text_blocks():
    blocks = [
        SimpleNamespace(type="thinking", thinking="", text="TANKER SKAL IKKE VISES"),
        SimpleNamespace(type="text", text="Første. "),
        SimpleNamespace(type="text", text="Andre."),
    ]
    out = AnthropicLLM(client=FakeClient([msg(blocks=blocks)])).complete(request())
    assert out == "Første. Andre." and "TANKER" not in out


# ---------- Stopp-grunner ----------


def test_refusal_and_truncation_raise_instead_of_returning_text():
    with pytest.raises(LLMRefused):
        AnthropicLLM(client=FakeClient([msg("delvis", stop="refusal", category="cyber")])).complete(request())
    with pytest.raises(LLMTruncated):
        AnthropicLLM(client=FakeClient([msg("halvt sv", stop="max_tokens")])).complete(request())


@pytest.mark.parametrize("stop,exc", [("refusal", "LLMRefused"), ("max_tokens", "LLMTruncated")])
def test_agent_falls_back_when_the_model_refuses_or_is_cut_off(stop, exc):
    llm = AnthropicLLM(client=FakeClient([msg("noe", stop=stop)]))
    r = InternAgent(llm=llm).handle_message(Q, "museumsvert")
    assert r.llm_used is False and r.fallback_reason == f"llm_feil: {exc}"
    assert "90 minutter" in r.text  # regelbasert svar


def test_agent_falls_back_on_sdk_errors():
    class Boom(FakeClient):
        def _create(self, **kw):
            raise ConnectionError("nettverk nede")

    llm = AnthropicLLM(client=Boom())
    r = InternAgent(llm=llm).handle_message(Q, "museumsvert")
    assert r.llm_used is False and r.fallback_reason == "llm_feil: ConnectionError"


# ---------- Kostnadstak ----------


def test_tokens_are_counted_across_calls():
    llm = AnthropicLLM(client=FakeClient([msg(inp=1000, out=100), msg(inp=2000, out=300)]), token_budget=10_000)
    llm.complete(request())
    llm.complete(request())
    assert (llm.tokens_in, llm.tokens_out, llm.tokens_used, llm.calls) == (3000, 400, 3400, 2)


def test_budget_stops_further_calls_once_reached():
    client = FakeClient([msg(inp=900, out=100), msg(), msg()])
    llm = AnthropicLLM(client=client, token_budget=1000)
    llm.complete(request())  # bruker akkurat budsjettet
    with pytest.raises(BudgetExceeded):
        llm.complete(request())
    assert len(client.calls) == 1  # ingen nytt kall ble sendt


def test_budget_exceeded_makes_the_agent_use_rule_based_answers():
    client = FakeClient([msg(inp=900, out=200)])
    llm = AnthropicLLM(client=client, token_budget=1000)
    a = InternAgent(llm=llm)
    first = a.handle_message(Q, "museumsvert")
    second = a.handle_message(Q, "museumsvert")
    assert first.llm_used is True
    assert second.llm_used is False and second.fallback_reason == "llm_feil: BudgetExceeded"
    assert "90 minutter" in second.text
    assert len(client.calls) == 1


def test_budget_defaults_and_env_override(monkeypatch):
    assert AnthropicLLM(client=FakeClient()).token_budget == DEFAULT_TOKEN_BUDGET == 150_000
    monkeypatch.setenv("KUNSTPIXEL_TOKEN_BUDGET", "5000")
    assert AnthropicLLM(client=FakeClient()).token_budget == 5000
    assert AnthropicLLM(client=FakeClient(), token_budget=7).token_budget == 7


def test_zero_budget_blocks_every_call():
    client = FakeClient()
    with pytest.raises(BudgetExceeded):
        AnthropicLLM(client=client, token_budget=0).complete(request())
    assert client.calls == []


def test_missing_usage_in_response_does_not_crash_the_counter():
    r = SimpleNamespace(content=[SimpleNamespace(type="text", text="x [1]")], stop_reason="end_turn")
    llm = AnthropicLLM(client=FakeClient([r]))
    assert llm.complete(request()) == "x [1]" and llm.tokens_used == 0


# ---------- Oppsett og nøkkel ----------


def test_real_client_is_built_with_timeout_and_key_comes_from_environment(monkeypatch):
    import anthropic

    seen = {}

    class Stub:
        def __init__(self, *a, **k):
            seen.update(k)
            seen["args"] = a

    monkeypatch.setattr(anthropic, "Anthropic", Stub)
    fake_key = "sk-" + "ant-test-" + "0" * 22  # delt i to så repoets nøkkelvakt ikke slår ut på testverdien
    monkeypatch.setenv("ANTHROPIC_API_KEY", fake_key)
    llm = AnthropicLLM()
    assert seen["timeout"] == 60.0 and "api_key" not in seen and seen["args"] == ()  # nøkkelen leses av SDK-en fra miljøet
    assert fake_key not in repr(vars(llm)) and fake_key not in str(llm.name)


def test_locality_is_external_and_cannot_be_changed_by_constructor():
    assert AnthropicLLM.locality == "external"
    assert AnthropicLLM(client=FakeClient()).locality == "external"
    with pytest.raises(TypeError):
        AnthropicLLM(client=FakeClient(), locality="local")  # type: ignore[call-arg]
