# PLAN — status

**Aktiv plan:** [Kart: ren main](docs/plans/2026-11-15-ren-main.md). Demo-v2 er droppet (DECISIONS W1).

**Pågår i `main`:** [Revisjonsfunnene](docs/plans/2026-11-10-revisjonsfunn.md), 17 funn fra ekstern gjennomgang.
- Pakke 1 er ferdig (2026-11-10): funn 6, 7, 9, 11, 13 og 14. Hele pytest: 2220 bestått, 9 hoppet over, 2 ventede feil. Også grønn i en ren utsjekk for de berørte testene.
- Pakke 2 er ferdig (2026-11-10): funn 3, 4 og 5. Colab-databasen og MintHCM-dumpen spores ikke lenger. Last opp de nye Colab-filene til Drive selv.
- Pakke 3 er ferdig i koden (2026-11-10): funn 1, 10 og 12. **Lars må bygge:** `py -3.13 src/kunstpixel/data/build_museum_db.py`, og `museum.db` må committes etterpå.
- Neste: pakke 4 (Datafinner-sperre) og 5 (innholdshash og dokumenter).
- Funn 2 (rolle fra klienten) er utsatt, og funn 16 (domene og telefon) gjøres ikke. Se `docs/DECISIONS.md`.

## Gjort (2026-11-16): Datafinner etappe 2, «I dag» (DECISIONS I1–I10), grenen `datafinner-ledelse`
- Kortet «I dag» på Hjem: åpent/stengt, besøk siste hele dag mot normalt, vakter, arrangementer, driftsmeldinger (bare antall per kategori), HMS-avvik. Hvert tall åpner radene bak. Virker uten KI. Committet (13aa545).
- B5 «Driften denne uka» er ferdig. Lars bygget `museum.db`, og den er committet (6641cda). Hele pytest: 2372 bestått, 9 hoppet over, 2 ventede feil.
- Uavhengig sjekk: kontrollfil til Antigravity i `.scratch/handoffs/AGY-REVIEW-2026-11-16-etappe2.md`. Funnene skal skrives til `AGY-FUNN-2026-11-16.md`.
- Ukjente endringer i `db.py`, `mcp_server.py`, `test_mcp_server.py`, `AGENTS.md` og `05_data/index.md` (ser ut som K2-arbeid fra en annen økt) er ikke rørt og ikke committet.

## Gjort (2026-11-22): regelbaserte rettinger i databasen (DECISIONS R1–R7), ikke committet
- 17 vakter, `hr_skills`, kopier i `personas`, rollekoder, publikumsserier til 31.12, lange sykemeldinger, ett tall i dokumentasjonen. Skjemaversjon 9.
- **Gjort:** `museum.db` er bygget (DECISIONS B2), og hele pytest er grønn.
- **Gjenstår, i denne rekkefølgen:** (1) start Datafinner og åpne Claude-økter på nytt (de har gammel kode som leser `hr_skills`), (2) `py -3.13 scripts/lag_claude_skill.py` og last opp pakken, (3) `py -3.13 scripts/lag_storskjerm.py` og publiser til samme lenke, (4) commit med `museum.db` og `museum.db.sha256`.
- Også gjort (DECISIONS O1–O3, N1): overtid med 40 % tillegg, og innlån returneres ved utstillingens slutt.
- **Gjort (Ø2–Ø6):** driftsregnskap per måned (`05_data/driftsregnskap.csv`, `regnskap_builder.py`, tabell `driftsregnskap`, MCP `get_operating_accounts`). h5 regnes fra vaktene og dagsdataene i bygget. Skjemaversjon fortsatt 9. Ikke committet.
- **Åpent for Lars:** bekreft kafé før 2024 (Ø3: h5-tall fordelt på måneder) og de frie kostnadsnivåene. Resultatet er negativt 2010–2018 og 2020–2021.
- **Lars:** bygg `museum.db` på nytt. Før det er K1-, D4- og skill-testene røde mot den gamle filen. Hvis vaktene endres: kjør `py -3.13 src/kunstpixel/data/regnskap_builder.py` før bygget.
- **Neste:** skjønnsrettinger S1–S6 med LLM (hr_people mot hr_ansatte, utstillinger mot historikken, stillingstitler som rolle, regeltekster, håndbokens målgrupper, fritekst).

## Gjort (2026-11-22): bygget, bilder og PDF (DECISIONS B1–B6), ikke committet
- PDF: `02_deliverables/bygningsdokumentasjon/kunstpixel_bygning.pdf`. Lages på nytt med `py -3.13 02_deliverables/bygningsdokumentasjon/lag_pdf.py`.
- Det gamle navnet er fjernet fra 8 bilder. Kafeen er flyttet til glassfløyen mot Nidelva og har 45 plasser. Kunnskapsfila om bygget følger nå kartdataene (1912/2016).
- **Nye tegninger (G1–G8):** bygget er tegnet som 58 × 25 m med 45 rom. BRA er 4 174,2 m², og tegningene, kartet og PDF-en er laget fra samme data. Ikke committet.
- **Maskinpark (MP1–MP8):** 37 maskiner, 4 MCP-verktøy (bare lesing og forslag) og skillen `maskinpark`. Serverrom og robotgarasje i U1. Ikke committet.
- **Gjort (MP9–MP12):** maskinlag i kartet, 6 øvingsscenarier med fasit (`get_drill_scenarios`), fasade sør/øst og snitt A–A/B–B. Committet 2026-11-22.
- **Neste:** nye bilder av Sal B, C og E og driftsrommene (krever ja til ekstern bildetjeneste), fasade nord/vest, situasjonsplan, rømningsplan, robotenes kjøreveier, eventuelt hvitelisting i Datafinner.
- **Neste:** nye bilder av Sal B, C og E og driftsrommene, og fasade-, snitt-, situasjons- og rømningstegninger.

## Gjort (2026-11-22): storskjermen for seks lederroller med KI-chat (DECISIONS SC1–SC21), committet
- Rollevalg i toppen: Direktør, Drift, HR, Økonomi, Publikum og Samling. Hver rolle har 3–4 tall med endring, status og kurve, og flater med underlag. Én flate vises om gangen og bytter selv hvert 12. sekund.
- KI-chat står fast til høyre (SC13), og forslagene følger rollen (SC20). Drift og HR-skuffen er fjernet og flyttet inn i rollene (SC19). `lag_storskjerm.py` skriver fire filer: side, `data.json`, `museum.db.gz.txt` og `chat-instruks.txt`.
- Endret: `deploy/claude-app/storskjerm.html`, `scripts/lag_storskjerm.py`, `src/kunstpixel/core/storskjerm.py`, ny `src/kunstpixel/core/storskjerm_roller.py`, `tests/test_storskjerm.py`, `tests/test_storskjerm_side.py`, ny `tests/test_storskjerm_chat.py`, ny `tests/test_storskjerm_roller.py`. Storskjermtestene: 98 bestått. Hele pytest: grønn.
- **Åpent for Lars:** statusgrensene (10 % og 25 % verre) er agentens valg (SC16).
- **Lenke (gjeldende):** https://claude.ai/artifact/59CjTmfETMo6evyza8Cbfx (privat, festet som «Kunstpixel i dag», SC21). Forrige lenke (PHo2…) er tatt ut av Festet, ikke slettet.
- **Lars:** åpne den i claude.ai og still ett spørsmål i chatten til høyre (første gang spør claude.ai om tillatelse). Se den på storskjermen. Bytt lenken i prosjektet Kunstpixel hvis den gamle står der.
- KI-chat-testkopien (4Gp2…) er tatt ut av Festet, ikke slettet. **Åpent:** specen fra 19.11 er ikke skrevet om.

## Gjort (2026-11-19): Storskjerm-dashbordet «Kunstpixel i dag» (DECISIONS D1–D8), committet
- Lenke: https://claude.ai/artifact/59CjTmfETMo6evyza8Cbfx (privat, se DECISIONS SC21). Den første lenken (SYi68…) er borte (SC7). Vis: Fullskjerm.
- Oppdater: `py -3.13 scripts/lag_storskjerm.py`, så publiserer Claude Code til samme lenke. Guide: «Storskjerm» i docs/GUIDE-claude-appen.md.
- **Lars:** se den på storskjermen én gang. Lim eventuelt lenken inn i prosjektet Kunstpixel.

## Gjort (2026-11-19): Kunstpixel-demo i Claude-appen (DECISIONS C1–C7), ikke committet
- Guide: [docs/GUIDE-claude-appen.md](docs/GUIDE-claude-appen.md). Pakken bygges med `py -3.13 scripts/lag_claude_skill.py`.
- **Lars:** last opp `.scratch/claude-app/kunstpixel-demo.zip` i claude.ai (Customize → Skills), lag prosjektet Kunstpixel-demo (guiden steg 4), og prøv én gang på mobil.
- Bygg pakken på nytt hver gang `museum.db` er bygget på nytt.

## Gjort (2026-11-18): Datafinner lettere å bruke (DECISIONS U1–U7), committet
- Lesbar Fasit og hjelpetekst, menyen blir stående, «Stengt» og ingen tomme dager i ukerapporten, søk i Tabeller, innlånsfrister skjult.
- Hele pytest: 2520 bestått, 9 hoppet over, 2 ventede feil. Sjekket i nettleseren på PC og mobil.
- **Åpent for Lars:** bekreft regelen for retur av innlån, så kan fristene vises igjen (U6).
- **Neste:** uavhengig gjennomgang med `.scratch/handoffs/REVIEW-2026-11-18-brukervennlighet.md`.

## Gjort (2026-11-17): Hjem i to faner og etappe 3b (DECISIONS H1–H9), committet (9087197)
- Hjem: fanene Oversikt og Chat. Oversikt viser bare det som krever oppmerksomhet, og resten ligger bak «Vis N andre tall».
- Handlingslinje med én eller to synlige knapper og resten under «Mer»: e-postutkast fra fast mal, «Meld avvik», «Følg opp» og «Spør KI». «Godta» erstatter avkrysningene. «Mine oppfølginger» har CSV-nedlasting, og de 3 nyeste står i huskelappen.
- Hele pytest: 2481 bestått.
- Skillen kunstpixel-data er rettet med tall-vakt (8f76c44), og K2 er lagret (d85af4e).
- **Neste:** etappe 4. D2 skal også rette de 17 vaktene med feil timer.

## Gjort (2026-11-16): Datafinner etappe 3a, «Mine frister» (DECISIONS F1–F6)
- «Mine frister» under «Følg opp» i menyen og som kort på Hjem: sykefravær uke 4/7 (HR og Avdelingsleder), driftsmeldinger og HMS-avvik åpne over 14 dager, rapportfrister, tilstandskontroll og retur av innlån. Gruppert Forfalt, I dag, Denne uka og Senere.
- «Fulgt opp» og «Angre» lagres i nettleseren. «Spør KI» tar fristen med til chatten. `get_condition_report` og `search_loans` er hvitelistet (B10). Hele pytest: 2426 bestått.
- Etappe 3b er ferdig (2026-11-17, se over).
- Åpent: tilstandskontroll hver 12. måned og innlån ved utstillingens slutt er forslag. Lars har ikke bekreftet dem.

## Gjort (2026-11-16): Datafinner etappe 1 (DECISIONS E1–E8)
- Hjem-knapp, brødsmuler, tilbake/frem, klikkbare rader, huskelapp til høyre, Søk/Arbeidsflyter//arena fjernet, rapportmaler og to verktøy rettet. Hele pytest: 2290 bestått.
- **Spec for etappe 2–4:** [docs/specs/datafinner-ledelse.md](docs/specs/datafinner-ledelse.md) (ready-for-agent, 🔒-oppgaver og åpne spørsmål Å1–Å4 venter på Lars).
- **Neste:** Lars prøver i nettleseren. Så etappe 2 («Driften denne uka»), etappe 3 (handlinger i nettleseren) og etappe 4 (datagenerator for kafévakter, ferdige spørsmål, personvern-casene).

## Gjort (2026-11-15): ren main (DECISIONS W1–W5)
- Driftsinnboksen, `museum.db`, hjelpeskriptene og dokumentene er committet. `AGENTS.md` er slått sammen (driftsregler + multiagent-lag). Hele pytest: 2254 bestått, 9 hoppet over, 2 ventede feil. `main` er pushet til GitHub.

## Krav nå (2026-11-15, detaljer i `.scratch/handoffs/HANDOFF-2026-11-15T1657.md`)
1. **K1. Prøverunde i en ny økt:** `start_claude.cmd`, spør om Stine Haugens personalmappe og Anja Eriksens stilling, og kjør `/sjekk` etter hvert svar.
2. **K2. Datahull:** demo-Claude (MCP) når ikke `dagsbesok` (6 209 rader), `hr_medarbeidersamtaler` (142) og `hr_innleide_kompetanse` (19). Lag tre lesende MCP-verktøy med TDD. Lars godkjenner først.
3. **K3.** Skal `.agents/` inn i git? Lars avgjør.
4. **K4.** Kjør én e-post gjennom multiagent-flyten (`handoffs/epost/README.md`).
5. **K5.** `design/startbilde`: flett, forkast eller la ligge. Lars avgjør.

## Gjort (2026-11-15): lekegrind for live-demo (DECISIONS L1–L12)
- Dobbeltklikk `start_claude.cmd`, og statusporten kjøres først. Still et fritt spørsmål, og skriv `/sjekk` etter svaret. Da finner en uavhengig kontrollør fasit med `scripts/sql_ro.py`.
- Neste: prøv flere frie spørsmål med `/sjekk` i en ny økt.

## Gjort (2026-11-06)
- `scripts/start_demo.ps1`: sjekker miljø og database, og åpner Datafinner. Kjørt og testet.
- `mcp` er låst til 1.29.1 i `pyproject.toml`.
- README har fått seksjonen «Start demoen». Beslutningene står i `docs/DECISIONS.md`.
- `.gitattributes` tvinger LF for CSV-filene og Colab-pakken. Hele pytest er grønn i en ny utsjekk.

- Datafinner i ett vindu ([spec](docs/specs/ett-vindu.md)): oppgave 02–08 er ferdige på `ux/ett-vindu`, og 08 ligger på `ux/ny-forside`. `/` er nå skallet med rapporter, Arena, Chat, Søk, Vaktrom og Arbeidsflyter. Oppgave 01 (Lars bygger `rolle_sporsmal`) og 09 (Lars velger samlingsrapporter) venter.

## Gjort (2026-11-09)
- Flyttet fra Drive. Alle Drive-grener er hentet inn som `drive/*`.
- `ux/ett-vindu` er slått inn i main.
- Det gamle museumsnavnet er byttet til Kunstpixel og `KP-` (DECISIONS punkt 10 og 10a, med vakttest). `museum.db` er bygget på nytt.
- Skjult datakatalog i rapportvinduet (`/api/katalog`).
- «Spør KI» som egen inngang øverst i menyen.
- Startkommandoen `start_demo.cmd` er kjørt og virker etter byttet.
- `.mcp.json`: din egen Claude får Kunstpixel-verktøyene via MCP (venter på godkjenning).
- Beslutningene står i `docs/DECISIONS.md`, punkt 1–12a.

## Neste (rekkefølge fra DECISIONS 2026-11-09)
0. Mål (DECISIONS 15): smoothe rapporter og en LLM som krysskobler data. Grunnlag: `docs/design/2026-11-09-designkritikk-datafinner.md`. Neste steg er å avklare hvordan.
1. Bruk «Spør KI» på nettsiden: start med skrivebordssnarveien (kjører `start_demo.cmd -KI`).
2. Lars godkjenner MCP-serveren `kunstpixel` i Claude Code (kjør `claude` i Kunstpixel-mappa og svar ja), og tester et spørsmål.
3. Valgfritt: koble samme server til Claude Desktop.
4. Senere: kart og leksjoner som faner, oppgave 09 (Lars velger rapporter), kopi av designsystemet, G:-stier i skriptene, slette Drive-kopien (bare etter Lars' ja).

## Neste (eldre, fra 2026-11-06)
1. Lars merger grenen `claude/kunstpixel-demo-database-fb3af9` til main.
2. Lars godkjenner taggen `demo-v1` og sjekker den ut i sin egen demomappe.
3. Senere: commit de 18 ventende endringene og lag `demo-v2`.
4. Test `-KI` når `.env` med nøkkel finnes. Den er ikke testet ennå.
