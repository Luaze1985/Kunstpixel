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
- **Tester:** `pytest` med 112 automatiserte tester

---

## 3. Kommandoer AI/Codex kan kjøre
Bruk disse standardkommandoene ved oppgaver i terminalen:

```powershell
# Kjør hele testpakken (skal ALLTID passere 100 %)
py -3.13 -m pytest -v

# Kjør spesifikke testsuiter
py -3.13 -m pytest tests/test_db_quality.py -v     # Datakvalitet og regler
py -3.13 -m pytest tests/test_mcp_server.py -v     # MCP-server verktøy
py -3.13 -m pytest tests/test_agent.py -v          # Museumsvert persona & adferd
py -3.13 -m pytest tests/test_integration.py -v    # E2E integrasjon

# Start den interaktive verten i CLI
py -3.13 src/cli.py "Hvor finner jeg Skrik?"

# Start lokal web-chat for gründerne (port 8000)
py -3.13 src/kunstpixel/adapters/chat_hub.py

# Start FastMCP-serveren over stdio
py -3.13 src/mcp_server.py
```

---

## 4. MCP-verktøy tilgjengelig
De 5 sentrale verktøyene i MCP-serveren:

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

---

## 6. Prosjektstruktur
- `00_felles/`: Formål (`FORMAAL.md`) og begrepsordliste (`ordliste.yaml`).
- `01_inbox/`: Råmateriale, ideer og møtenotater.
- `02_deliverables/`: Søknader, rapporter, kampanjer og publisert innhold.
- `03_team/`: Teamroster og rollebeskrivelser for både mennesker og AI-assistenter.
- `04_knowledge/`: Domenedokumentasjon, rutiner og masterprompter.
- `05_data/`: Autoritativ samlingsdatabase (`museum.db`) og datafiler.
- `src/`: Inngangspunkter (`cli.py`, `mcp_server.py`) og kjernelogikk under `src/kunstpixel/`.
- `tests/`: 112 automatiserte tester som verifiserer datakvalitet, MCP, agent og helhet.
- `arkiv/`: Historiske filer, eldre testkjøringer og tidligere proxy-lag.
