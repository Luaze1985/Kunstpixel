# 02: Rapportvisningen i skallet

**Hva:** Rapporten i midten blir komplett. Den får kontrollpunkter, status Utkast/Bekreftet, nedlasting og en tabell som får plass.
**Gren:** `ux/rapportflyt` (flytt til tuppen av `ux/ett-vindu` med `git branch -f` før start) · **Må gjøres først:** ingen
**Status:** done 2026-11-06 på `ux/rapportflyt`, ikke merget · **Funn:** F6, F7, F13 (F1, F3 og F4 er løst i skallet)

> **Ruling under byggingen:** Statusen heter «Bekreftet», ikke «Ferdig», som i `index.html`. Det er en tredje boks, «Jeg godtar vurdering og forslag», når regelen gir et systemforslag. Da har appen bare ett sett begreper.

## Indre sløyfe (0 tokens)
1. Les `src/kunstpixel/adapters/datafinner/ett-vindu.html` L228–L292 (`tabell`, `tegnRapport`).
2. Les hvordan dagens side gjør kontroll og nedlasting: `index.html` L125 (`KONTROLL`), L568–L580 og L637–L650 (`last`).
3. Mål tabellen før endring på «HR og bemanning → Hvem har vakt i dag?» i 1280 × 800. Lagre `scrollWidth` og `clientWidth` for `.af-table-wrap`.

## Ytre sløyfe (skjønn)
- Kontroll: to avkrysningsbokser fra `KONTROLL`. Når begge er huket av, går merket fra «Utkast» til «Ferdig». Over boksene står: «Huk av kontrollpunktene for å gjøre rapporten ferdig.» (F7)
- «Last ned rapport» gir samme filformat som `index.html`. Gjenbruk logikken, ikke skriv den på nytt.
- Tabellen (F6): maks 5 kolonner i 1280 px. Lengre tekst brytes i cellen.
- Grunnlag (F13) står i `<details>`, lukket som standard. Det er allerede slik.

## Guardrails
- Bare `ett-vindu.html`. Ikke `index.html`, `datafinner.py` eller `af.css`.

## Done når
1. Etter endring er `.af-table-wrap` `scrollWidth <= clientWidth` for «Hvem har vakt i dag?» i 1280 × 800.
2. Når alle kontrollboksene er huket av, viser merket «Bekreftet». Uten avhuking viser det «Utkast».
3. «Last ned rapport» gir en fil med samme felter som nedlastingen fra `index.html`.
4. Validatoren gir 15/15, og pytest er grønn.
