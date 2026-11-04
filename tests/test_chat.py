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
from http.server import ThreadingHTTPServer
from typing import Any

import pytest

from src.kunstpixel.adapters import datafinner, datafinner_api
from src.kunstpixel.core import llm
from tests.hjelpere_ki import RekkefolgeKi, _konfig



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


def test_hr_chat_finner_og_undersoeker_case_foer_svar() -> None:
    """Fanger regresjon der modellen får et åpent HR-spørsmål uten å bli ledet til kildebasert oppdagelse."""
    ki = RekkefolgeKi([
        {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "h1", "name": "discover_hr_cases",
                                                  "input": {"sok": "KP-ANS-153"}}]},
        {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "h2", "name": "investigate_hr_case",
                                                  "input": {"kategori": "medarbeidersamtale", "ansatt_id": "KP-ANS-153"}}]},
        {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Sindre Lindqvist har registrerte medarbeidersamtaler."}]},
    ])
    system = datafinner.SYSTEM_CHAT.format(dato="2026-11-02", ukedag="mandag", rolle="Leder")
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "Finn en interessant HR-oppgave"}], SKJEMA,
                                    datafinner.run_tool, _konfig("anthropic", ki.url), system)
    finally:
        ki.stopp()
    assert [k["navn"] for k in svar["verktoykall"]] == ["discover_hr_cases", "investigate_hr_case"]
    assert all(k["ok"] for k in svar["verktoykall"])
    assert "KP-ANS-153" in ki.sett[2]["kropp"]["messages"][-1]["content"][0]["content"]
    assert "discover_hr_cases" in ki.sett[0]["kropp"]["system"]
    assert "investigate_hr_case" in ki.sett[0]["kropp"]["system"]
    assert "neste_verktoy" in ki.sett[0]["kropp"]["system"]
    assert "resolve_employee" in ki.sett[0]["kropp"]["system"]


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


VERKTOY_SVAR = {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "t", "name": "list_stations", "input": {}}]}


def test_siste_runde_tvinger_fram_et_svar_claude() -> None:
    ki = RekkefolgeKi([VERKTOY_SVAR, VERKTOY_SVAR, {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Det jeg rakk: vaktrommet."}]}])
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                    _konfig("anthropic", ki.url), "system", maks_runder=3)
    finally:
        ki.stopp()
    assert svar["avkortet"] is True and svar["tekst"] == "Det jeg rakk: vaktrommet."
    siste = ki.sett[2]["kropp"]
    assert siste["tool_choice"] == {"type": "none"}
    assert siste["messages"][-1]["content"][-1] == {"type": "text", "text": llm.CHAT_SISTE_RUNDE}
    assert "tool_choice" not in ki.sett[0]["kropp"]


def test_siste_runde_tvinger_fram_et_svar_openai() -> None:
    kall = {"choices": [{"message": {"content": None, "tool_calls": [
        {"id": "c", "type": "function", "function": {"name": "list_stations", "arguments": "{}"}}]}}]}
    ki = RekkefolgeKi([kall, {"choices": [{"message": {"content": "Det jeg rakk."}}]}])
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                    _konfig("openai", ki.url), "system", maks_runder=2)
    finally:
        ki.stopp()
    assert svar["avkortet"] is True
    assert ki.sett[1]["kropp"]["tool_choice"] == "none"
    assert ki.sett[1]["kropp"]["messages"][-1] == {"role": "user", "content": llm.CHAT_SISTE_RUNDE}


def test_modell_som_ignorerer_siste_runde_gir_feil() -> None:
    ki = RekkefolgeKi([VERKTOY_SVAR])
    try:
        with pytest.raises(llm.LlmFeil) as feil:
            llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                 _konfig("anthropic", ki.url), "system", maks_runder=3)
    finally:
        ki.stopp()
    assert feil.value.kode == "for_mange_runder" and len(ki.sett) == 3


def test_timetak_midt_i_gir_dataene_som_er_hentet() -> None:
    ki = RekkefolgeKi([VERKTOY_SVAR])
    try:
        svar = llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                                    _konfig("anthropic", ki.url), "system", begrenser=llm.Begrenser(2))
    finally:
        ki.stopp()
    assert len(ki.sett) == 2
    assert svar["avbrutt"] == "tak" and svar["merke"] == "Systemmelding" and svar["tekst"] == llm.CHAT_TAK_TEKST
    assert len(svar["data_hentet"]) == 2 and "Magasin 1" in svar["data_hentet"][0]["utdrag"]


def test_timetak_for_forste_runde_gir_feil() -> None:
    with pytest.raises(llm.LlmFeil) as feil:
        llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], SKJEMA, datafinner.run_tool,
                             _konfig("anthropic", "http://127.0.0.1:9"), "system", begrenser=llm.Begrenser(0))
    assert feil.value.kode == "tak"


def test_tallkontroll_godtar_riktig_regnestykke_og_varsler_feil() -> None:
    grunnlag = [{"timepris_uten_tillegg": 284.92, "vaktlengde_timer": 8.0}]
    assert llm.tallkontroll("284,92 × 8 = 2 279,36 kr", grunnlag) == {"ok": True, "ukjente_tall": [], "utregnet": ["284,92 × 8 = 2 279,36"]}
    feil = llm.tallkontroll("284,92 × 8 = 2 500 kr", grunnlag)
    assert feil["ok"] is False and feil["feil_utregning"] == ["284,92 × 8 = 2 500"]
    assert llm.tallkontroll("rundt 2300 kr", grunnlag)["ukjente_tall"] == ["2300"]
    # Inndata som ikke finnes i grunnlaget, gir ikke et godkjent regnestykke.
    assert llm.tallkontroll("300 × 8 = 2 400", grunnlag)["ok"] is False


def test_tallkontroll_godtar_sitert_telefonnummer() -> None:
    grunnlag = [{"navn": "Fredrik Ruud", "telefon": "+47 483 77 67", "id": "KP-ANS-168"}]
    assert llm.tallkontroll("Ring 483 77 67 eller +47 483 77 67 (KP-ANS-168).", grunnlag)["ok"] is True



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
