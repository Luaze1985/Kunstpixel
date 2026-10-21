# Syntetisk KI-datasett

`05_data/hr_simulator/ai_profiles.json` og CSV-eksporten inneholder én profil for hver av de 168 unike ID-ene i `staff_source.csv`. Referansedato er **2026-10-21**. Ingen verdi beskriver faktisk KI-bruk hos virkelige personer. Også statusen `synthetic_report` betyr et konstruert demosvar.

Regenerer med:

```sh
.venv/bin/python scripts/generate_ai_profiles.py
.venv/bin/python -m pytest tests/test_ai_data.py -q
```

Generatoren bruker SHA256 av versjonsnavn og ansatt-ID som individuell seed. Radrekkefølge og endringer hos andre ansatte endrer ikke en persons profil. Avdeling og stilling påvirker konstruert brukssannsynlighet og relevante oppgaver. Navn, kjønn og alder brukes ikke. JSON sammenlignes mot en ny generering i testene. CSV har samme profilfelt; lister er JSON-kodet, nullverdier er tomme felt, og filen har UTF-8-signatur for regneark.

## Identitet og avdelingsgrunnlag

Stabil nøkkel er `person_id = staff_source.ansatt_id` (KP-ANS-ID), aldri navn. Seks avdelinger får stabile `department_id`-verdier og egne beskrivelser og antakelser. Avdelingsbeskrivelsene er scenarioer, ikke observasjoner eller dokumentasjon av en bestemt ansatt. Profilens `basis` viser kildeavdeling og stilling; `source`, `method`, `uncertainty` og `synthetic` viser begrensningene.

## Datoer, status og nevner

- `employment_status=active`: ansatt ved referansedatoen. `historical`: ansettelsen sluttet tidligere. `future`: ansettelsen begynner senere.
- `synthetic_report`: konstruert svar fra en syntetisk person. `assumed`: uttrykkelig antakelse fra rolle-/oppgavemal. `unknown`: manglende svar, ikke null bruk. `not_applicable`: utenfor relevant periode.
- Demoens moderne KI-periode starter konservativt 2023-01-01. Avsluttede ansettelser før denne grensen får ingen moderne verktøy, bruk eller skårer. Dette er en demogrense, ikke en historisk påstand om når KI oppsto.
- Historiske profiler har `observation_date` og `period_end` senest siste ansettelsesdag. Periodens start er seneste av ansettelsesstart og demogrensen. Fremtidige og ikke relevante profiler har ingen observasjonsperiode.
- `unknown` har tomme verktøy/oppgaver og null skårer. `never` er et eksplisitt syntetisk ikke-brukssvar og må ikke slås sammen med ukjent eller ikke relevant.

Rapporter nåværende bruk med aktive ansatte som uttrykkelig nevner. Vis manglende svar og antakelser separat. Historiske opplysninger skal aldri telles som dagens ikke-brukere.

## Tre forskjellige dimensjoner

Bruksfrekvens er `daily`, `weekly`, `monthly`, `never`, `unknown` eller `not_applicable`. Kompetanse og modenhet er separate syntetiske skalaer fra 1 til 5, med null for ukjent/ikke relevant:

| Nivå | Vurdert KI-kompetanse | Vurdert arbeidsmåtemodenhet |
|---|---|---|
| 1 | Nybegynner, trenger veiledning | Utforsking |
| 2 | Enkel bruk med støtte | Enkeltstående forsøk |
| 3 | Selvstendig grunnbruk og kontroll | Gjentatt arbeidsmåte |
| 4 | Avansert bruk og kildekritikk | Avklarte rutiner og kontroll |
| 5 | Veileder andre og vurderer begrensninger | Systematisk forbedring og oppfølging |

Skårene er konstruerte eksempler uten validert måleinstrument. Verktøynavn angir mulige scenarioer, ikke innkjøpte lisenser. Aldri-brukere kan ha teoretisk kompetanse. Verken høy frekvens eller mange verktøy beviser kompetanse, modenhet eller bedre resultater.

## Gradvis berikelse

Grunnprofilene er versjonerte filer. Individuelle suppleringer skal lagres separat med dato, kilde, grunnlag og revisjonshistorikk og kobles med samme person-ID. En senere opplysning kan supplere eller avløse en antakelse uten å slette originalen. Selvrapportering må beholdes som selvrapportering; avdelingsgrunnlag blir ikke automatisk en personobservasjon.

Datasettet leser ikke og endrer ikke `museum.db`. Det inneholder ingen målt tidsbesparelse, faktisk oppgaveinnsats eller årsakssammenheng mellom KI, vakter og fravær. Bemanningskvalifikasjoner og arbeidsplaner endres ikke av disse profilene.
