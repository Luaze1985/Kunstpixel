"""KI-chat og Drift og HR i storskjermen (spec docs/specs/2026-11-19-storskjerm-chat.md, DECISIONS SC8–SC12)."""

from __future__ import annotations

import base64
import functools
import gzip
import importlib.util
import sqlite3
import threading
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATO = "2026-11-19"


def _modul():
    spec = importlib.util.spec_from_file_location("lag_storskjerm", ROOT / "scripts" / "lag_storskjerm.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture(scope="module")
def mappe(tmp_path_factory) -> Path:
    ut = tmp_path_factory.mktemp("chat")
    _modul().bygg(ut, DATO)
    return ut


@pytest.fixture(scope="module")
def instruks(mappe: Path) -> str:
    return (mappe / "chat-instruks.txt").read_text("utf-8")


# --- Byggefilene ---

def test_databasen_pakkes_ut_til_samme_bytes(mappe: Path) -> None:
    raa = gzip.decompress(base64.b64decode((mappe / "museum.db.gz.txt").read_text("ascii")))
    assert raa == _modul().DB.read_bytes()


def test_instruksen_bruker_datoen_fra_dataene(instruks: str) -> None:
    assert f"I DAG er {DATO}" in instruks
    assert f"'{DATO[:4]}-01-01'" in instruks
    assert f"(dato BETWEEN '{DATO[:4]}-01-01' AND '{DATO}')" in instruks or f"'{DATO}'" in instruks


def test_instruksen_har_ingen_maskindato(instruks: str) -> None:
    assert "date('now'" not in instruks


def test_aldri_linjen_motsier_seg_ikke(instruks: str) -> None:
    linje = next(l for l in instruks.splitlines() if "ALDRI" in l and "I DAG" in l)
    aldri = linje.split("ALDRI", 1)[1]
    assert DATO not in aldri, linje


@pytest.mark.parametrize("tekst", ["aldri med ID", "to kilder er uenige", "Kilde:", "# Kjente hull", "# metrics.md",
                                   "# entities.md", "DIAGRAM:", "VALG:"])
def test_instruksen_har_reglene(instruks: str, tekst: str) -> None:
    assert tekst in instruks


def test_instruksen_har_alle_tabellene(instruks: str) -> None:
    with sqlite3.connect(_modul().DB.as_uri() + "?mode=ro", uri=True) as con:
        tabeller = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")]
    assert tabeller
    for t in tabeller:
        assert f"- {t}(" in instruks, t


def test_instruksen_far_plass_i_ett_kall(instruks: str) -> None:
    assert len(instruks.encode("utf-8")) < 100 * 1024


# --- Siden i nettleseren, med en falsk Claude ---

class _Stille(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8",
                      ".json": "application/json; charset=utf-8", ".txt": "text/plain; charset=utf-8"}

    def log_message(self, *args) -> None:
        pass


# Falsk window.claude: sample kaller sql-verktøyet med det testen har lagt i window.__sporringer,
# og svarer med teksten i window.__svar. Ingen ekte Claude.
FALSK_CLAUDE = """
window.__kall = [];
window.__verktoysvar = [];
window.claude = { use: async (navn) => {
  if (navn !== 'sample' || window.__utenSample) return null;
  const s = async (meldinger, opt) => {
    window.__kall.push(meldinger);
    for (const q of (window.__sporringer || [])) {
      try { window.__verktoysvar.push(await opt.tools[0].execute({ sporring: q }, {})); }
      catch (e) { window.__verktoysvar.push('FEIL: ' + e.message); }
    }
    const text = window.__svar || 'Svar.\\nKilde: test';
    opt.onText && opt.onText({ text, delta: text });
    return { text, truncated: false };
  };
  s.limits = async () => ({ maxPromptBytes: 262144, tools: { maxCount: 8 } });
  return s;
} };
"""


@pytest.fixture(scope="module")
def nettleser():
    pw = pytest.importorskip("playwright.sync_api", reason="UI-tester krever [ui-test]")
    with pw.sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture(scope="module")
def server(mappe: Path):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Stille, directory=str(mappe)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/storskjerm.html"
    srv.shutdown()


def _apne(nettleser, url: str, init: str | None = FALSK_CLAUDE, bredde: int = 1920, hoyde: int = 1080):
    s = nettleser.new_page(viewport={"width": bredde, "height": hoyde})
    s.feil = []
    s.on("pageerror", lambda e: s.feil.append(str(e)))
    if init:
        s.add_init_script(init)
    s.goto(url)
    s.wait_for_selector("main[data-klar]", timeout=10000)
    return s


def _nett() -> bool:
    try:
        urllib.request.urlopen("https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.12.0/sql-wasm.min.js", timeout=5)
        return True
    except Exception:
        return False


trenger_nett = pytest.mark.skipif(not _nett(), reason="sql.js hentes fra cdnjs")


# SC13 (Lars 2026-11-22): chatten står fast til høyre for dashbordet hele tiden, ingen egen knapp.
def _med_chat(s) -> None:
    s.wait_for_selector("body.med-chat", timeout=5000)


def test_chatten_staar_fast_ved_siden_av_dashbordet(nettleser, server) -> None:
    s = _apne(nettleser, server)
    try:
        _med_chat(s)
        m = s.evaluate("""() => { const a = document.querySelector('main').getBoundingClientRect();
            const c = document.getElementById('skuff').getBoundingClientRect();
            return { mainHoyre: a.right, chatVenstre: c.left, chatBredde: c.width, chatHoyde: c.height, vinduB: innerWidth, vinduH: innerHeight }; }""")
        assert m["chatVenstre"] >= m["mainHoyre"] - 1, m        # dekker ikke dashbordet
        assert m["chatBredde"] >= 0.2 * m["vinduB"], m
        assert m["chatHoyde"] >= 0.9 * m["vinduH"], m
        assert s.locator("#skuff").is_visible() and s.locator("#forslag button").count() == 4
        assert s.locator("#kichat-knapp").count() == 0
        assert s.locator("#drift-hr-knapp").is_visible()
        s.keyboard.press("Escape")
        assert s.locator("#skuff").is_visible()                 # Esc lukker ikke kolonnen
        assert s.feil == []
    finally:
        s.close()


def test_uten_claude_far_dashbordet_hele_skjermen(nettleser, server) -> None:
    s = _apne(nettleser, server, FALSK_CLAUDE + "window.__utenSample = true;")
    try:
        s.wait_for_timeout(800)
        assert s.locator("body.med-chat").count() == 0
        assert not s.locator("#skuff").is_visible()
        assert s.evaluate("document.querySelector('main').getBoundingClientRect().width >= innerWidth - 1")
        assert s.locator("#drift-hr-knapp").is_visible()
    finally:
        s.close()


def test_databasen_lastes_ikke_for_skuffen_aapnes(nettleser, server) -> None:
    s = _apne(nettleser, server)
    try:
        s.wait_for_timeout(800)
        assert s.evaluate("performance.getEntriesByType('resource').some(r => r.name.includes('museum.db'))") is False
    finally:
        s.close()


def test_testmerket_er_borte(nettleser, server) -> None:
    s = _apne(nettleser, server)
    try:
        assert "TESTVERSJON" not in s.locator("body").inner_text()
    finally:
        s.close()


@trenger_nett
def test_chatten_svarer_med_sql_og_tegner_diagram(nettleser, server) -> None:
    init = FALSK_CLAUDE + """
      window.__sporringer = ["SELECT count(*) AS n FROM hr_ansatte", "DELETE FROM hr_ansatte",
                             "SELECT 1; SELECT 2", "WITH x AS (SELECT value AS v FROM json_each('[1,2,3]')) SELECT v FROM x"];
      window.__svar = 'Tre tall.\\nKilde: test\\nDIAGRAM: {"tittel": "T", "etiketter": ["a", "<img src=x onerror=window.__hacket=1>"], "verdier": [1, 2], "enhet": "kr"}';
    """
    s = _apne(nettleser, server, init)
    try:
        _med_chat(s)
        s.locator("#forslag button").first.click()
        s.wait_for_selector(".sk-claude .sk-handling", timeout=90000)
        svar = s.evaluate("window.__verktoysvar")
        assert svar[0]["antall"] == 1 and svar[0]["rader"][0][0] > 0
        assert str(svar[1]).startswith("FEIL") and str(svar[2]).startswith("FEIL")
        assert svar[3]["antall"] == 3
        tekst = s.locator(".sk-claude").last.inner_text()
        assert "DIAGRAM:" not in tekst and "<img src=x" in tekst
        assert s.locator(".sk-claude .sk-diagram .ss-stolpe").count() == 2
        assert s.evaluate("window.__hacket === undefined")
        forste = s.evaluate("window.__kall[0][0].content")
        assert forste.startswith("Du er KI-chat") and "I DAG er" in forste
    finally:
        s.close()


@trenger_nett
def test_drift_og_hr_bruker_datoen_fra_dataene(nettleser, server) -> None:
    s = _apne(nettleser, server)
    try:
        s.click("#drift-hr-knapp")
        s.wait_for_selector("#rp-innhold table", timeout=90000)
        s.click("#rp-innhold .sk-handling button")
        sql = s.locator("#rp-innhold .sk-sql").inner_text()
        assert DATO in sql and "{IDAG}" not in sql
        assert s.feil == []
    finally:
        s.close()


# I claude.ai står chatten til høyre. Dashbordet skal fortsatt få plass uten rulling.
@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (1280, 720), (1568, 700)])
def test_alt_far_plass_med_chatkolonnen(nettleser, server, bredde: int, hoyde: int) -> None:
    s = _apne(nettleser, server, bredde=bredde, hoyde=hoyde)
    try:
        _med_chat(s)
        assert s.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        for underlag in (False, True):
            if underlag:
                s.click("#underlag")
            for fid in ["besok-uker", "frister", "utstillinger", "hull"]:
                s.click(f"#fane-{fid}")
                over = s.evaluate("""() => [...document.querySelectorAll('.ss-scene, .ss-felt, .ss-visning, .ss-flate, .ss-stolper, .ss-liste')]
                    .filter(e => e.getClientRects().length && e.scrollHeight > e.clientHeight + 1).map(e => e.id || e.className)""")
                assert over == [], (fid, underlag, over)
                assert s.evaluate("document.documentElement.scrollHeight <= window.innerHeight + 1"), (fid, underlag)
    finally:
        s.close()


def test_mobil_chatten_under_dashbordet_uten_sidelengs_rulling(nettleser, server) -> None:
    s = _apne(nettleser, server, bredde=400, hoyde=800)
    try:
        _med_chat(s)
        assert s.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert s.evaluate("document.getElementById('skuff').getBoundingClientRect().top >= "
                          "document.querySelector('main').getBoundingClientRect().bottom - 1")
    finally:
        s.close()
