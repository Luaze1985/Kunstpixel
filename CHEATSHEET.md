# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel | Sist oppdatert: 2026-10-31*

## 1. Hva vi gjorde sist
- **Arenaen er klar til testing:** siden `/arena` har 19 caser (bemanning, tidsbruk, GDPR, økonomi, publikum og Drift og bunnlinje D1–D5).
- **Databasen er bygd** (skjema 7): publikumsdata (2 040 anmeldelser, kafésalg), 14 roller (inkl. Kafeansvarlig og Kommunikasjon) og krav per stasjon.
- **Grønt:** full testpakke og statusporten (KLAR, 0 feil). D1–D5 er kjørt gjennom den ekte serveren.

## 2. Hvor vi slapp
- Grenen `arena` (ikke pushet). Alt er committet.
- Ikke gjort ennå: kafé- og anmeldelsescasene (dataene ligger nå i databasen), bemanningsmotoren (oppgave 08–09) og merking av `datakilde` på HR-tabellene.

## 3. Første oppgave neste gang du setter deg ned
- **Test arenaen selv:** start serveren, åpne http://127.0.0.1:8010/arena og klikk Kjør på hver case. Noter alt som skurrer eller er uforståelig, så rettes det.

## 4. Nyttige snarveier
- **Arenaen:** `py -3.13 src/kunstpixel/adapters/datafinner.py`
- **Intern assistent:** `py -3.13 src/kunstpixel/adapters/intern_hub.py` (http://127.0.0.1:8001)
- **Alle tester:** `py -3.13 -m pytest -q` · **Portvakt:** `py -3.13 scripts/db_status_gate.py`
- **Casene (rediger tekst):** `04_knowledge/07_arena/caser.yaml`
