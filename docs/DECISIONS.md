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
