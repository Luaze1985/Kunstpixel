# Project: Aura Kunstmuseum Demo-Prototype

## Architecture
Aura Kunstmuseum is an operational synthetic SMB cultural institution serving as an AI-founder training arena.
The software system consists of:
1. **Data Layer**: SQLite database (`memory.db` / `data/museum.db`) with 72 records across 7 tables (`kunstnere`, `saler`, `verk`, `utstillinger`, `utstilling_verk`, `hendelser`, `publikum_faq`).
2. **MCP Server (`src/mcp_server.py`)**: FastMCP-based Model Context Protocol server exposing 5 collection tools (`search_collection`, `get_artwork_details`, `get_room_artworks`, `search_events`, `search_faq`), strictly read-only and SQL-injection safe.
3. **Museumsvert Agent (`src/agent.py`, `src/cli.py`)**: Host agent connecting masterprompt (`prompts/museumsvert.md`) with MCP collection tools. Dual-engine architecture: deterministic facts engine (100% reproducible for pytest R3, zero tokens) and interactive CLI. Strict anti-hallucination, warm non-academic host tone.
4. **E2E Integration Test Suite (`tests/`)**: 4-tier test suite verifying that all MCP tools, the agent, and the whole museum enterprise function coherently ("Bedriften virker").

```
┌─────────────────────────────────────────────────────────────┐
│                    Museum Visitor / User                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ User questions / CLI
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Museumsvert Agent (`src/agent.py`)             │
│  - Prompts: `prompts/museumsvert.md`                        │
│  - Tone: Friendly, concrete, non-academic host             │
│  - Anti-hallucination: Only facts from database             │
│  - Dispatch: Intent classification & tool selection         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameterized tool calls (Read-only)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Aura MCP Server (`src/mcp_server.py`)            │
│  1. `search_collection`   2. `get_artwork_details`          │
│  3. `get_room_artworks`   4. `search_events`                │
│  5. `search_faq`                                            │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameterized SQL queries
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Database Helper (`src/db.py`)                   │
│  - Config precedence: `AURA_DB_PATH` -> local -> fallback   │
│  - Norwegian character handling & safe query execution      │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLite connection
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            SQLite Database (72 rows, 7 tables)              │
│  kunstnere, saler, verk, utstillinger,                      │
│  utstilling_verk, hendelser, publikum_faq                   │
└─────────────────────────────────────────────────────────────┘
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | DB Configuration & Local Mirror | Config loader with precedence (`AURA_DB_PATH` -> `data/museum.db` -> `C:\Users\larse\Documents\.headroom\memory.db`) | M1 (R1) | Survey DB & Env |
| 2 | DB Access Layer & Safe Queries | Parameterized query execution, column quoting (`[rekkefølge]`), Norwegian character normalization | M1 (R1) | Survey DB |
| 3 | Tool: `search_collection` | Search artworks by artist, title, technique, theme, room_id. Case-insensitive, partial matching. "Kittelsen" returns >= 2 | M1 (R1) | ORIGINAL_REQUEST R1 |
| 4 | Tool: `get_artwork_details` | Full metadata, curated wall text (50-90 words), and provenance for given `artwork_id`. 404 error on missing | M1 (R1) | ORIGINAL_REQUEST R1 |
| 5 | Tool: `get_room_artworks` | List exhibited artworks in room in order. "SAL-D" returns >= 3 works in order | M1 (R1) | ORIGINAL_REQUEST R1 |
| 6 | Tool: `search_events` | Upcoming events filtered by type or date, returning dates, times, room, prices | M1 (R1) | ORIGINAL_REQUEST R1 |
| 7 | Tool: `search_faq` | Keyword-normalized search for practical questions. "åpningstider" returns concrete hours; ticket prices in NOK | M1 (R1) | ORIGINAL_REQUEST R1 |
| 8 | Read-Only Security Enforcement | Absolute prohibition of write operations (INSERT, UPDATE, DELETE, ALTER, DROP) or raw SQL from agent surface | M1 (R1) | tool_access.md |
| 9 | Museumsvert System Prompt Loading | Load and enforce masterprompt from `prompts/museumsvert.md` | M2 (R2) | prompts/museumsvert.md |
| 10 | Museumsvert Response Engine | Intent classification, parameterized tool dispatch, 4-step answer formatting | M2 (R2) | workflows.md, prompt |
| 11 | Strict Anti-Hallucination | Never invent artist facts, dates, prices, or room locations not in database | M2 (R2) | values.md, prompt |
| 12 | 30-Minute Recommendation Logic | Recommend only currently exhibited artworks in open public galleries (Sal A or Sal D) | M2 (R2) | ORIGINAL_REQUEST R2 |
| 13 | Interactive CLI Host Loop | Rich terminal interface allowing interactive visitors to chat with Museumsvert | M2 (R2) | ORIGINAL_REQUEST R2 |
| 14 | E2E Test Suite (Tiers 1-4) | Comprehensive test suite with >= 8 scenarios across 4 categories (samling, utstilling, hendelse, praktisk) | M3 (R3) | ORIGINAL_REQUEST R3 |
| 15 | Database & Veggtekst Quality Audit | Automated checks for 72 rows, foreign key integrity, and wall text word count (50-90 words) | M3 (R3) | quality_rules.md |
| 16 | Adversarial Stress Testing | Negative test cases, prompt injection resistance, unknown IDs, edge queries | M3 (R3) | Acceptance criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | MCP Server (R1) | `src/config.py`, `src/db.py`, `src/mcp_server.py` exposing 5 collection tools with read-only safety | Survey complete | DONE (5 FastMCP tools verified live against SQLite) |
| M2 | Museumsvert Agent (R2) | `src/agent.py`, `src/cli.py` connecting masterprompt and MCP tools with tone and anti-hallucination rules | M1 | DONE (Dual engine, InProcessMCPClient, dynamic facts extraction) |
| M3 | E2E Integration Suite & Final Verification (R3) | `tests/` with Tiers 1-4 (8+ scenarios), DB quality checks, adversarial hardening, and `TEST_READY.md` | M1, M2 | DONE (112/112 tests pass, Gate passed) |

## Interface Contracts

### `src/config.py`
- `get_db_path() -> Path`: Resolves database path checking `AURA_DB_PATH` env var, `data/museum.db`, and `C:\Users\larse\Documents\.headroom\memory.db`.
- `ensure_local_db() -> Path`: Ensures local mirror exists for zero-dependency standalone execution.

### `src/db.py`
- `get_db_connection() -> sqlite3.Connection`: Returns read-only connection with `sqlite3.Row` row factory.
- Query helper functions mapping to the 5 tools:
  - `query_collection(query=None, artist=None, title=None, technique=None, theme=None, room_id=None, limit=10) -> list[dict]`
  - `query_artwork_details(artwork_id: str) -> dict | None`
  - `query_room_artworks(room_id: str) -> list[dict]`
  - `query_events(event_type=None, date_from=None, date_to=None, limit=5) -> list[dict]`
  - `query_faq(query: str, category=None) -> list[dict]`

### `src/mcp_server.py`
- FastMCP instance named `"Aura Kunstmuseum"`.
- Tools registered with `@mcp.tool()`:
  - `search_collection(query: str = None, artist: str = None, title: str = None, technique: str = None, theme: str = None, room_id: str = None, limit: int = 10) -> list[dict]`
  - `get_artwork_details(artwork_id: str) -> dict`
  - `get_room_artworks(room_id: str) -> list[dict]`
  - `search_events(event_type: str = None, date_from: str = None, date_to: str = None, limit: int = 5) -> list[dict]`
  - `search_faq(query: str, category: str = None) -> list[dict]`

### `src/agent.py`
- `class MuseumsvertAgent`:
  - `__init__(db_path: Path = None, mcp_client = None)`
  - `handle_message(user_message: str) -> AgentResponse`
  - `AgentResponse`: dataclass with `text: str`, `category: str`, `tools_used: list[str]`, `artworks_referenced: list[str]`, `rooms_referenced: list[str]`

### `tests/`
- Pytest suite invokable via `pytest` or `py -3.13 -m pytest`:
  - `tests/test_mcp_server.py`
  - `tests/test_agent.py`
  - `tests/test_integration.py`
  - `tests/test_db_quality.py`

## Code Layout
```
g:/Min disk/Fellesprosjekt KI/
├── pyproject.toml              # Pytest & package configuration
├── README.md                   # Setup, CLI usage, and test commands
├── data/
│   ├── samling.json            # Existing JSON mirror
│   └── museum.db               # SQLite database copy
├── src/
│   ├── __init__.py
│   ├── config.py               # DB path resolver and environment config
│   ├── db.py                   # SQLite access functions with parameterized queries
│   ├── mcp_server.py           # FastMCP server exposing the 5 collection tools
│   ├── agent.py                # Museumsvert agent (prompt + tool integration)
│   └── cli.py                  # Interactive terminal interface for visitors
└── tests/
    ├── __init__.py
    ├── conftest.py             # Shared fixtures (DB path, agent, mcp server)
    ├── test_mcp_server.py      # Acceptance tests for R1 (5 MCP tools)
    ├── test_agent.py           # Acceptance tests for R2 (Museumsvert behavior)
    ├── test_integration.py      # Acceptance tests for R3 (8+ scenarios)
    └── test_db_quality.py      # Database constraints & veggtekst word counts
```
