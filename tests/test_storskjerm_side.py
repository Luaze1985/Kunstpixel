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
    # Kunstig hull (I3/D5): tilfredshet uten tall skal vises som ordet Ukjent, uansett hva dataene har.
    ukjent = tmp_path_factory.mktemp("ukjent")
    _, data = _bygg(ukjent)
    d = json.loads(data.read_text("utf-8"))
    for f in d["flater"]:
        if f["id"] == "tilfredshet":
            f.update(verdi=None, status="Ukjent", sammenligning="kilden dekker ikke perioden")
    data.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return {"vanlig": vanlig, "uten_frister": uten_frister, "uten_data": uten_data, "ukjent": ukjent}


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


def _tilfredshet_mangler() -> bool:
    """R5 forlenget besok_tilfredshet. Testene følger sluttdatoen i museum.db."""
    from src.kunstpixel.core import db
    return db.execute_read_query("SELECT max(dato) AS m FROM besok_tilfredshet")[0]["m"] < "2026-11-18"


def test_ukjent_star_som_ord(side) -> None:
    assert ("Ukjent" in side.locator("#flate-tilfredshet").inner_text()) == _tilfredshet_mangler()


def test_ukjent_vises_som_ord_med_kunstig_hull(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["ukjent"])
    try:
        assert "Ukjent" in s.locator("#flate-tilfredshet").inner_text()
    finally:
        s.close()
        srv.shutdown()


def test_flaten_sier_hvilken_dag_besok_gjelder(side) -> None:
    assert "18.11" in side.locator("#flate-besok").inner_text()


def test_fem_felt_under_flatene(side) -> None:
    for i in ["besok-uker", "frister", "utstillinger", "hull"]:
        assert side.locator(f"#{i}").count() == 1, i
    assert "Slutter " in side.locator("#hull").inner_text()


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
    datoer = [li.split(":")[0] for li in linjer if li.startswith("Slutter ")]
    assert datoer and len(datoer) == len(set(datoer))  # én linje per sluttdato
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


# Oppsett C «Én ting om gangen» (DECISIONS SC1–SC6, 2026-11-22): fire tall står fast, én stor flate vises.
FELT = ["besok-uker", "frister", "utstillinger", "hull"]


def _synlige(s) -> list[str]:
    return s.evaluate("ids => ids.filter(i => document.getElementById(i).getClientRects().length)", FELT)


def test_en_flate_om_gangen(side) -> None:
    assert _synlige(side) == ["besok-uker"]


@pytest.mark.parametrize("fid", FELT)
def test_fanen_bytter_flate(side, fid: str) -> None:
    side.click(f"#fane-{fid}")
    assert _synlige(side) == [fid]


def test_forfalte_frister_vises_med_dager_over(side, data: dict) -> None:
    forfalt = [r for r in data["frister"]["rader"] if r["gruppe"] == "Forfalt"]
    if not forfalt:
        pytest.skip("ingen forfalte frister i dataene")
    side.click("#fane-frister")
    tekst = side.locator("#frister").inner_text()
    for r in forfalt[:4]:
        assert r["ref"] in tekst, r["ref"]
    assert "dager over" in tekst
    assert str(len(forfalt)) == side.locator("#frister .ss-stort").inner_text()


def test_underlaget_viser_radene_bak(side, data: dict) -> None:
    antall = {"besok-uker": len(data["besok_uker"]), "frister": len(data["frister"]["rader"]),
              "utstillinger": len(data["utstillinger"]),
              "hull": len([h for h in data["hull"] if h["type"] == "slutter"])}
    side.click("#underlag")
    for fid in FELT:
        side.click(f"#fane-{fid}")
        assert side.locator(f"#{fid} .ss-tab tbody tr").count() == antall[fid], fid
        assert side.locator(f"#{fid} .ss-tab").is_visible()
        assert "Kilde:" in side.locator(f"#{fid}").inner_text()
    side.click("#underlag")
    assert not side.locator("#hull .ss-tab").is_visible()


def test_tallet_hopper_til_flaten(side) -> None:
    side.click("#flate-saker")
    assert _synlige(side) == ["frister"]
    side.click("#flate-tilfredshet")
    assert _synlige(side) == ["hull"]


def test_flaten_bytter_selv(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"])
    try:
        s.wait_for_function("document.getElementById('frister').getClientRects().length > 0", timeout=20000)
        s.click("#bytting")  # Stopp bytting
        s.wait_for_timeout(13000)
        assert _synlige(s) == ["frister"]
    finally:
        s.close()
        srv.shutdown()


@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1280, 720), (1568, 700)])
@pytest.mark.parametrize("underlag", [False, True])
def test_hver_flate_far_plass(nettleser, mapper, bredde: int, hoyde: int, underlag: bool) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        if underlag:
            s.click("#underlag")
        for fid in FELT:
            s.click(f"#fane-{fid}")
            over = s.evaluate("""() => [...document.querySelectorAll('.ss-scene, .ss-felt, .ss-visning, .ss-flate, .ss-stolper, .ss-liste')]
                .filter(e => e.getClientRects().length && e.scrollHeight > e.clientHeight + 1).map(e => e.id || e.className)""")
            assert over == [], (fid, over)
            assert s.evaluate("document.documentElement.scrollHeight <= window.innerHeight + 1"), fid
    finally:
        s.close()
        srv.shutdown()


@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1568, 700)])
def test_kurven_har_hoyde(nettleser, mapper, bredde: int, hoyde: int) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        assert s.evaluate("document.querySelector('#besok-uker .ss-tegning').clientHeight") >= 120
    finally:
        s.close()
        srv.shutdown()
