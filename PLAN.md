# PLAN — status

**Aktiv plan:** [Demo-databasen med én startkommando](docs/plans/2026-11-06-demo-database.md)

## Gjort (2026-11-06)
- `scripts/start_demo.ps1`: sjekker miljø og database, og åpner Datafinner. Kjørt og testet.
- `mcp` er låst til 1.29.1 i `pyproject.toml`.
- README har fått seksjonen «Start demoen». Beslutningene står i `docs/DECISIONS.md`.
- `.gitattributes` tvinger LF for CSV-filene og Colab-pakken. Hele pytest er grønn i en ny utsjekk.

- Datafinner i ett vindu ([spec](docs/specs/ett-vindu.md)): oppgave 02–08 er ferdige på `ux/ett-vindu`, og 08 ligger på `ux/ny-forside`. `/` er nå skallet med rapporter, Arena, Chat, Søk, Vaktrom og Arbeidsflyter. Oppgave 01 (Lars bygger `rolle_sporsmal`) og 09 (Lars velger samlingsrapporter) venter.

## Neste
1. Lars merger grenen `claude/kunstpixel-demo-database-fb3af9` til main.
2. Lars godkjenner taggen `demo-v1` og sjekker den ut i sin egen demomappe.
3. Senere: commit de 18 ventende endringene og lag `demo-v2`.
4. Test `-KI` når `.env` med nøkkel finnes. Den er ikke testet ennå.
