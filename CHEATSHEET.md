# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel | Sist oppdatert: 2026-10-24 kl. 14:05*

## 1. Hva vi gjorde sist
- **Oppgave 02 er ferdig:** demokopien av Datafinner er borte, det finnes nå bare én utgave.
- **Fasiten for MVP-en er skrevet:** 23 sjekker i `tests/test_mvp_oppslag.py` og `tests/test_mvp_bemanning.py`. 1 består, 22 venter på at Codex bygger.
- **Kvalitetssjekkene kjører stille:** ved åpning av VS Code, ved lagring av en CSV og ved hver commit. Resultatet står i `.scratch/kvalitet/RAPPORT.md`.
- Din `museum.db` er bygget på nytt (versjon 4) og committet.

## 2. Hvor vi slapp
- MVP-en = en åpen nettside der AI slår opp i håndbøkene, foreslår bemanning for alle vakter og vurderer om ansatte er egnet. Faste regler kontrollerer AI-en.
- Neste bygg er **oppgave 03** (oppslagsside uten AI). Ingen er startet på den.
- Full teknisk overlevering: `.scratch/handoffs/HANDOFF-20261024-1405.md`

## 3. Første oppgave neste gang du setter deg ned
- **Åpne kvalitetsrapporten** (`.scratch/kvalitet/RAPPORT.md`) og se at den sier OK eller OBS, ikke FEIL.
- **Bestill oppgave 03 hos Codex** med prompten under «MVP» i `docs/specs/internside-oppslagsverk.md` (bytt NN med 03).
- Du må selv: godkjenne kravene per stasjon før oppgave 07, og bygge `museum.db` etter 07.

## 4. Nyttige snarveier for dette prosjektet
- Fremdrift: `py -3.13 -m pytest tests/test_mvp_oppslag.py tests/test_mvp_bemanning.py -q` (`.` = ferdig, `x` = venter)
- Alle tester: `py -3.13 -m pytest -q` · Statusport: `py -3.13 scripts/db_status_gate.py`
- Databasekvalitet i klartekst: `py -3.13 scripts/db_kvalitet.py`
