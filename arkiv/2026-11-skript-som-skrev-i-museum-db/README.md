# Skript som skrev rett i museum.db

Flyttet hit 2026-11-10 (revisjonsfunn 9, `docs/plans/2026-11-10-revisjonsfunn.md`).

Disse fire skriptene åpnet `05_data/museum.db` og skrev direkte. Regelen er at databasen
bare bygges av `src/kunstpixel/data/build_museum_db.py` fra datafilene i `05_data/`.
Ingen kode, tester eller dokumenter viste til dem.

- `consolidate_museum_db.py`
- `enrich_category_c_hr.py`
- `enrich_from_snl.py` (henter fra snl.no)
- `generate_daily_visitors.py` (bruker pandas og numpy)

Ikke kjør dem mot `museum.db`. Trengs noe av logikken igjen, flyttes den inn i byggeskriptet.
