# Kunstpixel Cheat Sheet

> Hurtigoppslag for utviklere, gründere og AI-agenter i Kunstpixel.  
> Teknisk miljø: Python 3.13 (`py -3.13`), FastMCP, SQLite, pytest.

---

## 1. Kjernekommandoer

### Kjøre Tester og Verifisering
```powershell
# Kjør hele testsuiten (skal ALLTID være 100 % pass – 161 tester)
py -3.13 -m pytest -v

# Kjør spesifikke testsuiter
py -3.13 -m pytest tests/test_archive_quality.py -v   # Arkivkvalitet, kalender & HMS (9 tester)
py -3.13 -m pytest tests/test_hrdemo.py -v            # HR-kjerne og tilgjengelighet (28 tester)
py -3.13 -m pytest tests/test_hr_eval.py -v           # KI-evaluator for feller L01-L03 (7 tester)
py -3.13 -m pytest tests/test_mcp_server.py -v        # Kunstvert FastMCP (23 tester)
py -3.13 -m pytest tests/test_db_quality.py -v        # Databaseintegritet (23 tester)

# Kjør full deterministisk verifisering (kjører pytest, CLI-sjekk og immutabilitet)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 -Mode manual
```

### HR, HMS & Bemanningsorakel (CLI & API)
```powershell
# Generer bemanningsforslag for kiosk
py -3.13 src/hr_cli.py kiosk

# Søk i 8 gjeldende HR/HMS/Kvalitetsregler
py -3.13 src/hr_cli.py rules

# Inspiser ansatts personkort og gyldige kompetanser
py -3.13 src/hr_cli.py person E101

# Evaluer et bemanningsforslag mot KI-feller (L01–L03 og F01–F10)
py -3.13 src/hr_cli.py eval E101,E102,E106

# Start lokal REST API (port 8765)
py -3.13 src/hr_api.py

# Start HR FastMCP-server over stdio
py -3.13 src/hr_mcp_server.py
```

### Kunstsamling & Museumsvert
```powershell
# Start interaktiv museumsvert i terminalen
py -3.13 src/cli.py "Hvor finner jeg Skrik?"

# Start lokal web-chat for gründerne (port 8000)
py -3.13 src/kunstpixel/adapters/chat_hub.py

# Start hoved-FastMCP over stdio
py -3.13 src/mcp_server.py
```

### Datagenerering og Kvalitetskontroll
```powershell
# Regenerer hele 16-årsarkivet (ansatte, utstillinger, innleie, vakter)
py -3.13 src/kunstpixel/data/archive_generator.py

# Kjør skrivebeskyttet revisjon av arkivet mot referansedato
py -3.13 src/kunstpixel/data/audit_hr_archive.py --as-of 2026-10-17
```

---

## 2. Nøkkelstier og Filstruktur

| Sti | Formål | Tilgang |
|---|---|---|
| `05_data/museum.db` | Autoritativ samlingsdatabase (16 verk, 12 kunstnere, 6 saler) | **STRIKT READ-ONLY (`mode=ro`)** |
| `05_data/kunstpixel_historikk.db` | Arkivdatabase over vakter (54 994 rader), ansatte, innleie | Operativ SQLite-base |
| `05_data/arkiv_hr_vakt_historikk.csv` | Operativ vakthistorikk (2010–2026, 0 avvik) | CSV + Parquet |
| `05_data/arkiv/` | Bevart legacy-stresstestarkiv for etterprøvbarhet (Linse p3) | Historisk arkiv |
| `04_knowledge/01_governance/` | Styringssystem, nasjonal HMS-veiledning (344 oppslag), AML | Autoritative styringsfiler |
| `04_knowledge/04_domain/projects/hr_simulator/` | Museumsrutiner `museumsrutiner.md` (R-01 til R-08) | Operative rutiner |
| `04_knowledge/05_linser/` | Revisjonsteamets 5 linser (d5, d6, f4, l2, p3) | Beslutningslinser |
| `src/kunstpixel/core/hrdemo.py` | HR-kjerne med `ClosingConnection` mot SQLite | Kjerne-logikk |
| `src/kunstpixel/core/hr_eval.py` | Deterministisk evaluator mot KI-feller (L01–L03) | Regelmotor |
| `work/TASK.md` & `work/REPORT.md` | Arbeidslogger og fullført sprintstatus | Styringsbevis |

---

## 3. Urokkelige Regler og Invarianter

1. **Strikt skrivebeskyttelse mot `museum.db`:**
   - Åpnes alltid med `file:05_data/museum.db?mode=ro` og URI-støtte (`uri=True`).
   - Ingen `INSERT`, `UPDATE`, `DELETE`, `DROP` eller `ALTER` er tillatt.
2. **Ingen HTML-dashbord eller web-UI i denne fasen:**
   - Prosjektet holdes 100 % i backend, CLI, REST API, FastMCP og automatiserte tester.
3. **Arbeidsmiljø og Vaktregler (R-01 til R-08):**
   - **Maks 1 vakt per person per dag** (0 kollisjoner, aldri > 13t eller > 24t).
   - **Minst 11 timer hviletid** mellom to skift (AML § 10-8).
   - **Maks 37,5 timer** per 7-dagers rullerende periode.
   - **Maks 90 minutter** sammenhengende vakt på harde steingulv før obligatorisk rotasjon (R-03).
   - **Mandager stengt for publikum:** Kun Magasin 1 og Vaktrom bemannes (R-04).
   - **Løftegrenser:** Maks 15 kg for én person, 15–40 kg for to personer, > 40 kg krever mekanisk løfteutstyr (R-06).
   - **Alenearbeid:** Forbudt ved > 80 gjester eller etter kl. 20:00 (R-05).

---

## 4. Feilsøking & Tips

| Problem / Symptom | Årsak | Løsning |
|---|---|---|
| `sqlite3.OperationalError: database is locked` på Windows | Åpen SQLite-tilkobling som ikke ble lukket | Bruk alltid `ClosingConnection` fra `src.kunstpixel.core.hrdemo` som sikrer `con.close()` i en context manager. |
| Test feiler i `test_archive_quality.py` | Manglende regenerering eller uventet datotilstand | Kjør `py -3.13 src/kunstpixel/data/archive_generator.py` etterfulgt av `py -3.13 src/kunstpixel/data/audit_hr_archive.py`. |
| Port 8765 opptatt | Gammel `hr_api.py`-prosess kjører i bakgrunnen | Sjekk med `Get-NetTCPConnection -LocalPort 8765` i PowerShell og stopp prosessen ved behov. |
| FastMCP svarer ikke i stdio | Buffer ikke tømt eller parser venter | Bruk `sys.stdout.flush()` eller kjør via `src/hr_mcp_server.py` med FastMCP standard wrapper. |
