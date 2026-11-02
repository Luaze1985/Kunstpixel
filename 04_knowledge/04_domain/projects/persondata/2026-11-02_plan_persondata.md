# Kundedatabase for Kunstpixel (medlemmer, gavekort, kunder 2021–2026) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Et Python-skript som genererer en stor, deterministisk og syntetisk kundedatabase for Kunstpixel, med medlemmer og medlemsfordeler, gavekort, påmeldinger, skole, utleie og henvendelser fra 2021-11-02 til 2026-11-02. Alle koblinger til ansatte bruker de eksisterende ansatte i `museum.db` (`hr_ansatte`, 168 personer, 2010–2026). Planen har også en behandlingsprotokoll, en slettesjekk og en skrivebeskyttet MCP-server.

**Architecture:**
- Grunnlaget er greina `hr-konsolidering`. Den har `05_data/museum.db` med `hr_ansatte`, `hr_vakter`, `hr_fravaer`, `dagsbesok` og `hendelser`, og datapolicyen `src/kunstpixel/core/datapolicy.py`.
- Generatoren leser `museum.db` skrivebeskyttet. Den skriver kundedata til en egen, generert fil, `05_data/persondata/persondata.db`, som ikke committes.
- Ansatte genereres ikke på nytt. De refereres med `ansatt_id` (`KP-ANS-NNN`), og navn kopieres eksakt fra `hr_ansatte.navn`.

**Tech Stack:** Python 3.13, `sqlite3`, `faker>=40.44` (locale `no_NO`), `pyyaml`, `mcp` (`mcp.server.fastmcp`), pytest.

**Spec:**
- `01_inbox/2026-11-02_forslag_persondata_ansatte_kunder.md`
- Brukerbeslutninger 2026-11-02:
  - navnet er **Kunstpixel**;
  - volumet skal være stort;
  - kunder 5 år tilbake;
  - ansatte 2010–2026;
  - tilgang via MCP;
  - navnene skal matche de eksisterende ansatte;
  - kunder omfatter medlemmer med fordeler og gavekort.

### Funn som styrer planen (kontrollert 2026-11-02)
- `hr-konsolidering:05_data/museum.db` har 168 ansatte i `hr_ansatte` (72 aktive per 2026-11-02, 94 sluttet). Alle har `datakilde` merket syntetisk via `archive_generator`. Telefonnumrene har 7 siffer etter +47, så de er ugyldige og kan ikke tilhøre noen. E-postene bruker `@kunstpixel.no`.
- **Medlemmer, gavekort og kunder finnes ikke** i noen grein.
- `dagsbesok` har 703 284 besøk fra 2021-11-02 til 2026-12-31. Medlemsbesøk må passe inn i disse dagstallene.
- `hendelser` dekker bare 2026-09-01 til 2026-12-31 (45 stk.). Tidligere arrangementer må genereres.
- `hr-konsolidering` har ingen PR og er ikke slått inn i `main`.

### Valgt bort (kort)
- **Generere ansatte på nytt** (forrige planversjon): de finnes allerede, og nye ansatte ville ikke matchet dem.
- **Legge kundetabellene inn i `museum.db`:** fila er 16 MB binær i git allerede. 200 000 nye rader per regenerering ville gjort historikken tung. Museumsverten leser også den fila.
- **Eksterne generatortjenester (Mockaroo, Gretel) og Supabase:** krever API-nøkkel eller skykonto og gir ingenting Faker ikke gjør lokalt. Supabase kan bli fase 2 for en delt database.

## Global Constraints

- Python `>=3.13`. På Windows kjøres alt som `py -3.13 ...`.
- `05_data/museum.db` åpnes kun med `mode=ro`. En test sjekker at SHA-256 er uendret.
- `05_data/persondata/*.db` committes aldri (`.gitignore`).
- Organisasjonsnavnet er **Kunstpixel** i alle nye filer.
- Hver rad i alle nye tabeller har `datakilde TEXT NOT NULL = 'syntetisk (persondata_generator)'`. Det matcher regexen i `datapolicy._SYNTETISK_RE`.
- Faker-locale er `no_NO`. Faker sin `phone_number()` brukes ikke.
- Kunders e-post er `<lokal>@eksempel.invalid` med lokal del `[a-z0-9.]` (æ→ae, ø→o, å→aa). Kunders telefon er `0` + 7 siffer.
- Ansatte som også er kunder (personalmedlemskap) har `kontakter.ansatt_id` satt, og `fornavn + " " + etternavn == hr_ansatte.navn` eksakt. Dobbelt etternavn med bindestrek beholdes, og alt etter første mellomrom regnes som etternavn. Kontakten får `epost` = `hr_ansatte.epost`.
- Alle referanser til ansatte (`solgt_av_ansatt_id`, `besvart_av_ansatt_id`, `ansvarlig_ansatt_id`) peker på en ansatt som var aktiv på datoen: `ansatt_fra <= dato` og (`ansatt_til` er NULL eller `ansatt_til >= dato`).
- Følgende lagres aldri: adresse, fødselsnummer, fødselsdato, kontonummer, kortdata eller barns navn.
- Standard seed er `2026`. Samme seed og skala gir identisk innhold.
- `REFERANSEDATO = date(2026, 11, 2)` og `KUNDER_START = date(2021, 11, 2)`.
- ASCII-identifikatorer uten æøå. Datoer lagres som ISO-tekst. Datoaritmetikk gjøres med `timedelta`.

## Review Focus

1. **Generatoren kjøres to ganger:** uten `--overskriv` skal den feile med en tydelig melding, og fila skal stå urørt. → Task 4.
2. **Navnematch mot ansatte med dobbelt etternavn** («Henrik Faye-Lund»): splitting og sammensetting gir eksakt originalnavnet. → Task 2.
3. **Gavekort brukt mer enn saldo eller etter utløp:** summen av innløsninger skal aldri overstige beløpet, og ingen innløsning skal skje etter `gyldig_til`. → Task 3.
4. **MCP-oppslag med ukjent eller ondsinnet ID/kode** (`"GK' OR '1'='1"`): skal gi `{"funnet": False}` og verken unntak eller andres data. → Task 6.
5. **Tabell uten regel i protokollen:** skal rapporteres som «mangler regel», ikke hoppes over. → Task 5.

---

## Filstruktur

| Fil | Ansvar |
| :--- | :--- |
| `src/kunstpixel/persondata/config.py` | Konstanter, skalaer, medlemskapstyper, fordeler, e-post- og telefonhjelpere |
| `src/kunstpixel/persondata/schema.sql` | DDL for kundetabellene |
| `src/kunstpixel/persondata/ansattkilde.py` | Leser `hr_ansatte` og `dagsbesok` skrivebeskyttet, og slår opp hvem som var aktiv |
| `src/kunstpixel/persondata/kunder.py` | Genererer alle kundetabeller |
| `src/kunstpixel/persondata/generer.py` | CLI som bygger `persondata.db` |
| `src/kunstpixel/persondata/slettesjekk.py` | Lagringstid mot protokollen, for både `persondata.db` og HR-tabellene i `museum.db` |
| `src/kunstpixel/persondata/mcp_server.py` + `src/persondata_mcp.py` | Skrivebeskyttet MCP |
| `05_data/persondata/behandlingsprotokoll.yaml`, `README.md`, `ovelser.md` | Dokumentasjon |
| `tests/test_persondata_*.py` | Én fil per task |

---

### Task 0: Grunnlag (krever brukerens ja)

- [ ] **Step 1:** `git merge origin/hr-konsolidering` inn i `claude/affectionate-einstein-1g8q56`. Prøvesammenslåing 2026-11-02 viste ingen konflikter. Ingen force-push.
- [ ] **Step 2:** Endre basen til PR Luaze1985/Kunstpixel#6 fra `main` til `hr-konsolidering`, slik at PR-en bare viser endringene i denne planen.
- [ ] **Step 3:** `py -3.13 -m pytest -q` på resultatet, før vi endrer noe. Noter antall bestått/feilet som baseline i PR-beskrivelsen. Tester som feiler allerede her, er ikke vår feil, men skal nevnes.

---

### Task 1: Konfigurasjon, skjema og avhengigheter

**Files:** Modify `pyproject.toml` (legg til `faker>=40.44` og `pyyaml>=6.0`, og markøren `slow`) og `.gitignore` (`05_data/persondata/*.db`). Create `config.py`, `schema.sql` og `05_data/persondata/README.md`. Test: `tests/test_persondata_schema.py`.

**Interfaces — Produces:**
- `config.REFERANSEDATO`, `config.KUNDER_START: date`; `config.SKALAER = {"test": 0.02, "full": 1.0}`; `config.STANDARD_DB_STI`, `config.MUSEUM_DB_STI`, `config.SCHEMA_STI: Path`; `config.DATAKILDE = "syntetisk (persondata_generator)"`.
- `config.lag_epost(fornavn: str, etternavn: str, lopenr: int) -> str` og `config.lag_telefon(rng: random.Random) -> str`.
- `config.MEDLEMSKAPSTYPER: dict[str, int]` (type → årspris i kr): `student 250`, `enkelt 450`, `senior 350`, `familie 750`, `venn 2500`, `ansatt 0`.
- `config.FORDELER: dict[str, tuple[str, ...]]` (fordel → typene som har den):
  - `fri_inngang`: alle typer;
  - `rabatt_butikk_10`: alle unntatt `venn`;
  - `rabatt_butikk_20`: `venn`, `ansatt`;
  - `rabatt_kafe_10`: alle typer;
  - `forhandsvisning`: `venn`, `familie`;
  - `invitasjon_aapning`: `venn`, `ansatt`;
  - `gratis_omvisning`: `venn`, `senior`;
  - `medbring_gjest`: `venn`, `familie`.
- Tabeller i `schema.sql`. Alle har `datakilde`, og `fordeler` og `medlemskapstyper` fylles fra config:
  - `kontakter(kontakt_id TEXT PK 'K000001', fornavn, etternavn, epost, telefon, ansatt_id NULL, opprettet, nyhetsbrev_samtykke INT, samtykke_dato NULL, samtykke_kilde NULL CHECK IN ('nettside','kasse','arrangement'), trukket_dato NULL, siste_aktivitet)`
  - `medlemskapstyper(type PK, aarspris INT)`, `fordeler(fordel PK, beskrivelse)`, `medlemskapstype_fordel(type FK, fordel FK)`
  - `medlemskap(medlemskap_id INTEGER PK, kontakt_id FK, type FK, startdato, sluttdato, betalt_belop INT, fornyelse_av NULL FK→medlemskap, solgt_av_ansatt_id NULL)`
  - `medlemsbesok(besok_id INTEGER PK, medlemskap_id FK, dato, antall_gjester INT)`
  - `fordel_bruk(bruk_id INTEGER PK, medlemskap_id FK, fordel FK, dato, rabatt_belop REAL)`
  - `gavekort(gavekort_id INTEGER PK, kode TEXT UNIQUE 'GK-XXXX-XXXX', belop INT CHECK IN (200,300,500,1000), kjoper_kontakt_id FK, mottaker_kontakt_id NULL FK, utstedt, gyldig_til, kanal CHECK IN ('butikk','nettbutikk','skranke'), solgt_av_ansatt_id NULL)`
  - `gavekort_bruk(bruk_id INTEGER PK, gavekort_id FK, dato, belop REAL, sted CHECK IN ('billett','butikk','kafe','arrangement'))`
  - `arrangementer(arrangement_id TEXT PK, kilde CHECK IN ('generert','museum.db'), type, tittel, dato, maks_deltakere INT, pris_voksen REAL, pris_barn REAL, ansvarlig_ansatt_id NULL)`
  - `pameldinger(pamelding_id INTEGER PK, arrangement_id FK, kontakt_id FK, antall_voksne INT, antall_barn INT, belop REAL, betalt_med CHECK IN ('kort_kasse','vipps','gavekort','medlemsfordel'), registrert)`
  - `skolebestillinger(bestilling_id INTEGER PK, skole, kontaktlaerer, jobb_epost, klassetrinn INT CHECK 1–13, antall_elever INT, dato, ansvarlig_ansatt_id NULL)`
  - `utleie(foresporsel_id INTEGER PK, kundetype CHECK IN ('privat','bedrift'), kontaktperson, epost, firmanavn NULL, dato, status CHECK IN ('forespurt','bekreftet','avlyst','gjennomfoert'), ansvarlig_ansatt_id NULL)`
  - `henvendelser(henvendelse_id INTEGER PK, tidspunkt, kanal CHECK IN ('cli','telegram','skranke','epost'), fritekst, kategori, inneholder_persondata INT, kontakt_id NULL, besvart_av_ansatt_id NULL)`

- [ ] **Step 1: Skriv feilende tester:**
  - `test_schema_lager_alle_tabeller`: settet av tabeller fra `:memory:` er lik listen over.
  - `test_alle_tabeller_har_datakilde`.
  - `test_ingen_forbudte_kolonner`: ingen kolonne matcher `fodselsnummer|fnr|adresse|kontonummer|kortnummer|fodt|barn_navn`.
  - `test_lag_epost`: `lag_epost("Bjørg", "Åsen", 7) == "bjorg.aasen.7@eksempel.invalid"`.
  - `test_lag_telefon`: 1000 numre matcher alle `^0\d{7}$`.
  - `test_datakilde_godtas_av_datapolicy`: `normalize_classification(DATAKILDE) == "syntetisk"`.
  - `test_fordeler_dekker_alle_typer`: hver medlemskapstype har minst `fri_inngang`.
- [ ] **Step 2:** `py -3.13 -m pytest tests/test_persondata_schema.py -v`. Forventet: FAIL.
- [ ] **Step 3:** Implementer.
- [ ] **Step 4:** Samme kommando. Forventet: PASS.
- [ ] **Step 5:** Commit `feat(persondata): skjema for medlemmer, gavekort og kunder`.

---

### Task 2: Ansattkilde (les eksisterende ansatte)

**Files:** Create `src/kunstpixel/persondata/ansattkilde.py`. Test: `tests/test_persondata_ansattkilde.py`.

**Interfaces:**
- Produces:
  - `Ansatt = NamedTuple(ansatt_id: str, navn: str, avdeling: str, stilling: str, ansatt_fra: date, ansatt_til: date | None, epost: str)`
  - `hent_ansatte(museum_db: Path) -> list[Ansatt]`. Leser kun med `mode=ro`.
  - `aktive_paa(ansatte: list[Ansatt], dato: date, avdelinger: set[str] | None = None) -> list[Ansatt]`
  - `del_navn(navn: str) -> tuple[str, str]`. Splitter ved første mellomrom.
  - `hent_dagsbesok(museum_db: Path, fra: date, til: date) -> dict[date, tuple[int, bool]]`. Gir besøk totalt og om museet var åpent.

- [ ] **Step 1: Skriv feilende tester** mot den ekte `05_data/museum.db`:
  - `test_henter_168_ansatte`.
  - `test_aktive_per_referansedato`: `len(aktive_paa(a, date(2026, 11, 2))) == 72`.
  - `test_del_navn_dobbelt_etternavn`: `del_navn("Henrik Faye-Lund") == ("Henrik", "Faye-Lund")`, og for alle 168 er `" ".join(del_navn(n)) == n`.
  - `test_avdelingsfilter`: alle resultater med `avdelinger={"Formidling"}` har den avdelingen.
  - `test_dagsbesok_periode`: nøklene dekker alle datoer fra 2021-11-02 til 2026-11-02.
  - `test_museum_db_uendret`: SHA-256 er lik før og etter.
- [ ] **Step 2:** FAIL. **Step 3:** Implementer. **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(persondata): les eksisterende ansatte skrivebeskyttet`.

---

### Task 3: Kundegenerator

**Files:** Create `src/kunstpixel/persondata/kunder.py`. Test: `tests/test_persondata_kunder.py`.

**Interfaces:**
- Consumes: `Ansatt`, `aktive_paa`, `del_navn`, dagsbesøk-dicten og config.
- Produces: `generer_kunder(rng: random.Random, fake: Faker, ansatte: list[Ansatt], dagsbesok: dict[date, tuple[int, bool]], hendelser: list[dict], faktor: float = 1.0) -> dict[str, list[dict]]`. Nøklene er lik tabellnavnene i Task 1, unntatt katalogtabellene.

**Volumer og regler ved `faktor=1.0`:**

| Tabell | Antall | Regler |
| :--- | :--- | :--- |
| `kontakter` | 25 000 + én per ansatt som var aktiv i perioden | 40 % samtykker til nyhetsbrev. 10 % av dem trekker samtykket. **Planter brudd:** 2 % av dem som trakk samtykket har fortsatt e-post og `siste_aktivitet` mer enn 3 år tilbake. |
| `medlemskap` | ca. 3 000 aktive til enhver tid, 1 års varighet, 65 % fornyer (`fornyelse_av`) | Fordeling: enkelt 40 %, familie 20 %, senior 15 %, student 15 %, venn 10 %. `ansatt`-medlemskap for alle ansatte som var aktive i perioden, med varighet = ansettelsen avgrenset til perioden. `solgt_av_ansatt_id` er en aktiv ansatt i Formidling eller Drift. **Planter brudd:** medlemskap som sluttet før 2023-11-02 og fortsatt har full kontaktinfo. |
| `medlemsbesok` | ca. 4 per medlemskap per år | Bare på åpne dager. Per dag er medlemsbesøk ≤ 25 % av `besok_totalt`. `antall_gjester` er større enn 0 bare for typer med `medbring_gjest`. |
| `fordel_bruk` | ca. 30 000 | Kun fordeler typen har. Datoen er innenfor medlemskapet. |
| `gavekort` | ca. 1 500 per år | `gyldig_til = utstedt + timedelta(days=1096)` (3 år, foreldelsesloven, må verifiseres). Koden er unik. 40 % har `mottaker_kontakt_id`. `solgt_av_ansatt_id` er aktiv på `utstedt` når kanalen ikke er `nettbutikk`. |
| `gavekort_bruk` | 1–3 innløsninger per kort, 15 % brukes aldri | Summen ≤ `belop`. Datoen er mellom `utstedt` og `gyldig_til` og ≤ REFERANSEDATO. |
| `arrangementer` | 1 000 genererte (2021-11-02 til 2026-08-31) + `hendelser` fra museum.db med `dato <= 2026-11-02` (`kilde='museum.db'`, `arrangement_id = 'MDB-' + id`) | `ansvarlig_ansatt_id` er en aktiv ansatt i Formidling. Typer og priser som i `hendelser`. |
| `pameldinger` | 40–100 % av kapasiteten | 1–4 voksne og 0–3 barn (barn bare på barnearrangement og verksted). `belop = voksne*pris_voksen + barn*pris_barn`. Bare kontakter med `opprettet <= dato`. `betalt_med='medlemsfordel'` bare når kontakten har aktivt medlemskap med `gratis_omvisning` og typen er omvisning. `'gavekort'` gir også en rad i `gavekort_bruk` med `sted='arrangement'`. |
| `skolebestillinger` / `utleie` | 1 500 / 300 | Skole = `f"{fake.city()} skole"`, trinn 1–13, 15–30 elever, hverdager utenom juli. Utleie: 60 % bedrift (`firmanavn = fake.company()`), 40 % privat. `ansvarlig_ansatt_id` er aktiv i Formidling (skole) eller i Ledelse/Marked (utleie). |
| `henvendelser` | 20 000 | Kategorier er FAQ-kategoriene i `publikum_faq` pluss `medlemskap` og `gavekort`, med minst 10 maler per kategori. 5 % har `inneholder_persondata = 1`, med navn, fiktiv telefon eller e-post flettet inn (f.eks. «Jeg heter {navn}, gavekortet mitt virker ikke, ring {tlf}»). Tekster med 0 skal aldri inneholde `@` eller matche `0\d{7}`. `besvart_av_ansatt_id` er en aktiv ansatt. 30 % har `kontakt_id`. |

- [ ] **Step 1: Skriv feilende tester.** Fixture med `faktor=SKALAER["test"]` og de ekte ansatte og dagsbesøkene. Én test er merket `@pytest.mark.slow` og kjører full skala.
  - `test_ansattkontakter_matcher_hr_navn`: for hver kontakt med `ansatt_id` er `f"{fornavn} {etternavn}" == hr_ansatte.navn` og `epost == hr_ansatte.epost`.
  - `test_ansattreferanser_aktive_paa_dato`: gjelder alle `*_ansatt_id` i alle tabeller.
  - `test_alle_datoer_i_kundeperioden`.
  - `test_medlemsfordeler_kun_for_riktig_type`: hver `fordel_bruk` finnes i `medlemskapstype_fordel` for medlemskapets type.
  - `test_medlemsbesok_innenfor_dagsbesok`: per dag er sum ≤ 25 % av `besok_totalt`, og bare på dager der `er_aapent`.
  - `test_gavekort_saldo_aldri_negativ`.
  - `test_gavekort_ikke_brukt_etter_utlop`.
  - `test_gavekortkoder_unike`: matcher `^GK-[A-Z0-9]{4}-[A-Z0-9]{4}$`.
  - `test_pameldinger_overstiger_aldri_kapasitet`.
  - `test_plantede_brudd_finnes`: for både kontakter og medlemskap.
  - `test_henvendelser_persondata_andel`: mellom 0,03 og 0,07.
  - `test_full_skala_volum` (slow): 25 000 kontakter uten ansatte, 20 000 henvendelser, og mellom 2 500 og 3 500 aktive medlemskap på 2026-11-02.
- [ ] **Step 2:** FAIL. **Step 3:** Implementer. **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(persondata): generator for medlemmer, gavekort og kunder`.

---

### Task 4: Bygg databasen (CLI)

**Files:** Create `src/kunstpixel/persondata/generer.py`. Test: `tests/test_persondata_generer.py`.

**Interfaces — Produces:**
- `bygg_database(sti: Path, museum_db: Path = MUSEUM_DB_STI, seed: int = 2026, skala: str = "full", overskriv: bool = False) -> dict[str, int]`
- CLI: `py -3.13 -m src.kunstpixel.persondata.generer [--sti] [--seed] [--skala test|full] [--overskriv]`

**Tester og steg:**
- [ ] **Step 1: Skriv feilende tester:**
  - `test_bygger_alle_tabeller`: alle tabeller har mer enn 0 rader ved `skala="test"`.
  - `test_nekter_overskriving`: gir `FileExistsError` som nevner `--overskriv`, og `mtime` er uendret.
  - `test_overskriv_flagg`.
  - `test_deterministisk_innhold`.
  - `test_ukjent_skala`: gir `ValueError`.
  - `test_museum_db_uendret`.
  - `test_fremmednokler_gyldige`: `PRAGMA foreign_key_check` er tom.
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implementer med én transaksjon og `executemany`. Faker får `seed_instance(seed)`, og generatoren bruker `random.Random(seed)`.
- [ ] **Step 4:** PASS. Kjør full generering og noter antall rader, kjøretid og filstørrelse i `05_data/persondata/README.md`. Forventet: ca. 200 000 rader og under 3 minutter.
- [ ] **Step 5:** Sjekk at `git status` ikke viser `.db`. Commit `feat(persondata): CLI for persondata.db`.

---

### Task 5: Behandlingsprotokoll og slettesjekk

**Files:** Create `05_data/persondata/behandlingsprotokoll.yaml` og `src/kunstpixel/persondata/slettesjekk.py`. Test: `tests/test_persondata_slettesjekk.py`.

**Interfaces — Produces:**
- `last_protokoll(sti: Path | None = None) -> dict`
- `Brudd = NamedTuple(database: str, tabell: str, antall: int, regel: str)`
- `finn_brudd(databaser: dict[str, sqlite3.Connection], protokoll: dict, referansedato: date) -> list[Brudd]`. Nøklene er `"persondata"` og `"museum"`.
- CLI: `py -3.13 -m src.kunstpixel.persondata.slettesjekk`

**Protokollformat:**
- Øverst: `organisasjon: Kunstpixel` og en merknad om at lagringstidene må verifiseres.
- Under `behandlinger:` er nøkkelen `<database>.<tabell>`. Hver behandling har `formaal`, `rettslig_grunnlag`, `kategorier`, `saerlig_kategori`, `tilgang`, `lagringsregler` (liste av `{felt, dager, betingelse}`) og `verifisert: false`.
- Dekker alle tabeller i `persondata.db` med persondata, og `museum.hr_ansatte`, `museum.hr_vakter`, `museum.hr_fravaer` og `museum.personas`.

**Forslag til regler (må verifiseres):**

| Behandling | Regel |
| :--- | :--- |
| `museum.hr_ansatte` | `ansatt_til` + 1 096 dager |
| `museum.hr_vakter` | `dato` + 731 dager |
| `museum.hr_fravaer` | `til` + 365 dager. `saerlig_kategori: true` (helse) |
| `persondata.kontakter` | `trukket_dato` + 30 dager, ellers `siste_aktivitet` + 1 096 dager |
| `persondata.medlemskap` | `sluttdato` + 1 096 dager |
| `persondata.medlemsbesok` / `fordel_bruk` | `dato` + 731 dager |
| `persondata.gavekort` / `gavekort_bruk` | `gyldig_til` + 1 827 dager (bokføring) |
| `persondata.pameldinger` | `registrert` + 1 827 dager |
| `persondata.henvendelser` | `tidspunkt` + 365 dager |
| `persondata.skolebestillinger` / `utleie` | `dato` + 1 096 dager / 1 827 dager |
| Katalogtabeller og `arrangementer` | `persondata: false` |

**Tester og steg:**
- [ ] **Step 1: Skriv feilende tester:**
  - `test_protokoll_dekker_alle_tabeller`: tabeller uten persondata er eksplisitt merket `persondata: false`.
  - `test_finner_sluttede_ansatte`: `museum.hr_ansatte` har antall > 0, fordi flere sluttet før 2023-11-02.
  - `test_finner_plantede_kundebrudd`: gjelder `kontakter` og `medlemskap`.
  - `test_mangler_regel_rapporteres`: gir `antall == -1` og `regel == "mangler regel"`.
  - `test_tom_database`: ingen unntak.
  - `test_museum_db_uendret`.
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implementer. Grensedatoen sendes som `?`-parameter. Tabell- og kolonnenavn valideres mot `PRAGMA table_info`.
- [ ] **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(persondata): behandlingsprotokoll og slettesjekk`.

---

### Task 6: Skrivebeskyttet MCP-server

**Files:** Create `src/kunstpixel/persondata/mcp_server.py` og `src/persondata_mcp.py`. Test: `tests/test_persondata_mcp.py`.

**Interfaces — Produces:**
- `FastMCP("Kunstpixel-persondata")` med nøyaktig disse verktøyene. Hvert svar har `"klassifisering": "syntetisk"`, samme konvensjon som `datapolicy`.
  - `tell_poster(tabell: str) -> dict`
  - `medlemsstatistikk(dato: str) -> dict`: aktive per type. Ingen navn.
  - `innsyn_kontakt(kontakt_id: str) -> dict`: innsyn etter art. 15. Gir kontakten, medlemskap, fordelsbruk, gavekort, påmeldinger og henvendelser, eller `{"funnet": False}`.
  - `gavekort_saldo(kode: str) -> dict`: `{funnet, belop, brukt, saldo, gyldig_til}`. Ingen navn.
  - `slettesjekk() -> list[dict]`
- DB-sti kan overstyres med `KUNSTPIXEL_PERSONDATA_DB`.

**Tester og steg:**
- [ ] **Step 1: Skriv feilende tester:**
  - `test_verktoyliste`: nøyaktig de fem verktøyene.
  - `test_alle_svar_er_merket_syntetisk`.
  - `test_innsyn_ukjent_og_injeksjon`: gir `{"funnet": False}`.
  - `test_gavekort_injeksjon`: `"GK' OR '1'='1"` gir `{"funnet": False}`.
  - `test_innsyn_kjent_id_kun_egne_data`.
  - `test_gavekort_saldo_stemmer`: saldo = beløp minus summen av innløsninger.
  - `test_ingen_skriving`: gir `sqlite3.OperationalError`.
  - `test_tell_poster_avviser_ukjent_tabell`.
- [ ] **Step 2:** FAIL. **Step 3:** Implementer. **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(persondata): skrivebeskyttet MCP-server`.

---

### Task 7: Dokumentasjon og full verifisering

- [ ] **Step 1:** Oppdater disse filene:
  - `AGENTS.md`: persondata.db, kommandoer, og at Regel 1 gjelder museum.db.
  - `04_knowledge/04_domain/operations/tool_access.md`: tilgangstabell for persondata.
  - `05_data/persondata/README.md`: volumer og kobling til Claude Desktop.
  - `01_inbox/2026-11-02_forslag_persondata_ansatte_kunder.md`: status «Besluttet».
- [ ] **Step 2:** Lag `05_data/persondata/ovelser.md` med 6 scenarioer:
  1. Innsyn for et medlem.
  2. Sletting etter trukket samtykke.
  3. En ansatt som sluttet i 2012 ber om innsyn, og hva som burde vært slettet.
  4. Avvik: en medlemsliste ble sendt til feil mottaker (72 timer).
  5. Utløpt gavekort og kundens rettigheter.
  6. Vasking av `henvendelser` før bruk som treningsdata.
- [ ] **Step 3:** `py -3.13 -m pytest -v`. Forventet: samme baseline som i Task 0, og alle nye tester består.
- [ ] **Step 4:** `git status`: ingen `.db` under `persondata/`. Commit `docs(persondata): AGENTS, tilgang, øvelser`.
