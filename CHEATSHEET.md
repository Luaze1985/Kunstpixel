# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel | Sist oppdatert: 2026-11-09 22:20*

## 1. Hva vi gjorde sist
- Flyttet fra Drive til lokalt, slo ett-vindu inn i main og byttet det gamle navnet til Kunstpixel/`KP-` overalt (også i databasen).
- Bygget en skjult datakatalog (under «Vis grunnlag» i rapporten) og «Spør KI» som svarer via **din egen Claude**, uten API-nøkkel.
- Designkritikk lagret i `docs/design/2026-11-09-designkritikk-datafinner.md`. Målet ditt (DECISIONS 15): smoothe rapporter og en LLM som krysskobler data.

## 2. Hvor vi slapp
- Ingenting er halvferdig. Alt ligger på main (`e410059`) og er ikke pushet. 2190 tester er grønne.
- Neste jobb: **rette opp design og tekst med minst 5 agenter**. Briefen står i `.scratch/handoffs/HANDOFF-2026-11-09T2220.md`.

## 3. Første oppgave neste gang du setter deg ned
- **Start en ny Claude-økt i Kunstpixel-mappa og skriv:** «Les .scratch/handoffs/HANDOFF-2026-11-09T2220.md og kjør den.»

## 4. Nyttige snarveier for dette prosjektet
- Nettsiden med KI: skrivebordssnarveien **Kunstpixel** (= `start_demo.cmd -KI`)
- Din egen Claude med dataene: `start_claude.cmd`
- Alle tester: `py -3.13 -m pytest -q`
