# Test Suite Readiness Report: Aura Museum Bygningsmodell & Kartpakke

**Dato:** 2026-10-31  
**Forfatter:** E2E Test Writer (`test_writer_e2e`)  
**Status:** TEST READY (Milestone M-E2E Fullført)  
**Mål:** Omfattende 4-lags testinfrastruktur for Aura Museum bygningsmodell, plantegninger og kartpakke iht. NS 8351, NS 3940, DiBK brannkonsept og Kartverket MCP.  
**Testfil:** `tests/test_building_map.py`  

---

## 1. Executive Summary

Den helhetlige 4-lags E2E-testsuiten for Aura Museum bygningsmodell og kartpakke er etablert og aktiv i `tests/test_building_map.py`.

Testsuiten består av **42 automatiserte tester** (langt over terskelkravet på 35 tester i `TEST_INFRA.md`). Testsuiten opprettholder 100 % bakoverkompatibilitet med de 5 opprinnelige testene, og tester nådeløst alle akseptansekriterier fra `ORIGINAL_REQUEST.md`, `PROJECT.md` og `TEST_INFRA.md`.

---

## 2. Test Runner Kommando

```powershell
# Kjør hele testpakken for kart- og bygningsmodellen
py -3.13 -m pytest tests/test_building_map.py -v

# Kjør kun atomære tester (Tier 1)
py -3.13 -m pytest tests/test_building_map.py -k "tier1" -v

# Kjør grenseverditester (Tier 2)
py -3.13 -m pytest tests/test_building_map.py -k "tier2" -v

# Kjør kryssartefakt-tester (Tier 3)
py -3.13 -m pytest tests/test_building_map.py -k "tier3" -v

# Kjør scenario-tester (Tier 4)
py -3.13 -m pytest tests/test_building_map.py -k "tier4" -v
```

---

## 3. Dekningssammendrag per Tier (Test Inventory)

| Tier | Kategori | Antall tester | Nåværende status | Hovedverifikasjoner |
| :--- | :--- | :---: | :---: | :--- |
| **Baseline** | Bakoverkompatibilitet | 5 | **5 / 5 PASS** (100 %) | Geometri-JSON eksistens, 3 etasjer/kjernesaler, index.html 2.5D nøkkelord, query_building_map_data() verktøy, SVG eksistens. |
| **Tier 1** | Feature Coverage (Atomære krav) | 16 | **9 PASS / 7 Venter M2+M3** | Kartverket-matrikkel, NS 3940 arealer, DiBK brannkonsept, veggtykkelser, berikede romstempler, SVG skravurmønstre, doble vegger, målekjeder, arkitekt-ticks, kotehøyder, tegningshode, bildeintegritet (14 filer), kompilator. |
| **Tier 2** | Boundary & Corner Cases | 10 | **10 / 10 PASS** (100 %) | Sum BRA == 3920 m², romsum <= etasje-BRA, positiv flomterskel (0.23m > 0.20m), monoton koteutvikling (U1 < Terreng < P1 < P2 < Gesims), 19 unike rom-IDer/romnumre, etasjeprefikser (0xx, 1xx, 2xx), veggtykkelseshierarki (400 > 300 > 200), TEK17 takhøyde >= 2.4m, branncellekrav, K1 vs K2 vs K3 klimagrenser. |
| **Tier 3** | Cross-Feature Combinations | 6 | **3 PASS / 3 Venter M2** | SSOT til SVG rom-IDer og antall, romareal-konsistens, tegningshode-konsistens, etasjekote-konsistens, HTML-modellkonsistens, skravurmønster-bruk. |
| **Tier 4** | Real-World Application Scenarios | 5 | **5 / 5 PASS** (100 %) | **Scenario 1:** Trøndelag brann- og redningstjeneste (sprinkler + Inergen).<br>**Scenario 2:** Trondheim kommune byggesak & arealattest.<br>**Scenario 3:** Sikkerhetspatrulje & adgangskontroll (S1-S4).<br>**Scenario 4:** Nasjonal konserveringsrevisjon (K1 i MAG-1 og Sal D).<br>**Scenario 5:** Entreprenør arbeidstegning-gransking. |
| **TOTALT** | **Helhetlig E2E Testsuite** | **42** | **32 PASS / 10 Venter M2+M3** | **Terskelkrav: >= 35 tester (Oppfylt med 42 tester)** |

---

## 4. Feature Checklist & Akseptansekriterier

### R1. Profesjonelle arkitektoniske plantegninger (NS 8351 / NS 3940)
- [x] Doble vegger med skravur definert i SSOT (400 mm tegl, 300 mm betong, 200 mm innervegg).
- [ ] SVG `<pattern>` og skravurfyll i SVG-plantegninger *(Implementeres i M2 `build_map.py`)*.
- [ ] Målekjeder med 45° arkitekt-ticks og millimetertekster i SVG *(Implementeres i M2 `build_map.py`)*.
- [ ] Kotehøyder (U1: +9.30, P1: +13.50, P2: +19.80 moh) tegnet i SVG *(Implementeres i M2 `build_map.py`)*.
- [x] Romstempler med formelle romnumre (001–206), BRA, takhøyde, materialer og brannklasse i SSOT.
- [ ] Utvidet 3-linjers romstempel i SVG-plantegninger *(Implementeres i M2 `build_map.py`)*.
- [ ] Fullverdig tegningshode med matrikkel, arealtabell og brannkonsept i SVG *(Implementeres i M2 `build_map.py`)*.

### R2. Visuell overensstemmelse med referansebilder
- [x] Samtlige 14 bildefiler (9 unike motiver) i `06_kart/bilder/` er verifisert intakte og > 100 kB.
- [x] Rominndeling i SSOT samsvarer med fasader, atrium, saler og magasin i bildene.
- [x] Materialstandarder (fiskebens eik i Sal A, dyp rød og betong i Sal D, hvelv og rullehyller i MAG-1) er innarbeidet i SSOT.

### R3. Oppdatering av komplett kartpakke og SSOT
- [x] `06_kart/bygning_geometri.json` er Single Source of Truth for rom, soner, mål, fasader og etasjer.
- [ ] `06_kart/build_map.py` oppdatert med ny SVG-generator *(Fokus for Milestone M2)*.
- [ ] `06_kart/index.html` oppdatert med beriket slide-over drawer og metadatavisning *(Fokus for Milestone M3)*.

### R4. Integrasjon mot Kartverket MCP og planstandarder
- [x] Offisiell adresse Bispegata 9B, 7012 Trondheim (Knr 5001) verifisert.
- [x] Matrikkel Gnr 401 / Bnr 12 (Teig lokalid 279106015) verifisert.
- [x] DTM1 laser terrengkote 13.27 moh og ferdig gulv P1 13.50 moh verifisert.

---

## 5. Eskalering & Neste Steg for Byggeagenter

Testene som p.t. feiler representerer de eksakte oppgavene som skal løses av de neste agentene:
1. **Milestone M2 (SVG Kompilator - `06_kart/build_map.py`):**
   - Implementere `<pattern id="hatch-tegl-400">`, `hatch-betong-300`, `hatch-baerevegg-200`.
   - Generere doble vegger med `fill="url(#hatch-...)"`.
   - Generere målekjeder med 45° arkitekt-ticks og millimetertekster.
   - Generere kotesymboler og koteangivelser for U1, P1 og P2.
   - Generere fullverdig tegningshode med BTA 4 350, BRA 3 920, BYA 1 450, BKL 3, RKL 5, Bispegata 9B og Gnr 401 / Bnr 12.
2. **Milestone M3 (Interaktiv Viser - `06_kart/index.html`):**
   - Oppdatere slide-over drawer i `generate_html()` slik at brannklasse, gulvmaterialer og arealer vises ved romklikk.
3. **Milestone M4 (Sluttverifisering):**
   - Kjøre `py -3.13 -m pytest tests/test_building_map.py -v` til 100 % passering (42 / 42 PASS).
