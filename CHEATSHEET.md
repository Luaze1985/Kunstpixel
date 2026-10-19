# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (museum.db og Datafinner) | Sist oppdatert: 2026-10-19 kl. 15:30*

## 1. Hva vi gjorde sist
- museum.db er live: du kjørte bygget, og det stemmer med prøvebygget (hash 63bf6cf4). Datafinner viser nå klokkeslett, «på jobb nå», overtid og kveldstimer, merket som syntetiske.
- Ny statusport `scripts/db_status_gate.py` og loop-agenten `db-merge-vakt` sjekker databasen før sammenslåing. Status nå: KLAR, 0 feil, 8 åpne hull som advarsler.

## 2. Hvor vi slapp
- Briefen til Antigravity (datahull G2–G9) er sendt. Den nye databasen og porten er committet på grenen min, men ikke slått sammen med `hr-konsolidering`.

## 3. Første oppgave neste gang du setter deg ned
- **Når Antigravity er ferdig:** start en ny Claude-økt og si «kjør db-merge-vakt på Antigravitys gren med briefen». Les rapporten og bestem om grenene skal slås sammen.

## 4. Nyttige snarveier for dette prosjektet
- Statusport: `py -3.13 scripts/db_status_gate.py` (rapport i `.scratch/db-status/`)
- Bygg databasen: `py -3.13 src/kunstpixel/data/build_museum_db.py` (prøve: `--check`)
- Datafinner: `py -3.13 src/kunstpixel/adapters/datafinner.py` og http://127.0.0.1:8010
- Tester: `py -3.13 -m pytest -q`
