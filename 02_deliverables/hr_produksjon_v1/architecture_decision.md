# Arkitekturvurdering: Integrasjon i AI-native HR-plattform

Dato: 2026-10-21  
Status: Anbefalt  
Evaluator: Senior AI Utviklingsagent

## 1. Kontekst og Formål
Oppdraget krever en vurdering av hvordan det kvalitetssikrede HR-datagrunnlaget (AP0–AP9, 94 fasitspørsmål, 212 regler og 58 tabeller) best kan driftes og tilgjengeliggjøres for tre roller:
- **Ansatte:** Selvbetjening, personalhåndbok, fraværsregistrering og rettighetsavklaring.
- **Ledere:** Bemanning, avviksoppfølging, HMS og beslutningsstøtte.
- **HR/Stab:** Tariffstyring, likelønnsanalyse (ARP), statistikk og compliance.

For å overholde arbeidsregel 8 («Ikke bygg funksjonalitet som allerede finnes og fungerer i et egnet åpen kildekode-system») er tre ledende åpen kildekode-løsninger evaluert mot de dokumenterte egenskapene.

---

## 2. Evaluering av Eksisterende Åpen Kildekode-Systemer

### A. MintHCM (vurdert mot kodebasen `minthcm-minthcm-8a5edab282632443.txt`)
- **Teknologi:** PHP, bygget på SuiteCRM/SugarCRM-rammeverket, MySQL/MariaDB.
- **Dokumenterte egenskaper:**
  - Inneholder en dedikert `McpController.php` med full OAuth2 flow (`/mcp/authorize`, `/mcp/deny`, consent tokens), noe som bekrefter at MintHCM har offisiell satsing på Model Context Protocol.
  - Modulen `AIPromptTemplates` muliggjør administrasjon av systemprompter og maler for KI-interaksjon.
  - Omfattende HR-funksjonalitet: Stillinger (`Positions`), rekruttering (`Recruitments`), tidsregistrering og sidepaneler.
  - Kraftig rolle- og tilgangsstyring via `ACL`, `ACLRoles` og `ACLActions`.
- **Svakheter for Kunstpixel:**
  - PHP/SuiteCRM-arkitekturen har betydelig teknisk gjeld og et tungt fotavtrykk.
  - Integrasjon mot Kunstpixels eksisterende Python 3.13-stack (`museum.db`, FastMCP, `pytest`) krever separate PHP-fpm-containere og ekstra driftsoverhead.
  - Norsk tarifflogikk (Virke, KS) og særavtaler må skrives i PHP/Vardefs.

### B. Frappe HR (Frappe Framework / ERPNext)
- **Teknologi:** Python, MariaDB/PostgreSQL, Redis, Vue.js.
- **Dokumenterte egenskaper:**
  - 100 % Python-basert backend. Passer perfekt med prosjektets Python 3.13-kjøretid.
  - DocType-metamodellen tillater deklarativ definisjon av de 58 tabellene fra `datasett_forslag.yaml` som egne DocTypes på minutter.
  - Svært moden kjerne for permisjonssøknader, skiftplanlegging, timeregistrering, lønnskjøring og personalmapper.
  - Eksisterende REST- og GraphQL-API-er som enkelt kan eksponeres via en tynn Python FastMCP-adapter.
- **Vurdering:** Klart beste operasjonelle kjerne for dataforvaltning, skift, lønn og ansattdata.

### C. Onyx (tidligere Danswer)
- **Teknologi:** Python/FastAPI, Postgres, Qdrant/Vespa (Vektorsøk), Next.js.
- **Dokumenterte egenskaper:**
  - Spesialdesignet for AI-native kunnskapssøk, RAG og chat over virksomhetsdokumenter.
  - Innebygd støtte for dokumentnivå-tilgangskontroll (RBAC), slik at en ansatt kun får svar basert på dokumenter vedkommende har innsyn i.
  - Kobler seg enkelt til eksterne kilder (Lovdata, Arbeidstilsynet, interne håndbøker i Markdown/PDF).
- **Vurdering:** Klart beste grensesnitt for språkmodell-basert veiledning, søk i personalhåndbok og kildebasert dialog.

---

## 3. Anbefalt Målarkitektur: Tredelt Hybrid

```
                          ┌─────────────────────────────────────┐
                          │     BRUKERFLATE / KLIENTER          │
                          │ (Ansatt, Leder, HR-stab, Chat Hub)   │
                          └──────────────────┬──────────────────┘
                                             │
                                             ▼
                          ┌─────────────────────────────────────┐
                          │      KUNSTPIXEL AGENT GATEWAY       │
                          │   (Python FastMCP / RBAC Sikkerhet) │
                          └──────┬───────────────────────┬──────┘
                                 │                       │
               ┌─────────────────┴─────┐   ┌─────────────┴─────────────────┐
               │  OPERASJONELL KJERNE  │   │     KUNNSKAP & REGELMOTOR     │
               │      (Frappe HR)      │   │         (Onyx + SQLite)       │
               ├───────────────────────┤   ├───────────────────────────────┤
               │ - Ansattregister      │   │ - 94 Fasitspørsmål            │
               │ - Vaktplan & Stempling│   │ - 212 Klassifiserte Regler    │
               │ - Lønnsarter & Tariff │   │ - Personal-/HMS-håndbøker     │
               │ - Fraværsadministrasjon│  │ - Kildebevis (Lov/Tariff)     │
               └───────────────────────┘   └───────────────────────────────┘
```

### Rollegrenser og Sikkerhet:
1. **Ansatt:** Får lese egne vakter, registrere egenmelding, og stille spørsmål til håndboken. Ingen innsyn i kollegers lønn, fravær eller vurderinger.
2. **Leder:** Får se vaktplan for eget team, godkjenne timeavvik, registrere HMS-hendelser og se anonymiserte trivselsrapporter ($k \ge 5$).
3. **HR/Stab:** Full administrasjon av tariffavtaler, stillingskataloger, lønnsdata og aggregerte likelønnsanalyser (ARP).
4. **KI-Agent Sperrer:**
   - Databasen åpnes strengt i `mode=ro` for KI-oppslag.
   - Ingen muterende endringer (f.eks. godkjenning av overtid, endring av lønn eller oppsigelse) utføres autonomt av KI uten eksplisitt menneskelig saksbehandlergodkjenning.
