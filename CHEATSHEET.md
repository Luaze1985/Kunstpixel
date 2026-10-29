# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel | Sist oppdatert: 2026-10-29 16:05*

## 1. Hva vi gjorde sist
- **Full sammenslåing av Steg 2:** Forente Intern assistent (port 8001), 9 read-only verktøy, datapolicy, faktasjekk, LLM-lag og H5-styringsdata inn på `hr-konsolidering`.
- **Validering:** 281/281 deltester og full `scripts/db_status_gate.py` passerte (KLAR, 0 feil).
- **Git:** Alt commitet (`5b37810`) og pushet til `origin/hr-konsolidering`.

## 2. Hvor vi slapp
- Koden og databasen er 100 % grønn og à jour på GitHub.
- Klar til å ta imot neste datainnsamling eller starte lokale tjenester for visuell inspeksjon.

## 3. Første oppgave neste gang du setter deg ned
- **Kjøre opp assistentene og se løsningen:** Start `py -3.13 src/kunstpixel/adapters/intern_hub.py` (port 8001) eller `datafinner.py` (port 8010) for å teste med faktiske spørsmål.
- **For neste Colab-økt:** Bruk malen i [`01_inbox/BESTILLING_COLAB_DATAFANGST.md`](01_inbox/BESTILLING_COLAB_DATAFANGST.md) for automatisk signert eksport.

## 4. Nyttige snarveier for dette prosjektet
- **Kjør full portvakt:** `py -3.13 scripts/db_status_gate.py`
- **Start Intern Assistent:** `py -3.13 src/kunstpixel/adapters/intern_hub.py` (http://127.0.0.1:8001)
- **Start Datafinner:** `py -3.13 src/kunstpixel/adapters/datafinner.py` (http://127.0.0.1:8010)
