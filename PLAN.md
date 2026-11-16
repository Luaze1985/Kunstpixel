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
- **Neste:** etappe 3 (frister og handlinger). Trenger svar på Å1, Å2 og godkjente fristregler (B7) først.

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
