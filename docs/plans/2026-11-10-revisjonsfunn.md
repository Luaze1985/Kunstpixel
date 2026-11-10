# Kunstpixel: vurdering av de 17 revisjonsfunnene, og plan for retting

## Context

En ekstern gjennomgang av GitHub-versjonen (`origin/main` = `b076cfe`) ga 17 funn. Disken er sannheten, og den ligger 31 upushede commits foran GitHub (`main` +25, `design/startbilde` +6). Alle funn er derfor kontrollert mot disken med kun lesing. Ingen tester eller bygg er kjørt: **STATUS: UNTESTED** for alt som handler om hva pytest faktisk gir.

Lars ba om en vurdering punkt for punkt med tydelige konsekvenser. Planen under er derfor først en dom per funn, så pakker i anbefalt rekkefølge.

Tre ting gjennomgangen ikke kunne se:
- `PLAN.md`, `docs/DECISIONS.md` og `docs/plans/` finnes bare lokalt. Flere funn er allerede kjent eller delvis rettet der.
- Funn 7 er verre lokalt enn på GitHub: en ny utsjekk av grenen vil trolig gi røde tester.
- Colab-databasen inneholder syntetiske fødselsnumre, helse- og fagforeningsfelt sammen med ekte gatenavn. Om GitHub-repoet er offentlig, er ikke kontrollert. Det bør Lars sjekke uansett.

## Dom per funn

| # | Funn | Lokalt | Bør gjøres? | Konsekvens hvis ikke | Kostnad / bivirkning ved retting |
|---|---|---|---|---|---|
| 1 | To navn på samme person | Stemmer, 12 av 12 avviker | **Ja** | KI og MCP-verktøy kan svare med «Ada Nord» der registeret sier «Jonas Berg». `tests/test_hrdemo.py` låser i dag det gale navnet. | Datamodellendring. 6+ lesere av `name` i `hrdemo.py`, MCP, API, CLI. Krever nytt bygg av `museum.db`. |
| 2 | Rollen velges av klienten | Stemmer, og en test bekrefter det som ønsket oppførsel | **Ja, men ikke først** | Alle på maskinen ser ledelsesdata ved å sende `"rolle":"museumsdirektor"`. I dag bare 127.0.0.1, så lav risiko. Blir alvorlig den dagen siden hostes. | Arkitekturvalg. 2–3 filer. Rollevelgeren i `intern.html` forsvinner eller blir «sårbar modus». |
| 3 | Fødselsnumre kan være ekte | Stemmer, 3 av 168 består mod 11 | **Ja** | Liten, men reell sjanse for at et nummer tilhører en ekte person, i et sett som også har helsefelt. | Generatoren endres på én linje, men CSV, Colab-database, notatbok og HTML må lages på nytt. Generatoren leser `museum.db`, så resultatet kan avvike fra oktober-versjonen på flere felt enn fødselsnummer. |
| 4 | 99 MB database i git | Stemmer | **Ja, men premisset er delvis feil** | Filen ligger alt på GitHub, så neste push stopper ikke. Den stopper først hvis filen vokser 1 MB. Hver kloning er treg. | Å slutte å spore den fjerner den ikke fra historikken. Historikken røres ikke (krever force push). Colab-flyten må få filen på annen måte. |
| 5 | Fasiten ligger i angrepsdataene | Stemmer. Ingen tester leser kolonnene | **Ja, hvis settet skal brukes til arenatester** | En KI som «avslører» noen, leser bare opp kolonnen `avslort_sensitiv_innsikt`. Testen måler ingenting. | 6 filer. Notatboken må lese fasiten fra egen fil. |
| 6 | Testen skriver i `05_data` | Stemmer. Kjent i `DECISIONS.md:44` | **Ja** | I dag bare støy. Samme mønster kan en dag endre innhold. | 2–3 filer. Ingen bivirkning. |
| 7 | Sjekksum bare gyldig med CRLF | Stemmer, verre enn beskrevet | **Ja, først** | Ny utsjekk gir trolig to røde tester. Colab-pakken avvises på sjekksum uten at noe er galt. `DECISIONS.md:43` påstår grønn ny utsjekk, og det stemmer trolig ikke. | 1–2 filer. |
| 8 | `--check` sammenligner filhash | Stemmer | **Ja, lav hast** | Falsk «ULIK» på annen maskin eller SQLite-versjon. På Lars' maskin virker den. | 2–3 filer, ny sammenligningsfunksjon. |
| 9 | Fem skript skriver rett i `museum.db` | Stemmer. Fire er ikke referert noe sted | **Ja** | Ett feilkjørt skript endrer databasen stille, og neste bygg visker det ut. `ADR_012` ber faktisk om å kjøre ett av dem. | 5 skript + 2 dokumenter. |
| 10 | Ansattlisten i mange kopier | Delvis. 0 avvik utenom funn 1 | **Bare en test** | Ingen feil i dag. | Én sammenligningstest. Ikke flytt filer. |
| 11 | YAML er generert, ikke kilde | Stemmer | **Bare merking og en test** | Håndretting i YAML forsvinner ved neste generering. | Merknad øverst + én samsvarstest. Ikke gjør YAML til kilde nå. |
| 12 | Ujevn merking av syntetisk | Stemmer | **Halvveis** | `personas` og `hr_personalmapper` regnes som ekte data og nektes modellen uten forklaring. | Rett de to formatene (4–5 filer + bygg). **Merk:** etterpå slipper policyen CV-er og personalmapper gjennom der den gjelder. Det er hensikten, men det er en endring i hva modellen ser. `datakilde` på 30 nye tabeller: ikke nå. |
| 13 | Avhengigheter | Delvis. `mcp==1.29.1` er alt låst lokalt | **Ja, lite** | Ny maskin stopper i testinnsamlingen når pandas mangler. | 1 fil. |
| 14 | Chat uten `anthropic`-pakken | Delvis. Produktkoden tåler det, bare to tester gjør det ikke | **Ja, trivielt** | Røde tester på maskin uten pakken. Ingen feil for brukeren. | 2 testfiler. |
| 15 | Dokumentene spriker | Delvis rettet lokalt | **Ja, sist** | `AGENTS.md` lister 5 verktøy som ikke finnes og sier 8, 5, 36 og 45 om hverandre. Koden har 51. Agenter skriver mot ting som ikke finnes. | 5–6 filer. |
| 16 | Telefon og e-postdomene | Stemmer | **Nei, ikke nå** | Ingen e-post sendes av systemet, så ingenting kan havne hos ekte mottaker. | Domenebytte krever endring i `kilde/museum_base.db`, som er frosset. Høy kostnad, nesten ingen gevinst. Tas opp igjen hvis utsending noen gang bygges. |
| 17 | Datafinner uten sperrer | Stemmer, bevisst unntak | **Ja, etter 12** | Unntaket hviler på at noen husker det. Første ekte rad går rett til Claude. | Ca. 3 filer. Må vente på funn 12, ellers slår sperren inn med en gang fordi to tabeller i dag regnes som ekte. |

## Lars' valg 2026-11-10

- Funn 1: navnekolonnen fjernes fra `hr_people`.
- Funn 2: venter. Bare beslutningen skrives ned.
- Funn 4: både Colab-databasen og MintHCM-dumpen tas ut av sporingen.
- Omfang: alle fem pakker, i rekkefølgen under. Utførelse inline, pakke for pakke, med stopp og rapport etter hver.
- Bekreftet på nytt etter spørsmål om demoen: hele revisjonen nå. Kjent konsekvens: demoen (Datafinner med KI-startbilde på `design/startbilde`) kommer ikke nærmere av dette. Bare funn 1 er synlig i den.
- Funn 17 endrer `datafinner.py`, som er ulik på `main` og `design/startbilde`. Er startbildet fortsatt uavgjort når pakke 4 står for tur, stopper jeg og spør hvilken gren den skal bygges på.

## Det jeg anbefaler å ikke gjøre

- Funn 16 (domene og telefon).
- `datakilde` på alle 30 tabeller (funn 12, andre halvdel).
- YAML som kilde (funn 11, alternativ to).
- Skript som skriver tall inn i dokumentene (funn 15). En test som feiler ved avvik er billigere.
- Omskriving av git-historikken for å fjerne store filer.

## Pakker i anbefalt rekkefølge

Hver oppgave følger rød-grønn: skriv testen, se den feile, minste retting, hele pytest, commit. Én commit per funn.

### Pakke 0: oppsett
- Ny gren `fix/revisjon-2026-11` fra lokal `main`. Rettingene er uavhengige av startbildet, bortsett fra funn 17 og kommentaren i `datafinner.py`.
- Kopier denne planen til `docs/plans/2026-11-10-revisjonsfunn.md` og pek dit fra `PLAN.md`.
- Kjør hele pytest én gang først og noter resultatet som utgangspunkt.

### Pakke 1: små og trygge
1. **Funn 7.** Rød: sjekk ut `01_inbox/h5_colab/` i en ren kopi (git worktree) og kjør `tests/test_leveranse_kjoring.py`. Forventet: `test_checksums_file_is_correct` og `test_package_is_regenerated_identically` feiler. Retting: `write_text(..., newline="\n")` i `skriv_colab_pakke` (`src/kunstpixel/core/intern/leveranse_bestilling.py:90-105`), lag pakken på nytt fra LF-filer. Rett `docs/DECISIONS.md:43`.
2. **Funn 6.** Ny test `test_build_skriver_lf_og_ikke_i_05_data`: bygg til `tmp_path`, krev `b"\r\n" not in` hver fil, og at `05_data/mock_*.csv` har uendret sha256 etter testen. Retting: `lineterminator="\n"` i `org_builder.py:645-653` og `h5_governance_builder.py:830-837`. Eksisterende test i `tests/test_org_builder.py` får `tmp_path`.
3. **Funn 14.** `pytest.importorskip("anthropic")` i `tests/test_chat_hub.py:180` og `tests/test_anthropic_llm.py:199`.
4. **Funn 13.** I `pyproject.toml`: ny valgfri gruppe `data = ["pandas", "numpy", "duckdb", "requests"]`, fjern `fastmcp`. `tests/test_daily_visitors_validator.py:14` får `importorskip("pandas")`.
5. **Funn 9.** Ny test `test_ingen_skript_skriver_i_museum_db`: for hver `.py` i `src/kunstpixel/data/` og `scripts/` unntatt `build_museum_db.py`, feil hvis filen har `sqlite3.connect(` mot `museum.db` uten `mode=ro`. Retting: flytt de fire ureferte skriptene til `arkiv/`, fjern skrivestien i `__main__` i `seed_handbooks.py:348-356`. Rett `ADR_012…md:30` og `docs/specs/internside-oppslagsverk/01-handboker-inn-i-bygget.md:15`.
6. **Funn 11.** Generatoren skriver `# GENERERT av h5_governance_builder.py. Ikke rediger for hånd.` øverst i hver YAML. Ny test: hver av de 8 filene starter med linjen, og antall poster i YAML er lik antall rader i tilhørende `h5_*`-tabell.

### Pakke 2: Colab-settet (funn 3, 5, 4 i én regenerering)
1. **Funn 3.** Ny test `test_fnr_er_tenor_format`: for alle 168 `syntetisk_fnr` er månedssifrene (posisjon 3–4) mellom 81 og 92. Retting i `generate_time_for_time.py:382`: `mnd + 80`.
2. **Funn 5.** Ny test: `mosaikk_risikoscore`, `risikonivaa`, `avslort_sensitiv_innsikt` finnes ikke i personvern-CSV-en, og `05_data/fasit/personvern_fasit.csv` har 168 rader med de tre kolonnene pluss ansatt-id. Retting i `generate_time_for_time.py:340-342, 523-525` og `create_colab_notebook.py:87-178` (notatboken leser fasiten i en egen, merket celle).
3. Regenerer én gang. Sammenlign ny og gammel CSV kolonne for kolonne og vis Lars forskjellen før commit.
4. **Funn 4.** Avklar først hvordan Colab får databasen i dag. Deretter `git rm --cached` på Colab-databasen og MintHCM-dumpen, legg begge i `.gitignore`, skriv regenereringskommandoen i `docs/DATAPIPELINE.md`. Filene blir liggende på disk. Krever Lars' bekreftelse.

### Pakke 3: én sannhet for personer og merking
1. **Funn 1.** Ny test `test_hr_people_har_ikke_egen_navnekolonne` (kolonnen `name` finnes ikke i `hr_people`) og `test_demo_navn_kommer_fra_hr_ansatte` (E101 gir «Jonas Berg»). Retting: fjern `name` fra `05_data/hr_demo/seed.json` og bygget, la `hrdemo.py:235, 255, 326, 335` hente navn via `ansatt_id`. Rett `tests/test_hrdemo.py:159, 185, 215` og kommentarene i `build_museum_db.py:1155-1163`. Nytt bygg.
2. **Funn 12.** Stram `tests/test_data_csv.py:42` og `tests/test_cv_personas_and_security.py:171` til å bruke `_SYNTETISK_RE` fra `core/datapolicy.py:21`. Rett `build_museum_db.py:950` og `scripts/generer_dype_personalmapper.py:285` til `syntetisk (kilde)`. Nytt bygg.
3. **Funn 10.** Ny test som sammenligner ansatt-id og navn mellom `hr_ansatte` og de to CSV-ene.

### Pakke 4: tilgang (etter at startbildet er flettet eller forkastet)
1. **Funn 2 utsettes (Lars, 2026-11-10).** Ingen kodeendring. Skriv i `docs/DECISIONS.md`: rollen velges av klienten, akseptert fordi siden bare binder til 127.0.0.1, og må rettes før intern-siden hostes. Skissen for senere: rolle settes ved oppstart, valideres med `role_id()` (`core/intern/data.py:54`), eget flagg for sårbar modus.
2. **Funn 17.** Før hvert KI-kall i `datafinner.py` (`/api/forklar`, `/api/grense/kjor`, `/api/chat`): bruk `arena.datamerke` (`core/arena.py:46`). Er én tabell «ekte», kjøres `check_policy` (`core/datapolicy.py:45`). Test med en midlertidig database der én rad har `datakilde="hr-system"`. Rett toppkommentaren `datafinner.py:37` og den døde spec-pekeren i `AGENTS.md:181`.

### Pakke 5: til slutt
1. **Funn 8.** Ny funksjon `innholdshash(db_path) -> str` i `build_museum_db.py` (skjema + sorterte rader per tabell), brukt av `--check`, `scripts/db_status_gate.py:57-63` og `scripts/db_kvalitet.py:121-142`. Test: samme innhold i to filer med ulik `page_size` gir lik hash.
2. **Funn 15.** Rett `AGENTS.md` (antall verktøy, de fem verktøynavnene som ikke finnes, rollene i regel 7), `03_team/team_roster.md` (stier), `PLAN.md` (pekeren), `docs/CHEATSHEET.md:12`, `TEST_READY.md:15`. Ny test: antallet i `AGENTS.md` er lik antall `@mcp.tool` i `core/mcp_server.py`. Hvilket av de fire formålsdokumentene som gjelder, avgjør Lars.

## Review Focus

- Ny utsjekk på Windows og Linux gir samme sjekksummer (funn 7).
- Ingen test etterlater endrede filer i `05_data` (kjør `git status` etter pytest).
- Etter funn 12: hva slipper nå gjennom datapolicyen som ikke gjorde det før.
- Etter funn 1: ingen MCP-, API- eller CLI-vei returnerer tomt navn.
- Etter funn 17: sperren slår ikke inn på dagens syntetiske data, men gjør det på én ekte rad.

## Verifisering

- Hele pytest (`py -3.13 -m pytest`) før og etter hver pakke, med tall rapportert.
- `py -3.13 src/kunstpixel/data/build_museum_db.py --check` og `scripts/db_status_gate.py` etter hvert nytt bygg.
- Pakke 1 steg 1 og Review Focus punkt 1 kjøres i en ren worktree, ikke i arbeidsmappen.
- Pakke 4: kjør Datafinner mot en midlertidig database med én ekte rad og vis at KI-kallet stoppes.
- Beslutninger skrives i `docs/DECISIONS.md`, status i `PLAN.md`.
