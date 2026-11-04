"""Tester for eval-kjøreren: sjekklogikken, kjøring mot falsk leverandør, rapport og pass@k/pass^k. Ingen ekte KI."""

from __future__ import annotations

from pathlib import Path

from src.kunstpixel.adapters import datafinner, datafinner_api
from src.kunstpixel.core import chat_eval
from tests.hjelpere_ki import RekkefolgeKi, _konfig

SKJEMA = datafinner_api.verktoyskjema(datafinner.VERKTOY)
VAKT = {"stasjon": "Vaktrom / Sikkerhetssentral", "dato": "2026-11-07", "start": "08:00", "slutt": "16:00"}


def _oppgave(**kw: object) -> dict:
    o = {"id": "X1", "kategori": "bemanning", "rolle": "Driftsansvarlig", "turer": ["Hvem kan ta vakten?"],
         "fasit": [], "forventet": [], "utregnet": [], "forbudt": [], "verktoy_krav": [], "args_krav": [],
         "maks_kall": 6, "tallkontroll": "ignorer"}
    o.update(kw)
    return o


def _svar(tekst: str, kall: list[tuple[str, dict]] | None = None, **kw: object) -> dict:
    return {"tekst": tekst, "verktoykall": [{"navn": n, "args": a, "ok": True} for n, a in (kall or [])],
            "tallkontroll": {"ok": True, "ukjente_tall": []}, **kw}


def _feilet(sjekker: list[dict]) -> list[str]:
    return [s["sjekk"] for s in sjekker if not s["ok"]]


def test_riktig_svar_bestar() -> None:
    o = _oppgave(forventet=["Fredrik Ruud", ["sykemelding", "sykmeld"]], utregnet=[{"uttrykk": "284.92 * 8", "verdi": "2279.36"}],
                 forbudt=["Trond Bakken"], verktoy_krav=[["get_staffing_candidates"]],
                 args_krav=[{"verktoy": "get_staffing_candidates", "args": {"dato": "2026-11-07"}}])
    s = _svar("Fredrik Ruud kan. 284,92 × 8 = 2 279,36 kr. Stian er sykmeldt.", [("get_staffing_candidates", VAKT)])
    assert _feilet(chat_eval.vurder(o, [s])) == []


def test_hver_sjekk_kan_feile() -> None:
    o = _oppgave(forventet=["Fredrik Ruud"], forbudt=["Trond Bakken"], verktoy_krav=[["get_staffing_candidates"]],
                 args_krav=[{"verktoy": "get_staffing_candidates", "args": {"dato": "2026-11-07"}}], maks_kall=1,
                 tallkontroll="ok")
    s = _svar("Trond Bakken kan.", [("list_stations", {}), ("list_stations", {})],
              tallkontroll={"ok": False, "ukjente_tall": ["9"]}, avbrutt="tak")
    feilet = _feilet(chat_eval.vurder(o, [s]))
    assert len(feilet) == 7, feilet


def test_alternative_verktoysett_og_samtale_over_flere_turer() -> None:
    o = _oppgave(verktoy_krav=[["get_staffing_candidates", "search_active_contractors"], ["get_employee_cv"]],
                 forventet=["Fatima"])
    tur1 = _svar("...", [("get_staffing_candidates", VAKT)])
    tur2 = _svar("Hei Fatima", [("search_active_contractors", {"query": "Fatima"})])
    assert _feilet(chat_eval.vurder(o, [tur1, tur2])) == [], "Verktøy fra alle turer teller, tekst fra siste tur"


def test_kjor_forsok_mot_falsk_leverandor_og_rapport(tmp_path: Path) -> None:
    ki = RekkefolgeKi([
        {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "t1", "name": "get_staffing_candidates", "input": VAKT}]},
        {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Fredrik Ruud er billigst: 284,92 × 8 = 2 279,36 kr."}]},
    ])
    o = _oppgave(forventet=["Fredrik Ruud"], utregnet=[{"uttrykk": "284.92 * 8", "verdi": "2279.36"}],
                 verktoy_krav=[["get_staffing_candidates"]], tallkontroll="ok")
    try:
        post = chat_eval.kjor_forsok(o, 1, konfig=_konfig("anthropic", ki.url), verktoy=SKJEMA, kjor=datafinner.run_tool,
                                     system_mal=datafinner.SYSTEM_CHAT, dato_i_dag="2026-11-02")
    finally:
        ki.stopp()
    assert post["bestatt"] is True, post["sjekker"]
    assert "I dag er mandag 2026-11-02" in ki.sett[0]["kropp"]["system"]
    assert post["svar"][0]["tallkontroll"]["utregnet"] == ["284,92 × 8 = 2 279,36"]

    jsonl = tmp_path / "k.jsonl"
    chat_eval.skriv_jsonl([post], jsonl)
    assert chat_eval.les_jsonl(jsonl)[0]["id"] == "X1"
    md = chat_eval.rapport_md([post], {"modell": "falsk", "k": 1}, jsonl.name)
    assert "1 av 1 oppgaver besto alle forsøk" in md


def test_leverandorfeil_blir_feilet_forsok() -> None:
    o = _oppgave(forventet=["x"])
    post = chat_eval.kjor_forsok(o, 1, konfig=_konfig("anthropic", "http://127.0.0.1:9"), verktoy=SKJEMA,
                                 kjor=datafinner.run_tool, system_mal=datafinner.SYSTEM_CHAT, dato_i_dag="2026-11-02")
    assert post["bestatt"] is False and "leverandorfeil" in post["svar"][0]["feil"]


def test_pass_at_k_og_pass_hat_k() -> None:
    def p(oid: str, ok: bool | None, kat: str = "fakta") -> dict:
        return {"id": oid, "kategori": kat, "bestatt": ok}
    s = chat_eval.oppsummer([p("A", True), p("A", True), p("B", True), p("B", False), p("C", False), p("C", False),
                             p("O", None, "observasjon")])
    assert (s["oppgaver"]["A"]["pass_hat_k"], s["oppgaver"]["B"]["pass_at_k"], s["oppgaver"]["B"]["pass_hat_k"]) == (True, True, False)
    assert s["oppgaver"]["B"]["pass_rate"] == 0.5 and s["oppgaver"]["C"]["pass_at_k"] is False
    assert s["total"] == {"oppgaver": 3, "pass_at_k": 2, "pass_hat_k": 1, "forsok": 6, "bestatt_forsok": 3}


def test_sammenligning_viser_endring() -> None:
    gammel = [{"id": "A", "kategori": "fakta", "bestatt": False, "forsok": 1, "sjekker": [], "svar": []}]
    ny = [{"id": "A", "kategori": "fakta", "bestatt": True, "forsok": 1, "sjekker": [], "svar": []}]
    assert "A: 0.00 → 1.00 (bedre)" in chat_eval.rapport_md(ny, {}, "x.jsonl", gammel)


def test_skriptet_dry_run(capsys) -> None:
    import importlib.util
    spec = importlib.util.spec_from_file_location("chat_eval_skript", Path(chat_eval.PROJECT_ROOT) / "scripts" / "chat_eval.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    assert modul.main(["--dry-run", "--k", "1"]) == 0
    assert f"{len(chat_eval.last()['oppgaver'])} oppgaver" in capsys.readouterr().out
