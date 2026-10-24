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
- **MVP-en er bestemt:** en åpen nettside med søk i håndbøkene og et AI-svar med kilder. Den bygges i
  oppgave 02 → 03 → 04 → 05.
- **Fasiten er skrevet:** 6 vitale sjekker i `tests/test_mvp_oppslag.py`. Alle venter (xfail) til Codex har
  bygget.

## 3. Første oppgave neste gang du setter deg ned
1. Bygg databasen: `py -3.13 src/kunstpixel/data/build_museum_db.py`
2. Sjekk at bygget er likt: `py -3.13 src/kunstpixel/data/build_museum_db.py --check` skal si **LIK**.
3. Gi Codex prompten fra avsnittet «MVP» i `docs/specs/internside-oppslagsverk.md`, med NN = 02.
4. Se fremdriften når som helst: `py -3.13 -m pytest tests/test_mvp_oppslag.py -q`. Hver «x» er en
   sjekk som venter, og hver «.» er en sjekk som består.

## 4. Nyttige snarveier for dette prosjektet
- Sjekk statusport: `py -3.13 scripts/db_status_gate.py`
- Tester: `py -3.13 -m pytest -q`
- Spesifikasjon: `docs/specs/internside-oppslagsverk.md`
