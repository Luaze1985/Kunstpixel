# Design: nye plantegninger for Kunstpixel som henger sammen

Dato: 2026-11-22 · Status: utkast til Lars · Gjelder: `06_kart/` (data, plantegninger, kart), kunnskapsfila om bygget, PDF-en

## Hvorfor

Lars vil ha tegninger av museet der mål, arealtall og romliste stemmer med hverandre og med bildene. Bygget skal senere brukes til å teste KI i drift (servere, renholds-, vakt- og transportroboter) og til øvingsdager. Det kommer i en egen runde. Denne runden lager tegningene og setter av plass til maskinparken.

I dag stemmer tegningene ikke:
- Bygget er tegnet 48 × 24 m (1 152 m²), mens BTA og BYA er 1 450 m² per etasje.
- Rommene dekker bare 52–77 % av BRA, og ganger, toaletter, garderober, kontorer og en ekstra rømningstrapp mangler.
- Heisen i P1 overlapper vestibylen. Heis og trapper står ikke over hverandre fra etasje til etasje.
- Veggene, målene og bygningskroppen i 2D og 2.5D er skrevet rett inn i `build_map.py`. De leses ikke fra dataene.

## Mål
1. Ett fotavtrykk i dataene som både plantegningene (SVG) og 2.5D-kartet tegnes fra.
2. Hver etasje fylles helt av rom. Arealet til hvert rom er lik bredde × dybde.
3. Arealtallene regnes ut fra tegningen og kan sjekkes med tester.
4. Bygget fungerer som bygg: rom og trapper står over hverandre, og det er to rømningsveier fra hver etasje. Publikum kommer ikke inn i drifts- og magasinsonene. Kunsten flyttes med vareheisen.
5. Det settes av et tomt areal i kjelleren til maskinparken.

## Ikke-mål (denne runden)
- Maskinparken: serverrom, robotgarasje, ladepunkter, kjøreveier og eget kartlag. Bare reservearealet tegnes.
- Øvingsdager og eventuelt øvingsrom.
- Fasadetegninger, snitt, situasjonsplan, rømningsplan og nye bilder.
- Endringer i `museum.db`. Tabellen `saler` har ikke arealer og berøres ikke.

## Anti-mål (dette ville vært feil selv om det virker)
- Tall som bare stemmer fordi de er skrevet inn for hånd et annet sted enn i dataene.
- At Sal A–E får andre arealer, navn eller etasjer enn det databasen, bildene og PDF-en bruker.
- Tegninger som ser riktige ut, men der rom overlapper eller trapper ikke henger sammen mellom etasjene.

## Valgt løsning (Lars valgte A og «regn BRA fra tegningen»)

**Tilnærminger som ble vurdert:**
- **A. To bygningskropper med samme BTA og BYA.** Hovedfløyen fra 1912 og glassfløyen fra 2016 tegnes hver for seg. *Valgt.* Tegningen, bildene og tallene forteller da samme historie.
- **B. Én rektangel.** Enklere, men skillet mellom fløyene forsvinner, og bildene viser to fløyer.
- **C. Behold dagens tegning og endre tallene til 1 152 m² per etasje.** Bygget blir mindre enn alt annet sier.

**Lars' beslutning om arealtall:**
- BTA 4 350 m² og BYA 1 450 m² står fast.
- BRA regnes ut fra tegningen og blir ca. 1 390 m² per etasje, ca. 4 170 m² totalt. I dag står det 3 920.
- Dagens BRA kan ikke stemme med 30–40 cm tykke yttervegger.

### Bygningskroppen
- **Totalt:** 58,0 × 25,0 m = 1 450 m² per etasje (BTA = BYA). Nord er øverst og Bispegata ligger i sør. Hovedinngangen går fra Bispegata inn i hovedfløyen.
- **Hovedfløy 1912 (vest):** 34,0 × 25,0 m.
  - Yttervegger i tegl, 400 mm.
  - Den gamle østfasaden står igjen som 400 mm innervegg mot glassfløyen.
- **Glassfløy 2016 (øst, mot Nidelva):** 24,0 × 25,0 m.
  - Yttervegger i betong/glass, 300 mm.
- **I dataene:** `fotavtrykk` med to volumer (x, y, b, d, veggtykkelse og byggeår). 10 koordinatenheter er 1 m, som i dag.

### Arealregning (fasit i testene)
- BTA per etasje = summen av volumene = 1 450.
- BRA per etasje = BTA − ytterveggenes areal. Den gamle fasadeveggen mellom fløyene er en innervegg og regnes med i BRA.
- **Rommene:**
  - Rommene fyller hele innsiden av ytterveggene. Innerveggene tegnes som linjer uten tykkelse.
  - Unntaket er fasadeveggen mellom fløyene, som tegnes som en egen stripe.
  - Summen av rommene pluss fasadeveggen er lik BRA for etasjen (toleranse 0,5 m²).
  - Hvert rom: `areal_m2` = b × d / 100 (én desimal).
- **Kjelleren (U1)** har samme fotavtrykk og veggtykkelse. Bygget har ingen terrasser, så BYA = BTA for 1. etasje.
- BRA-tallene i `arealer_ns3940` skrives fra utregningen. De er ikke en egen fasit.

### Romprogram

Sal A–E, magasinet og de andre 19 rommene beholder ID, navn, etasje og areal. Kafeen beholder 140 m², men flyttes innenfor glassfløyen. Nye rom fyller resten. Arealene for nye rom er mål og justeres så etasjen går opp.

**P1 Hovedplan.**
- Hovedfløyen (innvendig ca. 803 m², så det er trangt):
  - Sal A (216) og Sal B (156) i nord.
  - En gang øst–vest på ca. 2,5–2,7 m gjennom bygget. Den er resten av arealet når de faste rommene er plassert.
  - Bokhandel (140) i sørvest.
  - Vestibyle med billett (160) midt mot Bispegata.
  - Monumentaltrapp (25) og publikumsheis (16).
- Glassfløyen:
  - Sal E (156) i nord.
  - Kafé (140) i sørøst mot Nidelva, med kjøkken/anretning (ca. 40).
  - **Publikumsgarderobe og toaletter med HC-toalett (ca. 60).** De ligger her og ikke i hovedfløyen, fordi hovedfløyen ikke har plass (byggerens valg).
  - Rømningstrapp 2 og vareheis.

**P2 Galleri.**
- Hovedfløyen:
  - Sal D (216, høysikkerhet) i nord, bak massive vegger.
  - Administrasjon og kontorer (direktør, kurator, stab, ca. 120) og møterom (ca. 40).
  - Personalrom og garderobe (180).
  - Trapp og heis over P1.
- Glassfløyen:
  - Sal C (240) i sørøst. Den beholder de «sørøstvendte vinduene» fra beskrivelsen.
  - Vaktrom og sikkerhetssentral (140).
  - Rømningstrapp 2 og vareheis.
- Galleri og gang knytter salene sammen.

**U1 Kjeller.**
- Magasin 1 (252) og kunstmottak med konservering (168), med kjøresluse mot bakgården.
- Teknisk rom og klimasentral (196).
- Vareheis (36) og trapp (36).
- Magasin 2 / papirarkiv (ca. 100, S4/K1).
- Verksted for montering (ca. 80).
- Renhold og avfall (ca. 30).
- Gang.
- **Reserve – fremtidig maskinpark (ca. 150–200 m²):** S3, ved klimasentralen og vareheisen, så den senere kan dele kjøling og nå alle etasjer.

**Gjennomgående.**
- Publikumsheis og hovedtrapp står på samme sted i P1 og P2. Publikumsheisen går ikke til kjelleren, som i dag.
- **Hovedtrappen fortsetter ned til U1** som et lukket trapperom bare for ansatte. Ny rom-ID er `TRAPP-U1B` (25 m²), med låst dør på P1-nivå og S3. Kjelleren får da to trapper uten at publikum kommer inn i S3/S4 (byggerens valg).
- **`TRAPP-U1` (36 m²) er bunnen av rømningstrapp 2** i glassfløyen. Rømningstrapp 2 er 36 m² i alle tre etasjer og står inntil vareheisen.
- Vareheisen og rømningstrapp 2 står på samme sted i alle tre etasjer.
- Hver etasje har minst to trapper til rømning.
- **Kunsten flyttes** med vareheisen i glassfløyen. På P1 og P2 går den gjennom gangene utenom åpningstid. Det er ingen egen kunstkorridor. Adskilte veier for kunst og publikum gjelder kjelleren og heisen (byggerens valg).
- **Bakgården ligger i nord.** Kjøreslusen til kunstmottaket går via en rampe fra bakgården ned til U1, på nordsiden av glassfløyen (byggerens valg).
- **P2 har gulv over hele vestibylen.** Det er ikke noe rom åpent over to etasjer, siden BTA er fast. Bildet av vestibylen stemmer derfor ikke helt. Det står på avvikslista.

### Kart og tegninger
- **Plantegningene:** `build_map.py` tegner yttervegger, fasadevegg, mållinjer (58 000 / 25 000 mm, og 34 000 / 24 000 mm per fløy) og underlag fra `fotavtrykk`. Ingenting om bygget skrives fast i koden. Tegningshodet og romlista flyttes, så de ikke kolliderer med det større bygget. Den mørke stilen beholdes.
- **2.5D-kartet:** midtpunkt, gulvplate, bakke og skall leses fra `fotavtrykk`. Skallet tegnes som tegl for hovedfløyen og glass for glassfløyen. Sjaktene tegnes fra heis- og trapperommene.
- **Romlista** på tegningen kan bli lang. Rom under 20 m² kan grupperes eller få mindre skrift. Utformingen er byggerens valg.

### Tester (spesifikasjonen)
Testene i `tests/test_building_map.py` som låser 19 rom, BRA 3 920 og bestemte veggkoordinater, skrives om med vilje. Nye tester:
- Alle rom ligger innenfor fotavtrykket og overlapper ikke hverandre.
- `areal_m2` = b × d / 100 for hvert rom.
- Summen av rom og fasadevegg = BRA for etasjen. BRA = BTA − yttervegger. BTA = 1 450 = BYA. Summen av etasjene = BRA totalt.
- De 19 opprinnelige rom-ID-ene finnes, og Sal A–E har samme areal som før.
- Heis og trapper har samme posisjon i alle etasjer de går gjennom. Hver etasje har minst to trapper.
- Reservearealet for maskinparken finnes i U1.
- Mållinjene i SVG-ene viser målene fra `fotavtrykk`.
- Kafeen ligger i glassfløyen (gjelder fra før).
- Ingen faste byggmål står i `build_map.py`, for eksempel `48 000`.

### Følgeendringer
- `04_knowledge/04_domain/core/bygning_og_etasjeplaner.md` skrives om etter de nye planene. Det gjelder tegningene i tekst og BRA-tallene.
- `test_bygning_konsistens.py` justeres for nytt BRA.
- PDF-en lages på nytt.
- `docs/DECISIONS.md` og `PLAN.md` oppdateres.

## Overlatt til byggeren
- Eksakte koordinater og arealer for nye rom innenfor reglene over.
- Hvordan romlista og tegningshodet plasseres i SVG-en.
- Farger på nye romtyper, i samme stil som i dag.
- Rom-ID-er for nye rom, i samme mønster som i dag (`WC-P1`, `KON-1`, `RES-MASK-1` osv.). Romnummer følger etasjeprefikset.

## Risiko
- Bilder og tekst som omtaler plassering kan stemme dårligere etterpå. Eksempel: Sal C «sørøstvendte vinduer» stemmer bedre, mens bildet av vestibylen viser et rom over to etasjer. Byggeren sjekker beskrivelsene i JSON-en for hvert rom som flyttes.
- En Datafinner- eller MCP-server som kjører, viser den gamle modellen til den startes på nytt (`lru_cache`).
