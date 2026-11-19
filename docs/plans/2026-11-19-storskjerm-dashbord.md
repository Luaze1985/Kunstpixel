# Storskjerm-dashbord Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (Lars: inline som standard) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Én side i claude.ai som viser dagen på Kunstpixel på storskjerm, med samme tall som Datafinner og en kilde ved hvert tall.

**Architecture:** En ren lesefunksjon i `core/storskjerm.py` setter sammen tallene fra Datafinners eksisterende funksjoner (`get_today_overview`, `get_week_overview`, `get_my_deadlines`) pluss tre nye spørringer. Et skript skriver `data.json` og en ferdig `storskjerm.html` (med `af.css` lagt inn) til `.scratch/claude-app/`. Claude Code publiserer de to filene som én artifact med fast lenke.

**Tech Stack:** Python 3.13, SQLite (mode=ro), vanilla HTML/CSS/JS med inline SVG, pytest og Playwright.

**Spec:** `docs/specs/2026-11-19-storskjerm-dashbord.md`

## Global Constraints

- Bare lesing av `museum.db`. Ingen skriving, ingen knapper som endrer noe.
- Status som ord: `Normal`, `Følg med`, `Over terskel`, `Ukjent`. Flater uten terskelregel viser sammenligning uten statusord.
- Hvert tall har `kilde` (tabellnavn), og siden viser `Kilde: <tabell>` under det.
- Ingen navn, fraværsårsak eller e-postutkast i `data.json`. Frister: type, ref (ID), frist og gruppe.
- Innlånsfrister skjules (DECISIONS U6).
- Arbeidsflyt: én blå for handling, status i ord, ingen emoji, ingen ikoner, Inter. Storskjerm: minst 20 px tekst ved 1920×1080.
- Ingen nye mapper. Mal i `deploy/claude-app/`, bygg i `.scratch/claude-app/`.
- CSP i artifacts: ingen eksterne stilark utenom Google Fonts. `af.css` legges inn i siden av skriptet.

## Review Focus

1. **Mandag morgen:** uka har ingen hele dager. `get_week_overview` viser da forrige uke. Siden må si «forrige uke», ikke vise tom flate. Test i Task 1.
2. **Stengt i går:** besøk gjelder siste hele åpne dag. Siden må vise datoen tallet gjelder, ikke «i går». Test i Task 1.
3. **Kilde som slutter før i dag** (tilfredshet til 2026-10-29) må bli `Ukjent` og stå i «Dette vet vi ikke», aldri 0. Test i Task 1.
4. **Ingen frister i en gruppe:** siden viser «Ingen» og ikke en tom boks. Test i Task 3.
5. **Datafilen mangler eller er ødelagt:** siden viser én feilmelding som sier hva som mangler, ikke en hvit side. Test i Task 3.

---

### Task 1: Tallene (`core/storskjerm.py`)

**Files:**
- Create: `src/kunstpixel/core/storskjerm.py`
- Test: `tests/test_storskjerm.py`

**Interfaces:**
- Consumes: `driftsoversikt.get_today_overview(dato)`, `driftsoversikt.get_week_overview(dato)`, `frister.get_my_deadlines(rolle, dato)`, `db.get_db_connection()`.
- Produces: `lag_storskjerm(dato: str) -> dict` med nøklene `dato`, `ukedag`, `hentet_kl`, `oppmerksomhet` (int), `flater` (liste med 4 dict: `id`, `navn`, `verdi`, `enhet`, `normalt`, `sammenligning` (tekst), `status` (str eller None), `gjelder` (dato), `kilde`), `besok_uker` (liste med `uke`, `fra`, `i_aar`, `i_fjor`), `frister` (`antall` per gruppe og `rader` med `type`, `ref`, `tittel`, `frist_dato`, `gruppe`), `utstillinger` (liste med `utstilling_id`, `tittel`, `sesong`, `netto_resultat_nok`), `hull` (liste med `tekst`, `kilde`).

Flatene, i denne rekkefølgen: `besok` (siste hele åpne dag mot normalt for ukedagen, status fra `vurder`), `besok_uke` (uka mot forrige uke, status fra `vurder`), `saker` (åpne driftsmeldinger siste 30 dager pluss HMS-avvik siste 7 dager, sammenligning «eldre åpne: N», status None), `tilfredshet` (uka, `Ukjent` når kilden ikke dekker). `oppmerksomhet` = flater med `Følg med` eller `Over terskel` + frister i `Forfalt`.

- [ ] **Step 1: Write the failing tests** (lås `_idag` i `driftsoversikt` og `frister` til `date(2026, 11, 19)` med monkeypatch, slik eksisterende tester gjør)

```python
def test_fire_flater_med_kilde(idag): d = lag_storskjerm("2026-11-19"); assert [f["id"] for f in d["flater"]] == ["besok", "besok_uke", "saker", "tilfredshet"]; assert all(f["kilde"] for f in d["flater"])
def test_besok_er_lik_datafinner(idag): assert flate("besok")["verdi"] == get_today_overview("2026-11-19")["besok"]["verdi"]
def test_besok_sier_hvilken_dag(idag): assert flate("besok")["gjelder"] == get_today_overview("2026-11-19")["besok"]["dato"]
def test_tilfredshet_er_ukjent_naar_kilden_slutter(idag): assert flate("tilfredshet")["status"] == "Ukjent" and flate("tilfredshet")["verdi"] is None
def test_mandag_viser_forrige_uke(idag_mandag): assert "forrige uke" in flate("besok_uke")["navn"].lower()
def test_ingen_navn_i_data(idag): tekst = json.dumps(lag_storskjerm("2026-11-19"), ensure_ascii=False); assert not any(n in tekst for n in alle_ansattnavn())
def test_ingen_innlan_eller_epost(idag): d = lag_storskjerm("2026-11-19"); assert all(r["type"] != "innlan" and "epost" not in r for r in d["frister"]["rader"])
def test_besok_uker_er_8_og_lik_sql(idag): u = lag_storskjerm("2026-11-19")["besok_uker"]; assert len(u) == 8; assert u[-1]["i_aar"] == sql_sum_dagsbesok(u[-1]["fra"], min(søndag, "2026-11-18"))
def test_utstillinger_i_aar(idag): u = {x["utstilling_id"]: x for x in lag_storskjerm("2026-11-19")["utstillinger"]}; assert u["KP-EXH-2026-FOKUS-2"]["netto_resultat_nok"] == 657556 and len(u) == 6
def test_hull_finner_tilfredshet_og_utstillingstabeller(idag): t = " ".join(h["tekst"] for h in lag_storskjerm("2026-11-19")["hull"]); assert "2026-10-29" in t and "utstillinger" in t
def test_oppmerksomhet_teller_status_og_forfalt(idag): d = lag_storskjerm("2026-11-19"); assert d["oppmerksomhet"] == sum(f["status"] in ("Følg med", "Over terskel") for f in d["flater"]) + d["frister"]["antall"]["Forfalt"]
def test_fremtidig_dato_avvises(idag): with pytest.raises(ValueError): lag_storskjerm("2026-11-20")
```

- [ ] **Step 2: Run** `py -3.13 -m pytest tests/test_storskjerm.py -q`. Expected: FAIL (`ModuleNotFoundError: storskjerm`).
- [ ] **Step 3: Implement `lag_storskjerm(dato: str) -> dict`.** `besok_uker`: ISO-uker, siste 8 uker til og med i går, `i_fjor` = samme ISO-uke året før (None for uke 53). `utstillinger`: `utstillinger_historikk JOIN utstilling_okonomi USING (utstilling_id) WHERE aar = år(dato)`, sortert på `netto_resultat_nok` synkende. `hull`: tidsserier i `TIDSSERIER` (samme liste som `scripts/lag_claude_skill.py`, flytt den hit og importer den der) med `max(dato) < i går`, og uenighet når titlene i `utstillinger WHERE status='aktiv'` ikke finnes blant `utstillinger_historikk` som dekker dagen.
- [ ] **Step 4: Run** `py -3.13 -m pytest tests/test_storskjerm.py tests/test_claude_skill.py -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(storskjerm): tall for storskjerm-dashbordet (D1–D8)`

### Task 2: Byggeskript (`scripts/lag_storskjerm.py`)

**Files:**
- Create: `scripts/lag_storskjerm.py`
- Create: `deploy/claude-app/storskjerm.html` (mal, med plassholderen `/*AF_CSS*/` i `<style>`)
- Test: `tests/test_storskjerm.py` (tillegg)

**Interfaces:**
- Consumes: `lag_storskjerm(dato)` fra Task 1.
- Produces: `bygg(ut: Path, dato: str | None = None) -> tuple[Path, Path]` som skriver `ut/storskjerm.html` og `ut/data.json`. CLI: `py -3.13 scripts/lag_storskjerm.py [--ut MAPPE]`, standard `.scratch/claude-app/`.

- [ ] **Step 1: Write the failing tests**

```python
def test_bygg_skriver_side_og_data(tmp_path, idag): side, data = bygg(tmp_path, "2026-11-19"); assert json.loads(data.read_text("utf-8"))["dato"] == "2026-11-19"
def test_af_css_er_lagt_inn(tmp_path, idag): side, _ = bygg(tmp_path, "2026-11-19"); t = side.read_text("utf-8"); assert "/*AF_CSS*/" not in t and "--blue" in t
def test_siden_henter_ingen_eksterne_filer(tmp_path, idag): t = bygg(tmp_path, "2026-11-19")[0].read_text("utf-8"); assert not re.search(r'(src|href)="https?://(?!fonts\.googleapis\.com)', t)
```

- [ ] **Step 2: Run** og se FAIL.
- [ ] **Step 3: Implement `bygg`** (les malen, erstatt `/*AF_CSS*/` med innholdet i `src/kunstpixel/adapters/datafinner/af.css`, skriv JSON med `ensure_ascii=False, indent=1`).
- [ ] **Step 4: Run** og se PASS.
- [ ] **Step 5: Commit** `feat(storskjerm): byggeskript og sidemal`

### Task 3: Siden (`deploy/claude-app/storskjerm.html`)

**Files:**
- Modify: `deploy/claude-app/storskjerm.html`
- Test: `tests/test_storskjerm_side.py` (Playwright, server fra `ThreadingHTTPServer` med `SimpleHTTPRequestHandler` på byggemappa, slik `leder_side` gjør)

**Interfaces:**
- Consumes: `data.json` fra Task 2 (`fetch("data.json")`).
- Produces: siden. Hver flate har `id="flate-<id>"`, hver kildelinje teksten `Kilde: <kilde>`.

Oppsett: toppstripe (Kunstpixel, ukedag og dato, «Tall per <dato> kl. <hentet_kl>», «N krever oppmerksomhet», knappen **Fullskjerm**), fire flater, så to rader med to felt: «Besøk siste 8 uker» (SVG-linje, i år `blue`, i fjor grå) og «Frister» (Forfalt, I dag, Denne uka med antall og inntil 4 rader), «Utstillingene i år» (SVG-stolper, sesong i navnet) og «Dette vet vi ikke». Tokens fra `af.css`, lys og mørk. Under 720 px: én kolonne.

- [ ] **Step 1: Write the failing tests**

```python
def test_siden_viser_fire_flater_med_kilde(side): for i in ["besok", "besok_uke", "saker", "tilfredshet"]: expect(side.locator(f"#flate-{i}")).to_contain_text("Kilde:")
def test_oppmerksomhet_i_toppen(side, data): expect(side.locator("header")).to_contain_text(f"{data['oppmerksomhet']} krever oppmerksomhet")
def test_ukjent_star_som_ord(side): expect(side.locator("#flate-tilfredshet")).to_contain_text("Ukjent")
def test_tom_fristgruppe_viser_ingen(side_uten_frister): expect(side_uten_frister.locator("#frister")).to_contain_text("Ingen")
def test_manglende_data_gir_feilmelding(side_uten_data): expect(side_uten_data.locator("main")).to_contain_text("Fant ikke tallene")
@pytest.mark.parametrize("bredde,hoyde", [(1920, 1080), (400, 800)])
def test_ingen_sidelengs_rulling(side, bredde, hoyde): side.set_viewport_size(...); assert side.evaluate("document.documentElement.scrollWidth <= innerWidth")
def test_ingen_konsollfeil(side, konsollfeil): assert konsollfeil == []
def test_brodtekst_minst_20px_paa_storskjerm(side): side.set_viewport_size({"width": 1920, "height": 1080}); assert minste_skrift(side, ".flate") >= 20
```

- [ ] **Step 2: Run** og se FAIL.
- [ ] **Step 3: Implement siden.** Tegn med `textContent`, aldri `innerHTML` med data. Fullskjerm via `document.documentElement.requestFullscreen()` i klikket, med `catch` (knappen skjules hvis API-et mangler).
- [ ] **Step 4: Run** `py -3.13 -m pytest tests/test_storskjerm.py tests/test_storskjerm_side.py -q` og se PASS.
- [ ] **Step 5: Se på siden én gang** i nettleserpanelet (1920×1080, lys og mørk) og ta skjermbilde.
- [ ] **Step 6: Commit** `feat(storskjerm): siden`

### Task 4: Publiser, fest og dokumenter

**Files:**
- Modify: `docs/GUIDE-claude-appen.md` (nytt avsnitt «Storskjerm»), `docs/DECISIONS.md` (D1–D8), `PLAN.md`

- [ ] **Step 1:** `py -3.13 scripts/lag_storskjerm.py`. Expected: `OK` og to filer i `.scratch/claude-app/`.
- [ ] **Step 2:** Publiser med Artifact-verktøyet: `file_path` = `.scratch/claude-app/storskjerm.html`, `files` = `{"data.json": ".scratch/claude-app/data.json"}`, `icon: "chart"`, `pin: true`. Skriv lenken inn i guiden.
- [ ] **Step 3:** Les siden tilbake (Artifact `read`) og sjekk at tallene i toppstripen er like `data.json`.
- [ ] **Step 4:** Guide: hvordan vise (Festet → Fullskjerm), hvordan oppdatere («oppdater dashbordet»: kjør skriptet og publiser til samme lenke), linjen Lars kan lime inn i prosjektet Kunstpixel med lenken.
- [ ] **Step 5:** DECISIONS D1–D8 (fra spec «Det som er bestemt»), PLAN «Gjort (2026-11-19)».
- [ ] **Step 6:** Full testpakke `py -3.13 -m pytest -q`. Si fra om kjente ustabile tester (`test_invalid_content_length_gets_400`, Playwright-fristtestene) hvis de feiler.
- [ ] **Step 7: Commit** `docs(storskjerm): guide, beslutninger og plan`
