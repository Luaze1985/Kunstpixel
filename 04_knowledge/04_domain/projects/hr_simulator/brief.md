# Kunstpixel – syntetisk HR- og bemanningssimulator (MVP 1)

## Formål
Øve på arbeidsfordeling, oppgaveprioritering, HR-konflikter, intern ekstravaktpool og innleie i en fiktiv norsk småbedrift. Ingen reelle personopplysninger, ikke et produksjonsklart HR-system.

**Status:** Datamodell og regelbasert førsteversjon. En deterministisk forslagsmotor lager utkast. Det er foreløpig ingen tilkoblet KI-modell, ingen rolleautentisering og ingen ferdig bemanningstavle. Alle beslutninger i demo krever en eksplisitt godkjenningsfunksjon.

## Scenarioer
- `HR-001.json`: Åtte faste ansatte, tre pool-kandidater, skolebesøk, montering, kafé og kveldsarrangement. Avdekk én dobbeltbooking og én bemanningsmangel. Utred mulighet for intern ekstravakt eller innleie.
- `HR-002.json`: To fiktive ansatte er uenige om fordeling av senvakter. HR-saken er konfidensiell. KI/regelbaserte forslag kan foreslå faktainnhenting, aldri konkludere skyld eller foreslå automatiske personalreaksjoner.

## Data og personvern
- `persons`: person-ID, fiktivt navn, fødselsår, ugyldig test-epost (`@example.invalid`), dummytelefon (`000...`), stillingsandel og type.
- `person_skills`, `availability`: kompetanse og arbeidstidsvinduer.
- `activities`, `activity_requirements`, `assignments`: oppgaver, bemanningskrav og hvem som er fordelt.
- `providers`, `rental_requests`: fiktive bemanningsforetak, juridisk vurderingsstatus og likebehandlingskontroll.
- `hr_cases`, `hr_case_parties`: HR-saker med begrenset visning.
- `proposals`, `decision_log`: forslag, manuell beslutning og sporbar logg.

Ikke lagre reelle fødselsnumre, helseopplysninger, varslere, kontakter, arbeidsavtaler eller lønnsdata i offentlig GitHub-repo. Testpersoner er oppdiktede og har ikke gyldig kontaktinformasjon. I en reell løsning må innsynsstyring, autentisering, taushetsplikt, dataminimering, sletting og logging løses før bruk.

## Roller og fullmakter
1. **Leder:** Kan godkjenne ordinær flytting av aktivitet når regelkontrollene godtar endringen.
2. **HR:** Kan godkjenne innleieforslag og åpne konfidensiell saksutredning.
3. **KI/regelmotor:** Kan lese relevante syntetiske opplysninger, vise konflikter og foreslå alternativer; skal ikke avgjøre skyld, ansettelse, sanksjoner eller innleielovlighet.
4. **Tillitsvalgt/verneombud:** Scenarioaktører ved relevante saker. Ikke automatiserte beslutningstakere.

Merk at demoens `approver_role` kun er en strengverdi, ikke faktisk identitetskontroll. Den skal aldri brukes til ekte ansattdata eller på nettet uten innlogging og serverbasert tilgangsstyring.

## Viktig om innleie i Norge
Skill tydelig mellom:
- **Intern pool:** Allerede ansatt tilkallingsvikar eller intern ekstravakt, styrt av arbeidsavtale og arbeidstidsregler.
- **Innleie via bemanningsforetak:** Må vurderes separat med hensyn til lovlig innleiegrunnlag, foretakets aktuelle godkjenningsstatus, arbeidstid og likebehandling.
- **Tjenestekjøp/entreprise:** Ikke det samme som innleie. Klassifisering må vurderes etter faktisk opplegg, ikke etikett.

MVP inneholder kun **fiktiv leverandørstatus** i øvelsesdata og boolske kontrollfelt for simulert HR-avklaring. Den dokumenterer **ikke** lovligheten av konkret innleie. Ekstern kandidat som ser ledig og kompetent ut skal ikke automatisk bli godkjent. Det er særskilt viktig å ikke behandle generelt høyt aktivitetsnivå som tilstrekkelig juridisk grunnlag.

Offisielle kilder til bruk ved senere regelutvikling:
- Arbeidstilsynet: https://www.arbeidstilsynet.no/lonn-og-ansettelse/innleie-av-arbeidskraft/innleie-fra-bemanningsforetak/
- Arbeidstilsynet, godkjente foretak: https://prod.arbeidstilsynet.no/godkjenninger/godkjente-bemanningsforetak/
- Arbeidstilsynet, varsling og saksbehandling: https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/slik-bor-arbeidsgiver-handtere-varsling/

## Grunnregler for HR-konflikter
- Skille fakta, påstander og vurderinger. Utlever bare konfidensielle saksopplysninger til HR i øvelsen.
- Hør begge parter. Vurder habilitet og dokumentasjon.
- Ingen automatisk skyldfordeling, personprofilering, disiplinærreaksjoner eller rangering av ansattes verdi.
- Arbeidsfordeling skal ses i sammenheng med kompetanse, kapasitet, dokumenterte krav og rettferdighet over tid.
- Hvis opplysninger mangler, registrer «ikke dokumentert» fremfor å konkludere.

## Kjøring og tester
Fra repo-roten:

```bash
python -m src.kunstpixel.hr_simulator HR-001
python -m src.kunstpixel.hr_simulator HR-002
python -m pytest tests/test_hr_simulator.py -q
```

Python-komponentene bruker kun standardbiblioteket. Den generelle museumsdatabasen `05_data/museum.db` endres ikke. Simuleringen bruker sin egen SQLite `:memory:`-database.

## Neste trinn
1. Få testpakken grønn, inkludert den eksisterende testpakken.
2. Legge til en intern bemanningstavle med visning av konflikter, pool-kandidater, avvik og godkjenningsdialog.
3. Bygge scenario HR-003: sykefravær, legitimt vikariat og valg mellom intern pool/ekstern bemanning.
4. Innføre prioriterings- og rettferdighetsmål, uten å automatisere personavgjørelser.
5. Integrere valgfri KI-forslagsgenerator bak deterministiske kontroller og menneskelig godkjenning.

## Avgrensning
Dette er et læringsverktøy, ikke juridisk rådgivning, lønnssystem, personregister eller produksjonsløsning for HR.
