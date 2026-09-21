# Handoff Report: Milestone 1 (R1 - MCP Server)

**Agent:** Worker 1 (`worker_m1`)  
**Milestone:** M1 (R1 - MCP Server)  
**Status:** Hard Handoff (Task Complete)  
**Target Project:** Aura Kunstmuseum Demo-Prototype  
**Working Directory:** `g:/Min disk/Fellesprosjekt KI/.agents/worker_m1`  
**Timestamp:** 2026-09-14T17:19:00+02:00  

---

## 1. Observation

### 1.1 Files Created Under Exclusive Ownership
Under the designated write boundary, the following files were implemented and verified:

1. **`pyproject.toml`** (24 lines):
   - Configured with `[project]` metadata and `requires-python = ">=3.13"`.
   - `[tool.pytest.ini_options]` with `pythonpath = ["."]`, `testpaths = ["tests"]`, and `addopts = "-ra -q"`.

2. **`data/museum.db`** (77,824 bytes):
   - Copied from `C:\Users\larse\Documents\.headroom\memory.db`.
   - Verified row counts across 7 tables:
     - `kunstnere`: 12 rows
     - `saler`: 6 rows
     - `verk`: 16 rows
     - `utstillinger`: 3 rows
     - `utstilling_verk`: 15 rows
     - `hendelser`: 8 rows
     - `publikum_faq`: 12 rows
     - Total: exactly 72 rows.

3. **`src/__init__.py`** (1 line):
   - Initializes `src` package.

4. **`src/config.py`** (52 lines):
   - Implements `get_db_path() -> Path` resolving with precedence:
     1. `os.environ.get("AURA_DB_PATH")`
     2. Local repository copy `data/museum.db`
     3. External fallback `C:\Users\larse\Documents\.headroom\memory.db`
   - Implements `ensure_local_db() -> Path` which copies from fallback if missing.
   - Exports `DB_PATH: Path`.

5. **`src/db.py`** (338 lines):
   - `get_db_connection(db_path=None) -> sqlite3.Connection`: Connects using `file:{path}?mode=ro` with `uri=True` and `conn.row_factory = sqlite3.Row`.
   - `validate_read_only_query(sql: str)`: Enforces that queries start with `SELECT` or `WITH`, and prohibits `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `REPLACE`, `ATTACH`, `DETACH`, `PRAGMA`, `VACUUM`, `REINDEX`.
   - `execute_read_query(sql, params, db_path)`: Thread-safe, closes connection after execution.
   - Normalization helpers:
     - `normalize_room_identifier(room_id)`: Handles `Sal D`, `sal-d`, `SAL-D`, `D` -> `SAL-D`.
     - `normalize_norwegian_text(text)`: Normalizes `å` <-> `aa`, `æ` <-> `ae`, `ø` <-> `oe`.
   - 5 query helpers:
     - `query_collection`: Parameterized search on `query`, `artist`, `title`, `technique`, `theme`, `room_id`, `limit`.
     - `query_artwork_details`: Full metadata lookup by ID or title, computing `veggtekst_ordantall`, `kunstner_levetid`, and querying `[rekkefølge]` with column quoting.
     - `query_room_artworks`: Retrieves all exhibited artworks in room in order (`rekkefoelge ASC, v.aar ASC`).
     - `query_events`: Upcoming events filtered by `event_type`, `date_from` (defaults to `date('now')`), `date_to`.
     - `query_faq`: Keyword-normalized search with domain-specific synonym expansions for opening hours (`åpningstider` -> `aapent`, `åpen`, `tid`, `tider`), ticket prices (`koster`, `pris`, `billett`, `kr`), etc.

6. **`src/mcp_server.py`** (127 lines):
   - `from mcp.server.fastmcp import FastMCP`
   - `mcp = FastMCP("Aura Kunstmuseum")`
   - Exposes the 5 registered tools via `@mcp.tool()`:
     - `search_collection(...) -> list[dict[str, Any]]`
     - `get_artwork_details(artwork_id: str) -> dict[str, Any]` (returns `{"error": ..., "code": "NOT_FOUND"}` on missing)
     - `get_room_artworks(room_id: str) -> list[dict[str, Any]] | dict[str, Any]` (returns `{"error": ..., "code": "INVALID_ROOM"}` on invalid room)
     - `search_events(...) -> list[dict[str, Any]]`
     - `search_faq(...) -> list[dict[str, Any]]`
   - Standard entrypoint: `if __name__ == "__main__": mcp.run()`.

### 1.2 Direct Verification Tool Commands and Outputs
1. **Compilation Check (`py_compile`):**
   ```
   Command: py -3.13 -m py_compile src\__init__.py src\config.py src\db.py src\mcp_server.py
   Exit code: 0
   Output: (clean, zero warnings)
   ```

2. **Direct FastMCP Tool Call Execution:**
   ```
   Command: py -3.13 (test script invoking mcp_server tools directly)
   Output:
   - Registered tools (5): ['search_collection', 'get_artwork_details', 'get_room_artworks', 'search_events', 'search_faq']
   - Kittelsen count: 2 (AURA-2026-002: Soria Moria slott, AURA-2026-001: Nøkken)
   - Skrik details: Edvard Munch, Sal SAL-D, Veggtekst ordantall: 54, Proveniens: present
   - Missing artwork AURA-2026-999: {'error': "Verk med ID eller tittel 'AURA-2026-999' ble ikke funnet i samlingsdatabasen.", 'artwork_id': 'AURA-2026-999', 'code': 'NOT_FOUND'}
   - SAL-D artworks count: 3 (Rekkefoelge 5: Skrik, Rekkefoelge 6: Pikene på broen, Rekkefoelge 7: N. 7 – Stor blå fjellform)
   - Invalid room SAL-XYZ: {'error': "Ukjent sal-ID 'SAL-XYZ'", 'valid_rooms': ['SAL-A', 'SAL-B', 'SAL-C', 'SAL-D', 'SAL-E', 'MAG-1'], 'code': 'INVALID_ROOM'}
   - Upcoming events count: 5 (Guidet omvisning, Trolljakt, Mal som Munch, Kveldskafeen)
   - FAQ 'åpningstider': Top answer: 'Tirsdag–fredag: 10:00–17:00. Loerdag–soendag: 11:00–16:00. Mandag: stengt.'
   - FAQ 'Hva koster det?': Top answer: 'Voksne: 120 kr. Barn under 16 aar: gratis. Studenter og pensjonister: 80 kr...'
   - Security test: INSERT attempt blocked with PermissionError.
   ```

3. **Full Pytest Suite Run:**
   ```
   Command: py -3.13 -m pytest -v
   Output:
   tests\test_db_quality.py .......................                         [ 56%]
   tests\test_mcp_server.py ..................                              [100%]
   ============================= 41 passed in 0.20s ==============================
   ```

---

## 2. Logic Chain

1. **Self-Contained Portability:**
   - Observation: `C:\Users\larse\Documents\.headroom\memory.db` was external to the repo.
   - Inference: Moving or cloning the repository elsewhere would break without a local database.
   - Action: Copied database to `data/museum.db` and implemented a 3-tier precedence in `src/config.py` (`AURA_DB_PATH` -> local `data/museum.db` -> external `memory.db`).
   - Verified: Both `data/museum.db` and external fallback contain exactly 72 rows.

2. **Security & Read-Only Enforcement:**
   - Observation: Context rules (`context/operations/tool_access.md`) mandate strict read-only access with zero raw SQL execution.
   - Action: Enforced at two independent defense-in-depth layers:
     a) SQLite engine level: opened via URI `?mode=ro`.
     b) Application level: `validate_read_only_query()` blocks any non-SELECT/WITH statements and rejects write keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.).
   - Verified: Write attempts raise `PermissionError` and `sqlite3.OperationalError: attempt to write a readonly database`.

3. **Norwegian Linguistic and Schema Quirks:**
   - Observation: Table `utstilling_verk` has column `rekkefølge` with Norwegian character `ø`.
   - Action: Column name quoted as `[rekkefølge]` in all SQL queries.
   - Observation: FAQ question 2 is stored as `"Naar har museet aapent?"` using `aa` and `aapent` without the word `åpningstider`.
   - Action: `query_faq` normalizes `å` <-> `aa`, `æ` <-> `ae`, `ø` <-> `oe` and applies domain synonym expansion so that `åpningstider` reliably scores row 2 highest.
   - Verified: `search_faq("åpningstider")` returns concrete opening hours (10:00–17:00).

4. **FastMCP Tool Usability for Downstream Agents:**
   - Observation: FastMCP tools registered with `@mcp.tool()` are standard Python functions that can be called synchronously in unit tests and agent engines.
   - Action: Direct calls in `src/mcp_server.py` return clean Python dicts and lists, while providing JSON-RPC schemas automatically.
   - Verified: All 41 unit and contract tests in `test_mcp_server.py` and `test_db_quality.py` pass immediately.

---

## 3. Caveats

- **No Caveats:** All required features and edge cases (case insensitivity, partial matches, ordering, error payloads, read-only boundaries) have been genuinely implemented and tested with 0 mock/facade objects against live SQLite data.
- Note on file boundaries: Worker 1 strictly adhered to its assigned files (`pyproject.toml`, `src/config.py`, `src/db.py`, `src/mcp_server.py`, `src/__init__.py`, `data/museum.db`). Files in `tests/`, `prompts/`, and `context/` were not modified.

---

## 4. Conclusion

Milestone 1 (R1 - MCP Server) is 100% complete and fully verified:
1. `pyproject.toml` correctly configures pytest with `pythonpath = ["."]`.
2. `data/museum.db` contains verified 72 rows.
3. `src/config.py` seamlessly resolves database paths.
4. `src/db.py` provides read-only, injection-safe access with Norwegian character normalization and quoting `[rekkefølge]`.
5. `src/mcp_server.py` exposes the 5 collection tools with exact schemas and behavior:
   - `search_collection`: "Kittelsen" returns 2 artworks with metadata.
   - `get_artwork_details`: "Skrik" returns full metadata, 54-word wall text, provenance; unknown IDs return structured `NOT_FOUND` error.
   - `get_room_artworks`: "SAL-D" returns 3 exhibited artworks in sequence order.
   - `search_events`: returns upcoming events with date, times, room, prices in NOK.
   - `search_faq`: "åpningstider" returns concrete hours (10:00–17:00), ticket query returns prices in NOK.
6. The test suite (`pytest -v`) passes with 41/41 passing tests.

---

## 5. Verification Method

To independently verify this milestone, run the following commands in PowerShell from `g:\Min disk\Fellesprosjekt KI`:

1. **Run full pytest test suite:**
   ```powershell
   py -3.13 -m pytest -v
   ```
   *Expected output:* `41 passed in < 1s`.

2. **Verify 5 tools directly with Python 3.13:**
   ```powershell
   py -3.13 -c "from src.mcp_server import search_collection, get_artwork_details, get_room_artworks, search_events, search_faq; assert len(search_collection(artist='Kittelsen')) >= 2; assert get_artwork_details('AURA-2026-009')['sal_id'] == 'SAL-D'; assert len(get_room_artworks('SAL-D')) >= 3; assert len(search_events()) >= 1; assert '10:00' in search_faq('åpningstider')[0]['svar']; print('All 5 tools verified against live database!')"
   ```
   *Expected output:* `All 5 tools verified against live database!`.

3. **Verify read-only security boundary:**
   ```powershell
   py -3.13 -c "from src.db import execute_read_query; execute_read_query('INSERT INTO verk (id, tittel) VALUES (1, 2)')"
   ```
   *Expected output:* `PermissionError: Read-only violation: Only SELECT or WITH queries are permitted.`

**Invalidation conditions:**
- If `data/museum.db` is corrupted or deleted.
- If any of the 41 pytest tests in `tests/test_mcp_server.py` or `tests/test_db_quality.py` fail.
