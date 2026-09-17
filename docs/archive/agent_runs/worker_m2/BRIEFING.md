# BRIEFING — 2026-09-14T17:21:00Z

## Mission
Implement Milestone 2 (R2 - Museumsvert Agent): genuine, robust deterministic & MCP-backed agent in src/agent.py, interactive CLI in src/cli.py, and complete README.md. Ensure all 65 tests in pytest suite pass.

## 🔒 My Identity
- Archetype: worker_m2
- Roles: implementer, qa, specialist
- Working directory: g:/Min disk/Fellesprosjekt KI/.agents/worker_m2
- Original parent: 7a113f74-d69a-4786-89b6-4115c75be748
- Milestone: M2 (R2 - Museumsvert Agent)

## 🔒 Key Constraints
- Exclusive write ownership: src/agent.py, src/cli.py, README.md (and files in .agents/worker_m2/).
- Strictly forbidden to modify files outside ownership: 	ests/, src/db.py, src/mcp_server.py, prompts/, context/.
- Integrity mandate: DO NOT hardcode test results, expected outputs, or create dummy facades. Implement real logic with real database queries.
- Strict read-only security: Agent cannot write to SQLite database or expose write tools.
- Strict anti-hallucination: Only report facts from DB; if unknown, explicitly state as unknown.
- Style rules: Friendly, enthusiastic host tone, zero artspeak, strictly avoid forbidden terms (galleri, varelager, helpdesk, etc.).

## Current Parent
- Conversation ID: 7a113f74-d69a-4786-89b6-4115c75be748
- Updated: 2026-09-14T17:21:00Z

## Task Summary
- **What to build**:
  1. src/agent.py: MuseumsvertAgent class and AgentResponse dataclass.
     - Masterprompt loading & enforcement (prompts/museumsvert.md).
     - Tool integration with the 5 MCP/DB query functions.
     - Dual-engine / deterministic intent classifier & response generator:
       - Categories: practical, collection, exhibition, events, recommendations.
       - 4-step answer format: 1. Direkte svar (fakta), 2. Visuell formidlingsdetalj, 3. Praktisk retning (sal/etasje), 4. Tilleggsforslag.
       - Strict anti-hallucination, 30-minute highlights (exhibited only, never MAG-1).
       - Read-only security (no write tools, read-only DB connection).
  2. src/cli.py: Interactive CLI host loop using ich with welcome banner and graceful exit.
  3. README.md: Architecture overview, quickstart, CLI usage, MCP running instructions, test commands.
- **Success criteria**: All 65 tests in py -3.13 -m pytest -v pass (Tiers 1-4).
- **Interface contracts**: PROJECT.md § Interface Contracts, 	ests/test_agent.py, 	ests/test_integration.py.
- **Code layout**: PROJECT.md § Code Layout.

## Key Decisions Made
- MuseumsvertAgent will provide both direct programmatic query invocation via src.db / src.mcp_server functions and optional MCP client connection.
- AgentResponse dataclass fields: 	ext: str, category: str, 	ools_used: list[str], rtworks_referenced: list[str], ooms_referenced: list[str].
- Intent classifier will deterministically inspect visitor queries for keywords, entities (artists, artwork titles, rooms, practical terms, event terms) and map to appropriate tools.
- Response synthesizer will follow the 4-step template strictly, populating visual details from wall text (eggtekst) or curated descriptions in the DB.

## Artifact Index
- src/agent.py — Museumsvert agent implementation
- src/cli.py — Interactive rich CLI interface
- README.md — Project documentation and quickstart
- .agents/worker_m2/handoff.md — Final verification report

## Change Tracker
- **Files modified**:
  - `src/agent.py`: Full implementation of `MuseumsvertAgent` and `AgentResponse`, read-only connection wrapper, masterprompt enforcement, 4-step answer format, intent router, anti-hallucination.
  - `src/cli.py`: Interactive terminal host loop built with `rich`, welcome banner, help room table, direct query execution, graceful exit.
  - `README.md`: Architecture overview, quickstart with `py -3.13`, tool documentation, security rules, test commands.
- **Build status**: 65 / 65 PASS across all Tiers 1-4.
- **Pending issues**: None.

## Quality Status
- **Build/test result**: 65 passed in 0.35s (100% pass rate).
- **Lint status**: Clean (compilation passed with 0 warnings).
- **Tests added/modified**: 0 (all 65 pre-existing tests in tests/ maintained unchanged).

## Loaded Skills
- None specified in dispatch
