# Plassering og samarbeid

Kontrollert 26. oktober 2026. Lokal kodekopi er klargjort; arbeidsmåten med den andre deltakeren må fortsatt avklares før dere bytter hovedarbeidsmappe.

## Anbefalt plassering

- Kode, Git og lokal kjøring: `C:\Users\larse\source\Kunstpixel` på Lars sin PC. Vanlig lokal mappe utenfor Google Drive og OneDrive.
- Felles ideer, råfiler og leveranser: behold `G:\Min disk\Kunstpixel` som delt arbeidsflate inntil dere avtaler noe annet.
- Kodeutveksling mellom utviklere: eksisterende GitHub-repo `https://github.com/Luaze1985/Kunstpixel` og hver sin lokale kodekopi. Tilgang for den andre personen er ikke kontrollert eller endret.

Drive kan kjøre prosjektet, men dokumentasjonen beskriver Git-låser og problemer med Docker-montering på G:. En vanlig lokal mappe unngaar dette laget ved kodearbeid.

## Hva som er gjort

Det er laget en selvstendig lokal Git-klone fra Drive-repoets gren `hr-konsolidering`, commit `072ea54442eb5f33c0553b69908b4484f6056d8a`. Klonen deler ikke Git-objekter med originalen. `origin` peker på eksisterende GitHub-repo. Ingenting er sendt til GitHub.

`05_data/museum.db` er kopiert gjennom Git og hadde samme SHA-256 i begge mapper: `a8a90979a0a65ea32632b6e0cf300904a395942f2038de71a2c46393242c16e5`.

Klonen inneholder filer som var lagret i Git. Uregistrerte råfiler, leveranser, eksisterende arbeidstrær, lokale miljøfiler og agentoppsett blir liggende på Drive. Den lokale klonen er derfor en kodekopi, ikke en full flytting eller sikkerhetskopi av hele samarbeidsmappen.

## Slik unngaar dere to hovedkopier

1. Bruk fortsatt Drive til felles dokumenter til dere har avtalt arbeidsmåten. Dokumentkopier i den lokale Git-klonen er et øyeblikksbilde; de synkroniseres ikke automatisk med Drive.
2. Hvis begge endrer kode: bruk hver sin lokale klone og del gjennom GitHub. Avtal overgangen før noen fortsetter kodeendringer i den gamle Drive-kopien.
3. Hvis den andre bare arbeider med innhold: vedkommende kan fortsette i Drive. Overfør bare konkrete, avtalte filer til kodekopien når de skal brukes i programmet.
4. Ikke bruk automatisk toveissynkronisering mellom de to prosjektmappene. Ikke kopier `.git`, virtuelle miljoeer eller kjøredata frem og tilbake.
5. `museum.db` leses av programmet. Endringer gjores i datafiler; bare Lars bygger databasen etter prosjektets regler. To ulike databasefiler kan ikke flettes som tekst.

## Ta den lokale kopien i bruk

Legg `C:\Users\larse\source\Kunstpixel` til som eget prosjekt i Codex, og åpne en chat der. Denne chatten er fortsatt knyttet til G:-mappen; dens skrivetilgang foelger ikke automatisk med den nye mappen.

Kjør fra den lokale prosjektroten i PowerShell:

```powershell
py -3.13 -m pytest
py -3.13 scripts/db_status_gate.py --uten-pytest
py -3.13 src/kunstpixel/adapters/datafinner.py
```

Datafinner åpnes på `http://127.0.0.1:8010` på denne PC-en. Dette gir ikke automatisk tilgang fra den andre personens PC.

## Tilgangsfeilen som ble funnet

Agentens isolerte terminal fikk tilgang nektet på G:. Samme fil kunne leses utenfor isolasjonen, og testene kunne kjøres der. Dette viser et problem med agenttilgangen i denne chatten, ikke at prosjektet må flyttes for aa fungere. Globale sikkerhetsinnstillinger er ikke endret.

## Kontroller og avgrensning

Drive: 390 tester besto, 22 forventede feil for planlagte MVP-funksjoner. Statusport: 0 feil.

Datakvalitetskontrollen varsler 7 kjente tilfeller med kort hviletid og 1287 vakter over døgnmakset uten avklart overtidsmerking. Dette er eksisterende dataforhold og er ikke rettet som del av plasseringen.

Den andre personens PC, Drive-synkronisering og GitHub-tilgang er ikke testet. Endelig overgang avhenger av hvordan vedkommende arbeider med prosjektet.
Lokal kopi: 390 tester besto, 22 forventede feil. Statusport: 0 feil. En midlertidig HTTP-server på en ledig port på 127.0.0.1 ga 200 på `/`, `/api/status` og `/api/verktoyskjema`, og ble stoppet etter kontrollen. Dette er en HTTP-kontroll, ikke en visuell nettlesertest eller prøve fra den andre personens PC.

Google beskriver forskjellen mellom strømming og speiling her: https://support.google.com/drive/answer/13401938?hl=en