# Kunstpixel HR Lab – kode hentet fra GitHub (referanseområde)

**Status:** Kun kildekodeutvalg for vurdering. **IKKE** et installert HR-system. **IKKE** importert i Kunstpixels runtime.

Denne katalogen ligger isolert i `experiments/hr_lab/` på en separat Git-gren, og endrer ingen eksisterende kode- eller databasefiler. Materialet ble hentet fra GitHub 20.10.2026. Se `SOURCE_LOCK.json` for eksakt commit og filsti.

## Faktiske kildekodeutdrag

- **Frappe HR (GPL-3.0):** `upstream/frappe/frontend/src/composables/workflow.js`, `.../data/attendance.js`, `.../AttendanceRequestForm.vue`. Brukes for å vurdere selvbetjening, validering og godkjenningsflyt. De krever Vue, Frappe UI og backend; filene kjører ikke alene.
- **MintHCM (AGPL-3.0):** `upstream/mint/api/app/Routes/routes/mcp.php`, `.../McpController.php`, `.../14-mcp-login-flow.md`. Viser MCP/OAuth2-samtykke og kontroll av tilgang, ikke et ferdig Python-MCP-grensesnitt.
- **Onyx (MIT, kun Community Edition-filene som er kopiert):** `upstream/onyx/backend/onyx/chat/citation_processor.py`, `.../auth/scoped_permissions.py`, dokumentasjon. Brukes til å analysere kildehenvisninger og rettighetsgrenser. Har mange Onyx-spesifikke avhengigheter.

Lisensene ligger uendret i hver sin `upstream/<prosjekt>/`-mappe. Ingen fil er knyttet til Kunstpixels runtime.

## Sikkerhet / anti-forurensning

1. Ikke kopier de GPL-/AGPL-lisensierte modulene direkte til `src/kunstpixel/` uten lisens- og arkitekturvurdering.
2. Ikke gjør noen migrasjoner mot `05_data/museum.db` (som må fortsette med `mode=ro`).
3. Ikke importer disse upstream-mappene i museumsvertens app eller MCP-server.
4. AP0–AP9-regelverk importeres senere separat med status **ikke verifisert** til hvert kildebevis er gjennomgått.
5. Syntetiske ansatte, vaktplaner, datauttrekk og SQLite-filer skal bare være lokale og ikke sjekkes inn i Git.
6. Før faktisk integrering: kjør repoets opprinnelige tester, vurder norsk tariff/personvern og lag egen PR for hver funksjon.

## Hva som skal gjenbrukes

**Første mål:** Én enkel ansattsøknad med ledergodkjenning og kildeforankret svar, via Kunstpixels eget API/MCP-lag. Frappe og Mint brukes som funksjons- og sikkerhetsreferanse, Onyx' MIT-kode kan vurderes for konkret gjenbruk etter tilpasning.

**Ikke gjør:** installer hele ERP-systemet, hent all kildekode eller koble ukjent HR-data direkte inn i museets samlingsdatabase.

## Verifisering

Fra repo-roten: `python -m unittest discover -s experiments/hr_lab/tests -v`. Dette tester kun isolasjon av referansepakken; ikke upstream-programmenes egne tester. Eksisterende Kunstpixel-tester er ikke kjørt i GitHub-connectoren.
