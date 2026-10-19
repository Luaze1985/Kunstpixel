# SPEC – Kunstpixel internplattform v1 (Codex Cloud)

**Status:** Bestilling til Codex Cloud. Ingen produksjonssetting.  
**Repo:** `Luaze1985/Kunstpixel`  
**Utgangspunkt:** `feature/hr-simulator-syntetisk-innleie` / draft PR #1  
**Eiermål:** Lære å bygge og vurdere en liten virksomhets internplattform for HR, arbeidsfordeling, hendelser, godkjenninger og innleie – med kun oppdiktede personer og situasjoner.

## 0. Les dette før noe endres

Følg først `KUNNSKAPSKART.md`, `AGENTS.md`, `00_felles/FORMAAL.md` og `04_knowledge/04_domain/core/approval_boundaries.md`.

Gjennomgå eksisterende kode og innhold:
- `src/kunstpixel/hr_simulator/schema.py`
- `src/kunstpixel/hr_simulator/engine.py`
- `src/kunstpixel/hr_simulator/__main__.py`
- `05_data/hr_simulator/scenarios/HR-001.json`
- `05_data/hr_simulator/scenarios/HR-002.json`
- `05_data/hr_simulator/scenarios/HR-003.json`
- `02_deliverables/hr-simulator-demo.html`
- `tests/test_hr_simulator.py`
- eksisterende museumsvert og API under `src/kunstpixel/`

**Viktig:** Ny internplattform skal være isolert fra publikumsrettet museumsvert. Ikke endre `05_data/museum.db`, og ikke bruk den som skrivbar HR-database. Ikke introduser reelle personer eller sensitive opplysninger.

## 1. Produktmål

Bygg én fungerende lokal internplattform i nettleser der et fiktivt museum har 8–12 ansatte, flere parallelle aktiviteter og en liten vikarpool. Brukeren må kunne:

1. Velge et scenario og se ansatte, kompetanse, tilgjengelighet, aktiviteter og krav.
2. Se oppdagede bemanningskonflikter: dobbeltbooking, kompetansemangel, manglende kapasitet.
3. Se pool med interne ekstravakter og ekstern innleie, inkludert status/sperringer.
4. Se forslag med begrunnelse og forventede virkninger.
5. Godkjenne eller avslå – og få plan, konflikter og revisjonsspor oppdatert **fra samme backend-database**.
6. Se personalsaker i en særskilt HR-visning. Ingen automatiske konklusjoner om skyld.
7. Nullstille et scenario deterministisk, slik at øvelsen kan kjøres igjen.

Brukeren skal kunne lære av forskjellen mellom manuell beslutning, regelbasert forslag og eventuell fremtidig KI-anbefaling.

## 2. Arkitekturvalg (anbefalt)

**Behold dagens repo og Python/SQLite. Unngå mikroservices, ORM og tunge frontend-rammeverk.**

Første sammenhengende leveranse:
- Python 3.13 som repoet krever.
- FastAPI + Uvicorn som **separat lokal backend** under `src/kunstpixel/hr_simulator/`, eventuelt begrunnet enda lettere løsning dersom det gir reell gevinst.
- SQLite via standardbiblioteket for en *egen* lokal HR-simulator-DB (`05_data/hr_simulator/local_state.db` eller tilsvarende); denne skal være **gitignored**.
- HTML/CSS/vanilla JS fra den eksisterende demoen kan gjenbrukes, men dataene skal nå hentes fra API. Fjern kopierte scenario-datasett fra JavaScript så vi får én sannhetskilde.
- Én lokal prosess som serverer både interne API-endepunkter og skjermbildet. For demo: bind som standard til `127.0.0.1`; ingen deploy på internett.
- Ingen innlogging eller virkelig autorisasjon påstås i versjon 1. En valgboks for «Leder»/«HR» kan kun demonstrere prosessregler og skal merkes **demo, ikke tilgangskontroll**.
- Ikke koble til ekte Gmail, Google Kalender, HR-systemer, LLM-leverandører eller bemanningsregistre i denne leveransen.

**Ikke** skriv nye urelaterte systemer for CRM, regnskap, lønn, rekruttering, faktura eller publikumstjenester.

## 3. Datamodell (gjenbruk og suppler ved behov)

Eksisterende entiteter: `providers`, `persons`, `person_skills`, `availability`, `activities`, `activity_requirements`, `assignments`, `rental_requests`, `hr_cases`, `hr_case_parties`, `proposals`, `decision_log`.

Nødvendige felt og hensyn:
- Person: ID, navn (oppdiktet), rolle, type (`employee`, `internal_pool`, `agency_pool`), kontaktdata i ugyldig testformat, stillingsprosent, kompetanse, tilgjengelighet.
- Aktivitet: ID, tittel, start/slutt, prioritet, krav til antall og kompetanse, ansvarlig, oppdragsstatus.
- Tildeling: person + aktivitet + tidsrom + status; ingen overlapp uten eksplisitt konfliktsignal.
- HR-sak: egen ID, type, tilgangsklasse, påstander vs dokumenterte fakta, eierrolle, prosessstatus, relaterte personer, oppfølging. Ikke legg konkrete saksdetaljer i ordinær bemanningstabell.
- Innleie: internt/eksternt, kompetanse, tilgjengelighet, foretak, dokumentert rettslig grunnlag, kontroll av foretak, likebehandling, kostnadsestimat som **fiktivt** valgfritt felt, HR-vurdering.
- Forslag: ID, kilde (`rules` eller `llm`), strukturerte endringer, begrunnelse, sperringer, forventet effekt og status.
- Beslutning: forslag-ID, godkjent/avslått, demo-aktør, tid, begrunnelse og nytt statusbilde.
- Versjonering/optimistisk lås på scenario eller plan, slik at gamle forslag ikke kan godkjennes etter at planen endres.

Hvis endret skjema er nødvendig: lag enkel, sporbar migrering og tester; ikke rediger museumdatabasen.

## 4. Scenarioer som må fungere

### HR-001 – Travel torsdag
- 8 ansatte, skolebesøk, montering, kafé, kveldsarrangement.
- Start: én dobbeltbooking for Ola og én bemanningsmangel.
- Forslag: flytt montering fra 11–14 til 12–15.
- Etter godkjenning: dobbeltbooking løst, men arrangementets bemanningsmangel gjenstår.
- Etter avslag: planen uendret.

### HR-002 – Opplevd urettferdig arbeidsfordeling
- Fiktiv uenighet om senvakter, motstridende perspektiver og manglende turnushistorikk.
- HR kan se fiktiv saksbeskrivelse. Vanlig leder skal ikke se detaljer merket `hr_only`.
- Forslag: faktaundersøkelse, dialog med begge parter og innhenting av dokumentasjon.
- Ingen automatisk skyldfordeling, reaksjon, disiplinærtiltak eller personskår.

### HR-003 – Fravær, merarbeid og innleie
- En formidler er utilgjengelig uten opplysning om hvorfor.
- Skolebesøk mangler én kvalifisert formidler.
- Intern pool-kandidat Kari dekker kompetanse og hele tidsrommet.
- Ekstern kandidat Tove er faglig kvalifisert, men innleiegrunnlaget er ikke avklart.
- HR-sak om opplevd press for merarbeid holdes adskilt fra bemanningsproblemet.
- Godkjent intern ekstravakt fjerner kompetansemangelen; ekstern innleie forblir sperret.
- Avslag gir ingen endring. HR-undersøkelse setter kun prosessstatus, ikke konklusjon.

**Merk:** Alle scenarier må kunne lastes fra JSON via backend. Ikke vedlikehold separate sannheter i JavaScript og Python.

## 5. Forslags- og godkjenningsflyt

`Hendelse → kontrollregler → forslag → menneskelig beslutning → transaksjon → ny kontroll → logg`

Kontrollmotoren skal være deterministisk. Den skal sjekke:
- Tidsoverlapp og tilgjengelighet.
- Krav til kompetanse og bemanning per aktivitet.
- Pool-kandidatens kompetanse og vaktens tidsrom.
- Innleiesperrer og krav om dokumentert HR-vurdering.
- At godkjenningsforslaget fortsatt gjelder gjeldende versjon av planen.
- Ingen negative konflikter eller endringer som oppstår ved feilaktig gjennomføring uten rollback.

Forslag skal **aldri** direkte mutere tildelinger. Godkjenning må være en eksplisitt handling, med servervalidering og én transaksjon. Logg avslag også. Ved stale versjon eller brudd på regler returneres en forståelig feil og databasen forblir uendret.

Ikke påstå at en kandidat er «lovlig innleid» basert bare på en boolsk demo-verdi. Vis «Simulert kontrollstatus, krever virkelig vurdering».

## 6. Brukerflate

Lag mobilvennlig skjerm med tydelig norsk bokmål, sober grå/hvit/svart design, stor nok tekst og knapper. Ingen innlogging eller nettverksavhengige grafikkbiblioteker i demoen.

Visninger:
1. **Oversikt** – nøkkeltall og konflikter med prioritet.
2. **Bemanning** – aktiviteter, klokkeslett, ansatte, kompetansekrav og ledige ressurser.
3. **Pool/innleie** – intern versus ekstern, kvalifikasjoner, tilgjengelighet og juridiske sperrer.
4. **HR-saker** – begrenset demovisning av konfidensielle saker, fakta/påstander og prosessstatus.
5. **Forslag/beslutninger** – forskjell mellom regelmotor, KI og menneskelig godkjenning; beslutningslogg.

Kritisk: Etter godkjenning eller avslag skal brukerflaten hente nye data fra backend og vise oppdatert konfliktantall; ikke bare endre lokal JS-state.

Vis eksempel på begrunnelsen bak hver konflikt: «Ola er tildelt to oppgaver kl. 11–12» og «Skolebesøk mangler én person med formidlingskompetanse».

## 7. API – foreslåtte kontrakter

Konkrete endepunkter kan justeres, men de må være konsekvente og dokumenterte:

- `GET /api/hr/scenarios`
- `POST /api/hr/scenarios/{id}/reset`
- `GET /api/hr/dashboard`
- `GET /api/hr/people`
- `GET /api/hr/activities`
- `GET /api/hr/conflicts`
- `GET /api/hr/pool?activity_id=...`
- `GET /api/hr/proposals`
- `POST /api/hr/proposals/{id}/decide`
- `GET /api/hr/decisions`
- `GET /api/hr/cases` (med serverkontroll for demoens kontekst)

Foretrekk server-side sessions/scenario-ID slik at ikke alle testbrukere manipulerer samme tilstand. I MVP kan ett lokalt demonstrasjonsrom med tydelig «reset»-knapp være tilstrekkelig.

Feilformat i JSON: `code`, `message`, `details`. Valider input med Pydantic eller tilsvarende. Ingen rå SQL fra klienten.

## 8. Realisme og norske rammer

Arbeidsrettslige temaer er **manuelle kontrollpunkter**, ikke automatiske konklusjoner:
- Intern ekstravakt er ikke det samme som innleie fra bemanningsforetak.
- Innleie fra bemanningsforetak krever lovlig grunnlag, godkjent foretak og relevante vilkår om blant annet likebehandling.
- Arbeidstid, hvile, stillingsprosent, merarbeid/overtid og vern av ansatte skal vurderes.
- Uenighet eller påstand om kritikkverdige forhold krever forsvarlig saksbehandling, kontradiksjon, taushet og habilitetsvurdering.

Primærkilder:
- https://www.arbeidstilsynet.no/lonn-og-ansettelse/innleie-av-arbeidskraft/innleie-fra-bemanningsforetak/
- https://prod.arbeidstilsynet.no/godkjenninger/godkjente-bemanningsforetak/
- https://www.arbeidstilsynet.no/lonn-og-ansettelse/innleie-av-arbeidskraft/innleie-fra-bemanningsforetak/bemanningsforetakets-ansvar-og-plikter/

I simulatoren skal manglende eller uavklarte rettslige forhold **blokkere ekstern innleie**. Codex skal ikke bygge sin egen «lovlighetsdommer».

## 9. Sikkerhet, personvern, testdata

- Repoet er offentlig. **Kun syntetiske personer og situasjoner.**
- Test-eposter under `example.invalid`; telefonnummer med `000...`; aldri faktiske fødselsnumre, pasientinformasjon, fraværsårsaker, medisinske data eller ekte HR-notater.
- Lokal SQLite-state må stå i `.gitignore` og testes for utilsiktede commits.
- Demoens rolleskifte skal ikke beskrives som sikker autentisering; før reell bruk må systemet ha SSO, reell tilgangskontroll på backend, autorisasjon per sak, sikker lagring og tilgangslogger.
- Ikke aktiver ekstern nettverkspublisering; ikke bland inn museets publikumschat.
- Ingen direkte e-post, kalenderinnkallinger, kontrakter eller økonomiske handlinger.
- Ingen direkte personvurdering via LLM som ansettelse/avskjed/sanksjon.
- Unngå tilgang på sensitive case-data fra bemanningsoversikten, logger eller feilmeldinger.

## 10. Faseinndeling – viktig for Codex Cloud

### Fase A – bygg nå (ett begrenset vertical slice)

1. Inspiser repo og test baseline.
2. Gjenbruk eksisterende schema/engine og scenarioer; rett feil før UI-integrasjon.
3. Lag en liten lokal backend + tilhørende nettlesergrensesnitt.
4. Implementer kun scenario HR-003 ende-til-ende først: personoversikt → konflikt → intern pool-forslag → HR-godkjenning → oppdatert plan og logg.
5. Eksponer HR-001 og HR-002 når samme motor kan håndtere dem uten hardkodede UI-spesialregler.
6. Test på mobilbredde og desktop, dokumenter kjørekommandoer, legg ved skjermbilde hvis verktøyene tillater.
7. Lever arbeid i egen branch/PR. **Ikke merge automatisk.**

### Fase B – etter gjennomgang, ikke i første kjøring

- Bedre HR-saksflyt (fakta, partsinnsyn, vurderinger og oppfølging).
- Scenariogenerator og flere hendelser gjennom dagen.
- Enkle fiktive kostnadsestimater og historikk over tildeling av ubekvemme vakter.
- Eksporter scenario og beslutningsrapport.

### Fase C – senere og særskilt godkjenning

- Frivillig LLM-støtte med strukturert, validert forslag og menneskelig godkjenning.
- Reell innlogging/rolle- og datatilgang hvis løsning skal tas i faktisk intern bruk.
- Eventuell integrasjon mot kalender, prosjektstyring og andre interne datakilder.
- Ekstern deling/deploy først etter egen sikkerhets- og personvernvurdering.

## 11. Akseptansekriterier for fase A

- [ ] Én dokumentert kommando starter lokal backend og nettside.
- [ ] Dashboard viser HR-003 hentet fra SQLite via API, ikke hardkodede JS-data.
- [ ] HR-003 starter med nøyaktig én bemanningsmangel (formidler).
- [ ] Kari finnes i intern pool og er relevant for skolebesøket; Tove markeres som ekstern med sperre.
- [ ] Godkjenn Kari som HR → mangel forsvinner, tildeling og beslutning persisteres i simulerings-DB.
- [ ] Avslå forslag → ingen endring i planen, men avslag loggføres.
- [ ] Manglende lovlig innleiegrunnlag → Tove kan ikke tildeles.
- [ ] HR-001 gir to bemanningskonflikter før endring og én etter godkjent flytting.
- [ ] HR-002 forblir en konfidensiell sak; vanlig leder får ingen `hr_only`-detaljer fra API.
- [ ] Ingen reelle eller gyldige kontaktdata, ingen ekstern systemintegrasjon.
- [ ] Eksisterende museumsvert fungerer fortsatt; ingen endring i `museum.db`.
- [ ] Automatiske tester dekker motor, HTTP-endepunkter og feiltransaksjoner; hele pytest-pakken kjøres.
- [ ] Enkel visuell gjennomgang desktop + mobil, gjerne med Playwright hvis tilgjengelig.
- [ ] README/HOWTO angir kjøring, arkitektur, teststatus og hva som *ikke* er sikret.
- [ ] Lever PR, oppsummer endrede filer, faktisk testresultat, uløste svakheter og neste anbefalte steg.

## 12. Arbeidsregler for Codex

- Start med å lese eksisterende prosjektfiler. Ikke erstatt tidligere kodeblindly.
- Foretrekk små, avgrensede endringer fremfor total omskriving.
- Skille «faktisk implementert» fra «dokumentert intensjon».
- Bruk tester og lesbare feilmeldinger; ikke kun tillit til genererte forslag.
- Ikke endre mer enn det denne spesifikasjonen krever.
- Ikke start fase B/C på egen hånd.
- Hvis miljøet mangler Python-versjon eller avhengigheter, rapporter konkret blokkering og hvilke kommandoer som ble forsøkt.
- Ikke merk arbeidet ferdig uten skjermvisning, kontroll av API og dokumentert teststatus.

## 13. Første arbeidsordre til Codex Cloud

> Arbeid i `Luaze1985/Kunstpixel`. Ta utgangspunkt i branch `feature/hr-simulator-syntetisk-innleie` og draft PR #1 (ikke `main` alene). Les `04_knowledge/04_domain/projects/hr_simulator/SPEC_CODEX_CLOUD_V1.md`, `KUNNSKAPSKART.md` og `AGENTS.md`. Utfør kun **fase A**. Prioriter å koble eksisterende Python/SQLite-simulator til en fungerende lokal webapp med HR-003 ende-til-ende. Kontroller alle godkjenninger på serveren, behold eksterne innleieforslag sperret uten dokumentert grunnlag, bruk kun syntetiske data. Kjør tester, dokumenter faktiske funn og opprett en PR uten automatisk merge. Meld fra dersom GitHub-basen ikke inneholder feature-branchen; ikke erstatt arbeidet med en ny parallell implementasjon.

