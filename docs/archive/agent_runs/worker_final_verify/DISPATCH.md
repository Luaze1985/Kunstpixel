## 2026-09-14T16:20:31Z

You are the QA Verification Worker for Aura Kunstmuseum demo-prototype.
Your working directory is: g:/Min disk/Fellesprosjekt KI/.agents/worker_final_verify

The authoritative original user request is at: g:/Min disk/Fellesprosjekt KI/.agents/ORIGINAL_REQUEST.md
You MUST read this file before starting work. Do not skip reading it.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Context:
Milestone 1 (R1: FastMCP collection server in src/mcp_server.py), Milestone 2 (R2: Interactive museumsvert agent in src/agent.py & src/cli.py), and Milestone 3 (R3: Integration test suite in tests/) are completed. Predecessor Gate 2 approved the remediation with 112 tests passing.

Your Task:
1. Verify the full test suite by running pytest:
   `py -3.13 -m pytest -v`
   Record the total number of tests passed and the execution time.
2. Execute the verification checks specified in `g:/Min disk/Fellesprosjekt KI/.agents/reviewer_remedy/handoff.md`:
   a. Honest `tools_used` tracking check:
      `py -3.13 -c "from src.agent import MuseumsvertAgent; a = MuseumsvertAgent(); r = a.handle_message('Hva anbefaler du hvis jeg har 30 minutter?'); print('Tools:', r.tools_used); assert r.tools_used == ['get_room_artworks']"`
   b. Dynamic pricing against mutated database:
      Run the tempfile DB mutation script that updates `publikum_faq` prices to 175 kr / 110 kr / 390 kr and asserts dynamic agent reflection.
   c. FAQ precision check:
      `py -3.13 -c "from src.db import query_faq; assert len(query_faq('se')) == 0 and len(query_faq('do')) == 0 and len(query_faq('er')) == 0; print('FAQ token precision verified!')"`
   d. CLI smoke test:
      Verify `py -3.13 -m src.cli --help` or test running CLI in a non-interactive/help mode.
3. Verify repository file layout matches `PROJECT.md` and `README.md`.
4. Run `git status` or inspect repository files to ensure no unexpected untracked artifacts or uncommitted changes break clean state.
5. Write your complete verification report to `g:/Min disk/Fellesprosjekt KI/.agents/worker_final_verify/handoff.md` following the standard 5-section handoff format:
   - Observation (exact commands, logs, test outputs)
   - Logic Chain
   - Caveats
   - Conclusion
   - Verification Method
6. When done, update your `progress.md` and send a completion message back to the orchestrator (parent).
