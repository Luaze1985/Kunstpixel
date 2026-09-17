# AGENTS.md — Instruksjoner for OpenAI Codex & ChatGPT

> Dette dokumentet leses automatisk av **OpenAI Codex** (i ChatGPT desktop-app, Workspaces og Codex CLI) som fast prosjektkontekst og driftsinstruks.

---

## 1. Hvem vi er og hva vi bygger
- Vi er **to gründere** som eksperimenterer med AI-agenter, plugins, automatiseringer og digitale tvillinger.
- Prosjektet vårt er **Aura Kunstmuseum** — en syntetisk, men ultra-realistisk SMB-kulturinstitusjon som fungerer som treningsarena og testbed for agent-arbeidsflyter.
- **Filosofi:** Hold det enkelt, pragmatisk og raskt. Unngå overkompliserte skyløsninger eller unødvendige tunge rammeverk når rene Python-skript og lokale verktøy løser oppgaven.

---

## 2. Teknisk Miljø og Kjøretid
- **Python:** 3.13 (`py -3.13` på Windows)
- **Database:** SQLite i `05_data/museum.db` (72 rader: kunstnere, verk, saler, utstillinger, hendelser, publikum_faq)
- **Protokoll:** Model Context Protocol (FastMCP)
- **Tester:** `pytest` med 112 automatiserte tester

---

## 3. Kommandoer Codex kan kjøre
Codex skal bruke disse standardkommandoene ved oppgaver i terminalen:

```powershell
# Kjør hele testpakken (skal ALLTID passere 100 %)
py -3.13 -m pytest -v

# Kjør spesifikke testsuiter
py -3.13 -m pytest tests/test_db_quality.py -v     # Datakvalitet og kuratoriske regler
py -3.13 -m pytest tests/test_mcp_server.py -v     # MCP-server verktøy
py -3.13 -m pytest tests/test_agent.py -v          # Museumsvert persona & adferd
py -3.13 -m pytest tests/test_integration.py -v    # E2E integrasjon

# Start den interaktive museumsverten i CLI
py -3.13 src/cli.py "Hvor finner jeg Skrik?"

# Start lokal web-chat for gründerne (port 8000)
py -3.13 src/kunstpixel/adapters/chat_hub.py

# Start FastMCP-serveren over stdio
py -3.13 -m src.kunstpixel.core.mcp_server
```

---

## 4. MCP-verktøy tilgjengelig for Codex
Codex er konfigurert via `.codex/config.toml` til å koble seg direkte på museets MCP-server over `stdio`. De 5 verktøyene er:

1. `search_collection(query, artist, title, technique, theme, room_id, limit)`
   - Søker i kunstverk basert på tittel, kunstner, teknikk, tema eller sal.
2. `get_artwork_details(artwork_id)`
   - Henter fullstendig verkskort med kuratert veggtekst (50–90 ord) og proveniens.
3. `get_room_artworks(room_id)`
   - Returnerer verk utstilt i en sal (SAL-A til SAL-E) i kuratert visningsrekkefølge.
4. `search_events(event_type, date_from, date_to, limit)`
   - Finner kommende omvisninger, foredrag, verksteder og konserter.
5. `search_faq(query, category)`
   - Slår opp autoritative svar på åpningstider, billettpriser, adgang og fasiliteter.

---

## 5. Kritiske Regler for Codex

### Regel 1: Strikt Skrivebeskyttelse mot Databasen (Read-Only)
- Databasen `museum.db` åpnes alltid med `mode=ro`.
- Codex må ALDRI kjøre eller generere `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER` eller `CREATE`-spørringer mot databasen. Alle datauttrekk skal skje via `src.aura_museum.core.db` eller MCP-verktøyene.

### Regel 2: Norsk fagspråk og anti-hallusinasjon
- Bruk alltid norsk bokmål for museumsbeskrivelser, veggtekster, roller og feilmeldinger.
- Agentene og Codex skal aldri dikte opp kunstverk, kunstnere eller priser som ikke finnes i databasen. Dersom noe mangler, opplys om det på en vennlig måte.

### Regel 3: Verifiser med tester før ferdigstillelse
- Enhver kodeendring, nytt verktøy eller refaktorering skal verifiseres ved å kjøre `py -3.13 -m pytest`.
- Ingen oppgave regnes som ferdig hvis testene feiler.

---

## 6. Prosjektstruktur
- `src/aura_museum/` & `src/kunstpixel/`: Kjerneimplementasjon (`db.py`, `agent.py`, `mcp_server.py`, `config.py`).
- `src/cli.py` & `src/kunstpixel/adapters/chat_hub.py`: Brukergrensesnitt for gründerne.
- `05_data/museum.db` & `05_data/samling.json`: Autoritativ samlingsdatabase og eksport.
- `04_knowledge/`: Domenedokumentasjon, roller, kvalitetskrav og masterprompter.
- `tests/`: 112 automatiserte tester fordelt på datakvalitet, MCP, agent og helhetsscenarier.
