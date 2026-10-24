"""MVP-fasit for oppslagsverket (docs/specs/internside-oppslagsverk.md, oppgave 02–05).

Seks vitale sjekker, skrevet 2026-10-24 FØR koden finnes:
  1 Søk gir håndbokpunkter          4 Taket på AI-kall holder (20 per time)
  2 Ingen treff = ingen AI-kall     5 Siden virker uten AI
  3 AI kan bare vise til punktene   6 Nettoppsettet har tak og ingen demo
  den fikk

Regel for den som bygger: Endre koden, ikke sjekkene. Når en del er bygget, fjernes bare
merket (@VENTER_PA_03 osv.) foran sjekkene som hører til. Merket er strict, så en sjekk
som består mens merket står, feiler med vilje. Endringer i selve sjekkene avtales med Lars.

Kontrakten koden må oppfylle:
  core/oppslag.py
    sok(sporsmal, db_path=None, limit=5) -> list[dict]
        hvert treff har minst punkt_id, handbok_kode, avsnitt_tittel, innhold
    svar(sporsmal, konfig, begrenser, apne=urllib.request.urlopen, db_path=None) -> dict
        {"treff": [...], "ai": dict | None,
         "status": "ok" | "ingen_kilde" | "ai_av" | "grense_naadd" | "ai_feil"}
  core/llm.py
    svar_fra_handbok(sporsmal, punkter, konfig, apne=urllib.request.urlopen) -> dict
        {"tekst": str, "merke": "AI-forslag", "kilder": [punkt_id], "ukjente_kilder": [punkt_id]}
    fra_miljo(): standard maks_per_time = 20. ValueError når LLM_MAKS_PER_TIME ikke er et positivt heltall.
  adapters/datafinner.py: "lookup_handbook" i VERKTOY.
"""

from __future__ import annotations

import json
import re
import urllib.error
from pathlib import Path

import pytest

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import llm

ROOT = Path(__file__).resolve().parents[1]

VENTER_PA_02 = pytest.mark.xfail(strict=True, reason="MVP: bygges i oppgave 02 (fjern demokopien)")
VENTER_PA_03 = pytest.mark.xfail(strict=True, reason="MVP: bygges i oppgave 03 (oppslag uten AI)")
VENTER_PA_04 = pytest.mark.xfail(strict=True, reason="MVP: bygges i oppgave 04 (AI-svar med kilder)")
VENTER_PA_05 = pytest.mark.xfail(strict=True, reason="MVP: bygges i oppgave 05 (åpen hosting)")

KONFIG = llm.LlmKonfig(leverandor="anthropic", modell="test-modell", api_key="falsk")
PUNKT_ID = re.compile(r"\b[A-Z][A-Z_]+-\d+(?:[.-]\d+)*\b")
TULL = "zxqvw blorft"


def _oppslag():
    from src.kunstpixel.core import oppslag

    return oppslag


class _Svar:
    def __init__(self, kropp: bytes) -> None:
        self._kropp = kropp

    def read(self) -> bytes:
        return self._kropp

    def __enter__(self) -> _Svar:
        return self

    def __exit__(self, *exc) -> bool:
        return False


class FalskLeverandor:
    """Later som Claude. Husker hva som ble sendt, og svarer med fast tekst. Ingen nettverk."""

    def __init__(self, tekst: str = "Se PERSONAL-5.2.") -> None:
        self.tekst = tekst
        self.kall: list[dict] = []

    def __call__(self, foresporsel, timeout=None):
        self.kall.append(json.loads(foresporsel.data.decode("utf-8")))
        return _Svar(json.dumps({"content": [{"type": "text", "text": self.tekst}]}).encode("utf-8"))


def _brukertekst(kall: dict) -> str:
    """Det som ble sendt som brukermelding (spørsmål og punkter), uten systemprompten."""
    return json.dumps(kall["messages"], ensure_ascii=False)


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("mvp-oppslag") / "museum.db"
    bygg(db)
    return db


# ---------- 1 Søk gir håndbokpunkter ----------

def test_1_egenmelding_gir_treff_i_personalhandboken(bygget_db: Path) -> None:
    treff = _oppslag().sok("egenmelding", db_path=bygget_db)
    assert any(t["handbok_kode"] == "PERSONAL" for t in treff)
    for t in treff:
        assert {"punkt_id", "handbok_kode", "avsnitt_tittel", "innhold"} <= t.keys()


def test_1_datafinner_kan_sla_opp_i_handbokene() -> None:
    assert "lookup_handbook" in datafinner.VERKTOY


# ---------- 2 Ingen treff = ingen AI-kall ----------

@VENTER_PA_04
def test_2_ingen_treff_gir_ingen_kilde_og_ingen_ai(bygget_db: Path) -> None:
    lev = FalskLeverandor()
    res = _oppslag().svar(TULL, KONFIG, llm.Begrenser(20), apne=lev, db_path=bygget_db)
    assert res["status"] == "ingen_kilde"
    assert res["treff"] == []
    assert res["ai"] is None
    assert lev.kall == [], "AI-en skal ikke spørres (og ikke koste penger) når håndbøkene ikke har svaret"


# ---------- 3 AI kan bare vise til punktene den fikk ----------

@VENTER_PA_04
def test_3_ukjent_punkt_i_ai_svaret_blir_flagget() -> None:
    punkter = [{"punkt_id": "PERSONAL-5.2", "avsnitt_tittel": "Egenmeldingsregler", "innhold": "Egenmelding ..."}]
    lev = FalskLeverandor("Du kan bruke egenmelding (PERSONAL-5.2). Se også PERSONAL-99.9.")
    ai = llm.svar_fra_handbok("hvor mange dager egenmelding?", punkter, KONFIG, apne=lev)
    assert ai["merke"] == "AI-forslag"
    assert "PERSONAL-5.2" in ai["kilder"]
    assert ai["ukjente_kilder"] == ["PERSONAL-99.9"]
    assert len(lev.kall) == 1


@VENTER_PA_04
def test_3_ai_far_bare_sporsmalet_og_treffene(bygget_db: Path) -> None:
    lev = FalskLeverandor("Se PERSONAL-5.2.")
    res = _oppslag().svar("egenmelding", KONFIG, llm.Begrenser(20), apne=lev, db_path=bygget_db)
    assert res["status"] == "ok" and res["ai"] is not None
    sendt = _brukertekst(lev.kall[0])
    treff_ider = {t["punkt_id"] for t in res["treff"]}
    assert "egenmelding" in sendt
    assert treff_ider <= set(PUNKT_ID.findall(sendt)), "alle treffene skal sendes med"
    assert set(PUNKT_ID.findall(sendt)) <= treff_ider, "ingenting annet fra databasen skal sendes"


# ---------- 4 Taket på AI-kall holder ----------

@VENTER_PA_04
def test_4_sporsmal_21_i_timen_stoppes_men_treffene_vises(bygget_db: Path) -> None:
    tid = [0.0]
    begrenser = llm.Begrenser(20, klokke=lambda: tid[0])
    lev = FalskLeverandor()
    for _ in range(20):
        assert _oppslag().svar("egenmelding", KONFIG, begrenser, apne=lev, db_path=bygget_db)["status"] == "ok"
    res = _oppslag().svar("egenmelding", KONFIG, begrenser, apne=lev, db_path=bygget_db)
    assert res["status"] == "grense_naadd"
    assert res["treff"], "treffene skal vises selv om AI-taket er nådd"
    assert len(lev.kall) == 20
    tid[0] = 3600.0
    assert _oppslag().svar("egenmelding", KONFIG, begrenser, apne=lev, db_path=bygget_db)["status"] == "ok"


@VENTER_PA_04
def test_4_standardtaket_er_20() -> None:
    konfig = llm.fra_miljo({"LLM_PROVIDER": "anthropic", "LLM_MODEL": "m"})
    assert konfig is not None and konfig.maks_per_time == 20


@VENTER_PA_04
@pytest.mark.parametrize("verdi", ["0", "-5"])
def test_4_ugyldig_tak_stopper_oppstarten(verdi: str) -> None:
    with pytest.raises(ValueError):
        llm.fra_miljo({"LLM_PROVIDER": "anthropic", "LLM_MODEL": "m", "LLM_MAKS_PER_TIME": verdi})


# ---------- 5 Siden virker uten AI ----------

@VENTER_PA_04
def test_5_uten_ai_vises_treffene(bygget_db: Path) -> None:
    res = _oppslag().svar("egenmelding", None, None, db_path=bygget_db)
    assert res["status"] == "ai_av"
    assert res["treff"] and res["ai"] is None


@VENTER_PA_04
def test_5_feil_hos_claude_gir_likevel_treffene(bygget_db: Path) -> None:
    def nede(foresporsel, timeout=None):
        raise urllib.error.URLError("nede")

    res = _oppslag().svar("egenmelding", KONFIG, llm.Begrenser(20), apne=nede, db_path=bygget_db)
    assert res["status"] == "ai_feil"
    assert res["treff"] and res["ai"] is None


# ---------- 6 Nettoppsettet har tak og ingen demo ----------

def test_6_demokopien_er_borte() -> None:
    assert not (ROOT / "src" / "kunstpixel" / "data" / "build_demo_db.py").exists()
    assert "DATAFINNER_DEMO" not in (ROOT / "deploy" / "demo" / "Dockerfile").read_text(encoding="utf-8")


@VENTER_PA_05
def test_6_nettsiden_har_tak_20_og_er_apen() -> None:
    compose = (ROOT / "deploy" / "demo" / "compose.yaml").read_text(encoding="utf-8")
    assert "LLM_MAKS_PER_TIME:-20}" in compose
    assert "basic_auth" not in (ROOT / "deploy" / "demo" / "Caddyfile").read_text(encoding="utf-8")
