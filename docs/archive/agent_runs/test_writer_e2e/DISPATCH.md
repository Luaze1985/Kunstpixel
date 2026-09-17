## 2026-09-14T15:15:03Z

You are the E2E Test Writer (test_writer_e2e) for the Aura Kunstmuseum project.
Your working directory is: g:/Min disk/Fellesprosjekt KI/.agents/test_writer_e2e
Authoritative original request path: g:/Min disk/Fellesprosjekt KI/.agents/ORIGINAL_REQUEST.md
You MUST read ORIGINAL_REQUEST.md first.

Project specification: g:/Min disk/Fellesprosjekt KI/PROJECT.md
Survey handoffs to read:
- g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_db/handoff.md
- g:/Min disk/Fellesprosjekt KI/.agents/spec_miner_survey_context/handoff.md

Your exclusive write ownership:
- `TEST_INFRA.md`
- `tests/conftest.py`
- `tests/test_mcp_server.py`
- `tests/test_agent.py`
- `tests/test_integration.py`
- `tests/test_db_quality.py`
- `tests/__init__.py`
- `TEST_READY.md` (publish when test suite is complete)
DO NOT write or modify any files in `src/`, `data/`, `prompts/`, or `context/`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your tasks for the E2E Testing Track:
1. Create `TEST_INFRA.md` at project root documenting test methodology and coverage plan across Tiers 1-4.
2. Implement `tests/conftest.py` with pytest fixtures.
3. Implement `tests/test_mcp_server.py` verifying R1 acceptance criteria:
   - All 5 tools return correct, verifiable results from SQLite.
   - Search "Kittelsen" returns >= 2 artworks with metadata.
   - Room "SAL-D" returns >= 3 exhibited artworks in order.
   - Search events returns upcoming events with date and type.
   - Search FAQ for "åpningstider" returns concrete hours (10:00-17:00, etc.).
4. Implement `tests/test_agent.py` verifying R2 acceptance criteria:
   - Agent locates "Skrik" in Sal D.
   - Agent answers ticket prices from FAQ table in NOK.
   - Agent provides 30-minute highlights with currently exhibited artworks.
   - Agent never hallucinates facts/years not in DB.
   - Agent tone follows masterprompt style (friendly, concrete, non-academic).
5. Implement `tests/test_integration.py` verifying R3 acceptance criteria:
   - At least 8 distinct scenarios (>= 2 per category: samling, utstilling, hendelse, praktisk).
   - No empty answers or unhandled exceptions.
   - Verification that museumsvert agent cannot write to database.
6. Implement `tests/test_db_quality.py` verifying:
   - 72 rows across 7 tables.
   - Wall texts (veggtekst) follow quality rules (50-90 words, structured header).
7. Publish `TEST_READY.md` summarizing test counts and coverage across all tiers.
8. Document results and commands in `g:/Min disk/Fellesprosjekt KI/.agents/test_writer_e2e/handoff.md`.
9. Send completion message via send_message to orchestrator.
