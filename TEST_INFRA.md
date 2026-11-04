# E2E Test Infra: Aura Museum Bygningsmodell & Kartpakke

## Test Philosophy
- **Opaque-box, requirement-driven**: Testene verifiserer at de produserte artefaktene (`bygning_geometri.json`, `plantegning_u1.svg`, `plantegning_p1.svg`, `plantegning_p2.svg`, `index.html`) oppfyller alle krav i NS 8351, NS 3940, DiBK brannkonsept og Kartverket MCP uavhengig av intern implementering.
- **Kvalitetsmetodikk**: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Testing + Real-World Workload Testing.

## Feature Inventory Coverage Matrix
| # | Feature | Requirement | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Cross-feature) | Tier 4 (Scenario) |
|---|---------|-------------|:-----------------:|:-----------------:|:---------------------:|:-----------------:|
| 1 | Kartverket MCP Geodata | R4 / ORIGINAL_REQUEST | matrikkel, adresse, koordinater, koter | kote_terreng vs kote_fg_p1 (positiv terskel > 0.2m) | matrikkel i tegningshode vs JSON SSOT | Byggesakskontroll / Eiendomsoppslag |
| 2 | NS 3940 Arealmodell | R1 / ORIGINAL_REQUEST | BTA (4350), BRA (3920), BYA (1450) | sum(etasjer BRA) == 3920, BYA <= BTA | arealoppstilling i tegningshode vs JSON SSOT | Arealattest til Trondheim kommune |
| 3 | DiBK Brannkonsept | R1 / ORIGINAL_REQUEST | BKL 3, RKL 5, sprinkler, Inergen | brannklasse per rom (EI-60 vs EI-30) | slokkesystem vs sonetype (Inergen i S4) | Tilsyn fra Trøndelag brann- og redningstjeneste |
| 4 | Berikede Romstempler | R1 / ORIGINAL_REQUEST | romnummer, navn, BRA, H, gulv, brann, soner | alle 19 rom har komplette felt | romstempel tekst i SVG matcher romobjekt i JSON | Sikkerhets- og publikumsvandring |
| 5 | Veggdefinisjoner & Tykkelser | R1 / ORIGINAL_REQUEST | 400 mm tegl, 300 mm betong, 200 mm innervegg | veggtykkelse > 0, gyldig hatch-referanse | hatch patterns definert i SVG `<defs>` | Arkitektkontroll av bæresystem |
| 6 | SVG Doble Vegger med Skravur | R1 / ORIGINAL_REQUEST | `<pattern>` for tegl, betong, innervegg | mønsterstørrelse, vinkel 45° | vegger refererer mønstre via `fill="url(#...)"` | Grafisk produksjon av arbeidstegninger |
| 7 | SVG Målekjeder & Arkitekt-ticks | R1 / ORIGINAL_REQUEST | mållinjer, 45° ticks, millimetertekster | minst 4 målekjeder per etasje | målekjede koordinater stemmer med rombredder | Målsatt anbudstegning til entreprenør |
| 8 | SVG Kotehøyder | R1 / ORIGINAL_REQUEST | kotesymboler og tall for U1, P1, P2 | kote U1 < P1 < P2 < Gesims | koter i SVG matcher matrikkelkoter i JSON | Høydeprofil mot Nidelva flomkote |
| 9 | NS 8351 Romstempelformat | R1 / ORIGINAL_REQUEST | 3-linjers oppsett med ramme og standardrekkefølge | tekstformatering `[romnr romnavn ...]` | alle 19 rom har synlige stempler i SVG | Skilting og romorientering for vektere |
| 10 | Fullverdig Tegningshode | R1 / ORIGINAL_REQUEST | institusjon, matrikkel, arealer, brann, målestokk | tegningshode i alle 3 etasje-SVG-er | tegningshode data er 100% konsistent med JSON | Arkivgodkjenning etter arkivloven |
| 11 | 2.5D Kartviser & Drawer | R3 / ORIGINAL_REQUEST | Canvas isometri, drawer, datafelter | drawer viser nye felter (materialer, brann, NS 3940) | modell i JS matcher `bygning_geometri.json` | Operativt vaktrom i intern_hub (port 8001) |
| 12 | Visuell Konsistens (9 motiver) | R2 / ORIGINAL_REQUEST | 9 motiver i `06_kart/bilder/` matchet mot rom/soner | U1, P1, P2 dekker alle bildemotiver | bildereferanser i index.html er intakte | Formidlingspresentasjon for publikum |

## Test Architecture
- **Runner**: `py -3.13 -m pytest tests/test_building_map.py -v`
- **Tilleggsverktøy**: `scripts/verify.ps1`, `/deterministisk-validator`, `/validated-builder`
- **Pass/Fail Semantikk**: 100 % passering, null advarsler, null inkonsistenser mellom JSON, SVG og HTML.

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: Minst 15 atomære tester som verifiserer hvert enkelt krav isolert.
- **Tier 2 (Boundary & Corner Cases)**: Minst 10 tester som verifiserer grenseverdier (arealsummer, kote-relasjoner, veggtykkelser, romnummer-unikehet).
- **Tier 3 (Cross-Feature Combinations)**: Minst 6 tester som verifiserer konsistens på tvers av artefakter (JSON vs SVG vs HTML).
- **Tier 4 (Real-World Scenarios)**: Minst 4 helhetlige scenario-tester (Brann-/redningsscenario, museumstilsyn, arealattest, entreprenørgransking).
- **Totalt antall tester**: >= 35 tester i `tests/test_building_map.py`.
