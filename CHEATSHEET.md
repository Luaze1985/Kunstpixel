# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (Datafinner og museum.db) | Sist oppdatert: 2026-10-19*

## 1. Hva vi gjorde sist
- Datafinner (internt oppslag, kun lesing) har forside med rollene HR og bemanning og Økonomi og innkjøp, seks faste spørsmål, kort svar og rapport.
- Låst: alle svar skal komme fra museum.db. Det som mangler står som «Mangler». Klokkeslett og arbeidstidsgrenser er laget som syntetiske data og venter på bygget.

## 2. Hvor vi slapp
- Byggeskriptet `build_museum_db.py` er klart og testet mot en kopi, men museum.db er IKKE byttet ut ennå. Sikkerhetskontrollen lar ikke agenten gjøre det.

## 3. Første oppgave neste gang du setter deg ned
- **Få databasen live:** åpne terminal i arbeidsmappen og kjør bygget (se snarvei under). Si fra til agenten etterpå, så sjekker den resultatet og committer.

## 4. Nyttige snarveier for dette prosjektet
- Arbeidsmappe: `G:\Min disk\Kunstpixel\.claude\worktrees\arbeidsflyt-interne-sider-data-4e465d`
- Bygg databasen: `py -3.13 src/kunstpixel/data/build_museum_db.py`
- Prøvebygg uten å endre noe: `py -3.13 src/kunstpixel/data/build_museum_db.py --check`
- Start Datafinner: `py -3.13 src/kunstpixel/adapters/datafinner.py` og åpne http://127.0.0.1:8010
- Tester: `py -3.13 -m pytest -q`
