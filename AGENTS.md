> **Før du leser videre:** se `KUNNSKAPSKART.md` i roten og `00_felles/FORMAAL.md` — den viser formålet for de to gründerne, hvor ting ligger og hvilke kjøreregler som gjelder.

# AGENTS.md — Instruksjoner for OpenAI Codex, Claude & AI-assistenter

> Dette dokumentet leses automatisk av AI-agenter som fast prosjektkontekst og driftsinstruks.

---

## 1. Hvem vi er og hva vi bygger
- Vi er **to gründere** som eksperimenterer med AI-agenter, databruk, kampanjer og automatisering.
- Prosjektet vårt er **Kunstpixel** — en felles treningsarena og teknologisk verktøykasse.
- **Filosofi:** Hold det enkelt, pragmatisk og raskt. Unngå overkompliserte skyløsninger eller unødvendige tunge rammeverk når rene Python-skript og lokale verktøy løser oppgaven.
- **De 4 formålspunktene:** Se [`00_felles/FORMAAL.md`](00_felles/FORMAAL.md).

---

## 2. Teknisk Miljø og Kjøretid
- **Python:** 3.13 (`py -3.13` på Windows)
- **Database:** SQLite i `05_data/museum.db` (kunstnere, verk, saler, utstillinger, hendelser, publikum_faq)
- **Protokoll:** Model Context Protocol (FastMCP)
- **Tester:** `pytest` med 206 automatiserte tester


---

## 3. Kommandoer AI/Codex kan kjøre
Bruk disse standardkommandoene ved oppgaver i terminalen:

```powershell
# Kjør hele testpakken (skal ALLTID passere 100 %)
py -3.13 -m pytest -v

# Kjør spesifikke testsuiter
py -3.13 -m pytest tests/test_db_quality.py -v     # Datakvalitet og regler
py -3.13 -m pytest tests/test_mcp_server.py -v     # MCP-server verktøy (alle 8)
py -3.13 -m pytest tests/test_agent.py -v          # Museumsvert persona & adferd
py -3.13 -m pytest tests/test_integration.py -v    # E2E integrasjon

# Kjør stresstest for bemanningsplanlegging (30 scenarioer)
py -3.13 src/kunstpixel/data/workforce_planning_test.py

# Start den interaktive verten i CLI
py -3.13 src/cli.py "Hvor finner jeg Skrik?"

# Start lokal web-chat for gründerne (port 8000)
py -3.13 src/kunstpixel/adapters/chat_hub.py

# Start FastMCP-serveren over stdio
py -3.13 src/mcp_server.py

# HR, HMS & Kvalitet (Syntetisk demomodell)
py -3.13 src/hr_cli.py kiosk                     # Generer bemanningsorakel for kiosk
py -3.13 src/hr_cli.py hms "ergonomi"          # Søk i 344 autoritative nasjonale HMS-veiledningspunkter
py -3.13 src/hr_cli.py rules                     # Søk i 8 gjeldende HR/HMS/kvalitetsregler
py -3.13 src/hr_cli.py person E101               # Inspiser verifiserte kompetanser for ansatt
py -3.13 src/hr_cli.py eval E101,E102,E106       # Evaluer bemanningsforslag mot KI-feller (L01-L03)
py -3.13 src/hr_api.py                           # Start lokalt HTTP API (http://127.0.0.1:8765)
py -3.13 src/hr_mcp_server.py                    # Start HR FastMCP-serveren over stdio
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 -Mode manual # Deterministisk verifisering
```

---

## 4. MCP-verktøy tilgjengelig
### Samling og Publikumsvert (5 verktøy i `src/mcp_server.py`):
1. `search_collection(query, artist, title, technique, theme, room_id, limit)`
   - Søker i kunstverk basert på tittel, kunstner, teknikk, tema eller sal.
2. `get_artwork_details(artwork_id)`
   - Henter fullstendig verkskort med kuratert tekst og proveniens.
3. `get_room_artworks(room_id)`
   - Returnerer verk utstilt i en sal i kuratert visningsrekkefølge.
4. `search_events(event_type, date_from, date_to, limit)`
   - Finner kommende omvisninger, foredrag, verksteder og arrangementer.
5. `search_faq(query, category)`
   - Slår opp autoritative svar på åpningstider, billettpriser og fasiliteter.

### Arkiv, Direktør & Drift (3 verktøy i `src/mcp_server.py`):
6. `search_archive_exhibitions(query, year_from, year_to, curator, limit)`
   - Søker i 16 års utstillinger (2010–2026), saler, publikumstall og budsjetter.
7. `search_contractors(kategori, leverandor, aar, limit)`
   - Søker i innleiekontrakter (scenografi, Securitas, AV, konservering, transport).
8. `get_employee_cv(ident)`
   - Henter dype CV-er og personas (utdanning, tidligere arbeidsgivere, publikasjoner).

### Konsoliderte Operative Verktøy (6 nye verktøy i `src/mcp_server.py`):
9. `get_condition_report(artwork_id)`
   - Tilstandsrapport med tilstandsgrad (1–4), luks-grenser, klimakrav og forsikringsverdi.
10. `search_loans(exhibition_id, query, limit)`
    - Søk i 50 historiske kunstlån fra eksterne museer (Nasjonalmuseet, KODE m.fl.) med 3-lags tekst.
11. `get_exhibition_economy(exhibition_id)`
    - Prosjektøkonomi for utstilling (budsjett, innleie, billettinntekter og netto resultat).
12. `search_incidents(kategori, alvorlighetsgrad, sal_id, limit)`
    - Operativ avvikslogg (HMS, sikkerhetshendelser, klimasvingninger, teknisk drift, publikum).
13. `verify_supplier_brreg(orgnr_or_name)`
    - Verifisering mot Brønnøysundregistrenes Enhetsregister (org.form, MVA, ansatte, konkursstatus).
14. `calculate_shift_cost(lonnstrinn, timer, er_kveld, er_helg, er_helligdag)`
    - Lønnsberegning for skift basert på Virke Landsoverenskomst for museer (lønnstrinn 20–65).

### HR, HMS & Kvalitet (12 integrerte verktøy i `src/mcp_server.py` og `src/hr_mcp_server.py`):
15. `count_documented_skill(code, as_of)`
    - Nøyaktig telling av aktive ansatte med verifisert og gyldig kompetansebevis.
16. `propose_kiosk_staffing(work_date, start, end, need)`
    - Deterministisk rangering av skiftkandidater etter etablerte preferansevekter.
17. `lookup_hr_hms_quality_rules(domain, topic, as_of)`
    - Søk i strukturerte prosedyrer på tvers av HR, HMS og KVALITET.
18. `get_competence_catalog()`
    - Komplett katalog over definerte ferdigheter og utløpsbetingelser.
19. `get_staff_member(person_id, as_of)`
    - Henter ansatts personkort, dokumenterte kompetanser og tilgjengelighet.
20. `evaluate_kiosk_proposal(suggested_ids, work_date, need)`
    - Automatisk deterministisk evaluering av bemanningsforslag mot kognitive KI-feller (L01–L03).
21. `audit_shift_compliance(ansatt_id, dato, start, end)`
    - Deterministisk revisjon av skift mot AML kap. 10 (§ 10-8 hviletid 11t og § 10-4 arbeidstid).
22. `check_cleaning_supplier_approval(orgnr)`
    - Kontroll av renholdsleverandør mot Arbeidstilsynets Renholdsregister.
23. `get_job_profile_styrk(kode_or_stilling)`
    - Oppslag på offisiell SSB STYRK-08 yrkeskode, utdanningskrav og minste lønnstrinn.
24. `get_calendar_holiday_info(dato)`
    - Kontroll av bevegelige helligdager (133 % overtidstillegg) og skoleruteferier 2010–2026.
25. `get_ergonomic_rotation_rules(sal_or_station_id)`
    - STAMI ergonomiske retningslinjer, maksimal ståtid (2t) og rotasjonskrav for salverter.
26. `get_sickness_absence_statistics(year, quarter)`
    - Offisiell SSB sykefraværsstatistikk (tabell 12441) og vikarreservefaktor for kultursektoren.
27. `search_hms_guidance(query, topic, limit)`
    - Søk i 344 autoritative nasjonale HMS- og arbeidsmiljøveiledningspunkter (Arbeidstilsynet/BHT).
28. `lookup_handbook(query, handbok, role, limit)`
    - Søk i museets fire virksomhetshåndbøker (Personal, HMS, Drift, Beredskap).


---

## 5. Kritiske Regler for AI-agenter

### Regel 1: Strikt Skrivebeskyttelse mot Databasen (Read-Only)
- Databasen `museum.db` åpnes alltid med `mode=ro`.
- Agenter må ALDRI kjøre eller generere `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER` eller `CREATE`-spørringer mot databasen. Alle datauttrekk skal skje via `src.kunstpixel.core.db` eller MCP-verktøyene.

### Regel 2: Norsk fagspråk og anti-hallusinasjon
- Bruk alltid norsk bokmål for beskrivelser, tekster og meldinger.
- Agentene skal aldri dikte opp fakta, verk, kunstnere eller priser som ikke finnes i databasen. Sjekk `00_felles/ordliste.yaml` for definisjoner.

### Regel 3: Verifiser med tester før ferdigstillelse
- Enhver kodeendring, nytt verktøy eller refaktorering skal verifiseres ved å kjøre `py -3.13 -m pytest`.
- Ingen oppgave regnes som ferdig hvis testene feiler.

### Regel 4: Kvalitetssjekk før analyse
- Før du analyserer data fra `museum.db`: kjør `py -3.13 scripts/db_kvalitet.py` og vis resultatlinjen og eventuelle FEIL/OBS øverst i svaret.
- Er det FEIL: si fra og stopp analysen. Er det OBS: ta det med som forbehold i svaret.

---

## 6. Prosjektstruktur
- `00_felles/`: Formål (`FORMAAL.md`) og begrepsordliste (`ordliste.yaml`).
- `01_inbox/`: Råmateriale, ideer og møtenotater.
- `02_deliverables/`: Søknader, rapporter, kampanjer og publisert innhold.
- `03_team/`: Teamroster og rollebeskrivelser for både mennesker og AI-assistenter.
- `04_knowledge/`: Domenedokumentasjon, rutiner og masterprompter.
- `05_data/`: Autoritativ samlingsdatabase (`museum.db`) og datafiler.
- `src/`: Inngangspunkter (`cli.py`, `mcp_server.py`) og kjernelogikk under `src/kunstpixel/`.
- `tests/`: automatiserte tester som verifiserer datakvalitet, MCP, agent, SSOT, Kategori C og helhet.
- `arkiv/`: Historiske filer, eldre testkjøringer og tidligere proxy-lag.



---

## 7. Datadelen og hosting av Datafinner (les før du rører `05_data/`, `src/kunstpixel/data/` eller `deploy/`)
- **Datadelen kan gjøres av enhver modell som kan Python**, i hvilket som helst verktøy eller i Google Colab. Les `docs/DATAPIPELINE.md` først (kart, kommandoer, regler, oppskrift). Colab: `notebooks/data_pipeline_colab.ipynb`.
- `museum.db` bygges av datafiler (`05_data/*.csv`) via `build_museum_db.py`. Rediger datafilene, aldri databasen. Bare Lars kjører bygget uten `--check`. Bruk `python scripts/db_status_gate.py`.
- Alle nye data har `datakilde` som starter med «syntetisk». `tests/test_data_csv.py` vokter CSV-filene (komma i tekst må stå i anførselstegn).
- Åpent API og valgfritt KI-lag (av som standard, alltid merket AI-forslag): `docs/DATAFINNER_API.md`. Hosting på VPS: `deploy/demo/README.md`.
- Bruk `mcp==1.29.1`. Versjon 2.x brøt Datafinner.
