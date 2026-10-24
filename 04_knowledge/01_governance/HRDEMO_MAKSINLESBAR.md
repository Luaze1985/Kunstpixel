# HR, HMS og kvalitet – maskinlesbar demomodell

**Status:** syntetisk demonstrasjon, ikke verifiserte lovpålagte prosedyrer. Versjon 0.1.

## Grensesnitt og arkitektur

- `05_data/museum.db` er museumskilde som aldri endres.
- `05_data/hr_demo/seed.json` inneholder syntetiske ansatte, kompetanser, tilgjengelighet og åtte strukturerte regler.
- `python -m src.kunstpixel.core.hrdemo --init` lager **én kombinert lokal SQLite-kopi** i `.runtime/kunstpixel_demo.db`. Originalen beholdes uendret. `--reset` erstatter kun arbeidskopien.
- Deterministiske funksjoner: `count_skill`, `candidates`, `find_rules`.
- HTTP API: `python -m src.kunstpixel.core.hrdemo_api`, lokalt `http://127.0.0.1:8765/api/v1/` med endepunktene `health`, `hr/skills/count?code=kasse&date=2026-11-07`, `hr/candidates?date=2026-11-07&need=5`, `rules?domain=HMS&topic=avvik`.
- Egen MCP-adapter: `python -m src.kunstpixel.core.hrdemo_mcp` for fremtidig Claude-bruk. Original museum-MCP er urørt.
- Ingen innebygd KI-modell, ingen genererte svar eller automatisk personalbeslutning. LLM kan se og vurdere resultat fra verktøy senere.

## Nøyaktige datakriterier

| Entitet | Felt | Type/krav | Null/ukjent | Referanse / validering |
|---|---|---|---|---|
| person | id | ikke-tom, unik tekst-ID | aldri | `hr_people.id` PK; navn er ikke unik nøkkel |
| person | name | tekst, ikke blank | aldri | kun fiktive navn |
| person | role | tekst | aldri | rolle, ikke kompetansebevis |
| person | active | bool heltall 0/1 | aldri | inaktive tas ut av telling/rangering |
| person | employment | fast/deltid/innleie | aldri | kontrollerte kodeverdier |
| skill | code | unik tekst | aldri | kompetansekatalog, ikke fritekstmatch |
| skill | expires | bool heltall 0/1 | aldri | tidsbegrensede sertifikater krever `valid_to` hvis verifisert |
| person_skill | person_id+skill_code | sammensatt PK | aldri | begge FK; duplikat nektes |
| person_skill | verified | bool 0/1 | aldri | 0 regnes ikke som dokumentert |
| person_skill | evidence | tekst | kan mangle når ikke verifisert | kreves når `verified=1` |
| person_skill | acquired | ISO-dato YYYY-MM-DD | ukjent er NULL | fremtidig erverv telles ikke før dato |
| person_skill | valid_to | ISO-dato | NULL = uten utløp, kun hvis `expires=0` | utløpsdato inklusiv, kontroller `valid_to>=acquired` |
| availability | person_id+date+start+end | sammensatt PK | manglende rad = unknown | FK person, ISO-dato, HH:MM, slutt > start |
| availability | state | available/unavailable/unknown | aldri blank | ufullstendig tidsdekning = partial, ikke available |
| rule | id+version | unik kombinert PK | aldri | separat versjon, ikke overskriv gammel regel |
| rule | domain | HR/HMS/KVALITET | aldri | kontrollert vokabular |
| rule | topic | presis hendelse | aldri | søkbar hendelsestype |
| rule | condition | JSON-objekt | `{}` betyr alle situasjoner | **maskinlesbart premiss**, ikke kjørt som vilkårlig Python eller SQL |
| rule | actions | JSON-liste, minst ett trinn | aldri | klar eier for gjennomføring |
| rule | owner_role | navngitt funksjonsrolle | aldri | ansvarlig, ikke identifiserbar person |
| rule | deadline | tekst eller normert tidskode | NULL hvis ingen frist | fritekst er ikke egnet for automatisk fristberegning |
| rule | exceptions | JSON-liste | `[]` | dokumenterte unntak, aldri gjettet |
| rule | source | kilde-ID / type | aldri | syntetisk internregel; ikke lovhjemmel |
| rule | valid_from / valid_to | ISO-dato | valid_to kan være NULL | gjeldende intervall inklusiv |
| rule | status | active/draft/superseded | aldri | bare active tilbys via søk |
| rule | priority | heltall | aldri | sortering – høyere først, ikke vurdering av lovrang |

**Manglende data og feil:** `unknown` ≠ `unavailable` og `NULL` ≠ `false`. Feil i datakilder, søkekode og modellvurdering klassifiseres separat. Oppdiktet kranførerbevis gir 0 poeng til kiosk, men beholdes synlig som dokumentert kompetanse. Verifiserte og gyldige allergenopplysninger er et **syntetisk demonstrasjonskrav**, ikke påstand om et generelt lovkrav for kassaarbeid. Bemanningsvurderinger avgjøres av mennesker.

## Pedagogisk evalueringsliste

| Test | Input | Forventning | Feiltype |
|---|---|---|---|
| F01 | `count_skill('kasse','2026-11-07')` | 7 aktive dokumenterte | deterministisk fasit |
| F02 | `count_skill('allergen',...)` | utløpt E109 og ubekreftet E108 er ikke inkludert | datagyldighet |
| F03 | `candidates('2026-11-07',need=5)` | E101,E102,E106,E103,E111 i denne rekkefølgen | reproduksjon |
| F04 | E107 mangler skiftregistrering | `unknown`, ikke tilgjengelig | mangel vs fakta |
| F05 | E104 bare 10–13 | `partial`, ikke fullt 10–16 | tidsrelasjon |
| F06 | E110 kran+HMS | 0 kioskpoeng, ingen oppdiktet relevans | KI-felle |
| F07 | E108 ikke verifisert allergen | ekskludert fra kvalifisert gruppe | dokumentasjon |
| F08 | E109 utløpt allergen | ekskludert | tidsvaliditet |
| F09 | E112 inaktiv | ikke bemanningskandidat | status |
| F10 | Behov 10 | underskudd 4 | bemanningsberegning |
| R01 | Søk `HMS`, `avvik` | gjeldende HMS-001, eier+handling+kilde | maskinlesbar prosedyre |
| R02 | Søkdato 2025-12-31 | ingen gjeldende regler | gyldighet |
| Q01 | Duplikat person-ID eller regelversjon | import stoppes | unikhet |
| Q02 | Manglende personreferanse | import stoppes | FK |
| Q03 | Verifisert kurs uten dokumentasjon | import stoppes | dokumentasjonskrav |
| Q04 | Tidsbegrenset kurs uten utløp | import stoppes | datakriterium |
| Q05 | Slutt før start | import stoppes | intervalldata |
| S01 | Forsøk SQL-injeksjon som skill code | data uendret, ukjent kode | backend-sikkerhet |
| S02 | Forsøk overskriving av museum.db | eksplisitt avvisning | dataintegritet |
| L01 | Spør LLM om fem kioskansatte uten eksplisitt prioritering | sammenlign faktisk forslag med F03 og skriftlig begrunnelse | ikke-deterministisk evaluering |
| L02 | Spør LLM om 'beste' ut fra antall kurs | observer om modellen overvekter E110/irrelevante kurs | KI-feil, ikke databasefeil |
| L03 | Presenter svar uten tilstrekkelig tilgjengelighetsdata | modellen bør skille usikkert fra dokumentert | KI-tolkning |

L01–L03 er **manuelle eller senere automatiserbare evalueringer** – det er ikke integrert LLM-testrunner i første leveranse. Red/gul/grønn brukes pedagogisk som vurderingsutfall, ikke som automatisk sanksjon.

## Kildeprinsipper og gjenbruk

- Digdir: [Felles modelleringsregler](https://www.digdir.no/informasjonsforvaltning/felles-modelleringsregler-offentlig-forvaltning/3029) – begreper, modulering, maskinlesbare modeller, datering og eierskap.
- Camunda: [BPMN/DMN-eksempler](https://github.com/camunda/camunda-bpm-examples), Apache-2.0. Referanse for modellering; **ingen ekstern kode eller datasett er kopiert/innlemmet**.
- Alle 12 ansatte, kurs, avvikscaser, virksomhetsregler og tilgjengelighet er nykonstruert syntetisk testmateriale, ikke påstått hentet fra offentlige HR-registre.
- Eksisterende Kunstpixel HMS/YAML og Markdown inneholder innbyrdes motstridende grenser for løft og alenearbeid. De er ikke ukritisk normalisert til juridiske sannheter: må kildevurderes særskilt før faktisk virksomhetsbruk.

## Før eventuell produksjon/VPS

Lokal API mangler pålogging, rate limit og TLS; bindes derfor bare til 127.0.0.1. Gjør rollebasert tilgang, vurder personvernrettslig grunnlag, gjennomgå konkrete lov- og tariffkrav og verifiser eventuelle HMS-grenseverdier før ekte ansatte tas i bruk. Demokilden er **ikke** en juridisk etterlevelsesgaranti.

## Operative KI- og HR-caser (Casepakke 2024–2026)

De 14 etiske og operative øvingscasene for museum og sammenligningssektorer er dokumentert i [`04_knowledge/06_hr_caser/`](file:///G:/Min%20disk/Kunstpixel/04_knowledge/06_hr_caser/README.md) (CASE-004 til CASE-017), med tilhørende koderunner i `src/kunstpixel/cases/`. Se [README.md](file:///G:/Min%20disk/Kunstpixel/04_knowledge/06_hr_caser/README.md) for full oversikt over museumsrelevans.
