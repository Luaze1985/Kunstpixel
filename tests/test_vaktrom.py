"""Tester for vaktrommet, KI på toppen, grensemodus og nye verktøy. Datafinner kjører uten sperrer.

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


def test_fravaer_vises_med_type() -> None:
    """Uten sperrer: utilgjengelige vises med fraværstypen fra hr_fravaer."""
    from src.kunstpixel.core import db
    with db.get_db_connection() as con:
        f = con.execute(
            "SELECT f.ansatt_id, f.fra, f.type FROM hr_fravaer f "
            "WHERE f.fra >= '2025-01-01' AND f.ansatt_id IN (SELECT ansatt_id FROM org_ansatt_kompetanse WHERE skill_code = 'vekter') "
            "AND f.ansatt_id IN (SELECT ansatt_id FROM org_ansatt_kompetanse WHERE skill_code = 'forstehjelp') "
            "ORDER BY f.fra LIMIT 1"
        ).fetchone()
    k = vaktrom.get_staffing_candidates(STASJON, f["fra"], "08:00", "16:00")
    treff = [r for r in k["utilgjengelige"] if r["id"] == f["ansatt_id"]]
    assert treff, "Den fraværende skal stå blant de utilgjengelige"
    assert treff[0]["fravaerstype"] == f["type"]


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


def test_kontroll_av_innleide_sjekker_kurs_men_ikke_vakter() -> None:
    k = vaktrom.get_staffing_candidates(**VAKT)
    res = vaktrom.check_staffing_selection(**VAKT, ids=[k["innleide"][0]["id"]])
    assert res["resultater"][0]["status"] == "delvis"
    assert res["resultater"][0]["funn"][0] == "Kurs ok."


def test_innleide_filtreres_pa_kurs_gyldig_pa_datoen() -> None:
    """Vaktrommet krever vekter og førstehjelp. Trond Bakken (P08) har utløpt førstehjelp og faller ut."""
    k = vaktrom.get_staffing_candidates(**VAKT)
    assert {r["id"] for r in k["innleide"]} == {"KP-INN-P03", "KP-INN-P04"}
    res = vaktrom.check_staffing_selection(**VAKT, ids=["KP-INN-P08"])
    assert res["resultater"][0]["status"] == "avvik"
    assert "forstehjelp" in res["resultater"][0]["funn"][0]


def test_innleide_til_sal_er_de_med_kundebehandling_og_aktiv_avtale() -> None:
    """Sal A krever kundebehandling. P08 har kurset, men avtalen starter 2026-04-01 og teller ikke i mars."""
    mars = vaktrom.get_staffing_candidates("Sal A (Mytologi og natur)", "2026-03-14", "10:00", "17:00")
    assert {r["id"] for r in mars["innleide"]} == {"KP-INN-P03", "KP-INN-P06"}
    mai = vaktrom.get_staffing_candidates("Sal A (Mytologi og natur)", "2026-05-09", "10:00", "17:00")
    assert {r["id"] for r in mai["innleide"]} == {"KP-INN-P03", "KP-INN-P06", "KP-INN-P08"}


def test_verktoyene_er_hvitelistet_i_datafinner(server: str) -> None:
    args = urllib.parse.quote(json.dumps(VAKT))
    status, data = _get(f"{server}/api/verktoy?navn=get_staffing_candidates&args={args}")
    assert status == 200 and data["resultat"]["stasjon"] == STASJON
    status, _ = _get(f"{server}/vaktrom".replace("/vaktrom", "/api/status"))
    assert status == 200


# ---------- KI-laget (uten sperrer, spec vaktrom-uten-sperrer) ----------

def _falsk_ki(monkeypatch: pytest.MonkeyPatch, tekst: str = "Svar fra falsk modell.") -> dict[str, Any]:
    """Bytt ut KI-kallet og husk hva som ble sendt. Ingen ekte leverandør kalles."""
    sendt: dict[str, Any] = {}

    def falsk(bruker_tekst: str, grunnlag: Any, konfig: Any, system: str, apne: Any = None) -> dict[str, Any]:
        sendt.update(tekst=bruker_tekst, grunnlag=grunnlag, system=system)
        return {"tekst": tekst, "merke": "AI-forslag", "modell": "falsk", "leverandor": "anthropic",
                "tallkontroll": {"ok": True, "ukjente_tall": []}}

    monkeypatch.setattr(datafinner, "LLM_KONFIG", llm.LlmKonfig(leverandor="anthropic", modell="falsk"))
    monkeypatch.setattr(datafinner.llm, "utfor", falsk)
    return sendt


def test_ki_av_gir_503_for_vaktrom_og_grense(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(datafinner, "LLM_KONFIG", None)
    k = vaktrom.get_staffing_candidates(**VAKT)
    status, _ = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "kontaktutkast", "id": k["innleide"][0]["id"]})
    assert status == 503
    status, _ = _post(f"{server}/api/grense/kjor", {"id": "GR1"})
    assert status == 503


def test_sammenligning_sender_egne_ansatte_med_navn_og_kontaktinfo(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt = _falsk_ki(monkeypatch)
    k = vaktrom.get_staffing_candidates(**VAKT)
    egen = k["egne"][0]
    status, data = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "sammenlign", "ids": [egen["id"]]})
    assert status == 200 and data["merke"] == "AI-forslag"
    for verdi in (egen["navn"], egen["epost"], egen["telefon"], egen["id"]):
        assert verdi in sendt["tekst"], verdi
    assert "ranger" in sendt["system"]


def test_sammenligning_sender_innleide_i_rapportens_rekkefolge(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt = _falsk_ki(monkeypatch)
    k = vaktrom.get_staffing_candidates(**VAKT)
    ids = [r["id"] for r in k["innleide"][:2]]
    status, _ = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "sammenlign", "ids": list(reversed(ids))})
    assert status == 200
    nr = [c["nr"] for c in sendt["grunnlag"]["kandidater"]]
    assert nr == sorted(nr)
    assert all(r["navn"] in sendt["tekst"] for r in k["innleide"][:2])


def test_kontaktutkast_sender_mottakerens_navn(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt = _falsk_ki(monkeypatch, "Hei Fredrik")
    k = vaktrom.get_staffing_candidates(**VAKT)
    egen = k["egne"][0]
    status, data = _post(f"{server}/api/vaktrom/ki", {**VAKT, "oppgave": "kontaktutkast", "id": egen["id"]})
    assert status == 200 and data["tekst"] == "Hei Fredrik"
    assert egen["navn"] in sendt["tekst"]


def test_grensemodus_sender_foresporsel_og_data(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt = _falsk_ki(monkeypatch, "Her er rangeringen.")
    status, caser = _get(f"{server}/api/grense/caser")
    assert status == 200 and caser["tekst_fast"] == "Ulovlig i dag. Kun syntetiske data. Ingenting lagres."
    assert {c["case"] for c in caser["caser"]} == {"CASE-008", "CASE-012", "CASE-013", "CASE-016"}
    assert all(c.get("data") for c in caser["caser"]), "Hver grensecase skal sende med data"
    status, data = _post(f"{server}/api/grense/kjor", {"id": "GR1"})
    assert status == 200 and data["tekst"] == "Her er rangeringen."
    assert sendt["tekst"].startswith(caser["caser"][0]["foresporsel"])
    assert "get_absence_by_person" in data["data_sendt"][0]
    personer = next(iter(sendt["grunnlag"].values()))["personer"]
    assert personer and personer[0]["navn"] in sendt["tekst"]


def test_grensemodus_gr4_sender_personalmappen(server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sendt = _falsk_ki(monkeypatch)
    status, _ = _post(f"{server}/api/grense/kjor", {"id": "GR4"})
    assert status == 200 and "Jonas Berg" in sendt["tekst"] and "sykeoppfolging" in sendt["tekst"]


# ---------- nye verktøy uten rollesperre ----------

@pytest.mark.parametrize("navn,args,forventet", [
    ("get_personnel_file", {"ansatt_id": "KP-ANS-006"}, "LEDER_FORTROLIG"),
    ("get_employee_cv", {"ident": "KP-ANS-153"}, "Sindre Lindqvist"),
    ("search_active_contractors", {"query": "Securitas"}, "Securitas"),
    ("get_absence_by_person", {"fra": "2025-11-01", "til": "2026-10-31", "stasjon": STASJON}, "personer"),
    ("search_hms_guidance", {"query": "ergonomi", "limit": 2}, "Ergonomi"),
    ("lookup_handbook", {"query": "brann", "limit": 2}, "punkt_id"),
])
def test_nye_verktoy_kan_kalles_uten_rolle(server: str, navn: str, args: dict, forventet: str) -> None:
    status, data = _get(f"{server}/api/verktoy?navn={navn}&args={urllib.parse.quote(json.dumps(args))}")
    assert status == 200, data
    assert forventet in json.dumps(data["resultat"], ensure_ascii=False)


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
