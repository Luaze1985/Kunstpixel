# Kunstpixel – HR/HMS/kvalitet (syntetisk demo)

En tilleggspakke til eksisterende Kunstpixel. Bruker eksisterende museumskilde uten å endre den. Samler museumsdata og HR-demodata i **én kombinert runtime-database**.

## Start (fra repo-roten)

~~~bash
python -m src.kunstpixel.core.hrdemo --init
python -m src.kunstpixel.core.hrdemo --report kiosk
python -m src.kunstpixel.core.hrdemo --report rules
python -m src.kunstpixel.core.hrdemo_api
# I annen terminal:
# curl http://127.0.0.1:8765/api/v1/hr/candidates?date=2026-11-07
python -m src.kunstpixel.core.hrdemo_mcp
python -m pytest tests/test_hrdemo.py -q
~~~

For å nullstille demo: `python -m src.kunstpixel.core.hrdemo --init --reset`. Berører kun .runtime/kunstpixel_demo.db`. Du må ikke committe .runtime/` (legg til i .gitignore` dersom det ikke finnes). MCP-adapteren er separat fra eksisterende museum-MCP, for å unngå brudd i eksisterende verktøy.

Om datakriterier, fasitsvar, feiltester, prosedyrer og kilder: se `04_knowledge/01_governance/HRDEMO_MAKSINLESBAR.md`.
