# Prosjektbrief: Fra samling til publikum (MVP-case 1)

## Mål
Etablere en fullverdig, lokal ende-til-ende treningsprototype for AI-gründere der en samlingsdatabase kobles til spesialiserte agenter via MCP-verktøy for å produsere automatiserte veggtekster og en interaktiv museumsvert.

## Hva skal leveres (Artefakter)
1. **Lokal samlingskatalog:** En strukturert database/datasett med et representativt utvalg kunstverk (10–15 verk) med metadata, teknikk, motiv, sal og tilstand.
2. **MCP-verktøypakke (Samling & Formidling):**
   - `search_collection`: Søk på tittel, kunstner, epoke, motiv.
   - `get_artwork_details`: Hent alle metadata for et spesifikt verk.
   - `get_room_artworks`: Hent alle verk som henger i en gitt sal.
3. **Automatisert innholdsgenerator (Kurator/Formidler):**
   - Tar en verks-ID som input og produserer:
     - Standard veggtekst (70 ord).
     - Audioguide-manus for voksne (90 sek).
     - Oppdagelsesspørsmål for barn.
4. **Interaktiv museumsvert-agent:**
   - En kjøreklar agentprompt som bruker samlingsverktøyene til å svare på publikumsspørsmål med varme og presisjon.

## Suksesskriterier
- Ingen hallusinerte årstall eller kunstnerfakta.
- Agenten henter reell informasjon via MCP-verktøy.
- All generert formidling følger museets kvalitetskrav (50–90 ord per veggtekst).
- Koden og promptene er enkle nok til å brukes direkte som undervisningsmateriale for andre AI-utviklere.
