# Kunstpixel – HR/HMS/kvalitet (syntetisk demo)

En tilleggspakke til eksisterende Kunstpixel. Bruker eksisterende museumskilde uten å endre den. Samler museumsdata og HR-demodata i **én kombinert runtime-database**.

## Start (fra repo-roten)

```bash
# Initialisering og rapportering via dedikert CLI
py -3.13 src/hr_cli.py init --reset
py -3.13 src/hr_cli.py kiosk
py -3.13 src/hr_cli.py rules
py -3.13 src/hr_cli.py skills
py -3.13 src/hr_cli.py person E101
py -3.13 src/hr_cli.py eval E101,E102,E106,E103,E111

# Start lokalt HTTP API (127.0.0.1:8765)
py -3.13 src/hr_api.py

# Start FastMCP stdio server
py -3.13 src/hr_mcp_server.py

# Testkjøring og systemverifisering
py -3.13 -m pytest tests/test_hrdemo.py tests/test_hr_eval.py -v
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 -Mode manual
```

For å nullstille demo: `py -3.13 src/hr_cli.py init --reset`. Berører kun `.runtime/kunstpixel_demo.db` (lagt til i `.gitignore`). MCP-adapteren er isolert i `src/hr_mcp_server.py` for å unngå brudd i eksisterende museumsverktøy.

Om datakriterier, fasitsvar, feiltester, prosedyrer og kilder: se `04_knowledge/01_governance/HRDEMO_MAKSINLESBAR.md`.

