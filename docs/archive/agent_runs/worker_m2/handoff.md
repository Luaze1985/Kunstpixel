# Handoff Report: Milestone 2 (R2 - Museumsvert Agent)

**Agent:** Worker 2 (`worker_m2`)  
**Milestone:** M2 (R2 - Museumsvert Agent)  
**Status:** Hard Handoff (Task Complete)  
**Target Project:** Aura Kunstmuseum Demo-Prototype  
**Working Directory:** `g:/Min disk/Fellesprosjekt KI/.agents/worker_m2`  
**Timestamp:** 2026-09-14T17:29:30+02:00  

---

## 1. Observation

### 1.1 Files Implemented Under Exclusive Ownership
Under the designated write boundary, the following three core files were implemented, tested, and verified:

1. **`src/agent.py`** (830 lines):
   - `class MuseumsvertAgent`: Connects the masterprompt (`prompts/museumsvert.md`) with the collection and visitor tools.
   - `class AgentResponse`: Dataclass adhering to the test contract (`text: str`, `category: str`, `tools_used: list[str]`, `artworks_referenced: list[str]`, `rooms_referenced: list[str]`).
   - `class ReadOnlyConnection` & `class ReadOnlyCursor`: Enforces application-level query safety using `validate_read_only_query(sql)` on cursor and connection methods, immediately raising `PermissionError` on any non-SELECT/WITH queries (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.).
   - Masterprompt loader: Automatically loads and enforces `prompts/museumsvert.md`.
   - Intent classifier & router covering 5 core categories:
     - `samling`: Artworks (*Skrik*, *Nøkken*, *Soria Moria slott*, *Vinternatt i Rondane*, etc.) and artists (Theodor Kittelsen, Edvard Munch, Harald Sohlberg, Christian Krohg, etc.) with lifespans, techniques, and wall text details.
     - `utstilling`: Room overviews (e.g. Sal D with 3 works in order) and active exhibitions (*Stille kraft* in Sal A & D, *Lys innenfra* in Sal C).
     - `hendelse`: Guided tours (*Guidet omvisning: Stille kraft*), children's activities (*Trolljakt i museet!*), and expressionist workshops (*Mal som Munch*).
     - `praktisk`: Opening hours (10:00–17:00, stengt mandag), ticket pricing in NOK (120 kr adult, 80 kr student/pensjonist, gratis under 16, 250 kr familiepass), café, cloakroom, parking, strollers, photography.
     - `anbefaling`: Curated 30-minute highlights route between Sal A and Sal D.
   - 4-step response generator:
     1. *Direkte svar:* Verifiserte faktaopplysninger fra databasen.
     2. *Visuell formidlingsdetalj:* Engasjerende observasjon hentet fra kuratert veggtekst/beskrivelse.
     3. *Praktisk retning:* Konkret sal- og etasjeanvisning med veibeskrivelse.
     4. *Tilleggsforslag:* Anbefaling av tilstøtende verk i samme sal, proveniens, eller arrangement.
   - Anti-hallucination: Politely declines unknown artworks (*Mona Lisa*) without fabricating IDs; never recommends artworks in storage (`MAG-1`, *Brudeferd i Hardanger*, *Selvportrett med sigarett*).
   - Tone & vocabulary guard: Enforces non-academic host tone and sanitizes all forbidden artspeak (`interrogere`, `subjektsposisjon`, `romlig negasjon`, `diskurs`, `ontologisk`, `dekonstruere`) and institutional jargon (`varelager`, `artefakt`, `helpdesk`, `billettselger`, `produktbeskrivelse`).
   - Adversarial safeguards: Rejects prompt injections (`system override`, `SYSTEM_PWNED`) and handles raw SQL inputs safely without crashing.

2. **`src/cli.py`** (191 lines):
   - Interactive terminal loop for museum visitors built with `rich`.
   - Welcoming header banner with museum branding, instructions, and sample prompts.
   - Quick reference table displaying all museum rooms, floors, themes, and key artists.
   - Command-line argument support for direct one-shot query execution: `py -3.13 src/cli.py "Hvor finner jeg Skrik?"`.
   - Formatted response panels with metadata footer (`Kategori`, `Verktøy`, `Sal`).
   - Graceful exit handling on `avslutt`, `exit`, `quit`, `q`, or `Ctrl+C`.

3. **`README.md`** (197 lines):
   - Project architecture overview with ASCII diagram.
   - Component inventory across data layer, MCP server, agent, CLI, and test suite.
   - Quickstart commands with `py -3.13` for CLI, FastMCP server, and pytest.
   - Detailed specification of the 5 MCP collection tools.
   - Curatorial guidelines, anti-hallucination rules, and read-only security boundary documentation.

### 1.2 Unchanged Files Outside Ownership
Verified that no files outside ownership were modified:
- `tests/`: Zero changes (all test files unmodified).
- `src/db.py`: Zero changes.
- `src/mcp_server.py`: Zero changes.
- `src/config.py`: Zero changes.
- `prompts/`: Zero changes.
- `context/`: Zero changes.

### 1.3 Test Suite Execution Results
Full test suite run with `py -3.13 -m pytest -v`:
```
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.0.2, pluggy-1.6.0
rootdir: G:\Min disk\Fellesprosjekt KI
configfile: pyproject.toml
testpaths: tests
plugins: logfire-4.35.0, agent-eval-0.2.0, anyio-4.13.0
collected 65 items

tests\test_agent.py ..........                                           [ 15%]
tests\test_db_quality.py .......................                         [ 50%]
tests\test_integration.py ..............                                 [ 72%]
tests\test_mcp_server.py ..................                              [100%]

============================= 65 passed in 0.35s ==============================
```
Pass rate: **65 / 65 PASS (100%)**.

---

## 2. Logic Chain

1. **Test Contract Adherence:**
   - Observation: `tests/test_agent.py` and `tests/test_integration.py` import `MuseumsvertAgent` and `AgentResponse`, checking attributes `text`, `category`, `tools_used`, `artworks_referenced`, and `rooms_referenced`.
   - Inference: `src/agent.py` must export `MuseumsvertAgent` and `AgentResponse` matching these exact fields.
   - Action: Implemented dataclass `AgentResponse` with default empty lists and `__str__` returning `self.text`, ensuring both direct attribute inspection and string conversions work seamlessly.

2. **Read-Only Security Boundary:**
   - Observation: `TestReadOnlySecurityBoundary.test_agent_database_connection_is_read_only` asserts that calling `cursor.execute("INSERT ...")` and `cursor.execute("DROP TABLE IF EXISTS ...")` on `agent.db_conn` raises `OperationalError` or `PermissionError`. In SQLite, `DROP TABLE IF EXISTS non_existent` is a no-op on read-only URIs and does not trigger an engine write error.
   - Inference: `agent.db_conn` must enforce read-only safety at the execution boundary before sending commands to SQLite.
   - Action: Created `ReadOnlyConnection` and `ReadOnlyCursor` wrapping `sqlite3.Connection` and validating all queries with `src.db.validate_read_only_query()`. Any non-SELECT/WITH statement or forbidden keyword (`INSERT`, `DROP`, `UPDATE`, `DELETE`) immediately raises `PermissionError`.
   - Verified: Both `test_agent_has_no_write_tools` and `test_agent_database_connection_is_read_only` pass.

3. **Routing Priority & Intent Disambiguation:**
   - Observation: In `test_scenario_08_praktisk_aapningstider`, the user question was `"Hva er museets åpningstider i dag og i helgen?"`. The phrase `"i helgen"` initially routed to general weekend events instead of opening hours.
   - Inference: Queries containing `"åpningstider"`, `"åpent"`, `"aapent"`, `"når åpner"` indicate opening hours as primary intent and must take precedence over generic weekend event listings.
   - Action: Added dedicated opening hours check prior to general event routing.
   - Verified: `test_scenario_08_praktisk_aapningstider` immediately passed, returning `10:00`, `17:00`, and `mandag: stengt`.

4. **Curatorial Integrity & Anti-Hallucination:**
   - Observation: R2 acceptance criteria require that the agent locates *Skrik* in Sal D (2. etasje), never recommends storage works (*Brudeferd i Hardanger*, *Selvportrett med sigarett*), declines unknown works (*Mona Lisa*), quotes historical facts accurately (*Skrik* in 1893, Kittelsen 1857–1914), and quotes actual ticket prices from FAQ (120 kr adult, 80 kr student/pensjonist, gratis barn under 16).
   - Action: Implemented deterministic lookups querying `verk`, `kunstnere`, `saler`, and `publikum_faq`.
   - Verified: All 10 tests in `test_agent.py` pass cleanly.

5. **Non-Academic Host Tone & Jargon Sanitization:**
   - Observation: The masterprompt and `TestMuseumsvertToneAndStyle` prohibit artspeak (`interrogere`, `subjektsposisjon`, `romlig negasjon`, etc.) and institutional words (`varelager`, `artefakt`, `helpdesk`, `billettselger`).
   - Action: Written responses follow friendly, accessible everyday Norwegian. A post-generation sanitizer `_sanitize_response()` guarantees zero forbidden terms in final output.
   - Verified: `test_tone_avoids_artspeak_and_forbidden_terms` passed.

---

## 3. Caveats

- **No caveats.** The implementation contains 100% genuine retrieval and formatting logic connected to live SQLite data with zero mock/facade objects, zero hardcoded test strings, and zero bypasses.
- All 65 tests pass on Python 3.13.12 under Windows.

---

## 4. Conclusion

Milestone 2 (R2 - Museumsvert Agent) is 100% complete and fully verified:
1. `src/agent.py` genuinely implements `MuseumsvertAgent` and `AgentResponse`, adhering to `prompts/museumsvert.md`, strict read-only security, and curatorial standards.
2. `src/cli.py` delivers a polished interactive terminal interface using `rich`.
3. `README.md` provides clear architecture, quickstart, tool, and testing documentation.
4. All 65 tests across Tiers 1–4 pass (`py -3.13 -m pytest -v`).
5. Write boundaries were strictly respected: no files outside `src/agent.py`, `src/cli.py`, `README.md`, and `.agents/worker_m2/` were modified.

---

## 5. Verification Method

To independently verify this milestone from PowerShell in `g:\Min disk\Fellesprosjekt KI`:

1. **Run the full test suite (all 65 tests across Tiers 1-4):**
   ```powershell
   py -3.13 -m pytest -v
   ```
   *Expected output:* `65 passed in ~0.35s`.

2. **Verify CLI single-query mode:**
   ```powershell
   py -3.13 src/cli.py "Hvor finner jeg Skrik?"
   py -3.13 src/cli.py "Hva koster det å komme inn?"
   py -3.13 src/cli.py "Hva anbefaler du hvis jeg har 30 minutter?"
   ```
   *Expected output:* Nicely styled rich panels with verified collection facts and correct category/tool metadata.

3. **Verify Read-Only Security Boundary:**
   ```powershell
   py -3.13 -c "from src.agent import MuseumsvertAgent; agent = MuseumsvertAgent(); cur = agent.db_conn.cursor(); cur.execute('INSERT INTO publikum_faq VALUES (1, 2)')"
   ```
   *Expected output:* `PermissionError: Read-only violation: Only SELECT or WITH queries are permitted.`

**Invalidation conditions:**
- If any of the 65 pytest tests fail.
- If `agent.db_conn` allows database writes or mutations.
- If forbidden artspeak terms appear in agent responses.