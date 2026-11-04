"""Vaktchatten (JS-verktøy i nettleseren) skal regne likt med vaktrom.py i Datafinner.

Kjører src/kunstpixel/adapters/vaktchat/verktoy.js i Node på samme øyeblikksbilde som scripts/bygg_vaktchat.py
lager, og sammenligner med Python. Hoppes over hvis Node mangler.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import vaktrom

ROOT = Path(__file__).resolve().parents[1]
VERKTOY_JS = ROOT / "src" / "kunstpixel" / "adapters" / "vaktchat" / "verktoy.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")

VAKTER = [
    ("Vaktrom / Sikkerhetssentral", "2026-11-07", "08:00", "16:00"),
    ("Vaktrom / Sikkerhetssentral", "2026-11-14", "08:00", "16:00"),
    ("Sal A (Mytologi og natur)", "2026-03-14", "10:00", "17:00"),
    ("Museumskafé", "2026-06-13", "09:00", "17:00"),
    ("Resepsjon og billett", "2026-01-10", "10:00", "17:00"),
]
KALL = (
    [["get_staffing_candidates", {"stasjon": s, "dato": d, "start": a, "slutt": b}] for s, d, a, b in VAKTER]
    + [
        ["check_staffing_selection", {"stasjon": "Vaktrom / Sikkerhetssentral", "dato": "2026-11-21", "start": "15:00",
                                      "slutt": "23:00", "ids": ["KP-ANS-096", "KP-INN-P08"]}],
        ["get_weekend_shift_history", {"fra": "2025-11-07", "til": "2026-11-06", "stasjon": "Vaktrom / Sikkerhetssentral"}],
        ["get_shifts_for_date", {"dato": "2026-11-01"}],
        ["check_shift_swap", {"vakt_a": "VAKT-0054463", "vakt_b": "VAKT-0054464"}],
        ["check_shift_swap", {"vakt_a": "VAKT-0054457", "vakt_b": "VAKT-0054463"}],
        ["check_shift_takeover", {"vakt_id": "VAKT-0054457", "ansatt_id": "KP-ANS-153"}],
        ["find_employee", {"sok": "HR", "per_dato": "2026-11-01"}],
        ["get_employee_reviews", {"ansatt_id": "KP-ANS-153"}],
    ]
)


@pytest.fixture(scope="module")
def js_svar(tmp_path_factory: pytest.TempPathFactory) -> list:
    spec = importlib.util.spec_from_file_location("bygg_vaktchat", ROOT / "scripts" / "bygg_vaktchat.py")
    bygg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bygg)
    mappe = tmp_path_factory.mktemp("vaktchat")
    (mappe / "data.json").write_text(json.dumps(bygg.eksporter(), ensure_ascii=False), encoding="utf-8")
    (mappe / "kall.json").write_text(json.dumps(KALL, ensure_ascii=False), encoding="utf-8")
    drivar = mappe / "kjor.js"
    drivar.write_text(
        "const fs=require('fs');const {lagVerktoy}=require(process.argv[2]);"
        "const D=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));const V={};lagVerktoy(D).forEach(t=>V[t.name]=t.run);"
        "const ut=JSON.parse(fs.readFileSync(process.argv[4],'utf8')).map(([n,a])=>{try{return V[n](a)}catch(e){return {feil:e.message}}});"
        "process.stdout.write(JSON.stringify(ut));",
        encoding="utf-8",
    )
    res = subprocess.run([NODE, str(drivar), str(VERKTOY_JS), str(mappe / "data.json"), str(mappe / "kall.json")],
                         capture_output=True, text=True, encoding="utf-8", timeout=120, check=True)
    return json.loads(res.stdout)


def _like(a: object, b: object) -> None:
    """Sammenlign som JSON der 8 og 8.0 regnes som like."""
    norm = lambda x: json.loads(json.dumps(x), parse_float=lambda f: float(f), parse_int=lambda i: float(i))
    assert norm(a) == norm(b)


@pytest.mark.parametrize("i", range(len(VAKTER)), ids=[f"{s[:12]} {d}" for s, d, _, _ in VAKTER])
def test_kandidater_er_like(js_svar: list, i: int) -> None:
    py = vaktrom.get_staffing_candidates(*VAKTER[i])
    js = js_svar[i]
    _like([[r["id"], r["timepris_uten_tillegg"], r["vakter_paa_stasjonen_siste_12_mnd"]] for r in js["egne"]],
          [[r["id"], r["timepris_uten_tillegg"], r["vakter_paa_stasjonen_siste_12_mnd"]] for r in py["egne"]])
    assert [r["id"] for r in js["innleide"]] == [r["id"] for r in py["innleide"]]
    assert [[r["id"], r["fravaerstype"]] for r in js["utilgjengelige"]] == [[r["id"], r["fravaerstype"]] for r in py["utilgjengelige"]]
    _like(js["vaktlengde_timer"], py["vaktlengde_timer"])


def test_kontroll_er_lik(js_svar: list) -> None:
    py = vaktrom.check_staffing_selection(**KALL[5][1])
    assert [[r["id"], r["status"], r["funn"]] for r in js_svar[5]["resultater"]] == [[r["id"], r["status"], r["funn"]] for r in py["resultater"]]


def test_helgevakter_er_like(js_svar: list) -> None:
    py = vaktrom.get_weekend_shift_history(**KALL[6][1])
    _like([[r["ansatt_id"], r["helgevakter"], r["timer"]] for r in js_svar[6]["rader"][:10]],
          [[r["ansatt_id"], r["helgevakter"], r["timer"]] for r in py["rader"][:10]])


def test_vaktplan_er_lik_datafinner(js_svar: list) -> None:
    py = datafinner.run_tool("get_shifts_for_date", {"dato": "2026-11-01"})
    assert sorted((v["vakt_id"], v["ansatt_id"], v["start"], v["slutt"]) for v in js_svar[7]["vakter"]) == \
        sorted((v["vakt_id"], v["ansatt_id"], v["start"], v["slutt"]) for v in py if v.get("start"))


@pytest.mark.parametrize("i", [8, 9])
def test_bytte_er_likt(js_svar: list, i: int) -> None:
    py = vaktrom.check_shift_swap(**KALL[i][1])
    js = js_svar[i]
    assert js["status"] == py["status"]
    assert [[r["navn"], r["status"], r["funn"]] for r in js["retninger"]] == [[r["navn"], r["status"], r["funn"]] for r in py["retninger"]]


def test_overtakelse_er_lik(js_svar: list) -> None:
    py = vaktrom.check_shift_takeover(**KALL[10][1])
    assert [js_svar[10]["status"], js_svar[10]["funn"]] == [py["status"], py["funn"]]


def test_ansattsok_er_likt(js_svar: list) -> None:
    py = vaktrom.find_employee("HR", per_dato="2026-11-01")
    assert [[r["ansatt_id"], r["aktiv"], r["ansiennitet_aar"], len(r["kurs"])] for r in js_svar[11]] == \
        [[r["ansatt_id"], r["aktiv"], r["ansiennitet_aar"], len(r["kurs"])] for r in py]


def test_samtaler_er_like(js_svar: list) -> None:
    py = vaktrom.get_employee_reviews("KP-ANS-153")
    assert [r["samtale_id"] for r in js_svar[12]["samtaler"]] == [r["samtale_id"] for r in py["samtaler"]]
