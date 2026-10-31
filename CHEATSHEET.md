# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel | Sist oppdatert: 2026-10-31*

## 1. Hva vi gjorde sist
- **Grillet planen for arenaen** (plan: `C:\Users\larse\.claude\plans\les-siste-handoff-og-stateful-ripple.md`). Arenaen skal ha 5 områder: bemanning, tidsbruk, GDPR, økonomi og publikum. Den har 21 caser fordelt på 3 bølger.
- **Bygget bølge 1:** siden `/arena` i Datafinner med 14 caser (13 live og 1 lesecase) i dag (T1–T3, Ø1, Ø2, P2, P3, S1, G1–G5).
- Hver case viser svaret, kontrollen mot fasit, datamerket (kan dataene sendes til ekstern KI?), GDPR og gevinst, med et eget felt for antakelser.
- **Grønt:** full testpakke og statusporten (KLAR). Siden består Arbeidsflyt-validatoren.

- **Publikumsdata (syntetisk), laget lokalt uten Colab:**
  - 2 040 Google-lignende anmeldelser med ledelsens håndtering (ansvarlig, svar, svartid, tiltak)
  - fornøydhet per dag
  - kafémeny med 16 varer og salg per vare per dag
  - Skriptet er `src/kunstpixel/data/publikum_builder.py`, og skjemaversjonen er nå 6.

- **2026-10-31:** Oppgave 07 er ferdig: `05_data/stasjon_krav.csv` (13 rader), tabellen `stasjon_krav`, `core/bemanning.krav()`. Skjemaversjonen er nå **7**.
- **Drift og bunnlinje:** fire nye lesverktøy i `core/bunnlinje.py` og fire nye caser (D1 besøk mot vakter, D2 juni i pluss, D3 beste og dårligste utstillinger, D5 besøk per vakttime per team). Arenaen har nå 18 caser.

## 2. Hvor vi slapp
- Grenen `arena`. Bølge 1 er ferdig.
- Mangler i bølgen: **D4** (resultat 2010–2026). H5-historikken er bevisst skjermet fra åpne Datafinner (`tests/test_h5_governance.py`), så du må velge om den skal åpnes eller hentes via en rollestyrt vei.
- Kafé- og anmeldelsescasene venter på at du bygger databasen (tabellene finnes ikke i `museum.db` ennå).
- Deretter leverandørsjekk, helgevakt og hviletid.
- Merking av `datakilde` på HR-tabellene er **ikke** gjort: det ville ødelegge G4 (som viser at umerket data blokkeres). Tas sammen med oppgave 09.

## 3. Første oppgave neste gang du setter deg ned
- **Bygg databasen** (du gjør dette, agenten gjør det ikke): `py -3.13 src/kunstpixel/data/build_museum_db.py`. Først da kommer publikumsdataene, de nye rollene og `stasjon_krav` inn i `museum.db`.
- **Test arenaen selv:** `py -3.13 src/kunstpixel/adapters/datafinner.py` og åpne http://127.0.0.1:8010/arena. Klikk deg gjennom casene og noter det som skurrer.
- Bølge 3 (bemanningsmotoren) krever at du bygger `museum.db` etter oppgave 07. Kravlisten per stasjon er allerede godkjent.

## 4. Nyttige snarveier
- **Arenaen:** `py -3.13 src/kunstpixel/adapters/datafinner.py` → http://127.0.0.1:8010/arena
- **Casene (rediger tekst her):** `04_knowledge/07_arena/caser.yaml`. Kjør `py -3.13 -m pytest tests/test_arena_caser.py -q` etterpå.
- **Full portvakt:** `py -3.13 scripts/db_status_gate.py`
- **Intern assistent:** `py -3.13 src/kunstpixel/adapters/intern_hub.py` (http://127.0.0.1:8001)
