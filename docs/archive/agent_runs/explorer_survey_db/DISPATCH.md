## 2026-09-14T15:04:20Z

You are an Explorer subagent for the Aura Kunstmuseum project.
Your working directory is: g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_db
Authoritative original request path: g:/Min disk/Fellesprosjekt KI/.agents/ORIGINAL_REQUEST.md
You MUST read ORIGINAL_REQUEST.md first.

Objective:
Investigate the SQLite database and data files for Aura Kunstmuseum demo-prototype.
Specifically:
1. Locate the SQLite database file in the workspace (check data/, root, etc.) and examine data/samling.json.
2. Inspect the SQLite database tables (schema, columns, types, row counts):
   - kunstnere
   - verk
   - saler
   - utstillinger
   - utstilling_verk
   - hendelser
   - publikum_faq
3. Test and document the exact SQL queries needed for the 5 MCP tools:
   - Samlingssøk: search by artist, title, technique, themes, or room. Check Kittelsen (must return >= 2 artworks with metadata).
   - Verksdetaljer: complete metadata for a specific artwork including wall text (veggtekst) and provenance.
   - Salsoversikt: list all exhibited works in a given room with order (check SAL-D - must return >= 3 artworks).
   - Arrangementssøk: upcoming events, filtered by type or date.
   - FAQ-oppslag: search FAQ (check åpningstider - must return concrete opening hours).
4. Verify data quality for Acceptance Criteria:
   - Check word count of veggtekster in the database (rule: 50-90 words, formatting).
   - Check that Skrik exists and its room is SAL-D.
   - Check ticket prices in FAQ table (Hva koster det?).
   - Check artworks for a 30-minute recommendation (Hva anbefaler du hvis jeg har 30 minutter?).

Scope boundaries:
- READ-ONLY! Do NOT write or modify any application code, tests, or database tables.
- Update your progress in g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_db/progress.md.

Output requirements:
- Write your comprehensive findings and verified SQL queries to g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_db/handoff.md.
- Send a completion message via send_message to the orchestrator.
