# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (museum.db, Datafinner og personvernanalysen) | Sist oppdatert: 2026-10-20 kl. 11:00*

## 1. Hva vi gjorde sist
- **Alt er flettet** (AGYs personvernanalyse og mitt arbeid) og testet: 349 tester og statusporten er grønne, og Docker-testen består.
- **Demoen virker lokalt** med faste rapporter, Docker og innlogging via Caddy. Det finnes nå et åpent API, og en valgfri KI-forklaring som er **av** til du slår den på. Den er alltid merket «AI-forslag», og navn og kontaktopplysninger sendes aldri ut.
- **Datadelen kan tas over av en hvilken som helst modell med Python**, også i Colab: `docs/DATAPIPELINE.md` og `notebooks/data_pipeline_colab.ipynb`.

## 2. Hvor vi slapp
- Ingenting er hostet. Du har ikke kjørt veilederen (`scripts\vps_veileder.ps1`).
- **museum.db er utdatert.** Jeg rettet en feil i `05_data/rapport_regler.csv` (et komma som kuttet en kolonne), og databasen må bygges på nytt.
- KI-laget er bare testet mot en falsk server, ikke mot en ekte leverandør. To grener fra før er ikke flettet (se `HANDOFF`).

## 3. Første oppgave neste gang du setter deg ned
- **Bygg databasen på nytt:** `py -3.13 src/kunstpixel/data/build_museum_db.py`. Kjør så `--check` (skal gi LIK) og si ifra, så committer jeg.
- Deretter: kjør veilederen, gå gjennom navnene i `.scratch/demo/navneliste.md` og regeltekstene i `05_data/rapport_regler.csv`.

## 4. Nyttige snarveier for dette prosjektet
- Demoen lokalt: `py -3.13 scripts/start_demo.py` (http://127.0.0.1:8011)
- Statusport: `py -3.13 scripts/db_status_gate.py` · Tester: `py -3.13 -m pytest -q`
- Test hosting i Docker: `powershell -ExecutionPolicy Bypass -File scripts\test_demo_container.ps1`
- Overlevering: `docs/HANDOFF-2026-10-20.md` · API: `docs/DATAFINNER_API.md` · Hosting: `deploy/demo/README.md`
