# Fiktivt persongrunnlag for museumsuke

`staff_source.csv` er en renset kopi av 168 syntetiske ansatte fra
`05_data/arkiv_hr_ansatte.csv` i lokal `main`, kontrollert 17. oktober 2026.
SHA-256 for original-CSV: `4c26e07b77e002da1f259b1500281d7f9d5a67b37fadc584ff1c922c096f49bf`.
Bare ID, navn, avdeling, stilling, ansettelsesperiode, status og stillingsprosent
er tatt med. Originalens e-post og telefon brukes ikke. Alle demokontakter
genereres med `example.invalid` og 000-numre.

`staff_data.py` gir eksplisitt stillingsmapping. Første kompetanse får fiktiv
opplæring; tilleggskompetanse forblir ukjent i utgangspunktet. Tilgjengelighet
er konstruerte mulige tidsrom: `weekday` mandag–fredag 08–21, `technical`
mandag–fredag 08–18, `host` mandag–fredag 08–21 og lørdag 08–21. Ukentlig
kapasitet begrenses separat til `40 × stillingsprosent` timer. Disse reglene
beskriver en øvelse, ikke faktiske arbeidsavtaler eller lovlig arbeidstid.

`redigeringsbord/UTKAST-ansatte-kandidater.csv` er en flat arbeidskopi.
Kun `skills`, `training` og `availability_profile` kan endres. En lagring
aktiverer ikke endringen før lokal validering og «Bruk datagrunnlag».
Aktivering oppretter en ny dataversjon med separat planstatus.

`archive_quality.json` gjengir kontrollresultatet fra det større syntetiske
arkivet. Vakthistorikken brukes ikke i kapasitet, hvile eller KI-kontekst,
fordi den mangler klokkeslett og inneholder umulige persondager.
