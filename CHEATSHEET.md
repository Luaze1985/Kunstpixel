# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (museum.db, Datafinner og personvernanalysen) | Sist oppdatert: 2026-10-20 kl. 09:30*

## 1. Hva vi gjorde sist
- **Datafinner** er designsjekket, har demomodus (uten filverktøy, e-post, telefon og fødselsår), Docker med innlogging via Caddy, og en veileder for domene og VPS. Alt er testet lokalt.
- **Personvernanalysen (AGY, egen sak):** time-for-time-database med 439 952 rader og 168 simulerte ansatte i Trondheim, krysset mot kollektivstans, skattelister og Virke-lønn. Colab-notatboken ligger i `02_deliverables/02_rapporter/personvern_time_for_time_colab.ipynb`. Den er ikke del av Datafinner og ikke med i demoen.
- Grenene er nå flettet: AGYs siste og mitt arbeid ligger sammen.

## 2. Hvor vi slapp
- Ingenting er hostet ennå. Veileder og kjørebok er klare, men du har ikke kjørt dem.
- Regeltekstene i `05_data/rapport_regler.csv` og navnelisten `.scratch/demo/navneliste.md` er ikke gjennomgått av deg.

## 3. Første oppgave neste gang du setter deg ned
- Les `HANDOFF.md`. Den er skrevet slik at en hvilken som helst språkmodell med Python kan ta over datadelen.
- Kjør veilederen: `powershell -ExecutionPolicy Bypass -File scripts\vps_veileder.ps1`
- Utforsk Colab-analysen til AGY i Seksjon 7 når du vil.

## 4. Nyttige snarveier for dette prosjektet
- Demomodus lokalt: `py -3.13 scripts/start_demo.py` (http://127.0.0.1:8011)
- Statusport: `py -3.13 scripts/db_status_gate.py` (rapport i `.scratch/db-status/`)
- Datafinner vanlig: `py -3.13 src/kunstpixel/adapters/datafinner.py` (http://127.0.0.1:8010)
- Tester: `py -3.13 -m pytest -q`
- Test hosting-oppsettet i Docker: `powershell -ExecutionPolicy Bypass -File scripts\test_demo_container.ps1`
- Datakvalitet i personvernanalysen: `py -3.13 src/kunstpixel/data/audit_time_for_time_quality.py`
- Status og kjørebok for hosting: `02_deliverables/arbeidsflyt/hosting-demo.md`
