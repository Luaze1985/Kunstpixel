"""Storskjerm-siden i nettleseren (spec docs/specs/2026-11-19-storskjerm-dashbord.md, DECISIONS SC1–SC20).

Siden har seks roller. Hver rolle har fire tall og flere flater, én flate vises om gangen, og hver flate har
et underlag. Testene går gjennom alle roller og flater, så nye roller dekkes uten nye tester.
"""

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


def _endre(mappe: Path, f) -> None:
    data = mappe / "data.json"
    d = json.loads(data.read_text("utf-8"))
    f(d)
    data.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


class _Stille(SimpleHTTPRequestHandler):
    # Artifacten serveres med UTF-8. Uten dette gjetter nettleseren et annet tegnsett, og æøå blir feil.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8",
                      ".json": "application/json; charset=utf-8"}

    def log_message(self, *args) -> None:
        pass


def _uten_frister(d: dict) -> None:
    for r in d["roller"]:
        for p in r["flater"]:
            if p["type"] == "frister":
                p["data"] = {"antall": {"Forfalt": 0, "I dag": 0, "Denne uka": 0, "Senere": 0}, "rader": []}
                p["underlag"]["rader"] = []


def _ukjent_tilfredshet(d: dict) -> None:
    # Kunstig hull (I3/D5): et tall uten kilde skal stå som ordet Ukjent, uansett hva dataene har.
    pub = next(r for r in d["roller"] if r["id"] == "publikum")
    f = next(f for f in pub["fliser"] if f["id"] == "tilfredshet_uke")
    f.update(verdi=None, status="Ukjent", sammenligning="kilden dekker ikke perioden", endring_pst=None, retning=0)


@pytest.fixture(scope="module")
def mapper(tmp_path_factory) -> dict[str, Path]:
    ut = {}
    for navn in ("vanlig", "uten_frister", "uten_data", "ukjent", "html"):
        ut[navn] = tmp_path_factory.mktemp(navn)
        _bygg(ut[navn])
    _endre(ut["uten_frister"], _uten_frister)
    (ut["uten_data"] / "data.json").unlink()
    _endre(ut["ukjent"], _ukjent_tilfredshet)
    _endre(ut["html"], lambda d: d["roller"][0]["flater"].append(
        {"id": "test", "type": "liste", "tittel": "Test", "kilde": "test", "forklaring": "",
         "data": {"rader": ["<img src=x onerror=window.__hacket=1>"]},
         "underlag": {"kolonner": ["<b>K</b>"], "rader": [["<img src=y onerror=window.__hacket=2>"]], "tall": []}}))
    return ut


@pytest.fixture(scope="module")
def nettleser():
    pw = pytest.importorskip("playwright.sync_api", reason="UI-tester krever [ui-test]")
    with pw.sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


def _apne(nettleser, mappe: Path, bredde: int = 1920, hoyde: int = 1080, hash_: str = ""):
    # Hver mappe får sin egen server, så data.json hentes relativt slik som i artifacten.
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Stille, directory=str(mappe)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    side = nettleser.new_page(viewport={"width": bredde, "height": hoyde})
    feil: list[str] = []
    side.on("console", lambda m: feil.append(m.text) if m.type == "error" else None)
    side.on("pageerror", lambda e: feil.append(str(e)))
    side.goto(f"http://127.0.0.1:{srv.server_address[1]}/storskjerm.html{hash_}")
    side.wait_for_selector("main[data-klar]", timeout=10000)
    return side, feil, srv


@pytest.fixture()
def side(nettleser, mapper):
    s, feil, srv = _apne(nettleser, mapper["vanlig"])
    s.feil = feil
    yield s
    s.close()
    srv.shutdown()


@pytest.fixture(scope="module")
def data(mapper) -> dict:
    return json.loads((mapper["vanlig"] / "data.json").read_text("utf-8"))


ROLLER = ["direktor", "drift", "hr", "okonomi", "publikum", "samling"]
OVERFLYT = """() => [...document.querySelectorAll('.ss-scene, .ss-felt, .ss-flate, .ss-stolper, .ss-liste')]
    .filter(e => e.getClientRects().length && e.scrollHeight > e.clientHeight + 1).map(e => e.id || e.className)"""


def _synlig_flate(s) -> list[str]:
    return s.evaluate("""() => [...document.querySelectorAll('section.ss-felt[id^="flate-"]')]
        .filter(e => e.getClientRects().length).map(e => e.id.slice(6))""")


# --- Rollevalg ---

def test_seks_roller_i_toppen_og_direktor_forst(side) -> None:
    for r in ROLLER:
        assert side.locator(f"#rolle-{r}").count() == 1, r
    assert side.locator("#rolle-direktor").get_attribute("aria-pressed") == "true"


def test_rollevalg_bytter_tallene(side, data: dict) -> None:
    for r in data["roller"]:
        side.click(f"#rolle-{r['id']}")
        vist = side.locator(".ss-flate .ss-etikett").all_inner_texts()
        assert vist == [f["navn"] for f in r["fliser"]], r["id"]


def test_lenke_med_rolle_aapner_rollen(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], hash_="#hr")
    try:
        assert s.locator("#rolle-hr").get_attribute("aria-pressed") == "true"
        assert s.locator("#flis-fravaer_uke").count() == 1
    finally:
        s.close()
        srv.shutdown()


def test_varseltall_paa_rollen_stemmer(side, data: dict) -> None:
    for r in data["roller"]:
        antall = sum(f["status"] in ("Følg med", "Over terskel") for f in r["fliser"])
        prikk = side.locator(f"#rolle-{r['id']} .ss-prikk")
        if antall:
            assert prikk.inner_text() == str(antall), r["id"]
        else:
            assert prikk.count() == 0, r["id"]


# --- Fliser ---

def test_flis_viser_tall_endring_og_kilde_ved_mus(side, data: dict) -> None:
    f = data["roller"][0]["fliser"][0]
    flis = side.locator(f"#flis-{f['id']}")
    assert flis.get_attribute("title") == "Kilde: " + f["kilde"]
    tekst = flis.inner_text()
    assert f["sammenligning"] in tekst and "%" in tekst
    assert flis.locator(".ss-spark svg").count() == 1


def test_normal_status_vises_ikke_som_pille(side, data: dict) -> None:
    for f in data["roller"][0]["fliser"]:
        pille = side.locator(f"#flis-{f['id']} .ss-status")
        assert pille.count() == (0 if f["status"] == "Normal" else 1), f["id"]


def test_ukjent_star_som_ord(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["ukjent"], hash_="#publikum")
    try:
        assert "Ukjent" in s.locator("#flis-tilfredshet_uke").inner_text()
    finally:
        s.close()
        srv.shutdown()


def test_millioner_vises_kort(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], hash_="#okonomi")
    try:
        assert "mill. kr" in s.locator("#flis-inntekter").inner_text()
    finally:
        s.close()
        srv.shutdown()


# --- Flater og underlag ---

def test_en_flate_om_gangen(side, data: dict) -> None:
    assert _synlig_flate(side) == [data["roller"][0]["flater"][0]["id"]]


def test_hver_fane_bytter_flate_i_hver_rolle(side, data: dict) -> None:
    for r in data["roller"]:
        side.click(f"#rolle-{r['id']}")
        for p in r["flater"]:
            side.click(f"#fane-{p['id']}")
            assert _synlig_flate(side) == [p["id"]], (r["id"], p["id"])


def test_underlaget_viser_radene_bak(side, data: dict) -> None:
    side.click("#underlag")
    for r in data["roller"]:
        side.click(f"#rolle-{r['id']}")
        side.click("#underlag")
        for p in r["flater"]:
            side.click(f"#fane-{p['id']}")
            u = side.locator(f"#flate-{p['id']} .ss-tab")
            assert u.is_visible(), (r["id"], p["id"])
            assert u.locator("tbody tr").count() == len(p["underlag"]["rader"]), (r["id"], p["id"])
            assert "Kilde:" in side.locator(f"#flate-{p['id']}").inner_text()


def test_forfalte_frister_vises_med_dager_over(side, data: dict) -> None:
    p = next(p for p in data["roller"][0]["flater"] if p["type"] == "frister")
    forfalt = [r for r in p["data"]["rader"] if r["gruppe"] == "Forfalt"]
    if not forfalt:
        pytest.skip("ingen forfalte frister i dataene")
    side.click("#fane-frister")
    tekst = side.locator("#flate-frister").inner_text()
    for r in forfalt[:3]:
        assert r["ref"] in tekst, r["ref"]
    assert "dager over" in tekst
    assert str(len(forfalt)) == side.locator("#flate-frister .ss-stort").inner_text()


def test_tom_fristgruppe_viser_ingen(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["uten_frister"])
    try:
        s.click("#fane-frister")
        assert "Ingen" in s.locator("#flate-frister").inner_text()
    finally:
        s.close()
        srv.shutdown()


def test_flaten_bytter_selv_og_kan_stoppes(nettleser, mapper, data: dict) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"])
    try:
        andre = data["roller"][0]["flater"][1]["id"]
        s.wait_for_function(f"document.getElementById('flate-{andre}').getClientRects().length > 0", timeout=20000)
        s.click("#bytting")  # Stopp bytting
        s.wait_for_timeout(13000)
        assert _synlig_flate(s) == [andre]
    finally:
        s.close()
        srv.shutdown()


# --- Sikkerhet, feil og lesbarhet ---

def test_data_vises_som_tekst_ikke_html(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["html"])
    try:
        s.click("#fane-test")
        assert "<img src=x" in s.locator("#flate-test").inner_text()
        s.click("#underlag")
        assert "<img src=y" in s.locator("#flate-test").inner_text()
        assert s.evaluate("window.__hacket === undefined")
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


def test_ingen_konsollfeil(side) -> None:
    side.wait_for_timeout(300)
    assert [f for f in side.feil if "fonts.g" not in f] == []


def test_brodtekst_minst_20px_paa_storskjerm(side, data: dict) -> None:
    for r in data["roller"]:
        side.click(f"#rolle-{r['id']}")
        minste = side.evaluate("""() => Math.min(...[...document.querySelectorAll('main *')]
            .filter(e => e.children.length === 0 && e.textContent.trim() && e.getClientRects().length)
            .map(e => parseFloat(getComputedStyle(e).fontSize)))""")
        assert minste >= 20, (r["id"], minste)


@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1280, 720), (400, 800)])
def test_ingen_sidelengs_rulling(nettleser, mapper, bredde: int, hoyde: int) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        for r in ROLLER:
            s.click(f"#rolle-{r}")
            assert s.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), r
    finally:
        s.close()
        srv.shutdown()


# 1568x700: vinduet i claude.ai med verktøylinjen, bredere og lavere enn 16:9.
@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1280, 720), (1568, 700)])
def test_hver_rolle_og_flate_far_plass_paa_en_skjerm(nettleser, mapper, data: dict, bredde: int, hoyde: int) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        s.click("#bytting")
        for r in data["roller"]:
            s.click(f"#rolle-{r['id']}")
            for underlag in (False, True):
                if underlag != (s.locator("#underlag").get_attribute("aria-pressed") == "true"):
                    s.click("#underlag")
                for p in r["flater"]:
                    s.click(f"#fane-{p['id']}")
                    assert s.evaluate(OVERFLYT) == [], (r["id"], p["id"], underlag)
                    assert s.evaluate("document.documentElement.scrollHeight <= window.innerHeight + 1"), (r["id"], p["id"])
    finally:
        s.close()
        srv.shutdown()


@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1568, 700)])
def test_kurven_har_hoyde(nettleser, mapper, bredde: int, hoyde: int) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], bredde, hoyde)
    try:
        assert s.evaluate("document.querySelector('#flate-besok .ss-tegning').clientHeight") >= 120
    finally:
        s.close()
        srv.shutdown()


def test_ukenavn_overlapper_ikke_paa_mobil(nettleser, mapper) -> None:
    s, _, srv = _apne(nettleser, mapper["vanlig"], 400, 900)
    try:
        bokser = s.evaluate("""() => [...document.querySelectorAll('#flate-besok svg text')]
            .filter(t => t.textContent.startsWith('uke') || /^\\d+$/.test(t.textContent))
            .map(t => { const r = t.getBoundingClientRect(); return [r.left, r.right, r.top]; })""")
        rad = sorted(b for b in bokser if abs(b[2] - max(x[2] for x in bokser)) < 2)
        assert all(a[1] <= b[0] for a, b in zip(rad, rad[1:])), rad
    finally:
        s.close()
        srv.shutdown()
