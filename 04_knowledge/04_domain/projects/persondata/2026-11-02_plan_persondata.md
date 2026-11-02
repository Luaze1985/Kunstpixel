# Fiktiv persondatabase (ansatte 2010–2026, kunder 2021–2026) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Et Python-skript som genererer en stor, deterministisk, tydelig fiktiv SQLite-database med ansatte (2010-01-01 → 2026-11-02) og kunder (2021-11-02 → 2026-11-02) for Kunstpixel, pluss behandlingsprotokoll, slettesjekk og en egen skrivebeskyttet MCP-server.

**Architecture:** Generatoren (Faker `no_NO` + `random.Random(seed)`) skriver til en egen fil `05_data/persondata/persondata.db`, fullstendig adskilt fra `museum.db`. Databasen er generert og committes ikke; skriptet, skjemaet og protokollen committes. En egen FastMCP-server (`src/persondata_mcp.py`) gir agenter og Claude tilgang via MCP, men bare til aggregater, innsyn per kontakt og slettesjekk.

**Tech Stack:** Python 3.13, `sqlite3` (stdlib), `faker>=40.44` (ny avhengighet), `pyyaml` for protokollen, `mcp` (`mcp.server.fastmcp`, allerede i bruk), pytest.

**Spec:** `01_inbox/2026-11-02_forslag_persondata_ansatte_kunder.md` + brukerbeslutninger 2026-11-02: navnet er **Kunstpixel**; volum er «stort»; kunder 5 år tilbake; ansatte 2010–2026; tilgang via MCP.

### Valgt bort (kort)
- **Eksterne generatortjenester (Mockaroo, Gretel, SDV-skytjenester):** krever API-nøkkel, sender skjema/data til tredjepart, og gir ingenting Faker ikke gjør lokalt.
- **Supabase (MCP er koblet til i Claude):** gir en delt skydatabase for begge gründerne, men innfører konto, nettverk og kostnad før behovet er bevist. Kan bli fase 2 — skjemaet her er vanlig SQL og kan flyttes.
- **Persondata i `museum.db`:** museumsverten svarer publikum fra den basen. Lekkasjerisiko.

## Global Constraints

- Python `>=3.13`; kjøres på Windows som `py -3.13 ...`.
- `museum.db` skal aldri åpnes for skriving. Generatoren skriver kun til `05_data/persondata/persondata.db` (eller en sti gitt som argument).
- `*.db` under `05_data/persondata/` committes aldri (`.gitignore`).
- Organisasjonsnavn i alle filer: **Kunstpixel**.
- Faker-locale: `no_NO` (ikke `nb_NO` — finnes ikke, verifisert).
- Alle e-poster: `<lokal>@eksempel.invalid`, lokal del kun `[a-z0-9.]` (æ→ae, ø→o, å→aa).
- Alle telefonnumre: 8 siffer som starter med `0` (format `0XXXXXXX`). Norske abonnentnumre starter aldri med 0, så de kan ikke tilhøre noen. Faker sin `phone_number()` skal **ikke** brukes (gir realistiske numre, verifisert).
- Ingen adresser, fødselsnumre, fødselsdatoer, kontonumre, lønn eller kortdata i noe skjema.
- Barn registreres kun som antall, aldri med navn.
- Standard seed: `2026`. Samme seed + skala ⇒ byte-identisk innhold.
- `REFERANSEDATO = date(2026, 11, 2)`; `ANSATTE_START = date(2010, 1, 1)`; `KUNDER_START = date(2021, 11, 2)`.
- Tabell- og kolonnenavn i ASCII uten æøå (samme konvensjon som `museum.db`, f.eks. `spoersmaal`).
- Hver tabell har kolonnen `fiktiv INTEGER NOT NULL DEFAULT 1`.
- Datoer lagres som ISO-tekst (`YYYY-MM-DD`, tidspunkt `YYYY-MM-DDTHH:MM`).
- Datoaritmetikk med `timedelta`, aldri `date.replace(year=...)` (29. februar).

## Review Focus

1. **Generator kjøres to ganger:** eksisterende `persondata.db` skal ikke overskrives uten `--overskriv`; uten flagget feiler kjøringen med tydelig melding. → test i Task 4.
2. **Norske tegn:** navn med æøå lagres og leses riktig, men e-postadressen inneholder aldri æøå. → test i Task 2.
3. **29. februar:** kurs tatt 2024-02-29 får gyldig_til uten krasj. → test i Task 2.
4. **MCP-innsyn med ukjent eller ondsinnet ID** (`"K1' OR '1'='1"`): gir tomt resultat, ikke unntak og ikke andres data. → test i Task 6.
5. **Tabell uten regel i protokollen:** slettesjekken rapporterer «mangler regel» i stedet for å late som alt er i orden. → test i Task 5.

---

## Filstruktur

| Fil | Ansvar |
| :--- | :--- |
| `src/kunstpixel/persondata/__init__.py` | Pakke |
| `src/kunstpixel/persondata/config.py` | Konstanter: datoer, skalaer, roller, sti, e-post/telefon-hjelpere |
| `src/kunstpixel/persondata/schema.sql` | DDL for alle 11 tabeller |
| `src/kunstpixel/persondata/ansatte.py` | Genererer ansatte, ansettelser, vakter, kurs, fravaer_karantene |
| `src/kunstpixel/persondata/kunder.py` | Genererer kontakter, arrangementer, pameldinger, skolebestillinger, utleie, henvendelser |
| `src/kunstpixel/persondata/generer.py` | CLI: bygger databasen fra skjema + generatorer |
| `src/kunstpixel/persondata/slettesjekk.py` | Leser protokollen, finner poster over lagringstid |
| `src/kunstpixel/persondata/mcp_server.py` | FastMCP-verktøy, skrivebeskyttet |
| `src/persondata_mcp.py` | Inngangspunkt for MCP over stdio |
| `05_data/persondata/behandlingsprotokoll.yaml` | Art. 30-protokoll, én oppføring per tabell |
| `05_data/persondata/README.md` | «FIKTIVE DATA», hvordan generere, forventede volumer |
| `tests/test_persondata_*.py` | Én testfil per task |

---

### Task 1: Oppsett, konfigurasjon og skjema

**Files:**
- Modify: `pyproject.toml` (legg til `"faker>=40.44"`, `"pyyaml>=6.0"` i `dependencies`)
- Modify: `.gitignore` (legg til `05_data/persondata/*.db`)
- Create: `src/kunstpixel/persondata/__init__.py`, `config.py`, `schema.sql`
- Create: `05_data/persondata/README.md`
- Test: `tests/test_persondata_schema.py`

**Interfaces:**
- Produces:
  - `config.REFERANSEDATO`, `config.ANSATTE_START`, `config.KUNDER_START: date`
  - `config.SKALAER: dict[str, float] = {"test": 0.02, "full": 1.0}`
  - `config.STANDARD_DB_STI: Path` = `PROJECT_ROOT / "05_data" / "persondata" / "persondata.db"`
  - `config.SCHEMA_STI: Path`
  - `config.lag_epost(fornavn: str, etternavn: str, lopenr: int) -> str`
  - `config.lag_telefon(rng: random.Random) -> str`
  - `config.ROLLER: dict[str, tuple[str, int, int]]` — rolle → (stillingstype, antall_samtidig, stillingsprosent):
    `museumsdirektor (fast,1,100)`, `kurator (fast,2,100)`, `samlingsforvalter (fast,2,100)`, `formidler (fast,3,100)`, `driftsansvarlig (fast,1,100)`, `administrasjon (fast,2,100)`, `kommunikasjon (fast,1,80)`, `montor (fast,2,100)`, `kafeleder (fast,1,100)`, `museumsvert (deltid,10,40)`, `kafemedarbeider (deltid,6,50)`, `sommervikar (sesong,6,100)`
  - `schema.sql` tabeller og kolonner (alle + `fiktiv`):
    - `ansatte(ansatt_id TEXT PK, fornavn, etternavn, jobb_epost, telefon)`
    - `ansettelser(ansettelse_id INTEGER PK, ansatt_id FK, rolle, stillingstype CHECK IN ('fast','deltid','sesong'), stillingsprosent INT, startdato, sluttdato NULL, leder_id NULL)`
    - `vakter(vakt_id INTEGER PK, ansatt_id FK, dato, start, slutt, stasjon CHECK IN ('sal','kafe','skranke'))`
    - `kurs(kurs_id INTEGER PK, ansatt_id FK, kurstype CHECK IN ('brannvern','hygiene','skjenking'), dato, gyldig_til)`
    - `fravaer_karantene(fravaer_id INTEGER PK, ansatt_id FK, fra, til, type CHECK IN ('karantene_ik_mat'))`
    - `kontakter(kontakt_id TEXT PK, fornavn, etternavn, epost, opprettet, nyhetsbrev_samtykke INT, samtykke_dato NULL, samtykke_kilde NULL CHECK IN ('nettside','kasse','arrangement'), trukket_dato NULL, siste_aktivitet)`
    - `arrangementer(arrangement_id TEXT PK, type CHECK IN ('omvisning','barnearrangement','verksted','foredrag','aaapning'), dato, maks_deltakere INT, pris_voksen REAL, pris_barn REAL)`
    - `pameldinger(pamelding_id INTEGER PK, arrangement_id FK, kontakt_id FK, antall_voksne INT, antall_barn INT, belop REAL, betalt INT, registrert)`
    - `skolebestillinger(bestilling_id INTEGER PK, skole, kontaktlaerer, jobb_epost, klassetrinn INT CHECK 1–13, antall_elever INT, dato)`
    - `utleie(foresporsel_id INTEGER PK, kundetype CHECK IN ('privat','bedrift'), kontaktperson, epost, firmanavn NULL, dato, status CHECK IN ('forespurt','bekreftet','avlyst','gjennomfoert'))`
    - `henvendelser(henvendelse_id INTEGER PK, tidspunkt, kanal CHECK IN ('cli','telegram','skranke'), fritekst, kategori, inneholder_persondata INT)`

- [ ] **Step 1: Skriv feilende tester** i `tests/test_persondata_schema.py`:
  - `test_schema_lager_alle_tabeller`: kjør `schema.sql` mot `sqlite3.connect(":memory:")`; settet av tabellnavn == de 11 over.
  - `test_alle_tabeller_har_fiktiv_kolonne`: `PRAGMA table_info` for hver tabell inneholder `fiktiv`.
  - `test_ingen_forbudte_kolonner`: ingen kolonnenavn matcher `fodselsnummer|fnr|adresse|kontonummer|lonn|kort|fodt|barn_navn`.
  - `test_lag_epost`: `lag_epost("Bjørg", "Åsen", 7) == "bjorg.aasen.7@eksempel.invalid"`.
  - `test_lag_telefon`: 1000 kall med `random.Random(1)` → alle matcher `^0\d{7}$`.
  - `test_gitignore_dekker_persondata_db`: `.gitignore` inneholder linjen `05_data/persondata/*.db`.
- [ ] **Step 2:** `py -3.13 -m pytest tests/test_persondata_schema.py -v` → FAIL (`ModuleNotFoundError`).
- [ ] **Step 3:** Implementer filene over. `README.md` starter med `> **FIKTIVE DATA.** Alle personer er oppdiktet.` og forklarer `py -3.13 -m pip install -e .` og genereringskommandoen fra Task 4.
- [ ] **Step 4:** Samme kommando → PASS.
- [ ] **Step 5:** Commit: `feat(persondata): skjema, konfig og avhengigheter`

---

### Task 2: Ansattgenerator (2010-01-01 → 2026-11-02)

**Files:**
- Create: `src/kunstpixel/persondata/ansatte.py`
- Test: `tests/test_persondata_ansatte.py`

**Interfaces:**
- Consumes: `config.ROLLER`, `ANSATTE_START`, `REFERANSEDATO`, `lag_epost`, `lag_telefon`
- Produces: `generer_ansatte(rng: random.Random, fake: Faker) -> dict[str, list[dict]]` med nøklene `"ansatte"`, `"ansettelser"`, `"vakter"`, `"kurs"`, `"fravaer_karantene"`; hver dict har nøyaktig kolonnene fra skjemaet unntatt `fiktiv`.

**Simuleringsregler (det testene ikke alene bestemmer):**
- Start: fyll alle plasser i `ROLLER` med startdato `ANSATTE_START`.
- Gå år for år. Årlig avgang: fast 8 %, deltid 35 %. Ved avgang: `sluttdato` tilfeldig i året, ny person ansettes 14–60 dager etter.
- Sommervikar: 6 ansettelser hvert år 15.06–15.08. 30 % sjanse for at en fjorårsvikar gjenbrukes (samme `ansatt_id`, ny rad i `ansettelser`).
- `leder_id`: museumsdirektørens `ansatt_id` på datoen for alle andre roller. Direktøren selv har `NULL`.
- Vakter: for `museumsvert`, `kafemedarbeider`, `sommervikar`. Åpent tirsdag–søndag. Per åpningsdag: 4 sal, 1 skranke, 2 kafé (3 sal + 1 kafé ekstra i juni–august, dekket av vikarer). Vakt 10:00–16:00 eller 11:00–17:00. Bare ansatte som er aktive på datoen.
- Kurs: `brannvern` for alle aktive i mars hvert år, `gyldig_til = _gyldig_til(dato, 1)`. `hygiene` for kafeleder/kafemedarbeider ved start, `gyldig_til = _gyldig_til(dato, 3)`. `skjenking` for kafeleder ved start, ingen utløp (`gyldig_til = NULL`).
- Fravær: 2–4 karantener per år blant kaféansatte, varighet 2–4 dager.
- Forventet volum (seed 2026): ca. 150–200 personer, ca. 35 000–45 000 vakter.

- [ ] **Step 1: Skriv feilende tester** (fixture: `generer_ansatte(random.Random(2026), Faker("no_NO"))` med `fake.seed_instance(2026)`, `scope="module"`):
  - `test_deterministisk`: to kjøringer med samme seed gir like resultater.
  - `test_ansettelser_innenfor_perioden`: alle `startdato >= "2010-01-01"`, alle `sluttdato` er `None` eller `<= "2026-11-02"`.
  - `test_ingen_overlappende_ansettelser_per_person`.
  - `test_bemanning_per_rolle_aldri_over_maks`: på 1. juli i hvert år 2010–2026 er antall aktive per rolle `<= antall_samtidig`, og totalt antall aktive er `>= 0.8 * sum(antall_samtidig)` (avganger gir midlertidige hull).
  - `test_vakter_kun_for_aktive_og_ikke_mandag`: hver vakt har en aktiv ansettelse den datoen, og `date.fromisoformat(dato).weekday() != 0`.
  - `test_vaktvolum`: `30_000 <= len(vakter) <= 50_000`.
  - `test_epost_og_telefon_fiktive`: alle e-poster slutter på `@eksempel.invalid`, matcher `^[a-z0-9.]+@`, og alle telefoner matcher `^0\d{7}$`.
  - `test_norske_tegn_bevart`: minst ett `fornavn` eller `etternavn` inneholder `[æøåÆØÅ]`.
  - `test_kurs_29_februar`: `_gyldig_til(date(2024, 2, 29), aar=3) == date(2027, 3, 1)` og `_gyldig_til(date(2024, 2, 29), aar=1) == date(2025, 2, 28)`.
  - `test_fravaer_kun_kafeansatte`.
- [ ] **Step 2:** `py -3.13 -m pytest tests/test_persondata_ansatte.py -v` → FAIL.
- [ ] **Step 3:** Implementer `generer_ansatte` og privat `_gyldig_til(dato: date, aar: int) -> date` = `dato + timedelta(days=round(aar * 365.25))` etter reglene over. Navn med `fake.first_name()` / `fake.last_name()`.
- [ ] **Step 4:** Samme kommando → PASS. Kjøretid < 30 s.
- [ ] **Step 5:** Commit: `feat(persondata): generator for ansatte 2010–2026`

---

### Task 3: Kundegenerator (2021-11-02 → 2026-11-02)

**Files:**
- Create: `src/kunstpixel/persondata/kunder.py`
- Test: `tests/test_persondata_kunder.py`

**Interfaces:**
- Consumes: `config.KUNDER_START`, `REFERANSEDATO`, `SKALAER`, `lag_epost`
- Produces: `generer_kunder(rng: random.Random, fake: Faker, faktor: float = 1.0) -> dict[str, list[dict]]` med nøklene `"kontakter"`, `"arrangementer"`, `"pameldinger"`, `"skolebestillinger"`, `"utleie"`, `"henvendelser"`.

**Volumer ved `faktor=1.0` (rund av med `round(n * faktor)`, minimum 1):**
| Tabell | Antall | Regler |
| :--- | :--- | :--- |
| `arrangementer` | 1 000 | Type og pris som i `museum.db`: omvisning 20 plasser / 50 kr, barnearrangement 15 / 0, verksted 12 / 150, foredrag 40 / 100, aaapning 100 / 0 (4 per år). `pris_barn` = 0 eller halv pris. |
| `kontakter` | 25 000 | `opprettet` jevnt i perioden. 40 % samtykker til nyhetsbrev; av dem trekker 10 % samtykket senere (`trukket_dato > samtykke_dato`). **Plantede brudd:** 2 % av de som har trukket samtykket har `siste_aktivitet` mer enn 3 år tilbake, og `epost` står fortsatt. |
| `pameldinger` | fylles per arrangement til 40–100 % av `maks_deltakere` | 1–4 voksne, 0–3 barn (barn bare på barnearrangement/verksted). `belop = voksne*pris_voksen + barn*pris_barn`. Bare kontakter med `opprettet <= arrangementsdato`. |
| `skolebestillinger` | 1 500 | Skole = `f"{fake.city()} skole"`. Klassetrinn 1–13, 15–30 elever. Dato på hverdager i skoleåret (ikke juli). |
| `utleie` | 300 | 60 % bedrift (`firmanavn = fake.company()`), 40 % privat (`firmanavn = None`). |
| `henvendelser` | 20 000 | Kategori fra FAQ-kategoriene i `museum.db` (`billett, praktisk, fasiliteter, formidling, tilgjengelighet, utleie, samling, butikk`). 5 % har `inneholder_persondata = 1`, med navn, fiktiv telefon eller e-post flettet inn i teksten (f.eks. «Jeg heter {navn}, mistet lommeboka i Sal C, ring {tlf}»). Minst 10 maler per kategori. |

- [ ] **Step 1: Skriv feilende tester** (fixture med `faktor=SKALAER["test"]`, plus én `@pytest.mark.slow`-test med `faktor=1.0`):
  - `test_alle_datoer_innenfor_kundeperioden`: alle dato-/tidspunktfelt i alle seks tabeller ligger mellom `"2021-11-02"` og `"2026-11-02T23:59"`.
  - `test_pameldinger_overstiger_aldri_kapasitet`: per arrangement er `sum(voksne+barn) <= maks_deltakere`.
  - `test_kontakt_opprettet_for_pamelding`.
  - `test_samtykkerekkefolge`: `trukket_dato` er `None` eller `> samtykke_dato`; `samtykke_dato` er `None` når `nyhetsbrev_samtykke == 0`.
  - `test_plantede_brudd_finnes`: minst én kontakt med `trukket_dato` satt, `epost` satt og `siste_aktivitet < "2023-11-02"`.
  - `test_henvendelser_persondata_andel`: andelen med `inneholder_persondata == 1` ligger mellom 0,03 og 0,07, og hver slik tekst inneholder et navn, `@eksempel.invalid` eller `0\d{7}`.
  - `test_henvendelser_uten_persondata_er_rene`: ingen tekst med `inneholder_persondata == 0` matcher `@|0\d{7}`.
  - `test_full_skala_volum` (slow): `len(kontakter) == 25_000`, `len(henvendelser) == 20_000`.
- [ ] **Step 2:** `py -3.13 -m pytest tests/test_persondata_kunder.py -v` → FAIL.
- [ ] **Step 3:** Implementer `generer_kunder` etter tabellen. Registrer markøren `slow` i `pyproject.toml` under `[tool.pytest.ini_options] markers`.
- [ ] **Step 4:** Samme kommando → PASS.
- [ ] **Step 5:** Commit: `feat(persondata): generator for kunder 2021–2026`

---

### Task 4: Bygg databasen (CLI)

**Files:**
- Create: `src/kunstpixel/persondata/generer.py`
- Test: `tests/test_persondata_generer.py`

**Interfaces:**
- Consumes: `generer_ansatte`, `generer_kunder`, `config.SCHEMA_STI`, `config.SKALAER`, `config.STANDARD_DB_STI`
- Produces:
  - `bygg_database(sti: Path, seed: int = 2026, skala: str = "full", overskriv: bool = False) -> dict[str, int]`, som returnerer tabell → antall rader.
  - CLI: `py -3.13 -m src.kunstpixel.persondata.generer [--sti STI] [--seed N] [--skala test|full] [--overskriv]`, som skriver en tabell med antall rader per tabell.
  - Faker-instansen opprettes inne i `bygg_database` med `Faker("no_NO")` og `seed_instance(seed)`. Ansatte og kunder får hver sin `random.Random(seed)` og `random.Random(seed + 1)`.

- [ ] **Step 1: Skriv feilende tester** (alle mot `tmp_path`):
  - `test_bygger_alle_tabeller`: `bygg_database(tmp_path/"p.db", skala="test")` gir 11 nøkler, alle `> 0`.
  - `test_nekter_overskriving`: andre kall uten `overskriv` gir `FileExistsError` med `"--overskriv"` i meldingen, og filens `mtime` er uendret.
  - `test_overskriv_flagg`: `overskriv=True` lykkes.
  - `test_deterministisk_innhold`: to bygg med samme seed i ulike filer gir lik `SELECT * ... ORDER BY 1` for hver tabell.
  - `test_ukjent_skala`: `skala="enorm"` gir `ValueError`.
  - `test_museum_db_uendret`: SHA-256 av `05_data/museum.db` er lik før og etter et bygg.
  - `test_fremmednokler_gyldige`: `PRAGMA foreign_key_check` gir ingen rader.
- [ ] **Step 2:** `py -3.13 -m pytest tests/test_persondata_generer.py -v` → FAIL.
- [ ] **Step 3:** Implementer. Bruk `executemany` innenfor én transaksjon, `PRAGMA foreign_keys = ON`, og opprett foreldermappen hvis den mangler.
- [ ] **Step 4:** Samme kommando → PASS. Kjør deretter `py -3.13 -m src.kunstpixel.persondata.generer`. Forventet: tabell med antall rader, kjøretid under 2 minutter, fil på ca. 10–30 MB. Noter faktiske tall i `05_data/persondata/README.md`.
- [ ] **Step 5:** `git status` skal **ikke** vise `persondata.db`. Commit: `feat(persondata): CLI for å bygge persondata.db`

---

### Task 5: Behandlingsprotokoll og slettesjekk

**Files:**
- Create: `05_data/persondata/behandlingsprotokoll.yaml`
- Create: `src/kunstpixel/persondata/slettesjekk.py`
- Test: `tests/test_persondata_slettesjekk.py`

**Interfaces:**
- Consumes: en `sqlite3.Connection` til persondata.db
- Produces:
  - `last_protokoll(sti: Path | None = None) -> dict`
  - `Brudd = NamedTuple("Brudd", [("tabell", str), ("antall", int), ("regel", str)])`
  - `finn_brudd(conn: sqlite3.Connection, protokoll: dict, referansedato: date) -> list[Brudd]`. En tabell uten regel gir `Brudd(tabell, -1, "mangler regel")`.
  - CLI: `py -3.13 -m src.kunstpixel.persondata.slettesjekk [--sti STI]`, som skriver en rapport.

**Protokollformat:** én nøkkel per tabell under `behandlinger:`, med feltene `formaal`, `rettslig_grunnlag` (artikkelhenvisning), `kategorier`, `saerlig_kategori` (bool), `tilgang` (liste med agentroller), `lagringsregler` (liste av `{felt: <kolonne>, dager: <int>, betingelse: <valgfri SQL-WHERE fra protokollfilen>}`; en post er et brudd hvis den treffer minst én regel) og `verifisert: false`. Øverst står `organisasjon: Kunstpixel` og `merknad: "Lagringstider er forslag og må verifiseres mot Datatilsynets veiledning."`

**Lagringsregler (forslag, alle `verifisert: false`):**
| Tabell | Regel |
| :--- | :--- |
| `ansatte` / `ansettelser` | `sluttdato` + 3 år (1 096 dager) |
| `vakter` | `dato` + 2 år (731) |
| `kurs` | `dato` + 5 år (1 827) |
| `fravaer_karantene` | `til` + 1 år (365), `saerlig_kategori: true`, `tilgang: [driftsansvarlig]` |
| `kontakter` | `trukket_dato` + 30 dager når `trukket_dato IS NOT NULL`, ellers `siste_aktivitet` + 3 år |
| `pameldinger` | `registrert` + 5 år (1 827) |
| `skolebestillinger` | `dato` + 3 år |
| `utleie` | `dato` + 5 år |
| `henvendelser` | `tidspunkt` + 1 år |
| `arrangementer` | ingen persondata: `lagringsregler: []`, `persondata: false` (teller ikke som «mangler regel») |

- [ ] **Step 1: Skriv feilende tester** (bygg en `skala="test"`-database i `tmp_path`, `scope="module"`):
  - `test_protokoll_dekker_alle_tabeller`: nøklene i protokollen == de 11 tabellene.
  - `test_protokoll_bruker_kunstpixel`: `organisasjon == "Kunstpixel"`.
  - `test_finner_brudd_i_generert_data`: `finn_brudd` gir `antall > 0` for `ansettelser` (fratrådt før 2023), `vakter` og `kontakter`.
  - `test_mangler_regel_rapporteres`: protokollen uten `henvendelser` gir `Brudd("henvendelser", -1, "mangler regel")`.
  - `test_tom_database`: kun skjema, ingen rader, gir `antall == 0` for alle regler og ingen unntak.
  - `test_betingelse_er_parameterisert`: `finn_brudd` aksepterer bare `betingelse` fra protokollfilen. Ingen verdier fra brukeren flettes inn.
- [ ] **Step 2:** `py -3.13 -m pytest tests/test_persondata_slettesjekk.py -v` → FAIL.
- [ ] **Step 3:** Implementer. Grensedatoen beregnes i Python (`referansedato - timedelta(days=dager)`) og sendes som `?`-parameter. Kolonne- og tabellnavn valideres mot `PRAGMA table_info` før de brukes i SQL.
- [ ] **Step 4:** Samme kommando → PASS.
- [ ] **Step 5:** Commit: `feat(persondata): behandlingsprotokoll og slettesjekk`

---

### Task 6: Skrivebeskyttet MCP-server for persondata

**Files:**
- Create: `src/kunstpixel/persondata/mcp_server.py`, `src/persondata_mcp.py`
- Test: `tests/test_persondata_mcp.py`

**Interfaces:**
- Consumes: `finn_brudd`, `last_protokoll`, `config.STANDARD_DB_STI` (kan overstyres med miljøvariabelen `KUNSTPIXEL_PERSONDATA_DB`)
- Produces: `FastMCP("Kunstpixel-persondata")` med nøyaktig disse verktøyene:
  - `tell_poster(tabell: str) -> dict`: `{"tabell", "antall"}`. Tabellen må finnes i protokollen og ikke være `fravaer_karantene`.
  - `statistikk_ansatte(aar: int) -> dict`: antall aktive per rolle 1. juli det året. Ingen navn.
  - `innsyn_kontakt(kontakt_id: str) -> dict`: øvelse på innsyn etter art. 15. Gir kontaktposten og kontaktens påmeldinger, eller `{"funnet": False}`.
  - `slettesjekk() -> list[dict]`: `finn_brudd` som en liste med dicts.
  - Tilkobling med `mode=ro` (samme mønster som `src/kunstpixel/core/db.py:get_db_connection`).

- [ ] **Step 1: Skriv feilende tester** (database fra `bygg_database` med `skala="test"` i `tmp_path`, satt via `monkeypatch.setenv`):
  - `test_verktoyliste`: de registrerte verktøyene er nøyaktig de fire over.
  - `test_tell_poster_avviser_fravaer`: `tell_poster("fravaer_karantene")` gir `PermissionError`.
  - `test_tell_poster_ukjent_tabell`: `tell_poster("sqlite_master")` gir `ValueError`.
  - `test_innsyn_ukjent_id`: `innsyn_kontakt("K999999")` gir `{"funnet": False}`.
  - `test_innsyn_injeksjon`: `innsyn_kontakt("K1' OR '1'='1")` gir `{"funnet": False}`.
  - `test_innsyn_kjent_id`: for den første `kontakt_id` i databasen gir den `funnet: True`, og alle påmeldinger har den samme `kontakt_id`.
  - `test_ingen_skriving`: et forsøk på `INSERT` via serverens tilkobling gir `sqlite3.OperationalError`.
  - `test_museum_mcp_vet_ikke_om_persondata`: ingen fil under `src/kunstpixel/core/` inneholder strengen `persondata`.
- [ ] **Step 2:** `py -3.13 -m pytest tests/test_persondata_mcp.py -v` → FAIL.
- [ ] **Step 3:** Implementer. `src/persondata_mcp.py` gjør bare `from src.kunstpixel.persondata.mcp_server import mcp; mcp.run()`.
- [ ] **Step 4:** Samme kommando → PASS. Kjør `py -3.13 src/persondata_mcp.py` manuelt. Forventet: prosessen starter og venter på stdio (avslutt med Ctrl+C).
- [ ] **Step 5:** Commit: `feat(persondata): skrivebeskyttet MCP-server`

---

### Task 7: Dokumentasjon og full verifisering

**Files:**
- Modify: `AGENTS.md`. Under §2 Database: legg til `05_data/persondata/persondata.db` (fiktiv, generert, ikke i git). Under Regel 1: presiser at regelen gjelder `museum.db` og at persondata.db bare skrives av generatorskriptet, aldri av agenter. Under §3: kommandoene for generer, slettesjekk og persondata-MCP.
- Modify: `04_knowledge/04_domain/operations/tool_access.md`. Ny tabell «Persondata (fiktiv)»: Driftsansvarlig → `statistikk_ansatte`, `slettesjekk`. Museumsdirektør → `tell_poster`, `statistikk_ansatte`. Museumsvert → ingen. Formidler, Kurator, Samlingsforvalter → ingen.
- Modify: `05_data/persondata/README.md`. Legg til faktiske volumer fra Task 4 og hvordan MCP-serveren kobles til Claude Desktop (oppføring i `claude_desktop_config.json` med `py -3.13` og full sti til `src/persondata_mcp.py`).
- Create: `05_data/persondata/ovelser.md` — 5 scenarioer, hvert med situasjon, hvilket MCP-verktøy/skript som brukes, og hva et godt svar inneholder: (1) innsynsbegjæring fra en kontakt (`innsyn_kontakt`, frist 1 måned, art. 12–15), (2) sletteforespørsel etter trukket samtykke (`slettesjekk`, art. 17), (3) tidligere ansatt fra 2012 ber om innsyn — hva burde vært slettet?, (4) avvik: vaktliste sendt til feil mottaker (72 timer, art. 33), (5) vask av `henvendelser` før bruk som treningsdata (`inneholder_persondata` er fasit).
- Modify: `01_inbox/2026-11-02_forslag_persondata_ansatte_kunder.md`. Sett status til «Besluttet 2026-11-02, se plan» og lenk til denne planen.

- [ ] **Step 1:** Gjør endringene over.
- [ ] **Step 2:** `py -3.13 -m pytest -v`. Forventet: alle eksisterende tester og alle nye persondata-tester består (slow inkludert).
- [ ] **Step 3:** `git status`. Forventet: ingen `.db`-filer er sporet.
- [ ] **Step 4:** Commit: `docs(persondata): AGENTS, tilgangsmatrise og README`
