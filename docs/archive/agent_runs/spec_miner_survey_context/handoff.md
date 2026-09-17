# Handoff Report: Domene- og Kontekstspesifikasjon for Aura Kunstmuseum

**Dato:** 2026-09-14  
**Agent:** spec_miner_survey_context (Specification Miner Archetype)  
**Oppdrag:** Kartlegge og formalisere alle spesifikasjoner, regler, avgrensninger og kontrakter fra museets autoritative kontekstfiler, instrukser og prompter.

---

## 1. Observation

Vi har utført en systematisk, kildekritisk undersøkelse av alle relevante styrings- og kontekstdokumenter i prosjektet. Observasjonene baserer seg på følgende autoritative primærkilder:

1. `CONTEXT.md` (linje 1–46): Fastsetter offisiell fagspråksdefinisjon og 10 eksplisitte «Avoid»-termer for å unngå kommersiell/teknisk sjargong:
   - **Kunstmuseum** (_Avoid_: Galleri, kunsthall, utstillingslokale)
   - **Samling** (_Avoid_: Beholdning, varelager, inventar)
   - **Verk** (_Avoid_: Vare, objekt, artefakt)
   - **Samlingsdatabase** (_Avoid_: Filarkiv, varelager, database)
   - **Utstilling** (_Avoid_: Showcase, messe, event)
   - **Kuratere** (_Avoid_: Redigere, publisere, sette sammen)
   - **Formidling** (_Avoid_: Markedsføring, reklame, PR, kundeservice)
   - **Veggtekst** (_Avoid_: Skilt, etikett, plakat, produktbeskrivelse)
   - **Museumsvert** (_Avoid_: Supportagent, helpdesk-medarbeider, billettselger)
   - **Proveniens** (_Avoid_: Transaksjonshistorikk, opprinnelseslogg)

2. `context/core/company.md` (linje 1–20): Fastsetter virksomhetskontekst:
   - Navn: Aura Kunstmuseum (syntetisk SMB-kulturinstitusjon)
   - Status: Operativ, uavhengig ideell stiftelse / SMB-foretak med flate beslutningslinjer.
   - Formål: Forvalte, bevare og formidle visuell kunst; operativ treningsarena og testbenk for AI-gründere til å utvikle plugins, MCP-verktøy, automatiseringer og undervisningsopplegg.
   - Omfang: Mellomstort kunstmuseum, 12–15 kjernefunksjoner, ca. 2 500 katalogiserte verk, 4 sesongutstillinger per år + fast samling.
   - Driftsmodell: Slank, agil administrasjon med høy grad av automatisering i rutineoppgaver.

3. `context/core/values.md` (linje 1–17): Definerer fire ufravikelige kjerneverdier:
   - 1. Faglig integritet: Fakta forankres i verifiserte kilder eller samlingsdatabasen. Nulltoleranse for hallusinerte fakta om kunstverk. Mangler informasjon merkes den som ukjent.
   - 2. Inkluderende og levende formidling: Unngå artspeak; formidlingen skal være presis, engasjerende og tilpasset ulike målgrupper.
   - 3. Nysgjerrig teknologibruk med menneskelig varme: Bruk av KI til å berike publikumsopplevelsen og avlaste rutiner uten å fjerne menneskelig varme.
   - 4. Åpenhet og sporbarhet: AI-generert innhold merkes og etterprøves; full sporbarhet over hvem som har foreslått, endret eller godkjent leveranser.

4. `context/core/decision_rules.md` (linje 1–19):
   - Prioriteringsrekkefølge: 1. Sikkerhet og etikk -> 2. Publikums- og formidlingsverdi -> 3. Lærings- og treningsverdi for AI-gründere -> 4. Prosess- og formatperfeksjonisme.
   - Sannhetsregler: Fakta over antakelser (mangler opplysning merkes den som ukjent/hypotese); motstridende kilder varsles og eskaleres; ingen hemmelig gjetning.
   - Beslutningsmyndighet: Menneskelig eier (strategi, budsjett, ekstern publisering) -> Museumsdirektør (operasjonell prioritering, intern koordinering) -> Fagspesialister (kurator, samlingsforvalter, formidler, drift innen eget domene).

5. `context/core/quality_rules.md` (linje 1–23):
   - Faglige tekster og veggtekster: Lengdebegrensning mellom 50 og 90 ord (aldri over 120 ord). Fast struktur: Linje 1: Kunstnernavn, nasjonalitet, levetid; Linje 2: Tittel (kursiv), datering, teknikk, samlings-ID; Avsnitt 1: Hva betrakteren ser (blikkfang / visuell inngang); Avsnitt 2: Kontekst / betydning / hvorfor verket er vesentlig. Språk: Klart, tilgjengelig, unngå uforklart sjargong.
   - Audioguider og muntlige manus: Maks 60–90 sekunder per verk (ca. 130–180 ord opplest). Fortellende, varm, veiledende tone.
   - Barne- og familieformidling: Inkluder en sanselig observasjon eller åpent spørsmål («Hva tror du personen tenker på?», «Finn tre dyr i bildet»). Enkel syntaks, nysgjerrighetsdrevet, fri for tørre årstallrekker.
   - Dataintegritet og teknisk kvalitet: Alle verksoppslag må inkludere unikt inventarnummer (f.eks. `AURA-2026-042`). Alle JSON-strukturer og API-kall typesjekkes og valideres mot skjema før persistens.

6. `context/core/approval_boundaries.md` (linje 1–24): Tredelt risikokontrollmatrise:
   - Nivå 1 (Full agentautonomi): Søke og lese i samlingsdatabase via MCP, analysere metadata, generere utkast, besvare interne henvendelser, kjøre tester.
   - Nivå 2 (Faglig godkjenning): Fellesbibliotek (ownCloud), endre metadata/tilstandsrapporter, godkjenne utstillingsliste.
   - Nivå 3 (Menneskelig eiergodkjenning påkrevd): Publisere eksternt (nettside, SoMe, nyhetsbrev), ekstern kommunikasjon/e-post, endre billettpriser, inngå avtaler, slette/overskrive historiske verk/data, utvide tilganger.

7. `context/core/owner_intent.md` (linje 1–21) & `docs/adr/0001-lean-independent-museum-model.md`: AI-gründer treningsverdi prioriteres over unødig forvaltningsbyråkrati. Menneskelig eier beholder suverenitet over visjon, etikk, økonomi og publisering.

8. `context/roles/` (6 filer):
   - `museumsdirektor.md`: Operasjonell leder, delegere oppgaver, godkjenne utkast, eskalere Nivå 3.
   - `samlingsforvalter.md`: Registrar, accessioning (`AURA-YYYY-NNN`), 9 obligatoriske felt, proveniensformat, 5 tilstander.
   - `kurator.md`: Kunstfaglig profil, utstillingsideer, verkutvalg, kunsthistoriske tekster uten artspeak.
   - `formidler.md`: Veggtekster (50–90 ord), audioguide (60–90 sek, 130–180 ord), barneformidling.
   - `museumsvert.md`: Frontoffice publikumsvert, kun lesetilgang, veilede, anbefale, besvare FAQ.
   - `driftsansvarlig.md`: Logistikk, kalender, billettering, avvik, arrangementssjekkliste.

9. `context/operations/workflows.md` (linje 1–62): Tre kjernearbeidsflyter:
   - Arbeidsflyt 1: Verk-inntak og berikelse (Rådata -> ID -> MCP-metadata -> Skjemavalidering -> Persistering -> Status «Registrert / Magasin»).
   - Arbeidsflyt 2: Utstillingsproduksjon og innholdsgenerering (Initiativ -> Kurator-søk 10–15 verk -> Utvalg & salplassering -> Formidler produserer innholdspakke -> Review -> Lagring).
   - Arbeidsflyt 3: Interaktiv museumsvert (Publikumshenvendelse -> Analyse -> MCP-kall `search_collection` & `get_artwork_location` -> Varmt, presist svar med salhenvisning og formidling -> Ruteanbefaling).

10. `context/operations/tool_access.md` (linje 1–18):
   - Minste privilegium: Museumsvert har kun `sqlite_read_public` og `faq_search`. Forbud mot skriveoperasjoner.
   - Sikkerhetsregel 1: Skrivebeskyttelse av samling (validering av obligatoriske felt).
   - Sikkerhetsregel 2: Ingen rå SQL fra åpne promptflater (kun forhåndsdefinerte, parameteriserte funksjonskall).
   - Sikkerhetsregel 3: Ingen persondata i treningsdata.

11. `prompts/museumsvert.md` (linje 1–98): Masterprompt for verten:
   - Rolle: Museets ansikt utad, vennlig, tålmodig, entusiastisk formidler, ikke kunsthistoriker.
   - Kun lesetilgang (`read_query` / MCP-verktøy). Aldri skrive til databasen.
   - 5 mentale kategorier: Praktisk (FAQ), Samling (verk/kunstnere), Utstilling (utstillinger/verk), Hendelse (hendelser), Anbefaling.
   - 4-delt svarstruktur: 1. Direkte svar (fakta), 2. Kort formidlingsdetalj, 3. Praktisk retning (sal/etasje), 4. Tilleggsforslag.
   - 4 absolutte begrensninger: Aldri dikte opp fakta/tider/priser/plassering; Aldri skrive til database; Aldri gi udokumenterte tolkninger; Være ærlig når noe er stengt/utilgjengelig.

12. `prompts/samlingsforvalter.md` (linje 23–46):
   - 9 obligatoriske felt ved nyregistrering: `id`, `tittel`, `kunstner_id`, `aar`, `teknikk`, `dimensjoner`, `sal_id`, `status`, `tilstand`.
   - Inventarnummer: `AURA-YYYY-NNN`.
   - Tilstandsverdier (enum): `utmerket`, `god`, `akseptabel`, `skadet`, `ukjent`.

13. `context/projects/samling_til_publikum/brief.md` (linje 8–12):
   - MCP-verktøypakke: `search_collection`, `get_artwork_details`, `get_room_artworks`.

14. `data/samling.json`: Inneholder 12 representative kunstverk med tittel, kunstner, datering, teknikk, dimensjoner, sal, status, tema og veggtekst-status.

---

## 2. Logic Chain

1. **SMB-institusjonell forankring og formål:** Aura Kunstmuseum er en uavhengig ideell SMB-institusjon etablert som treningsarena for AI-gründere (ADR-0001, `company.md`). Løsningen skal være smidig, lokal og lettbeint (lokal SQLite/JSON og MCP), men samtidig ha streng faglig integritet.
2. **Kildetrohet og nulltoleranse for hallusinasjoner:** Kjerneverdi 1 (`values.md`), beslutningsregel 1 (`decision_rules.md`) og risikopost RSK-001 krever at all verksinformasjon som formidles til publikum skal være 100 % forankret i verifiserte data fra samlingsdatabasen. Dersom et årstall, en teknikk eller en biografisk detalj ikke finnes i databasen, er det forbudt å dikte opp svaret; agenten skal da eksplisitt opplyse om at informasjonen er ukjent eller henvise til godkjent formidlingstekst.
3. **Sikkerhet, minste privilegium og rå SQL-forbud:** `tool_access.md` og `prompts/museumsvert.md` slår fast at museumsverten er et eksternt/publikumsrettet kontaktpunkt. For å forhindre SQL-injeksjon og datamanipulasjon tillates **ingen rå SQL** fra åpne promptflater. Datatilgang skal utelukkende skje via forhåndsdefinerte, parameteriserte MCP-verktøykall. Museumsverten tildeles **strikt lesetilgang** (`sqlite_read_public`, `faq_search`).
4. **Verktøykrav for de 5 samlingsfunksjonene:** For å realisere arbeidsflytene i `workflows.md` og innfri kravene i `ORIGINAL_REQUEST.md` (R1 & R2), må de fem MCP-verktøyene dekke:
   - `search_collection`: Fleksibelt søk på kunstner, tittel, teknikk, tema og sal.
   - `get_artwork_details`: Oppslag av samtlige metadata, godkjent veggtekst og proveniens for en gitt verks-ID.
   - `get_room_artworks`: Henting av alle utstilte verk i en gitt sal, ordnet etter visningsrekkefølge.
   - `search_events`: Søk etter bekreftede, fremtidige hendelser (omvisninger, verksteder, foredrag).
   - `search_faq`: Søk etter autoritative svar på praktiske spørsmål (åpningstider, billettpriser, fasiliteter).
5. **Kvalitetsstyring av formidling og anbefalinger:** Ifølge `quality_rules.md` og `prompts/formidler.md` må veggtekster ha mellom 50 og 90 ord, starte med det visuelle foran bildet, unngå sjargong/artspeak og bruke aktive verb. Anbefalinger fra museumsverten (f.eks. «30 minutter») må utelukkende velge verk som faktisk har status `utstilt` og en tildelt publikumssal. Verk i magasin eller under konservering skal aldri anbefales som utstilt.
6. **E2E-verifikasjon og helhetlig systemtest:** `ORIGINAL_REQUEST.md` (R3) krever minst 8 scenarier fordelt på fire kategorier (`samling`, `utstilling`, `hendelse`, `praktisk`) med minst 2 per kategori. Hvert scenario må ha entydige pass/fail-kriterier som verifiserer at hele kjeden (verktøy -> agent -> svar) fungerer feilfritt.

---

## 3. Detaljert Spesifikasjon

### 3.1 Domeneglossar og Låst Terminologi (fra CONTEXT.md)

Enhver agent, systemprompt og formidlingstekst SKAL bruke de autoritative begrepene og eksplisitt unngå de forbudte synonymene:

| Autorativt Begrep | Definisjon / Betydning | Forbudte Synonymer (AVOID) |
|---|---|---|
| **Kunstmuseum** | Uavhengig, ikke-kommersiell institusjon i samfunnets tjeneste som samler, bevarer, forsker på, formidler og stiller ut kunst. | Galleri, kunsthall, utstillingslokale |
| **Samling** | Samlet bestand av kunstverk og dokumentasjon museet eier og forvalter på vegne av allmennheten. | Beholdning, varelager, inventar |
| **Verk** | Individuelt kunstverk i samlingen eller innlånt, med unikt accession-/inventarnummer. | Vare, objekt, artefakt |
| **Samlingsdatabase** | Det strukturerte registeret over museets verk med metadata om kunstner, datering, teknikk, sal, tilstand. | Filarkiv, varelager, database (for generisk) |
| **Utstilling** | Kuratert, tidsavgrenset eller fast visning organisert rundt en tematisk/historisk idé. | Showcase, messe, event |
| **Kuratere** | Faglig utvelgelse, kontekstualisering og romlig/narrativ sammensetning av verk. | Redigere, publisere, sette sammen |
| **Formidling** | Pedagogisk og opplevelsesmessig tilrettelegging (omvisninger, tekster, digitale guider). | Markedsføring, reklame, PR, kundeservice |
| **Veggtekst** | Kortfattet, kuratert formidlingstekst montert ved verket (50–90 ord) for blikkfang og kontekst. | Skilt, etikett, plakat, produktbeskrivelse |
| **Museumsvert** | Førstelinjens publikumsdialog, besvarer praktiske og faglige spørsmål. | Supportagent, helpdesk-medarbeider, billettselger |
| **Proveniens** | Dokumentert eierhistorikk, opprinnelse og overdragelser fra skapelse til nåværende samling. | Transaksjonshistorikk, opprinnelseslogg |

---

### 3.2 Spesifikasjon av de 5 Samlingsverktøyene (MCP Collection Tools)

Verktøyene eksponeres via en standard MCP-server (stdio/JSON-RPC). Alle parametere skal typesjekkes og valideres.

#### Verktøy 1: `search_collection` (Samlingssøk)
- **Hensikt:** Søke etter verk i samlingen basert på fleksible kriterier.
- **Input Parametere:**
  - `query` *(valgfri, string)*: Fritekstsøk i tittel, beskrivelse, temaer eller kunstnernavn.
  - `artist` *(valgfri, string)*: Filtrer på kunstnerens navn (f.eks. «Kittelsen», «Edvard Munch»). Delvis match / case-insensitive.
  - `title` *(valgfri, string)*: Filtrer på verktittel (f.eks. «Skrik», «Nøkken»).
  - `technique` *(valgfri, string)*: Filtrer på teknikk (f.eks. «Olje på lerret», «Pastell»).
  - `theme` *(valgfri, string)*: Filtrer på tematisk tagg (f.eks. «mytologi», «stemning», «realisme»).
  - `room_id` *(valgfri, string)*: Filtrer på sal-ID (f.eks. «SAL-D», «SAL-A»).
  - `limit` *(valgfri, integer, default: 10)*: Maksimalt antall resultater (min: 1, maks: 50).
- **Output Schema (JSON Array):**
  ```json
  [
    {
      "id": "AURA-2026-001",
      "tittel": "Nøkken",
      "kunstner": "Theodor Kittelsen",
      "aar": 1904,
      "teknikk": "Pastell og blyant på papir",
      "dimensjoner": "43 x 67 cm",
      "sal_id": "SAL-A",
      "sal_navn": "Sal A (Mytologi og natur)",
      "status": "utstilt",
      "tema": ["mytologi", "folketro", "natur", "stemningskunst"]
    }
  ]
  ```
- **Valideringsregler:**
  - `limit` må være et positivt heltall (1–50).
  - Sanitiser input mot parameteriserte spørringer (ingen strengsammenkobling i SQL).
- **Feilhåndtering:**
  - Dersom ingen verk matcher kriteriene, returneres en tom liste `[]` med status OK (ikke krasj eller unntak).
  - Dersom databasen er utilgjengelig, returneres feilmelding med feilkode `DATABASE_UNAVAILABLE`.

#### Verktøy 2: `get_artwork_details` (Verksdetaljer)
- **Hensikt:** Hente komplette og autoritative metadata for ett enkelt verk, inkludert kuratert veggtekst og proveniens.
- **Input Parametere:**
  - `artwork_id` *(påkrevd, string)*: Unik inventar-ID (format: `AURA-YYYY-NNN`, f.eks. `AURA-2026-009`).
- **Output Schema (JSON Object):**
  ```json
  {
    "id": "AURA-2026-009",
    "tittel": "Skrik",
    "kunstner": "Edvard Munch",
    "kunstner_levetid": "1863–1944",
    "kunstner_nasjonalitet": "Norsk",
    "aar": 1893,
    "teknikk": "Tempera og oljekritt på papp",
    "dimensjoner": "91 x 73.5 cm",
    "sal_id": "SAL-D",
    "sal_navn": "Sal D (Eksistens og modernisme)",
    "etasje": 2,
    "status": "utstilt",
    "tilstand": "utmerket",
    "beskrivelse": "En skikkelse som holder seg for ørene på en bro under en blodrød himmel...",
    "tema": ["angst", "eksistens", "ekspresjonisme", "modernitet"],
    "veggtekst": "Edvard Munch (1863–1944), Norsk.\nSkrik, 1893. Tempera og oljekritt på papp, 91 x 73.5 cm. AURA-2026-009.\n\nEn fortvilet skikkelse holder hendene mot hodet i en åpen munn av angst under en brennende oransjerød kveldshimmel over Oslofjorden.\n\nMunchs mest berømte verk regnes som selve ur-ikonet for det moderne menneskets eksistensielle uro. Bildet formidler ikke bare en ytre scene, men et indre skrik som runger gjennom hele naturen.",
    "veggtekst_ordantall": 72,
    "proveniens": "Kunstneren → Olaf Schou 1893 → Nasjonalgalleriet 1910 → Aura Kunstmuseum (deponert)"
  }
  ```
- **Valideringsregler:**
  - `artwork_id` må være utfylt og følge gyldig ID-format.
- **Feilhåndtering:**
  - Hvis `artwork_id` ikke finnes i databasen: returner et strukturert feilobjekt: `{"error": "Verk ikke funnet", "artwork_id": "...", "code": "NOT_FOUND"}`.

#### Verktøy 3: `get_room_artworks` (Salsoversikt)
- **Hensikt:** Liste alle verk som stilles ut i en gitt sal, ordnet etter rekkefølge eller plassering.
- **Input Parametere:**
  - `room_id` *(påkrevd, string)*: Salens identifikator (f.eks. `SAL-A`, `SAL-B`, `SAL-C`, `SAL-D`, `SAL-E`, `SAL-F`, `MAG-1`). Skal også akseptere case-insensitive varianter som «Sal D» eller «sal-d».
- **Output Schema (JSON Array):**
  ```json
  [
    {
      "id": "AURA-2026-009",
      "rekkefoelge": 1,
      "tittel": "Skrik",
      "kunstner": "Edvard Munch",
      "aar": 1893,
      "teknikk": "Tempera og oljekritt på papp",
      "status": "utstilt",
      "vegg_plassering": "Hovedvegg nord"
    }
  ]
  ```
- **Valideringsregler:**
  - Filtrerer kun på verk med `status = 'utstilt'` for publikumssaler.
- **Feilhåndtering:**
  - Dersom salen eksisterer, men ikke har utstilte verk: returner tom liste `[]`.
  - Dersom `room_id` er ukjent: returner `{"error": "Ukjent sal-ID", "valid_rooms": ["SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E", "SAL-F"]}`.

#### Verktøy 4: `search_events` (Arrangementssøk)
- **Hensikt:** Finne kommende omvisninger, foredrag, verksteder og arrangementer.
- **Input Parametere:**
  - `event_type` *(valgfri, string)*: Filtrer etter type hendelse (f.eks. «omvisning», «verksted», «foredrag», «utstillingsaapning»).
  - `date_from` *(valgfri, string, ISO format YYYY-MM-DD)*: Fra og med dato. Standard: dagens dato (`date('now')`).
  - `date_to` *(valgfri, string, ISO format YYYY-MM-DD)*: Til og med dato.
  - `limit` *(valgfri, integer, default: 5)*: Maksimalt antall hendelser.
- **Output Schema (JSON Array):**
  ```json
  [
    {
      "id": "HEND-2026-001",
      "tittel": "Munch og modernismen: Guidet omvisning",
      "type": "omvisning",
      "dato": "2026-09-19",
      "klokkeslett_start": "12:00",
      "klokkeslett_slutt": "13:00",
      "sal_id": "SAL-D",
      "sal_navn": "Sal D (Eksistens og modernisme)",
      "pris_voksen": 150,
      "pris_barn": 0,
      "kapasitet": 25,
      "beskrivelse": "Dypdykk i Edvard Munchs mest sentrale verk i Sal D med museets kurator.",
      "status": "bekreftet"
    }
  ]
  ```
- **Valideringsregler:**
  - Avlyste hendelser (`status = 'avlyst'`) skal ekskluderes fra standard respons.
  - Datostrenger må typesjekkes mot gyldig format.
- **Feilhåndtering:**
  - Hvis ingen hendelser oppfyller kravene: returner tom liste `[]`.
  - Ved feilformattert dato: returner valideringsfeil `{"error": "Ugyldig datoformat. Bruk YYYY-MM-DD."}`.

#### Verktøy 5: `search_faq` (FAQ-oppslag)
- **Hensikt:** Finne autoritative svar på publikums praktiske spørsmål om billetter, åpningstider, adkomst, garderobe, tilgjengelighet og kafé.
- **Input Parametere:**
  - `query` *(påkrevd, string)*: Søkeord fra den besøkendes spørsmål (f.eks. «åpningstider», «pris», «billett», «student», «rullestol», «kafé»).
  - `category` *(valgfri, string)*: Filtrer på kategori (f.eks. «billetter», «tider», «fasiliteter»).
- **Output Schema (JSON Array):**
  ```json
  [
    {
      "id": "FAQ-001",
      "spoersmaal": "Hva er museets åpningstider?",
      "svar": "Aura Kunstmuseum er åpent tirsdag til søndag fra kl. 10:00 til 17:00. Torsdager er det kveldsåpent til kl. 20:00. Mandager holder vi stengt for konservering og monteringsarbeid.",
      "kategori": "tider"
    }
  ]
  ```
- **Valideringsregler:**
  - `query` kan ikke være tom eller bestå kun av blanktegn.
  - Søket skal utføres fleksibelt (substreng / LIKE / fulltekst).
- **Feilhåndtering:**
  - Dersom ingen oppslag matcher: returner tom liste `[]`.

---

### 3.3 Sikkerhetskrav og Tilgangsmatrise (Tool Access & Least Privilege)

I henhold til `context/operations/tool_access.md` og `context/core/approval_boundaries.md` gjelder følgende tillatelser:

| Agent / Rolle | Tillatte MCP-verktøy | Tillatte Handlinger | Forbudte Handlinger |
|---|---|---|---|
| **Museumsvert** | `sqlite_read_public`, `faq_search` (`search_collection`, `get_artwork_details`, `get_room_artworks`, `search_events`, `search_faq`) | Lese utstilte verk, salplassering, arrangementskalender, besvare FAQ | **Forbudt:** Skrive til samlingsdatabasen, endre billettpriser, endre bookingregler, opprette/endre verksdata |
| **Samlingsforvalter** | `sqlite_read`, `sqlite_write`, `filesystem_local` | Søke, opprette og oppdatere verksdata og plassering (med logg) | Offentlig ekstern publisering uten godkjenning; slette verk (deaccessioning krever styrevedtak) |
| **Kurator** | `sqlite_read`, `web_search` (kunstfag), `file_write` | Søke i samling, hente kunstkilder, skrive utstillingsplaner | Endre fysisk plassering uten loggføring hos samlingsforvalter |
| **Formidler** | `sqlite_read`, `file_read`, `file_write` | Lese verksfakta, skrive veggtekster, audiomanus, pedagogiske opplegg | Dikte opp biografiske data eller årstall; endre samlingsdatabasen |
| **Museumsdirektør** | `plane_*`, `calendar_*`, `db_read` | Lese status, opprette/tildele oppgaver, koordinere, godkjenne interne utkast | Direkte sletting av verksdata; eksterne publiseringer uten eiers forhåndsgodkjenning |
| **Driftsansvarlig** | `calendar_*`, `ticket_read`, `plane_*`, `sqlite_read`, `sqlite_write` (kun hendelser/drift) | Oppdatere kalender, justere kapasitet, logge driftsoppgaver | Endre billettpriser, inngå leieavtaler, slette historiske logger |

#### Sikkerhetsregler for Plugins og Åpne Promptflater:
1. **Museumsvert er STRICT READ-ONLY:** Museumsvert-agenten skal aldri ha tilgang til `write_query`, `INSERT`, `UPDATE`, `DELETE`, `DROP` eller `ALTER`.
2. **Ingen Rå SQL fra Åpne Flater:** Offentlige henvendelser og museumsvert-prompter må KUN benytte forhåndsdefinerte, parameteriserte funksjonskall. Fri SQL fra LLM eller bruker mot databasen er strengt forbudt.
3. **Godkjenningsgrenser (3 Nivåer):**
   - *Nivå 1 (Full agentautonomi):* Søke og lese i samlingsdatabase, analysere metadata, generere utkast.
   - *Nivå 2 (Faglig godkjenning):* Innlemme utkast i fellesarkiv, endre metadata/tilstandsrapporter, godkjenne utstillingsliste.
   - *Nivå 3 (Menneskelig eiergodkjenning påkrevd):* Ekstern publisering, eksterne henvendelser (e-post), endre billettpriser, inngå avtaler, slette historiske data/verk.
4. **Personvern:** Ingen reelle personopplysninger tillates i syntetiske treningsdata.

---

### 3.4 Museumsvertens Adferdsregler og Promptkonstruksjon (prompts/museumsvert.md)

1. **Rolle og Væremåte:**
   - Museumsverten er museets imøtekommende vertskap som står i resepsjonen og vandrer i salene.
   - Er en entusiastisk formidler med god oversikt, **ikke en akademisk kunsthistoriker**.
   - Varm, tålmodig og uformell («som en hyggelig vertskap i sitt eget hjem»).
   - Entusiastisk uten å mase; gir god informasjon og lar den besøkende velge selv.
2. **Språk- og stilkrav:**
   - Unngå «artspeak» og akademisk jargong (forbudt: formuleringer som «interrogere subjektsposisjon», «romlig negasjon», «diskurs»).
   - Kort og presist for praktiske spørsmål (åpningstider, fasiliteter, billettpriser).
   - Varmere, mer fortellende og visuelt engasjerende for kunstspørsmål.
   - Bruk gjerne imperativ i veibeskrivelser («Gå opp trappen og ta til venstre — du kan ikke gå feil»).
3. **Streng Anti-Hallusinasjon:**
   - Aldri finne på åpningstider, priser, plassering eller kunstnerfakta. Alt SKAL hentes fra databasen via verktøy.
   - Aldri gi datering, teknikk eller biografiske data som ikke finnes i databasen.
   - Dersom en opplysning mangler i databasen, skal agenten ærlig si: «Det vet jeg dessverre ikke sikkert, men formidleren vår har skrevet en flott tekst om det som du finner ved verket.» eller «Denne opplysningen er ikke registrert i samlingsdatabasen.»
   - Være helt ærlig dersom et verk er i magasin, til konservering eller om et arrangement er utsolgt.
4. **Promptkonstruksjon og Trinnvis Responsprosess:**
   - **Trinn 1 — Mental kategorisering:** Identifiser om henvendelsen er Praktisk, Samling, Utstilling, Hendelse eller Anbefaling.
   - **Trinn 2 — Verktøyoppslag:** Kall relevant parameterisert verktøy (`search_collection`, `get_artwork_details`, `get_room_artworks`, `search_events`, `search_faq`).
   - **Trinn 3 — 4-delt Svarstruktur:**
     1. *Direkte svar:* Faktaopplysning direkte basert på databasetreffet.
     2. *Kort formidlingsdetalj:* Én engasjerende setning som beriker opplevelsen (visuell observasjon, blikkfang).
     3. *Praktisk retning:* Konkret salhenvisning, etasje, veibeskrivelse.
     4. *Tilleggsforslag:* Ett tilstøtende verk i samme sal eller et kommende arrangement.

---

### 3.5 Kvalitetsregler for Veggtekster, Priser og Anbefalinger

1. **Veggtekster (Wall Texts) — Fra `quality_rules.md` & `formidler.md`:**
   - **Lengde:** Strengt 50 til 90 ord (aldri over 120 ord, eksklusive overskriftslinjene).
   - **Struktur:**
     * *Linje 1 (Metadata):* `[Kunstnernavn] ([fødselsår]–[dødsår]), [nasjonalitet].`
     * *Linje 2 (Verksdata):* `_[Tittel]_, [år]. [Teknikk], [dimensjoner]. [Unikt inventarnummer, f.eks. AURA-2026-001].`
     * *Avsnitt 1 (Visuell inngang):* Hva betrakteren ser foran seg akkurat nå (1–2 setninger, blikkfang).
     * *Avsnitt 2 (Kontekst & betydning):* Hvorfor verket er vesentlig, historisk betydning (2–3 setninger).
   - **Språk:** Klart, tilgjengelig, aktive verb («Krohg viser...», «Munch maler...»). Aldri passive fyllfraser som «dette verket er interessant fordi».
2. **Priser (Prices) — Fra `approval_boundaries.md`, `tool_access.md`, `publikum_faq`:**
   - Alle priser skal hentes direkte fra `publikum_faq` eller `hendelser`.
   - Priser oppgis i norske kroner (NOK / kr).
   - Agenten har aldri lov til å endre priser, gi rabatter eller love refusjoner (Nivå 3 krever menneskelig eiergodkjenning).
3. **Anbefalinger (Recommendations) — Fra `museumsvert.md` & `quality_rules.md`:**
   - Anbefalinger må tilpasses gjestens tilgjengelige tid (f.eks. «30 minutter», «1 time») og interesser.
   - **Kun utstilte verk:** En anbefaling må ALDRI foreslå et verk som befinner seg i magasin (`status: magasin`), under konservering (`status: konservering`) eller utlånt (`status: utlaant`).
   - For «30 minutter»: Foreslå 2–3 utvalgte mesterverk (f.eks. *Skrik* i Sal D og *Vinternatt i Rondane* i Sal A) med logisk rekkefølge og salplassering.

---

### 3.6 E2E Testingskriterier (Minst 8 Scenarier, >= 2 per kategori)

| # | Kategori | Scenario & Brukerprompt | Forventet Verktøykall | Pass-kriterier (Må oppfylles) | Fail-kriterier (Underkjenning) |
|---|----------|------------------------|----------------------|-------------------------------|--------------------------------|
| **1** | `samling` | «Har dere noen verker av Theodor Kittelsen, og hvor henger de?» | `search_collection(artist="Theodor Kittelsen")` | Returnerer minst 2 verk (*Nøkken* AURA-2026-001 og *Soria Moria slott* AURA-2026-002). Agenten oppgir Sal A, nevner tittel, årstall og gir en varm formidlingsdetalj. | Færre enn 2 verk; feil sal; dikter opp verker; hallusinerer årstall; tomt svar. |
| **2** | `samling` | «Hvor finner jeg Skrik, og hva forestiller bildet?» | `search_collection(title="Skrik")` eller `get_artwork_details(artwork_id="AURA-2026-009")` | Identifiserer Edvard Munch (1893), plassert i **Sal D** (Eksistens og modernisme, 2. etasje). Beskriver angstmotivet/himmelen og gir salanvisning. | Henviser til feil sal (ikke Sal D); påstår verket er i magasin; mangler tittel/kunstner. |
| **3** | `samling` | «Kan jeg få se detaljer og proveniens for Vinternatt i Rondane?» | `get_artwork_details(artwork_id="AURA-2026-007")` | Returnerer Harald Sohlberg (1914), olje på lerret, 160 x 180 cm, Sal A, samt fullstendig provenienskjede (opprinnelse → eier → Aura Kunstmuseum). | Krasjer på ID-oppslag; mangler proveniens eller veggtekst; feil format. |
| **4** | `utstilling` | «Hvilke verker kan jeg se i Sal D?» | `get_room_artworks(room_id="SAL-D")` | Returnerer minst 3 utstilte verk i Sal D med titler, kunstner og teknikk (inkl. Edvard Munchs verker). | Færre enn 3 verk i Sal D; returnerer verk fra andre saler; viser verk som har status 'magasin'. |
| **5** | `utstilling` | «Hvilke faste og midlertidige utstillinger vises på museet nå?» | `search_collection` / utstillingsoppslag | Presenterer aktuelle utstillinger (f.eks. samlingsutstillingene fordelt på salene A–D) med overordnet tema. | Viser fiktive utstillinger som ikke eksisterer i databasen; tomt svar. |
| **6** | `hendelse` | «Når arrangeres det neste guidet omvisning?» | `search_events(event_type="omvisning")` | Returnerer kommende omvisning med dato (>= dagens dato), klokkeslett, sal, pris og kort beskrivelse. Utelukker avlyste arrangementer. | Returnerer passert arrangement; returnerer avlyst hendelse; hallusinerer tid/sted. |
| **7** | `hendelse` | «Har dere noen aktiviteter eller verksteder for barn?» | `search_events(event_type="verksted")` | Identifiserer planlagt barneverksted / familieaktivitet med tidspunkt, sal og billettpris for barn/voksne. | Finner på uoffisielle barneaktiviteter; oppgir feil pris eller dato som ikke finnes. |
| **8** | `praktisk` | «Hva er museets åpningstider i dag og i helgen?» | `search_faq(query="åpningstider")` | Returnerer konkrete klokkeslett fra FAQ (f.eks. tirsdag–søndag kl. 10–17, torsdager til 20, stengt mandager). | Mangler klokkeslett; gjetter eller oppgir ukorrekte åpningstider; tomt svar. |
| **9** | `praktisk` | «Hva koster det å komme inn for en voksen og en student?» | `search_faq(query="pris")` | Returnerer faktiske priser fra `publikum_faq` i NOK spesifisert per kategori (voksen, student/honnør, barn). | Mangler priser; endrer priser; oppgir feil beløp eller feil valuta. |
| **10** | `praktisk` | «Hva anbefaler du hvis jeg bare har 30 minutter til rådighet?» | `search_collection` / `get_room_artworks` | Anbefaler et personlig utvalg av 2–3 utstilte nøkkelverk (f.eks. Munch i Sal D og Sohlberg/Kittelsen i Sal A) med logisk vandringsrute og formidlingsglimt. | Anbefaler > 4 verk; foreslår verk som ligger i magasin; mangler salhenvisning. |

---

## 4. Features Discovered Table

| # | Kategori | Funksjon (Feature) | Beskrivelse | Inputs | Outputs | Feilhåndtering / Error Behavior | Discovered Via |
|---|----------|--------------------|-------------|--------|---------|--------------------------------|----------------|
| 1 | Samlingsverktøy | `search_collection` | Parameterisert søk i samlingsdatabase etter verk på tittel, kunstner, teknikk, tema og sal. | `query?: str`, `artist?: str`, `title?: str`, `technique?: str`, `theme?: str`, `room_id?: str`, `limit?: int` | JSON Array med verkskort (`id`, `tittel`, `kunstner`, `aar`, `teknikk`, `sal_id`, `status`, `tema`) | Returnerer tom liste `[]` ved ingen treff; parameterisert SQL hindrer injeksjon. | `workflows.md:54`, `brief.md:9`, `ORIGINAL_REQUEST.md:31` |
| 2 | Samlingsverktøy | `get_artwork_details` | Henter fullstendige metadata, inkludert godkjent veggtekst og provenienshistorikk for ett verk. | `artwork_id: str` (format: `AURA-YYYY-NNN`) | JSON Objekt med alle verksdata, dimensjoner, tilstand, veggtekst, ordantall og proveniens. | Returnerer strukturert feilobjekt `{"error": "Verk ikke funnet", "code": "NOT_FOUND"}` ved ukjent ID. | `brief.md:10`, `ORIGINAL_REQUEST.md:32`, `quality_rules.md:21` |
| 3 | Samlingsverktøy | `get_room_artworks` | Henter liste over alle verk som for tiden stilles ut i en gitt sal, ordnet etter rekkefølge/plassering. | `room_id: str` (f.eks. `SAL-A` til `SAL-F`, `MAG-1`) | JSON Array over utstilte verk med rekkefølge, tittel, kunstner, år og veggplassering. | Returnerer tom liste `[]` hvis salen er tom; returnerer liste over gyldige saler hvis `room_id` er ukjent. | `brief.md:11`, `ORIGINAL_REQUEST.md:33`, `prompts/museumsvert.md:52` |
| 4 | Arrangementsverktøy | `search_events` | Henter kommende arrangementer (omvisninger, verksteder, foredrag) filtrert på type og tidsrom. | `event_type?: str`, `date_from?: str`, `date_to?: str`, `limit?: int` | JSON Array med hendelser (`id`, `tittel`, `type`, `dato`, `klokkeslett`, `sal`, `pris`, `kapasitet`). | Returnerer tom liste `[]` ved ingen treff; validerer ISO-dato; ekskluderer avlyste (`status != 'avlyst'`). | `ORIGINAL_REQUEST.md:34`, `prompts/museumsvert.md:57`, `driftsansvarlig.md:19` |
| 5 | FAQ-verktøy | `search_faq` | Søker etter autoritative svar på praktiske spørsmål om åpningstider, priser, fasiliteter og adkomst. | `query: str`, `category?: str` | JSON Array med FAQ-poster (`id`, `spoersmaal`, `svar`, `kategori`). | Returnerer tom liste `[]` ved ingen treff; avviser tomme søkestrenger med valideringsfeil. | `ORIGINAL_REQUEST.md:35`, `prompts/museumsvert.md:62`, `tool_access.md:11` |
| 6 | Sikkerhet & Rettighet | Skrivebeskyttelse for Museumsvert | Museumsvert-agenten tildeles utelukkende lesetilgang (`sqlite_read_public`, `faq_search`). | N/A (RBAC / konfigurasjon) | Avviser skrivekall (`sqlite_write`, `write_query`, `UPDATE`, `INSERT`). | Kaster tilgangsnektet-unntak (`PermissionDeniedError`) ved forsøk på skriving. | `tool_access.md:11`, `prompts/museumsvert.md:18`, `approval_boundaries.md:21` |
| 7 | Sikkerhet & Rettighet | Parameterisert SQL-barriere | Forbud mot fri/rå SQL fra åpne agentflater; kun faste, typesikre parametere tillates. | Parameteriserte funksjonskall | Validerte SQL-spørringer med bundne variable | Forespørsler med rå SQL avvises umiddelbart før databasetilgang. | `tool_access.md:16` |
| 8 | Styring & Beslutning | Tredelt Godkjenningsmatrise | Håndhever autonomigrenser: Nivå 1 (Full agentautonomi), Nivå 2 (Faglig leder), Nivå 3 (Menneskelig eier). | Forespurt handling og rolle | Godkjent / Eskalert til leder / Eskalert til eier | Blokkerer utførelse av handlinger som mangler påkrevd godkjenningsnivå. | `approval_boundaries.md:1-24`, `owner_intent.md:10` |
| 9 | Samlingsforvaltning | Accessioning & ID-validering | Tildeling av unikt inventarnummer `AURA-YYYY-NNN` og validering av 9 obligatoriske felt. | `id`, `tittel`, `kunstner_id`, `aar`, `teknikk`, `dimensjoner`, `sal_id`, `status`, `tilstand` | Registrert verkskort i database med revisjonslogg | Avviser registrering dersom noen obligatoriske felt mangler; feilmelding spesifiserer mangel. | `samlingsforvalter.md:23-46`, `quality_rules.md:21` |
| 10 | Samlingsforvaltning | Tilstands- og Plasseringsstyring | Håndhever de 5 gyldige tilstandsverdiene og kontrollerer flytting mellom sal og magasin. | `tilstand: enum`, `sal_id: str` | Oppdatert lokasjon og tilstand med versjonsdato | Fritekst i tilstandsfeltet avvises; ukjent sal-ID avvises. | `samlingsforvalter.md:37,53` |
| 11 | Kuratering | Kuratorpakke for Utstillinger | Utvikling av utstillingskonsept med tittel, undertittel, 100–150 ord konsept og rangert verksliste. | Utstillingstittel, konsept, verkutvalg | Strukturert Markdown-utstillingsplan med romfordeling | Blokkerer sletting eller fysisk flytting uten samlingsforvalter; kildekreves for påstander. | `kurator.md:23-46`, `workflows.md:28` |
| 12 | Formidling | Standard Veggtekstgenerator | Produserer kuratert veggtekst etter 4-delt mal på nøyaktig 50–90 ord (maks 120 ord). | `artwork_id: str`, verksmetadata | Formatert tekst (metadata, visuell inngang, kontekst/betydning) | Tekster under 50 ord eller over 90 ord avvises i automatisk kvalitetskontroll. | `quality_rules.md:4-10`, `formidler.md:22-41` |
| 13 | Formidling | Audioguide-manus | Generering av fortellende manus for lydguide på 60–90 sekunder (130–180 ord). | `artwork_id: str`, målgruppe | Strukturert audiomanus med sanselige observasjoner og pauser | Tekster utenfor 130–180 ord flagges for revisjon. | `quality_rules.md:12-15`, `formidler.md:42-57` |
| 14 | Formidling | Barne- og familieformidling | Genererer oppdagelsesspørsmål og sanselig «oppdrag» for barn (4–12 år). | `artwork_id: str`, aldersgruppe | Formatert oppdrag (🔍 Oppdrag, 💬 Tenk på) | Tekster med tørre årstallrekker eller akademisk fagspråk underkjennes. | `quality_rules.md:16-19`, `formidler.md:58-68` |
| 15 | Driftsansvar | Arrangementsvalidering | Sjekkliste før arrangement bekreftes: kollisjonssjekk på sal, kapasitetsgrense, tildelt ansvarlig. | Hendelsesdata, sal, tidspunkt | Status settes til `bekreftet` | Kollisjon i sal eller manglende kapasitet gir feilmelding og hindrer bekreftelse. | `driftsansvarlig.md:23-32` |
| 16 | Publikumsdialog | Museumsvert 4-delt Svarstruktur | Syntetisering av svar: 1. Direkte fakta, 2. Opplevelsesdetalj, 3. Veibeskrivelse, 4. Tilleggsforslag. | Spørsmål fra besøkende + databasetreff | Varm, engasjerende og presis tekstrespons | Manglende databasefakta erstattes med ærlig avkreftelse («Det vet jeg dessverre ikke sikkert...»). | `prompts/museumsvert.md:66-73` |

---

## 5. Edge Cases Table

| # | Funksjon / Område | Inndata (Input / Scenario) | Observert / Spesifisert Adferd | Regel / Kildehenvisning |
|---|---|---|---|---|
| 1 | `get_artwork_details` | Spørsmål om verk med ukjent ID (f.eks. `AURA-2026-999`). | Returnerer eksplisitt feilobjekt `{"error": "Verk ikke funnet", "code": "NOT_FOUND"}`; agenten svarer at verket ikke finnes i samlingen. | `quality_rules.md:21`, `samlingsforvalter.md:72` |
| 2 | `get_room_artworks` | Forespørsel om sal med blandet status (f.eks. noen verk utstilt, noen i magasin). | Filtrerer strengt på `status = 'utstilt'`. Verk med status `magasin` eller `konservering` ekskluderes fra publikumsoversikten. | `prompts/museumsvert.md:45,55`, `data/samling.json:140` |
| 3 | `search_collection` | Søk etter kunstner med skrivefeil eller delvis navn (f.eks. «kittelsen», «Munch», «Harriet»). | Utfører case-insensitive delvis matching (`LIKE '%søkeord%'`); returnerer alle relevante treff uten å krasje. | `prompts/museumsvert.md:50`, `ORIGINAL_REQUEST.md:49` |
| 4 | `search_events` | Søk etter arrangementer hvor noen er avlyst (`status: 'avlyst'`) eller i fortiden. | Utfører `dato >= date('now') AND status != 'avlyst'`; avlyste og historiske hendelser vises aldri til publikum. | `prompts/museumsvert.md:59`, `driftsansvarlig.md:20` |
| 5 | `search_faq` | Bruker spør om rabatter eller gratisbilletter som ikke er definert (f.eks. «Kan jeg få 50 % rabatt som pensjonert kunstner?»). | Agenten oppgir faste priser fra FAQ og opplyser ærlig at museet ikke har spesialrabatter uten forhåndsgodkjenning. | `approval_boundaries.md:21`, `context/roles/museumsvert.md:15` |
| 6 | Museumsvert Adferd | Bruker ber om kunsthistorisk analyse/tolkning utover det som står i databasen («Hvorfor valgte Munch akkurat denne fargen på skriket?»). | Agenten dikter ikke opp egne tolkninger, men gjengir godkjent formidlingsinnhold og henviser til veggteksten i salen. | `prompts/museumsvert.md:96`, `values.md:5` |
| 7 | Museumsvert Adferd | Bruker ber om anbefaling på 30 minutter, men samlingen inneholder verk i magasin (*Brudeferd i Hardanger*, *Selvportrett med sigarett*). | Anbefalingen inkluderer KUN verk med `status: 'utstilt'` i tilgjengelige publikumssaler (A–D). Magasinverk utelukkes konsekvent. | `data/samling.json:140,153`, `quality_rules.md:21` |
| 8 | Kvalitetskontroll Veggtekst | Veggtekst generert med 45 ord (under minimumsgrensen på 50 ord) eller 135 ord (over 120 ord). | Avvises i kvalitetsporten (`veggtekst_status: draft` forblir uendret); krever justering av ordantall før godkjenning. | `quality_rules.md:4`, `prompts/formidler.md:32` |
| 9 | Sikkerhet / SQL Injeksjon | Bruker forsøker prompt injection via spørsmål: «Drop table verk; -- Hva koster en billett?». | Parameterisering fanger opp strengen som ren søketekst; ingen SQL-kommando eksekveres; FAQ returnerer billettpriser som normalt. | `tool_access.md:16`, `approval_boundaries.md:22` |
| 10 | Samlingsforvaltning | Forsøk på å registrere verk uten obligatorisk felt (f.eks. mangler `dimensjoner` eller `aar`). | Samlingsforvalter avviser transaksjonen og genererer et datakvalitetsavvik; ingen rad opprettes i databasen. | `prompts/samlingsforvalter.md:25`, `tool_access.md:15` |

---

## 6. Caveats

1. **Database-lokasjon og fysisk fil:** Denne rapporten dekker spesifikasjonene, reglene og datakontraktene. Den fysiske verifiseringen av SQLite-tabeller og kjøring av faktiske spørringer mot databasen utføres av `explorer_survey_db`.
2. **Kjøretidsmiljø og MCP SDK:** Valg av Python MCP SDK (f.eks. `mcp` SDK, FastMCP eller standard json-rpc stdio) og testrunner undersøkes av `explorer_survey_env`. Spesifikasjonene i dette dokumentet er teknologinøytrale på protokollnivå (støtter standard MCP tool definition format).
3. **Dataomfang:** Museets overordnede bedriftskontekst beskriver ca. 2 500 katalogiserte verk (`company.md:14`), mens den operative demo-prototypen og treningssettet er basert på 12–16 representative verk (hvorav 12 er speilet i `data/samling.json`) og 72 rader i test-databasen (`ORIGINAL_REQUEST.md:5`).

---

## 7. Conclusion

Spesifikasjonen for Aura Kunstmuseum er entydig, helhetlig og konsistent på tvers av alle kildedokumenter:
- De 5 samlingsverktøyene (`search_collection`, `get_artwork_details`, `get_room_artworks`, `search_events`, `search_faq`) danner et komplett, funksjonelt grensesnitt som tilfredsstiller både kjernearbeidsflytene (WF1, WF2, WF3) og samtlige akseptansekriterier i `ORIGINAL_REQUEST.md`.
- Sikkerhetsarkitekturen er kompromissløs: Museumsverten har strikt read-only tilgang uten mulighet for skriving til databasen eller kjøring av fri SQL.
- Formidlingskvaliteten er strengt regulert av målbare regler: veggtekster skal ha 50–90 ord, priser skal være faktiske, og anbefalinger skal kun basere seg på reelt utstilte verk.
- Testkriteriene er formalisert i 10 detaljerte scenarier (minst 2 per kategori) med klare pass/fail-betingelser som gjør det rett frem å bygge en automatisert testsuite.

---

## 8. Verification Method

For å etterprøve og verifisere denne rapporten uavhengig:
1. **Inspeksjon av låst terminologi:** Sjekk `CONTEXT.md` og bekreft at ingen forbudte ord («galleri», «varelager», «helpdesk») forekommer i genererte prompter eller verktøybeskrivelser.
2. **Inspeksjon av sikkerhetsmatrise:** Åpne `context/operations/tool_access.md` linje 5–18 og bekreft at museumsvert kun er tildelt `sqlite_read_public` og `faq_search`, samt at rå SQL er forbudt.
3. **Inspeksjon av kvalitetsregler:** Åpne `context/core/quality_rules.md` linje 3–11 og bekreft ordgrensene for veggtekst (50–90 ord).
4. **Inspeksjon av museumsvert-prompt:** Åpne `prompts/museumsvert.md` linje 16–23 og bekreft read-only klausulen og spørremalene.
5. **Kjøring av E2E-testpakke:** Når testpakken for R3 implementeres, skal den eksekvere de 10 definerte scenariene i tabell 3.6 mot MCP-serveren og validere at ingen tester feiler.
