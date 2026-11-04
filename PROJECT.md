# Project: Aura Museum Bygningsmodell, Sonebeskrivelser & Kartpakke

## Architecture
- **SSOT (Single Source of Truth)**: `06_kart/bygning_geometri.json` inneholder autoritativ bygningsgeometri, rominndeling, soner, veggtykkelser, materialer og standardiserte metadata.
- **Kartkompilator**: `06_kart/build_map.py` er en deterministisk kompilator (Python 3.13) som genererer:
  - 2D-plantegninger etter NS 8351: `06_kart/plantegning_u1.svg`, `plantegning_p1.svg`, `plantegning_p2.svg`.
  - Interaktiv 2.5D kartviser: `06_kart/index.html` med 30° isometrisk Canvas, lagvelgere for etasjer og soner, og dynamisk informasjonsdrawer.
- **Konsumerende systemer i repoet**:
  - `src/kunstpixel/core/db.py` (`query_building_map_data()`)
  - `src/mcp_server.py` (FastMCP-verktøy `get_building_map_data()`)
  - `tests/test_building_map.py` (automatisert testpakke)
- **Geodata & Matrikkel (Kartverket MCP verifisert)**:
  - Adresse: Bispegata 9B, 7012 Trondheim (Knr: 5001)
  - Eiendom: Gnr 401 / Bnr 12 (Teig lokalid 279106015)
  - Koordinater: WGS84 lat 63.4273687, lon 10.3914082
  - Terrengkote: 13.27 moh (DTM1 laser)
  - Kote P1 FG (±0.000): +13.50 moh (+230 mm over terreng)
  - Kote U1 FG (-4.200 m): +9.30 moh
  - Kote P2 FG (+6.300 m): +19.80 moh
  - Kote Gesims (+11.400 m): +24.90 moh
- **Arealberegning etter NS 3940**:
  - BTA: 4 350 m² (U1: 1 450 m², P1: 1 450 m², P2: 1 450 m²)
  - BRA: 3 920 m² (U1: 1 300 m², P1: 1 310 m², P2: 1 310 m²)
  - BYA: 1 450 m² (Tomteareal: 3 200 m², %-BYA: 45.3 %)
- **Brannkonsept (DiBK / TEK17)**:
  - Brannklasse: BKL 3, Risikoklasse: RKL 5
  - Bæresystem: R 90, etasjeskiller REI 90 / REI 120, brannceller EI 60
  - Slokkesystem: Pre-action våtsprinkler i publikums-/fellesarealer (S1, S2, S3), Inergen inertgasslukkeanlegg i Magasin 1 (`MAG-1`), Kunstmottak (`VER-1`) og Teknisk rom (`TEK-1`).
- **Tegningsstandarder etter NS 8351**:
  - Doble vegger med skravur (hatching): 400 mm tegl/isolasjon i eldre fløy (1912), 300 mm betong/glass i tilbygg (2016), og 200 mm innvendige bærevegger.
  - Målekjeder med 45° arkitekt-ticks og millimeterangivelser.
  - Norske romstempler: `[romnr romnavn | BRA ...m² | H: ...m | Gulv: ... | Brann: ... | Sone: ...]`.
  - Fullverdig tegningshode med arealoppstilling, brannkonsept og matrikkeldata.
- **Visuelt samsvar mot 9 motiver i `06_kart/bilder/`**:
  - Hovedfløy (1912): Nyklassisistisk rød tegl, Iddefjord-granittsokkel, kobber-mansardtak, siktlinje mot Nidarosdomen i vest, inngang mot Bispegata i nord.
  - Tilbygg Øst (2016): Skandinavisk glass og lys betong, trelameller, utkraget P2-balkong, kafé langs Nidelvas kai i øst mot historiske trebrygger.
  - Sentralatrium & Skulpturhage: Dagslysoverlys, vindeltrapp, gangbro, skulpturhage mot Marinen i sør med rektangulært vannspeil.
  - Interiører: Vestibyle med speedgates, Bokhandel, Kafé, Sal A (mytologi, mørk koksgrå, fiskebensparkett), Sal D (Munch, karmosinrød, K1-montre), Magasin 1 (hvelvdør, uttrekkbare nettingracks, 18°C/50% RH, Inergen-rør).

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Kartverket MCP-integrasjon | Innarbeide autoritativ matrikkel (Bispegata 9B, Gnr 401 / Bnr 12, Knr 5001) og terrengkote (+13.27 moh DTM1, FG P1 +13.50 moh) i SSOT. | M1 | survey (spec_miner) |
| 2 | NS 3940 Arealmodell | Fullverdig arealoppstilling: BTA 4 350 m², BRA 3 920 m², BYA 1 450 m² med etasjefordeling for U1, P1, P2 i JSON. | M1 | survey (spec_miner, codebase) |
| 3 | DiBK Brannkonsept | Brannklasse BKL 3, Risikoklasse RKL 5, bæreevne R 90, seksjonering EI 60, sprinkler i S1/S2/S3 og Inergen i S4/Magasin. | M1 | survey (spec_miner) |
| 4 | Berikede Romstempeldata | Utvide alle 19 rom i `bygning_geometri.json` med `romnummer`, `materialer` (gulv, vegg, himling) og `brannklasse` (EI-60 / EI-30). | M1 | survey (codebase, images) |
| 5 | Veggdefinisjoner i SSOT | Legge inn spesifikke veggtykkelser (400 mm eldre fløy, 300 mm tilbygg, 200 mm innervegger) og hatch-typer i geometri-JSON. | M1 | survey (spec_miner, images) |
| 6 | SVG Doble Vegger med Skravur | Implementere SVG `<pattern>` (tegl, betong, innervegg) og doble vegger i `generate_blueprint_svg()` i `build_map.py`. | M2 | survey (spec_miner, codebase) |
| 7 | SVG Målekjeder & Arkitekt-ticks | Implementere 3-trinns målekjeder med 45° arkitekt-ticks og millimeterangivelser i SVG-plantegningene. | M2 | survey (spec_miner, codebase) |
| 8 | SVG Kotehøyder | Tegne standard kotesymboler og koteangivelser for U1 (+9.30 moh), P1 (+13.50 moh) og P2 (+19.80 moh). | M2 | survey (spec_miner) |
| 9 | NS 8351 Romstempler i SVG | Tegne profesjonelle 3-linjers romstempler med ramme for samtlige 19 rom i plantegningene. | M2 | survey (spec_miner, codebase) |
| 10 | Fullverdig Tegningshode i SVG | Standardisert tegningshode med matrikkel, koter, NS 3940 arealtabell, brannkonsept, målestokk 1:100 og tegningsnr. | M2 | survey (spec_miner, codebase) |
| 11 | Interaktiv 2.5D Kartviser oppdatering | Oppdatere `generate_html()` i `build_map.py` og `index.html` til å vise berikede romdata (materialer, brannklasse, NS 3940 arealer) i drawer. | M3 | survey (codebase) |
| 12 | 100% Visuell overensstemmelse | Sikre at geometri, soner og romfunksjoner gjenspeiler de 9 motivene fra `06_kart/bilder/` i både 2D og 2.5D. | M3 | survey (images) |
| 13 | Opaque-Box E2E Testsuite | Utvide `tests/test_building_map.py` med tester for alle 4 tiers: NS 8351 tegningskrav, NS 3940 arealer, Kartverket geodata og deterministisk bygg. | M-E2E / M4 | survey (codebase) |
| 14 | Deterministisk Validering & Bygg-gate | Kjøre `deterministisk-validator` og `validated-builder` for å sikre feilfri oppfyllelse før sluttgodkjenning. | M4 | ORIGINAL_REQUEST |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M-E2E | E2E Test Suite Creation | Opprette omfattende testinfrastruktur og tester for alle akseptansekriterier i `tests/test_building_map.py` og publisere `TEST_READY.md`. | Survey | DONE |
| M1 | Geometri & SSOT Datamodell | Oppdatere `06_kart/bygning_geometri.json` med matrikkel, koter, arealer (NS 3940), brannkonsept (DiBK), veggtykkelser og berikede romstempeldata. | Survey | DONE |
| M2 | SVG Blueprint Kompilator | Oppdatere `06_kart/build_map.py` med doble vegger, hatching, målekjeder, arkitekt-ticks, koter, NS 8351 romstempler og tegningshode. Generere `plantegning_u1.svg`, `plantegning_p1.svg`, `plantegning_p2.svg`. | M1 | IN_PROGRESS |
| M3 | Interaktiv 2.5D Kartviser | Oppdatere `generate_html()` i `06_kart/build_map.py` og generere `06_kart/index.html` med full visning av ny geometri, soner og romdrawer. | M2 | PLANNED |
| M4 | Sluttverifisering & Kvalitetssikring | Kjøre hele E2E-testpakken (`tests/test_building_map.py`), kjøre `deterministisk-validator` og `validated-builder`, gjennomføre adversarial hardening og audit. | M3, M-E2E | PLANNED |

---

## Interface Contracts

### 06_kart/bygning_geometri.json ↔ 06_kart/build_map.py
- **Arealer**: `museum.arealer_ns3940`: `{ "bta_m2": 4350, "bra_m2": 3920, "bya_m2": 1450, "etasjefordeling_bra": { "U1": 1300, "P1": 1310, "P2": 1310 } }`
- **Brannkonsept**: `museum.brannkonsept`: `{ "brannklasse": "BKL 3", "risikoklasse": "RKL 5", "slokking": "Automatisk sprinkleranlegg (pre-action i saler) og Inergen gasslukking (S4 Magasin 1, VER-1, TEK-1)", "baeresystem": "R 90", "etasjeskiller": "REI 90 / REI 120", "seksjonering": "EI 60" }`
- **Matrikkel & Koter**: `museum.matrikkel`: `{ "kommune": "Trondheim (5001)", "gnr": 401, "bnr": 12, "adresse": "Bispegata 9B, 7012 Trondheim", "kote_terreng_moh": 13.27, "kote_p1_fg_moh": 13.50, "kote_u1_fg_moh": 9.30, "kote_p2_fg_moh": 19.80, "kote_gesims_moh": 24.90 }`
- **Romobjekter** i `etasjer[].rom[]`:
  - Skal inneholde: `id`, `romnummer` (f.eks. "101"), `navn`, `areal_m2`, `takhoyde_m`, `sikkerhetssone`, `klimasone`, `materialer: { "gulv": str, "vegg": str, "himling": str }`, `brannklasse`: str, `x`: int, `y`: int, `w`: int, `h`: int.
- **Bakoverkompatibilitet**:
  - `src/kunstpixel/core/db.py` `query_building_map_data()` krever at rotfeltene `museum`, `datakilde`, `soner_definisjon` og `etasjer` forblir tilstede og velformede.

---

## Code Layout
- `06_kart/bygning_geometri.json`: SSOT for arkitektonisk geometri, rom og soner.
- `06_kart/build_map.py`: Kompilatorskript (Python 3.13) som produserer SVG-er og `index.html`.
- `06_kart/plantegning_u1.svg`: NS 8351 2D arbeidstegning for underetasje.
- `06_kart/plantegning_p1.svg`: NS 8351 2D arbeidstegning for 1. etasje.
- `06_kart/plantegning_p2.svg`: NS 8351 2D arbeidstegning for 2. etasje.
- `06_kart/index.html`: 2.5D interaktiv kartviser.
- `tests/test_building_map.py`: Pytest-testsuite for kartpakken.
- `tests/test_building_map_e2e.py` (valgfritt/tillegg) eller utvidelse i `tests/test_building_map.py`.
