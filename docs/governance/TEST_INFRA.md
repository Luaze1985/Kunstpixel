# Test Infrastructure & Quality Assurance Specification: Aura Kunstmuseum

## 1. Executive Summary

This document formalizes the End-to-End (E2E) testing methodology, architectural test pyramid, fixture lifecycle, and coverage matrix for the **Aura Kunstmuseum Demo-Prototype**.

Aura Kunstmuseum is an operational synthetic SMB cultural institution serving as an AI-founder training arena. To verify that the enterprise is fully operational ("Bedriften virker"), the test infrastructure validates the complete stack:
1. **SQLite Database Layer** (72 records, 7 relational tables)
2. **FastMCP Collection Server** (5 domain tools, parameterized SQL, read-only security)
3. **Museumsvert Host Agent** (Masterprompt compliance, anti-hallucination guardrails, 4-step response synthesis)
4. **End-to-End Enterprise Integration** (Multi-scenario visitor workflows, permission boundaries)

---

## 2. Test Architecture: 4-Tier Pyramid

```
                       ┌───────────────────────────────┐
                       │   Tier 4: E2E Integration     │
                       │   `tests/test_integration.py`  │
                       │   (8+ scenarios, read-only    │
                       │    boundary, cross-workflow)  │
                       └───────────────┬───────────────┘
                                       │
                       ┌───────────────▼───────────────┐
                       │   Tier 3: Museumsvert Agent   │
                       │   `tests/test_agent.py`       │
                       │   (Intent, tone, anti-halluc- │
                       │    ination, recommendations)  │
                       └───────────────┬───────────────┘
                                       │
                       ┌───────────────▼───────────────┐
                       │   Tier 2: FastMCP Server      │
                       │   `tests/test_mcp_server.py`  │
                       │   (5 MCP tools, schema types, │
                       │    R1 criteria, SQL injection)│
                       └───────────────┬───────────────┘
                                       │
                       ┌───────────────▼───────────────┐
                       │   Tier 1: DB Quality & Schema │
                       │   `tests/test_db_quality.py`  │
                       │   (72 rows, 7 tables, FKs,    │
                       │    veggtekst 50-90 words)     │
                       └───────────────────────────────┘
```

### 2.1 Tier 1: Database Content & Quality Assurance (`tests/test_db_quality.py`)
- **Objective:** Verify physical data integrity, completeness, and curatorial standards before exposing data to MCP tools or agents.
- **Coverage:**
  - Table existence: Exactly 7 tables (`kunstnere`, `saler`, `verk`, `utstillinger`, `utstilling_verk`, `hendelser`, `publikum_faq`).
  - Baseline row counts: Exactly 72 rows total (12 artists, 6 rooms, 16 artworks, 3 exhibitions, 15 exhibition-artwork links, 8 events, 12 FAQs).
  - Referential integrity: All foreign keys resolve (`verk.kunstner_id -> kunstnere.id`, `verk.sal_id -> saler.id`, `utstilling_verk -> utstillinger & verk`, `hendelser.sal_id -> saler.id`).
  - Wall text (`veggtekst`) curatorial rule:
    - 14 exhibited works have approved wall text (`veggtekst_status = 'approved'`).
    - 2 magazine works have `veggtekst_status = 'draft'`.
    - Every approved wall text adheres to word count constraints (50–90 words, 49–60 verified) and 2-line header structure (`[Kunstner] ([år]–[år]), [nasjonalitet].` / `_[Tittel]_, [år]. [Teknikk], [dimensjoner]. [ID].`).
  - Enum constraints: Check valid values for `verk.status`, `verk.tilstand`, `hendelser.type`, `hendelser.status`, `utstillinger.status`.

### 2.2 Tier 2: MCP Server & Tool Verification (`tests/test_mcp_server.py`)
- **Objective:** Verify that all 5 FastMCP tools return genuine, structured, and verifiable data from SQLite meeting R1 acceptance criteria.
- **Coverage:**
  - `search_collection`:
    - Artist filter: "Kittelsen" returns >= 2 artworks with complete metadata.
    - Free text query, technique filter, room filter, theme filter.
    - Empty query handling and pagination limit.
    - Non-matching query returns `[]` without error.
  - `get_artwork_details`:
    - Valid ID lookup: `AURA-2026-009` ("Skrik") returns Edvard Munch, Sal D, wall text, provenance.
    - Invalid ID lookup: `AURA-2026-999` returns structured error `{"error": "Verk ikke funnet", "code": "NOT_FOUND"}`.
  - `get_room_artworks`:
    - Room `SAL-D` returns >= 3 exhibited artworks in display sequence order (`rekkefølge`).
    - Excludes non-exhibited works (e.g. magazine).
    - Unknown room handling.
  - `search_events`:
    - Returns upcoming events with date, start time, room, adult/child prices.
    - Filters by `event_type` (e.g. `omvisning`, `verksted`).
    - Excludes cancelled (`avlyst`) and past events.
  - `search_faq`:
    - Keyword search for "åpningstider" returns concrete hours (10:00–17:00).
    - Keyword search for "pris" / "koster" returns ticket prices in NOK.
    - Handles Norwegian vowel variations (`å` / `aa`, `ø` / `oe`).
  - Security & SQL Injection:
    - Tool inputs containing SQL injection syntax (e.g., `' OR '1'='1`, `'; DROP TABLE verk; --`) are safely handled as parameter values and never executed.

### 2.3 Tier 3: Museumsvert Agent Persona & Intelligence (`tests/test_agent.py`)
- **Objective:** Verify host agent persona, prompt adherence, tool invocation, and anti-hallucination guardrails meeting R2 acceptance criteria.
- **Coverage:**
  - Room localization: "Hvor finner jeg Skrik?" correctly routes to Sal D (2. etasje).
  - Price accuracy: "Hva koster det?" returns actual prices from FAQ in NOK (120 kr adult, 80 kr student, free under 16).
  - 30-minute highlights: "Hva anbefaler du hvis jeg har 30 minutter?" recommends only currently exhibited artworks (e.g. Munch in Sal D or Kittelsen/Sohlberg in Sal A), NEVER magazine artworks.
  - Anti-hallucination verification:
    - Never fabricates dates, artists, or artworks not present in SQLite.
    - Unknown artist inquiry ("Har dere Rembrandt?") honestly states work is not in collection.
    - Rejects undocumented interpretations; refers to approved wall text.
  - Tone & Style guardrails:
    - Friendly, welcoming, concrete host tone.
    - Strictly avoids "artspeak" and academic jargon (e.g. "interrogere", "subjektsposisjon", "romlig negasjon").
    - Avoids prohibited institutional terms (e.g. "galleri", "varelager", "helpdesk", "billettselger", "artifakt").
    - Adheres to 4-step response structure (Direct Answer, Narrative Detail, Practical Guidance, Additional Suggestion).

### 2.4 Tier 4: E2E Integration & Enterprise Persona Simulation (`tests/test_integration.py`)
- **Objective:** Verify that the full enterprise stack functions as a coherent, operational museum meeting R3 acceptance criteria.
- **Coverage:**
  - Minimum 8 distinct multi-turn / comprehensive operational scenarios across all 4 business categories (>= 2 per category):
    1. `samling`: Artist catalog inquiry ("Kittelsen i Sal A")
    2. `samling`: Artwork deep-dive with provenance ("Vinternatt i Rondane")
    3. `samling`: Masterwork discovery ("Hvor er Skrik?")
    4. `utstilling`: Room inventory review ("Hva henger i Sal D?")
    5. `utstilling`: Current exhibition overview ("Stille kraft")
    6. `hendelse`: Guided tour schedule & booking details ("Neste omvisning")
    7. `hendelse`: Family/children workshop inquiries ("Aktiviteter for barn")
    8. `praktisk`: Opening hours & weekend planning ("Åpningstider")
    9. `praktisk`: Ticket pricing calculation ("Pris for voksen og student")
    10. `praktisk`: Express visitor itinerary ("30 minutters anbefaling")
  - Zero-failure requirement: No scenario yields empty output, unhandled exceptions, or fallback crashes.
  - Least Privilege & Read-Only Enforcement:
    - Directly attempts `sqlite_write`, `INSERT INTO verk ...`, `DROP TABLE ...` through agent surface to verify strict rejection.
    - Verifies agent connection has no write permissions on database.

---

## 3. Authoritative Source of Expected Outputs

All test assertions derive expected values from authoritative project artifacts:
1. **SQLite Database (`memory.db` / `data/museum.db`)**: Ground truth for row counts, IDs, titles, artists, rooms, dates, prices.
2. **`CONTEXT.md`**: Ground truth for required vocabulary and forbidden terms (`AVOID`).
3. **`context/core/quality_rules.md`**: Ground truth for wall text length (50–90 words), header lines, and structure.
4. **`context/operations/tool_access.md`**: Ground truth for agent permissions (read-only, parameterized queries only).
5. **`prompts/museumsvert.md`**: Ground truth for tone, 4-step response model, and 30-minute highlights.

---

## 4. Test Execution & Environment

### 4.1 Runtime Requirements
- **Python:** Python 3.13 (`py -3.13`)
- **Test Runner:** `pytest 9.0.2`
- **Key Libraries:** `mcp`, `fastmcp`, `pydantic`, `sqlite3`

### 4.2 Standard Test Commands
```bash
# Run entire test suite across all 4 tiers
py -3.13 -m pytest -v

# Run specific tiers
py -3.13 -m pytest tests/test_db_quality.py -v       # Tier 1
py -3.13 -m pytest tests/test_mcp_server.py -v       # Tier 2
py -3.13 -m pytest tests/test_agent.py -v            # Tier 3
py -3.13 -m pytest tests/test_integration.py -v      # Tier 4

# Run with summary and short traceback
py -3.13 -m pytest --tb=short -ra
```
