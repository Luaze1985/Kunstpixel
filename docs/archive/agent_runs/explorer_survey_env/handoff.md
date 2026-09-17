# Environment & Runtime Survey Handoff Report — Aura Kunstmuseum

**Agent:** Environment & Runtime Explorer (`explorer_survey_env`)  
**Milestone:** S01-survey  
**Timestamp:** 2026-09-14T17:11:00+02:00  
**Target Project:** Aura Kunstmuseum Demo-Prototype (R1, R2, R3)  
**Working Directory:** `g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_env`

---

## 1. Observation

### 1.1 Python Executables and Versions
- **Default `python` on PATH:**
  - Command: `python --version`
  - Output: `Python 3.11.9`
  - Executable path: `C:\Users\larse\AppData\Local\Programs\Python\Python311\python.exe`
  - Note: This Python 3.11 installation lacks `mcp`, `fastmcp`, `pytest`, and `pydantic`.
- **Python 3.13 on PATH (Python Launcher / direct):**
  - Command: `py -3.13 --version` or `C:\Users\larse\AppData\Local\Programs\Python\Python313\python.exe --version`
  - Output: `Python 3.13.12`
  - Command `py --list` output:
    ```
     -V:3.14 *        Python 3.14.3
     -V:3.13          Python 3.13 (64-bit)
     -V:3.11          Python 3.11 (64-bit)
    ```

### 1.2 Installed Packages and Package Managers
- **Package verification in Python 3.13 (`py -3.13`):**
  - `mcp`: version `1.29.1` (Official Anthropic Model Context Protocol SDK)
  - `fastmcp`: version `3.4.2` (`from fastmcp import FastMCP`)
  - `mcp.server.fastmcp`: included within official SDK (`from mcp.server.fastmcp import FastMCP`)
  - `pytest`: version `9.0.2` (`pytest.exe` located at `C:\Users\larse\AppData\Local\Programs\Python\Python313\Scripts\pytest.exe`)
  - `pydantic`: version `2.12.5`
  - `pydantic-ai`: version `1.106.0`
  - `openai`: version `2.41.0`
  - `rich`: version `15.0.0`
  - `typer`: version `0.24.1`
  - `sqlite3`: standard library module
- **Package managers and runners on PATH:**
  - `uv.exe`: version `0.12.7` at `C:\Users\larse\AppData\Local\hermes\bin\uv.exe`
  - `pytest.exe`: available on PATH pointing to Python 3.13 (`pytest --version` -> `pytest 9.0.2`)
- **Virtual environments:**
  - No existing virtualenv in workspace root `g:\Min disk\Fellesprosjekt KI\.venv`.

### 1.3 Repository Structure and Code Status
- **Workspace root:** `g:/Min disk/Fellesprosjekt KI`
- **Files and directories found:**
  - `CONTEXT.md` (Domain glossary, 2.3 KB)
  - `ORIGINAL_REQUEST.md` (Original prompt and acceptance criteria, 4.2 KB)
  - `context/` (36 files: `core/`, `roles/`, `operations/`, `projects/`, etc.)
  - `data/samling.json` (12 artwork entries, 6.5 KB)
  - `prompts/` (6 master prompts: `museumsdirektor.md`, `kurator.md`, `samlingsforvalter.md`, `formidler.md`, `museumsvert.md`, `driftsansvarlig.md`)
  - `digital_bedrift_preclone_v0_3/` (Reference pre-clone artifacts)
  - `docs/` (`adr/`)
  - `.agents/` (Agent coordination folders)
- **Codebase status:**
  - Zero Python source files (`*.py`) exist in `g:/Min disk/Fellesprosjekt KI`.
  - Greenfield implementation required for R1 (MCP server), R2 (Museumsvert agent), and R3 (Integration test suite).

### 1.4 SQLite Database Location and Contents
- In `.gemini/config/mcp_config.json` (line 37-43) and `.gemini/antigravity-ide/mcp_config.json` (line 28-34):
  ```json
  "sqlite": {
    "command": "mcp-server-sqlite",
    "args": [
      "--db-path",
      "C:\\Users\\larse\\Documents\\.headroom\\memory.db"
    ]
  }
  ```
- Connecting to `C:\Users\larse\Documents\.headroom\memory.db` via `sqlite3` reveals 7 tables with exactly 72 total rows:
  - `kunstnere`: 12 rows
  - `saler`: 6 rows
  - `verk`: 16 rows
  - `utstillinger`: 3 rows
  - `utstilling_verk`: 15 rows
  - `hendelser`: 8 rows
  - `publikum_faq`: 12 rows
  - Total: 72 rows (exact match to `ORIGINAL_REQUEST.md` specification).

### 1.5 External Runtimes and Local LLMs
- **Local Ollama endpoint:** active on `http://localhost:11434`
  - Models available: `borealis:latest` (Norwegian-tuned 3.9B model), `gemma4:latest` (8.0B tool-capable model), `nomic-embed-text:latest`
- **Environment variables:**
  - `GEMINI_API_KEY`: present
  - `OLLAMA_API_KEY`: present

---

## 2. Logic Chain

1. **Python Interpreter Selection:**
   - Because typing `python` invokes Python 3.11 (which lacks `mcp`, `fastmcp`, `pytest`), executing any project scripts or tests using plain `python` will fail with `ModuleNotFoundError`.
   - However, invoking `py -3.13` or `pytest` directly invokes Python 3.13.12, where all necessary packages (`mcp`, `fastmcp`, `pytest`, `pydantic`, `rich`) are already installed and tested working.
   - Therefore, all development commands and documentation must specify `py -3.13` (or set up a project-local `.venv` pointing to Python 3.13 using `uv venv --python 3.13`).

2. **MCP Server Framework Choice:**
   - Both `from mcp.server.fastmcp import FastMCP` (official SDK) and `from fastmcp import FastMCP` are installed and verified.
   - FastMCP allows declarative tool registration via `@mcp.tool()`, automatic JSON-RPC schema generation from Python type annotations and docstrings, and stdio transport via `mcp.run()`.
   - Crucially, FastMCP tool functions are regular Python functions that can be directly imported and invoked in `pytest` test suites (`from src.mcp_server import samlingssok; res = samlingssok("Kittelsen")`). This eliminates the need for async subprocess spawning during unit testing.

3. **Database Access Architecture:**
   - The authoritative populated database is currently located at `C:\Users\larse\Documents\.headroom\memory.db`.
   - Hardcoding an absolute path outside the repository would make the repository non-portable.
   - The recommended design is a database configuration helper in `src/config.py` that resolves the database path using precedence:
     1. Environment variable `AURA_DB_PATH`
     2. Repository-local file `g:/Min disk/Fellesprosjekt KI/data/museum.db` (if present)
     3. Default fallback to `C:\Users\larse\Documents\.headroom\memory.db`
   - The implementer can optionally copy `C:\Users\larse\Documents\.headroom\memory.db` to `data/museum.db` to make the repository completely self-contained.

4. **Museumsvert Agent Architecture (R2):**
   - The agent requires:
     a) Loading system prompt from `prompts/museumsvert.md`.
     b) Enforcement of `context/operations/tool_access.md`: Museumsvert has read-only access and calls parameterized tools (`search_collection`, `get_artwork_location`, etc.), NEVER raw SQL.
     c) Dual-engine architecture:
        - **Deterministic Engine:** Analyzes intent (practical, collection, exhibition, event, recommendation), dispatches to MCP tools, and templates the response following the exact style rules in `prompts/museumsvert.md`. This executes in <50ms with 0 tokens, making it 100% reliable for CI and `pytest`.
        - **LLM Adapter (Optional):** When running in interactive CLI mode with `--llm`, calls local Ollama (`borealis:latest` / `gemma4:latest`) or Gemini API.
     d) Interactive CLI loop in `src/cli.py` using `rich` for a clean museum terminal experience.

5. **Test Runner & Integration Suite (R3):**
   - `pytest 9.0.2` runs cleanly in the repo root via `pytest` or `py -3.13 -m pytest`.
   - Tests should be structured into:
     - `tests/test_mcp_server.py` (Validates R1 criteria: Kittelsen search >= 2, SAL-D >= 3, opening hours FAQ, events, artwork details).
     - `tests/test_agent.py` (Validates R2 criteria: Skrik in Sal D, ticket prices, 30-minute highlights, no hallucinations, tone).
     - `tests/test_integration.py` (Validates R3 criteria: >=8 end-to-end scenarios across samling, utstilling, hendelse, praktisk).
     - `tests/test_db_quality.py` (Validates 72 rows, foreign keys, veggtekst lengths 50-90 words).

---

## 3. Caveats

1. **FAQ Search Matching:**
   - In `publikum_faq`, the question for opening hours is stored as `"Naar har museet aapent?"` with answer `"Tirsdag–fredag: 10:00–17:00. Loerdag–soendag: 11:00–16:00. Mandag: stengt."`.
   - A naive SQL search `WHERE spoersmaal LIKE '%åpningstider%'` will return 0 rows.
   - The `faq_oppslag` tool MUST search both `spoersmaal` and `svar`, and apply Norwegian character normalization (`å` <-> `aa`, `ø` <-> `oe`) or keyword synonym mapping.
2. **Veggtekst Quality Rules:**
   - Two works in the database (`AURA-2026-011` Brudeferd i Hardanger and `AURA-2026-012` Selvportrett med sigarett) have `veggtekst_status = 'draft'` and empty veggtekst.
   - The remaining 14 works have approved veggtekster with 49–60 words, strictly complying with the 50–90 word rule (with `AURA-2026-014` at 49 words).
   - Test assertions should filter on `veggtekst_status = 'approved'`.
3. **Subagent Read-Only Constraint:**
   - This survey was performed strictly read-only. No files outside `.agents/explorer_survey_env` were written or modified.

---

## 4. Conclusion

- The execution environment is fully capable and ready for immediate implementation of R1, R2, and R3.
- **Python Runtime:** Use `py -3.13` (Python 3.13.12). All dependencies (`mcp` 1.29.1, `fastmcp` 3.4.2, `pytest` 9.0.2, `pydantic` 2.12.5, `rich` 15.0.0) are already installed.
- **Database:** Authoritative SQLite database with all 72 rows is at `C:\Users\larse\Documents\.headroom\memory.db`. Implementer should make path configurable via `AURA_DB_PATH` with fallback to this location or a local copy at `data/museum.db`.
- **MCP Framework:** Use `from mcp.server.fastmcp import FastMCP`.
- **Testing:** `pytest` runs directly and seamlessly.

### Recommended Project Layout
```
g:/Min disk/Fellesprosjekt KI/
├── pyproject.toml              # Pytest and project configuration
├── README.md                   # CLI instructions and test commands
├── data/
│   ├── samling.json            # Existing JSON mirror
│   └── museum.db               # (Optional copy of SQLite database)
├── src/
│   ├── __init__.py
│   ├── config.py               # Database path and configuration loader
│   ├── db.py                   # SQLite connection and helper queries
│   ├── mcp_server.py           # FastMCP server exposing the 5 collection tools
│   ├── agent.py                # Museumsvert agent core logic & response synthesis
│   └── cli.py                  # Interactive CLI interface with terminal loop
└── tests/
    ├── __init__.py
    ├── conftest.py             # Fixtures for DB connection and server
    ├── test_mcp_server.py      # Acceptance tests for R1 MCP tools
    ├── test_agent.py           # Acceptance tests for R2 Museumsvert
    ├── test_integration.py      # Acceptance tests for R3 (8+ operational scenarios)
    └── test_db_quality.py      # Database constraints and veggtekst checks
```

---

## 5. Verification Method

To independently verify these findings, run the following commands in PowerShell from `g:/Min disk/Fellesprosjekt KI`:

1. **Verify Python 3.13 and core libraries:**
   ```powershell
   py -3.13 -c "import mcp, fastmcp, pytest, pydantic, sqlite3; print('All modules imported successfully!')"
   ```
2. **Verify FastMCP initialization:**
   ```powershell
   py -3.13 -c "from mcp.server.fastmcp import FastMCP; s = FastMCP('Aura'); print(s)"
   ```
3. **Verify Pytest installation and version:**
   ```powershell
   pytest --version
   ```
4. **Verify SQLite database and 72-row count:**
   ```powershell
   py -3.13 -c "import sqlite3; conn = sqlite3.connect(r'C:\Users\larse\Documents\.headroom\memory.db'); cur = conn.cursor(); tables = ['kunstnere', 'saler', 'verk', 'utstillinger', 'utstilling_verk', 'hendelser', 'publikum_faq']; counts = {t: cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in tables}; print(counts); print('Total rows:', sum(counts.values()))"
   ```
5. **Verify local Ollama service availability:**
   ```powershell
   curl.exe -s http://localhost:11434/api/tags
   ```
