# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel | Sist oppdatert: 2026-11-15 16:57*

## 1. Hva vi gjorde sist
- Lekegrinden er klar for live-demo: åpne Claude, spør fritt, og skriv `/sjekk` for å få svaret kontrollert mot databasen.
- Main er ryddet og pushet til GitHub. Alt er committet, og testene er grønne (2254).
- Låst: korte svar, du spør som museumsdirektør, ingen demo-v2 (DECISIONS L1–L12, W1–W5).

## 2. Hvor vi slapp
- `/sjekk` er ikke prøvd i en helt ny økt ennå.
- Tre tabeller finner ikke Claude i demoen: dagsbesøk, medarbeidersamtaler og innleides kompetanse. Bare Datafinner når dem.

## 3. Første oppgave neste gang du setter deg ned
- **Prøverunde (10 min):** dobbeltklikk `start_claude.cmd`. Spør «Hva står i personalmappen til Stine Haugen?» og «Hvilken stilling har Anja Eriksen?». Skriv `/sjekk` etter hvert svar.
- Alle kravene (K1–K5) står i `.scratch/handoffs/HANDOFF-2026-11-15T1657.md`.

## 4. Nyttige snarveier
- Demo: `start_claude.cmd` (dobbeltklikk)
- Helsesjekk: `sjekk_helse.cmd`
- Statusport: `py -3.13 scripts/db_status_gate.py --uten-pytest`
- Alle tester: `py -3.13 -m pytest`
