# Importert katalog: samtaler og rollespill

Kilde: brukers innlimte tekst 20. oktober 2026. Dette er **en katalogoversikt** med titler, kortbeskrivelser, varighet, samtaletype, personnavn/rolle og enkelte synlige tagger. Den inneholder **ikke** fullstendige instruksjoner for simulerte karakterer, forventet replikkveksling eller vurderingsrubrikker.

## Opptelling

- **113 katalogoppføringer** med originale ID-er; **112** har alle hovedfeltene.
- **96 komplette** innen HR, ledelse, coaching, samtaler og konflikter.
- **16 komplette** innen salg, forhandling og kundedialog; bevisst separert fra HR-samlinger.
- **1 ufullstendig:** `VANS-07` har bare ID, tittel og beskrivelse fordi den opprinnelige innlimingen stopper der.
- Kildens `+1`/`+2` er bevart i `hidden_tag_count`, ikke forsøkt tolket som faktiske synlige tagger.

## Filer

- `oversikt.html` — åpne lokalt for fritekstsøk og filtrering (lesegrensesnitt, ingen nettverkskall).
- `scenario_catalog.json` — alle oppføringene samlet, med kildefelt og fullstendighetsstatus.
- `scenario_catalog.csv` — flat katalog for Excel og videre analyse.
- `scenarios/*.json` — 113 individuelle metadatafiler med originale ID-er.
- `links_to_hr_cases.json` — redaksjonelle koblinger fra 14 eksisterende KI-HR-case til relevante samtaler.
- `source_paste_2026-10-20.txt` — uendret kildetekst for sporbarhet.

## Betydningen av koblingene

`SYK-03` er trening på å snakke om et fraværsmønster. `HR-012` er trening på KI og personvern ved fraværsanalyse. Disse er *ulike* øvelser. De kan kombineres sekvensielt: først en KI-/dataetisk avgjørelse, deretter en vanskelig samtale. Koblingen innebærer ikke at de deler juridisk fasit eller database.

## Personvern, publisering og gjenbruk

Kildetekstens navn er *ikke verifisert som syntetiske*. Bare etter en egen kontroll av lisens, kildeopphav og personopplysninger bør tekst/karakterer publiseres i et offentlig repo. Verken alle personer eller alle scenariodetaljer er dokumentert som oppdiktede. Ikke koble katalogen til ekte personalopplysninger, Teams, Gmail eller eksterne LLM-er.

## Hva som gjenstår for kjørbare samtalescenarioer

1. Avklar om oppføringene kan gjenbrukes og om personaene er oppdiktet; bytt ellers til egenkomponerte personas.
2. Skriv et manus/rolleprompt per valgt scenario: mål, skjult motivasjon, gradvis informasjonsdeling, stoppkriterier.
3. Lag vurderingsrubrikk for samtaleferdigheter (lytting, åpne spørsmål, kontradiksjon, medbestemmelse, relevant lovforståelse).
4. Test KI som simulator og separat KI som vurderer, ikke som automatisk avgjører i reell personalsak.
5. Implementer først etter Kunstpixels eksisterende fase A og med syntetiske data.
