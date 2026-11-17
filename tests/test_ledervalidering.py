"""Lederens data- og nettleserkontrakt. Kjør: py -3.13 -m pytest tests/test_ledervalidering.py -v."""

from __future__ import annotations

import re
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
    page.goto(_adr(base, "flate:chat"), wait_until="networkidle")
    _chat_aapen(page)
    assert page.locator("#chat-felt").is_enabled()
    assert "KI konfigurert" in page.locator("#chat-status").inner_text()
    assert page.locator("#chat-felt").evaluate("(e) => document.activeElement === e")
    assert page.locator("#rollevalg").input_value() == "Museumsdirektør"
    for navn in ("Hjem", "Rapporter", "Tabeller"):  # Hjem har fanene Oversikt og Chat (2026-11-17)
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
    page.goto(_adr(base, "flate:chat"), wait_until="networkidle")
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
    page.goto(_adr(base, "flate:chat"), wait_until="networkidle")
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
    page.goto(_adr(base, "flate:chat"), wait_until="networkidle")
    page.locator("#chat-felt").fill("Finn et tall")
    page.get_by_role("button", name="Send", exact=True).click()
    page.get_by_role("alert").get_by_text("Claude svarte ikke.").wait_for()
    assert "KI svarte ikke" in page.locator("#chat-status").inner_text()
    assert "KI tilkoblet" not in page.locator("#chat-status").inner_text()


def test_mobil_har_sporsmal_og_tabellvei(leder_side) -> None:
    page, base = leder_side
    page.set_viewport_size({"width": 390, "height": 844})
    page.route("**/api/chat", lambda route: route.fulfill(json={"tekst": "Nettoresultatet er 657 556 kr.", "verktoykall": [{"navn": "get_exhibition_economy", "args": {}, "ok": True}], "data_hentet": [{"kilde": "utstilling_okonomi"}]}))
    page.goto(_adr(base, "flate:chat"), wait_until="networkidle")
    _chat_aapen(page)
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


def _chat_aapen(page) -> None:
    """Hjem har fanene Oversikt og Chat (Lars 2026-11-17). Chat-fanen er valgt og skrivefeltet finnes."""
    page.locator("#chat-felt").wait_for()
    assert page.get_by_role("tab", name="Chat").get_attribute("aria-selected") == "true"


def test_hjem_fra_rapport_gaar_til_oversikt(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan"), wait_until="networkidle")
    page.get_by_role("heading", name="Vaktplan for en dag").wait_for()
    page.get_by_role("navigation", name="Innhold").get_by_role("button", name="Hjem", exact=True).click()
    page.get_by_role("region", name="I dag").wait_for()
    assert page.get_by_role("tab", name="Oversikt").get_attribute("aria-selected") == "true"


def test_arena_er_fjernet_fra_siden(leder_side) -> None:
    """Lars 2026-11-17: «Fjern hele Arena». Rådumpen fra øvingscasene skal aldri vises."""
    page, base = leder_side
    page.goto(base, wait_until="networkidle")
    nav = page.get_by_role("navigation", name="Innhold")
    nav.get_by_text("Mer", exact=True).click()
    assert "Arena" not in nav.inner_text() and "Tidsbruk" not in nav.inner_text()
    assert page.locator("#mobilvalg option[value^='arena']").count() == 0
    page.goto(_adr(base, "arena:tidsbruk/T1"), wait_until="networkidle")  # gamle lenker går til Hjem
    page.get_by_role("region", name="I dag").wait_for()
    assert "Dette sier de interne dataene" not in page.locator("main").inner_text()


def test_hjem_har_fanene_oversikt_og_chat(leder_side) -> None:
    """Lars 2026-11-17: Hjem som to faner, så oversikten og chatten ikke står oppå hverandre."""
    page, base = leder_side
    page.goto(base, wait_until="networkidle")
    page.get_by_role("region", name="I dag").wait_for()
    assert page.locator("#chat-felt").count() == 0  # chatten står ikke på Oversikt
    page.get_by_role("tab", name="Chat").click()
    _chat_aapen(page)
    assert page.get_by_role("region", name="I dag").count() == 0
    page.go_back()
    page.get_by_role("region", name="I dag").wait_for()


def test_oversikt_viser_bare_det_som_krever_oppmerksomhet(leder_side) -> None:
    page, base = leder_side
    page.route("**/api/verktoy?navn=get_today_overview*", lambda route: route.fulfill(json={"resultat": {
        "dato": "2026-11-17", "aapent_i_dag": True, "hentet_kl": "09:05",
        "besok": {"navn": "Besøk", "dato": "2026-11-16", "verdi": 300, "normalt": 400, "endring_pst": -25, "status": "Følg med", "rader": []},
        "vakter": {"navn": "Vakter i dag", "verdi": 10, "rader": []},
        "arrangementer": {"navn": "Arrangementer i dag", "verdi": 0, "rader": []},
    }}))
    page.goto(base, wait_until="networkidle")
    kort = page.get_by_role("region", name="I dag")
    kort.get_by_text("Følg med", exact=False).first.wait_for()
    assert not kort.get_by_text("Vakter i dag", exact=False).is_visible()
    kort.get_by_text("Vis 2 andre tall", exact=True).click()
    assert kort.get_by_text("Vakter i dag", exact=False).is_visible()


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
    _chat_aapen(page)
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
    assert forste.inner_text() == "Hjem" and forste.get_attribute("value") == "hjem"
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")


# ---------- Etappe 2 (2026-11-16): kortet «I dag» på Hjem ----------

def _norsk_side(page, naa: str, ki: bool = False):
    from datetime import datetime

    side = page.context.browser.new_page(viewport={"width": 1400, "height": 900}, timezone_id="Europe/Oslo")
    side.route("**/api/status", lambda route: route.fulfill(json={"llm": ki, "llm_modell": "Testmodell"}))
    side.clock.install(time=datetime.fromisoformat(naa))
    return side


def test_i_dag_kortet_virker_uten_ki_paa_stengt_dag(leder_side) -> None:
    page, base = leder_side
    side = _norsk_side(page, "2026-11-16T09:05:00+01:00")
    side.goto(base, wait_until="networkidle")
    kort = side.get_by_role("region", name="I dag")
    kort.wait_for()
    kort.get_by_text(re.compile(r"^Vis \d+ andre tall$")).click()  # besøk er normalt og står bak ett klikk
    tekst = kort.inner_text()
    assert "Stengt i dag" in tekst
    assert "søndag 15.11." in tekst and "391" in tekst  # siste hele åpne dag, ikke dagens syntetiske tall
    assert "Tall per kl." in tekst
    side.get_by_role("tab", name="Chat").click()
    assert side.locator("#chat-felt").is_disabled()  # KI av, oversikten vises likevel
    side.close()


def test_i_dag_tall_aapner_radene_bak(leder_side) -> None:
    page, base = leder_side
    side = _norsk_side(page, "2026-11-16T09:05:00+01:00", ki=True)
    side.goto(base, wait_until="networkidle")
    kort = side.get_by_role("region", name="I dag")
    kort.get_by_role("button", name=re.compile("^Vis radene: Åpne driftsmeldinger")).click()
    kort.locator("table tbody tr").first.wait_for()
    assert kort.locator("table tbody tr").count() > 0
    side.close()


def test_i_dag_mangler_data_er_aldri_gronn(leder_side) -> None:
    page, base = leder_side
    side = _norsk_side(page, "2026-11-16T09:05:00+01:00")
    side.route("**/api/verktoy?navn=get_today_overview*", lambda route: route.fulfill(json={"resultat": {
        "dato": "2026-11-16", "aapent_i_dag": True, "hentet_kl": "09:05",
        "besok": {"navn": "Besøk", "dato": "2026-11-15", "verdi": None, "normalt": None, "endring_pst": None, "status": "Ukjent", "rader": []},
    }}))
    side.goto(base, wait_until="networkidle")
    kort = side.get_by_role("region", name="I dag")
    kort.get_by_text("Mangler data").wait_for()
    assert kort.locator(".af-signal.go").count() == 0
    side.close()


def test_i_dag_viser_farlig_tekst_som_tekst(leder_side) -> None:
    """XSS: navn og radverdier fra serveren skal aldri tolkes som HTML (textContent, ikke innerHTML)."""
    page, base = leder_side
    side = _norsk_side(page, "2026-11-16T09:05:00+01:00")
    farlig = "<img src=x onerror=window.__x=1>"
    side.route("**/api/verktoy?navn=get_today_overview*", lambda route: route.fulfill(json={"resultat": {
        "dato": "2026-11-16", "aapent_i_dag": True, "hentet_kl": "09:05",
        "driftsmeldinger": {"navn": farlig, "verdi": 1, "kilde": farlig,
                            "rader": [{"dato": "2026-11-14", "emne": farlig, "status": "APEN"}]},
    }}))
    side.goto(base, wait_until="networkidle")
    kort = side.get_by_role("region", name="I dag")
    kort.get_by_role("button", name=re.compile("^Vis radene")).click()
    kort.locator("table tbody tr").first.wait_for()
    assert kort.locator("img").count() == 0
    assert side.evaluate("window.__x") is None
    assert farlig in kort.inner_text()
    side.close()


def test_driften_uka_viser_dagene_og_flere_tall(leder_side) -> None:
    """B5: dagene som tabell (mot forrige uke og i fjor), og resten av tallene under «Flere tall»."""
    page, base = leder_side
    page.goto(_adr(base, "rolle:Driftsansvarlig/driften-uka?dato=2026-11-14"), wait_until="networkidle")
    page.get_by_role("heading", name="Driften denne uka").wait_for()
    hoder = page.locator("main table thead").first.inner_text()
    assert "Forrige uke" in hoder and "I fjor" in hoder
    flere = page.get_by_text("Flere tall", exact=True)
    flere.click()
    assert "Tilfredshet" in page.locator("main").inner_text()


def test_driften_uka_er_lesbar_for_leder(leder_side) -> None:
    """Helsesjekk 2026-11-16: merknaden synlig øverst, norske etiketter, ingen true/false eller rå hjelpefelt."""
    page, base = leder_side
    page.goto(_adr(base, "rolle:Driftsansvarlig/driften-uka?dato=2026-11-14"), wait_until="networkidle")
    page.get_by_role("heading", name="Driften denne uka").wait_for()
    page.get_by_text("Besøk sammenlignes med de samme ukedagene", exact=False).first.wait_for()
    assert page.get_by_text("Besøk sammenlignes", exact=False).first.is_visible()  # ikke gjemt i «Flere tall»
    assert "Endring mot forrige uke (%)" in page.locator(".af-kpis").inner_text()
    page.get_by_text("Flere tall", exact=True).click()
    tekst = page.locator("main").inner_text()
    assert "true" not in tekst and "false" not in tekst
    assert "· navn" not in tekst and "Hentet kl" not in tekst


def test_i_dag_kategorinavn_uten_understrek(leder_side) -> None:
    page, base = leder_side
    side = _norsk_side(page, "2026-11-16T09:05:00+01:00")
    side.goto(base, wait_until="networkidle")
    kort = side.get_by_role("region", name="I dag")
    kort.get_by_role("button", name=re.compile("^Vis radene: Åpne driftsmeldinger")).click()
    kort.locator("table tbody tr").first.wait_for()
    tabell = kort.locator("table").inner_text()
    assert "Klima og samling" in tabell and "klima_og_samling" not in tabell
    side.close()


# ---------- Etappe 3a (2026-11-16): «Mine frister» og «Fulgt opp» ----------

def test_meny_har_mine_frister_under_folg_opp(leder_side) -> None:
    page, base = leder_side
    page.goto(base, wait_until="networkidle")
    nav = page.get_by_role("navigation", name="Innhold")
    assert nav.get_by_text("Følg opp", exact=True).is_visible()
    nav.get_by_role("button", name=re.compile("^Mine frister")).click()
    page.get_by_role("heading", name="Mine frister", exact=True).wait_for()
    assert "Mine frister" in page.get_by_role("navigation", name="Du er her").inner_text()


def test_forfalte_innlan_og_fulgt_opp_huskes(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "frister"), wait_until="networkidle")
    forfalt = page.get_by_role("region", name=re.compile("^Forfalt"))
    forfalt.get_by_text("Retur av innlån", exact=False).first.wait_for()
    for_antall = forfalt.locator("li").count()
    forfalt.get_by_role("button", name=re.compile("^Fulgt opp: Retur av innlån")).first.click()
    fulgt = page.get_by_role("region", name=re.compile("^Fulgt opp"))
    fulgt.get_by_text("Retur av innlån", exact=False).first.wait_for()
    assert page.get_by_role("region", name=re.compile("^Forfalt")).locator("li").count() == for_antall - 1
    page.reload(wait_until="networkidle")  # lagret i nettleseren
    page.get_by_role("region", name=re.compile("^Fulgt opp")).get_by_text("Retur av innlån", exact=False).first.wait_for()
    page.get_by_role("region", name=re.compile("^Fulgt opp")).get_by_role("button", name=re.compile("^Angre")).first.click()
    page.wait_for_function("!document.body.innerText.includes('Angre')")


def test_hjem_viser_mine_frister_med_lenke(leder_side) -> None:
    page, base = leder_side
    page.goto(base, wait_until="networkidle")
    kort = page.get_by_role("region", name="Mine frister")
    kort.get_by_text("Forfalt", exact=False).first.wait_for()
    kort.get_by_role("link", name="Se alle frister").click()
    page.get_by_role("heading", name="Mine frister", exact=True).wait_for()


def test_frist_kan_tas_med_til_ki(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "frister"), wait_until="networkidle")
    rad = page.locator("li", has_text="Retur av innlån").first
    rad.get_by_text("Mer", exact=True).click()  # 3b: Spør KI ligger under «Mer»
    rad.get_by_role("button", name=re.compile("^Spør KI: Retur av innlån")).click()
    _chat_aapen(page)
    assert "Retur av innlån" in page.locator("#chat-felt").input_value()


def test_i_dag_paa_mobil_uten_sidelengs_rulling(leder_side) -> None:
    page, base = leder_side
    side = _norsk_side(page, "2026-11-16T09:05:00+01:00")
    side.set_viewport_size({"width": 390, "height": 844})
    side.goto(base, wait_until="networkidle")
    kort = side.get_by_role("region", name="I dag")
    kort.get_by_role("button", name=re.compile("^Vis radene: Åpne driftsmeldinger")).click()
    kort.locator("table tbody tr").first.wait_for()
    assert side.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    side.close()

# ---------- Etappe 3b (2026-11-17): handlinger, «Godta» og «Mine oppfølginger». Én synlig handling, resten under «Mer». ----------

def _mer(omraade):
    """Åpner «Mer» i handlingslinjen (resten av handlingene ligger der, så radene ikke blir fulle av knapper)."""
    omraade.get_by_text("Mer", exact=True).first.click()


def test_fristrad_har_epostutkast_og_meld_avvik_under_mer(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "frister"), wait_until="networkidle")
    rad = page.get_by_role("region", name=re.compile("^Forfalt")).locator("li", has_text="Retur av innlån").first
    rad.wait_for()
    assert not rad.get_by_role("link", name=re.compile("^E-postutkast")).is_visible()  # skjult til «Mer» åpnes
    _mer(rad)
    from urllib.parse import unquote
    href = rad.get_by_role("link", name=re.compile("^E-postutkast")).get_attribute("href")
    assert href.startswith("mailto:?subject=") and "Retur av innlån" in unquote(href)
    rad.get_by_role("button", name=re.compile("^Meld avvik")).click()
    rad.get_by_role("status").get_by_text("Lagt i Mine oppfølginger", exact=False).wait_for()
    page.goto(_adr(base, "oppfolging"), wait_until="networkidle")
    aapne = page.get_by_role("region", name=re.compile("^Åpne"))
    aapne.get_by_text("Avvik: Retur av innlån", exact=False).first.wait_for()


def test_rapport_har_godta_i_stedet_for_avkrysninger(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan?dato=2026-11-14"), wait_until="networkidle")
    godta = page.get_by_role("button", name="Godta", exact=True)
    godta.wait_for()
    assert page.locator("main input[type=checkbox]").count() == 0
    assert page.locator("main .af-badge").first.inner_text() == "Utkast"
    godta.click()
    page.wait_for_function("document.querySelector('main .af-badge').textContent === 'Bekreftet'")
    page.reload(wait_until="networkidle")  # godkjenningen huskes for denne rapporten og disse valgene
    page.wait_for_function("document.querySelector('main .af-badge') && document.querySelector('main .af-badge').textContent === 'Bekreftet'")
    page.get_by_role("button", name="Angre godkjenning").click()
    page.wait_for_function("document.querySelector('main .af-badge').textContent === 'Utkast'")


def test_folg_opp_fra_rapport_lukk_og_last_ned(leder_side) -> None:
    page, base = leder_side
    page.goto(_adr(base, "rolle:HR og bemanning/vaktplan?dato=2026-11-14"), wait_until="networkidle")
    page.get_by_role("button", name="Følg opp", exact=True).click()
    page.get_by_role("status").get_by_text("Lagt i Mine oppfølginger", exact=False).first.wait_for()
    # Huskelappen til høyre viser de nyeste åpne oppfølgingene.
    assert "Vaktplan for en dag" in page.get_by_role("complementary", name="Fasit").inner_text()
    nav = page.get_by_role("navigation", name="Innhold")
    nav.get_by_role("button", name=re.compile("^Mine oppfølginger")).click()
    aapne = page.get_by_role("region", name=re.compile("^Åpne"))
    rad = aapne.locator("li", has_text="Vaktplan for en dag").first
    assert rad.get_by_role("link", name="Åpne kilden").get_attribute("href").startswith("#rolle")
    with page.expect_download() as nedlasting:
        page.get_by_role("button", name="Last ned (.csv)").click()
    innhold = open(nedlasting.value.path(), encoding="utf-8-sig").read()
    assert "Vaktplan for en dag" in innhold and innhold.startswith('"Tittel"')
    rad.get_by_role("button", name=re.compile("^Lukk")).click()
    page.get_by_role("region", name=re.compile("^Lukket")).get_by_text("Vaktplan for en dag", exact=False).first.wait_for(state="attached")


def test_ki_svar_kan_folges_opp(leder_side) -> None:
    page, base = leder_side
    page.route("**/api/chat", lambda route: route.fulfill(json={"tekst": "Tre åpne HMS-avvik.", "verktoykall": [], "data_hentet": []}))
    page.goto(_adr(base, "flate:chat"), wait_until="networkidle")
    page.locator("#chat-felt").fill("Hvor mange HMS-avvik er åpne?")
    page.get_by_role("button", name="Send", exact=True).click()
    page.get_by_text("Tre åpne HMS-avvik.").wait_for()
    page.get_by_role("button", name="Følg opp", exact=True).click()
    page.goto(_adr(base, "oppfolging"), wait_until="networkidle")
    page.get_by_role("region", name=re.compile("^Åpne")).get_by_text("Hvor mange HMS-avvik er åpne?", exact=False).wait_for()


def test_oppfolging_med_farlig_tittel_vises_som_tekst(leder_side) -> None:
    page, base = leder_side
    farlig = "<img src=x onerror=window.__x=1>"
    page.goto(base, wait_until="networkidle")
    page.evaluate("""f => localStorage.setItem('kunstpixel.oppfolginger.v1', JSON.stringify([
        {id: 'a', tittel: f, type: 'avvik', adresse: 'javascript:alert(1)', kilde: f, opprettet: 't', lukket: null}]))""", farlig)
    page.goto(_adr(base, "oppfolging"), wait_until="networkidle")
    aapne = page.get_by_role("region", name=re.compile("^Åpne"))
    aapne.get_by_text(farlig, exact=False).first.wait_for()
    assert page.locator("main img").count() == 0 and page.evaluate("window.__x") is None
    assert aapne.get_by_role("link", name="Åpne kilden").get_attribute("href").startswith("#")
