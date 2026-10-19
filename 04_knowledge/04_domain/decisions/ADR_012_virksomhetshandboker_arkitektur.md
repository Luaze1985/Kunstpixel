# ADR 012: To-lags Arkitektur for Virksomhetshåndbøker (Personal, HMS, Drift, Ledelse)

## Status
Godkjent (2026-10-19)

## Kontekst
Aura Kunstmuseum / Kunstpixel har etablert omfattende datastrukturer i `museum.db` og operative retningslinjer spredt i enkeltfiler (`KVALITETS_OG_STYRINGSSYSTEM.md`, `museumsrutiner.md`, `hms_veiledning_nasjonal.yaml`, ADR-ene 001–011). 
For at virksomheten skal fungere realistisk i hverdagen for både mennesker (ansatte, verter, kafépersonale, ledelse) og KI-assistenter, er det behov for en autoritativ håndbokpakke. 

Tradisjonelle PDF-håndbøker blir passive hyllevarmere som verken kan vedlikeholdes smidig eller konsumeres effektivt av språkmodeller og CLI-verktøy uten å overbelaste kontekstvinduet.

## Beslutning
Det etableres en 4-delt håndbokpakke med en **to-lags arkitektur**:

1. **Menneskelesbart dokumentasjonslag (Markdown):**
   - `04_knowledge/01_governance/handboker/01_personalhandbok.md` (HR, AML kap. 10, Virke-tariff, fravær, etikk)
   - `04_knowledge/01_governance/handboker/02_hms_sikkerhetshandbok.md` (Internkontroll, STAMI-ergonomi, løft, brann, RVR-kunstevakuering, RUH)
   - `04_knowledge/01_governance/handboker/03_drifts_kvalitetshandbok.md` (Vertskap, universell utforming, åpne/stenge, IK-mat/HACCP, skjenking, renhold)
   - `04_knowledge/01_governance/handboker/04_leder_beredskapshandbok.md` (Sykefraværsoppfølging, kriseledelse, varsling AML § 2 A, anskaffelser)

2. **System- og agentlesbart oppslagslag (SQLite & FastMCP):**
   - Ny tabell i `05_data/museum.db`: `handbok_oppslag`
   - Strukturerte felter: `punkt_id`, `handbok_kode`, `kapittel_nr`, `kapittel_tittel`, `tema`, `malgruppe`, `lovhjemmel`, `regeltekst`, `tiltak_sjekkliste`, `siste_revidert`.
   - FastMCP-verktøy nr. 27: `lookup_handbook(query, handbok, role, limit)` i `src/kunstpixel/core/mcp_server.py`.
   - Deterministisk selektivitet: Tillater presise uttrekk på millisekunder uten å lese hele dokumenter.

## Konsekvenser
- **Positivt:** 100 % transparens for ansatte og ledere. Hvert enkelt punkt har klar forankring i norsk lovverk (AML, Internkontrollforskriften, Matloven, Brann- og eksplosjonsvernloven, Virke-tariffen).
- **Positivt:** Null token-sløsing; agenter og CLI kan hente eksakte regler på sekunder ved behov.
- **Oppfølging:** Ved revisjon av en håndbok kjøres ingest-skriptet `py -3.13 src/kunstpixel/data/seed_handbooks.py` for å synkronisere databasen.
