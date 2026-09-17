# No Excuse-kildepakke

Status: normalisert arbeidsgrunnlag
Dato for pakking: 2026-09-14

## Formål

Denne mappen gjør No Excuse-materialet håndterlig for senere bruk i den digitale bedriften. Råfiler beholdes urørt under `raw/`; arbeidsfiler ligger under `normalized/`.

## Viktig kildegrense

Rapporten opplyser at Ledelse 60:2 bygger på 60 diagnostiske spørsmål, men den gjengir **ikke den eksakte ordlyden til hvert spørsmål**. Sidene 6-65 har i stedet ett tema per side, med `REFLEKSJON`, `SAMMENHENG` og `MULIGHETER`. Derfor er spørsmålene i 60-punktsbanken rekonstruert forsiktig fra sidetittelen og merket som rekonstruerte.

`REFLEKSJON` er behandlet som omtrent svar / intervjunotat. `SAMMENHENG` er No Excuse sin forklaringsramme for hvordan temaet skal forstås. `MULIGHETER` er tiltak rapporten foreslår med omfang og effekt.

## Kilder hentet

1. `raw/602-rapport-orienteringene-VBS.pdf` - original 68-siders No Excuse-rapport, datert 16.03.2026.
2. `raw/vibs-noexcuse-oppsummering.pdf` - én sides oppsummering laget i etterarbeidet.
3. `raw/vibs-noexcuse-rapport.html` - intern HTML-oppsummering, inkludert teamets refleksjoner etter rapportgjennomgang.
4. Gmail: e-post `Stikkord til morgendagens mlter` (13.03.2026) - forarbeid og rolle-/risikobilde før No Excuse-intervjuet.
5. Notion: `Forberedelse – NoExcuse-møte 14. mars 2026` - fire hovedrammer og spørsmål teamet skulle være forberedt på.
6. Notion: `VIBS – Firmaprofil og hvem vi er` - senere kuratert oppsummering av funn og tiltak.
7. Notion: `Teamprofilkort – Bjørn, Lars Gunnar, Lars Erik` - destillert rolle- og teamdynamikk etter intervjuet.

## Normaliserte filer

- `01_EXECUTIVE_SUMMARY.md` - kort hva rapporten faktisk konkluderer med.
- `02_60_QUESTIONS_ANSWERS_INTERPRETATION.md` - menneskelesbar bank med alle 60 temaer.
- `03_60_QUESTIONS_ANSWERS_INTERPRETATION.jsonl` - maskinlesbar bank, én JSON-post per tema.
- `04_60_QUESTIONS_ANSWERS_INTERPRETATION.csv` - tabellversjon for Excel/Sheets.
- `05_PREINTERVIEW_NOTION_GMAIL.md` - spørsmål og forarbeid før møtet.
- `06_POSTREPORT_TEAM_REFLECTIONS.md` - refleksjoner etter rapportgjennomgangen.
- `07_REUSE_RULES_FOR_DIGITAL_COMPANY.md` - hvordan materialet kan brukes senere uten å blande VIBS-svar med generiske styringsregler.

## Tekstnormalisering

PDF-teksten er hentet digitalt, ikke OCR-et. Ved normalisering er linjeskift og enkelte tydelige font-/ligaturfeil rettet (for eksempel `ﬁ` -> `fi`, `trede` -> `treffe`, `di8eranse` -> `differanse`). Innhold og vurderinger er ellers ikke omskrevet.
