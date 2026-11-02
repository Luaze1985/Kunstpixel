# Inspeksjon: er kundedataene klare for å integreres med resten?

**Dato:** 2026-11-02
**Gjelder:** `05_data/persondata/persondata.db` (39 880 rader) mot `05_data/museum.db` (greina `hr-konsolidering`)
**Konklusjon:** Kundedataene er **klare til bruk ved siden av `museum.db`**: de kan kobles på, slås sammen i spørringer, og MCP fungerer. De er **ikke klare til å bygges inn i `museum.db`**. Det stopper på én motsetning i `museum.db` selv, fire kalibreringsfeil i kundedataene og ett sikkerhetspunkt.

---

## 1. Det som holder (kontrollert)

| Sjekk | Resultat |
| :--- | :--- |
| Ansatte som kunder | Alle 98 ansatte som var aktive i perioden har en kontakt. Navn og e-post er like som i `hr_ansatte` |
| Ansattreferanser | Alle peker på en ansatt som var i jobb den datoen |
| ID-kollisjoner med museum.db | Ingen (`K000001`, `ARR-00001`, `GK-…` finnes ikke der) |
| Tabellnavn | Ingen kolliderer med `museum.db` |
| Fiktive kontaktdata | 0 kunde-e-poster utenfor `@eksempel.invalid` |
| Merking | Alle rader har `datakilde = syntetisk (persondata_generator)`, godkjent av `datapolicy.py` |
| Medlemsinntekt | ca. 550 000 kr/år. Det passer med `andre_inntekter_tkr` i H5 (480–690) |
| Medlemsbesøk | 2–3 % av dagsbesøket, bare på åpne dager |

## 2. Blokkerer: `museum.db` er uenig med seg selv (fakta)

To tabeller i `museum.db` gir svært ulike besøkstall for de samme årene:

| År | `h5_historikk_2010_2026.besok_totalt` | `dagsbesok` (sum) | `utstillinger_historikk` (sum) | Billettinntekt H5 | Billettinntekt `dagsbesok` |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 2022 | 31 200 | 147 507 | 147 507 | 1,5 mill. | 10,1 mill. |
| 2024 | 37 900 | 145 156 | 145 156 | 2,1 mill. | 11,6 mill. |
| 2026 | 41 200 | 120 586* | 120 586* | 2,5 mill. | 9,7 mill. |

\* `dagsbesok` har tall til og med 2026-12-31.

Forskjellen er omtrent fire ganger. Kundedataene er laget ut fra `dagsbesok`. **Dette er ikke en feil i kundedataene, men alt som skal integreres trenger én sannhet. Det må eieren bestemme.**

## 3. Kalibreringsfeil i kundedataene (vurdering, kan rettes)

| # | Funn | Nå | Bør være (ut fra H5) |
| :--- | :--- | :--- | :--- |
| K1 | Arrangementer per år | 46–75 | 31–43 (`arrangementer_antall`) |
| K2 | Skoleelever per år | 2 000–2 800 | 4 300–5 900 (`skoleelever`) |
| K3 | Medlemsmassen starter på null i november 2021. Den bygger seg opp gjennom 2022 og har bare 542 aktive 1. juli 2022 | Synlig hakk i trendene | Ca. 800 aktive fra første dag |
| K4 | Gavekort brukt på «billett» med opptil 1 000 kr per gang | Snitt 222 kr | En billett koster 100–120 kr |
| K5 | Henvendelser jevnt fordelt på kategorier (ca. 300 hver) | Jevnt | Vektet etter `publikum_faq.hyppighet` (praktisk og samling oftest, utleie sjeldent) |

Mindre ting:
- 29 kunder har samme navn som en ansatt. Det er realistisk, men alle koblinger må gå på ID, aldri på navn.
- 30 kommende arrangementer i `hendelser` (etter 2026-11-02) har ingen forhåndspåmeldinger.
- 5 av arrangementene fra `museum.db` ligger på dager `dagsbesok` sier er stengt. Feilen ligger i `museum.db`.

## 4. Integrasjon i `museum.db`: hva som må til (fakta om repoet)

Konvensjonen i `docs/DATAPIPELINE.md` og `build_museum_db.py`:
1. CSV-ene skal ligge i `05_data/`, kommadelt og UTF-8. Kundedataene bruker nå semikolon og BOM i `05_data/persondata/csv/`.
2. Hver tabell trenger et `bygg_*`-trinn i `build_museum_db.py`, og `SKJEMAVERSJON` må gå fra 5 til 6.
3. Filene må med i `CSV_FILER`-vakta (`tests/test_data_csv.py`), og bygget må gjennom `scripts/db_status_gate.py`.
4. Bare Lars kjører bygget uten `--check`.

## 5. Sikkerhetspunkt (vurdering)

`deploy/demo/Dockerfile` kopierer **hele `museum.db`** inn i demobildet som hostes på en VPS. Datafinner viser bare hvitelistede verktøy, men fila ligger likevel på serveren. Legger vi kundedataene inn i `museum.db`, blir de med dit. De er fiktive, men det strider mot «ingen sperrer nå, sperrer i fase 2»: integrasjonen ville gjort valget for fase 2 på forhånd.

## 6. Anbefaling

| Steg | Hva | Hvem |
| :--- | :--- | :--- |
| 1 | Velg hvilket besøkstall som er sannheten: H5 (ca. 40 000/år) eller `dagsbesok` (ca. 145 000/år) | Eier |
| 2 | Rett K1–K5 slik at kundedataene følger den valgte sannheten | Claude |
| 3 | **Integrer ved å koble på, ikke ved å bygge inn:** hold `persondata.db` adskilt, og koble den på `museum.db` skrivebeskyttet i spørringer, slik MCP-en gjør nå. Da blir kundedataene ikke med i demobildet | Claude |
| 4 | Bygg inn i `museum.db` (punkt 4) først hvis dere bestemmer at kundedata skal ligge der, etter at sperrene i fase 2 er bestemt | Eier + Lars |
