# Oppdrag: Fullføring av Kunstpixel HR/HMS/Kvalitet Backend og Dataforbedringsplan

**Mål:** Bygge ferdig backend-komponentene fra `kunstpixel_hr_hms_demo.zip` i tråd med godkjent plan `plan_hr_backend.md`, og gjennomføre forbedrings- og dataforbedringsplanen `plan_forbedring_og_dataforbedring.md`.
**Avgrensning:** Ingen HTML-dashbord eller web-brukergrensesnitt. 100 % fokus på kjerne, CLI, REST API, FastMCP, deterministisk KI-evaluator, datakvalitet og automatiserte tester.

## Done-when kriterier
1. [x] Kjerne i `src/kunstpixel/core/hrdemo.py` er utvidet med `list_skills()`, `list_people()` og `get_person()`.
2. [x] Deterministisk evaluator `src/kunstpixel/core/hr_eval.py` er implementert for å avdekke kjente KI-feil (L01–L03 fra `HRDEMO_MAKSINLESBAR.md`).
3. [x] HTTP API i `src/kunstpixel/core/hrdemo_api.py` håndterer `/api/v1/hr/skills` og `/api/v1/hr/people` (både liste og per ID).
4. [x] FastMCP i `src/kunstpixel/core/hrdemo_mcp.py` tilbyr `get_competence_catalog()`, `get_staff_member()` og `evaluate_kiosk_proposal()`.
5. [x] Dedikerte kjørbare inngangspunkter er etablert i `src/`:
   - `src/hr_cli.py` (CLI for rapportering og inspeksjon)
   - `src/hr_api.py` (Lokal HTTP-server)
   - `src/hr_mcp_server.py` (FastMCP stdio server)
6. [x] Nye og eksisterende tester passerer 100 %:
   - `tests/test_hrdemo.py` (28 tester) og `tests/test_hr_eval.py` (7 tester)
   - Hele testsuiten i repoet (`py -3.13 -m pytest -v`: 161 av 161 tester bestått)
7. [x] `AGENTS.md` og `README_HRDEMO.md` er oppdatert med nye verktøy og kommandoer.
8. [x] `work/REPORT.md` er oppdatert med alle 5 obligatoriske seksjoner.
9. [x] Vaktarkiv- og datakvalitetsfeil gransket flerdimensjonalt med DeepInvestigator (d5, d6, f4, l2, p3).
10. [x] Styringsdokumenter harmonisert: løftegrenser (15 kg) og alenearbeid (>80 gjester) i `KVALITETS_OG_STYRINGSSYSTEM.md` samstemt med `hms_arbeidsmiljo.yaml`.
11. [x] Klassifisering av fremtidige vakter i `audit_hr_archive.py` rettet opp til `planlagt_fremtidig`.
12. [x] Samlingsdatabasen `05_data/museum.db` grundig revidert (integritet, 6 autoriserte saler, 0 FK-brudd, ingen Sal F).
13. [x] Automatisert testport `tests/test_archive_quality.py` etablert og verifisert i CI-suiten.
14. [x] Bevisbevaring & historisk arkiv sikret (Linse p3): 48 298 legacy-rader bevart i `05_data/arkiv/arkiv_hr_vakt_historikk_legacy_stresstest.csv` og `.parquet` med `README_LEGACY_ARKIV.md`.
15. [x] Datagenerator re-arkitekturert (`src/kunstpixel/data/archive_generator.py`):
    - Full kalender- og behovsmodell (dager 1–31, 0 kalender-blackout)
    - Publikumsstasjoner stengt på mandager (kun Magasin 1 og Vaktrom bemannes)
    - Fiktiv Sal F fullstendig fjernet fra saler, stasjoner og utstillinger
    - 0 persondager > 13t eller > 24t (maks 1 vakt/dag, 11t hviletid, 37,5t/uke)
    - Stillingsbrøk harmonisert (~21–22 vakter/mnd for 1,0 FTE)
    - 54 994 feilfrie vakter regenerert til CSV, Parquet og SQLite
16. [x] Nasjonal HMS-veiledningsbase integrert: `04_knowledge/01_governance/hms_veiledning_nasjonal.yaml` (344 autoritative oppslag).
17. [x] Museumsrutiner formalisert: `04_knowledge/04_domain/projects/hr_simulator/museumsrutiner.md` (R-01 til R-08, 90 min steingulvrotasjon).
18. [x] Deterministisk verifisering bestått (`scripts/verify.ps1 -Mode manual` -> PASS).
