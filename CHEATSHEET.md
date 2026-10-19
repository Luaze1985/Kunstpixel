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
- Regler og roller fra Antigravity var merket «autoritativ». Det er nå rettet til «syntetisk» i CSV-filene, men museum.db er ikke bygget på nytt. Inntil du bygger, viser Datafinner «autoritativ» i Grunnlag.
- Ingenting er pushet. Ingenting er slått sammen inn i `hr-konsolidering`.

## 3. Første oppgave neste gang du setter deg ned
- Bygg databasen i arbeidstreet `statusporten-loop-agent-722112`: `py -3.13 src/kunstpixel/data/build_museum_db.py`. Ny hash skal være `0da9c837…`.
- Bestem deretter om grenen skal slås sammen inn i `hr-konsolidering`.

## 4. Nyttige snarveier for dette prosjektet
- Statusport: `py -3.13 scripts/db_status_gate.py` (rapport i `.scratch/db-status/`)
- Bygg databasen: `py -3.13 src/kunstpixel/data/build_museum_db.py` (prøve: `--check`)
- Datafinner: `py -3.13 src/kunstpixel/adapters/datafinner.py` og http://127.0.0.1:8010
- Tester: `py -3.13 -m pytest -q`
