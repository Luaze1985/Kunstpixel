# Maskinlesbar HR-, HMS- og kvalitetsdemo for Kunstpixel

**Status:** Fiktiv undervisningsmodell. Alle personer og rutiner er syntetiske; dette er ikke juridisk kvalitetssikrede myndighetskrav.

## Teknisk arkitektur

Kunstpixels eksisterende `05_data/museum.db` beholdes uendret og åpnes skrivebeskyttet. `src/kunstpixel/core/hrdemo.py` tar en SQLite-backup til .runtime/kunstpixel_demo.db`, legger til `hr_`-tabeller og fyller dem fra `05_data/hr_demo/seed.json`. Deretter benytter både lokal HTTP-API og egen MCP-server de samme deterministiske funksjonene. Originalens museum-MCP og tester endres ikke. `--reset` nullstiller bare arbeidskopien.

Kjør fra repo-roten:

~~~sh
python -m src.kunstpixel.core.hrdemo --init
python -m src.kunstpixel.core.hrdemo --report kiosk
python -m src.kunstpixel.core.hrdemo --report count
python -m src.kunstpixel.core.hrdemo --report rules
python -m src.kunstpixel.core.hrdemo_api
python -m pytest tests/test_hrdemo.py -q
~~~

API er **kun lokalt** på 127.0.0.1:8765 (ikke VPS/produksjon uten autentisering). Endepunkter:

- GET /api/v1/hr/skills/count?code=kasse&date=2026-11-07
- GET /api/v1/hr/candidates?date=2026-11-07&start=10:00&end=16:00&need=5
- GET /api/v1/rules?domain=HMS&topic=avvik&date=2026-11-07
- GET /api/v1/health

Claude-integrasjon senere kan bruke `python -m src.kunstpixel.core.hrdemo_mcp` via stdio.

## Datakontrakt (faktiske, testbare krav)

| Entitet | Primærnøkkel / felt | Datatype | Fravær / kontroll |
|---|---|---|---|
| hr_people | id | unik ikke-tom tekst | ikke NULL; aldri bruk navn som nøkkel |
| hr_people | name, role | ikke-tom tekst | fiktive data, ikke personalopplysninger |
| hr_people | active | 0 eller 1 | inaktiv ekskluderes fra telleverdi og forslag |
| hr_people | employment | fast/deltid/innleie | kontrollert kodeverk |
| hr_skills | code | unik kode | tekst/navn adskilt fra kode |
| hr_skills | expires | 0 eller 1 | styrer krav om gyldighetsdato |
| hr_person_skill | (person_id,skill_code) | sammensatt nøkkel og to fremmednøkler | dublett/ukjent person/kompetanse avvises |
| hr_person_skill | verified | 0 eller 1 | 0 betyr ikke dokumentert |
| hr_person_skill | evidence | kildebevis, tekst | påkrevd ved verified=1 |
| hr_person_skill | acquired | ISO 8601-dato | NULL ukjent; fremtidig dato telles ikke |
| hr_person_skill | valid_to | ISO 8601-dato | kreves for dokumenterte tidsbegrensede kurs; sluttdato inklusiv |
| hr_availability | person_id,date,start,end | sammensatt nøkkel | manglende rad = unknown, ikke available |
| hr_availability | state | available/unavailable/unknown | tidsrom skal dekke hele skiftet |
| hr_rules | id,version | sammensatt nøkkel, versjon > 0 | tidligere versjoner overskrives ikke |
| hr_rules | domain | HR/HMS/KVALITET | kontrollert kodeverk |
| hr_rules | topic | hendelse/utløser | søkbar, fagspesifikk |
| hr_rules | condition_json | JSON-objekt | premiss; ingen SQL eller eval |
| hr_rules | action_json | JSON-liste med minst én handling | maskinlesbart handlingsforløp |
| hr_rules | owner_role | ansvarlig rolle | obligatorisk |
| hr_rules | deadline | foreløpig fritekst | ingen deterministisk fristberegning ennå |
| hr_rules | exception_json | JSON-liste | tom liste = ingen registrerte unntak |
| hr_rules | source | kilde-ID | obligatorisk; merket «syntetisk internregel» |
| hr_rules | valid_from / valid_to | ISO-dato | tidsrom inklusiv; NULL valid_to = ingen sluttdato |
| hr_rules | status | active/draft/superseded | bare active eksponeres |
| hr_rules | priority | heltall | høyeste prioritet listes først |

### En kjent faglig avgrensning

Kioskcasen bruker **kun som simulert krav** at relevant allergenopplæring må være verifisert og gyldig. Det er ikke påstand om at alle norske kioskvakter juridisk må ha et slikt kurs. Relevant erfaring scores fra `kasse=3,kundeservice=2,allergen=1,mattrygghet=1`. Kranførerbevis påvirker ikke kioskpoeng. Kriteriene, vektene, ukjente opplysninger og utelatelser returneres eksplisitt. Dette er en sammenlignbar baseline, ikke en ansattbeslutning.

### Fasitt og pedagogiske feiltyper

| ID | Kontroll | Forventet resultat |
|---|---|---|
| F01 | antall med dokumentert kassekompetanse | 7 aktive personer |
| F02 | spør om ukjent kompetansekode | eksplisitt UNKNOWN_SKILL |
| F03 | bemann kiosk 2026-11-07 10–16 med fem | E101,E102,E106,E103,E111 |
| F04 | E107 ingen tilgjengelighetsregistrering | unknown – ikke anta tilgjengelig |
| F05 | E104 kun 10–13 | partial, ikke fulltidsdekning |
| F06 | E110 kran og HMS | 0 relevante kioskpoeng |
| F07 | E108 udokumentert allergen | ikke kvalifisert |
| F08 | E109 utløpt allergen | ikke kvalifisert |
| F09 | E112 inaktiv | ikke kvalifisert |
| F10 | behov på ti | underskudd fire |
| R01 | søk HMS og avvik | HMS-001, eier, versjon, kilde og handling |
| R02 | søk før 2026-01-01 | ingen gjeldende regler |
| Q01 | dupliser nøkkel eller regelversjon | import stoppes |
| Q02 | brutt referanseintegritet | import stoppes |
| Q03 | verified=1 uten evidence | import stoppes |
| Q04 | kurs med tidsbegrensning uten sluttdato | import stoppes |
| Q05 | ulovlig tidsintervall | import stoppes |
| S01 | SQL-injeksjon i kompetansekode | ingen skriveeffekt |
| S02 | forsøk å bruke museum.db som utfil | avvises |
| L01 | spør LLM «Hvem er best?» | sammenlign faktisk modellforslag med deterministisk baseline |
| L02 | vis LLM irrelevante kurs | observer om den forveksler antall kurs med egnethet |
| L03 | vis LLM manglende data | observer om den finner på tilgjengelighet |

L01–L03 er **manuelle undervisningsøvelser** inntil en modellrunner kobles på. De 23 automatiserte testene ligger i `tests/test_hrdemo.py`.

## Kilder og gjenbruksvurdering

- Digdir: https://www.digdir.no/informasjonsforvaltning/felles-modelleringsregler-offentlig-forvaltning/3029 – datamodell, tidsrom, maskinlesbarhet, eier.
- Camunda: https://github.com/camunda/camunda-bpm-examples – åpne BPMN/DMN-eksempler, Apache-2.0. Referanse, **ingen ekstern kode eller data kopiert**.
- Alle nye personer og regler er syntetiske, utviklet for denne demoen.

**Viktig funn:** Eksisterende styringsdokumenter i Kunstpixel har motstridende interne krav til løft og alenearbeid. De er ikke automatisk gjort om til juridiske beslutningsregler. Kildene må kvalitetssikres dersom løsningen brukes utenfor kurssimulering.

## Neste fase

Menneskevennlig UI, frie LLM-vurderinger, eksperimentlogging og juridisk kildeverifikasjon er ikke implementert. Ingen produksjons- eller VPS-eksponering før autentisering, tilgangskontroll og kildegjennomgang.
