# ADR 014: Morgensløyfe med Informasjonsjeger, Direkte Oppdatering og Automatisk Tilbakerulling

## Status
Godkjent (2026-11-04, grilling med Lars)

## Kontekst
De opprinnelige fire automasjonene (`data-builder`, `engine-builder`, `colab-mcp`, `sentinel`) fungerte kun som et internt samlebånd som resirkulerte eksisterende lokale data uten å hente inn manglende kunnskap, lovhjemler eller operative prosedyrer utenfra. I tillegg brukte `colab-mcp` en hel agentøkt hver dag på å sjekke en lokal mappe (`01_inbox/incoming/`), noe `scripts/colab_sync.py` gjør deterministisk på 0,1 sekunder uten tokens.

Samtidig avdekket kartleggingen av `handbok_oppslag` to konkrete kvalitetsgap:
1. Mange håndbokpunkter falt tilbake på kopierte, generiske samlehjemler fra dokumenttoppen (f.eks. stod «Matloven / Mattilsynet / Renholdsregisteret» som lovhjemmel på både billettsalg, universell utforming, klimakontroll og kunstlån).
2. `04_knowledge/02_sops/` inneholdt kun fire HR-rutiner (`SOP-001` til `SOP-004`), og manglet helt operative standardprosedyrer (SOP) for HMS/vernerunde, brann/Restverdiredning (RVR), IK-Mat/HACCP og daglig åpning/stenging/klimatilsyn.

## Beslutning
1. **Firetrinns morgensløyfe med 15 minutters avstand (09:00–09:45):**
   - **Kl. 09:00 – Informasjonsjeger & Prosedyrebygger:** Skanner etter kunnskapshull i håndbøker, SOP-er og tabeller, søker opp autoritative norske kilder (Lovdata, Arbeidstilsynet, STAMI, Mattilsynet, DSB, ICOM, SSB) og oppdaterer Markdown-håndbøker, SOP-er og CSV-kilder direkte.
   - **Kl. 09:15 – Kontrollport, Colab-synk & Databygger:** Kjører `colab_sync.py` (0 tokens), indekserer håndbøker/SOP-er, bygger `museum.db` og kjører full `pytest` og `db_status_gate.py`.
   - **Kl. 09:30 – Motor- og Funksjonsbygger:** Videreutvikler og verifiserer kjernelogikk i `src/kunstpixel/core/` mot oppdatert database.
   - **Kl. 09:45 – Systeminspektør & Fornuftsvakt (Sentinel):** Kjører `database-inspektor`, Mermaid ERD og Tracer Bullet-kontroll på tvers av SQL og API.
2. **Direkte oppdatering med umiddelbar tilbakerulling ved testfeil:**
   - Informasjonsjegeren skriver direkte til håndbøker, SOP-er og CSV-er for å unngå manuelle flaskehalser i morgensløyfen.
   - Dersom `pytest` eller `db_status_gate.py` feiler i kontrollsteget kl. 09:15, rulles de uverifiserte filendringene automatisk tilbake (`git checkout --`) slik at `05_data/museum.db` aldri forurenses.
3. **Forbud mot generiske samlehjemler og krav om komplett SOP-dekning:**
   - Hvert eneste avsnitt i virksomhetshåndbøkene og hver SOP skal ha en seksjonsspesifikk, reell lov-, forskrifts- eller standardhjemmel i `handbok_oppslag`.
   - `tests/test_handbook_compliance.py` håndhever dette maskinelt: ethvert punkt som faller tilbake på en generisk samlehjemmel feiler i `pytest`.

Begrepet `informasjonsjeger_og_funnkontroll` er definert i `00_felles/ordliste.yaml`.

## Konsekvenser
- **Positivt:** Morgensløyfen tilfører reell ny verdi og tetter faglige hull automatisk uten manuell godkjenningsblokkering.
- **Positivt:** Vi sparer en hel daglig agentøkt ved å erstatte den passive Colab-sidecaren med 0-token-skriptet `colab_sync.py` inne i databyggeren.
- **Risiko og sikring:** Fordi funn skrives direkte til kildefiler, er `pytest` og `db_status_gate.py` eneste barriere før `museum.db`. Testsuiten må derfor ha strenge innholds- og hjemmelskrav.
