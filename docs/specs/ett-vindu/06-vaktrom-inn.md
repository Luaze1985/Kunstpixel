# 06: Vaktrom inn i midten

**Hva:** Vaktrommets fem steg (Vakt, Historikk, Kandidater, Kontroll, Kontakt og utkast) vises i midten. Stegene står i venstre meny mens vaktrommet er åpent.
**Gren:** `ux/vaktrom-inn` fra tuppen av `ux/ett-vindu` etter 05 · **Må gjøres først:** 05 (samme fil)
**Status:** done 2026-11-06 på `ux/vaktrom-inn`, ikke merget

> **Beslutninger under byggingen:**
> - Skriptet er flyttet fra `vaktrom.html` til `vaktrom.js`, nesten uendret. Begge sider bruker det. `Vaktrom.start(opt)` tar et rot-element og valgfrie tilbakekall (`rolle`, `vedSteg`, `vedVakt`, `vedKall`). Den eneste endringen i Python er én linje i `ASSETS`.
> - Skallet henter markupen fra `/vaktrom`, så den finnes ett sted. `<style>` fra siden gjelder bare `#midt`.
> - Rollen i vaktrommet er «Jeg er»-rollen. Velgeren «Du er» fra `vaktrom.html` brukes ikke i skallet.
> - `#flate:vaktrom/utkast` åpner rett på «Mine kontaktutkast». Avkrysninger og utkast deles med `vaktrom.html`, fordi de bruker samme lagringsnøkkel.

## Indre sløyfe (0 tokens)
1. Les `vaktrom.html` L148–L474: stegene, verktøyene som kalles, og hvordan utkast lagres i nettleseren.
2. `rg -n "vaktrom" tests/`: hva som er låst (for eksempel `tests/test_vaktrom.py`).
3. Sjekk at kontrollen (hviletid, fravær, kurs, dobbeltbooking) kommer fra verktøyene, ikke fra JS i siden.

## Ytre sløyfe (skjønn)
- Flytt logikken. Ikke skriv den på nytt. Hvis det blir for mye JS i én fil, flytt vaktrom-JS til `vaktrom.js` og server den gjennom `ASSETS` i `datafinner.py`. Det er den eneste tillatte endringen i Python.
- Utkast lagres fortsatt bare lokalt. Ingenting sendes.

## Guardrails
- Ingen endring i bemanningsmotoren (`src/kunstpixel/core/bemanning*`) eller i verktøyene.
- `vaktrom.html` blir stående til 08.

## Done når
1. Hele flyten for én vakt (lørdag 2026-11-07, Vaktrom, 08–16) gir kandidater og kontroll i midten, uten konsollfeil.
2. Et utkast som lagres i skallet, finnes etter at siden lastes på nytt.
3. `tests/test_vaktrom.py` og hele pytest er grønne, og validatoren gir 15/15.
