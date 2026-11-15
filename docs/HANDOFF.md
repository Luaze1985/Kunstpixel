# Kunstpixel Handoff-dokument

> **Sist oppdatert:** 2026-11-14T08:01+01:00  
> **Prosjekt:** Kunstpixel (`C:\Users\larse\Documents\Kunstpixel`, gren `main`)  
> **Målgruppe:** Neste AI-agent (Claude Code, Codex, ChatGPT, Antigravity) eller utvikler som plukker opp stafettpinnen.  
> **Status:** 100 % grønt — full repo-pytest (`2 250 passed, 9 skipped, 2 xfailed, 0 failed`), `pixel_bygger.ps1` exit `0`, alle 4 `/kunstpixel`-sidecars fullført uten feil.

---

## 1. Mål og Kontekst
Kunstpixel er en felles treningsarena og teknologisk verktøykasse for museumsdrift med KI-agenter, lov-/SOP-oppslag og syntetiske driftsdata.  
Det siste arbeidet (2026-11-13 / 2026-11-14) hadde tre mål:
1. Sikre at `/kunstpixel`-kjeden og de 4 sidecarene (`kunstpixel-colab-mcp`, `kunstpixel-data-builder`, `kunstpixel-engine-builder`, `kunstpixel-sentinel`) kjører deterministisk og transparent ende-til-ende.
2. Bygge en realistisk, **pandas-generert daglig meldings- og e-postinnboks (`2010–2026`, tyngdepunkt `2020–2026`)** i `05_data/museum.db` for både **intern drift**, **eksterne kundemailer** og **arrangementer/bookinger** med lovhjemler og svarutkast.
3. Gjennomføre full `/goal`-revisjon av samtlige tabeller i `05_data/museum.db` og verifisere alt via tester, sjekksum og kunnskapsgraf.

---

## 2. Hva som er Ferdig og Verifisert

### A. Daglig drifts-, kunde- og arrangementsinnboks (`pandas 3.0.2`, `SEED = 42`)
- **Generator:** [`src/kunstpixel/data/generer_driftsmeldinger_pandas.py`](file:///C:/Users/larse/Documents/Kunstpixel/src/kunstpixel/data/generer_driftsmeldinger_pandas.py)
  - Leser gyldige referanser (`mode=ro`) fra `hr_ansatte`, `utstillinger_historikk`, `saler`, `handbok_oppslag` og `hendelser`.
  - Genererer **`3 889` meldinger** (`05_data/arkiv_driftsmeldinger_2010_2026.csv`) og **`3 889` tiltak/svarutkast** (`05_data/arkiv_driftsmeldinger_tiltak.csv`), totalt **`7 778` rader**.
  - Periodedekning: `700` meldinger i `2010–2019` (`18,0 %`) og `3 189` meldinger i `2020–2026` (`82,0 %`).
  - **8 kategorier:** `sykefraver_og_vikar` (`548`), `kafe_og_allergen` (`526`), `kundekontakt_og_epost` (`511`), `vakt_og_hviletid` (`492`), `hms_og_sikkerhet` (`491`), `klima_og_samling` (`486`), `arrangement_og_booking` (`480`), `personvern_og_gdpr` (`355`).
  - **9 faste ankercaser (`MELD-2026-9001`–`MELD-2026-9009`):** Dekker bl.a. ulovlig vaktbytte (`PERSONAL-3.2`), akutt sykefravær (`SOP-004-2`), 36 % RH + blokkert nødutgang (`SOP-008-2`), alenestenging (`SOP-001-4`), allergen/GDPR (`SOP-007-2`), privat takseringshonorar (`PERSONAL-8.1`), rullestol/ledsagerbevis (`DRIFT_KVALITET-2.1`), skjenking + overkapasitet i `SAL-E` (`DRIFT_KVALITET-8.1`) og skoleklasse med ryggsekker i `SAL-A` (`DRIFT_KVALITET-1.2`).

### B. Database (`05_data/museum.db`), KI-verktøy & MCP
- **`src/kunstpixel/data/build_museum_db.py`:** Bygger `driftsmeldinger_epost` og `driftsmeldinger_tiltak` med fremmednøkler inn i `05_data/museum.db`.
- **`src/kunstpixel/core/db.py`:** Ny skrivebeskyttet spørring `query_daglig_driftsinnboks(...)`.
- **`src/kunstpixel/core/mcp_server.py`:** Nytt `@mcp.tool()` `get_daily_ops_inbox(...)`.
- **`src/kunstpixel/adapters/datafinner.py`:** Registrert `get_daily_ops_inbox` (samt `get_cafe_menu_and_sales`, `search_visitor_reviews_and_satisfaction`, `search_hms_incident_narratives`, `get_role_workflows_and_testcases`) i `VERKTOY`.
- **Rettelser i eksisterende filer:**
  - `05_data/ansatt_testcaser.csv`: `syntetisk (museum.db)` rettet til `syntetisk (museum_db)` for å følge `datapolicy._SYNTETISK_RE`.
  - `AGENTS.md`: Punkt 6 («Lokal modell brukes ikke pt») sikret på plass slik at `tests/test_no_local_model.py` passerer `16/16`.

### C. Verifikasjon og Testbevis
- **Databasehelse:** `61` brukertabeller (`62` totalt inkl. `sqlite_sequence`), **`92 505` brukerrader**, `22 932 KB`, `PRAGMA user_version = 8`, `integrity_check = ok`, `fk_brudd = 0`, `0` tomme eller blinde tabeller (`61/61` dekket i `src/`), `42/42` CSV-filer uten feil.
- **Deterministisk sjekksum:** `sha256 = fd4262df266d5fe74d6184998b6cfabc8bd2e3d226c3312586eb81fcb053aaf4 -> LIK`.
- **Full pytest:** `2 250 passed, 9 skipped, 2 xfailed, 0 failed` (verifisert i sidecar-kjøring `1c4ed217-5370-47e4-8c9c-66535b3cf6a0`).
- **Samlet `/kunstpixel`-pipeline (`scripts/pixel_bygger.ps1`):** Exit `0` (`115 passed, 2 xfailed` i fase 5) og alle 4 sidecars logget grønt i [bygger-fremdrift.md](file:///C:/Users/larse/Documents/Kunstpixel/.scratch/bygger-fremdrift.md).

---

## 3. Hva som IKKE er gjort / Kjente avgrensninger
- **Ingen UI-visning for innboks/svarutkast ennå:** `get_daily_ops_inbox` fungerer i Python og MCP, men svarutkastene (`epost_sms_utkast`) er ennå ikke koblet inn med egne bokser/knapper i Datafinner-grensesnittet.
- **Ucommittet arbeidskatalog:** Endringene ligger foreløpig lokalt på `main` (`ahead 37`, ikke pushet). Ikke kjør `git add -A` uten å se over eldre uavhengige filer fra `git status -s`.
- **Detalj i `db.py` (`dagens_kritiske_saker`):** Spørringen sjekker `t.status IN ('ÅPEN', 'ESKALERT') OR e.hastegrad = 'KRITISK'`, mens CSV-generatoren skriver `'APEN'` (uten `Å`). Kritiske saker kommer med via `e.hastegrad = 'KRITISK'`, men hvis også ikke-kritiske `'APEN'`-saker ønskes i `dagens_kritiske_saker`, bør `'APEN'` legges til i `IN (...)`.

---

## 4. Viktige og Nylig Endrede Filer
- **Data & bygg:** `src/kunstpixel/data/generer_driftsmeldinger_pandas.py`, `src/kunstpixel/data/build_museum_db.py`, `05_data/arkiv_driftsmeldinger_2010_2026.csv`, `05_data/arkiv_driftsmeldinger_tiltak.csv`, `05_data/ansatt_testcaser.csv`, `05_data/museum.db`, `05_data/museum.db.sha256`
- **KI-motor & tester:** `src/kunstpixel/core/db.py`, `src/kunstpixel/core/mcp_server.py`, `src/kunstpixel/adapters/datafinner.py`, `tests/test_daglig_driftsinnboks.py`, `scripts/pixel_bygger.ps1`
- **Dokumentasjon & logger:** `05_data/index.md`, `KUNNSKAPSKART.md`, `04_knowledge/00_DATA_OG_MCP_OVERSIKT.md`, `.scratch/bygger-fremdrift.md`, `.scratch/db-status/INSPEKSJON-SISTE.md`, `.scratch/handoffs/HANDOFF-2026-11-14T0801.md`

---

## 5. Låste Beslutninger og Verifikasjonskommandoer
1. **`museum.db` skal alltid åpnes `mode=ro`** i all applikasjonskode og spørring (håndheves av `tests/test_ingen_direkte_db_skriving.py`).
2. **All `datakilde` skal matche `^syntetisk(?: \([a-z0-9_]+\))?$`** (`src/kunstpixel/core/datapolicy.py`).
3. **Ikke rør `datafinner_api.SPORSMAL`** uten samtidig å oppdatere `tests/test_datafinner_api.py`.
4. **Hurtig verifikasjon (fra `C:\Users\larse\Documents\Kunstpixel`):**
   ```powershell
   py -3.13 src/kunstpixel/data/build_museum_db.py --check
   py -3.13 scripts/sjekk_kunnskapsgraf.py
   py -3.13 scripts/db_status_gate.py --uten-pytest
   py -3.13 -m pytest tests/test_daglig_driftsinnboks.py tests/test_datakilde_og_kopier.py tests/test_no_local_model.py -q
   ```

---

## 6. Ett Konkret Neste Steg
Koble `get_daily_ops_inbox` (inkl. `handbok_punkt_id`-referanser og kopierbare `epost_sms_utkast`-kort) inn i Datafinner-visningen dersom brukeren ønsker å prøve ut triage og utkast i nettleseren, etter først å ha avklart med Lars om endringene på `main` skal committes som egen milepæl.

> *Historisk arkivhandoff (2026-10-17 / 2026-10-19) ligger i `docs/HANDOFF-2026-10-20.md` og `.scratch/handoffs/`.*
