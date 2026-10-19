# KI-støttet museumsuke — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Utførelsesmåte velges av brukeren før implementering.

**Goal:** Bygge en lokal øvelse der KI bruker et kildebelagt museumsgrunnlag til å foreslå en samlet bemanningsplan for én uke.

**Architecture:** Research og data etableres som versjonert prosjektgrunnlag først. Gjenbruk eksisterende simulator; en separat FastAPI-prosess serverer API og enkel HTML/JavaScript, med egen varig SQLite-state. Regelmotoren kontrollerer forslag før menneskelig godkjenning; OpenAI leverer forslag som siste integrasjonstrinn.

**Tech Stack:** Python 3.13, SQLite via standardbiblioteket, Pydantic, FastAPI, Uvicorn, HTML/CSS/JavaScript, pytest og OpenAI Python SDK.

**Spec:** `04_knowledge/04_domain/projects/hr_simulator/BEHOV_UKEPLAN_2026-10-16.md`

## Global Constraints
- Python 3.13. Windows PowerShell. Kontroller CLI-tilgjengelighet før bruk.
- Museumsdatabasen 05_data/museum.db forblir skrivebeskyttet og uendret.
- Norsk bokmål. Kun fiktive personer og situasjoner; e-post under example.invalid og telefoner med 000-prefiks.
- Gjenbruk feature/hr-simulator-syntetisk-innleie. Ikke erstatt simulatoren med en ny parallell implementasjon.
- Lokal server bindes til 127.0.0.1. Ingen produksjonssetting, ekte meldinger eller personalsaker.
- Research og kontrollert datagrunnlag må være ferdig før oppgave 3–6 starter.
- Hele pytest-pakken kjøres ved kodeendringer. Tester, nettleserprøving og ekte modellkjøring rapporteres separat.

## Review Focus
- Manglende opplæring eller kildegrunnlag må gi uavklart/udekket behov, ikke en oppdiktet kvalifikasjon. Testes i oppgave 2, 3 og 6.
- En person med flere ferdigheter kan ikke fylle samtidige separate bemanningsposter. Testes i oppgave 3.
- Et ja er ikke automatisk en tildeling; avbud må gjenåpne behovet. Testes i oppgave 4.
- Gamle forslag eller samtidige nettleserfaner må ikke overskrive nyere plan. Testes i oppgave 4.
- Modellfeil, ukjente kilde-ID-er og instruksjoner i kildetekst må ikke endre regler eller gjeldende plan. Testes i oppgave 6.

---

## Oppgave 1: Hent eksisterende arbeid og gjør research til prosjektgrunnlag

**Files:**
- Bevar: `02_deliverables/hr-simulator-demo.html`
- Opprett: `04_knowledge/04_domain/projects/hr_simulator/research_museumsdrift.md`
- Opprett: `04_knowledge/04_domain/projects/hr_simulator/kilder.json`
- Opprett: `04_knowledge/04_domain/projects/hr_simulator/museumsrutiner.md`
- Opprett: `04_knowledge/04_domain/projects/hr_simulator/datamangler.md`
- Oppdater: `KUNNSKAPSKART.md` med pekere til det nye grunnlaget.

**Interfaces:**
- Consumes: eksisterende feature-branch, simulatorfiler, scenarioer og primærkildene nedenfor.
- Produces: kilderegister med `id`, `title`, `url`, `published_or_updated`, `checked_at`, `claim`, `scope`, `verification_status`. Museumsrutiner har regel-ID, kilde-ID eller fiktiv beslutning, og angitt anvendelsesområde. Ukjent dato lagres som null.

- [ ] Kontroller lokal Git-status og remote. Hent feature-branchen til egnet utsjekking uten å overskrive lokalt arbeid. Ved ny worktree brukes superpowers:using-git-worktrees. Bevar original HTML-demo uendret som referanse. Registrer commit-ID som ble brukt.
- [ ] Les feature-branchens AGENTS.md, simulator, scenarioer og tidligere spesifikasjon. Denne behovsspesifikasjonen styrer nytt omfang; tidligere personalsaksflyt skal ikke utvides.
- [ ] Kontroller primærkildene på nytt. Bruk minst tre konkrete museumseksempler: Oljemuseets helgevert, Fredssenterets vertskap og Teknisk museums drift/formidling. Registrer også arbeidsplan, arbeidstid/hvile, innleie og relevant tariffkilde.
- [ ] Skriv researchnotatet med kilder ved hver påstand. Skill lokal museumspraksis, rettslige krav og våre fiktive prosjektvalg. Ikke kopier hele nettsider eller identifiserbare personalsaker.
- [ ] Oversett funn til museumsrutiner for øvelsen: roller, opplæring, språk, forberedelse/stenging, intern ekstravakt, avklaringsbehov og ansvar for beslutning. Ingen universelle bemanningsnormer utledes fra ett museum.
- [ ] Kartlegg hvert nødvendig datafelt mot eksisterende scenarioer: finnes, må suppleres eller er ukjent. Legg manglene i datamangler.md med konsekvens for planleggingen.
- [ ] Kontroller lenker, påstander, kilde-ID-er og merkingen av egne valg. Research er ikke ferdig bare fordi en lenkeliste finnes.
- [ ] Lever researchgrunnlaget som en egen gjennomgåbar dokumentendring før databygging.

Startkilder fra forundersøkelsen, må kontrolleres i denne fasen:
- https://www.norskolje.museum.no/ledig-stilling-som-museumsvert-i-helg-og-omviser/
- https://www.nobelpeacecenter.org/museumsverter-2026
- https://www.tekniskmuseum.no/rapporter/organisasjon-2024
- https://www.tekniskmuseum.no/rapporter/formidling-og-laering-2024
- https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/arbeidsplan-vaktliste-skift-og-turnus/
- https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/
- https://www.arbeidstilsynet.no/lonn-og-ansettelse/innleie-av-arbeidskraft/innleie-fra-bemanningsforetak/
- https://www.virke.no/tariff-og-lonn/finn-tariffavtale/landsoverenskomst-for-museer-og-andre-kulturinstitusjoner/

## Oppgave 2: Lag og kontroller det fiktive datagrunnlaget

**Files:**
- Opprett: `05_data/hr_simulator/planning_week.json`
- Opprett: `src/kunstpixel/hr_simulator/context.py`
- Opprett: `tests/test_planning_context.py`
- Gjenbruk: eksisterende `05_data/hr_simulator/scenarios/` og `schema.py`.

**Interfaces:**
- Produces: `load_planning_context(path: Path) -> PlanningContext` og `build_week_context(context: PlanningContext, week_start: date) -> WeekContext`.
- PlanningContext inneholder personer, opplæring, tidsrom for tilgjengelighet, vakter, aktiviteter, rollekrav, kontaktforløp og kildehenvisninger. WeekContext inneholder valgt uke og relevant historikk/tilstøtende vakter fra fireukersgrunnlaget.

- [ ] Skriv tester som avviser ekte kontaktformater, ukjente person-/kilde-ID-er og ugyldige tidsrom. Test at manglende opplæring forblir ukjent og at forberedelse/stenging inngår i oppgavens tidsrom.
- [ ] Kjør `py -3.13 -m pytest tests/test_planning_context.py -v`; bekreft meningsfull feil før implementering.
- [ ] Suppler de eksisterende fiktive personene og lag fire sammenhengende uker. Ha faste publikumsoppgaver, skolebesøk, montering og kveldsvakter, samt kontaktforløp med ubesvart, nei, ja og avbud. Merk alle konstruerte verdier som syntetiske.
- [ ] Implementer kontekstlasting og validering med Pydantic. Versjoner grunnlaget og gi fakta stabile ID-er. Ingen bred repo-innlasting eller vektordatabase.
- [ ] Kjør testene på nytt. Kontroller manuelt én komplett uke mot research og mangelliste. Ingen regel uten kilde eller uttrykkelig fiktiv beslutning.
- [ ] Lever datagrunnlag og validering som egen endring. Først nå kan oppgave 3–6 starte.

## Oppgave 3: Utvid kontrollmotoren til én sammenhengende uke

**Files:**
- Utvid: `src/kunstpixel/hr_simulator/engine.py` og `schema.py`.
- Opprett: `src/kunstpixel/hr_simulator/planning.py`
- Opprett: `tests/test_week_planning.py`

**Interfaces:**
- Produces: `check_week(context: WeekContext, plan: WeekPlan) -> CheckResult` og `evaluate_proposal(context: WeekContext, current: WeekPlan, proposal: WeekProposal) -> ProposalReview`.
- CheckResult skiller dokumenterte brudd, uavklarte kontroller og udekkede behov. WeekProposal har grunnlagsversjon, endringsgrupper, begrunnelse, kilde-ID-er og manglende informasjon.

- [ ] Skriv tester for overlapp, ulike samtidige roller, delvis tilgjengelighet, manglende kompetanse/opplæring, hvile over ukegrensen og ukjent arbeidshistorikk. Uavklart skal ikke bli bestått.
- [ ] Skriv test som avviser flytting av arrangementstid. Vurder hele uka ved en endring; færre konflikter totalt skal ikke skjule en ny konflikt et annet sted.
- [ ] Kjør `py -3.13 -m pytest tests/test_week_planning.py -v` og bekreft feil før implementering.
- [ ] Implementer kontrollene fra godkjent datagrunnlag. Bruk eksplisitte arbeidstidsforutsetninger; ukjente tariffunntak gir avklaringsbehov. Vis avtalte vakter separat fra faktisk registrert arbeidstid.
- [ ] Lag deterministiske eksempelutkast gjennom samme WeekProposal-interface som OpenAI senere bruker. Merk dem som simulerte og la dem ikke endre planen.
- [ ] Kjør tester og lever motorendringen separat.

## Oppgave 4: Varig lagring og lokalt API

**Files:**
- Opprett: `src/kunstpixel/hr_simulator/store.py` og `api.py`
- Utvid: `schema.py`, `__main__.py`, `pyproject.toml`, `.gitignore`
- Opprett: `tests/test_planning_api.py`

**Interfaces:**
- `GET /api/planning/weeks/{week_start}`: plan, versjon, kontroller, arrangementer og neste handling.
- `GET /api/planning/activities/{activity_id}/candidates`: kompetanse, opplæring, tidskapasitet, kontakt og forklaring.
- `POST /api/planning/contacts`: person, aktivitet, status, faktisk registrert tidspunkt og eventuell svarfrist. Status: ikke kontaktet, forespurt, ja, nei, trukket.
- `POST /api/planning/proposals`: valgt uke og kilde (`simulated` eller `openai`).
- `POST /api/planning/proposals/{id}/decisions`: endringsgruppe, approved/rejected, begrunnelse og forventet planversjon.
- `GET /api/planning/demo/scenarios` og `POST /api/planning/demo/scenarios/{id}/reset`: isolert demo-state.
- Alle operasjoner har eksplisitt arbeidsområde (`work` eller et demo-scenario). Ukjent ID gir 404, feil data 422, gammel planversjon 409; feil inneholder code/message/details.

- [ ] Skriv API-tester for godkjenning, avslag, ja uten tildeling, avbud som gjenåpner behov, gammel versjon, gjentatt beslutning, rollback, omstart og isolert reset.
- [ ] Kjør `py -3.13 -m pytest tests/test_planning_api.py -v`; bekreft feil før implementering.
- [ ] Implementer egen lokal SQLite-state, gitignored, med migreringsversjon. Last startdata bare ved opprettelse eller uttrykkelig reset. Planendring og beslutningslogg lagres i samme transaksjon etter ny kontroll av hele uka.
- [ ] Server API og statiske filer fra én prosess på 127.0.0.1:8001. Kommando: `py -3.13 -m src.kunstpixel.hr_simulator web`. Museumsvertens eksisterende inngangspunkter bevares.
- [ ] Kjør API-testene og full pytest-pakke. Lever varig lokal flyt separat.

## Oppgave 5: Enkel arbeidsflate og demomodus

**Files:**
- Opprett: `src/kunstpixel/hr_simulator/web/index.html`, `app.js`, `styles.css`
- Utvid: `api.py` for statiske filer og `README.md` med kjøring.

**Interfaces:**
- Consumes: API fra oppgave 4; ingen separate kopier av scenarioer i JavaScript.
- Produces: ukeoversikt, arrangementsdetaljer, kandidater, kontaktregistrering, forslag og beslutningshistorikk.

- [ ] Bygg ukeoversikten med faste oppgaver, arrangementer, bemanningsstatus og neste handling. Vis foreslått og gjeldende plan hver for seg.
- [ ] Vis kildegrunnlag og kontrollresultat per forslag. Gi hver endringsgruppe godkjenn/avvis. Etter mutasjon hentes oppdatert state fra API; nettleseren er ikke sannhetskilde.
- [ ] Bevar valgt uke/arrangement ved navigasjon og gjenhent lagret status ved oppdatering. Vis lagringsfeil; ikke presenter en mislykket lagring som gjennomført.
- [ ] Lag separat demomodus med scenarioene fra behovet. Nullstilling påvirker bare valgt scenario.
- [ ] Prøv hele flyten i nettleser: registrer kontakt, registrer ja, godkjenn, bytt arrangement, oppdater siden og start serveren på nytt. Kontroller at samme status består. Prøv også avbud, tastaturbetjening og mobilbredde.
- [ ] Dokumenter faktisk resultat og skjermbilder. Finpuss navigasjon og forståelse nå; visuell profil kan tas senere.

## Oppgave 6: OpenAI-forslag og separat evaluering

**Files:**
- Opprett: `src/kunstpixel/hr_simulator/openai_planner.py`
- Opprett: `tests/test_openai_planner.py`
- Utvid: `api.py`, `pyproject.toml`, `README.md`

**Interfaces:**
- Produces: `generate_week_proposal(context: WeekContext, current: WeekPlan, *, model: str) -> WeekProposal` gjennom OpenAI Responses API og strukturert output.
- API-nøkkel leses på serveren fra OPENAI_API_KEY. Modell angis eksplisitt med KUNSTPIXEL_OPENAI_MODEL; ingen hemmeligheter i nettleser, repo eller logger.

- [ ] Skriv tester med simulerte API-svar: gyldig forslag, ukjent kilde/person, endret arrangementstid, manglende fakta, ugyldig format, timeout og modellavslag. Kildetekst kan ikke endre systemregler.
- [ ] Kjør `py -3.13 -m pytest tests/test_openai_planner.py -v`; bekreft feil før implementering.
- [ ] Implementer én eksplisitt utløst modellkjøring per forespørsel. Send avgrenset fiktiv kontekst med fakta-ID-er. Strukturell validering suppleres med kontrollmotoren; modellen får ingen direkte skrivetilgang.
- [ ] Ved API-feil bevares gjeldende plan og en forståelig feil vises. Ingen skjult erstatning med simulerte forslag. Vis modell og faktisk tokenbruk når tilgjengelig.
- [ ] Kjør full pytest-pakke. Gjennomfør deretter separat ekte modellprøve med kontrollert API-oppsett: normal uke, kompetansemangel og avbud. Vurder kildebruk, udekkede behov og prioriteringen av minst mulig vaktendring.
- [ ] Kontroller at museum.db er uendret. Dokumenter lokal teststatus, nettleserbevis og ekte KI-resultat hver for seg. Ikke hevde at godkjent JSON beviser kontekstforståelse eller at alle bemanningskontroller er bestått.

## Utførelsesrekkefølge og godkjenning
1. Kildearbeid og eksisterende feature-arbeid.
2. Fiktive data og kontroll av proveniens.
3. Ukemotor.
4. Varig API.
5. Brukerflyt og demomodus.
6. OpenAI og evaluering.

Oppgave 1–2 utgjør første leveranse og kontrollpunkt. Ingen bygging av den nye applikasjonsflyten før dette grunnlaget består kriteriene. Planen er dokumentert; innhenting, databygging og implementering er ikke utført ved lagring av planen. Brukeren bekrefter plan og utførelsesmåte før implementering; ingen automatisk merge eller deploy.
