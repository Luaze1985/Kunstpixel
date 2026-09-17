# BRIEFING — 2026-09-14T17:18:00+02:00

## Mission
Implement Milestone 1 (R1 - MCP Server) for Aura Kunstmuseum: setup configuration, read-only DB access layer, FastMCP server with 5 collection tools, copy database, and verify against real SQLite database.

## 🔒 My Identity
- Archetype: worker_m1
- Roles: implementer, qa, specialist
- Working directory: g:/Min disk/Fellesprosjekt KI/.agents/worker_m1
- Original parent: 7a113f74-d69a-4786-89b6-4115c75be748
- Milestone: M1 (R1 - MCP Server)

## 🔒 Key Constraints
- Exclusive write ownership: pyproject.toml, src/config.py, src/db.py, src/mcp_server.py, src/__init__.py, data/museum.db
- DO NOT write or modify files outside ownership (no touching tests/, prompts/, context/).
- MANDATORY INTEGRITY MANDATE: Genuine implementations only. No hardcoded outputs, no facades.
- Python 3.13 (`py -3.13`) environment.
- Read-only SQLite queries only: no INSERT, UPDATE, DELETE, ALTER, DROP, or arbitrary SQL execution.
- Quoting `[rekkefølge]` in `utstilling_verk` queries.
- Norwegian normalization for FAQ search.

## Current Parent
- Conversation ID: 7a113f74-d69a-4786-89b6-4115c75be748
- Updated: 2026-09-14T17:18:00+02:00

## Task Summary
- **What to build**:
  1. `pyproject.toml` with pytest settings (`pythonpath = ["."]`)
  2. `data/museum.db` copied from `C:\Users\larse\Documents\.headroom\memory.db`
  3. `src/__init__.py`
  4. `src/config.py`: DB path resolution (`AURA_DB_PATH` -> `data/museum.db` -> fallback `C:\Users\larse\Documents\.headroom\memory.db`)
  5. `src/db.py`: Read-only connection, dict-like rows, parameterized queries, Norwegian char normalization, sequence ordering
  6. `src/mcp_server.py`: FastMCP server registering 5 collection tools (`search_collection`, `get_artwork_details`, `get_room_artworks`, `search_events`, `search_faq`)
- **Success criteria**:
  - `search_collection`: Kittelsen returns >= 2 artworks (verified: 2 returned)
  - `get_artwork_details`: complete metadata, wall text, provenance; structured error on missing (verified: Skrik 54 words, provenance, error on AURA-2026-999)
  - `get_room_artworks`: artworks in room in sequence order; SAL-D returns >= 3 artworks (verified: 3 returned in sequence)
  - `search_events`: upcoming events filtered by type/date (verified: 5 upcoming events returned)
  - `search_faq`: 'åpningstider' returns concrete opening hours (10:00-17:00, etc.); prices in NOK (verified: 10:00-17:00 and 120 kr returned)
  - Pytest test suite: 41 of 41 tests passed in 0.20s

## Change Tracker
- **Files modified**:
  - `pyproject.toml`: Pytest configuration with pythonpath = ["."]
  - `data/museum.db`: Copied exact 72-row SQLite database
  - `src/__init__.py`: Package init
  - `src/config.py`: Database path resolution logic
  - `src/db.py`: Database helper layer with parameterized queries, normalization, read-only enforcement
  - `src/mcp_server.py`: FastMCP server exposing 5 tools
- **Build status**: PASS (41 of 41 tests passing)
- **Pending issues**: None

## Quality Status
- **Build/test result**: PASS (41 passed, 0 failed)
- **Lint status**: Clean (`py_compile` succeeded with 0 errors)
- **Tests added/modified**: Verified against `tests/test_mcp_server.py` and `tests/test_db_quality.py`

## Loaded Skills
None

## Key Decisions Made
- Used SQLite URI `?mode=ro` to enforce read-only access at the engine level in addition to application-level keyword validation.
- Implemented synonym expansion and character normalization (`å` <-> `aa`, `æ` <-> `ae`, `ø` <-> `oe`) for visitor FAQ queries so that 'åpningstider' reliably maps to 'Naar har museet aapent?'.
- Wrapped column name `[rekkefølge]` in square brackets in SQL queries to prevent encoding and parsing issues with the Norwegian letter `ø`.

## Artifact Index
- `g:/Min disk/Fellesprosjekt KI/.agents/worker_m1/handoff.md` — Final handoff report
