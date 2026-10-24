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
- **MVP-en er bestemt:** en åpen nettside der AI-en slår opp i håndbøkene, foreslår bemanning for alle vakter
  og vurderer om ansatte er egnet. Faste regler kontrollerer AI-forslagene. Den bygges i oppgave
  02 → 03 → 04 → 07 → 08 → 09 → 05.
- **Fasiten er skrevet:** 23 vitale sjekker i `tests/test_mvp_oppslag.py` og `tests/test_mvp_bemanning.py`.
  Alle venter (xfail) til Codex har bygget.
- **Du må godkjenne kravene per stasjon** (oppgave 07) før Codex lager dataene. Forslaget står i
  `docs/specs/internside-oppslagsverk/07-krav-per-stasjon.md`.

## 3. Første oppgave neste gang du setter deg ned
1. Bygg databasen: `py -3.13 src/kunstpixel/data/build_museum_db.py`
2. Sjekk at bygget er likt: `py -3.13 src/kunstpixel/data/build_museum_db.py --check` skal si **LIK**.
3. Gi Codex prompten fra avsnittet «MVP» i `docs/specs/internside-oppslagsverk.md`, med NN = 02.
4. Se fremdriften når som helst: `py -3.13 -m pytest tests/test_mvp_oppslag.py tests/test_mvp_bemanning.py -q`. Hver «x» er en
   sjekk som venter, og hver «.» er en sjekk som består.

## 4. Nyttige snarveier for dette prosjektet
- Sjekk statusport: `py -3.13 scripts/db_status_gate.py`
- Tester: `py -3.13 -m pytest -q`
- Spesifikasjon: `docs/specs/internside-oppslagsverk.md`
