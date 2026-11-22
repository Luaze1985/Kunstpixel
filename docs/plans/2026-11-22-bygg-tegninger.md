# Nye plantegninger for Kunstpixel – byggeplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (Lars' standard: inline) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Mål:** Tegne Kunstpixel på nytt som 58 × 25 m (to fløyer), slik at rom, arealer, trapper og tegninger henger sammen og leses fra én modell.

**Arkitektur:**
- `06_kart/bygning_geometri.json` får et `fotavtrykk`, og romlisten fyller hver etasje.
- En ny modul, `06_kart/geometri.py`, regner arealer og sjekker regler.
- `build_map.py` tegner SVG-ene og 2.5D-kartet fra fotavtrykket i stedet for faste tall.

**Verktøy:** Python 3.13, pytest, vanlig JS i den genererte HTML-en og Edge (headless) for PDF-en. Ingen nye pakker.

**Spec:** `docs/specs/2026-11-22-bygg-tegninger-design.md` (godkjent av Lars 2026-11-22)

## Globale krav
- 10 koordinatenheter er 1 m. Bygget har ytre hjørne (40, 40).
- **Hovedfløy:**
  - x 40–380, y 40–290, vegg 400 mm.
  - Innvendig x 44–376, y 44–286.
- **Glassfløy:**
  - x 380–620, y 40–290, vegg 300 mm.
  - Innvendig x 380–617, y 43–287.
- **Fasadevegg** mellom fløyene: x 376–380, y 44–286 (9,68 m²).
- **Arealer:**
  - BTA 1 450 per etasje, 4 350 totalt. BYA 1 450.
  - BRA 1 391,4 per etasje, 4 174,2 totalt.
  - Utnyttelse (%-BYA) 45,3.
- Romareal = b × d / 100. Rommene i en etasje dekker hele innsiden. Summen av rom og fasadevegg er BRA (toleranse 0,5).
- **Uendret:** Sal A 216, B 156, C 240, D 216 og E 156.
- **Andre rom:** KAF-1 140, BUT-1 140, RES-1 160, MAG-1 252, VER-1 168, TEK-1 196, PAU-1 180, HEIS-U1 36, TRAPP-U1 36 og publikumsheis 16 beholder arealet.
- **Avvik fra spec, notert:** VAK-1 140 → 120 og TRAPP-P1/P2 25 → 26,4. Det gikk ikke opp ellers. Vaktrommet flyttes til hovedfløyen.
- Ingen faste byggmål i `build_map.py` (ingen `48 000`, `24 000`, `3 920`, `4 350` eller veggkoordinater).

## Romoppsett (fasit for oppgave 1, x, y, b, d)

**P1**
| ID | Nr | Navn | x | y | b | d | m² | Sone/klima | Sjakt |
|---|---|---|---|---|---|---|---|---|---|
| SAL-A | 101 | Sal A – Mytologi og natur | 44 | 44 | 180 | 120 | 216 | S2/K2 | |
| SAL-B | 102 | Sal B – Realisme og samfunn | 224 | 44 | 130 | 120 | 156 | S2/K2 | |
| TRAPP-P1 | 108 | Monumentaltrapp P1 | 354 | 44 | 22 | 120 | 26.4 | S1/K3 | hovedtrapp |
| GANG-P1 | 109 | Gang hovedfløy P1 | 44 | 164 | 332 | 22 | 73.04 | S1/K3 | |
| BUT-1 | 105 | Museumsbutikk / Bokhandel | 44 | 186 | 140 | 100 | 140 | S1/K3 | |
| RES-1 | 104 | Vestibyle & Resepsjon | 184 | 186 | 160 | 100 | 160 | S1/K3 | |
| HEIS-P1 | 107 | Publikumsheis P1 | 344 | 186 | 32 | 50 | 16 | S1/K3 | publikumsheis |
| LAG-P1 | 110 | Billett- og brosjyrelager | 344 | 236 | 32 | 50 | 16 | S3/K3 | |
| VHEIS-P1 | 111 | Vare- og kunstheis P1 | 380 | 43 | 60 | 60 | 36 | S3/K2 | vareheis |
| TRAPP2-P1 | 112 | Rømningstrapp 2 P1 | 380 | 103 | 60 | 60 | 36 | S3/K3 | romningstrapp-2 |
| SLU-P1 | 113 | Kunstsluse og lager Sal E | 440 | 43 | 47 | 120 | 56.4 | S3/K2 | |
| SAL-E | 103 | Sal E – Temporær utstilling | 487 | 43 | 130 | 120 | 156 | S2/K2 | |
| GANG-P1G | 114 | Gang glassfløy P1 | 380 | 163 | 237 | 24 | 56.88 | S1/K3 | |
| WC-P1 | 115 | Publikumsgarderobe og toaletter | 380 | 187 | 57 | 100 | 57 | S1/K3 | |
| KJK-P1 | 116 | Kafékjøkken | 437 | 187 | 40 | 100 | 40 | S3/K3 | |
| KAF-1 | 106 | Museumskafé & Atrium | 477 | 187 | 140 | 100 | 140 | S1/K3 | |

**P2**
| ID | Nr | Navn | x | y | b | d | m² | Sone/klima | Sjakt |
|---|---|---|---|---|---|---|---|---|---|
| SAL-D | 202 | Sal D – Eksistens og modernisme | 44 | 44 | 180 | 120 | 216 | S2/K1 | |
| ADM-1 | 207 | Administrasjon og direktørkontor | 224 | 44 | 130 | 120 | 156 | S3/K3 | |
| TRAPP-P2 | 206 | Trappeløp Repos P2 | 354 | 44 | 22 | 120 | 26.4 | S1/K3 | hovedtrapp |
| GANG-P2 | 208 | Gang hovedfløy P2 | 44 | 164 | 332 | 22 | 73.04 | S1/K3 | |
| PAU-1 | 204 | Personalrom & Garderobe | 44 | 186 | 180 | 100 | 180 | S3/K3 | |
| VAK-1 | 203 | Vaktrom & Sikkerhetssentral | 224 | 186 | 120 | 100 | 120 | S3/K3 | |
| HEIS-P2 | 205 | Heis Repos P2 | 344 | 186 | 32 | 50 | 16 | S1/K3 | publikumsheis |
| WC-P2 | 209 | Toaletter P2 | 344 | 236 | 32 | 50 | 16 | S1/K3 | |
| VHEIS-P2 | 210 | Vare- og kunstheis P2 | 380 | 43 | 60 | 60 | 36 | S3/K2 | vareheis |
| TRAPP2-P2 | 211 | Rømningstrapp 2 P2 | 380 | 103 | 60 | 60 | 36 | S3/K3 | romningstrapp-2 |
| FOR-P2 | 212 | Heisforrom og føringssjakt | 440 | 43 | 17 | 120 | 20.4 | S3/K3 | |
| KON-P2 | 213 | Kontorer, kurator og møterom | 457 | 43 | 160 | 94 | 150.4 | S3/K3 | |
| SAL-C | 201 | Sal C – Lys, farge og interiør | 457 | 137 | 160 | 150 | 240 | S2/K2 | |
| GANG-P2G | 214 | Gang glassfløy P2 | 380 | 163 | 77 | 24 | 18.48 | S1/K3 | |
| WC-P2G | 215 | Toaletter og lager P2 | 380 | 187 | 77 | 100 | 77 | S1/K3 | |

**U1**
| ID | Nr | Navn | x | y | b | d | m² | Sone/klima | Sjakt |
|---|---|---|---|---|---|---|---|---|---|
| MAG-1 | 001 | Magasin 1 – Klimastyrt lager | 44 | 44 | 210 | 120 | 252 | S4/K1 | |
| MAG-2 | 006 | Magasin 2 – Papirarkiv | 254 | 44 | 100 | 120 | 120 | S4/K1 | |
| TRAPP-U1B | 007 | Hovedtrapp U1 (kun ansatte) | 354 | 44 | 22 | 120 | 26.4 | S3/K3 | hovedtrapp |
| GANG-U1 | 008 | Gang hovedfløy U1 | 44 | 164 | 332 | 22 | 73.04 | S3/K3 | |
| VERK-1 | 009 | Monteringsverksted | 44 | 186 | 80 | 100 | 80 | S3/K3 | |
| REN-1 | 010 | Renhold, avfall og lager | 124 | 186 | 56 | 100 | 56 | S3/K3 | |
| TEK-1 | 003 | Teknisk rom & Klimasentral | 180 | 186 | 196 | 100 | 196 | S3/K3 | |
| HEIS-U1 | 004 | Vare- og Kunstheis U1 | 380 | 43 | 60 | 60 | 36 | S3/K2 | vareheis |
| TRAPP-U1 | 005 | Rømningstrapp 2 U1 | 380 | 103 | 60 | 60 | 36 | S3/K3 | romningstrapp-2 |
| VER-1 | 002 | Kunstmottak & Konservering | 440 | 43 | 140 | 120 | 168 | S4/K2 | |
| KJS-U1 | 011 | Kjøresluse fra bakgården | 580 | 43 | 37 | 120 | 44.4 | S4/K2 | |
| GANG-U1G | 012 | Gang glassfløy U1 | 380 | 163 | 237 | 24 | 56.88 | S3/K3 | |
| MASK-RES-1 | 013 | Reserve – fremtidig maskinpark | 380 | 187 | 177 | 100 | 177 | S3/K3 | |
| LAG-U1 | 014 | Lager U1 | 557 | 187 | 60 | 100 | 60 | S3/K3 | |

Kontrollert med et skript 2026-11-22: ingen overlapp, alle rom ligger innenfor fløyene, og summen av rom (1 381,72) pluss fasadevegg (9,68) er 1 391,4 per etasje.

## Gjennomgangsfokus
- **Smale rom (gang 2,2 m, trapp 2,2 m, forrom 1,7 m):** romteksten i SVG-en skal ikke flyte utover rommet. *Test:* i oppgave 2 skal teksten i rom under 4 m være kortnavn eller romnummer.
- **Rom flyttet mellom fløyene (vaktrom, Sal C):** beskrivelsene i JSON-en må ikke si noe annet enn plasseringen. *Test:* i oppgave 1 skal ingen beskrivelse nevne «48 m», «24 m» eller «1980».
- **Kjørende Datafinner/MCP med `lru_cache`:** viser den gamle modellen til den startes på nytt. Noteres i PLAN, ingen test.
- **Rotasjon av 2.5D-kartet (4 vinkler):** bygget må holde seg sentrert. *Sjekkes* i nettleseren i oppgave 3.
- **PDF-tabellene for etasjene:** blir lengre (14–16 rom). *Sjekkes* visuelt i oppgave 4.

---

### Oppgave 1: Modell og arealregning

**Filer:**
- Lag: `06_kart/geometri.py`, `tests/test_bygning_geometri.py`
- Endre: `06_kart/bygning_geometri.json`, `tests/test_building_map.py`, `tests/test_bygning_konsistens.py`

**Grensesnitt (brukes av senere oppgaver):**
- `geometri.rom_areal(rom: dict) -> float`: b × d / 100, avrundet til 2 desimaler.
- `geometri.bra_etasje(modell: dict) -> float`: summen av innvendige rektangler pluss fasadevegg.
- `geometri.bta_etasje(modell: dict) -> float`: summen av volumene.
- `geometri.feil(modell: dict) -> list[str]`: tom liste når alt stemmer. Sjekker:
  - overlapp,
  - rom utenfor fløyene,
  - areal ≠ b × d,
  - at etasjen ikke er fylt (rom + fasadevegg ≠ BRA),
  - at rom med samme `sjakt` har ulik plassering,
  - at en etasje har færre enn 2 trapper.
- JSON:
  - `museum.fotavtrykk = {"volumer": [{id, navn, x, y, b, d, vegg_mm, byggeaar, materiale, innvendig: {x, y, b, d}}], "fasadevegg": {x, y, b, d}}`.
  - Hvert rom får `type` (sal | publikum | gang | trapp | heis | wc | kontor | drift | lager | magasin | teknisk | reserve) og eventuelt `sjakt`.

- [ ] **Steg 1:** Skriv testene i `test_bygning_geometri.py`:
  - `test_modellen_har_ingen_feil`: `feil(modell) == []`.
  - `test_bta_og_bya_er_1450`: BTA per etasje 1450, `bta_m2 == 4350`, `bya_m2 == 1450`.
  - `test_bra_regnes_fra_tegningen`:
    - `bra_etasje == 1391.4` (±0,01).
    - `etasjefordeling_bra` er 1391.4 for U1, P1 og P2.
    - `bra_m2 == 4174.2`.
  - `test_innvendig_stemmer_med_veggtykkelse`: innvendig rektangel = volumet krympet med `vegg_mm/100` enheter på ytre sider.
  - `test_de_19_opprinnelige_rommene_finnes` og `test_salene_har_samme_areal`: A 216, B 156, C 240, D 216, E 156.
  - `test_hver_etasje_har_to_trapper`, `test_reserveareal_for_maskinpark_i_U1`.
  - `test_ingen_beskrivelse_nevner_gamle_mal`: ingen «48 m», «24 m» eller «1980».
- [ ] **Steg 2:** `py -3.13 -m pytest tests/test_bygning_geometri.py -q`. Forventet: FEIL. Modulen og feltene mangler.
- [ ] **Steg 3:** Skriv `geometri.py` og legg inn fotavtrykk og rom fra tabellene i JSON-en.
  - Rom som finnes fra før beholder materialer og sensorer.
  - Nye rom får korte `materialer` (gulv, vegg, himling), `brannklasse` (trapp EI-60, heis REI-120, MAG-2 EI-90, ellers EI-30/EI-60), `takhoyde_m` (P1 hovedfløy 6.0, P1 glass 4.5, P2 4.8 for saler og 3.2 for andre, U1 3.8), `kapasitet_verk`, `beskrivelse`, `dor_pos` og `sensorer: []`.
  - Oppdater `arealer_ns3940` med de nye BRA-tallene.
- [ ] **Steg 4:** Skriv om de låste testene i `test_building_map.py`:
  - 19 rom → minst 19 og unike.
  - BRA 3920 → 4174.2.
  - Bredde ≥ 30 → oppholdsrom (sal, kontor, publikum, magasin, drift) ≥ 30, andre ≥ 16.
  - Veggkoordinatene i `test_tier1_svg_innvendige_baerevegger…` → erstattes av `test_tier3_svg_vegger_fra_fotavtrykk` i oppgave 2.
  - Tegningshode «3 920» → verdien fra JSON.
  
  I `test_bygning_konsistens.py`: VAK-1 har 120 i kunnskapslista, og BRA er 4 174.
- [ ] **Steg 5:** Kjør `py -3.13 -m pytest tests/test_bygning_geometri.py tests/test_bygning_konsistens.py -q`. Forventet: PASS, men kunnskapsfila feiler til oppgave 4. Testene i `test_building_map.py` som gjelder SVG feiler til oppgave 2.

### Oppgave 2: Plantegninger (SVG) fra fotavtrykket

**Filer:** Endre `06_kart/build_map.py` (`generate_blueprint_svg`), test i `tests/test_building_map.py`.
**Grensesnitt:** Bruker `geometri.*` og `fotavtrykk` fra oppgave 1. Gir `plantegning_{u1,p1,p2}.svg`.

- [ ] **Steg 1:** Tester:
  - `test_tier3_svg_vegger_fra_fotavtrykk`: hvert volum har ytterveggrektangler med hatch etter materiale. Fasadeveggen er tegnet med `hatch-tegl-400`.
  - `test_svg_malkjeder_viser_fotavtrykk`: «58 000», «25 000», «34 000» og «24 000» finnes.
  - `test_svg_tegningshode_fra_data`: BTA, BRA og BYA fra JSON.
  - `test_ingen_faste_byggmal_i_build_map`: kildeteksten inneholder ikke «48 000», «24 000 mm</text>» eller `x="105" y="279"`.
  - `test_smale_rom_far_kortnavn`: for rom med b eller d under 40 er tittelteksten romnummeret.
- [ ] **Steg 2:** Kjør. Forventet: FEIL.
- [ ] **Steg 3:** Skriv om `generate_blueprint_svg`:
  - **Vegger** fra volumene: tegl-hatch for 1912 og betong-hatch for 2016.
  - **Fasadevegg.**
  - **Bærevegger** langs gangene med `hatch-baerevegg-200`, så mønsteret fortsatt brukes.
  - **Mållinjer** fra volumene.
  - **Layout:** `viewBox="0 0 1100 680"`, tegningshodet på `translate(740, 80)`.
  - **Farger** etter `type`.
  - **Romteksten** krympes eller byttes til romnummer for smale rom.
- [ ] **Steg 4:** Kjør `py -3.13 06_kart/build_map.py`, deretter `py -3.13 -m pytest tests/test_building_map.py tests/test_bygning_geometri.py -q`. Forventet: PASS.

### Oppgave 3: 2.5D-kartet fra fotavtrykket

**Filer:** Endre `06_kart/build_map.py` (JS i `generate_html`: `toIso`, `drawGround`, `drawFloorSlab`, `drawExteriorShell`, `drawShafts`, `getRoomColor`, tekst i headeren).

- [ ] **Steg 1:** Test `test_html_bruker_fotavtrykk`:
  - HTML-en inneholder `MODEL.museum.fotavtrykk`.
  - HTML-en inneholder ikke de faste koordinatene `toIso(540, 20` og `toIso(370, 20`.
  - Headeren viser BRA fra data.
- [ ] **Steg 2:** Kjør. Forventet: FEIL.
- [ ] **Steg 3:** Regn ut grensene (minimum og maksimum av volumene) én gang i JS.
  - Midtpunktet til `toIso` er midten av fotavtrykket.
  - Bakke og gulvplate tegnes fra grensene med 20 enheters marg.
  - Skallet tegnes per volum: tegl `#991b1b` for 1912 og glass `rgba(56,189,248,0.35)` for 2016.
  - Sjaktene tegnes fra rom som har samme `sjakt` i flere etasjer.
- [ ] **Steg 4:** Bygg og kjør testene. Forventet: PASS.
- [ ] **Steg 5:** Åpne kartet med oppstarten «kart» i det innebygde vinduet og sjekk:
  - P1, P2 og U1 i røntgen,
  - skallet,
  - alle 4 rotasjoner,
  - konsollen uten feil.
  
  Ta ett skjermbilde.

### Oppgave 4: Kunnskapsfil, PDF og logg

**Filer:**
- `04_knowledge/04_domain/core/bygning_og_etasjeplaner.md`
- `02_deliverables/bygningsdokumentasjon/lag_pdf.py`
- `docs/DECISIONS.md`, `PLAN.md`

- [ ] **Steg 1:** Skriv om kunnskapsfila etter romtabellene. Det gjelder planene i tekst, BRA 4 174 / 1 391 og «Ikke tegnet inn ennå», som fjernes.
- [ ] **Steg 2:** Kjør `py -3.13 -m pytest tests/test_bygning_konsistens.py -q`. Forventet: PASS.
- [ ] **Steg 3:** I `lag_pdf.py`:
  - Fjern avvikene om fotavtrykk og rom mot BRA.
  - Legg til et avvik om vestibylebildet (rom over to etasjer).
  - Bilder som mangler oppdateres med nye rom: VAK-1 i hovedfløyen, maskinpark-reserve og administrasjon.
  - Kjør skriptet og se gjennom alle sidene som PNG.
- [ ] **Steg 4:** DECISIONS: nytt avsnitt G1–Gn. Skriv inn Lars' valg (A, BRA fra tegningen, tegninger først), agentens valg fra speccen og avvikene VAK 120 og trapp 26,4. Oppdater PLAN.
- [ ] **Steg 5:** Kjør hele `py -3.13 -m pytest -q`. Forventet: de samme 8 kjente feilene som før (arena, chat-eval U2, skill, start-gate) og ingen nye.
- [ ] **Steg 6:** Commit bare når Lars sier ja.
