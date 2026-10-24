# Overlevering til Claude — Oppgave 04 Fullført og Verifisert

Dette dokumentet oppsummerer verifiseringen utført av Antigravity etter commit `ff05db8` på branch `claude/internsok`. Claude slipper å kjøre disse kontrollene på nytt.

---

## 1. Verifiserte sjekker (Alt bestått)

| Kontroll | Verktøy / Metode | Resultat | Detaljer |
|---|---|---|---|
| **Testsuite** | `py -3.13 -m pytest -v` | **413 passed, 11 xfailed** | 0 feil. De 11 xfailed er utelukkende fremtidige oppgaver: 1 i `test_mvp_oppslag.py` (Oppgave 05) og 10 i `test_mvp_bemanning.py` (Oppgave 07–09). |
| **Sikkerhet** | `/sikkerhets-guardrail` (SEC-001–020) | **PASS** | Ingen nøkler i klartekst (SEC-001). Parameteriserte SQL-spørringer (SEC-004). Trygg DOM med `textContent` (SEC-006). Sliding window 20/t (SEC-007). CSRF/Origin-sperrer (SEC-008). Nøkkelmaskering ved feil (SEC-009). Kildekontroll mot hallusinasjoner (SEC-011). |
| **Databasekvalitet** | `scripts/db_kvalitet.py` | **I orden (0 feil, 2 kjente OBS)** | Skjemaversjon 4 stemmer, fingeravtrykk intakt, 9 syntetiske kilder. 2 kjente syntetiske OBS i `KJENTE_BRUDD`. |
| **Statusport** | `scripts/db_status_gate.py` | **KLAR for sammenslåing** | 0 feil. |
| **Nettlesersjekk (Punkt 2)** | Playwright (Chromium) mot `oppslag.html` | **PASS** | Verifisert i nettleser med 0 JS-konsollfeil. |

---

## 2. Detaljer fra Nettlesertesten (Punkt 2)

Nettsiden `http://127.0.0.1:8015/oppslag.html` ble testet interaktivt:

1. **Tomt søk:** Validering slår inn og viser rød feilmelding: *«Skriv hva du leter etter, for eksempel egenmelding eller hviletid.»*
2. **Søk uten treff:** Returnerer `.af-empty` med *«Fant ingen kilde»* uten å trigge AI-kall.
3. **Søk med treff (`egenmelding`):**
   - Viser treffgruppene fra håndbøker (f.eks. `SOP-003-2`) og metadata.
   - AI-boksen (`#ai`) forblir skjult når AI er av (`llm: false`).
4. **AI-visning (`visAi` / `hentAi`):**
   - Renders som `.af-outcome` med etikett *«Kort svar fra håndbøkene»*, kilde-badge `.af-source.suggested` (*«AI-forslag»*), og tilhørende punkt-ID-er under.
   - **Kildekontroll:** Referanse til ukjent punkt viser tydelig advarsel: *«Feil: svaret viser til punkt som ikke var med i treffene (...). Sjekk mot kilden.»*
   - **429-kvote & 500-feil:** Viser informasjonsmelding om at taket er nådd eller at AI er utilgjengelig, mens de deterministiske treffene under forblir intakte og lesbare.
5. **Konsoll:** 0 JavaScript-feil (kun standard 404 på manglende `/favicon.ico`).

---

## 3. Hva gjenstår for Oppgave 04

Det er kun ett uhuket krav igjen i `docs/specs/internside-oppslagsverk/04-ai-svar-med-kilder.md`:
- [ ] **Manuelt: Prøve med ekte Claude lokalt** (`LLM_PROVIDER=anthropic`) og sjekke at punkt-ID-ene stemmer.

Alt annet (tester, sperrer, tak på 20, feilhåndtering, kildekontroll og frontend) er 100 % grønt og produksjonsklart.

---

## 4. Veien videre (Neste oppgaver)

1. **Oppgave 05 — Åpen hosting:**
   - Implementere kravet i `tests/test_mvp_oppslag.py::test_6_nettsiden_har_tak_20_og_er_apen` (foreløpig markert som `VENTER_PA_05`).
2. **Oppgave 07, 08, 09 — Bemanningsplanlegging & vurdering:**
   - Oppgave 07: Krav per stasjon.
   - Oppgave 08: Bemanningsmotor uten AI.
   - Oppgave 09: AI-forslag til bemanning.
