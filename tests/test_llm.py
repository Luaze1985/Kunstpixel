"""Tester for det valgfrie KI-laget. Ingen ekte nøkkel eller nett: en falsk KI-server i standardbiblioteket tar imot kallene."""

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

RAPPORT = {
    "sporsmal_id": "vaktplan",
    "sporsmal": "Vaktplan for en dag",
    "verktoy": "get_shifts_for_date",
    "args": {"dato": "2026-10-20"},
    "fakta": [
        {"vakt_id": "VAKT-1", "navn": "Ola Nordmann", "ansatt_id": "KP-ANS-001", "epost": "ola@eksempel.no", "telefon": "+47 12345678", "avdeling": "Drift", "timer": 7.5},
    ] + [{"vakt_id": f"VAKT-{i}", "avdeling": "Marked", "timer": 7.5} for i in range(2, 20)],
    "regelverdier": {"antall_vakter": 19},
    "vurdering": {"regel_id": "R-PLAN-01", "vurdering": "Godkjent stasjonsdekning.", "forslag": "Ingen tiltak."},
}


class FalskKi:
    """Tar imot ett kall om gangen og husker hva som ble sendt."""

    def __init__(self, svar: dict | None = None, status: int = 200) -> None:
        self.svar, self.status, self.sett = svar, status, []
        falsk = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                lengde = int(self.headers["Content-Length"])
                falsk.sett.append({"sti": self.path, "hoder": {k.lower(): v for k, v in self.headers.items()}, "kropp": json.loads(self.rfile.read(lengde))})
                self.send_response(falsk.status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(falsk.svar or {}).encode())

            def log_message(self, *a: Any) -> None:
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def stopp(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture()
def openai_ki() -> Iterator[FalskKi]:
    ki = FalskKi({"choices": [{"message": {"content": "Vaktplanen viser 19 vakter. Regelen sier godkjent dekning."}}]})
    yield ki
    ki.stopp()


@pytest.fixture()
def anthropic_ki() -> Iterator[FalskKi]:
    ki = FalskKi({"content": [{"type": "text", "text": "Vaktplanen viser 19 vakter."}]})
    yield ki
    ki.stopp()


# ---------- innstillinger ----------

def test_kilaget_er_av_uten_leverandor() -> None:
    assert llm.fra_miljo({}) is None
    assert llm.fra_miljo({"LLM_PROVIDER": "  "}) is None


def test_ugyldige_innstillinger_gir_tydelig_feil() -> None:
    with pytest.raises(ValueError, match="openai eller anthropic"):
        llm.fra_miljo({"LLM_PROVIDER": "gpt5"})
    with pytest.raises(ValueError, match="LLM_MODEL"):
        llm.fra_miljo({"LLM_PROVIDER": "openai"})


def test_innstillinger_leses_med_standardverdier() -> None:
    k = llm.fra_miljo({"LLM_PROVIDER": "Anthropic", "LLM_MODEL": "claude-haiku-5-5", "LLM_API_KEY": "hemmelig"})
    assert (k.leverandor, k.max_tokens, k.timeout, k.maks_per_time) == ("anthropic", 600, 30.0, 20)
    assert k.adresse() == "https://api.anthropic.com"
    assert llm.fra_miljo({"LLM_PROVIDER": "openai", "LLM_MODEL": "m", "LLM_BASE_URL": "http://ollama:11434/v1/"}).adresse() == "http://ollama:11434/v1"


# ---------- grunnlaget som sendes ----------

def test_personfelt_fjernes_og_lange_lister_kortes() -> None:
    ren = llm.forenkle_for_llm(RAPPORT)
    tekst = json.dumps(ren, ensure_ascii=False)
    for forbudt in ("Ola Nordmann", "ola@eksempel.no", "+47 12345678", "KP-ANS-001"):
        assert forbudt not in tekst
    assert len(ren["fakta"]) == llm.MAKS_RADER + 1 and ren["fakta"][-1] == {"_utelatt_rader": 19 - llm.MAKS_RADER}
    assert RAPPORT["fakta"][0]["navn"] == "Ola Nordmann", "Originalen skal ikke endres"


# ---------- formatet mot leverandørene ----------

def test_openai_formatet_og_svaret_leses(openai_ki: FalskKi) -> None:
    konfig = llm.LlmKonfig("openai", "min-modell", api_key="nokkel-123", base_url=openai_ki.url)
    svar = llm.forklar(RAPPORT, konfig)
    sendt = openai_ki.sett[0]
    assert sendt["sti"] == "/chat/completions"
    assert sendt["hoder"]["authorization"] == "Bearer nokkel-123"
    assert sendt["kropp"]["model"] == "min-modell" and sendt["kropp"]["temperature"] == 0
    assert sendt["kropp"]["messages"][0]["role"] == "system" and "Bruk bare tall" in sendt["kropp"]["messages"][0]["content"]
    assert "Ola Nordmann" not in json.dumps(sendt["kropp"]), "Personnavn skal aldri sendes"
    assert svar["merke"] == "AI-forslag" and svar["tekst"].startswith("Vaktplanen viser 19 vakter")


def test_anthropic_formatet_og_svaret_leses(anthropic_ki: FalskKi) -> None:
    konfig = llm.LlmKonfig("anthropic", "claude-haiku-5-5", api_key="nokkel-abc", base_url=anthropic_ki.url)
    svar = llm.forklar(RAPPORT, konfig)
    sendt = anthropic_ki.sett[0]
    assert sendt["sti"] == "/v1/messages"
    assert sendt["hoder"]["x-api-key"] == "nokkel-abc" and sendt["hoder"]["anthropic-version"] == llm.ANTHROPIC_VERSJON
    assert "Bruk bare tall" in sendt["kropp"]["system"] and sendt["kropp"]["messages"][0]["role"] == "user"
    assert svar["tekst"] == "Vaktplanen viser 19 vakter."


def test_lokal_modell_uten_nokkel_sender_ikke_autorisasjon(openai_ki: FalskKi) -> None:
    llm.forklar(RAPPORT, llm.LlmKonfig("openai", "llama", base_url=openai_ki.url))
    assert "authorization" not in openai_ki.sett[0]["hoder"]


# ---------- feil ----------

@pytest.mark.parametrize("status,forventet", [(401, "feil (401)"), (500, "feil (500)")])
def test_leverandorfeil_lekker_ikke_nokkelen(status: int, forventet: str) -> None:
    ki = FalskKi({"error": "invalid key nokkel-hemmelig"}, status=status)
    try:
        with pytest.raises(llm.LlmFeil) as e:
            llm.forklar(RAPPORT, llm.LlmKonfig("openai", "m", api_key="nokkel-hemmelig", base_url=ki.url))
    finally:
        ki.stopp()
    assert forventet in str(e.value) and "nokkel-hemmelig" not in str(e.value) and e.value.kode == "leverandorfeil"


def test_uventet_svarformat_og_tomt_svar() -> None:
    for innhold in ({"noe": "annet"}, {"choices": [{"message": {"content": "  "}}]}):
        ki = FalskKi(innhold)
        try:
            with pytest.raises(llm.LlmFeil):
                llm.forklar(RAPPORT, llm.LlmKonfig("openai", "m", base_url=ki.url))
        finally:
            ki.stopp()


def test_ingen_kontakt_og_tidsavbrudd() -> None:
    import socket
    with socket.socket() as s:  # en port som var ledig et øyeblikk siden, og nå er lukket
        s.bind(("127.0.0.1", 0))
        lukket = s.getsockname()[1]
    with pytest.raises(llm.LlmFeil, match="kontakt"):
        llm.forklar(RAPPORT, llm.LlmKonfig("openai", "m", base_url=f"http://127.0.0.1:{lukket}", timeout=5))

    def treg(*a: Any, **k: Any) -> None:
        raise urllib.error.URLError(TimeoutError("timed out"))

    with pytest.raises(llm.LlmFeil) as e:
        llm.forklar(RAPPORT, llm.LlmKonfig("openai", "m"), apne=treg)
    assert e.value.kode == "tidsavbrudd"


# ---------- tallkontroll ----------

@pytest.mark.parametrize("tekst,ok,ukjente", [
    ("Vaktplanen har 19 vakter på 7,5 timer.", True, []),
    ("Det er 806 738 kr i kostnad.", True, []),                 # norsk tusenskille
    ("Fraværet er 5,6 prosent.", True, []),                      # avrundet fra 5,64
    ("Det er 42 vakter.", False, ["42"]),                        # funnet på
    ("Dato 2026-10-20 med 19 vakter.", True, []),                # tall fra args og tekst telles som kjente
])
def test_tallkontroll(tekst: str, ok: bool, ukjente: list[str]) -> None:
    grunnlag = {"args": {"dato": "2026-10-20"}, "fakta": {"antall": 19, "timer": 7.5, "kostnad": 806738.43, "fravaer": 5.64}}
    r = llm.tallkontroll(tekst, grunnlag)
    assert (r["ok"], r["ukjente_tall"]) == (ok, ukjente)


def test_tallkontroll_godtar_avrunding_men_ikke_andre_tall() -> None:
    assert llm.tallkontroll("Rundt 8 timer.", {"timer": 7.5})["ok"] is True       # 7,5 avrundet
    assert llm.tallkontroll("Rundt 9 timer.", {"timer": 7.5})["ok"] is False      # for langt unna
    assert llm.tallkontroll("Fravær 5,6 %.", {"f": 5.64})["ok"] is True
    assert llm.tallkontroll("Fravær 5,7 %.", {"f": 5.64})["ok"] is False
    assert llm.tallkontroll("Rundt 806 738 kr.", {"k": 806738.43})["ok"] is True
    assert llm.tallkontroll("Ingen tall her.", {"k": 1})["ok"] is True


# ---------- begrensning ----------

def test_begrenseren_slipper_inn_maks_og_nullstilles() -> None:
    tid = [0.0]
    b = llm.Begrenser(2, vindu=10, klokke=lambda: tid[0])
    assert [b.tillat(), b.tillat(), b.tillat()] == [True, True, False]
    tid[0] = 11
    assert b.tillat() is True


# ---------- endepunktet /api/forklar ----------

@pytest.fixture()
def server_med_ki(monkeypatch: pytest.MonkeyPatch, openai_ki: FalskKi) -> Iterator[tuple[str, FalskKi]]:
    konfig = llm.LlmKonfig("openai", "min-modell", api_key="nokkel-123", base_url=openai_ki.url, maks_per_time=2)
    monkeypatch.setattr(datafinner, "LLM_KONFIG", konfig)
    monkeypatch.setattr(datafinner, "LLM_BEGRENSER", llm.Begrenser(2))
    s = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_address[1]}", openai_ki
    s.shutdown()
    s.server_close()


def _post(url: str, kropp: bytes, hoder: dict | None = None) -> tuple[int, dict]:
    h = {"Content-Type": "application/json", **(hoder or {})}
    try:
        with urllib.request.urlopen(urllib.request.Request(url + "/api/forklar", data=kropp, headers=h, method="POST"), timeout=20) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


KROPP = json.dumps({"sporsmal": "vaktplan", "args": {"dato": "2026-10-20"}}).encode()


def test_forklar_gir_ai_forslag_og_avslorer_funnet_pa_tall(server_med_ki: tuple[str, FalskKi]) -> None:
    """Den falske KI-en sier 19 vakter, men den ekte rapporten har et annet antall. Det skal bli synlig."""
    url, ki = server_med_ki
    status, data = _post(url, KROPP)
    assert status == 200
    assert data["merke"] == "AI-forslag" and data["status"] == "Utkast"
    assert data["rapport"]["vurdering"]["regel_id"], "KI-en forklarer den faste rapporten, den bytter den ikke ut"
    faktisk = len(data["rapport"]["fakta"])
    assert faktisk != 19
    assert data["tallkontroll"] == {"ok": False, "ukjente_tall": ["19"]}
    sendt = json.dumps(ki.sett[0]["kropp"], ensure_ascii=False)
    assert "epost" not in sendt and "telefon" not in sendt


def test_forklar_godkjenner_tall_som_stemmer_med_rapporten(server_med_ki: tuple[str, FalskKi]) -> None:
    url, ki = server_med_ki
    n = len(datafinner.run_tool("get_shifts_for_date", {"dato": "2026-10-20"}))
    ki.svar = {"choices": [{"message": {"content": f"Vaktplanen viser {n} vakter."}}]}
    status, data = _post(url, KROPP)
    assert status == 200 and data["tallkontroll"] == {"ok": True, "ukjente_tall": []}


def test_status_viser_at_kilaget_er_pa(server_med_ki: tuple[str, FalskKi]) -> None:
    url, _ = server_med_ki
    with urllib.request.urlopen(url + "/api/status", timeout=10) as res:
        data = json.loads(res.read())
    assert data["llm"] is True and data["llm_modell"] == "min-modell"
    assert "nokkel-123" not in json.dumps(data)


def test_forklar_avviser_andre_sider_feil_type_og_for_stor_kropp(server_med_ki: tuple[str, FalskKi]) -> None:
    url, ki = server_med_ki
    assert _post(url, KROPP, {"Origin": "https://ond-side.example"})[0] == 403
    assert _post(url, KROPP, {"Sec-Fetch-Site": "cross-site"})[0] == 403
    assert _post(url, KROPP, {"Content-Type": "text/plain"})[0] == 415
    assert _post(url, b"x" * 5000)[0] == 413
    assert _post(url, b"{ikke json")[0] == 400
    assert _post(url, json.dumps({"sporsmal": "finnes-ikke"}).encode())[0] == 400
    assert not ki.sett, "Ingen av de avviste kallene skal nå KI-leverandøren"


def test_forklar_begrenses_per_time(server_med_ki: tuple[str, FalskKi]) -> None:
    url, _ = server_med_ki
    assert [_post(url, KROPP)[0] for _ in range(3)] == [200, 200, 429]


def test_leverandorfeil_gir_502_uten_detaljer(monkeypatch: pytest.MonkeyPatch) -> None:
    ki = FalskKi({"error": "x"}, status=500)
    monkeypatch.setattr(datafinner, "LLM_KONFIG", llm.LlmKonfig("openai", "m", api_key="nokkel-hemmelig", base_url=ki.url))
    monkeypatch.setattr(datafinner, "LLM_BEGRENSER", None)
    s = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        status, data = _post(f"http://127.0.0.1:{s.server_address[1]}", KROPP)
    finally:
        s.shutdown()
        s.server_close()
        ki.stopp()
    assert status == 502 and "nokkel-hemmelig" not in json.dumps(data)


def test_alle_spor_smalene_kan_forklares_uten_personfelt() -> None:
    """Hver rapport som API-et lager er trygg å sende ut: ingen personfelt gjenstår etter rensing."""
    from tests.test_datafinner_api import EKSEMPEL_ARGS
    for sporsmal, args in EKSEMPEL_ARGS.items():
        rapport = datafinner_api.lag_rapport(sporsmal, args, datafinner.run_tool)
        ren = json.dumps(llm.forenkle_for_llm(rapport), ensure_ascii=False)
        for felt in llm.PERSONFELT:
            assert f'"{felt}"' not in ren, (sporsmal, felt)


# ---------- endepunktet /api/oppslag (håndboksvar) ----------

def _post_oppslag(url: str, sporsmal: str, hoder: dict | None = None) -> tuple[int, dict]:
    h = {"Content-Type": "application/json", **(hoder or {})}
    kropp = json.dumps({"sporsmal": sporsmal}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url + "/api/oppslag", data=kropp, headers=h, method="POST"), timeout=20) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_oppslag_gir_ai_forslag_med_kilder_og_flagger_ukjent_punkt(server_med_ki: tuple[str, FalskKi]) -> None:
    url, ki = server_med_ki
    ki.svar = {"choices": [{"message": {"content": "Se PERSONAL-99.9 om egenmelding."}}]}
    status, data = _post_oppslag(url, "egenmelding")
    assert status == 200 and data["status"] == "ok" and data["treff"]
    assert data["ai"]["merke"] == "AI-forslag" and data["ai"]["ukjente_kilder"] == ["PERSONAL-99.9"]
    sendt = json.dumps(ki.sett[0]["kropp"], ensure_ascii=False)
    assert "egenmelding" in sendt and "system" in sendt


def test_oppslag_uten_treff_spor_ikke_ki(server_med_ki: tuple[str, FalskKi]) -> None:
    url, ki = server_med_ki
    status, data = _post_oppslag(url, "zxqvw blorft")
    assert status == 200 and data["status"] == "ingen_kilde" and data["ai"] is None and data["treff"] == []
    assert not ki.sett


def test_oppslag_har_samme_sperrer_og_taket(server_med_ki: tuple[str, FalskKi]) -> None:
    url, ki = server_med_ki
    assert _post_oppslag(url, "egenmelding", {"Origin": "https://ond-side.example"})[0] == 403
    assert _post_oppslag(url, "egenmelding", {"Sec-Fetch-Site": "cross-site"})[0] == 403
    assert _post_oppslag(url, "egenmelding", {"Content-Type": "text/plain"})[0] == 415
    assert _post_oppslag(url, "   ")[0] == 400
    assert not ki.sett
    koder = [_post_oppslag(url, "egenmelding")[0] for _ in range(3)]
    assert koder == [200, 200, 429]
    status, data = _post_oppslag(url, "egenmelding")
    assert status == 429 and data["treff"], "treffene skal vises selv om taket er nådd"


def test_oppslag_gir_503_uten_ki_og_502_ved_leverandorfeil(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(datafinner, "LLM_KONFIG", None)
    s = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        assert _post_oppslag(f"http://127.0.0.1:{s.server_address[1]}", "egenmelding")[0] == 503
    finally:
        s.shutdown()
        s.server_close()
    ki = FalskKi({"error": "x"}, status=500)
    monkeypatch.setattr(datafinner, "LLM_KONFIG", llm.LlmKonfig("openai", "m", api_key="nokkel-hemmelig", base_url=ki.url))
    monkeypatch.setattr(datafinner, "LLM_BEGRENSER", None)
    s = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        status, data = _post_oppslag(f"http://127.0.0.1:{s.server_address[1]}", "egenmelding")
    finally:
        s.shutdown()
        s.server_close()
        ki.stopp()
    assert status == 502 and data["treff"] and "nokkel-hemmelig" not in json.dumps(data)
