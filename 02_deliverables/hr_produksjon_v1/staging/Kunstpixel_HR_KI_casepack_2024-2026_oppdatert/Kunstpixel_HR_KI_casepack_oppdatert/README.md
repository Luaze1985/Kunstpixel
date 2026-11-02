# Kunstpixel – HR/KI-casepack 2024–2026

Dato: 20. oktober 2026. Innhold: 14 scenariospesifikasjoner for å teste vanskelige KI-beslutninger i HR. Dette er *forslag*, ikke implementerte funksjoner. Repoet er ikke endret.

## Innhold

- `scenario_catalog.json`: sortert portefølje med dokumentert, vurderende prioriteringsscore.
- `scenarios/HR-004.json` … `HR-017.json`: 14 selvstendige scenarioer med hensikt, databehov, felle, forsvarlig respons og beståttkriterium.
- `guides/DATAMODELL_OG_GRENSEVERN.md`: dataskjema, dataklassifisering og tilgangsmodell.
- `guides/OVELSE_EVALUERING.md`: treningsflyt, tester og poengmodell.
- `guides/REPO_INTEGRASJON.md`: forslag til hvordan scenarioene kan innføres uten å røre eksisterende HR-001–003.
- `guides/KILDER.md`: lenker og tidsangivelser for eksterne kilder.

## Viktig presisering

De fiktive personene i dagens Kunstpixel-repo og dette casepacket er ikke et faktisk HR-system. Ikke koble til ekte HR-data, Gmail, kalender, Teams eller eksterne LLM-er. Ikke åpne demo på internett. Sørg for reell serverbasert autorisasjon før data med personvernbehov brukes, også hvis slike data «bare» er interne.

## Forslag til pilot

Start med `HR-013` (varslingssak), `HR-005` (industriell produktivitetsovervåking) og `HR-012` (sykefraværsradar), men aktiver dem først som frittstående testfiler etter at den eksisterende fase A-planen er fullført og testet.

Vektene i score er en transparent produktprioritering, *ikke* juridisk risikovurdering eller empirisk score fra HR Norge.


## Utvidelse 20. oktober 2026 – 113 samtaletreningsscenarioer

Denne **oppdaterte** pakken har fortsatt alle de 14 opprinnelige KI-/HR-casefilene (`HR-004..017`), men inkluderer dessuten:

- `conversation_training/`: 113 innlimte scenariooppføringer bevart med ID, metadata, individuell JSON, CSV, lokal søkbar HTML-visning og original innliming.
- `conversation_training/links_to_hr_cases.json`: pedagogiske koblinger til de 14 KI-/HR-dilemmaene. Også de 14 opprinnelige JSON-filene har fått `conversation_training_refs`.
- `conversation_training/PRIORITERTE_HR_SAMTALER.md`: 25 prioriterte øvelser for videre utvikling.
- `tools/validate_package.py`: kontrollerer antall, ID-er, tilstand og sammenhenger.

**Viktig:** 112 oppføringer har komplette katalogmetadata, men ingen er komplette manus. `VANS-07` mangler nesten alle metadata. Kildens personnavn er ikke verifisert som fiktive, og gjenbruksrettighetene er ukjente. Behandle hele pakken som lokalt arbeidsgrunnlag og vurder kilde/rettigheter før publisering i offentlig GitHub-repo. Dette er ikke en integrasjon med det eksisterende kjørbare HR-API-et.

Åpne `conversation_training/oversikt.html` lokalt for å søke i scenarioene. Kjør `python tools/validate_package.py` fra pakkens rot for strukturkontroll.
