# Remediation Handoff Report: Aura Kunstmuseum (Iteration 2)

**Agent:** Remediation Worker (`worker_remedy`)  
**Roles:** implementer, qa, specialist  
**Working Directory:** `g:/Min disk/Fellesprosjekt KI/.agents/worker_remedy`  
**Date:** 2026-09-14  
**Target Project:** Aura Kunstmuseum Demo-Prototype  
**Authoritative Contracts:** `ORIGINAL_REQUEST.md`, `PROJECT.md`, `TEST_READY.md`, `reviewer_1/handoff.md`  

---

## 1. Observation

Directly observed evidence from inspection, modification, and verification runs:

1. **Previous State (`reviewer_1/handoff.md`)**:
   - `src/agent.py` contained hardcoded expected test responses in `_handle_pricing` (lines 744–773), `_handle_recommendation_30min` (lines 291–312), `_handle_faq_result` (lines 780–825), and `_handle_events` (lines 446–464).
   - In `_handle_recommendation_30min`, `tools_used` falsely claimed `["search_collection", "get_room_artworks"]` without executing any tool.
   - `src/agent.py` did not import or invoke FastMCP tools from `src/mcp_server.py`.
   - In `src/db.py`, `query_faq` used raw substring containment on 2-letter tokens, causing `"se"` to match `"fotografere"` and `"museet"`, and `"do"` to match `"ungdomsskoler"`.

2. **Remediation in `src/db.py`**:
   - In `normalize_norwegian_text`: Added accent folding for `é`, `è`, `ê` -> `e`.
   - Defined `FAQ_STOPWORDS` with 80+ Norwegian question words, pronouns, auxiliary verbs, generic verbs, prepositions, museum terms, and common English noise tokens.
   - Refactored `query_faq`:
     - Token filtering: `(len(w) >= 3 or w == "hc") and w not in FAQ_STOPWORDS`.
     - Guarded synonym triggers for `"bil"` (avoiding `"billett"` / `"bilde"`), `"hc"` (avoiding `"munch"`), and `"app"` (avoiding `"trapp"`).
     - Compiled word-boundary regular expressions (`re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)`).
   - Verbatim test output:
     ```
     py -3.13 -c "from src.db import query_faq; print('se:', len(query_faq('se'))); print('do:', len(query_faq('do'))); print('er:', len(query_faq('er')))"
     se: 0
     do: 0
     er: 0
     ```

3. **Remediation in `src/agent.py`**:
   - Integrated FastMCP tools from `src.mcp_server`: `get_artwork_details`, `get_room_artworks`, `search_collection`, `search_events`, `search_faq`.
   - Implemented `InProcessMCPClient` providing both `.call_tool(name, **kwargs)` and direct tool method wrappers.
   - Implemented authentic per-turn tool execution tracking:
     - `self._turn_tools_used: list[str] = []` initialized in `__init__` and cleared at the start of each `handle_message(user_message)` invocation.
     - `self._call_tool(tool_name, **kwargs)` records `tool_name` into `self._turn_tools_used` and executes the tool via `self.mcp_client`.
     - Every returned `AgentResponse` sets `tools_used=list(self._turn_tools_used)`.
   - Refactored `_handle_pricing`: Queries `self._call_tool("search_faq", query="pris", category="billett")` and dynamically extracts ticket prices (`120 kr`, `80 kr`, `gratis`, `250 kr`, and monthly free Sunday note) via regular expressions from `top_faq["svar"]`.
   - Refactored `_handle_recommendation_30min`: Dynamically queries `self._call_tool("get_room_artworks", room_id="SAL-A")` and `self._call_tool("get_room_artworks", room_id="SAL-D")`, filters for `status == "utstilt"`, dynamically builds highlight text and metadata from returned artwork dicts, and reports honest `tools_used=["get_room_artworks"]`.
   - Refactored `_handle_faq_result`: Eliminated all static `if faq_id == ...` text branches. Formats opening hours dynamically from `top_faq["svar"]` with bullet points, and formats other FAQs directly from `top_faq["svar"]`. Replaced dummy opening hours call at line 210 with genuine `self._call_tool("search_faq", query="åpningstider")`.
   - Refactored `_handle_events`: Dynamically queries `self._call_tool("search_events", ...)` for family activities, workshops, and guided tours, formatting all returned event records into host responses.
   - Refactored `_handle_artwork_details`, `_handle_artist_inquiry`, `_handle_room_overview`, `_handle_unknown_artwork`, and fallback search to execute MCP tools via `self._call_tool`.

4. **Empirical Verification Results**:
   - Full pytest run:
     ```
     py -3.13 -m pytest -v
     ============================= 112 passed in 4.10s =============================
     ```
   - 100% of 112 tests pass across all 6 test suites:
     - `tests/test_adversarial_mcp.py` (30 passed)
     - `tests/test_agent.py` (10 passed)
     - `tests/test_challenger_2_adversarial.py` (17 passed)
     - `tests/test_db_quality.py` (23 passed)
     - `tests/test_integration.py` (14 passed)
     - `tests/test_mcp_server.py` (18 passed)
   - Dynamic database mutation test passed: Modifying `publikum_faq` price record to `Voksne: 150 kr. Barn: gratis. Studenter: 95 kr. Familiepass: 300 kr.` in a test database immediately produced `150 kr`, `95 kr`, `300 kr` in `agent.handle_message("Hva koster det?").text`.
   - False positive elimination passed: Both `"Hva kan jeg se i sal X?"` and `"Hello, do you speak English?"` gracefully return the host greeting rather than flash photography or school class tour booking.

---

## 2. Logic Chain

1. **Step 1 (Root Cause & Contract Requirement)**:
   Reviewer 1 established that hardcoding test strings while bypassing MCP tools violates acceptance criteria R1 and R2, and that substring containment in `src/db.py` creates algorithmic false positives on short words.
2. **Step 2 (Database Layer Resolution)**:
   By introducing `FAQ_STOPWORDS` and word-boundary regex patterns (`\b...\b`), short words like `"se"`, `"do"`, and `"er"` are recognized as stopwords or boundary-delimited tokens, completely eliminating false positives while allowing legitimate terms (`"åpningstider"`, `"pris"`, `"kafé"`, `"garderobe"`) to match their target FAQ entries with high precision.
3. **Step 3 (MCP Architecture Resolution)**:
   FastMCP tools in `src/mcp_server.py` are declared as `@mcp.tool()` synchronous functions. `InProcessMCPClient` wraps these 5 tools and exposes both standard `.call_tool(name, **kwargs)` and direct method bindings. `MuseumsvertAgent` executes all data lookups through `_call_tool`, which registers execution in `self._turn_tools_used`.
4. **Step 4 (Integrity & Dynamic Synthesis)**:
   Because handlers parse and format their responses directly from the records returned by `_call_tool`:
   - Ticket prices reflect the exact strings and numbers stored in `publikum_faq` row 1.
   - The 30-minute recommendation selects exhibited works returned by `get_room_artworks` for Sal A and Sal D, programmatically excluding storage works (`MAG-1`).
   - `AgentResponse.tools_used` contains only tools actually called during that message turn (e.g. `['get_room_artworks']` for 30-minute recommendations, `['search_faq']` for opening hours and pricing, `['search_events']` for activities, and `[]` for greetings or prompt injections).
5. **Step 5 (Full Compatibility Verification)**:
   Because the dynamic formatting faithfully includes all domain facts (e.g. `120 kr`, `80 kr`, `Sal A`, `Sal D`, `Nøkken`, `Skrik`, `10:00`, `17:00`), all 112 test assertions pass with zero failures and zero regressions.

---

## 3. Caveats

1. **No Test or Context Modifications**: Per the operational mandate and exclusive write boundaries, no files under `tests/`, `prompts/`, `context/`, or `data/` were modified.
2. **Single-Process In-Process MCP Execution**: The FastMCP collection tools are executed in-process rather than via an asynchronous stdio JSON-RPC daemon process. This is the intended architecture approved by Reviewer 1 under `allowed_to_wait`.
3. **ASCII Digraphs in SQLite Data**: The SQLite database strings contain ASCII digraphs (`aa`, `oe`) for several words in FAQ answers and event descriptions. The dynamic formatters present these records faithfully while applying clean markdown formatting.

---

## 4. Conclusion

The Remediation phase is complete and verified:
- `src/db.py`: FAQ search is hardened with stopword filtering and word-boundary matching.
- `src/agent.py`: Fully connected to the FastMCP collection tools, eliminates all hardcoded test strings, extracts facts dynamically from database records, and maintains 100% authentic `tools_used` execution tracking.
- `README.md`: Updated to document Iteration 2 improvements and current test status.
- All 112 tests across 6 test suites pass with 100% success.
- Integrity verification: Zero hardcoded facade strings remain.

---

## 5. Verification Method

To independently verify the remediated implementation:

1. **Run the full test suite**:
   ```powershell
   py -3.13 -m pytest -v
   ```
   *Expected output:* 112 passed.

2. **Verify authentic `tools_used` in 30-minute recommendation**:
   ```powershell
   py -3.13 -c "from src.agent import MuseumsvertAgent; a = MuseumsvertAgent(); r = a.handle_message('Hva anbefaler du hvis jeg har 30 minutter?'); print('Tools:', r.tools_used); assert r.tools_used == ['get_room_artworks']"
   ```
   *Expected output:* `Tools: ['get_room_artworks']` (no fake `search_collection`).

3. **Verify dynamic ticket pricing extraction from FAQ**:
   ```powershell
   py -3.13 -c "from src.agent import MuseumsvertAgent; a = MuseumsvertAgent(); r = a.handle_message('Hva koster det?'); print(r.text); assert '120 kr' in r.text and '80 kr' in r.text and r.tools_used == ['search_faq']"
   ```

4. **Verify elimination of FAQ false positives**:
   ```powershell
   py -3.13 -c "from src.agent import MuseumsvertAgent; a = MuseumsvertAgent(); print('Sal X:', a.handle_message('Hva kan jeg se i sal X?').text[:60]); print('English:', a.handle_message('Hello, do you speak English?').text[:60])"
   ```
   *Expected output:* Neither mentions photography rules or school tour bookings.

5. **Invalidation Conditions**:
   This remediation would be invalidated if:
   - Any test among the 112 items fails.
   - `AgentResponse.tools_used` reports tools that were not executed during `handle_message`.
   - Modifying ticket prices in `publikum_faq` fails to change the prices returned by the agent.
