# AGENT HANDOFF: Kontroller og legg Kunstpixel-dataene inn i datasjøen
*Timestamp: 2026-11-03 | Fra: Claude Code (sky) | Til: LLM som skal kontrollere dataene og ta dem inn i en datasjø | Eier: Lars*

Les dette først, deretter `docs/HANDOFF-2026-11-03.md` (hva som er gjort og hvorfor), `docs/DATAPIPELINE.md` (hvordan `museum.db` bygges) og `05_data/persondata/README.md` (kundedataene).

---

## 0. Oppdraget, og hva som ikke er avklart

1. **Kontroller** at dataene er komplette, konsistente og riktig merket (avsnitt 4). Rapporter funn, men ikke rett noe i stillhet.
2. **Ta dataene inn i datasjøen** (avsnitt 5).

> **Ikke avklart:** Repoet har ingen datasjø i dag. Plattform, format, lagdeling og tilgangsstyring er ikke bestemt. **Spør Lars før du velger.** Ikke gjett på skytjeneste eller konto. Forslaget til minimal løsning i avsnitt 5 er bare et utgangspunkt.

**Grein:** `claude/affectionate-einstein-1g8q56`, PR [Luaze1985/Kunstpixel#6](https://github.com/Luaze1985/Kunstpixel/pull/6) (utkast, base `hr-konsolidering`). Siste commit da dette ble skrevet: `06b3512`.

## 1. Låste beslutninger (fra Lars). Ikke endre dem.

- Virksomheten heter **Kunstpixel**.
- **`dagsbesok` er sannheten** for besøk. Årsoversikten og kundedataene er kalibrert mot den.
- **`hr_ansatte` er sannheten** for ansatte (168 personer, 2010–2026). Kundedata og HR/HMS-pakken refererer til de samme `ansatt_id`-ene.
- **Fase 1 har ingen tilgangssperrer, men all lesing er skrivebeskyttet.** Sperrer mellom datastedene kommer i fase 2.
- **Alt er syntetisk.** Ingen ekte personer skal inn.
- **Feil rettes i kilden** (CSV, YAML eller generator), aldri i en bygget database.

## 2. Hva som er kilde, og hva som er bygget

| Datasett | Kilde (rediger her) | Bygget fil (les herfra) | Byggekommando |
| :--- | :--- | :--- | :--- |
| Museum, HR, HMS, H5 | `05_data/kilde/museum_base.db` (frosset, rør aldri) og `05_data/*.csv` | `05_data/museum.db` (i git) og `05_data/museum.db.sha256` | `py -3.13 src/kunstpixel/data/build_museum_db.py` (bare Lars uten `--check`) |
| Årsoversikt (`h5_historikk_2010_2026`) | `_H` i `src/kunstpixel/core/intern/leveranse.py` | via `05_data/h5_historikk_2010_2026.csv` inn i `museum.db` | se fallgruver i `docs/HANDOFF-2026-11-03.md` §6 |
| Kundedata | `05_data/persondata/csv/*.csv` og `innstillinger.yaml` | `05_data/persondata/persondata.db` (ikke i git) | `py -3.13 -m src.kunstpixel.persondata.generer --fra-csv` |
| Feilmeldinger | `05_data/feilmeldinger/feilmeldinger.csv` | ingen | `py -3.13 scripts/meld_feil.py` |
| Governance-tekster | `05_data/governance/*.yaml` | delvis i `museum.db` (H5-tabellene) | `h5_governance_builder.py` |

**Fingeravtrykk ved overlevering.** Kontroller disse først. Hvis de ikke stemmer, har noen endret dataene etterpå.
- `05_data/museum.db`: sha256 begynner med `dae3d0cd7f163b62` (16,7 MB, 44 tabeller).
- `05_data/persondata/persondata.db`, bygget med `--fra-csv`: sha256 begynner med `4186666f4d1de18e` (4,6 MB, 14 tabeller, 49 513 rader). Fila skal være byte-identisk når den bygges fra de committede CSV-ene. Hvis den ikke er det, sammenligner du innholdet tabell for tabell i stedet.

## 3. Datakatalog

### 3a. `museum.db` (44 tabeller)

| Domene | Tabeller (rader) | Nøkkel og koblinger |
| :--- | :--- | :--- |
| Samling | `verk` (16), `kunstnere` (12), `saler` (6), `utstillinger` (3), `utstilling_verk` (15), `utstillinger_historikk` (103), `utstilling_okonomi` (102), `utstillingsinnlan` (50), `tilstandsrapporter` (16) | `verk.kunstner_id` → `kunstnere.id`. `sal_id` → `saler.id` |
| Publikum | `dagsbesok` (6 209 dager, 2010–2026), `hendelser` (45, 2026-09 til 2026-12), `publikum_faq` (12) | `dagsbesok.dato` (ISO) |
| HR | `hr_ansatte` (168), `hr_vakter` (54 258), `hr_fravaer` (3 456), `hr_innleie` (318), `org_ansatt_kompetanse` (596), `org_ferdigheter` (14), `hr_opplaering_onboarding` (18), `personas` (28), `hr_people` (12), `hr_person_skill` (30), `hr_skills` (7), `hr_availability` (11), `hr_rules` (8), `roller` (12), `rolle_sporsmal` (11) | `ansatt_id` = `KP-ANS-NNN`. `hr_people.ansatt_id` → `hr_ansatte` |
| HMS og drift | `avvik_hms_drift` (34), `hms_avvik_tekst` (40), `hms_ergonomi_rotasjon` (9), `arbeidstilsynet_renhold` (7), `arbeidstid_grenser` (6), `interne_henvendelser` (60) | |
| Styring (H5) | `h5_historikk_2010_2026` (17), `h5_myndighetskontakter` (8), `h5_rapporteringskalender` (12), `h5_rapportmaler` (21), `h5_tilsynsbesok_rutine` (6), `h5_arbeidsoppgaver_tidsbruk` (19), `rapport_regler` (22) | `h5_historikk.ar` |
| Referanse | `norske_helligdager` (237), `ssb_sykefraver_kultur` (68), `styrk08_katalog` (10), `virke_tariff` (67), `leverandor_enhetsregister` (12), `handbok_oppslag` (99) | |

### 3b. `persondata.db` (14 tabeller, alle med `datakilde = syntetisk (persondata_generator)`)

| Tabell (rader) | Nøkkel | Koblinger |
| :--- | :--- | :--- |
| `kontakter` (5 098) | `kontakt_id` `K000001`… | `ansatt_id` → `museum.hr_ansatte` (98 ansatte er også kunder) |
| `medlemskap` (4 920), `medlemsbesok` (16 060), `fordel_bruk` (5 997) | `medlemskap_id` | `kontakt_id`, `type` → `medlemskapstyper`, `solgt_av_ansatt_id` → `hr_ansatte` |
| `medlemskapstyper` (6), `fordeler` (8), `medlemskapstype_fordel` (26) | katalog | |
| `gavekort` (1 501), `gavekort_bruk` (2 329) | `gavekort_id`, `kode` `GK-XXXX-XXXX` | `kjoper_kontakt_id`, `mottaker_kontakt_id`, `solgt_av_ansatt_id` |
| `arrangementer` (760), `pameldinger` (5 430) | `arrangement_id` `ARR-NNNNN` eller `MDB-<id>` | `MDB-<id>` → `museum.hendelser.id`. `ansvarlig_ansatt_id` |
| `skolebestillinger` (4 278), `utleie` (100), `henvendelser` (3 000) | løpenummer | `ansvarlig_ansatt_id` / `besvart_av_ansatt_id`, `henvendelser.kontakt_id` |

**Persondata, selv om alt er syntetisk:**
- `kontakter`: navn, e-post (`@eksempel.invalid`) og telefon (`0` + 7 siffer).
- `henvendelser.fritekst`: 5 % inneholder navn, telefon eller e-post (`inneholder_persondata = 1`).
- `hr_ansatte`: fødselsår, lønnstrinn, e-post `@kunstpixel.no` og telefon med 7 siffer etter +47 (ugyldig nummer).
- `hr_fravaer`: helseopplysninger, særlig kategori.

## 4. Kontrollsjekkliste (kjør i denne rekkefølgen og rapporter hvert punkt)

Kjør alt fra rotmappa i repoet.

| # | Kontroll | Kommando | Forventet |
| :--- | :--- | :--- | :--- |
| K1 | Fingeravtrykk | `python -c "import hashlib;print(hashlib.sha256(open('05_data/museum.db','rb').read()).hexdigest())"` | begynner med `dae3d0cd7f163b62` |
| K2 | `museum.db` bygget fra gjeldende kilder | `py -3.13 src/kunstpixel/data/build_museum_db.py --check` | LIK |
| K3 | Statusport | `py -3.13 scripts/db_status_gate.py` | KLAR. I skymiljøet blokkerer den bare på 2 tester som trenger pakken `anthropic` |
| K4 | Datakvalitet | `py -3.13 scripts/db_kvalitet.py` | 0 FEIL. Kjent OBS: 1 287 vakter over 9 timer er ikke merket som overtid |
| K5 | Hele testpakken | `py -3.13 -m pytest` | 1726 bestått. Bare de 2 `anthropic`-testene kan feile |
| K6 | Kundedata bygges | `py -3.13 -m src.kunstpixel.persondata.generer --fra-csv` | 49 513 rader |
| K8 | Alle koblinger mellom datalagene (A: nøkler, B: samsvar) | `py -3.13 scripts/koblingssjekk.py --vis-kjente` | 41 OK, 0 FEIL. Kontrollene står i `src/kunstpixel/data/koblinger.py` |
| K7 | Kryssjekker | SQL under, mot `persondata.db` med `museum.db` koblet på som `museum` | alle gir 0 rader eller angitt verdi |

```sql
-- K7a: årsoversikten stemmer med dagsbesøket (forventet 0 rader)
SELECT h.ar FROM museum.h5_historikk_2010_2026 h
JOIN (SELECT aar, SUM(besok_totalt) b FROM museum.dagsbesok GROUP BY aar) d ON d.aar = h.ar
WHERE h.besok_totalt <> d.b;

-- K7b: alle ansattreferanser peker på en ansatt som var i jobb (forventet 0, eksempel for gavekort)
SELECT g.gavekort_id FROM gavekort g JOIN museum.hr_ansatte a ON a.ansatt_id = g.solgt_av_ansatt_id
WHERE a.ansatt_fra > g.utstedt OR (a.ansatt_til IS NOT NULL AND a.ansatt_til < g.utstedt);

-- K7c: ansatte som kunder har samme navn som i hr_ansatte (forventet 0)
SELECT k.kontakt_id FROM kontakter k JOIN museum.hr_ansatte a USING (ansatt_id)
WHERE k.fornavn || ' ' || k.etternavn <> a.navn;

-- K7d: gavekortsaldo aldri negativ (forventet 0)
SELECT g.gavekort_id FROM gavekort g JOIN gavekort_bruk b USING (gavekort_id)
GROUP BY g.gavekort_id HAVING SUM(b.belop) > g.belop + 0.001;

-- K7e: ingen kundeaktivitet på stengte dager (forventet 0)
SELECT m.besok_id FROM medlemsbesok m JOIN museum.dagsbesok d ON d.dato = m.dato WHERE d.er_aapent = 0;

-- K7f: ingen kunde-e-post utenfor det reserverte domenet (forventet 0)
SELECT kontakt_id FROM kontakter WHERE ansatt_id IS NULL AND epost NOT LIKE '%@eksempel.invalid';
```

## 5. Inn i datasjøen: regler og forslag

**Regler (gjelder uansett plattform):**
1. **Les, ikke skriv.** Åpne begge databasene med `mode=ro`. Datasjøen er en kopi, ikke en ny kilde. Endringer går tilbake via kildefilene og et nytt bygg.
2. **Ta med opphav på hver tabell:** kildefil, byggekommando, sha256 for databasen, commit og tidspunkt for innlasting.
3. **Klassifisering:**
   - Datapolicyen i repoet (`src/kunstpixel/core/datapolicy.py`) godtar bare `syntetisk` eller `syntetisk (<kilde>)`. **Alt annet regnes som ekte (fail-closed).**
   - **29 av 44 tabeller i `museum.db` mangler kolonnen `datakilde`** og blir derfor tolket som ekte.
   - Ikke merk dem som syntetiske på eget initiativ. Foreslå regelen («alt i `museum.db` er syntetisk med mindre annet er oppgitt») for Lars, og vent på et ja.
4. **Persondata og hosting:**
   - `deploy/demo/Dockerfile` kopierer hele `museum.db` til en VPS. Kundedataene ligger derfor med vilje i en egen `persondata.db`.
   - Ikke slå dem sammen i én fil som kan ende i demoen.
   - Merk tabellene med persondata (avsnitt 3b) og `hr_fravaer` (helse) i datasjøen, selv om fase 1 ikke har sperrer.
5. **Bruk nøklene, ikke navn.** Seks personer i `hr_ansatte` har samme navn som en annen ansatt, og noen kunder har samme navn som en ansatt.
6. **Datoer er ISO-tekst** (`YYYY-MM-DD`, `henvendelser.tidspunkt` er `YYYY-MM-DDTHH:MM`). Konverter til datotype i datasjøen og avvis rader som ikke lar seg tolke.

**Forslag til minimal løsning (avklar med Lars først):** én mappe per kilde og én fil per tabell.
- **Mappe:** `datasjo/<kilde>/<tabell>.parquet`. Parquet fordi formatet tar vare på datatypene. Repoet har allerede Parquet-filer i `05_data/`, men `pyarrow` står ikke i `pyproject.toml` og må legges til som avhengighet.
- **Manifest:** `datasjo/manifest.json` med rader, kolonner, nøkkel, klassifisering og opphav per tabell.
- **Innlasting:** et innlastingsskript som er idempotent og nekter å overskrive uten `--overskriv`, samme mønster som `generer.py`.
- **Tester:** kontrollene i K7 kjøres som tester mot datasjøen etterpå.

## 6. Kjente avvik (rapporter, ikke rett i stillhet)

- **De 8 avvikene koblingssjekken fant (B18–B25) er rettet 2026-11-03** i `build_museum_db.rett_koblingsavvik`, `org_builder.py` og `hr_demo/seed.json`. Se avsnitt 9.

- `h5_historikk`: billettinntekt avviker under 2 % fra `dagsbesok`, med vilje, fordi snittprisen aldri faller.
- `dagsbesok` har tall til og med 2026-12-31, altså i fremtiden. `hendelser` har 30 hendelser etter 2026-11-02, og 5 av dem ligger på dager `dagsbesok` sier er stengt.
- `hr_ansatte` har to ansettelser som starter i desember 2026.
- 1 287 vakter er over 9 timer uten å være merket som overtid (K4).
- `faker` har ingen øvre versjonsgrense. CSV-ene er sannheten for kundedataene, så det påvirker ikke `--fra-csv`.
- Eksisterende skript (`tests/test_org_builder.py` og `h5_governance_builder.eksporter_csv_filer()`) skriver om CSV-filer med CRLF. Tilbakestill med `git checkout` før du committer.

## 7. Når du finner en feil

- **Ikke rett i databasen eller datasjøen.**
- Skriv funnet i kontrollrapporten med tabell, ID, felt, verdien du så, hva du forventet og spørringen som viste det.
- Lars, eller en ansatt han utpeker, registrerer feilen i `05_data/feilmeldinger/feilmeldinger.csv` via `py -3.13 scripts/meld_feil.py`. Mekanismen krever at den som melder, er en ansatt i jobb, så en LLM skal ikke melde i en ansatts navn.
- Retting skjer i kilden, og databasen bygges på nytt. Følg `AGENTS.md` Regel 1b.

## 8. Forventet leveranse fra deg

1. **`docs/KONTROLLRAPPORT-DATASJO-<dato>.md`** med resultatet av K1–K7, funn med bevis, og hva som er kontrollert og hva som ikke er det.
2. **Et forslag til datasjø**: plattform, format, lag og klassifiseringsregel, lagt fram for Lars før du bygger noe.
3. **Etter et ja:** innlastingsskript, manifest og tester, på egen grein med egen PR. Ingen sammenslåing uten Lars.

## 9. Rettinger 2026-11-03 (koblingssjekk B18–B25)

| # | Retting | Hvor |
| :--- | :--- | :--- |
| B25 | 5 hendelser på stengte mandager er flyttet til neste åpne dag | `rett_koblingsavvik` |
| B24 | Arkivets høst 2026 følger det kuraterte programmet: «Stille kraft» (KP-EXH-2026-068) og «Lys innenfra» (ny, KP-EXH-2026-069). Besøk og budsjett er delt 2/3 og 1/3, så årssummen er uendret | `rett_koblingsavvik` |
| B18 | 736 publikumsvakter på stengte dager er fjernet: 54 994 → 54 258 vakter i databasen. Kildefila `arkiv_hr_vakt_historikk.csv` er uendret | `rett_koblingsavvik` |
| B19 | Vaktenes `utstilling_id` er utstillingen som gikk den dagen (hovedutstilling foran fokusrom), ellers tom. 6 952 vakter i monteringsuker har tom kobling | `rett_koblingsavvik` |
| B21 / B22 | Godkjenner og ansvarlig som ikke var i jobb, er byttet med den lengst ansatte i samme stilling (ellers avdeling) | `rett_koblingsavvik` |
| B20 | Interne saker meldes bare av ansatte som er i jobb på datoen | `org_builder.generate_internal_requests` |
| B23 | Navnene i HR-demoen er de samme som i `hr_ansatte` (E101 Ada Nord → Jonas Berg osv.) | `05_data/hr_demo/seed.json` |

Fasiten (`tests/golden/regelbasert/golden.json`) er laget på nytt med `tests/make_golden.py`. Bare datoene til de flyttede hendelsene er endret.
