"""Lederens data- og nettleserkontrakt. Kjør: py -3.13 -m pytest tests/test_ledervalidering.py -v."""

from __future__ import annotations

import sqlite3
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from src.kunstpixel.adapters.datafinner import SYSTEM_CHAT, DatafinnerHandler, run_tool


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
    for navn in ("Hjem", "Rapporter", "Tabeller"):  # «Hjem» er KI-chatten (etappe 1, 2026-11-16)
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


# ---------- Etappe 1 (2026-11-16): navigasjon, huskelapp og feilrettinger ----------

def _adr(base: str, rute: str) -> str:
    from urllib.parse import quote
    return base + "/#" + quote(rute, safe="")


def test_meny_har_hjem_og_faa_punkter(leder_side) -> None:
    page, base = leder_side
    page.goto(base, wait_until="networkidle")
    nav = page.get_by_role("navigation", name="Innhold")
    for navn in ("Hjem", "Rapporter", "Tabeller"):
        assert nav.get_by_role("button", name=navn, exact=True).is_visible()
    nav.get_by_text("Mer", exact=True).click()
    assert nav.get_by_role("button", name="Vaktrom", exact=True).is_visible()
    tekst = nav.inner_text()
    assert "Arbeidsflyter" not in tekst and "Søk" not in tekst and "Flater" not in tekst
    # «Jeg er» ligger nederst i menyen, under navigasjonen.
    assert page.evaluate("document.getElementById('meny').compareDocumentPosition(document.getElementById('rollevalg')) & Node.DOCUMENT_POSITION_FOLLOWING")


def test_hjem_fra_rapport_gaar_til_ki(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    page.get_by_role("heading", name="Vaktplan for en dag").wait_for()
    page.get_by_role("navigation", name="Innhold").get_by_role("button", name="Hjem", exact=True).click()
    page.get_by_role("heading", name="Spør om data", exact=True).wait_for()


def test_brodsmuler_og_tilbake(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    sti = page.get_by_role("navigation", name="Du er her")
    sti.get_by_text("Vaktplan for en dag").wait_for()
    assert "Rapporter" in sti.inner_text() and "HR og bemanning" in sti.inner_text()
    page.get_by_role("button", name="Tilbake").click()
    page.get_by_role("heading", name="HR og bemanning", exact=True).wait_for()


def test_rapportvalg_ligger_i_adressen_og_tilbake_virker(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    for dato in ("2026-11-14", "2026-11-13"):
        page.locator("#p-dato").fill(dato)
        page.get_by_role("button", name="Oppdater").click()
        page.wait_for_function(f"decodeURIComponent(location.hash).indexOf('dato={dato}') > 0")
    page.go_back()
    page.wait_for_function("document.getElementById('p-dato') && document.getElementById('p-dato').value === '2026-11-14'")


def test_rad_i_rapport_kan_aapnes_med_alle_felt(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:Museumsdirektør/rapporteringskalender"), wait_until="networkidle")
    page.get_by_role("link", name="Brannøvelsesrapport", exact=True).click()
    detalj = page.get_by_role("region", name="Brannøvelsesrapport")
    detalj.wait_for()
    assert "RP-10" in detalj.inner_text()
    assert "Evaluere evakueringstider" in detalj.inner_text()
    page.go_back()
    detalj.wait_for(state="detached")


def test_dagens_dato_er_lokal_ikke_utc(leder_side) -> None:
    from datetime import datetime

    page, base = leder_side
    norsk = page.context.browser.new_page(viewport={"width": 1400, "height": 900}, timezone_id="Europe/Oslo")
    norsk.clock.install(time=datetime.fromisoformat("2026-11-16T00:30:00+01:00"))
    norsk.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    assert norsk.locator("#p-dato").input_value() == "2026-11-16"
    norsk.close()


def test_rapportmaler_viser_malen_ikke_kalenderen(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:Kvalitetsvokter/rapportmaler"), wait_until="networkidle")
    assert page.locator("#p-mal_id").input_value() == "ML-01"
    page.get_by_text("Driftsrapport").first.wait_for()
    assert "Brannøvelsesrapport" not in page.locator("#midt").inner_text()


def test_vaktliste_viser_stilling_og_stasjon(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    page.locator("#p-dato").fill("2026-11-14")
    page.get_by_role("button", name="Oppdater").click()
    page.locator("main table thead").first.wait_for()
    hoder = page.locator("main table thead").first.inner_text()
    assert "Stilling" in hoder and "Stasjon" in hoder


def test_huskelapp_er_ett_kort_med_spor_ki(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    fasit = page.get_by_role("complementary", name="Fasit")
    fasit.wait_for()
    assert fasit.locator(".af-context-card").count() == 1
    fasit.get_by_role("button", name="Spør KI om dette").click()
    page.get_by_role("heading", name="Spør om data", exact=True).wait_for()
    assert "Vaktplan for en dag" in page.locator("#chat-felt").input_value()


def test_vaktrom_steg_ligger_i_adressen(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "flate:vaktrom"), wait_until="networkidle")
    page.wait_for_function("decodeURIComponent(location.hash) === '#flate:vaktrom/vakt'")


def test_mobil_har_hjem_forst(leder_side) -> None:
    page, base = leder_side
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    forste = page.locator("#mobilvalg option").first
    assert forste.inner_text() == "Hjem" and forste.get_attribute("value") == "flate:chat"
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")