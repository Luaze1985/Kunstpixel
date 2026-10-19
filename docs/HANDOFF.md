# Kunstpixel Handoff-dokument

> **Dato:** 2026-10-17  
> **Prosjekt:** Kunstpixel  
> **Målgruppe:** Neste AI-agent eller utvikler som plukker opp stafettpinnen.  
> **Status:** 100 % grønt – 161 tester bestått, deterministisk verifisering bestått.

---

## 1. Mål og Kontekst
Kunstpixel er en felles treningsarena og teknologisk verktøykasse for to gründere som eksperimenterer med AI-agenter, databruk og automatisering. Formålet med denne økten var:
1. Fullføre HR/HMS/Kvalitet backend-komponentene fra `kunstpixel_hr_hms_demo.zip` (kjerne, evaluator, CLI, REST API, FastMCP).
2. Gjennomføre en dyp revisjon av det syntetiske 16-års vaktarkivet (`arkiv_hr_vakt_historikk.csv`) gjennom 5 spesialiserte linser.
3. Re-arkitekturere datageneratoren for å eliminere 4 759 ulovlige dager (>13t), 36 umulige dager (>24t), kalender-blackout (dager 29–31) og fantoombemanning på mandager.
4. Integrere nasjonal HMS-veiledning (344 punkter) og museumsrutiner inn i styringssystemet, med full bevisbevaring av legacy-data (Linse p3).

---

## 2. Hva som er Ferdig og Verifisert

### A. Kjerne, Evaluator, CLI, API og FastMCP
- **SQLite Locking Løst:** Etablert `ClosingConnection` i [`src/kunstpixel/core/hrdemo.py`](file:///g:/Min%20disk/Kunstpixel/src/kunstpixel/core/hrdemo.py) som forhindrer NT-filhenging.
- **Katalog og Personkort:** Utvidet `hrdemo.py` med `list_skills()`, `list_people()`, `get_person()`.
- **Deterministisk KI-Evaluator:** Utviklet [`src/kunstpixel/core/hr_eval.py`](file:///g:/Min%20disk/Kunstpixel/src/kunstpixel/core/hr_eval.py) for å avsløre kognitive KI-feller:
  * `L01`: Hallusinerte ID-er / ikke-eksisterende ansatte.
  * `L02`: Manglende kasse- eller skjenkekurs (utløpte/udokumenterte sertifikater).
  * `L03`: For få kandidater tildelt skiftet (krav til bemanning brutt).
- **Inngangspunkter:**
  * CLI: [`src/hr_cli.py`](file:///g:/Min%20disk/Kunstpixel/src/hr_cli.py) (`kiosk`, `rules`, `person <ID>`, `eval <IDs>`).
  * REST API: [`src/hr_api.py`](file:///g:/Min%20disk/Kunstpixel/src/hr_api.py) (port 8765, `/api/v1/hr/skills`, `/api/v1/hr/people`).
  * FastMCP Server: [`src/hr_mcp_server.py`](file:///g:/Min%20disk/Kunstpixel/src/hr_mcp_server.py) (stdio protokoll, 6 verktøy).

### B. Arkiv, Kalender & Datakvalitet
- **Bevisbevaring (Linse p3):** Sikret 48 298 opprinnelige rader i [`05_data/arkiv/arkiv_hr_vakt_historikk_legacy_stresstest.csv`](file:///g:/Min%20disk/Kunstpixel/05_data/arkiv/arkiv_hr_vakt_historikk_legacy_stresstest.csv) med [`05_data/arkiv/README_LEGACY_ARKIV.md`](file:///g:/Min%20disk/Kunstpixel/05_data/arkiv/README_LEGACY_ARKIV.md).
- **Re-arkitekturert Generator ([`src/kunstpixel/data/archive_generator.py`](file:///g:/Min%20disk/Kunstpixel/src/kunstpixel/data/archive_generator.py)):**
  * Kalenderstyrt (1–31 dager, 0 dager tapt).
  * Mandager stengt for publikum (kun `Magasin 1` og `Vaktrom`).
  * Fiktiv «Sal F» fullstendig fjernet fra saler, utstillinger og vakter.
  * Maks 1 vakt/dag, minst 11t hvile, maks 37,5t/uke.
  * 54 994 rene vakter generert til CSV, Parquet og SQLite (`kunstpixel_historikk.db`).
- **Kvalitetsrevisjon ([`src/kunstpixel/data/audit_hr_archive.py`](file:///g:/Min%20disk/Kunstpixel/src/kunstpixel/data/audit_hr_archive.py)):**
  * 0 dager > 24t, 0 dager > 13t.
  * 54 332 historiske vakter godkjent med `ingen_funn_i_disse_reglene`.
  * 662 fremtidige vakter merket `planlagt_fremtidig`.

### C. Styring og Museumsrutiner
- **Nasjonal HMS-veiledning ([`04_knowledge/01_governance/hms_veiledning_nasjonal.yaml`](file:///g:/Min%20disk/Kunstpixel/04_knowledge/01_governance/hms_veiledning_nasjonal.yaml)):** 344 autoritative Q&A-oppslag fra Excel strukturert til YAML.
- **Museumsrutiner ([`04_knowledge/04_domain/projects/hr_simulator/museumsrutiner.md`](file:///g:/Min%20disk/Kunstpixel/04_knowledge/04_domain/projects/hr_simulator/museumsrutiner.md)):** Etablert regler `R-01` til `R-08` (maks 90 min på steingulv, alenearbeid >80 gjester, løft 15 kg).
- **Harmonisering:** [`04_knowledge/01_governance/KVALITETS_OG_STYRINGSSYSTEM.md`](file:///g:/Min%20disk/Kunstpixel/04_knowledge/01_governance/KVALITETS_OG_STYRINGSSYSTEM.md) samstemt med [`05_data/governance/hms_arbeidsmiljo.yaml`](file:///g:/Min%20disk/Kunstpixel/05_data/governance/hms_arbeidsmiljo.yaml).

### D. Testbevis
- **Pytest:** `py -3.13 -m pytest -v` $\rightarrow$ **161 av 161 tester bestått 100 %** (inkl. 9 tester i [`tests/test_archive_quality.py`](file:///g:/Min%20disk/Kunstpixel/tests/test_archive_quality.py)).
- **Deterministisk verifisering:** `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 -Mode manual` $\rightarrow$ **PASS**.

---

## 3. Begrensninger og Hva som IKKE er Gjort
- **Ingen HTML-dashbord eller UI:** Eksplisitt avgrenset av brukeren i denne fasen.
- **Ekstern OpenAI API-kall:** Ikke utført mot ekstern sky i denne økten; all logikk er deterministisk og testet lokalt med 0 kostnad/tokens.
- **Ukeplan-simulatormotor:** Feature-grenen og de fire sammenhengende ukene fra `BEHOV_UKEPLAN_2026-10-16.md` er spesifisert og forberedt i datagrunnlaget, men ukeplansammenslåingslogikken (mot reell LLM) er neste etappe.

---

## 4. Viktige Filer og Databaser
- **Samlingsbase (READ-ONLY):** [`05_data/museum.db`](file:///g:/Min%20disk/Kunstpixel/05_data/museum.db) (16 verk, 12 kunstnere, 6 saler, må aldri muteres).
- **Vakthistorikkbase:** [`05_data/kunstpixel_historikk.db`](file:///g:/Min%20disk/Kunstpixel/05_data/kunstpixel_historikk.db) (tabell `hr_vakter` med 54 994 rader).
- **Styring og Rutiner:**
  * [`04_knowledge/01_governance/hms_veiledning_nasjonal.yaml`](file:///g:/Min%20disk/Kunstpixel/04_knowledge/01_governance/hms_veiledning_nasjonal.yaml)
  * [`04_knowledge/04_domain/projects/hr_simulator/museumsrutiner.md`](file:///g:/Min%20disk/Kunstpixel/04_knowledge/04_domain/projects/hr_simulator/museumsrutiner.md)
  * [`04_knowledge/05_linser/00_REVISJONSTEAM_MASTER.md`](file:///g:/Min%20disk/Kunstpixel/04_knowledge/05_linser/00_REVISJONSTEAM_MASTER.md)
- **Kjerne og CLI:**
  * [`src/hr_cli.py`](file:///g:/Min%20disk/Kunstpixel/src/hr_cli.py)
  * [`src/hr_api.py`](file:///g:/Min%20disk/Kunstpixel/src/hr_api.py)
  * [`src/hr_mcp_server.py`](file:///g:/Min%20disk/Kunstpixel/src/hr_mcp_server.py)
  * [`src/kunstpixel/core/hr_eval.py`](file:///g:/Min%20disk/Kunstpixel/src/kunstpixel/core/hr_eval.py)
  * [`src/kunstpixel/core/hrdemo.py`](file:///g:/Min%20disk/Kunstpixel/src/kunstpixel/core/hrdemo.py)
  * [`src/kunstpixel/data/archive_generator.py`](file:///g:/Min%20disk/Kunstpixel/src/kunstpixel/data/archive_generator.py)
- **Oppdragslogger:**
  * [`work/TASK.md`](file:///g:/Min%20disk/Kunstpixel/work/TASK.md)
  * [`work/REPORT.md`](file:///g:/Min%20disk/Kunstpixel/work/REPORT.md)
  * [`docs/CHEATSHEET.md`](file:///g:/Min%20disk/Kunstpixel/docs/CHEATSHEET.md)

---

## 5. Viktige Beslutninger og Invarianter
1. `museum.db` åpnes ALLTID med `file:...mode=ro` og `uri=True`. Ingen skriveoperasjoner tillatt!
2. Ingen hemmeligheter eller rå API-nøkler i repoet.
3. Ingen bygging av HTML-grensesnitt før backend, regelmotor og datakvalitet er fullt testet.
4. Legacy-avvik skal aldri slettes eller skjules, men oppbevares i `05_data/arkiv/` som bevis på feilkilder og baseline.

---

## 6. Foreslåtte Skills for Neste Agent (Suggested Skills)
Neste agent bør benytte følgende skills via verktøykall:
1. `determ`: For rask 0-token verifisering av kode, filer og loggtilstand før resonnering.
2. `verified-work`: For autonom gjennomføring med verifiserte gates og QA-sensor.
3. `database-inspektor`: Ved videre arbeid med SQLite-skjemaer eller spørringer i `kunstpixel_historikk.db`.
4. `kildeverifikator-norsk-arbeidsliv`: Dersom nye arbeidsrettslige regler eller tariffspørsmål skal innarbeides.
5. `instruks-for-agenter`: Hvis nye subagenter eller instrukser skal defineres.

---

## 7. Ett Konkret Neste Steg
**Koble nasjonal HMS-veiledning (`hms_veiledning_nasjonal.yaml`) direkte til et søkeverktøy i `hr_cli.py` og `hr_mcp_server.py`:**
- Implementer en funksjon `search_hms_guidance(query: str, topic: str | None)` i `src/kunstpixel/core/hrdemo.py` som lar agenter og museumsledere søke blant de 344 veiledningspunktene over FastMCP og CLI.
- Legg til tilhørende test i `tests/test_hrdemo.py`.
