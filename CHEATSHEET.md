# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel | Sist oppdatert: 2026-10-24*

## 1. Hva vi gjorde sist
- **Spesifikasjon for internsiden er skrevet:** `docs/specs/internside-oppslagsverk.md`, med seks oppgaver i
  `docs/specs/internside-oppslagsverk/`. Der står søkefelt i håndbøkene, AI-svar med kilder, fjerning av
  demokopien, åpen hosting og arbeidsroller.
- **HR-casepakken er committet:** 14 øvingscaser i `04_knowledge/06_hr_caser/`, koden i `src/kunstpixel/cases/`
  og `hr_cli.py cases`.
- Antigravity-rettingen av org-dataene (`25c45da`) ligger allerede i grenen. Den trenger ikke slås sammen.
- Testet 2026-10-24: pytest 387 består, og statusporten sier KLAR.

## 2. Hvor vi slapp
- `museum.db` er på skjemaversjon 3, men koden bygger versjon 4. **Du må bygge den** før neste LLM starter.
- Oppgave 01 (håndbøkene leses inn i bygget) skal gjøres av Codex.

## 3. Første oppgave neste gang du setter deg ned
1. Bygg databasen: `py -3.13 src/kunstpixel/data/build_museum_db.py`
2. Sjekk at bygget er likt: `py -3.13 src/kunstpixel/data/build_museum_db.py --check` skal si **LIK**.
3. Gi Codex prompten for oppgave 01. Den står nederst i oppgavefilen
   `docs/specs/internside-oppslagsverk/01-handboker-inn-i-bygget.md`.

## 4. Nyttige snarveier for dette prosjektet
- Sjekk statusport: `py -3.13 scripts/db_status_gate.py`
- Tester: `py -3.13 -m pytest -q`
- Spesifikasjon: `docs/specs/internside-oppslagsverk.md`
