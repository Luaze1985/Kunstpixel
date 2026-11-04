# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel / Aura Museum | Sist oppdatert: 2026-11-01 00:20*

## 1. Hva vi gjorde sist
- **Minimalistiske plantegninger for Aura Museum:** Bygget helt rene, enkle og lesbare SVG-tegninger (U1, P1, P2) for Bispegata 9B i Trondheim uten teknisk støy, med fargekodede rom og romliste.
- **2.5D Kartviser og SSOT:** `06_kart/index.html` og `bygning_geometri.json` v2.0 er koblet sammen. 44 av 44 tester er 100 % grønne i `tests/test_building_map.py`.

## 2. Hvor vi slapp
- Alt i `06_kart/` er ferdigstilt, minimalistisk og verifisert. Webviseren kjører lokalt på port 8085 (`http://localhost:8085`).

## 3. Første oppgave neste gang du setter deg ned
- **Inspiser i nettleser:** Åpne `http://localhost:8085` (fanen «2D Blueprint») og sjekk at layouten føles like rolig og enkel som ønsket.
- **Commit i git:** Lagre endringene i `06_kart/`, `tests/test_building_map.py` og `build_map.py` til git på en ryddig commit.

## 4. Nyttige snarveier for dette prosjektet
- Start kartviser: `py -3.13 -m http.server 8085 --directory 06_kart`
- Re-kompiler kart & tegninger: `py -3.13 06_kart/build_map.py`
- Kjør karttester: `py -3.13 -m pytest tests/test_building_map.py -q`
