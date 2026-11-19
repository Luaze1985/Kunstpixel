"""Storskjerm-siden i nettleseren (spec docs/specs/2026-11-19-storskjerm-dashbord.md, plan Task 3)."""

from __future__ import annotations

import functools
import importlib.util
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATO = "2026-11-19"


def _bygg(ut: Path) -> tuple[Path, Path]:
    spec = importlib.util.spec_from_file_location("lag_storskjerm", ROOT / "scripts" / "lag_storskjerm.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul.bygg(ut, DATO)


class _Stille(SimpleHTTPRequestHandler):
    # Artifacten serveres med UTF-8. Uten dette gjetter nettleseren et annet tegnsett, og æøå blir feil.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8",
                      ".json": "application/json; charset=utf-8"}

    def log_message(self, *args) -> None:
        pass


@pytest.fixture(scope="module")
def mapper(tmp_path_factory) -> dict[str, Path]:
    vanlig = tmp_path_factory.mktemp("vanlig")
    _bygg(vanlig)
    uten_frister = tmp_path_factory.mktemp("uten_frister")
    _, data = _bygg(uten_frister)
    d = json.loads(data.read_text("utf-8"))
    d["frister"] = {"antall": {"Forfalt": 0, "I dag": 0, "Denne uka": 0, "Senere": 0}, "rader": [], "skjult": 0}
    data.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    uten_data = tmp_path_factory.mktemp("uten_data")
    side, data = _bygg(uten_data)
    data.unlink()
    return {"vanlig": vanlig, "uten_frister": uten_frister, "uten_data": uten_data}


@pytest.fixture(scope="module")
def nettleser():
    pw = pytest.importorskip("playwright.sync_api", reason="UI-tester krever [ui-test]")
    with pw.sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


def _apne(nettleser, mappe: Path, bredde: int = 1920, hoyde: int = 1080):
    # Hver mappe får sin egen server, så data.json hentes relativt slik som i artifacten.
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Stille, directory=str(mappe)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    side = nettleser.new_page(viewport={"width": bredde, "height": hoyde})
    feil: list[str] = []
    side.on("console", lambda m: feil.append(m.text) if m.type == "error" else None)
    side.on("pageerror", lambda e: feil.append(str(e)))
    side.goto(f"http://127.0.0.1:{srv.server_address[1]}/storskjerm.html")
    side.wait_for_selector("main[data-klar]", timeout=10000)
    return side, feil, srv


@pytest.fixture()
def side(nettleser, mapper):
    s, feil, srv = _apne(nettleser, mapper["vanlig"])
    s.feil = feil
    yield s
    s.close()
    srv.shutdown()


@pytest.fixture()
def data(mapper) -> dict:
    return json.loads((mapper["vanlig"] / "data.json").read_text("utf-8"))


@pytest.mark.parametrize("fid", ["besok", "besok_uke", "saker", "tilfredshet"])
def test_siden_viser_fire_flater_med_kilde(side, fid: str) -> None:
    tekst = side.locator(f"#flate-{fid}").inner_text()
    assert "Kilde:" in tekst


def test_oppmerksomhet_i_toppen(side, data: dict) -> None:
    assert f"{data['oppmerksomhet']} krever oppmerksomhet" in side.locator("header").inner_text()


def test_ukjent_star_som_ord(side) -> None:
    assert "Ukjent" in side.locator("#flate-tilfredshet").inner_text()


def test_flaten_sier_hvilken_dag_besok_gjelder(side) -> None:
    assert "18.11" in side.locator("#flate-besok").inner_text()


def test_fem_felt_under_flatene(side) -> None:
    for i in ["besok-uker", "frister", "utstillinger", "hull"]:
        assert side.locator(f"#{i}").count() == 1, i
    assert "29.10" in side.locator("#hull").inner_text()


def test_tom_fristgruppe_viser_ingen(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["uten_frister"])
    try:
        assert "Ingen" in s.locator("#frister").inner_text()
    finally:
        s.close()
        srv.shutdown()


def test_manglende_data_gir_feilmelding(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["uten_data"])
    try:
        assert "Fant ikke tallene" in s.locator("main").inner_text()
    finally:
        s.close()
        srv.shutdown()


@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1280, 720), (400, 800)])
def test_ingen_sidelengs_rulling(nettleser, mapper, bredde: int, hoyde: int) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        assert s.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    finally:
        s.close()
        srv.shutdown()


def test_alt_far_plass_paa_en_storskjerm(side) -> None:
    assert side.evaluate("document.documentElement.scrollHeight <= window.innerHeight + 1")


def test_ingen_konsollfeil(side) -> None:
    side.wait_for_timeout(300)
    assert [f for f in side.feil if "fonts.g" not in f] == []


def test_brodtekst_minst_20px_paa_storskjerm(side) -> None:
    minste = side.evaluate("""() => Math.min(...[...document.querySelectorAll('main *')]
        .filter(e => e.children.length === 0 && e.textContent.trim() && e.getClientRects().length)
        .map(e => parseFloat(getComputedStyle(e).fontSize)))""")
    assert minste >= 20, minste


def test_data_vises_som_tekst_ikke_html(nettleser, mapper, tmp_path) -> None:
    _, data = _bygg(tmp_path)
    d = json.loads(data.read_text("utf-8"))
    d["hull"].append({"tekst": "<img src=x onerror=window.__hacket=1>", "kilde": "test"})
    data.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    s, _, srv = _apne(nettleser, tmp_path)
    try:
        assert "<img src=x" in s.locator("#hull").inner_text()
        assert s.evaluate("window.__hacket === undefined")
    finally:
        s.close()
        srv.shutdown()


def test_norske_tegn_og_periode(side) -> None:
    assert "Besøk siste 8 uker" in side.locator("#besok-uker").inner_text()
    assert "16.11–18.11" in side.locator("#flate-besok_uke").inner_text()


# 1568x700: vinduet i claude.ai med verktøylinjen, bredere og lavere enn 16:9.
@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1280, 720), (1568, 700)])
def test_ingen_felt_flyter_over(nettleser, mapper, bredde: int, hoyde: int) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        over = s.evaluate("""() => [...document.querySelectorAll('.ss-felt, .ss-flate, .ss-stolper, .ss-liste')]
            .filter(e => e.scrollHeight > e.clientHeight + 1).map(e => e.id)""")
        assert over == []
    finally:
        s.close()
        srv.shutdown()


def test_hull_samlet_per_sluttdato(side) -> None:
    linjer = side.locator("#hull li").all_inner_texts()
    assert sum("29.10" in li for li in linjer) == 1
    assert any("uenige" in li for li in linjer)


def test_ukenavn_overlapper_ikke_paa_mobil(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], 400, 900)
    try:
        bokser = s.evaluate("""() => [...document.querySelectorAll('#besok-uker svg text')]
            .filter(t => t.textContent.startsWith('uke ')).map(t => { const r = t.getBoundingClientRect(); return [r.left, r.right]; })""")
        bokser.sort()
        assert all(a[1] <= b[0] for a, b in zip(bokser, bokser[1:])), bokser
    finally:
        s.close()
        srv.shutdown()


def test_fristfeltet_har_luft_nederst(side) -> None:
    luft = side.evaluate("""() => { const f = document.getElementById('frister');
        const sist = f.lastElementChild.getBoundingClientRect().bottom;
        return f.getBoundingClientRect().bottom - sist; }""")
    assert luft >= 8, luft


@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1568, 700)])
def test_kurven_har_hoyde(nettleser, mapper, bredde: int, hoyde: int) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        assert s.evaluate("document.querySelector('#besok-uker .ss-tegning').clientHeight") >= 120
    finally:
        s.close()
        srv.shutdown()
