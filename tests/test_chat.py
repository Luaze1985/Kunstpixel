"""Tester for chatten i Datafinner: KI-en kaller verktøy selv og svarer i tekst.

Leverandørene er falske servere som svarer i rekkefølge. Ingen ekte KI kalles, så formatet er bare
testet mot det vi tror Claude og OpenAI sender. Første ekte kjøring må gjøres manuelt.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from src.kunstpixel.adapters import datafinner, datafinner_api
from src.kunstpixel.core import llm


class RekkefolgeKi:
    """Falsk leverandør: svarer med neste svar i lista for hvert kall, og husker hver forespørsel."""

    def __init__(self, svar: list[dict]) -> None:
        self.svar, self.sett = list(svar), []
        falsk = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                kropp = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                falsk.sett.append({"sti": self.path, "kropp": kropp})
                neste = falsk.svar.pop(0) if len(falsk.svar) > 1 else falsk.svar[0]
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(neste).encode())

            def log_message(self, *a: Any) -> None:
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def stopp(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def _konfig(leverandor: str, url: str) -> llm.LlmKonfig:
    return llm.LlmKonfig(leverandor=leverandor, modell="falsk", api_key="n", base_url=url)


SKJEMA = datafinner_api.verktoyskjema(datafinner.VERKTOY)
VAKT = {"stasjon": "Vaktrom / Sikkerhetssentral", "dato": "2026-11-07", "start": "08:00", "slutt": "16:00"}


def test_claude_formatet_kaller_verktoy_og_svarer() -> None:
    ki = RekkefolgeKi([
        {"stop_reason": "tool_use", "content": [
            {"type": "text", "text": "Jeg slår opp."},
            {"type": "tool_use", "id": "tu1", "name": "list_stations", "input": {}}]},
        {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Vaktrommet krever vekterkurs og førstehjelp."}]},
    ])
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "Hva krever vaktrommet?"}], SKJEMA,
                                    datafinner.run_tool, _konfig("anthropic", ki.url), "system")
    finally:
        ki.stopp()
    assert svar["tekst"].startswith("Vaktrommet krever") and svar["merke"] == "AI-forslag"
    assert svar["verktoykall"] == [{"navn": "list_stations", "args": {}, "ok": True}]
    forste, andre = ki.sett[0]["kropp"], ki.sett[1]["kropp"]
    assert ki.sett[0]["sti"] == "/v1/messages" and forste["system"] == "system"
    assert any(t["name"] == "list_stations" and "input_schema" in t for t in forste["tools"])
    assert andre["messages"][1]["role"] == "assistant"
    resultat = andre["messages"][2]["content"][0]
    assert resultat["type"] == "tool_result" and resultat["tool_use_id"] == "tu1" and "Vaktrom" in resultat["content"]


def test_openai_formatet_kaller_verktoy_og_svarer() -> None:
    ki = RekkefolgeKi([
        {"choices": [{"message": {"content": None, "tool_calls": [
            {"id": "c1", "type": "function", "function": {"name": "get_staffing_candidates", "arguments": json.dumps(VAKT)}}]}}]},
        {"choices": [{"message": {"content": "Fredrik Ruud er billigst."}}]},
    ])
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "Hvem kan ta vakten?"}], SKJEMA,
                                    datafinner.run_tool, _konfig("openai", ki.url), "system")
    finally:
        ki.stopp()
    assert svar["tekst"] == "Fredrik Ruud er billigst."
    assert svar["verktoykall"][0]["navn"] == "get_staffing_candidates" and svar["verktoykall"][0]["ok"]
    forste, andre = ki.sett[0]["kropp"], ki.sett[1]["kropp"]
    assert forste["messages"][0] == {"role": "system", "content": "system"}
    sjekk = next(t for t in forste["tools"] if t["function"]["name"] == "check_staffing_selection")
    assert sjekk["function"]["parameters"]["properties"]["ids"]["items"] == {"type": "string"}
    verktoymelding = andre["messages"][-1]
    assert verktoymelding["role"] == "tool" and verktoymelding["tool_call_id"] == "c1"
    assert "Fredrik Ruud" in verktoymelding["content"]


def test_feil_i_verktoykall_gaar_tilbake_til_modellen() -> None:
    ki = RekkefolgeKi([
        {"choices": [{"message": {"content": None, "tool_calls": [
            {"id": "c1", "type": "function", "function": {"name": "list_stations", "arguments": '{"ukjent": 1}'}}]}}]},
        {"choices": [{"message": {"content": "Jeg fikk en feil og prøver ikke igjen."}}]},
    ])
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                    _konfig("openai", ki.url), "system")
    finally:
        ki.stopp()
    assert svar["verktoykall"][0]["ok"] is False
    assert "Ukjente argumenter" in ki.sett[1]["kropp"]["messages"][-1]["content"]


def test_for_mange_runder_stopper() -> None:
    ki = RekkefolgeKi([{"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "t", "name": "list_stations", "input": {}}]}])
    try:
        with pytest.raises(llm.LlmFeil) as feil:
            llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                 _konfig("anthropic", ki.url), "system", maks_runder=3)
    finally:
        ki.stopp()
    assert feil.value.kode == "for_mange_runder" and len(ki.sett) == 3


def test_hver_runde_teller_mot_taket() -> None:
    ki = RekkefolgeKi([{"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "t", "name": "list_stations", "input": {}}]}])
    try:
        with pytest.raises(llm.LlmFeil) as feil:
            llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                 _konfig("anthropic", ki.url), "system", begrenser=llm.Begrenser(2))
    finally:
        ki.stopp()
    assert feil.value.kode == "tak" and len(ki.sett) == 2


def test_tallkontroll_hopper_over_telefonnumre_i_verktoysvar() -> None:
    ki = RekkefolgeKi([
        {"choices": [{"message": {"content": None, "tool_calls": [
            {"id": "c1", "type": "function", "function": {"name": "get_staffing_candidates", "arguments": json.dumps(VAKT)}}]}}]},
        {"choices": [{"message": {"content": "Ring 483 på 77 67."}}]},
    ])
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                    _konfig("openai", ki.url), "system")
    finally:
        ki.stopp()
    assert svar["tallkontroll"]["ok"] is False, "Sifre fra et telefonnummer skal ikke gjøre et tall «kjent»"


# ---------- HTTP-ruten ----------

@pytest.fixture()
def server() -> Iterator[str]:
    s = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_address[1]}"
    s.shutdown()
    s.server_close()


def _post(url: str, kropp: bytes) -> tuple[int, dict]:
    req = urllib.request.Request(url, data=kropp, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_chat_med_ki_av_gir_503_og_godtar_stor_historikk(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(datafinner, "LLM_KONFIG", None)
    lang = [{"rolle": "bruker", "tekst": "a" * 3000}, {"rolle": "assistent", "tekst": "b" * 3000}, {"rolle": "bruker", "tekst": "hei"}]
    status, data = _post(f"{server}/api/chat", json.dumps({"meldinger": lang}).encode())
    assert status == 503 and "LLM_PROVIDER" in data["error"]
    status, _ = _post(f"{server}/api/chat", json.dumps({"meldinger": [{"rolle": "bruker", "tekst": "x" * 40_000}]}).encode())
    assert status == 413


def test_chat_avviser_feil_form(server: str) -> None:
    status, _ = _post(f"{server}/api/chat", json.dumps({"meldinger": [{"rolle": "assistent", "tekst": "x"}]}).encode())
    assert status == 400


def test_chat_ende_til_ende_med_falsk_leverandor(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    ki = RekkefolgeKi([
        {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "tu1", "name": "get_personnel_file", "input": {"ansatt_id": "KP-ANS-006"}}]},
        {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Mappen har én sak om sykeoppfølging."}]},
    ])
    monkeypatch.setattr(datafinner, "LLM_KONFIG", _konfig("anthropic", ki.url))
    monkeypatch.setattr(datafinner, "LLM_BEGRENSER", None)
    try:
        status, data = _post(f"{server}/api/chat", json.dumps({
            "meldinger": [{"rolle": "bruker", "tekst": "Hva står i mappen til KP-ANS-006?"}], "rolle": "Museumsvert"}).encode())
    finally:
        ki.stopp()
    assert status == 200 and data["merke"] == "AI-forslag" and data["verktoykall"][0]["navn"] == "get_personnel_file"
    system = ki.sett[0]["kropp"]["system"]
    assert "Museumsvert" in system and "I dag er" in system
    assert "Jonas Berg" in json.dumps(ki.sett[1]["kropp"], ensure_ascii=False)


def test_chatsiden_finnes(server: str) -> None:
    with urllib.request.urlopen(f"{server}/chat", timeout=20) as res:
        assert res.status == 200 and b"AI-forslag" in res.read()
