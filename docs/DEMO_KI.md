# Kjør KI- og ansattdemoen lokalt

Demoen er en del av samme Kunstpixel-repo og kjører på egen PC med Python 3.13. Den viser 168 syntetiske ansatte med syntetiske KI-profiler og koblet HR-kontekst. KI-register, søk og supplering fungerer uten API-nøkkel.

## Hent riktig kode og start

Åpne en terminal i din lokale Kunstpixel-mappe. Demogrenen heter `feat/ki-ansatt-demo`. Dette er navnet på leveransegrenen; instruksjonen forutsetter at grenen er gjort tilgjengelig i din kopi, og innebærer ingen påstand om at den er pushet til GitHub.

```text
git switch feat/ki-ansatt-demo
```

Har du allerede en annen arbeidskopi med egne endringer, ta vare på dem før du bytter gren. Installer Python 3.13 og Git dersom de mangler. Windows trenger Python-launcheren `py`; macOS/Linux trenger kommandoen `python3.13`.

Windows PowerShell, fra repo-roten:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_demo.ps1
```

macOS/Linux, fra repo-roten:

```bash
bash scripts/start_demo.sh
```

Skriptene går til repo-roten, oppretter `.venv` ved behov, kontrollerer Python 3.13, installerer `requirements-demo.txt` og starter eksisterende app. Første oppstart krever nett for pakkeinstallasjon. Avhengighetsfilen følger prosjektmanifestet med et fast kompatibelt MCP-par. En eksisterende `.venv` med annen Python-versjon må erstattes eller flyttes før ny oppstart.

Åpne **http://127.0.0.1:8001/** i nettleseren. La terminalen være åpen mens du bruker demoen. Serveren lytter bare på den lokale maskinen.

## Kort gjennomgang

1. Åpne KI- og ansattregisteret. Søk etter navn eller ansatt-ID, og prøv avdeling, status og KI-verktøy som filtre. Se antallet treff og hvilke profiler som er ukjente.
2. Velg en person. Se avdeling, ansettelsesperiode, KI-verktøy, bruk, kompetanse og modenhet. Dette er forskjellige dimensjoner; en antatt verktøybruk dokumenterer ikke arbeidsprestasjon.
3. Les HR-konteksten, kildene og datoperiodene. Historiske vakter og fravær gir kontekst, ikke bevis for at KI har endret innsatsen.
4. Legg inn en syntetisk individuell supplering med beskrivelse. Se at suppleringen og revisjonshistorikken vises uten å overskrive grunnprofilens opphav. Legg bare inn oppdiktede opplysninger.
5. Stopp og start appen igjen, og kontroller at suppleringen er bevart.
6. Valgfritt: åpne bemanningsplanen, velg uke, registrer kontaktsvar og lag et lokalt regelbasert forslag. Vurder og godkjenn eller avvis endringene. KI-profiler endrer ikke automatisk plan eller bemanningskvalifikasjoner.

Profilene er et versjonert øvingsgrunnlag. «Ukjent» betyr manglende kunnskap, ikke at personen ikke bruker KI eller har lav kompetanse. Historiske ansatte skal ikke telles som dagens KI-brukere; noen profiler er ikke relevante for aktuell periode. Antakelser, syntetiske registreringer og senere suppleringer skal leses med sin status, kilde og dato. Tallene er ingen måling av virkelige ansatte.

## Valgfri OpenAI-planlegging

Den eksisterende ukeplanleggeren kan bruke OpenAI når du selv velger det. Sett begge variablene i samme terminaløkt **før** oppstart. Velg et modellnavn som er tilgjengelig for din konto og passer ditt kostnadsvalg. Ingen modell velges automatisk her.

PowerShell:

```powershell
$env:OPENAI_API_KEY = '<din nøkkel, kun lokalt>'
$env:KUNSTPIXEL_OPENAI_MODEL = '<ditt eksplisitte modellnavn>'
.\scripts\start_demo.ps1
```

Bash:

```bash
export OPENAI_API_KEY='<din nøkkel, kun lokalt>'
export KUNSTPIXEL_OPENAI_MODEL='<ditt eksplisitte modellnavn>'
bash scripts/start_demo.sh
```

Eksemplene er plassholdere. Del aldri nøkkelen i Git eller chat; følg lokale rutiner for hemmeligheter og terminalhistorikk. Appen leser serverprosessens miljøvariabler. Den laster ikke automatisk en `.env`-fil. Nøkkelen brukes på serveren og sendes ikke til nettleseren. Ved et faktisk OpenAI-forslag sendes den avgrensede syntetiske planleggingskonteksten til OpenAI; registeret trenger ingen slik forespørsel. Modellforslag kontrolleres lokalt og krever fortsatt menneskelig godkjenning.

## Stopp, omstart og data

Stopp med **Ctrl+C** i serverterminalen. Kjør samme oppstartsskript for å starte igjen. Port 8001 må være ledig; stopp en tidligere demoprosess hvis adressen allerede er i bruk. Vil du hoppe over pakkeinstallasjonen etter første vellykkede oppsett, kan du starte direkte fra repo-roten:

```powershell
.\.venv\Scripts\python.exe -m src.kunstpixel.hr_simulator web
```

```bash
.venv/bin/python -m src.kunstpixel.hr_simulator web
```

Grunnprofiler og kildefiler ligger versjonert i repoet. Lokal planstatus, suppleringer og revisjoner lagres separat på din maskin i simulatorens lokale SQLite-filer og legges ikke i Git. Omstart bevarer disse filene. Ikke slett dem dersom du vil beholde demoarbeidet. Den autoritative `museum.db` endres ikke av denne arbeidsflyten.

Det er ingen automatisk GitHub-synkronisering. Ny versjonert kode og nye grunnprofiler må overføres med vanlig Git-flyt; lokale suppleringer blir ikke automatisk delt med andre maskiner eller brukere.
