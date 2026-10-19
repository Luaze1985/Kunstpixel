# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (Trondheim) | Sist oppdatert: 19. oktober 2026 kl. 23:38*

## 1. Hva vi gjorde sist
- Bygget time-for-time historisk personverndatabase (439 952 rader) og forankret museet til Trondheim med 168 simulerte ansatte i bydeler som Bakklandet, Byåsen, Tiller, Ranheim og Stjørdal.
- Analyserte hvordan ufarlige data (vakter) blir sensitive når de krysses mot AtB/Trønderbanen kollektivstans, skattelister, og Virke-lønn.
- La inn en nøktern Seksjon 7 i Colab-notebooken om ansatte i hverdagsgrenseland (slitasje, tidsklemme og stram økonomi).

## 2. Hvor vi slapp
- Alle 168 profiler og Colab-notebooken ligger ferdigkjørt og synkronisert med Google Drive i `02_deliverables/02_rapporter/personvern_time_for_time_colab.ipynb` og `05_data/`.
- Notatboken er åpnet i Playwright-vinduet i Colab scratchpad.

## 3. Første oppgave neste gang du setter deg ned
- **Utforsk Colab-analysen:** Åpne `personvern_time_for_time_colab.ipynb` i Google Colab (eller kjør opp Playwright) og se på tabellene i Seksjon 7.

## 4. Nyttige snarveier for dette prosjektet
- Kjøre datakvalitetskontroll: `py -3.13 src/kunstpixel/data/audit_time_for_time_quality.py`
- Relevant test: `py -3.13 -m pytest -q`
