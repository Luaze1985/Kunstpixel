---
name: sjekk
description: Rettekommando for live-demo i Kunstpixel. Kontrollerer siste svar mot museum.db med en uavhengig kontrollør som finner fasit selv før den ser svaret. Bruk når Lars skriver /sjekk etter et svar.
---

# /sjekk

Kontroller det **siste spørsmålet fra Lars og ditt svar på det** (eller spørsmålet og svaret Lars angir i argumentet).

## Steg

1. **Fase 1, blind.** Start subagenten `kontrollor` med **bare spørsmålet**, ordrett. Ikke ta med svaret, verktøyresultatene eller dine egne tall. Be om fase 1 (fasit).
2. **Fase 2, dom.** Send svaret ordrett til den samme kontrolløren (SendMessage til agent-ID-en fra steg 1) og be om fase 2. Finnes ikke SendMessage, start `kontrollor` på nytt med spørsmålet, fasiten fra fase 1 og svaret, og be om fase 2.
3. **Vis bare dommen** slik kontrolløren leverte den. Ikke vis fasen 1-rapporten, ikke legg til innledning eller oppsummering, og ikke forsvar det opprinnelige svaret.
4. Er noe `❌`: én linje `Trolig årsak: <verktøy eller steg>`. Ellers ingenting.

## Regler

- Ingen omformulering av spørsmålet før fase 1. Den uavhengige fasiten er hele poenget.
- Ingen endringer i filer eller data under en sjekk.
- Hvis kontrolløren sier at spørsmålet er tvetydig, vis det og stopp der.
