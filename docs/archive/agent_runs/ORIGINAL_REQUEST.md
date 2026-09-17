# Original User Request

## 2026-09-14T15:02:39Z

Aura Kunstmuseum er en syntetisk SMB-kulturinstitusjon som brukes som treningsarena for AI-gründere. Vi har allerede bygget komplett domenekontekst (glossar, roller, kvalitetsregler, godkjenningsporter), 6 masterprompter for agentroller, og en SQLite-database med 72 rader realistiske museumsdata (12 kunstnere, 16 verk med veggtekster, 6 saler, 3 utstillinger, 8 arrangementer, 12 FAQ-oppslag).

**Oppdraget:** Bygg en kjørbar demo-prototype som verifiserer at hele denne bedriftskonteksten faktisk *fungerer* — at agentene kan bruke verktøyene, at dataen er realistisk nok, og at det føles som en ekte liten museumsbedrift i drift.

Working directory: g:/Min disk/Fellesprosjekt KI/
Integrity mode: benchmark

## Eksisterende filer teamet MÅ lese og bruke

Disse filene er allerede opprettet og skal brukes som kilde — ikke overskrives:

- `CONTEXT.md` — domeneglossar med låst fagspråk
- `context/core/` — verdier, beslutningsregler, kvalitetsregler, godkjenningsgrenser
- `context/roles/` — rolleinstrukser for 6 agenter
- `context/operations/workflows.md` — 3 kjernearbeidsflyter
- `context/operations/tool_access.md` — verktøymatrise og sikkerhetsregler
- `prompts/` — 6 ferdige masterprompter (museumsdirektør, samlingsforvalter, kurator, formidler, museumsvert, driftsansvarlig)
- SQLite-databasen som allerede er populert via MCP (tabeller: kunstnere, verk, saler, utstillinger, utstilling_verk, hendelser, publikum_faq)
- `data/samling.json` — JSON-speiling av samlingen

## Requirements

### R1. MCP-server med samlingsverktøy

Lag en MCP-server som eksponerer verktøy for å interagere med museets SQLite-database. Verktøyene skal dekke de tre kjernebruksmønstrene beskrevet i `context/operations/workflows.md`:

1. **Samlingssøk:** Søk etter verk basert på kunstner, tittel, teknikk, temaer eller sal.
2. **Verksdetaljer:** Hent komplett metadata for et spesifikt verk (inkludert veggtekst og proveniens).
3. **Salsoversikt:** List alle utstilte verk i en gitt sal med rekkefølge.
4. **Arrangementssøk:** Finn kommende hendelser, filtrert på type eller dato.
5. **FAQ-oppslag:** Søk i publikums-FAQ etter relevant svar.

### R2. Interaktiv museumsvert-agent

Lag en kjørbar agent (prompt + verktøytilkobling) som bruker MCP-serveren fra R1 til å svare på realistiske besøkendes henvendelser. Agenten skal bruke masterprompten i `prompts/museumsvert.md` og følge kvalitetsreglene i `context/core/quality_rules.md`.

### R3. Integrasjonstest — «Bedriften virker»

Lag en automatisert testpakke som kjører et sett representative scenarier gjennom hele stacken (MCP-verktøy → agent → svar) og verifiserer at bedriftskonteksten henger sammen som en realistisk, operativ museumsinstitusjon.

## Acceptance Criteria

### MCP-server fungerer
- [ ] Alle 5 verktøy fra R1 returnerer korrekte, verifiserbare resultater fra den eksisterende SQLite-databasen
- [ ] Søk etter «Kittelsen» returnerer minst 2 verk med korrekte metadata
- [ ] Søk etter sal «SAL-D» returnerer minst 3 utstilte verk
- [ ] Arrangementssøk returnerer kommende hendelser med riktig dato og type
- [ ] FAQ-oppslag for «åpningstider» returnerer et svar som inneholder konkrete klokkeslett

### Museumsvert er realistisk
- [ ] Agenten besvarer «Hvor finner jeg Skrik?» med korrekt salhenvising (Sal D) hentet fra databasen
- [ ] Agenten besvarer «Hva koster det?» med faktiske priser fra FAQ-tabellen
- [ ] Agenten besvarer «Hva anbefaler du hvis jeg har 30 minutter?» med et personlig forslag basert på faktiske utstilte verk
- [ ] Agenten finner aldri på kunstnerfakta eller årstall som ikke finnes i databasen
- [ ] Agentens tone matcher stilreglene i masterprompten (vennlig, konkret, ikke akademisk)

### Bedriften virker som en helhet
- [ ] Testpakken kjører minst 8 forskjellige scenarier (minst 2 per kategori: samling, utstilling, hendelse, praktisk)
- [ ] Ingen scenario gir feilmelding eller tomt svar
- [ ] Veggtekstene som allerede ligger i databasen følger kvalitetsreglene (50-90 ord, riktig format)
- [ ] Verktøymatrisen i `context/operations/tool_access.md` overholdes: museumsvert-agenten kan IKKE skrive til databasen
