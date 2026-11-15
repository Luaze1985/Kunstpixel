"""Lederens data- og nettleserkontrakt. Kjør: py -3.13 -m pytest tests/test_ledervalidering.py -v."""

from __future__ import annotations

import sqlite3
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from src.kunstpixel.adapters.datafinner import DatafinnerHandler, SYSTEM_CHAT, run_tool


@pytest.fixture(scope="module")
def leder_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DatafinnerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


@pytest.fixture()
def leder_side(leder_server):
    playwright_module = pytest.importorskip("playwright.sync_api", reason="UI-tester krever [ui-test]; bruk scripts/valider_leder.ps1")
    sync_playwright = playwright_module.sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.route("**/api/status", lambda route: route.fulfill(json={"llm": True, "llm_modell": "Testmodell"}))
        yield page, leder_server
        browser.close()


def test_database_integritet_og_fremmednokler(db_path: Path) -> None:
    with sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True) as con:
        con.execute("PRAGMA query_only=ON")
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []


@pytest.mark.parametrize("tabell,kolonne", [
    ("hr_ansatte", "ansatt_id"),
    ("hr_personalmapper", "saksnr"),
    ("utstilling_okonomi", "utstilling_id"),
    ("dagsbesok", "dato"),
])
def test_lederdata_har_unike_og_ikke_tomme_nokler(db_conn: sqlite3.Connection, tabell: str, kolonne: str) -> None:
    antall, unike, tomme = db_conn.execute(
        f'SELECT count(*), count(DISTINCT "{kolonne}"), '
        f'SUM(CASE WHEN "{kolonne}" IS NULL OR "{kolonne}" = "" THEN 1 ELSE 0 END) FROM "{tabell}"'
    ).fetchone()
    assert antall > 0 and antall == unike and tomme == 0


def test_lederdata_har_gyldige_verdier_og_relaterte_rader(db_conn: sqlite3.Connection) -> None:
    assert db_conn.execute("SELECT count(*) FROM dagsbesok WHERE er_aapent NOT IN (0, 1) OR er_aapent IS NULL").fetchone()[0] == 0
    assert db_conn.execute("SELECT count(*) FROM hr_personalmapper WHERE gradering != 'LEDER_FORTROLIG' OR gradering IS NULL").fetchone()[0] == 0
    assert db_conn.execute(
        "SELECT count(*) FROM hr_personalmapper p LEFT JOIN hr_ansatte a USING (ansatt_id) WHERE a.ansatt_id IS NULL"
    ).fetchone()[0] == 0
    assert db_conn.execute(
        "SELECT count(*) FROM utstilling_okonomi o LEFT JOIN utstillinger_historikk u USING (utstilling_id) WHERE u.utstilling_id IS NULL"
    ).fetchone()[0] == 0


def test_lederens_navnefelle_kan_avklares_med_data(db_conn: sqlite3.Connection) -> None:
    fasit = {r[0] for r in db_conn.execute("SELECT ansatt_id FROM hr_ansatte WHERE navn='Anja Eriksen'")}
    funn = run_tool("resolve_employee", {"sok": "Anja Eriksen"})
    assert fasit == {"KP-ANS-047", "KP-ANS-115"}
    assert funn["status"] == "tvetydig"
    assert {k["ansatt_id"] for k in funn["kandidater"]} == fasit


def test_ki_faar_instruks_om_kort_svar_og_kilde() -> None:
    instruks = SYSTEM_CHAT.format(ukedag="søndag", dato="2026-11-15", rolle="Museumsdirektør")
    assert "1–3 korte linjer" in instruks
    assert "Kilde:" in instruks
    assert "ikke legg til ekstra nøkkeltall" in instruks.lower()


def test_leder_aapner_til_sporsmal_uten_menystoy(leder_side) -> None:
    page, base = leder_side
    page.goto(base, wait_until="networkidle")
    assert page.get_by_role("heading", name="Spør om data", exact=True).is_visible()
    assert page.locator("#chat-felt").is_enabled()
    assert "KI konfigurert" in page.locator("#chat-status").inner_text()
    assert page.locator("#chat-felt").evaluate("(e) => document.activeElement === e")
    assert page.locator("#rollevalg").input_value() == "Museumsdirektør"
    for navn in ("Spør om data", "Rapporter", "Tabeller"):
        assert page.get_by_role("navigation", name="Innhold").get_by_role("button", name=navn).is_visible()
    assert not page.get_by_role("navigation", name="Innhold").get_by_text("Arena", exact=True).is_visible()
    assert not page.get_by_role("complementary", name="Fasit").is_visible()


def test_leder_spor_og_aapner_tabell(leder_side) -> None:
    page, base = leder_side
    sendt = []
    def svar(route):
        sendt.append(route.request.post_data_json)
        route.fulfill(json={"tekst": "Nettoresultatet er 657 556 kr.", "verktoykall": [{"navn": "get_exhibition_economy", "args": {"exhibition_id": "KP-EXH-2026-FOKUS-2"}, "ok": True}], "data_hentet": [{"kilde": "utstilling_okonomi"}]})
    page.route("**/api/chat", svar)
    page.goto(base, wait_until="networkidle")
    page.locator("#chat-felt").fill("Hva er nettoresultatet for KP-EXH-2026-FOKUS-2?")
    page.get_by_role("button", name="Send", exact=True).click()
    page.get_by_text("Nettoresultatet er 657 556 kr.").wait_for()
    assert "KI tilkoblet" in page.locator("#chat-status").inner_text()
    assert not page.get_by_text("Forslag til spørsmål", exact=True).is_visible()
    assert sendt[0]["rolle"] == "Museumsdirektør"
    assert page.get_by_role("complementary", name="Fasit").is_visible()
    assert "get_exhibition_economy" in page.get_by_role("complementary", name="Fasit").inner_text()
    page.get_by_role("navigation", name="Innhold").get_by_role("button", name="Tabeller").click()
    page.get_by_role("heading", name="Alle tabellene i databasen").wait_for()
    page.get_by_role("link", name="hr_ansatte", exact=True).click()
    page.get_by_role("heading", name="hr_ansatte").wait_for()
    assert page.locator("main table tbody tr").count() > 0


def test_ki_utilgjengelig_gir_fortsatt_tilgang_til_rapporter_og_tabeller(leder_side) -> None:
    page, base = leder_side
    page.route("**/api/status", lambda route: route.fulfill(json={"llm": False}))
    page.goto(base, wait_until="networkidle")
    assert page.locator("#chat-felt").is_disabled()
    assert "KI er utilgjengelig" in page.locator("main").inner_text()
    nav = page.get_by_role("navigation", name="Innhold")
    nav.get_by_role("button", name="Rapporter").click()
    page.get_by_role("heading", name="Museumsdirektør").wait_for()
    nav.get_by_role("button", name="Tabeller").click()
    page.get_by_role("heading", name="Alle tabellene i databasen").wait_for()


def test_ki_feil_vises_uten_falsk_tilkobling(leder_side) -> None:
    page, base = leder_side
    page.route("**/api/chat", lambda route: route.fulfill(status=502, json={"error": "Claude svarte ikke."}))
    page.goto(base, wait_until="networkidle")
    page.locator("#chat-felt").fill("Finn et tall")
    page.get_by_role("button", name="Send", exact=True).click()
    page.get_by_role("alert").get_by_text("Claude svarte ikke.").wait_for()
    assert "KI svarte ikke" in page.locator("#chat-status").inner_text()
    assert "KI tilkoblet" not in page.locator("#chat-status").inner_text()


def test_mobil_har_sporsmal_og_tabellvei(leder_side) -> None:
    page, base = leder_side
    page.set_viewport_size({"width": 390, "height": 844})
    page.route("**/api/chat", lambda route: route.fulfill(json={"tekst": "Nettoresultatet er 657 556 kr.", "verktoykall": [{"navn": "get_exhibition_economy", "args": {}, "ok": True}], "data_hentet": [{"kilde": "utstilling_okonomi"}]}))
    page.goto(base, wait_until="networkidle")
    assert page.get_by_role("heading", name="Spør om data", exact=True).is_visible()
    page.locator("#chat-felt").fill("Hva er nettoresultatet?")
    page.get_by_role("button", name="Send", exact=True).click()
    page.get_by_text("Nettoresultatet er 657 556 kr.").wait_for()
    assert page.get_by_role("complementary", name="Fasit").is_visible()
    page.locator("#mobilvalg").select_option("katalog")
    page.get_by_role("heading", name="Alle tabellene i databasen").wait_for()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
