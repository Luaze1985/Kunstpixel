# PLAN — status

**Aktiv plan:** [Demo-databasen med én startkommando](docs/plans/2026-11-06-demo-database.md)

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
- Beslutningene står i `docs/DECISIONS.md`, punkt 1–12a.

## Neste (rekkefølge fra DECISIONS 2026-11-09)
1. Én startkommando.
2. Test «Spør KI» med ekte nøkkel (koster noen øre).
3. Senere: kart og leksjoner som faner, oppgave 09 (Lars velger rapporter), kopi av designsystemet, G:-stier i skriptene, slette Drive-kopien (bare etter Lars' ja).

## Neste (eldre, fra 2026-11-06)
1. Lars merger grenen `claude/kunstpixel-demo-database-fb3af9` til main.
2. Lars godkjenner taggen `demo-v1` og sjekker den ut i sin egen demomappe.
3. Senere: commit de 18 ventende endringene og lag `demo-v2`.
4. Test `-KI` når `.env` med nøkkel finnes. Den er ikke testet ennå.
