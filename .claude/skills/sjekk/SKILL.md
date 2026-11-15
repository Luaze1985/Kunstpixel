---
name: sjekk
description: Rettekommando for live-demo i Kunstpixel. Kontrollerer siste svar mot museum.db med en uavhengig kontrollør som finner fasit selv før den leser svaret. Bruk når Lars skriver /sjekk etter et svar.
---

# /sjekk

1. Start subagenten `kontrollor` én gang med denne teksten, der spørsmålet og svaret er ordrett (siste spørsmål fra Lars og ditt svar, eller det Lars angir):

   ```
   Spørsmål: <spørsmålet>
   Finn fasit først. Les svaret først etterpå.
   <<<SVAR
   <svaret>
   SVAR>>>
   ```

   Ta ikke med verktøyresultater eller egne tall.
2. Vis kontrollørens svar ordrett, og ingenting annet. Formatet står under «Output-oversikt» i `CLAUDE.md`.
3. Er noe `❌`: legg til én linje `Trolig årsak: <verktøy eller steg>`.
