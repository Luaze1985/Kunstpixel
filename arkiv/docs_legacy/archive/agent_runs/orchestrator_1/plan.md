# Master Execution Plan: Aura Kunstmuseum Demo-Prototype

## Overview
Build and verify an executable demo-prototype proving that the Aura Kunstmuseum synthetic SMB enterprise operates seamlessly:
1. R1: FastMCP / standard MCP server exposing 5 tools for SQLite museum data.
2. R2: Interactive museumsvert agent connecting masterprompt (`prompts/museumsvert.md`) with the MCP tools, adhering to domain rules and tone.
3. R3: Comprehensive integration test suite verifying that all 8+ scenarios pass and "Bedriften virker" as a coherent cultural institution.

## Execution Phases

### Phase 0: Survey & Specification Mining
- Spawn 3 parallel Explorers:
  - Explorer 1 (`survey_db`): Explore database location, schema, existing records, sample queries matching acceptance criteria (Kittelsen >= 2, Sal D >= 3, hendelser, FAQ åpningstider, veggtekster 50-90 words).
  - Explorer 2 (`survey_context`): Explore `CONTEXT.md`, `context/core/`, `context/roles/`, `context/operations/workflows.md`, `tool_access.md`, `prompts/museumsvert.md`. Map exact rules, permissions, formatting, tone.
  - Explorer 3 (`survey_env`): Explore Python/Node runtime environment, available packages (mcp, sqlite3, pytest, pydantic, etc.), workspace directory layout, existing files.
- Consolidate findings into `PROJECT.md`.

### Phase 1: Milestones
- **Milestone 1 (R1 - MCP Server)**:
  - 5 Collection tools:
    1. `samlingssok`: Search artworks by artist, title, technique, themes, or room.
    2. `verksdetaljer`: Retrieve full metadata for artwork (wall text, provenance).
    3. `salsoversikt`: List exhibited artworks in room in order.
    4. `arrangementssok`: Upcoming events filtered by type or date.
    5. `faq_oppslag`: Search audience FAQ.
  - Read-only enforcement (tool_access.md).
- **Milestone 2 (R2 - Museumsvert Agent)**:
  - Agent implementation using masterprompt `prompts/museumsvert.md`.
  - Tool integration via MCP / function calling.
  - Enforce style rules: friendly, concrete, non-academic, no hallucination.
- **Milestone 3 (R3 - E2E Integration Suite & Verification)**:
  - >= 8 diverse scenarios across samling, utstilling, hendelse, praktisk.
  - Verify acceptance criteria and quality rules.
  - Forensic audit & adversarial testing.

### Phase 2: Final Delivery & Reporting
- Final verification review.
- Report completion and results to Sentinel.
