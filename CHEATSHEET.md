# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (museum.db og Datafinner) | Sist oppdatert: 2026-10-19 kl. 20:10*

## 1. Hva vi gjorde sist
- Antigravitys datahull (T1–T7) og statusporten ligger nå sammen på grenen `claude/statusporten-loop-agent-722112`.
- Datafinner er ferdig koblet til databasen:
  - Rollekortene kommer fra museum.db.
  - Sykefravær viser museets eget fravær mot SSB.
  - Vurdering og Forslag kommer fra regeltabellen.
  - Vaktkostnad har 0 vakter uten tariff.
- Statusporten sier KLAR med 0 feil, og alle 262 tester består.

## 2. Hvor vi slapp
- museum.db er bygget på nytt med regler og roller merket «syntetisk» (hash `0da9c837…`, lik prøvebygget).
- Grenen er slått sammen inn i `hr-konsolidering`. Ingenting er pushet.

## 3. Første oppgave neste gang du setter deg ned
- Les regeltekstene i `05_data/rapport_regler.csv`. Antigravity skrev dem selv, og terskler og kilder som «Bemanningsplan 2026» finnes ikke i repoet. Godkjenn dem eller skriv dem om.

## 4. Nyttige snarveier for dette prosjektet
- Statusport: `py -3.13 scripts/db_status_gate.py` (rapport i `.scratch/db-status/`)
- Bygg databasen: `py -3.13 src/kunstpixel/data/build_museum_db.py` (prøve: `--check`)
- Datafinner: `py -3.13 src/kunstpixel/adapters/datafinner.py` og http://127.0.0.1:8010
- Tester: `py -3.13 -m pytest -q`
