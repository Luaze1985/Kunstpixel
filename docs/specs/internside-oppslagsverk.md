# Spesifikasjon: Internsiden – oppslagsverk i håndbøkene med AI-svar

**Status:** ready-for-agent · **Dato:** 2026-10-24 · **Grunnlag:** ADR-013, ADR-012, ADR-004, AGENTS.md §7
**Oppgaver:** [internside-oppslagsverk/](internside-oppslagsverk/)

## MVP (besluttet av Lars 2026-10-24)
**Mål:** Lars skriver et spørsmål på en åpen nettside og får treffene fra håndbøkene, med et kort AI-svar
øverst som viser kildene. AI-kostnaden har et tak.

**Rekkefølge:** 02 → 03 → 04 → 05. Oppgave 01 og 06 kommer etter MVP.

**Fasit:** [`tests/test_mvp_oppslag.py`](../../tests/test_mvp_oppslag.py) har seks vitale sjekker, skrevet før
koden. Hver sjekk er merket med oppgaven den hører til (`@VENTER_PA_02` til `@VENTER_PA_05`). Når en oppgave
er ferdig, fjernes merkene for den oppgaven, og sjekkene skal da bestå. Sjekkene i seg selv endres ikke uten at
Lars godtar det. Kontrakten (funksjonsnavn og returverdier) står øverst i fila.

**Prompt til bygger (Codex eller annen LLM). Bytt ut NN med oppgavenummeret:**
```text
Repo: G:\Min disk\Kunstpixel. Windows og PowerShell. Python: py -3.13.
Les først: AGENTS.md, docs/specs/internside-oppslagsverk.md (MVP og «Regler for agenten som bygger»),
oppgavefilen docs/specs/internside-oppslagsverk/NN-*.md og tests/test_mvp_oppslag.py.
Bygg bare oppgave NN.

Fasit: sjekkene i tests/test_mvp_oppslag.py som er merket @VENTER_PA_NN. Endre koden, ikke sjekkene.
Når de består, fjerner du bare merket @VENTER_PA_NN foran dem.

Arbeidsmåte:
1. Lag grenen codex/NN-<kort-navn> fra hr-konsolidering.
2. Bygg til sjekkene for oppgave NN består, og til akseptkravene i oppgavefilen er oppfylt.
3. Kjør `py -3.13 -m pytest -q` (alt grønt, og sjekkene for senere oppgaver står fortsatt som xfail) og
   `py -3.13 scripts/db_status_gate.py` (KLAR).
4. Commit bare filene du har endret, med `git add <fil>` og aldri `git add -A` eller `git add .`. Ikke push.

Forbudt: å skrive til 05_data/museum.db, å kjøre build_museum_db.py uten --check, å endre
05_data/kilde/museum_base.db og å endre innholdet i sjekkene i test_mvp_oppslag.py.

Lever: en liste over endrede filer, siste linje fra pytest, siste linje fra statusporten og
commit-hash. Skriv «STATUS: UNTESTED» hvis noe ikke ble kjørt.
```

## Problembeskrivelse
Håndbøkene (personal, HMS, drift, leder og SOP-rutiner) finnes som md-filer og som en søkbar indeks i
`museum.db`, men det er ingen enkel side der man skriver et spørsmål og får svar. I tillegg er det tre ting
som skurrer:

- **Indeksen oppdateres ikke riktig.** `handbok_oppslag` ligger i det frosne grunnlaget `museum_base.db` og
  kopieres bare videre ved bygging. ADR-012 sier at endringer leses inn med `seed_handbooks.py`, men det
  skriptet skriver rett i `museum.db`. Det bryter regelen om at bare byggeskriptet skriver databasen
  (ADR-004 og AGENTS.md §7), og endringen forsvinner ved neste bygg.
- **Datafinner har to utgaver.** Demokopien (`build_demo_db.py`, `DATAFINNER_DEMO`) skal bort etter ADR-013.
- **AI-laget forklarer bare rapporter.** Det finnes ikke noe som svarer på et spørsmål med kilder fra håndbøkene.

## Løsning
Lars åpner internsiden og ser ett søkefelt midt på siden. Han skriver for eksempel «hvor mange dager
egenmelding?». Under feltet kommer de vanlige treffene fra håndbøkene, med håndbok, kapittel og punkt-ID.
Er AI-laget slått på, kommer et kort svar øverst, merket **AI-forslag**, med lenke til punktene svaret bygger
på. Finnes ingen treff, står det at ingen kilde ble funnet, og AI-en blir ikke spurt. Siden virker fullt ut
uten AI. AI-en endrer aldri dokumentene.

Siden hostes åpent, uten innlogging, mot full `museum.db`. Grensen på antall AI-kall (standard 20 per time)
beskytter Claude-nøkkelen.

## Brukerhistorier
1. Som Lars vil jeg skrive et spørsmål i ett felt og få håndbokpunktene som passer, slik at jeg finner
   rutinen uten å bla i fire håndbøker.
2. Som Lars vil jeg få et kort AI-svar som viser hvilke punkter det bygger på, slik at jeg kan sjekke svaret
   mot kilden.
3. Som Lars vil jeg få beskjed om at ingen kilde finnes når håndbøkene ikke dekker spørsmålet, i stedet for
   et oppdiktet svar.
4. Som Lars vil jeg kunne endre en håndbok i md-filen og få endringen inn i databasen ved neste bygg, uten
   et eget skript som skriver i databasen.
5. Som Lars vil jeg ha én utgave av Datafinner, slik at nye verktøy ikke må holdes i takt med en demokopi.
6. Som Lars vil jeg at AI-kostnaden har et tak, slik at en åpen side ikke kan tømme kontoen min.
7. Som ansatt i en arbeidsrolle (for eksempel Salvert eller Kafé) vil jeg kunne avgrense treffene til min
   rolle, slik at jeg ser rutinene som gjelder meg.

## Beslutninger om implementasjon

**Håndbøkene leses inn i bygget**
- Byggeskriptet sletter og bygger `handbok_oppslag` på nytt fra md-filene (håndbøker og `SOP-*.md`) ved hvert
  bygg. Kopien i grunnlaget blir da overflødig, men grunnlaget endres ikke.
- `seed_handbooks.py` blir en modul som bare leser og deler opp md-filene. Den åpner ikke lenger noen database.
- `siste_revidert` skal være deterministisk og må aldri komme fra dagens dato. Den kan stå som fast verdi
  eller leses fra filen. Hensikten er at to bygg gir samme innhold.
- Paritet er bekreftet 2026-10-24: md-filene gir i dag nøyaktig de samme 99 radene (alle 11 kolonner) som
  `museum_base.db`.
- Skjemaet er uendret, så `SKJEMAVERSJON` trenger ikke økes.
- `--check` vil vise ULIK etter endringen selv om innholdet er likt, fordi tabellen skrives på nytt
  (rader og sider får ny plassering). Akseptkravet er derfor likt innhold, ikke lik hash.
- ADR-012s «Oppfølging» erstattes av et tillegg: endringer leses inn ved bygg, og Lars bygger.

**Demokopien fjernes (ADR-013 punkt 1)**
- Følgende fjernes: `build_demo_db.py`, `scripts/start_demo.py`, `bruk_demomodus`, `DEMO`, `FILVERKTOY`,
  `DEMO_SKJULTE_SIDER`, `BEHOLD`/`TOMMES`, testene for dem og `demo`-feltet i `/api/status`.
- Docker-bildet bruker full `museum.db`.
- Mappen `deploy/demo/` beholder navnet. Navnet byttes eventuelt i en egen opprydding.

**Oppslag uten AI**
- `lookup_handbook` legges i hvitelisten i Datafinner. Søket gjøres av `query_handbook` i `core/db.py`, med
  dagens nøkkelordsøk.
- Det kommer en egen oppslagsside (eller oppslagsvisning) med ett søkefelt. Treffene viser punkt-ID, håndbok,
  kapittel, avsnitt og innhold.

**AI-svar på oppslag**
- `llm.py` får en egen funksjon for håndboksvar. `forklar()` er laget for rapporter og gjenbrukes ikke.
  Funksjonen får spørsmålet og de N beste punktene (punkt-ID og tekst), og ingenting annet.
- Systemprompten krever at svaret bare bygger på punktene som er sendt, nevner punkt-ID-ene og sier fra når
  punktene ikke dekker spørsmålet. Instruksjoner som står inne i punktene skal ikke følges.
- **Kildekontroll** (tilsvarer `tallkontroll`): hver punkt-ID i svaret må være blant punktene som ble sendt.
  Ukjente ID-er flagges i svaret til siden.
- Gir oppslaget null treff, svarer siden «fant ingen kilde» uten å kalle AI.
- Grensen er 20 kall per time som standard i både `llm.py` og `compose.yaml`. Oppstarten stopper med en
  tydelig melding hvis AI er på og `LLM_MAKS_PER_TIME` ikke er et positivt heltall.
- Sperrene som finnes for `/api/forklar` gjelder også det nye AI-endepunktet: Origin, Sec-Fetch-Site,
  Content-Type og størrelse. Begrunnelsen i kommentaren oppdateres. Sperrene stopper ikke lenger misbruk av
  innlogging, siden innloggingen fjernes. De stopper andre nettsider fra å bruke kvoten.

**Åpen hosting (Lars, 2026-10-24)**
- `basic_auth`, `bruker.sh` og `brukere.caddy` fjernes fra hostingen. HTTPS og sikkerhetshoder beholdes.
- Filsøket er med: bildet får mappene i `MAPPER` (`00_felles`, `01_inbox`, `02_deliverables`, `03_team`,
  `04_knowledge`, `05_data/governance`). Lars har vurdert at alt der er syntetisk.
- Docker kopierer fra arbeidsmappen, ikke fra git. Filer som ikke er i git (for eksempel `01_inbox/raw/`)
  kommer derfor også med. Før publisering lager et skript listen over alle filer som havner i bildet, og
  Lars går gjennom den.
- Grensen i koden nullstilles når serveren starter på nytt. Lars setter i tillegg et månedlig utgiftstak i
  Anthropic-konsollen. Det gjøres manuelt.

**Arbeidsroller (ADR-013 punkt 5)**
- Rollelisten (6–8 roller) og koblingene ligger som syntetiske CSV-filer i `05_data/`, med `datakilde` som
  starter med «syntetisk». Koblingene går fra stilling i `hr_ansatte` og fra `malgruppe` i håndbøkene til en
  eller flere roller.
- Dataene bygges inn av byggeskriptet. Oppslaget kan filtreres på rolle.
- Selve rollelisten bekreftes av Lars før dataene lages. Ordlisten foreslår Salvert, Montør/drift, Kafé,
  Formidling, Samling/kurator, Leder og Verneombud.

## Teststrategi og testgrenser
Godkjent av Lars 2026-10-24.
- **Hva som testes automatisk:**
  - Bygget gir samme `handbok_oppslag`-innhold som md-filene, og to bygg gir likt innhold.
  - `seed_handbooks.py` åpner ingen database.
  - Oppslag gir punkter med riktige felt.
  - Null treff gir «ingen kilde» uten AI-kall (den falske leverandøren skal ikke bli kalt).
  - Kildekontrollen flagger ukjente punkt-ID-er.
  - Grensen stopper kall nummer 21 innen en time (med falsk klokke).
  - Oppstarten stopper ved ugyldig grense.
  - Siden og API-et svarer når AI er av.
  - Statiske tester for hosting: ingen `basic_auth`, ingen `DATAFINNER_DEMO`, standard 20.
- **Testgrense:** de offentlige funksjonene i `core/db.py`, `core/llm.py` og rutefunksjonene i Datafinner,
  mot en midlertidig bygget database (`bygget_db`-mønsteret) og en falsk `apne` for AI-leverandøren.
  Ingen nettverkskall i testpakken.
- **Hva som ikke testes automatisk:**
  - Ekte kall til Claude.
  - Klikk i nettleseren og visuell sjekk av siden.
  - Docker-bygget ende til ende (`scripts/test_demo_container.ps1`, krever Docker).
  - Gjennomgangen av fillisten før publisering.
  - Utgiftstaket i Anthropic-konsollen.

## Avgrensning (lages ikke nå)
- Kompetanseplan 2027, `rollekrav`-tabellen og kobling til utstillinger og interne prosjekter.
- Chat eller samtalehistorikk. Siden gir ett svar per spørsmål.
- At AI-en skriver eller endrer håndbøker eller andre dokumenter.
- Semantisk søk (embeddings). Dagens nøkkelordsøk beholdes, og svake treff på naturlige spørsmål er en
  kjent risiko.
- En grense for AI-kall som overlever omstart, og grense per bruker.
- Nye interne verktøy i Datafinner ut over `lookup_handbook`, for eksempel `get_employee_skills` og
  `search_internal_requests`. Varsler (CASE-013) skjermes fortsatt.
- Å bytte navn på `deploy/demo/`.
- Å bygge `museum.db`. Det gjør Lars.

## Regler for agenten som bygger
- Ikke rør eller commit filene som lå endret fra før: `src/hr_cli.py`, `HRDEMO_MAKSINLESBAR.md`,
  `context_index.yaml`, `CHEATSHEET.md`, `04_knowledge/06_hr_caser/`, `src/kunstpixel/cases/` og
  `tests/test_hr_cases.py`.
- Ingen skriving mot `museum.db`. Bygget kjøres bare med `--check`.
- `py -3.13 -m pytest -q` skal være grønn etter hver oppgave.
