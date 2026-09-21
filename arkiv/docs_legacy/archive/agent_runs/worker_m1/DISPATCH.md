## 2026-09-14T15:15:03Z

<USER_REQUEST>
You are Worker 1 (worker_m1) for the Aura Kunstmuseum project.
Your working directory is: g:/Min disk/Fellesprosjekt KI/.agents/worker_m1
Authoritative original request path: g:/Min disk/Fellesprosjekt KI/.agents/ORIGINAL_REQUEST.md
You MUST read ORIGINAL_REQUEST.md first.

Project specification: g:/Min disk/Fellesprosjekt KI/PROJECT.md
Survey handoffs to read:
- g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_db/handoff.md (contains exact verified SQL queries, schema details, table structure)
- g:/Min disk/Fellesprosjekt KI/.agents/spec_miner_survey_context/handoff.md (contains tool signatures, schemas, security rules)
- g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_env/handoff.md (contains Python 3.13 setup, FastMCP examples, package versions)

Your exclusive write ownership:
- `pyproject.toml`
- `src/config.py`
- `src/db.py`
- `src/mcp_server.py`
- `src/__init__.py`
- `data/museum.db` (copy from C:\Users\larse\Documents\.headroom\memory.db)
DO NOT write or modify any files outside this ownership (specifically do NOT touch tests/, prompts/, or context/).

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your tasks for Milestone 1 (R1 - MCP Server):
1. Setup `pyproject.toml` configured with pytest settings (pythonpath = ["."]).
2. Copy `C:\Users\larse\Documents\.headroom\memory.db` to `data/museum.db` so the repo has a self-contained local copy, while keeping fallback logic in `src/config.py`.
3. Implement `src/config.py` to resolve DB path checking `AURA_DB_PATH`, `data/museum.db`, then `C:\Users\larse\Documents\.headroom\memory.db`.
4. Implement `src/db.py` with read-only SQLite connection (`sqlite3.Row`), parameterized queries, Norwegian character handling (normalization for FAQ: 'åpningstider' -> 'aapent' / 'åpen' to match "Naar har museet aapent?"), quoting `[rekkefølge]` in `utstilling_verk`.
5. Implement `src/mcp_server.py` using `from mcp.server.fastmcp import FastMCP`, registering the 5 collection tools:
   - `search_collection`: search by query, artist, title, technique, theme, room_id. Kittelsen returns >= 2 artworks.
   - `get_artwork_details`: complete metadata, wall text, provenance. Returns structured error on missing.
   - `get_room_artworks`: artworks in room in sequence order. SAL-D returns >= 3 artworks.
   - `search_events`: upcoming events filtered by type or date, returning date, times, room, prices.
   - `search_faq`: keyword-normalized search. 'åpningstider' returns concrete opening hours (10:00-17:00, etc.); prices in NOK.
6. Enforce read-only constraint: strictly NO write queries (INSERT, UPDATE, DELETE, ALTER, DROP) or arbitrary raw SQL.
7. Run verification commands using `py -3.13` to test direct tool calls and ensure all 5 tools return real, verified data from the database.
8. Document all verification commands and outputs in `g:/Min disk/Fellesprosjekt KI/.agents/worker_m1/handoff.md`.
9. Send completion message via send_message to orchestrator.
</USER_REQUEST>
