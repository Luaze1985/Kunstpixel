# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (museum.db og Datafinner) | Sist oppdatert: 2026-10-20 kl. 08:45*

## 1. Hva vi gjorde sist
- Datafinner er ferdig designsjekket (10 funn lukket) og har demomodus: filverktøyene er borte, og det er sikkerhetshoder og generelle feilmeldinger.
- Demokopi av databasen uten fødselsår, e-post og telefon. Alle tall er like som i museum.db.
- En veileder (`scripts/vps_veileder.ps1`) tar deg gjennom domene, VPS, SSH-nøkkel og DNS. Du gjør innlogging og betaling selv.

## 2. Hvor vi slapp
- Ingenting er hostet. Dockerfile, Caddy (innlogging) og utrulling er ikke laget.
- Trinn 3 og 6 i veilederen (lage nøkkel, logge inn på serveren) er ikke kjørt, fordi de krever deg.
- Grenene for «én verktøyliste» og «del db.py» er ikke slått sammen.

## 3. Første oppgave neste gang du setter deg ned
- Kjør veilederen: `powershell -ExecutionPolicy Bypass -File scripts\vps_veileder.ps1`
- Gå gjennom navnene i `.scratch/demo/navneliste.md`, og regeltekstene i `05_data/rapport_regler.csv`.
- Si «VPS og domene er klare» til Claude, så lages Docker og Caddy.

## 4. Nyttige snarveier for dette prosjektet
- Demomodus lokalt: `py -3.13 scripts/start_demo.py` (http://127.0.0.1:8011)
- Statusport: `py -3.13 scripts/db_status_gate.py` (rapport i `.scratch/db-status/`)
- Datafinner vanlig: `py -3.13 src/kunstpixel/adapters/datafinner.py` (http://127.0.0.1:8010)
- Tester: `py -3.13 -m pytest -q`
- Status og kjørebok for hosting: `02_deliverables/arbeidsflyt/hosting-demo.md`
