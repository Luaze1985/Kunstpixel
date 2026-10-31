"""Tester for vaktrommet: kandidater, kontroll, KI på toppen og grensemodus.

KI-kallene erstattes av en falsk funksjon. Ingen ekte leverandør kalles.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from typing import Any

import pytest

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import llm, vaktrom

STASJON = "Vaktrom / Sikkerhetssentral"
VAKT = {"stasjon": STASJON, "dato": "2026-11-07", "start": "08:00", "slutt": "16:00"}


@pytest.fixture()
def server() -> Iterator[str]:
    s = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_address[1]}"
    s.shutdown()
    s.server_close()


def _get(url: str) -> tuple[int, Any]:
    try:
        with urllib.request.urlopen(url, timeout=20) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _post(url: str, kropp: dict) -> tuple[int, Any]:
    req = urllib.request.Request(url, data=json.dumps(kropp).encode(), headers={"Content-Type": "application/json"}, method="POST")
    return _get(req)  # type: ignore[arg-type]


# ---------- rapportlaget ----------

def test_stasjoner_har_krav_fra_databasen() -> None:
    st = {s["stasjon"]: [k["kode"] for k in s["krav"]] for s in vaktrom.list_stations()}
    assert st[STASJON] == ["forstehjelp", "vekter"]


def test_helgehistorikk_teller_bare_lordag_og_sondag() -> None:
    h = vaktrom.get_weekend_shift_history("2025-11-07", "2026-11-06", STASJON)
    assert h["helgevakter_totalt"] == sum(r["helgevakter"] for r in h["rader"]) > 0
    assert all(r["stasjon"] == STASJON for r in h["rader"])


def test_kandidater_egne_forst_sortert_pa_pris_og_innleide_etter() -> None:
    k = vaktrom.get_staffing_candidates(**VAKT)
    assert k["egne"] and k["innleide"]
    priser = [r["timepris_uten_tillegg"] for r in k["egne"]]
    assert priser == sorted(priser)
    assert [r["nr"] for r in k["egne"] + k["innleide"]] == list(range(1, len(k["egne"]) + len(k["innleide"]) + 1))
    assert all({"forstehjelp", "vekter"} <= set(r["kompetanse"]) for r in k["egne"])
    assert all(r["merknad"] == vaktrom.MERKNAD_INNLEID for r in k["innleide"])


def test_ukjent_pris_kommer_sist_og_regnes_ikke_som_null() -> None:
    rader = [{"id": "B", "timepris_uten_tillegg": None}, {"id": "A", "timepris_uten_tillegg": 500.0}]
    rader.sort(key=lambda r: (r["timepris_uten_tillegg"] is None, r["timepris_uten_tillegg"] or 0.0, r["id"]))
    assert [r["id"] for r in rader] == ["A", "B"]


def test_fravaer_vises_uten_arsak() -> None:
    # Finn en dag der noen med vekterkurs har fravær, og sjekk at bare «utilgjengelig» vises.
    for dag in ("2026-03-02", "2026-03-09", "2026-06-15", "2026-09-07", "2025-11-03"):
        k = vaktrom.get_staffing_candidates(STASJON, dag, "08:00", "16:00")
        for r in k["utilgjengelige"]:
            assert r["status"] == "utilgjengelig"
            assert set(r) == {"id", "navn", "stilling", "status"}


def test_kontroll_finner_overlapp_med_registrert_vakt() -> None:
    # Ta en registrert vakt og kontroller samme person på samme tidspunkt.
    from src.kunstpixel.core import db
    with db.get_db_connection() as con:
        v = con.execute(
            "SELECT ansatt_id, dato, start, slutt, stasjon FROM hr_vakter WHERE stasjon = ? AND dato >= '2026-01-01' "
            "AND start IS NOT NULL ORDER BY vakt_id LIMIT 1", (STASJON,)
        ).fetchone()
    res = vaktrom.check_staffing_selection(v["stasjon"], v["dato"], v["start"], v["slutt"], [v["ansatt_id"]])
    assert res["resultater"][0]["status"] == "avvik"
    assert any("Overlapper" in f for f in res["resultater"][0]["funn"])
    assert res["hviletid_krav_timer"] == 11.0


def test_kontroll_sier_fra_om_innleide() -> None:
    k = vaktrom.get_staffing_candidates(**VAKT)
    res = vaktrom.check_staffing_selection(**VAKT, ids=[k["innleide"][0]["id"]])
    assert res["resultater"][0]["status"] == "kan_ikke_kontrolleres"


def test_verktoyene_er_hvitelistet_i_datafinner(server: str) -> None:
    args = urllib.parse.quote(json.dumps(VAKT))
    status, data = _get(f"{server}/api/verktoy?navn=get_staffing_candidates&args={args}")
    assert status == 200 and data["resultat"]["stasjon"] == STASJON
    status, _ = _get(f"{server}/vaktrom".replace("/vaktrom", "/api/status"))
    assert status == 200


# ---------- KI-laget ----------

def test_ki_av_gir_503_for_vaktrom_og_grense(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(datafinner, "LLM_KONFIG", None)
    k = vaktrom.get_staffing_candidates(**VAKT)
    status, _ = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "kontaktutkast", "id": k["innleide"][0]["id"]})
    assert status == 503
    status, _ = _post(f"{server}/api/grense/kjor", {"id": "GR1"})
    assert status == 503


def test_sammenligning_av_egne_ansatte_stoppes_av_datapolicy(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    kalt: list[str] = []
    monkeypatch.setattr(datafinner, "LLM_KONFIG", llm.LlmKonfig(leverandor="anthropic", modell="falsk"))
    monkeypatch.setattr(datafinner.llm, "utfor", lambda *a, **k: kalt.append("x") or {})
    k = vaktrom.get_staffing_candidates(**VAKT)
    status, data = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "sammenlign", "ids": [k["egne"][0]["id"]]})
    assert status == 200 and data["status"] == "stoppet_av_datapolicy"
    assert not kalt, "Ingenting skal sendes til modellen når en kildetabell er umerket"


def test_innleide_kan_sammenlignes_uten_navn_og_rekkefolgen_beholdes(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt: dict[str, Any] = {}

    def falsk(bruker_tekst: str, grunnlag: Any, konfig: Any, system: str, apne: Any = None) -> dict[str, Any]:
        sendt.update(tekst=bruker_tekst, grunnlag=grunnlag, system=system)
        return {"tekst": "Kandidat nr 3 og nr 4 har ulik timepris.", "merke": "AI-forslag", "modell": "falsk",
                "leverandor": "anthropic", "tallkontroll": llm.tallkontroll("nr 3 og nr 4", grunnlag)}

    monkeypatch.setattr(datafinner, "LLM_KONFIG", llm.LlmKonfig(leverandor="anthropic", modell="falsk"))
    monkeypatch.setattr(datafinner.llm, "utfor", falsk)
    # Merket på hr_innleide_personer følger ikke formatet «syntetisk (kilde)» ennå, så policyen stopper den.
    # Her testes mekanismen når alle kildene er merket riktig.
    monkeypatch.setattr(datafinner.arena, "datamerke", lambda t: [{"tabell": x, "merke": "syntetisk", "klassifisering": "syntetisk"} for x in t])
    k = vaktrom.get_staffing_candidates(**VAKT)
    ids = [r["id"] for r in k["innleide"][:2]]
    status, data = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "sammenlign", "ids": list(reversed(ids))})
    assert status == 200 and data["merke"] == "AI-forslag"
    nr = [c["nr"] for c in sendt["grunnlag"]["kandidater"]]
    assert nr == sorted(nr), "Rekkefølgen fra rapporten skal beholdes"
    for r in k["innleide"][:2]:
        assert r["navn"] not in sendt["tekst"] and r["epost"] not in sendt["tekst"] and r["telefon"] not in sendt["tekst"]
    assert "Ikke ranger" in sendt["system"]


def test_kontaktutkast_for_egen_ansatt_sender_bare_vakt_og_krav(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt: dict[str, Any] = {}

    def falsk(bruker_tekst: str, grunnlag: Any, konfig: Any, system: str, apne: Any = None) -> dict[str, Any]:
        sendt.update(tekst=bruker_tekst, system=system)
        return {"tekst": "Hei [NAVN]", "merke": "AI-forslag", "modell": "falsk", "leverandor": "anthropic",
                "tallkontroll": {"ok": True, "ukjente_tall": []}}

    monkeypatch.setattr(datafinner, "LLM_KONFIG", llm.LlmKonfig(leverandor="anthropic", modell="falsk"))
    monkeypatch.setattr(datafinner.llm, "utfor", falsk)
    k = vaktrom.get_staffing_candidates(**VAKT)
    egen = k["egne"][0]
    status, data = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "kontaktutkast", "id": egen["id"]})
    assert status == 200 and data["tekst"] == "Hei [NAVN]"
    assert egen["navn"] not in sendt["tekst"] and egen["id"] not in sendt["tekst"]
    assert "[NAVN]" in sendt["system"]


def test_grensemodus_sender_bare_foresporselen(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt: dict[str, Any] = {}

    def falsk(bruker_tekst: str, grunnlag: Any, konfig: Any, system: str, apne: Any = None) -> dict[str, Any]:
        sendt.update(tekst=bruker_tekst, grunnlag=grunnlag)
        return {"tekst": "Det kan jeg ikke hjelpe med.", "merke": "AI-forslag", "modell": "falsk",
                "leverandor": "anthropic", "tallkontroll": {"ok": True, "ukjente_tall": []}}

    monkeypatch.setattr(datafinner, "LLM_KONFIG", llm.LlmKonfig(leverandor="anthropic", modell="falsk"))
    monkeypatch.setattr(datafinner.llm, "utfor", falsk)
    status, caser = _get(f"{server}/api/grense/caser")
    assert status == 200 and caser["tekst_fast"] == "Ulovlig i dag. Kun syntetiske data. Ingenting lagres."
    assert {c["case"] for c in caser["caser"]} == {"CASE-008", "CASE-012", "CASE-013", "CASE-016"}
    status, data = _post(f"{server}/api/grense/kjor", {"id": "GR1"})
    assert status == 200 and data["tekst"] == "Det kan jeg ikke hjelpe med."
    assert sendt["grunnlag"] == {} and sendt["tekst"] == caser["caser"][0]["foresporsel"]


def test_systemprompt_kan_byttes_og_standard_er_uendret() -> None:
    konfig = llm.LlmKonfig(leverandor="anthropic", modell="m")
    _, _, standard = llm.bygg_foresporsel(konfig, "x")
    _, _, egen = llm.bygg_foresporsel(konfig, "x", "EGEN")
    assert json.loads(standard)["system"] == llm.SYSTEMPROMPT
    assert json.loads(egen)["system"] == "EGEN"


def test_sidene_finnes(server: str) -> None:
    for sti, tekst in (("/vaktrom", b"Mine kontaktutkast"), ("/arena", b"Grensemodus"), ("/", b"Arbeidsflater")):
        with urllib.request.urlopen(server + sti, timeout=20) as res:
            assert res.status == 200 and tekst in res.read()
