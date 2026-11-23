# Beslutninger

## 2026-11-06 — Demo-databasen med én startkommando

Bestemt av Lars etter grilling. Planen ligger i `docs/plans/2026-11-06-demo-database.md`.

| Beslutning | Valg | Hvorfor |
|---|---|---|
| Første bruker | Lars, på egen PC (kurs og kundemøter) | Ingen hosting eller installasjon hos andre trengs nå |
| Flaten som åpnes | Datafinner (port 8010) | Viser best «Fasit vs. Skjønn»: tallene kommer fra databasen, og KI bare formulerer |
| Versjon | Låst git-tagg (`demo-v1`, `demo-v2` …) | Halvferdig arbeid i hovedmappen skal ikke kunne knekke demoen |
| Plassering | Lars flytter demomappen selv | Skriptet går til sin egen repo-rot og virker derfor fra hvilken som helst mappe |
| KI | Av som standard, `-KI` slår den på | Demoen virker uten nett. KI vises bare når Lars ber om det |
| Python-pakker | Globale `py -3.13`. Skriptet sjekker `mcp==1.29.1` | Ingen venv å vedlikeholde. En feil versjon stopper skriptet med en tydelig melding |
| Innhold i demo-v1 | Siste commit på main pluss startskriptet | De 18 ucommittede endringene fra 2026-11-06 kommer i demo-v2 |

Rulings under byggingen:
- `hr_cli init --reset` er ikke med. HR-tabellene ligger i `museum.db` (ADR 004), og den committede databasen har `hr_people`.
- Oppstartsjekken bruker `scripts/db_kvalitet.py --uten-bygg` og sjekksummen i `05_data/museum.db.sha256`. Begge bare leser og tar rundt 6 sekunder. `db_status_gate.py` er ikke brukt, fordi den bygger databasen to ganger og kjører hele pytest. Den er laget som port før sammenslåing.
- Datafinners KI-lag bruker `urllib` og `.env` (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`), ikke `anthropic`-pakken. Skriptet slår av KI ved å sette `LLM_PROVIDER` til et mellomrom. En variabel som allerede er satt, vinner over `.env`.
- `mcp` er låst til `==1.29.1` i `pyproject.toml`, i tråd med `AGENTS.md`.
- Skriptet bruker `$ErrorActionPreference = 'Continue'`. Med `Stop` ble stderr fra `py` en rå feil i PowerShell 5.1, og STOPP-meldingen ble skjult. Datafinner startes med `python.exe` direkte, så det er selve serveren som stoppes.

## 2026-11-06 — Datafinner i ett vindu (prototype på `ux/ett-vindu`)

Lars: «alt i ett vindu, med tre paneler». Gjelder `02_deliverables/arbeidsflyt/SPEC.md:5`. Lars overlot de tekniske valgene til Claude («du vet best»).

| Beslutning | Valg | Hvorfor |
|---|---|---|
| Plassering | Ny side `/ett-vindu` ved siden av dagens sider | Kan prøves uten å fjerne noe. Kan angres ved å slette én fil og én linje. |
| Venstre panel | Arena (6 områder), Roller (med spørsmål), Flater (Chat, Vaktrom, Søk, Arbeidsflyter) | Alt som kan velges, står på ett sted. Arena står først fordi den virker uten KI. |
| Midten | Svaret hentes med én gang med standardverdier. «Oppdater» vises bare når det finnes felt. | Løser F3 og F4 (ett klikk, én tittel). |
| Høyre panel | «Fasit»: verktøykall, kilde, regel og KI-status | Viser skillet mellom fasit og skjønn (MISSION.md). |
| Data | Bare eksisterende API-er (`/api/rapport`, `/api/arena/kjor`, `list_roles`, `/api/verktoyskjema`). Ingen ny Python-logikk. | Én kilde til spørsmål og roller. |
| Visning | Generisk: nøkkeltall, én tabell uten kontaktinfo, ID-er eller kolonner med lik verdi | Løser F6 for skallet. Alle 16 spørsmål og 21 caser vises uten egen kode. |
| Flater som ikke er flyttet inn | Kort med «Åpne» og merket «Krever KI» for Chat | De flyttes inn én om gangen etter at Lars har godkjent skallet. |
| Forside (oppgave 08, Lars 2026-11-06) | `/` serverer skallet. De gamle sidene ligger i `arkiv/2026-11-datafinner-gamle-sider/`, og de gamle adressene gir 302 til riktig visning. | Én inngang. Gamle lenker virker fortsatt. Ingenting er slettet. |
| Arbeidsrolle og «Jeg er» (B5, Lars 2026-11-06) | To lister uten kobling. Arbeidsrollen velges inne i Arbeidsflyter. | Ingen endring i datamodellen, og Lars trenger ikke bygge. En kobling kan legges til senere som egen tabell. |

## Linjeskift i en ny utsjekk (funnet og rettet 2026-11-06, Lars valgte å rette)
- Tre tester feilet i en ny utsjekk av main `0ba51e4`: `test_leveranse_kjoring` (2) og `test_publikum_data` (1). Årsaken var `core.autocrlf=true`, som ga CRLF ved utsjekk, mens generatorene skriver LF og testene sammenligner byte for byte.
- Rettet i `.gitattributes`: `*.csv`, `01_inbox/h5_colab/*.py` og `src/kunstpixel/core/intern/leveranse*.py` får `eol=lf`. `SJEKKSUM.txt` er unntatt, fordi `skriv_colab_pakke` skriver den med plattformens linjeskift.
- Ingen filinnhold er endret, bare hvordan git sjekker ut. Hele pytest er grønn i en ny utsjekk.
- **Rettet 2026-11-10 (revisjonsfunn 7):** påstanden over holdt ikke. Etter sammenslåingen `5cbce56` hadde `SJEKKSUM.txt` hashene av CRLF-bytes, mens filene i git er LF. Testene var grønne bare fordi arbeidsmappen hadde gamle CRLF-kopier. Nå normaliserer `skriv_colab_pakke` alltid til LF, `SJEKKSUM.txt` har `eol=lf`, og to nye tester låser dette. Ikke kontrollert i en ren utsjekk ennå.
- Kjent støy: `test_org_builder` skriver fire `05_data/mock_*.csv` på nytt med `\r\n`, slik at `git status` viser dem som endret selv om `git diff` er tom. Dette skjedde også før. Rett eventuelt med `lineterminator="\n"` i `org_builder.write_csv`, eller ved å la testen skrive til en temp-mappe.

## 2026-11-06 — «AI-forslag» er kildemerket, «KI» er ordet i tekst (oppgave 03)
- Planens B3 («KI» overalt, også «KI-forslag») er endret. «AI-forslag» er et fast kildemerke i designsystemet Arbeidsflyt (`DESIGN.md:390`: Bekreftet, AI-forslag, Bør verifiseres, Mangler) og brukes i testene. Merket beholdes. All annen tekst sier «KI».
- Mønster å huske: flere `af-*`-klasser i `af.css` (`.af-report-block`, `.af-actions`, `.af-alert`) har `display`, som overstyrer `hidden`. Skjul med `style.display = "none"`. Bør bli en fast sjekk (kandidat til `/retro`).

## 2026-11-09 — Kunstpixel operativt etter flytting fra Drive (grilling-økt)

Utgangspunkt (fakta sjekket i økten):
- Lokal kopi `C:\Users\larse\Documents\Kunstpixel` virker: 2155 tester grønne, 9 hoppet over, 2 xfail (~2 min).
- Drive-kopien `G:\Min disk\Kunstpixel` er fortsatt et eget git-repo, én commit bak, med 14 worktrees og 19 grener som ikke finnes lokalt eller på GitHub.
- `scripts/oppstart_bygger.ps1` og `scripts/pixel_bygger.ps1` har hardkodet `G:\Min disk\Kunstpixel`.
- `.claude/agents/designsystem-team.md` leser `G:\Min disk\Designssystemer\arbeidsflyt`.
- `.claude/launch.json` (`datafinner-demo`) peker på `scripts/start_demo.py`, som ikke finnes.
- MCP-serverne i repoet er ikke registrert i noen klientkonfig.

Beslutninger:
1. **Lokal mappe er eneste arbeidssted.** Drive-kopien slettes — men først etter punkt 2.
2. **Redd alt fra Drive før sletting.** Alle 19 unike grener hentes inn lokalt (`git fetch` fra Drive-mappen), og worktrees sjekkes for ucommittet arbeid.
3. **Første bruker er Lars selv, for å øve agentbygging.** Ikke deling, hosting eller kurs nå.
4. **Én vei inn: én lokal nettside** bygget på Datafinner. Andre innganger (CLI-er, MCP-servere, API-er) blir byggeklosser bak siden.
5. **Gratis først, KI på knapp.** Siden starter uten API-nøkkel; oppslag, kart og leksjoner er deterministiske. KI-chat er en bryter som virker når nøkkel finnes i `.env`.
6. **Grunnmuren er grenen `ux/ett-vindu`** (8 av 9 oppgaver fra spec «Datafinner i ett vindu»). Den hentes inn, testes mot dagens main, fullføres (oppgave 9), og får kart (`06_kart`) og leksjoner (`lessons/`) som faner.
7. **Designsystemet `arbeidsflyt` kopieres inn i Kunstpixel** (fast kopi), og designsystem-agenten peker dit. Kjent avveining: kopien kan gli fra originalen.
8. **Utvidelser: lekegren + rask røyktest.** Hvert eksperiment på egen gren (`scripts/ny_forgreining.ps1`), en røyktest under ~15 sek (siden starter, databasen er hel), full pakke før innfletting i main.

9. **«Operativt» godkjennes ved å se siden først.** Prøvesammenslåing av `drive/ux/ett-vindu` i `C:\tmp\kp`: én konflikt (`.gitattributes`, løst ved å beholde begge regelsett), 2155 tester grønne, siden kjører uten API-nøkkel (testet på :8020). Main røres ikke før Lars sier ja.

10. **Aura fjernes helt med ett deterministisk søk-og-erstatt-skript.** «Aura Kunstmuseum (Kunstpixel)», «Aura Kunstmuseum», «Aura Museum» → «Kunstpixel» (genitiv «Kunstpixels»). Inventarnumre `AURA-` → `KP-`. Kodenavn `AURA_DB_PATH`/`AURA_TODAY`/`aura_id` → `KUNSTPIXEL_DB_PATH`/`KUNSTPIXEL_TODAY`/`kp_id`. Ord som «restaurant» holdes utenfor (ordgrense). Databasene (`museum.db`, `kilde/museum_base.db`) endres med samme regler via SQL, ikke tekst-erstatning i binærfil. En test feiler hvis «Aura» dukker opp igjen. Lars må selv endre `AURA_DB_PATH` hvis den er satt i Windows.
11. **Minst mulig støy.** Forsiden er rapportene. Datakatalogen (alle 56 tabeller, 85 000 rader) ligger skjult bak en diskret lenke i rapportvinduet, og Lars oppsøker den selv.
12. **LLM som egen inngang: chat.** Chatten ligger på samme side, men som eget sted ved siden av rapportene, ikke oppå dem. Den svarer gjennom de 45 hvitelistede verktøyene. Uten nøkkel er den slått av, og rapportene virker uansett (jf. punkt 5).

10a. **Utført 2026-11-09** med `scripts/fjern_aura.py` og vakttest `tests/test_ingen_aura.py`. Bytter utover punkt 10 (valgt av agenten): «Aura Museumsvert/Bokhandel/MCP Server» → «Kunstpixel …», «AURA MUSEUM» → «KUNSTPIXEL», `aura-museum`/`aura-kunstmuseum` (MCP-navn i `.codex/config.toml`) → `kunstpixel`, `src/aura_museum/` → `arkiv/kunstpixel_legacy/`, `aura_museum_komplett.json` → `kunstpixel_komplett.json`, små/blandede ID-er beholder skrivemåten (`kp-`, `Kp-`). `museum_base.db` endret via SQL (136 celler, «Laura» urørt). `museum.db` bygget én gang av agenten med `build_museum_db.py` etter Lars' ja i økten.

11a. **Utført 2026-11-09:** `GET /api/katalog` (alle tabeller, antall rader og kolonner) og `GET /api/katalog?tabell=navn` (de 25 første radene). Skrivebeskyttet, og bare et eksakt tabellnavn fra `sqlite_master` slipper gjennom til SQL. Katalogen er ikke et verktøy for språkmodellen og står ikke i menyen. Den nås bare fra lenken «Se alle tabellene i databasen» inne i «Vis grunnlag» i en rapport.

12a. **Utført 2026-11-09:** Chatten fantes alt (`/api/chat`, alle 45 verktøy, tallkontroll, av uten nøkkel). Lars valgte en egen knapp øverst i menyen: «Spør KI» står over rapportene og er tatt ut av «Flater». Chatten åpnes i midten og erstatter rapporten mens den er åpen. Chatpanel i høyre kolonne ble valgt bort. Ikke testet med ekte nøkkel i denne økten.

12b. **Startkommando (2026-11-09):** Den fantes alt: `start_demo.cmd` → `scripts/start_demo.ps1` (sjekker Python, mcp, port 8010, sjekksum, datakvalitet og selvtest, og åpner siden). Kjørt fra ende til ende etter Aura-byttet: alle sjekker OK. Den døde oppføringen `datafinner-demo` i `.claude/launch.json` peker nå på dette skriptet.

13. **Din egen Claude via MCP, ikke API-nøkkel (2026-11-09, Lars' valg).** Poenget er at Lars øver med sin egen Claude på abonnementet. `.mcp.json` i prosjektroten registrerer serveren `kunstpixel` (`src/kunstpixel/core/mcp_server.py`, 51 verktøy, lesing mot museum.db) for Claude Code. Ingen nøkkel og ingen ekstra regning. Inngangsfila `src/mcp_server.py` fant ikke pakken `src` og er rettet. «Spør KI» på nettsiden krever fortsatt en API-nøkkel (betales per bruk) og blir stående av. Ingen `.env` finnes, verken lokalt eller på Drive.

14. **«Spør KI» på nettsiden går via din egen Claude (2026-11-09, Lars' valg).** Ny KI-leverandør `claude-cli` (`src/kunstpixel/core/claude_cli.py`): siden kaller den lokale claude-kommandoen på abonnementet, uten API-nøkkel. Låst: ingen innebygde verktøy (`--tools ""`), bare Kunstpixel-MCP og bare Datafinners hvitelistede verktøy (`--allowedTools`), ingen brukerinnstillinger eller hooks (`--setting-sources ""`), ingen lagret økt, tom arbeidsmappe, spørsmålet på stdin. `start_demo.cmd -KI` bruker dette når `.env` mangler nøkkel. Testet med to ekte spørsmål (Sal A, brann). Svartid ca. 10–20 sekunder.

15. **Mål fremover (Lars, 2026-11-09, ikke bygget ennå):** «deilige, smoothe rapporter, og LLM som finner data, krysskobler og lager sammenhenger». Designkritikken som ligger til grunn: `docs/design/2026-11-09-designkritikk-datafinner.md`. Hvordan dette bygges, er ikke avgjort.

Rekkefølge: (1) slå `ux/ett-vindu` inn i main, (2) Aura-skriptet + vakttest, (3) skjult datakatalog, (4) chat-inngang, (5) én startkommando.

Åpent / ikke avgjort:
- Oppgave 9 (rapporter for Samlingsforvalter og Formidler) venter på Lars' valg av rapporter.
- Kart og leksjoner som faner, og én startkommando, kommer etter sammenslåingen.
- Hvilke innganger som arkiveres (Telegram-bro og `chat_hub` foreslått).
- Hvor kopien av designsystemet skal ligge (forslag: `00_felles/design/`).

## 2026-11-10: revisjonsfunnene (gren `fix/revisjon-2026-11`)

Plan og vurdering av alle 17 funn: `docs/plans/2026-11-10-revisjonsfunn.md`.

Lars' valg:
- **R1.** Funn 1: navnekolonnen fjernes fra `hr_people`. Navn hentes alltid fra `hr_ansatte`. (Pakke 3, ikke bygget ennå.)
- **R2.** Funn 2: rollen i intern-siden velges fortsatt av klienten. Akseptert fordi siden bare binder til 127.0.0.1. Må rettes før intern-siden hostes: rolle settes ved oppstart og valideres med `role_id()`.
- **R3.** Funn 4: Colab-databasen og MintHCM-dumpen tas ut av sporingen. Git-historikken røres ikke. (Pakke 2, ikke gjort ennå.)
- **R4.** Hele revisjonen gjøres nå, pakke for pakke, selv om bare funn 1 er synlig i demoen.
- **R5.** Funn 16 (e-postdomene og telefon) gjøres ikke. Systemet sender ingen e-post, og et domenebytte krever endring i den frosne `kilde/museum_base.db`.

Valg jeg (Claude) tok underveis i pakke 1. Si fra hvis noen skal gjøres om:
- **R6.** Funn 7: `skriv_colab_pakke` normaliserer alltid til LF, i stedet for bare å lage sjekksumfilen på nytt. Grunn: sjekksummen ble regnet av bytes på disken og var derfor plattformavhengig i selve koden. Kostnad hvis feil: en pakke laget på Windows har LF i stedet for CRLF.
- **R7.** Funn 9: de fire ureferte skriptene er flyttet til `arkiv/2026-11-skript-som-skrev-i-museum-db/`, og `seed_handbooks.py` stopper med en melding hvis den kjøres direkte. Vakttesten bruker en godkjentliste for skript som skriver til andre databaser. Kostnad hvis feil: `git mv` tilbake.
- **R8.** Funn 11: testen sammenligner lagret YAML med det generatoren lager, i stedet for å telle poster mot databasen som planen sa. Grunn: det fanger håndretting direkte, og CSV mot database er alt testet. Kostnad hvis feil: et avvik mellom YAML og database som ikke skyldes håndretting, fanges ikke her.
- **R9.** Funn 13: `fastmcp` er fjernet fra `pyproject.toml` (0 importer). pandas, numpy, duckdb og requests ligger i en valgfri gruppe `data`, ikke som faste avhengigheter. Kostnad hvis feil: én linje tilbake.
- **R10.** Funn 14 har ingen rød test: `anthropic` er installert her, så feilen kan ikke vises uten å avinstallere pakken. Endringen er `importorskip` i to tester.

Testet: hele pytest 2220 bestått, 9 hoppet over, 2 ventede feil. De berørte testene (59) er også kjørt grønt i en ren utsjekk. Ikke testet: Linux og Colab.

Pakke 2 (2026-11-10, commit `6316ab5`):
- **R11.** Funn 5: alle seks konklusjonskolonnene er flyttet til `fasit/personvern_trondheim_fasit.csv` (Lars' valg). Det gjelder både CSV-en og tabellen `ekstern_osint_trondheim` i Colab-databasen.
- **R12.** GitHub-repoet er offentlig. De gamle fødselsnumrene, helsefeltene og fasiten ligger fortsatt i historikken der. Lars valgte å rette fremover og ikke røre historikken. Om repoet skal gjøres privat, avgjør Lars selv.
- **R13 (Claude).** Fasitfilen ligger i `fasit/` i repo-roten, ikke i `05_data/fasit/` som planen sa. Grunn: notatboken leter etter data i `05_data` på Drive, og da ville fasiten blitt lastet opp sammen med angrepsdataene. Kostnad hvis feil: flytt én mappe og én sti.
- **R14 (Claude).** Funn 3, 4 og 5 er én commit, ikke tre. Grunn: den nye databasen måtte tas ut av sporingen i samme commit som den ble laget, ellers hadde en ny 99 MB-fil havnet i historikken.
- **R15 (Claude).** Generatoren skriver nå LF i alle tre CSV-ene, som resten av datafilene.
- `02_deliverables/02_rapporter/personvern_trondheim_colab.html` er et gammelt øyeblikksbilde uten generator. Det har ingen fødselsnumre, men viser de gamle fasitkolonnene. Det er ikke endret.

Testet: generatoren og notatboken er kjørt lokalt. Notatboken virker med og uten fasit. 8 nye tester er grønne. Ikke testet: i selve Colab, og kopien på Drive er ikke oppdatert.
- **R16 (Claude).** Pakke 2 ble committet før Lars så sammenligningen gammel/ny, i strid med planen. Sammenligningen var ren (bare `syntetisk_fnr` endret, alle 1008 fasitverdier like). Ingenting er pushet, så commiten `6316ab5` kan gjøres om.
- **Felle ved grenbytte:** de to filene som ikke lenger spores, er fortsatt sporet på `design/startbilde`. Bytter du dit, legger git tilbake den gamle databasen (gamle fødselsnumre, med fasit) og MintHCM-dumpen. Bytter du tilbake til `main`, slettes begge fra disken. Gjenopprett med `py -3.13 src/kunstpixel/data/generate_time_for_time.py` og `git restore --source=7fc0d4f -- 01_inbox/raw/minthcm-minthcm-8a5edab282632443.txt`. Fellen forsvinner når `main` er flettet inn i `design/startbilde`.

Pakke 3 (2026-11-10):
- **R17.** Funn 1: `name` er fjernet fra `hr_people` og `seed.json`. `seed.json` har nå `ansatt_id`, og alle oppslag henter navnet fra `hr_ansatte` (`PERSON_SQL` i `core/hrdemo.py`). Svarfeltet heter fortsatt `name`, så MCP, API og CLI er uendret. `SKJEMAVERSJON` er 8.
- **R18. `museum.db` er ikke bygget på nytt.** `AGENTS.md` sier at bare Lars kjører bygget uten `--check`. Koden virker både på dagens og den nye databasen. `--check` sier ULIK, og `db_kvalitet` melder feil på skjemaversjon, til Lars har kjørt `py -3.13 src/kunstpixel/data/build_museum_db.py`.
- **R19 (rettelse).** Planen og gjennomgangen sa at funn 12 gjør at modellen nektes data, og at CV-er og personalmapper slipper gjennom etter rettingen. Det stemmer ikke. `check_policy` leser `klassifisering` satt av agenten, ikke kolonnen `datakilde`. `datakilde` styrer bare merkelappene i Arena og Vaktrom (`arena.datamerke`). Funn 12 endrer derfor ingen datatilgang i dag. Det får betydning først med funn 17.
- **R20 (Claude).** Funn 1, 12 og 10 er én commit, fordi funn 1 og 12 endrer samme byggefil. De gamle `startswith`-testene er beholdt, og en ny, strengere test sjekker alle tabeller med policyens egen funksjon.
- **R21 (Claude).** Leveransen `01_inbox/incoming/order_personalmapper_163` er ikke endret, fordi den har sjekksum. Flettes den inn på nytt, kommer det gamle formatet tilbake, og den nye testen feiler.
- **Åpent, ikke rettet:** rolle og ansettelsesform i `hr_people` stemmer heller ikke med `hr_ansatte`. E110 er `driftstekniker` i `hr_people`, men Kirsti Johansen er audioguide-produsent i registeret. E106 er `kafevert`, men Henrik Pettersen er vekter. Koblingen fra G10 ble satt uten å se på stillingene.

Testet: hele pytest 2240 bestått, 9 hoppet over, 2 ventede feil. Databasesjekken er grønn på et midlertidig bygg.

## 2026-11-15 — Lekegrind og demo av oppgaver (grilling-økt)

- **L1. Formål:** portefølje for Lars. Vises bare som live-demo på egen PC, ikke publisert offentlig. Personvern og risiko er ikke aktuelt (alt syntetisk).
- **L2. Motor:** Claude Code med MCP-serveren `kunstpixel` (`.mcp.json`).
- **L3. Ingen oppgavekatalog.** Lars stiller frie spørsmål i demoen (vanlige og spesielle, blant annet HR, drift, vakt, økonomi). Ingen YAML, tabell eller ferdige oppgavekort.
- **L4. Data følger `main`.** Ingen frosset demo-versjon. Fasit regnes alltid fra `museum.db` i øyeblikket.
- **L5. Én agent svarer,** ingen ruting-krav nå. Multiagent kommer senere.
- **L6. Rettekommando `/sjekk`** som prosjekt-skill i `.claude/skills/sjekk`, kjøres manuelt etter et svar.
- **L7. Kontrollør:** egen agentfil `.claude/agents/kontrollor.md`. Kun Read/Bash, åpner `museum.db` med `mode=ro`, får ikke MCP. Skriver egen SQL uten å se svaret først, og sammenligner etterpå.
- **L8. Visning:** kort dom per påstand (✅/❌), riktig verdi og SQL-en som viser det.
- **L9. Fritekst** (f.eks. svarutkast) vurderes av LLM-dommer med fri vurdering av tone og korrekthet.
- **L10. Start:** `start_claude.cmd` utvides med `db_status_gate.py --uten-pytest` og stopper ved rødt.

Bygget samme dag (gjenbruker `core/db.execute_read_query` og statusporten):
- `scripts/sql_ro.py`: kontrollørens eneste vei inn i databasen. `tests/test_sql_ro.py` (4 tester) var rød først og er grønn nå. Testene dekker blant annet DELETE, DROP, ATTACH, PRAGMA og to setninger etter hverandre.
- `.claude/agents/kontrollor.md` og `.claude/skills/sjekk/SKILL.md`.
- `start_claude.cmd` kjører `db_status_gate.py --uten-pytest` først. Testet grønn vei (`start_claude.cmd --version`: porten har 0 feil, og Claude starter). Ikke testet: rød vei.
- Testet ende til ende med instruksene i `kontrollor.md` (via en generell agent, fordi nye agentfiler lastes først i neste økt). Svaret hadde to plantede feil, og fase 2 fanget begge: datoen 12.11 (❌) og SAL-C (❌). «7,5 timer» ble merket ⚠️, fordi klokketiden er 8,0. Ikke testet: `/sjekk` kalt fra en ny økt, med verktøysperren til agenttypen.
- **L11. Korte svar, minst mulig støy (Lars, 2026-11-15).** Svar på dataspørsmål: 1–3 linjer, så `Kilde:` (ny `CLAUDE.md` i Kunstpixel). `/sjekk` viser bare tabellen Påstand/Dom/Riktig, `Bevis:`-SQL bare for ❌/⚠️, høyst én setning fritekst, og `Samlet:`. Fase 1 vises aldri.
- **L12. Etter kast-prototype (Lars, 2026-11-15).** `/sjekk` gir én linje når alt stemmer, ellers bare avvik med bevis (layout under «Output-oversikt» i `CLAUDE.md`). Kontrolløren kjører på Sonnet og gjør fasit og dom i ett kall, med svaret forseglet. Fritekst-dom kommer bare ved utkast eller råd. `CLAUDE.md` har fått egne regler for HR-feller.
  - Prototype (`.scratch/prototype-lekegrind`, 5 + 4 spørsmål med `claude -p`):
    - Alle svar var på 1–3 linjer pluss kilde.
    - Runde 1: begge HR-fellene lurte svaret, og `/sjekk` fanget begge.
    - Runde 2: navnelikheten gir nå et oppfølgingsspørsmål. Den tomme mappen (`KP-ANS-155`) lurer fortsatt svaret, fordi `get_personnel_dossier` krever en rolle, og agenten spør om rolle i stedet for å slå opp.
  - Tid: en tom `claude -p` brukte 136 sek, men bare 1,5 sek i API-et. Nesten all ventetid er altså oppstart (hooks og MCP), og den skjer én gang i en interaktiv økt. Selve `/sjekk` gikk fra omtrent 180 til omtrent 40 sek, og kostnaden fra 1,00 til 0,70 USD.
  - **Funn:** docstringen til `get_personnel_dossier` (`mcp_server.py:302`) nevnte 4 roller, men `AUTHORIZED_HR_ROLES` (`db.py:777`) har 7. Docstringen er rettet til 7, og tilgangen er uendret.
  - **Demo-rolle:** Lars spør som `museumsdirektor` (`CLAUDE.md`), så agenten slår opp direkte i stedet for å spørre om rolle.
- **Funn:** `05_data/index.md` stemmer ikke med databasen. JOIN-eksempelet bruker `fra_klokke`/`til_klokke`, men kolonnene heter `start`/`slutt`. ID-katalogen nevner `arkiv_hr_vakt_historikk` og `arkiv_hr_vakt_klokkeslett`, som ikke finnes i `museum.db`. **Rettet samme dag.** Alle fire JOIN-eksemplene hadde kolonner som ikke finnes, og er skrevet om og kjørt mot databasen. Rettet også: verktøynavn som ikke finnes (`get_employee_profile`, `check_shift_compliance`, `bemanning_sjekk`), og at `syntetisk_fnr` bare ligger i CSV. Radtallene (61 tabeller, 92 505 rader) stemte allerede.

## 2026-11-15 — Kart mot ren main (wayfinder-økt)

Kartet står i `docs/plans/2026-11-15-ren-main.md`.

- **W1. Målet er ren main.** Taggen `demo-v2` droppes. Demoen kjører fra `main` (L4), så en frosset versjon har ingen bruk.
- **W2. Ucommittet arbeid:** data og kode committes nå. `AGENTS.md` og `KUNNSKAPSKART.md` er skrevet om av en annen agent og går ikke inn før Lars har sett en sammenligning.
- **W3. `arkiv/drive_redning_2026-11-09`** beholdes på disk og legges i `.gitignore`.
- **W4. Push:** `main` pushes til GitHub når den er ren. Repoet er offentlig, og Lars valgte det med åpne øyne.
- **W5. `AGENTS.md` er slått sammen.** Den gamle fila står urørt (del 1–7), og multiagent-laget fra den nye er lagt til som del 8. Den nye manglet byggeregelen, testkravet, datapolicyen og kommandoene. `KUNNSKAPSKART.md` er den nye versjonen, med avviksnotatet fra den gamle beholdt som del 6. `handoffs/epost/README.md` er lagt i git.
- **Åpent:** `design/startbilde` er ikke avgjort. Lars vet ikke ennå hva grenen skal brukes til.

## 2026-11-15 — Helsesjekken måler MCP-dekning (etter loggjennomgang)

- **H1. `sjekk_kunnskapsgraf.py` måler nå hva demo-Claude når.** Den gamle målingen talte en tabell som dekket hvis navnet sto i en hvilken som helst fil i `src/`, og meldte «61 av 61, 0 blinde». Den nye (`tabeller_via_mcp`) følger kallene fra hvert `@mcp.tool` gjennom funksjoner og konstanter i `core/`. Resultat: 58 av 61. `dagsbesok`, `hr_medarbeidersamtaler` og `hr_innleide_kompetanse` er blinde for MCP (krav K2). Det gamle målet vises fortsatt som «Nevnt i src/». Tester: `tests/test_sjekk_kunnskapsgraf_mcp.py` (3), som var røde først. Hele pytest: 2257 bestått.
- **Funn i loggjennomgangen (ikke rettet):** `.scratch/bygger-fremdrift.md` (morgenagenten 2026-11-15 09:34) påstår at den har verifisert `check_shift_compliance`, `lookup_handbook_and_sops` og `cases/runner.py`. Ingen av dem finnes i koden. Den oppgir også 34 MCP-verktøy, men `core/mcp_server.py` har 56 `@mcp.tool`. Regel: påstander i agentlogger er ikke bevis før en kommando har kjørt og vist resultatet.


## 2026-11-16 — Datafinner alltid på via localhost

- **A1. Datafinner starter skjult ved pålogging** (Lars valgte «alltid på»). `scripts/autostart.ps1` lager snarvei i Windows-oppstarten (`scripts/start_bakgrunn.vbs` -> `start_demo.ps1 -Bakgrunn`) og bokmerke på skrivebordet til `http://127.0.0.1:8010`. Ingen tjeneste, ingen admin, ingen registerendring. Av: `autostart.ps1 -Fjern`.
- **A2. Samme sjekker som før.** Bakgrunnsstart kjører sjekksum, kvalitet og selvtest; feiler den, starter ikke serveren, og grunnen står i `.scratch/datafinner_bakgrunn.log`.
- **A3. Port 8010 opptatt:** er det Datafinner fra denne mappen (sjekkes på full sti i prosessens kommandolinje), åpner `start_demo` bare nettleseren. Annen prosess gir STOPP som før.
- **Ikke testet:** selve påloggingen (krever omstart). Skjult start via `.vbs`, «kjører allerede»-veien og et KI-spørsmål i nettleseren er kjørt og virket.
## 2026-11-16 — Datafinner etappe 1: navigasjon, opprydding og feil (plan: ~/.claude/plans/jeg-jeg-er-jeg-keen-tulip.md)

- **E1. Oppsett:** venstre = hovedting (Hjem, Finn data: Rapporter og Tabeller, Mer: Arena og Vaktrom), «Jeg er» nederst. Midten = brødsmuler med «← Tilbake» (ett nivå opp) og arbeidet. Høyre = ett huskelapp-kort (fasit) med én knapp «Spør KI om dette». Inspirert av mønsteret Lars viste, ikke kopiert. `af.css` er ikke endret.
- **E2. Hjem = KI-chatten** (`#flate:chat`), alltid først i meny og mobilvalg. Erstatter menypunktet «Spør om data».
- **E3. Adressen bærer tilstanden:** rapportvalg (`?dato=…`), åpen rad (`&rad=N`), vaktrom-steg (`flate:vaktrom/<steg>`) og Arena-oversikt (`#arena`). Nettleserens tilbake/frem virker.
- **E4. Rader kan åpnes:** første celle er en lenke til en detalj med alle felt (ikke bare 5 kolonner). «Vis alle N rader» over 50.
- **E5. Fjernet (Lars):** Søk, Arbeidsflyter og egen `/arena`-side med Grensemodus. `arena.html` flyttet til `arkiv/2026-11-datafinner-gamle-sider/`. Gamle adresser gir 302. `/api/arbeidsflyt` og `/api/grense/*` består.
- **E6. «Offisielle rapportmaler» rettet, ikke fjernet** (Lars): den eneste rapporten til Kvalitetsvokter. `SPORSMAL` har nå `parametre: ["mal_id"]`.
- **E7. Feil rettet:** hvitelisten for `get_cafe_menu_and_sales` og `search_visitor_reviews_and_satisfaction` hadde argumentnavn funksjonen ikke kjenner (vokter: `test_hvitelistens_argumenter_finnes_i_funksjonen`). «I dag» er lokal dato, ikke UTC.
- **E8. Kafé-blandingen** er synliggjort, ikke løst: tabeller viser stilling, stasjon og målgruppe først. Årsaken er data (vakter fordelt etter avdeling, håndbokens målgruppe per bok), etappe 4. Håndbokens rollefilter gir 0 treff for «Jeg er»-roller.
- **Utsatt:** Kontroll-avkrysningene fjernes i etappe 3 sammen med handlingslinjen («Godta» må finnes før de går).
- **Tester:** 13 nye (Playwright i `test_ledervalidering.py`, API i `test_datafinner.py`), alle røde først. Endret med vilje: menynavn, `/arbeidsflyt`- og `/arena`-adressene. Hele pytest: 2290 bestått, 9 hoppet over, 2 ventede feil.
- Committet på grenen `datafinner-ledelse` (7489e90), ikke på `main`.

## 2026-11-16 — Datafinner etappe 2: «I dag» (spec `docs/specs/datafinner-ledelse.md`)

- **I1. Testgrense (Lars):** dypere tester på enkeltfunksjoner. Utregning i rene funksjoner (`core/ledelse.py`, `datafinner/ledelse.js`), verktøyene i `core/driftsoversikt.py` henter bare rader. Én tynn Playwright-runde for kortet.
- **I2. Terskler ±15 % (Følg med) og ±30 % (Over terskel)** mot normalt, i `ledelse.TERSKLER`. Lars: dataene er simulert, så dette er et forslag som kan justeres. «Normalt» = snitt for samme ukedag de siste 4 åpne ukene (minst 2, ellers Ukjent).
- **I3. Fem statuser:** Normal, Følg med, Over terskel, Ukjent («Mangler data», aldri grønn) og Stengt (egen, ikke et fall i besøk). Vises med `af-signal` (ord + form), ikke `af-source`, som betyr kilde/merke (Bekreftet, Systemforslag …).
- **I4. D1, dagens tall:** besøk vises for siste hele åpne dag, aldri for i dag (de syntetiske tallene for hele dagen finnes allerede). «I dag» viser bare det planlagte: åpent/stengt, vakter per stasjon, arrangementer. En dato etter i dag avvises (400).
- **I5. Driftsmeldinger deles i to:** åpne siste 30 dager (15) og eldre åpne (198, helt tilbake til 2010). Et samlet «213 åpne» ville bare vært støy.
- **I6. «Tallet lenker til radene bak»:** radene følger med i svaret og åpnes under kortene med «Vis radene». Vakter har i tillegg «Åpne rapporten» (vaktplan for dagen, aktiv rolle eller første rolle som har den). Avvik fra spec B3, som foreslo en rapportadresse: det fantes ikke rapporter for alle tallene.
- **I7. Personvern:** svarene har bare summer per stasjon og kategori, aldri ansatt-ID eller navn. **Lars valgte «bare antall per kategori»:** driftsmeldinger på Hjem vises som kategori, antall og antall kritiske. Ingen emnetekst, dato eller mottaker. Vokter: `test_i_dag_lekker_ikke_ansatte_eller_persondata` og `test_i_dag_driftsmeldinger_er_bare_antall_per_kategori`.
- **I8. Uka (`get_week_overview`).** Tilfredshet, anmeldelser og kafé gir «Mangler data» når kilden ikke dekker hele perioden (de stopper 2026-10-29). Har uka ingen hele dager ennå (mandag), vises forrige uke med merknad.
- **I10. B5 «Driften denne uka» (Lars sa ja, bygger `museum.db` selv):** står først for Museumsdirektør, Driftsansvarlig og Kafeansvarlig (`rekkefolge` 0). Regel R-UKE-01: besøk ≥ −15 % mot forrige uke gir «på nivå». Ellers, eller hvis tallene mangler, brukes fallback med manuell sjekk. Samme grense som `ledelse.TERSKLER`. Rapporten viser dagene som tabell og resten under «Flere tall». Endret med vilje: rolle-rekkefølgen i `test_vakter_tools.py`.
- **I9. Etiketter med æøå** (Måned, Formål, År, Åpent …) fra én ordtabell i `ledelse.js`, brukt i alle tabeller.
- **Tester:** 68 nye (`test_ledelse.py` 38, `test_ledelse_js.py` 25, Playwright 5). De 66 første var røde først. XSS- og mobiltesten kom etterpå som vakter og var grønne med en gang. Hele pytest: 2361 bestått, 9 hoppet over, 2 ventede feil. Codex-review er ikke kjørt (MCP-tilkoblingen feilet). Kontrollfil: `.scratch/handoffs/CODEX-REVIEW-2026-11-16-etappe2.md`.

## 2026-11-16 — Datafinner etappe 3a: «Mine frister» (spec B6–B8, B10, F5–F6)

- **F1. Sykefravær (Lars, Å1):** frist = første fraværsdag + 4 uker (oppfølgingsplan) og + 7 uker (dialogmøte) for alle sykemeldinger. Dataene skiller ikke hel og delvis, så alle tas med («heller én påminnelse for mye»). Bare pågående fravær (`til` ≥ i dag) som varer til fristen. Egenmelding og permisjon tas ikke med. Fraværstype og årsak går aldri ut. Navn vises bare for HR og bemanning og Avdelingsleder.
- **F2. Rapportfrist (Lars, Å2):** siste dag i måneden. «Månedlig» gir siste dag i inneværende måned, «Kvartalsvis» siste dag i kvartalet, og en navngitt måned gir neste gang den måneden slutter. «Løpende» gir ingen frist. Rapporter vises for rollen som er `eier`.
- **F3. Åpne saker (Lars):** driftsmeldinger og HMS-avvik som har vært åpne i mer enn 14 dager. Driftsmeldinger vises for `mottaker_rolle`, og bare fra det siste året. Eldre saker telles i én linje, så listen ikke drukner (min antakelse, 198 gamle saker). Ingen emnetekst, bare kategori og ID.
- **F4. Forslag, ikke avklart med Lars:** tilstandskontroll = siste inspeksjon + 12 måneder. Innlån har frist ved utstillingens `periode_slutt` når status ikke er «Returnert». Begge vises for Samlingsforvalter og Kurator. Innlån vises også for Museumsdirektør, fordi Samlingsforvalter og Kurator ikke har rapporter og ikke kan velges i «Jeg er». Funn: tre innlån står som «Aktiv i utstilling» med sluttdato 2026-03-01.
- **F5. Grupper:** Forfalt, I dag, Denne uka (til og med søndag) og Senere (innen 60 dager). Frister regnes ut når siden lastes og lagres aldri.
- **F6. «Fulgt opp»** lagres bare i nettleseren (`kunstpixel.oppfolging.v1`). Siden virker uten lagring.
- **Funn:** ingen sykemeldinger i dataene varer 4 uker eller mer, så uke 4/7-regelen slår aldri ut på dagens data. Hører til datageneratoren (D2).

## 2026-11-17 — Datafinner: Hjem i to faner og etappe 3b (spec B9, F7–F9)

- **H1. Lite støy (Lars):** «Pass på støyen, poenget er å ikke få masse rot.» Regelen gjelder alt nytt: én eller to synlige knapper, resten under «Mer».
- **H2. Hjem i to faner (Lars valgte):** Oversikt (`#hjem`) og Chat (`#flate:chat`). Begge fanene har egen adresse, så tilbake og frem virker. Hjem åpner på Oversikt. Etappe 1-testene som forutsatte chatten på Hjem, er endret med vilje.
- **H3. Oversikt viser det som krever oppmerksomhet (min regel):** status Følg med, Over terskel eller Ukjent, eller et åpent driftsmeldings- eller HMS-tall over 0. Resten ligger under «Vis N andre tall». Der står det «andre tall», ikke «normale», fordi tall uten status ikke er vurdert.
- **H4. Full 3b (Lars valgte):** e-postutkast, «Meld avvik», «Godta» og «Mine oppfølginger».
- **H5. E-postmaler (B9)** ligger i `core/epostmaler.py`. `fyll_mal` feiler når en verdi mangler. Verdier settes inn i én omgang, uten linjeskift, og kuttes etter 300 tegn. Ingen mal spør om diagnose eller årsak. Utkastet lages på serveren:
  - Hver frist i `get_my_deadlines` får `epost`.
  - Hver rapport fra `lag_rapport` får `epost`.
  - Ingen ny hvitelisting. KI-chatten får derfor ikke nye verktøy.
  - Feltet heter `overskrift` (ikke `emne`), fordi vakttesten for frister forbyr ordet «emne».
- **H6. E-postutkast bare der malen kan fylles med fakta fra databasen** (frister og rapporter), ikke på rader og KI-svar. Dette er et avvik fra F7 i specen, og skal hindre støy og fritt oppdiktede e-poster.
- **H7. «Mine oppfølginger» (F9)** har egen nøkkel `kunstpixel.oppfolginger.v1` (en liste). «Fulgt opp» på frister (`kunstpixel.oppfolging.v1`) er urørt.
  - Typene er Følg opp, Avvik og Godkjent.
  - Samme åpne sak legges ikke inn to ganger.
  - CSV-filen bruker semikolon og BOM, og celler som starter med = + - @ får ' foran (CSV-injeksjon).
  - Huskelappen viser de 3 nyeste åpne når den er synlig.
- **H8. «Godta» (F8)** erstatter avkrysningene. Godkjenningen huskes per rapportadresse, det vil si rapport og valg, uten rad, og kan angres. Uten regel blir rapporten ikke «Bekreftet».
- **Tester:** hele pytest ga 2481 bestått, 9 hoppet over og 2 ventede feil. Datafinner er startet på nytt og sjekket i Chrome, uten konsollfeil.
- **H9. Arena er fjernet fra siden (Lars: «Fjern hele Arena»).** Grunnen var at casen T1 viste en rådump («Dette sier de interne dataene: AO-03 …»).
  - Menyen, adressene og visningen er fjernet.
  - Gamle `#arena…`-lenker går til Hjem, og `/arena` går til `/`.
  - Lars vil kanskje bruke casene til øving senere, så de skal ikke slettes. Kommer de tilbake, må svaret fra den interne assistenten vises ryddig (tabell), ikke som rådump.
  - Står igjen urørt: `core/arena.py`, `04_knowledge/07_arena/caser.yaml`, `/api/arena/*` og `tests/test_arena_caser.py`. Den interne assistenten (`core/intern/`) brukes også av `intern_hub`.
  - Hele pytest ga 2482 bestått.

## 2026-11-17 — Skillen `kunstpixel-data` sjekket mot databasen (oppgaver i `.scratch/kunstpixel-data-skill/issues/`)

- **S1. Tall-vakt:** `tests/test_skill_kunstpixel_data.py` sjekker hvert tall i skillen mot `museum.db`. Testen feiler hvis databasen bygges på nytt og skillen ikke følger med.
- **S2. «Ansatte uten vakter»** er 24 nåværende (46 med sluttede), etter D1.
- **S3. Offentlig og syntetisk** følger `arena.datamerke`:
  - 4 tabeller er offentlige: SSB, helligdager, Arbeidstilsynet og enhetsregisteret.
  - 31 tabeller er merket syntetisk.
  - 26 tabeller er umerket, fordi de ikke har kolonnen `datakilde`.
  - Påstanden «alle rader er syntetiske» er fjernet.
- **S4. «I år»** bruker `date('now','localtime','start of year')`, ikke `'2026-01-01'`.
- **S5. Kolonnen `timer` brukes alltid.** 83 vakter avviker fra slutt − start − 0,5, og 66 av dem er over døgnmaks. **Lars:** de 17 andre er feil og skal rettes i datageneratoren (D2, etappe 4).
- **S6. K2 er lagret i git (d85af4e) etter Lars' ja:** `get_daily_visitors`, `get_contractor_competencies` og `get_performance_reviews`. Alle er bare MCP-verktøy. Ingen av dem er hvitelistet i Datafinner.
- **S7. Medarbeidersamtaler er åpne uten rollesperre (Lars: «det skal være åpnet»).** Personalmappen har fortsatt sperre (CASE-016). Dataene er syntetiske. Blir det ekte data, må dette vurderes på nytt.

## 2026-11-16 — Datadefinisjoner (skill `kunstpixel-data`)

- **D1. «Ansatte» betyr nåværende** (`status <> 'Sluttet'`, 74 personer). Alle 168 bare ved «tidligere», «historisk» eller et tidligere årstall.
- **D2. «I år» og «2026» telles til og med i dag.** Dataene går til 2026-12-31. Det som ligger etter i dag, er plan og tas med bare når Lars spør om fremtiden.
- **D3. Nøkkeltall:** formlene for lønnskostnad, besøk, sykefravær og utstillingsøkonomi står i `.claude/skills/kunstpixel-data/references/metrics.md`. Alle 16 SQL-eksempler er kjørt. Lønnsformelen gir samme svar som `query_shift_cost` for 2026-10. Egen sykefraværsprosent regnes ikke: prosenten kommer bare fra SSB.
- **Funn:** `00_DATA_OG_MCP_OVERSIKT.md` sier at 26 ansatte står uten medarbeidersamtale. Databasen viser at 2 nåværende mangler samtale, og at ingen av de 94 som har sluttet, har noen. Ikke rettet.
- **Tester (3a):** `test_frister.py` (31), nye Node-tester for «Fulgt opp» (falsk og blokkert lagring) og 4 Playwright-tester (meny, Forfalt til Fulgt opp, som huskes etter omlasting, kortet på Hjem, «Spør KI»). Røde først, unntatt direktør-innlån-testen. Hele pytest: 2426 bestått, 9 hoppet over, 2 ventede feil.

## 2026-11-18 — Datafinner: lettere å bruke (U1–U7)

Lars ba om «løs frontend-problemene så det blir lett å bruke». Agenten gikk gjennom siden på PC og mobil og la funnene fram som valg. Lars valgte alle fire grupper og å skjule innlånsfristene.

- **U1. Hjelpetekst uten formatkode.** Datofeltet sier ikke lenger «ISO-format 'YYYY-MM-DD'», fordi datovelgeren viser formatet selv. Teksten kommer fortsatt fra verktøybeskrivelsen (som MCP bruker), og den er ikke endret. Siden fjerner bare formatet for dato- og månedsfelt (`Ledelse.hjelpTekst`).
- **U2. Fasit er lesbar.** Verktøyet vises som `get_week_overview(dato 2026-11-18)`, ikke som JSON. Regelen bruker samme etiketter som tabellene og ekte tegn: «Endring mot forrige uke (%) ≥ −15». Gjelder også «Vis grunnlag». Dette var åpent fra designkritikken 2026-11-09.
- **U3. Menyen blir stående** når du blar ned. «Mer» husker om den er åpen mens fanen er åpen. «Jeg er» viser hele rollenavnet.
- **U4. «Driften denne uka»:** dager som ikke har vært ennå, vises ikke som tomme rader, og en stengt dag viser «Stengt» i stedet for 0. Bare visningen er endret, ikke `get_week_overview`.
- **U5. Tabeller har søk** i tabellnavn og kolonnenavn. Søket skiller ikke mellom store og små bokstaver, ø og o, eller mellomrom og understrek, og det huskes i fanen.
- **U6. Innlånsfrister er skjult i Datafinner** (Lars). Regelen «retur når utstillingen slutter» er et forslag som ikke er bekreftet. `get_my_deadlines` og MCP har fortsatt fristene. Siden «Mine frister» sier hvor mange som er skjult. Fjern `innlan` fra `SKJULTE_FRISTER` i `ledelse.js` når regelen er bekreftet.
- **U7. «I dag»-kortet** har ikke lenger en tom plass til venstre når tallet ikke har farget status.
- **Tester:** 15 nye Node-tester og 7 nye Playwright-tester, alle røde først. To av Node-testene er ekte verktøytekster som ga feil svar ved første kjøring («Måned i formatet.»). Fire eksisterende fristtester brukte innlån og bruker nå driftsmeldinger (endret med vilje). Hele pytest: 2520 bestått, 9 hoppet over, 2 ventede feil, 0 feil. De to siste Node-testene kom til etter kjøringen og er grønne hver for seg.
- **Sjekket i nettleseren:** 1400 px, 900 px og mobil (375 px), ingen konsollfeil og ingen sidelengs rulling på mobil.
- **Ikke gjort:** uavhengig gjennomgang. Kontrollfilen ligger i `.scratch/handoffs/REVIEW-2026-11-18-brukervennlighet.md`.

## 2026-11-19 — Kunstpixel-demo i Claude-appen (C1–C7)

Lars ba om en guide for å ta med databasen inn i Claude og kjøre demoen i Claude-appen hvor som helst. Han spurte om databasen er ferdig nok. Statusporten sa KLAR (0 feil, 2 kjente varsler). Lars: hullene er greie «så lenge du finner de og kan resonnere i KI».

- **C1. Skill med databasen, ikke ekstern MCP-kobling.** Valgt av agenten etter Lars' svar over, fordi skillen virker uten server og uten at PC-en er på, og fordi KI-en kan finne hull selv med SQL. MCP-koblingen (offentlig server med innlogging) kan legges til senere.
- **C2. Pakken bygges fra repoet:** `scripts/lag_claude_skill.py` lager `.scratch/claude-app/kunstpixel-demo.zip` (gitignorert) med `museum.db`, `deploy/claude-app/SKILL.md`, `deploy/claude-app/sql.py` og referansene fra skillen `kunstpixel-data`. Bygget stopper over 30 MB ukomprimert (Anthropics grense for skills). I dag er pakken 23,5 MB ukomprimert og 3,2 MB som zip.
- **C3. `references/kjente-hull.md` regnes fra databasen ved hver bygging:** hvor langt hver tidsserie går, plan etter i dag, vakter over 9 timer, navnelikhet og fristregler som er forslag. Tre av punktene står som fast tekst: 83/17 vakter med avvikende timer, 7 hviletidsbrudd og `hr_people` mot `hr_ansatte`.
- **C4. SQL-skriptet er lesende med tre sperrer:** filen åpnes med `mode=ro&immutable=1`, bare én SELECT/WITH tas imot, og SQLite-autorisasjonen avviser alt annet enn lesing. Unntaket er `pragma_table_info` for `--kolonner`. Skriptet importerer ingenting fra repoet.
- **C5. Ingen rollesperrer i appen.** Claude leser alle tabeller, også personalmapper. Det er greit fordi dataene er syntetiske. Med ekte persondata må dette vurderes på nytt.
- **C6. «sjekk» i appen** gjøres av samme KI med nye SQL-spørringer. Det er ikke like uavhengig som `/sjekk` med egen kontrollør i Claude Code, og det står i SKILL.md.
- **Tester:** `tests/test_claude_skill.py` (15), røde først. To ble lagt til etter første kjøring (`--kolonner` ble avvist av sperren, og utskrift av æøå).  Hele pytest: 2537 bestått, 9 hoppet over, 2 ventede feil, 0 feil.
- **IKKE TESTET:** opplasting i claude.ai, og skillen på mobil. Anthropics hjelpeside nevner ikke mobil.
- Guide: `docs/GUIDE-claude-appen.md`.
- **C7. Lars spør i vanlig språk, og hullene står ikke som fasit** (Lars 2026-11-19: «jeg ville aldri spurt slik» om ID-spørsmål, og «du forstår formålet med repo her»). SKILL.md har to nye regler: finn ID-en selv ut fra navn, tittel, sal eller periode, og vis begge kildene når to tabeller er uenige. Nye hull funnet med SQL (`utstillinger` og `utstillinger_historikk` er uenige om hva som vises nå, og høstutstillingen har resultat før den er slutt) legges med vilje ikke i `kjente-hull.md`. Poenget med demoen er at KI-en oppdager slikt selv. Guiden har nå et prosjektsteg og demospørsmål i hverdagsspråk med fasit. Tester: 2 nye i `tests/test_claude_skill.py`, røde først, 17 bestått.

## 2026-11-19 — Storskjerm-dashbordet «Kunstpixel i dag» (D1–D8)

Lars vil «komme på jobb» som museumsdirektør og vise dagen på storskjerm, «så enkelt som mulig å hente fram og vise». Design: `docs/specs/2026-11-19-storskjerm-dashbord.md` (godkjent av Lars). Plan: `docs/plans/2026-11-19-storskjerm-dashbord.md`.

- **D1. Vanlig nettside (artifact), ikke Claudes Data-type eller Datafinner på nett.** Lars valgte etter fordeler og ulemper: én lenke, åpnes i fullskjerm uten sidepanel.
- **D2. Samme tall som Datafinner.** `src/kunstpixel/core/storskjerm.py` bruker `get_today_overview`, `get_week_overview` og `get_my_deadlines("Museumsdirektør")`.
- **D3. Oppdatering:** `py -3.13 scripts/lag_storskjerm.py`, så publiserer Claude Code til samme lenke. Lenke: https://claude.ai/artifact/SYi68yGa61mepG7aCyfpiY (privat, festet). **Erstattet av SC7:** lenken finnes ikke lenger.
- **D4. «I dag» er dagen skriptet kjøres.** Rader etter i dag telles ikke.
- **D5. Status som ord** (Normal, Følg med, Over terskel, Ukjent). Flater uten terskelregel (Åpne saker) viser sammenligning uten statusord.
- **D6. «Dette vet vi ikke»** regnes ved hver kjøring: tidsserier som slutter før i går, og utstillingstabeller som er uenige om hva som vises nå.
- **D7. Ingen navn, fraværsårsak eller e-postutkast** i dataene. Innlånsfrister skjules (U6). Sykefraværsfrister er ikke med (de hører til HR).
- **D8. Arbeidsflyt-utseende** (én lys palett, status som ord, ingen ikoner eller emoji). Storskjerm: minst 20 px tekst ved 1920×1080. Tekststørrelsen følger både bredde og høyde.
- **Valg tatt under byggingen** (fremdriftslogg `.scratch/handoffs/LEDGER-2026-11-19-storskjerm.md`): kurven viser 8 hele uker; fristfeltet viser 2 frister og «N til»; høyre kolonne er litt bredere; datahull grupperes per sluttdato.
- **Tester:** `tests/test_storskjerm.py` (20) og `tests/test_storskjerm_side.py` (24), røde først.

## 2026-11-22 — Regelbaserte rettinger i databasen (R1–R7, skjemaversjon 9)

Lars: «Unødvendige feil kan tas vekk», regelrettinger først, skjønn og LLM etterpå. Lars ba agenten velge de beste alternativene selv. Utført av tre underagenter med hver sine filer.

- **R1.** 17 korte Vaktrom-vakter hadde `timer` 9,0, men klokka ga 8,0 (sluttid stoppet på 23:30). Generatoren regner nå timer = slutt − start − 0,5 for forlengelser på høyst 9 t. De 66 lange vaktene er urørt (overtid eller feil er Lars' valg). Etter bygget avviker 66 vakter, ikke 83.
- **R2.** `hr_skills` er fjernet. `hr_person_skill` peker på `org_ferdigheter`, som har fått `kortnavn`. Kompetansekatalogen går fra 7 til 14 koder (ønsket). Svarfeltene er uendret.
- **R3.** `personas` har ikke lenger navn, avdeling og stilling. De hentes fra `hr_ansatte` med JOIN. Bygget stopper hvis `arkiv_cv_personas.json` er uenig med `hr_ansatte`.
- **R4 (tillegg, ikke erstatning).** `driftsmeldinger_epost`, `driftsmeldinger_tiltak`, `anmeldelser` og `hendelser` har fått `rolle_kode` med fremmednøkkel til `roller`. Oppslaget lages fra `roller.navn` (`05_data/rolle_kode_oppslag.csv`). De gamle rollekolonnene er urørt, fordi frister, I dag og storskjerm filtrerer på dem. Ukjent rolle stopper bygget.
- **R5 (agentens valg).** Kafésalg, tilfredshet og anmeldelser er forlenget fra 2026-10-29 til 2026-12-31, likt med dagsbesøk og vakter. Rader etter i dag er plan (D2). Kafeen har samme omsetning per besøkende som resten av 2026, ikke skalert til årstallet. Da blir hele 2026 −3,3 % mot `h5_historikk` (1 663 tkr mot 1 720 tkr).
- **R6.** Tre lange sykemeldinger lagt inn på nåværende ansatte uten vakter: KP-ANS-089 (2024, 5 uker), KP-ANS-010 (2026-08-03–09-27) og KP-ANS-025 (2026-10-02–12-03). Høyst én per kvartal, så avviket mot SSB holder seg under 1,5 prosentpoeng. Fristene uke 4 og uke 7 slår nå ut.
- **R7.** `00_DATA_OG_MCP_OVERSIKT.md` sier 2 nåværende uten medarbeidersamtale, ikke 26.
- **Ikke gjort:** R8 (navnebytte på rundt 80 filer).
- **Tester endret med vilje:** storskjerm- og ledelsestester som låste hullet 2026-10-29, følger nå sluttdatoen i databasen. Skilltallene (66 avvikende vakter, 25 umerkede tabeller) og kjente-hull-teksten i `lag_claude_skill.py` er oppdatert til det nye bygget.
- **Testet:** hele pytest mot et prøvebygg i kladdemappen. Alt grønt unntatt `test_start_gate`, som krever at `museum.db` er bygget på nytt. Statusporten: KLAR (0 feil, 2 varsler).
- **IKKE TESTET:** mot ekte `museum.db` etter Lars' bygg. Mot den gamle `museum.db` er skill-testene røde til bygget er kjørt.

## 2026-11-22 — Overtid, innlån og driftsregnskap (Lars' svar)

- **O1. Vakter over 9 timer er overtid (Lars).** `hr_vakter.overtid_timer` = max(0, timer − døgnmaks). Kostnaden har 40 % tillegg for de timene (AML § 10-6), som egne felt i `query_shift_cost` og `calculate_shift_cost`. Kvalitetssjekken gir FEIL hvis kolonnen ikke stemmer. Varselet om døgnmaks er borte, og statusporten har 1 varsel (hviletid).
- **O2 (agentens tolkning, ikke bekreftet).** Tillegget legges oppå helge- og helligdagssatsen. Satsen 0,40 står i `core/db.py`, ikke i `arbeidstid_grenser`.
- **O3.** Fasit i `caser.yaml` og `chat_eval.yaml` for juni 2026: vaktkostnad 778 083,81 kr og differanse 279 636,19 kr (før 776 898,74 og 280 821,26).
- **N1. Innlån returneres når utstillingen slutter (Lars).** Erstatter forslaget i F4 og skjulingen i U6 og D7. Fristene vises igjen i Datafinner og på storskjermen. LAN-2026-016, -033 og -050 sto som «Aktiv i utstilling» etter at utstillingen sluttet 2026-03-01, og får «Returnert» i bygget (`returner_innlan_etter_utstilling`). `museum_base.db` er ikke rørt.
- **Ø1. Driftsregnskap per måned (Lars valgte) er IKKE bygget.** Målingen stoppet det. Lønn regnet fra vaktene er rundt 10,1–10,5 mill. kr hvert år. Det er 174 % av `h5_historikk.kostnader_tkr` i 2010, og fortsatt 79 % i 2026. Vaktene tilsvarer rundt 14 årsverk hvert år, mens h5 sier 6,5–11,5. Billettinntekten i `dagsbesok` er 2,9–8,4 ganger tallet i h5. Lars må velge hvilken kilde som er fasit, før regnskapet kan lages.
- **B1. «Tall for barn» (Lars: barn som besøkende) finnes:** `dagsbesok.antall_barn` (439 221 i 2010–2026) og `h5_historikk.skoleelever`. Tallene nås via `get_daily_visitors`, men vises ikke på storskjermen eller i Datafinner.
- **Testet:** hele pytest mot prøvebygget. Alt grønt unntatt `test_start_gate`, som krever at Lars bygger. Statusporten: KLAR (0 feil, 1 varsel).
- **B2. `museum.db` bygget av Claude 2026-11-22 med Lars' tillatelse for denne ene gangen** (unntak fra AGENTS.md del 7). sha256 `0d6204d0d7b0…`, skjemaversjon 9, `driftsregnskap` 2 609 rader. Hele pytest er grønn mot den, og `db_kvalitet` gir 1 OBS (hviletid, med vilje). Ikke committet.

## 2026-11-22 — Driftsregnskap bygget, h5 regnet fra fasit (Ø1 løst)

- **Ø2. Vaktene og dagsdataene er fasit (Lars).** Ny generator `src/kunstpixel/data/regnskap_builder.py` skriver `05_data/driftsregnskap.csv` (13 kontoer etter NS 4102, 2010-01–2026-12, 2 609 rader). Bygget laster den i tabellen `driftsregnskap` (PK maaned, konto; CHECK på kontoene og beløp > 0) og stopper hvis filen mangler. Beløp 0 får ingen rad.
- **Ø3 (agentens valg, ikke bekreftet).** `kafe_varesalg` finnes bare for 2024–2026. For 2010–2023 er konto 3100 h5 `kafeinntekter_tkr` fordelt jevnt på 12 måneder, ikke 0. Varekjøp kafé (4000) er 35 % av 3100.
- **Ø4 (agentens valg, ikke bekreftet).** Frie nivåer (fast frø): husleie, strøm, vedlikehold, kontor/IT og forsikring. Lik sum hver måned i året og 3 % prisvekst. Strøm har sesong (høyest januar) og ganger 2,4 i 2022 og 1,7 i 2023. Innleie (6700) føres i måneden for `periode_fra` (alle oppdrag er innen én måned).
- **Ø5. h5 regnes i bygget** (`regn_h5_fra_fasit`, R21: h5-kilden og leveransene er urørt): `besok_totalt`, `billettinntekter_tkr`, `kafeinntekter_tkr`, `inntekter_totalt_tkr`, `kostnader_tkr`, `resultat_tkr` og `ansatte_arsverk` (vakttimer/1700). `betalende_besokende` og `snittpris_kr` er ikke regnet om og stemmer ikke lenger med billettinntekten. Resultatet er negativt 2010–2018 og 2020–2021 (2020: −5 162 tkr), fordi lønnen fra vaktene er ca. 10,2 mill. kr hvert år.
- **Kjent uenighet som står igjen:** h5-kilden (`h5_historikk_2010_2026.csv`, `governance/historikk_tall.yaml`, `leveranse._H`) har de gamle tallene, fordi den er låst med sjekksum (R21). Den interne assistenten (port 8001) leser `historikk_tall.yaml` for ledelsesroller og gir derfor de gamle tallene, og `hr_hms_pakke` bruker de gamle årsverkene (6,5–11,5). Lars må velge om kilden skal regnes om.
- **Ø6.** `publikum_builder` leser kafémålet fra h5-CSV-en, ikke fra `museum.db`, ellers ville den lest sitt eget resultat etter bygget. Utdataene er uendret.
- **Tester og fasiter endret med vilje:** K1 i `caser.yaml` (kildene er nå enige) og testen for K1, D4 (svakeste år −5162, var −420), skilltallet 32 syntetiske tabeller, kafétesten i `test_publikum_data.py` (målet fra h5-kilden), merknaden i `get_result_trend`.
- **Testet:** hele pytest mot et prøvebygg. Alt grønt unntatt `test_start_gate`. Statusporten: KLAR (0 feil, 1 varsel). **IKKE TESTET:** mot ekte `museum.db` etter Lars' bygg.

## 2026-11-22 — Storskjermen ryddet: oppsett A «Haster først» (A1–A4)

Lars syntes storskjermen var rotete. Tre prototyper ble vist (https://claude.ai/artifact/Fps3nRkzx6pNEt7CEzrGzM), og Lars valgte A.

- **A1. Fristene som haster står størst (Lars).** Venstre del av skjermen: antall forfalte som stort tall, og hver frist med hvor mange dager den har ligget. Feltet er rødt bare når noe er forfalt. Under står «Dette vet vi ikke».
- **A2. Kravene fra D1–D8 står (Lars).** Hvert tall har fortsatt kildelinje, og «Dette vet vi ikke» og utstillingsøkonomien er fortsatt egne felt. Prototypen tok dem ut. Det ble ikke gjort.
- **A3 (agentens valg).** De fire nøkkeltallene er rader i ett felt, ikke fire fliser. Kilden står på samme linje som tittelen i feltene, og på samme linje som sammenligningen i radene. Fristfeltet viser 3 frister og «N til» (var 2). Endringen gjelder bare `deploy/claude-app/storskjerm.html`. `core/storskjerm.py` og `data.json` er urørt.
- **A4. Feil som ble rettet samtidig.** Etter N1 (innlånsfrister vises igjen) fløt fristfeltet over i det gamle oppsettet. Fire sidetester var røde før endringen.
- **Tester:** to nye i `tests/test_storskjerm_side.py`, røde først. `test_storskjerm_side.py` og `test_storskjerm.py`: 49 bestått. Sett på skjermbilde i 1920×1080 og 400 px.
- **IKKE GJORT:** ikke publisert til lenken, ikke committet. KI-chat-testkopien (https://claude.ai/artifact/4Gp2AweTDj9m54E6ZDxiL9) har ingen kildefil i repoet og har fortsatt det gamle oppsettet. Hele pytest er ikke kjørt.
- **Erstattet samme dag av SC1–SC6.** Lars valgte A før han hadde sett prototypene. Da han så dem, valgte han C. Oppsett A ble aldri publisert eller committet.

## 2026-11-22 — Storskjermen: oppsett C «Én ting om gangen» med underlag (SC1–SC7)

Erstatter A1–A3. Lars: «Én ting om gangen er mye bedre», og han vil ha et underlag så man kan fordype seg. Lenke: se SC7.

- **SC1. Én stor flate om gangen (Lars).** Toppen og de fire nøkkeltallene står fast. Under vises én flate: Besøk, Frister, Utstillinger eller Vet ikke. Dette endrer målet i specen fra 19.11 om at alt vises samtidig på én skjerm. Det er fortsatt ingen rulling på storskjerm.
- **SC2. Underlag (Lars).** «Vis underlaget» bytter flaten til radene bak: besøk per uke med endring i prosent, alle frister, utstillingene med ID og full tittel, og tabellene som slutter før i dag. Underlaget bruker bare det som alt står i `data.json`. `core/storskjerm.py` er urørt.
- **SC3 (agentens valg).** Flaten bytter selv hvert 12. sekund. Byttingen kan stoppes med en knapp, står stille mens underlaget er åpent, og er av når maskinen ber om mindre bevegelse.
- **SC4 (agentens valg).** Et trykk på et nøkkeltall hopper til flaten: Besøk og Besøk denne uka til Besøk, Åpne saker til Frister, Tilfredshet til Vet ikke.
- **SC5. Kravene fra D1–D8 står ellers.** Kildelinje på hvert tall og hver flate, status som ord, Ukjent i stedet for 0, minst 20 px tekst, ingen navn i fristene. Fristflaten viser 4 frister og «N til», resten står i underlaget.
- **SC6. Feil som ble rettet samtidig.** Etter N1 (innlånsfrister vises igjen) fløt fristfeltet over i oppsettet fra 19.11. Fire sidetester var røde før endringen.
- **Tester endret med vilje:** `test_fristfeltet_har_luft_nederst` er erstattet av `test_hver_flate_far_plass`, som sjekker hver flate og hvert underlag i tre skjermstørrelser. Nye tester for faner, underlag, hopp fra tall og automatisk bytting. Testene ble skrevet sammen med malen, ikke røde først. `test_storskjerm_side.py` og `test_storskjerm.py`: 61 bestått. Sett på skjermbilder i 1920×1080.
- **SC7. Ny lenke (Lars).** Den gamle lenken (SYi68…) ga «finnes ikke» da den skulle oppdateres. Den festede siden i claude.ai var nå KI-chat-testkopien. Lars valgte en ny egen lenke framfor å skrive over den: https://claude.ai/artifact/PHo2wkd94Pmgo1qr1PzKXw (privat, festet i claude.ai etter Lars' ja). Publisert med tall fra `museum.db` bygget 2026-11-22 kl. 15:07 (B2). Storskjermtestene: 61 bestått mot den.
- **IKKE GJORT:** ikke committet, hele pytest ikke kjørt, ikke sett på den fysiske storskjermen. Specen `docs/specs/2026-11-19-storskjerm-dashbord.md` er ikke skrevet om.

## 2026-11-22 — KI-chat og Drift og HR inn i storskjermen (SC8–SC12)

Lars: «Chatten må jo være der.» Chatten og Drift og HR fantes bare i artifacten «Kunstpixel KI-chat test» (4Gp2…), uten kildefil i repoet. Derfor forsvant de da storskjermen ble bygget fra repoet. Designet er det Lars godkjente 19.11 i `docs/specs/2026-11-19-storskjerm-chat.md` (skuff fra høyre, hele databasen med SQL, alle data med fordi de er syntetiske).

- **SC8. Chatten ligger nå i repoet.** Begge skuffene står i `deploy/claude-app/storskjerm.html`. `scripts/lag_storskjerm.py` skriver i tillegg `museum.db.gz.txt` og `chat-instruks.txt`, så «oppdater dashbordet» tar med alt og chatten får samme database som tallene. Artifacten erklærer `sample`.
- **SC9. Instruksen bygges fra skillen.** Den settes sammen av `deploy/claude-app/SKILL.md` (fra «Definisjoner»), `kjente_hull()` fra `lag_claude_skill.py`, `metrics.md`, `entities.md` og alle tabeller med kolonner. Maskinens dato byttes med datoen i `data.json`. Den ble sammenlignet med instruksen i 4Gp2: den er lik bortsett fra dato, nye hull og nye regler for overtid og økonomi.
- **SC10. Rettet en selvmotsigelse i instruksen.** Den gamle linjen sa «Bruk alltid '2026-11-19'» og så «Bruk ALDRI '2026-11-19'». Nå står det «aldri maskinens dato (now, localtime eller CURRENT_DATE)». Test passer på det.
- **SC11 (agentens valg).** Databasen lastes først når en skuff åpnes, ikke når siden åpnes (slik specen sier). KI-chat-knappen vises bare når claude.ai lar siden spørre Claude med verktøy, og skjules hvis Lars sier nei. Drift og HR vises alltid. TESTVERSJON-merket er tatt bort.
- **SC12. Drift og HR følger datoen i dataene.** SQL-en hadde `'2026-11-19'` skrevet fast. Nå brukes datoen i `data.json`, så skjermen, chatten og rapportene regner «i år» likt.
- **Tester:** ny `tests/test_storskjerm_chat.py` (22), røde først: databasen pakkes ut til samme bytes, instruksen (dato, ingen `date('now'`, regler, alle tabeller), knappene med og uten Claude, skuffen åpnes og lukkes, ingen lasting før skuffen åpnes, SQL avviser `DELETE` og to setninger, `DIAGRAM:` tegnes og tåler HTML, Drift og HR bruker datoen. Claude er falsk i testene, men SQL kjører ekte i sql.js. Ny test sjekker også at skjermen får plass med begge knappene i toppen (1920×1080, 1280×720, 1568×700). Storskjermtestene: 86 bestått. Hele pytest: grønn (9 hoppet over, 2 ventede feil). Publiseringen er sjekket: alle fire filene ligger i artifacten med riktig størrelse.
- **Publisert** til samme lenke, https://claude.ai/artifact/PHo2wkd94Pmgo1qr1PzKXw, med `sample` og alle fire filene.
- **SC13. Chatten står fast ved siden av dashbordet (Lars).** Lars: «fiks at chat og dashboard kommer samlet». Han valgte «chat alltid synlig» framfor side om side ved åpning og chat som femte fane. Det erstatter skuffen fra 20.11 for KI-chat. I claude.ai er chatten en kolonne til høyre (30 % av bredden, minst 20rem) hele tiden, og KI-chat-knappen er borte. Uten Claude, eller hvis Lars sier nei til tillatelsen, får dashbordet hele skjermen. På mobil står chatten under dashbordet. Drift og HR er fortsatt en skuff. Databasen lastes først når noen klikker i tekstfeltet eller på et forslag. Tester omskrevet med vilje: plass-testen med chat i tre skjermstørrelser, uten Claude og på mobil. Storskjermtestene: 85 bestått. Publisert som versjon 3.
- **IKKE TESTET:** ekte svar fra Claude i claude.ai, tillatelsesdialogen og om claude.ai slipper gjennom sql.js fra cdnjs. Det kan bare Lars prøve. 4Gp2 er tatt ut av Festet etter Lars' ja, men er ikke slettet.

## 2026-11-22 — Storskjermen for seks lederroller (SC14–SC20)

Lars: «Du lager det som er best. Støy og stygge ting skal vekk. Det skal være relevant for ulike lederroller.» Han ga agenten mandat til å velge. Valgene under er agentens, innenfor det mandatet.

- **SC14. Seks roller med rollevalg i toppen.** Rollene er Direktør, Drift og HMS, HR og bemanning, Økonomi, Publikum og kafé, og Samling og utstilling. De følger `roller`-tabellen og fristreglene i `frister.py`. Avdelingsleder er ikke en egen rolle, fordi den krever valg av avdeling, men fristene ligger under HR. Lenken kan åpne en rolle direkte (`#hr`, `#okonomi` osv.). Et tall på rollen i toppen viser hvor mange av rollens tall som er Følg med eller Over terskel.
- **SC15. Alle tall regnes i Python.** Ny modul `src/kunstpixel/core/storskjerm_roller.py` lager `data.json["roller"]`. Hver rolle har 3–4 tall og 3–5 flater, hver med underlag. Siden tegner alle roller med samme mal. De gamle nøklene i `data.json` er beholdt for testene i `test_storskjerm.py`. Siden bruker dem ikke.
- **SC16. Hvert tall har sammenligning, retning og status.** Sammenligningen er samme uke eller periode i fjor, eller for en uke siden for beholdninger som åpne meldinger og forfalte frister. Statusregelen er Normal ved høyst 10 % verre, Følg med ved 10–25 % verre og Over terskel ved mer enn 25 % verre. Små tall får en minste forskjell før alarm (overtid 5 timer, HMS-avvik og lave anmeldelser 2, nye meldinger 3). Pilen er grønn når endringen er bra og rød når den er dårlig.
- **SC17. Kurve i hvert tall.** Kurven viser de siste 8 ukene (eller månedene, eller årene for utstillinger). En uke uten tall er et hull, ikke 0. Slutter kilden før siste hele uke, viser tallet den siste uka med tall, og navnet sier hvilken uke (for eksempel «HMS-avvik uke 45»).
- **SC18. Støy tatt bort (agentens valg, endrer D-kravet om kildelinje under hvert tall).** Kilden står ikke lenger under hvert tall. Den vises når musen holdes over tallet, én gang per flate og i underlaget. «Normal» vises ikke som pille, fordi pilen og fargen sier det. Pillen vises bare for Følg med, Over terskel og Ukjent. Tatt bort: «gjelder 21.11», «198 eldre», «snitt vektet etter antall svar», «Svar hentes med SQL fra museum.db», ukedagen i toppen og «Ingen senere». Millioner vises som «17,2 mill. kr» på tallene, og eksakt beløp står i underlaget. «Dette vet vi ikke» bruker vanlige ord i stedet for tabellnavn.
- **SC19. Drift og HR-skuffen er fjernet.** Innholdet er flyttet inn i rollene: fravær per avdeling, overtid og innleie under HR, og fristene under hver rolle. Toppen er én linje.
- **SC20. Chatten følger rollen.** Hver rolle har fire egne forslag, uten spørsmål om enkeltpersoner. Hvert spørsmål sendes med «[Rolle: …]» foran, og instruksen sier at rollen går foran «museumsdirektør».
- **Personvern (D7):** sykefraværsfrister vises som «Oppfølgingsplan sykefravær (uke 4)» med ansatt-ID. Navnet fra `frister.py` tas bort. En test sjekker at ingen navn fra `hr_ansatte` står noe sted i rolledataene.
- **Tester:** ny `tests/test_storskjerm_roller.py` (23), skrevet rød først, med SQL-kontroll av besøk, resultat, sykefraværsdager og overtid. `test_storskjerm_side.py` er skrevet om med vilje for rollene (alle roller, flater og underlag i tre skjermstørrelser, 20 px-regelen for hver rolle, HTML i data vises som tekst). `test_storskjerm_chat.py`: Drift og HR-testen er erstattet av tester for rolleforslag og rolle i spørsmålet. Storskjermtestene: 95 bestått. Sett på skjermbilde for alle seks roller i 1920×1080 med chatten.
- **Rettet etter egen gjennomgang:** «Åpne driftsmeldinger» og «Åpne meldinger om klima» viste 0,0 % endring bare fordi driftsmeldingene slutter 14.11. Nå gjelder tallet kildens siste dag, navnet sier «per 14.11», og sammenligningen er uka før den datoen. Ny test, rød først. Chatteksten var under 20 px på storskjerm (forslag, knapper under svaret, SQL). Den er hevet, og en ny test sjekker hele chatten.
- **Publisert** som versjon 5 til https://claude.ai/artifact/PHo2wkd94Pmgo1qr1PzKXw. Storskjermtestene: 98 bestått. Hele pytest: grønn (9 hoppet over, 2 ventede feil), kjørt før de siste rettingene.
- **IKKE TESTET:** ekte svar fra Claude i claude.ai, og visningen på den fysiske storskjermen. Statusgrensene (10 og 25 %) og de minste forskjellene er agentens valg og er ikke bekreftet av Lars.
- **SC21. Ny gjeldende lenke (Lars: «lag nytt artifact som gjeldende»).** Rolleutgaven er publisert som en ny artifact: https://claude.ai/artifact/59CjTmfETMo6evyza8Cbfx (privat, festet som «Kunstpixel i dag»). PHo2… er tatt ut av Festet og er ikke slettet. Den har versjonene fra i dag (oppsett C, chat og roller). «Oppdater dashbordet» publiserer heretter til den nye lenken. Lenken er byttet i PLAN og guiden.

## 2026-11-22 — Bygget: bilder, plantegninger og PDF (B1–B6)

Lars ba om bilder og tegninger av museet samlet i en PDF med beskrivelser, og en vurdering av om det trengs flere. Gjennomgangen fant det gamle museumsnavnet i åtte bilder og to versjoner av bygget. Lars: «Rett opp det som trengs. Navnet skal vekk, og det andre.»

- **B1. Kartdataene er fasit for bygget (agentens valg, etter Lars' «rett opp»).** Gjelder `06_kart/bygning_geometri.json`: hovedfløy fra 1912 og glassfløy fra 2016. Kartet, plantegningene, `get_building_map_data` og tabellen `saler` i `museum.db` bruker allerede denne. `04_knowledge/04_domain/core/bygning_og_etasjeplaner.md` beskrev et bygg fra 1980 med andre arealer (Sal A 95 m², kafé 65 m²), og den er skrevet om etter kartdataene. Personkapasiteten per sal er beholdt fra HMS-håndboka.
- **B2. Navnet er fjernet fra bildene (Lars, DECISIONS 10).** Det gjelder skilt, disker og fasader i 8 bilder pluss en dublett. `scripts/fjern_navn_i_bilder.py` leser originalene fra commit 1c4d9a4, maler over bokstavene (OpenCV-inpainting) og skriver «KUNSTPIXEL» der det sto et skilt. Kafédisken og logoen på resepsjonsdisken står blanke. Den rotete KI-teksten på de samme skiltene er også rettet («VELAONHEN» → «VELKOMMEN», «ERSISTENS» → «EKSISTENS»). Filnavnene er beholdt. Originalene ligger i git og kan hentes tilbake.
- **B3. Kafeen ligger i glassfløyen mot Nidelva (agentens valg).** KAF-1 og BUT-1 har byttet plass i plan P1 (kafé i øst, bokhandel i vest), slik at planen stemmer med bildet og teksten «glassvegg mot Nidelva». Kafeen har 45 sitteplasser som i HMS-håndboka og kvalitetssystemet (var 60 i kartet). Kartet og plantegningene er bygget på nytt med `06_kart/build_map.py`.
- **B4. PDF.** `02_deliverables/bygningsdokumentasjon/kunstpixel_bygning.pdf` (9 sider) lages med `lag_pdf.py` i samme mappe: Edge uten vindu, ingen nye pakker. Den inneholder alle tall fra kartdataene, alle 12 ulike bildene og de 3 plantegningene, og ender med en vurdering av hva som mangler.
- **B5. Løst samme dag, se G1–G8.** Fotavtrykket på tegningene er 48 × 24 m = 1 152 m², mens BYA og BTA per etasje er 1 450 m². De tegnede rommene dekker 688 av 1 300 m² i U1, 1 009 av 1 310 m² i P1 og 817 av 1 310 m² i P2. Ganger, toaletter, garderober og kontorer er ikke tegnet. Testene i `test_building_map.py` låser 19 rom og arealtallene, så en retting endrer datamodellen.
- **B6. Andre avvik som står igjen.** Glassfløyen står på ulik side i de to fasadebildene. Skulpturhage-bildet viser et annet teglbygg. HMS-håndboka bruker andre navn på Sal A, B og C enn kartet og databasen. To bilder er dubletter (testen krever alle 14 filene).
- **Tester:** nye `tests/test_bilder_uten_gammelt_navn.py` (SHA-256 for de 8 gamle bildene) og `tests/test_bygning_konsistens.py` (kafeens side, sitteplasser og kunnskapsfila mot kartdataene). Begge ble kjørt røde først. Kart-, navne-, MCP- og nye tester: grønne. I hele pytest feiler 8 tester (arenacaser, chat-eval U2, to skill-tester og start-gate). De feilet før denne endringen, og de venter på at `museum.db` bygges på nytt (se PLAN).
- **Sett i nettleseren:** `06_kart/index.html` via ny oppstart «kart» i `.claude/launch.json` (port 8766). P1 i røntgenvisning har kafeen i øst ved Sal E. Alle 9 galleribildene lastes, og konsollen har ingen feil. De 6 grafene i `assets/` har ikke det gamle navnet. Skjermbildene i `02_deliverables/arbeidsflyt/designsjekk-2026-10-20/` er historikk og er ikke sjekket eller endret.
- **IKKE GJORT:** ikke committet eller pushet. En Datafinner- eller MCP-server som kjører, husker den gamle byggmodellen (`lru_cache`) til den startes på nytt.

## 2026-11-22 — Nye plantegninger som henger sammen (G1–G8)

Spec: `docs/specs/2026-11-22-bygg-tegninger-design.md`. Plan: `docs/plans/2026-11-22-bygg-tegninger.md`. Lars: «Rett opp og lag nye tegninger som gjør at det henger sammen.»

- **G1. To bygningskropper, samme BTA og BYA (Lars valgte A).** Hovedfløyen er 34 × 25 m (1912, tegl 400 mm) og glassfløyen 24 × 25 m (2016, glass/betong 300 mm). Til sammen er det 58 × 25 m = 1 450 m² per etasje. Fotavtrykket står i `museum.fotavtrykk` i `bygning_geometri.json`.
- **G2. BRA regnes fra tegningen (Lars).** BRA er 1 391,4 m² per etasje og 4 174,2 m² totalt (var 3 920). Det er BTA minus ytterveggene. Den gamle østfasaden mellom fløyene er en innervegg og regnes med. BTA 4 350 og BYA 1 450 står.
- **G3. Tegninger først, maskinpark senere (Lars).** I U1 er det satt av et reserveareal på 177 m² (MASK-RES-1) ved klimasentralen og vareheisen. Øvingsdager er ikke planlagt ennå.
- **G4. Romoppsettet (agentens valg innenfor specen).** 45 rom: 16 i P1, 15 i P2 og 14 i U1. De fyller hver etasje uten overlapp. Sal A–E har samme areal. Nye rom er ganger, toaletter og garderobe, kafékjøkken, kunstsluse, administrasjon, kontorer, magasin 2/papirarkiv, verksted, renhold, kjøresluse og lager.
- **G5. Trapper og heiser (agentens valg).** Hovedtrappen går gjennom alle etasjer og er låst for publikum i U1. Rømningstrapp 2 og vareheisen står i glassfløyen og går gjennom alle etasjer. Publikumsheisen går mellom P1 og P2. Testen sjekker at hver sjakt står på samme sted.
- **G6. Avvik fra specen (agentens valg).**
  - Vaktrommet er flyttet til hovedfløyen i P2 og er nå 120 m² (var 140).
  - Hovedtrappene er 26,4 m² (var 25).
  - Gangen i hovedfløyen er 2,2 m bred (specen sa ca. 2,5).
  
  Arealene gikk ikke opp ellers.
- **G7. Tegnes fra data.** `06_kart/geometri.py` regner arealene og sjekker reglene. `build_map.py` tegner vegger, mållinjer, tegningshode og 2.5D-kart fra fotavtrykket, og ingen byggmål står fast i koden. Nye felt i JSON: `type`, `sjakt` og `dor_langs` (valgfri dørplassering).
- **G8. Tester endret med vilje.** `test_building_map.py` låste 19 rom, BRA 3 920 og faste veggkoordinater. Nå er det minst 19 rom, BRA fra tegningen og vegger fra fotavtrykket. Ny `tests/test_bygning_geometri.py` (18 tester) ble kjørt rød først, bortsett fra `test_romtitler_far_plass_i_rommet`, som ble skrevet etter rettingen. `test_bygning_konsistens.py` er oppdatert for BRA og vaktrommet. Kartet er sett i nettleseren: røntgen, skall, rotasjon og konsoll uten feil.
- **G9. Rettet etter uavhengig gjennomgang.**
  - **Dører inn i heissjakt:** To dører gikk inn i heissjakta. LAG-P1 går nå til vestibylen, og WC-P2 er blitt SIK-P2, et teknisk rom for sikkerhetsanlegg som nås fra vaktrommet. `geometri.dorfeil()` stopper slike feil.
  - **PDF:** Tegningene ble kuttet nederst.
  - **2.5D-kartet:** Smale rom viser bare romnummer. Skallet følger rotasjonen.
  - **Rømningstrapp 2 (agentens valg):** Trappen har ingen yttervegg. Den leder via gangen i glassfløyen til en nødutgang i øst mot elvepromenaden.
  - **Små funn som står igjen:** står i loggen `.superpowers/sdd/2026-11-22-bygg-tegninger/progress.md`.
- **Tester:** hele pytest er grønn, uten feil.
- **IKKE GJORT:** ikke committet. En Datafinner- eller MCP-server som kjører, må startes på nytt for å vise den nye modellen.

## 2026-11-22 — Maskinpark: KI i drift (MP1–MP8)

Lars: «Kjør, lag fullstendig maskinpark» med ting som kan styres og vedlikeholdes via KI, og en agentinstruks for det. Lars hoppet over spørsmålene, så valgene under er agentens med mindre annet står.

- **MP1. Agentinstruks.** Skillen `.claude/skills/maskinpark/SKILL.md` er laget etter `instruks-for-agenter`. Den inneholder kontekstpekere, en deterministisk indre sløyfe, sperrene SEC-M1–M7 og fem ferdig-kriterier (PASS/FAIL).
- **MP2. KI-en foreslår, mennesket godkjenner (agentens valg).** MCP-serveren er fortsatt skrivebeskyttet. `propose_machine_command` gir «venter_godkjenning» eller «avvist» og endrer ingenting. Driftsansvarlig godkjenner alltid. Sikkerhetsansvarlig godkjenner i tillegg for kritikalitet A og sikkerhetsutstyr. En egen styringsdel som faktisk sender kommandoer er ikke bygget.
- **MP3. Data ved siden av bygget, ikke i museum.db (agentens valg).** `06_kart/maskinpark.json` lages av `06_kart/maskinpark_builder.py` med fast frø, og to kjøringer gir lik fil. Samme mønster som `bygning_geometri.json`. `museum.db` trenger ikke bygges på nytt.
- **MP4. Innhold:**
  - 37 maskiner: 8 KI-servere, 8 roboter (4 renhold, 2 vakt, 2 kunsttransport), 12 anlegg (ventilasjon, befukter, kjøling, klima i magasinene og Sal D, lys i Sal A–E, lading), 7 sikkerhet (Inergen, adgang, CCTV, brannsentral) og 2 heiser.
  - 100 hendelser over 90 dager, 257 arbeidsordrer og 8 kommandoer i loggen.
  - Fire åpne scenarier til øvingsdager: RF-avvik i Magasin 1, GPU-node som går varm, renholdsrobot som står fast, og lavt Inergen-trykk.
- **MP5. Sperrer:**
  - Forbudt uansett: deaktivere slukking, låse opp dører, slå av kamera, alarm eller adgang, overstyre heis.
  - Klima og lys må ligge innenfor rommets klimasone.
  - Kunsttransport bare 17–10, og to personer ved S4.
  - Renholds- og vaktroboter kjører ikke inn i S4.
  - Sikkerhetsutstyr er bare lesbart for KI. Bare selvtest kan foreslås.
- **MP6. Rom:** Reservearealet i U1 er delt i KI-serverrom SRV-1 (90 m²) og robotgarasje ROB-1 (87 m²). Romtypen er `maskin`. Tegningene er bygget på nytt, og BRA er uendret.
- **MP7. MCP:** Fire nye verktøy (`get_machine_park`, `get_machine_health`, `get_maintenance_plan`, `propose_machine_command`). De er bare MCP og er ikke hvitelistet i Datafinner-chatten. De er dokumentert i `AGENTS.md` og `00_DATA_OG_MCP_OVERSIKT.md`.
- **MP8. Tester:** Ny `tests/test_maskinpark.py` (25 tester) ble kjørt rød først. Hele pytest er grønn. PDF-en har fått to sider om maskinparken (nå 11 sider).
- **IKKE GJORT:**
  - ikke committet,
  - ingen uavhengig gjennomgang av maskinparken,
  - ikke noe eget maskinlag i 2.5D-kartet,
  - ikke hvitelistet i Datafinner.
  
  En MCP-server som kjører, må startes på nytt for å se verktøyene.

## 2026-11-22 — Maskinlag, øvingsscenarier, fasader og snitt (MP9–MP12)

Lars: «ja gjør dette» om punktene i PLAN (maskinlag, øvingsdager, nye bilder, fasade- og snittegninger).

- **MP9. Maskinlag i 2.5D-kartet.** Ny knapp «Maskiner» ved siden av sikrings- og klimasonene. Rommene får fargen til den verste maskinstatusen i rommet: grønn i drift, gul varsel, rød feil, blå vedlikehold. Rom uten maskiner tones ned. Rommets skuff viser maskinene og åpne hendelser. Dataene er `maskinpark.json`, bakt inn i `index.html`. Sett i nettleseren, og konsollen har ingen feil.
- **MP10. Øvingsdager (agentens valg).** Seks scenarier ligger i `maskinpark.json` (KP-OV-01–06): fukt i magasinet, varm GPU, fastkjørt robot, lavt Inergen-trykk, kunsttransport og lys på papirverk. Hvert scenario har et riktig forslag (gir «venter_godkjenning») og en felle (gir «avvist»). Testen kjører begge mot regelsjekken, så fasiten kan ikke gli. Nytt MCP-verktøy: `get_drill_scenarios`.
- **MP11. Fasader og snitt (agentens valg).** `06_kart/fasader.py` tegner fasade sør og øst og snitt A–A (hovedfløyen) og B–B (glassfløyen) fra modellen. Bredder kommer fra fotavtrykket, høyder fra kotene, og snittene viser rommene linja krysser. Nye felt: `tak_topp_moh` (mansard 28,40 / flatt 24,90) og `takform`. Tegningene lages med `build_map.py` og står i PDF-en (nå 13 sider).
- **MP12. Nye bilder av Sal B, C og E og driftsrommene er ikke laget.** De krever en ekstern bildetjeneste, og det må Lars si ja til først.
- **Tester:** nye `tests/test_fasader_snitt.py` (13). `test_maskinpark.py` er utvidet med maskinlag og scenarier. Alle ble kjørt røde først.

## 2026-11-23 — Kunstroboter og produktark (MP13–MP14)

Lars valgte begge anbefalingene: produktark generert fra dataene, og kunstrobotene lagt inn i maskinparken.

- **MP13. Kunstroboter.** Tre nye maskiner står sist i `MASKINER`, så de eldre maskinenes data er uendret: `KP-MASK-HNG-01` (hengerobot, type `hengerobot`) og `KP-MASK-KAS-01/02` (selvkjørende kunstkasser, type `kunstkasse`). Nye kommandoer er `ta_ned_verk`, `heng_opp_verk`, `pakk_verk` og `kjor_kasse_til_magasin`. SEC-M4 gjelder nå all kunsthåndtering, og hengeroboten krever konservator til stede. Hengeroboten jobber bare i saler, og kassen kjører bare til MAG-1 eller MAG-2. Nye øvingsscenarier: KP-OV-07 og KP-OV-08. Ladestasjonen har nå 10 plasser. Maskinparken har 40 maskiner.
- **MP14. Produktark (Lars' valg: generert).** `06_kart/produktark_builder.py` skriver ett ark per maskintype pluss `README.md` med dataflyt (Mermaid) til `04_knowledge/04_domain/operations/maskinpark/`. Hvert ark viser enhetene, datastrømmen (signaler og hendelseskoder), MCP-kallene for å følge maskinen, og kommandoene med et eksempel. Telemetrisignalene er oppdiktet produkttekst; det som er lagret, er hendelsene. `maskinpark_builder.py` kjører generatoren. Testen sjekker at arkene stemmer med dataene, og at eksemplet i hvert ark godtas av regelsjekken.
- **Tester:** ny `tests/test_kunstroboter_og_produktark.py`, kjørt rød først.

