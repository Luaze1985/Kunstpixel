# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (museum.db, Datafinner og personvernanalysen) | Sist oppdatert: 2026-10-20 kl. 14:19*

## 1. Hva vi gjorde sist
- **Databasen er bygget på nytt** og sjekket: samme fingeravtrykk som fasit (`93cfcdaa…`), statusporten sier KLAR, og alle tester er grønne.
- **Notatboken `notebooks/utforsk.ipynb` er laget** med tre eksempler: tabelloversikt, besøk per vakttime i 2026, og lønnskostnad per avdeling.
- Alt dette er committet på grenen `hr-konsolidering`. Ingenting er pushet.

## 2. Hvor vi slapp
- Alle tre cellene i `notebooks/utforsk.ipynb` er nå kjørt med kjernen `Python 3.13 (Kunstpixel)`, slik at både tabellene og stolpediagrammet (besøk per vakttime i 2026) ligger ferdig tegnet i filen.
- `ordliste.yaml`, `BESTILLING-opplaeringsarena.md`, `datafinner/index.html` og `CHEATSHEET.md` er committet på `hr-konsolidering`.

## 3. Første oppgave neste gang du setter deg ned
- **Åpne `notebooks/utforsk.ipynb` i VS Code** — da ser du grafen og tabellene med én gang. Du kan klikke på Data Wrangler-knappen over tabellene for å sortere og filtrere som et regneark.
- Spør deretter agenten om noe du vil vite om tallene, for eksempel «Hvilke dager har mange besøkende, men få vakter?».

## 4. Nyttige snarveier for dette prosjektet
- Demoen lokalt: `py -3.13 scripts/start_demo.py` (http://127.0.0.1:8011)
- Statusport: `py -3.13 scripts/db_status_gate.py` · Tester: `py -3.13 -m pytest -q`
- Overlevering til neste agent: `.scratch/handoffs/HANDOFF-20261020-1419.md`
