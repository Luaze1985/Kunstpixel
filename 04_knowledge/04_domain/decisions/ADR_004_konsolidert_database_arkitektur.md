# ADR 004: Konsolidert databasearkitektur i museum.db

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Tidligere har prosjektet hatt to adskilte SQLite-databaser: `05_data/museum.db` (samling, verk, saler, dagsbesøk, FAQ) og `05_data/kunstpixel_historikk.db` (54 994 vakter, 102 utstillinger, 318 innleiekontrakter, 28 personas). Dette skapte en risiko for split-brain, dupliserte tabellnavn og manglende referanseintegritet mellom samling og intern drift.

---

## Beslutning
Vi slår sammen alle tabeller og datasett til **én konsolidert SQLite-database**: `05_data/museum.db`.
1. **Felles SSOT (Single Source of Truth):**  
   Alle 6 roller i masterprompten spør mot én samlet database.
2. **Ekte referanseintegritet (Foreign Keys):**  
   Fremmednøkler håndheves på tvers av verk, utstillinger, innleie, vakter, personas og avvik.
3. **Strikt Read-Only tilgang:**  
   AI-agenter og MCP-tjenester åpner alltid `museum.db` med `mode=ro` (jf. Regel 1 i AGENTS.md). All berikelse og mutasjon skjer via deterministiske Python-skript.

---

## Konsekvenser
- **Eliminerer split-brain:** En utstilling har nå direkte relasjoner til utstilte verk, ansvarlig kurator, vaktplan og innleiekontrakter i samme database.
- **Enklere vedlikehold og testing:** Testsuiter og FastMCP-tjenester trenger kun én databaseforbindelse.
- **Arkivering:** `kunstpixel_historikk.db` beholdes som historisk backup i `05_data/arkiv/`.
