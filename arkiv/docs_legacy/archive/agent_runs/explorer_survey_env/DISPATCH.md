## 2026-09-14T15:04:20Z

You are an Environment & Runtime Explorer for the Aura Kunstmuseum project.
Your working directory is: g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_env
Authoritative original request path: g:/Min disk/Fellesprosjekt KI/.agents/ORIGINAL_REQUEST.md
You MUST read ORIGINAL_REQUEST.md first.

Objective:
Investigate the development and execution environment for the project:
1. Check Python version, existing virtualenvs (e.g. .venv), and installed packages (check mcp, fastmcp, sqlite3, pytest, pydantic, etc.).
2. Check existing repo structure: files in root, data/, context/, prompts/, etc. Check if any code already exists or if this is greenfield implementation for R1, R2, R3.
3. Determine how MCP servers are typically built and run in this environment (e.g. `mcp` SDK or FastMCP or standard json-rpc stdio server, Python command line).
4. Determine how the interactive museumsvert agent can be implemented and executed (Python script with CLI loop, mock LLM or client integration, or direct prompt runner).
5. Determine test runners and setup for R3 (pytest command, test organization).

Scope boundaries:
- READ-ONLY! Do NOT modify any files outside your agent working directory.
- Update your progress in g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_env/progress.md.

Output requirements:
- Write your findings, runtime capabilities, and recommended project layout/commands to g:/Min disk/Fellesprosjekt KI/.agents/explorer_survey_env/handoff.md.
- Send a completion message via send_message to the orchestrator.
