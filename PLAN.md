# PLAN — status

**Aktiv plan:** [Demo-databasen med én startkommando](docs/plans/2026-11-06-demo-database.md)

**Pågår i `main`:** [Revisjonsfunnene](docs/plans/2026-11-10-revisjonsfunn.md), 17 funn fra ekstern gjennomgang.
- Pakke 1 er ferdig (2026-11-10): funn 6, 7, 9, 11, 13 og 14. Hele pytest: 2220 bestått, 9 hoppet over, 2 ventede feil. Også grønn i en ren utsjekk for de berørte testene.
- Pakke 2 er ferdig (2026-11-10): funn 3, 4 og 5. Colab-databasen og MintHCM-dumpen spores ikke lenger. Last opp de nye Colab-filene til Drive selv.
- Neste: pakke 3 (navn og merking), 4 (Datafinner-sperre) og 5 (innholdshash og dokumenter).
- Funn 2 (rolle fra klienten) er utsatt, og funn 16 (domene og telefon) gjøres ikke. Se `docs/DECISIONS.md`.

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
