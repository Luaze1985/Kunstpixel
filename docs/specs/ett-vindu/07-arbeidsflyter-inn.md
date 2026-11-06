# 07: Arbeidsflyter inn i midten

**Hva:** Arbeidsflyter (oppgaver per arbeidsrolle) vises i midten.
**Gren:** `ux/arbeidsflyt-inn` fra tuppen av `ux/ett-vindu` etter 06 · **Må gjøres først:** 06 (samme fil)
**Status:** trenger-avklaring (B5): hvordan skal de 7 arbeidsrollene (Salvert …) henge sammen med «Jeg er»-rollene (Museumsdirektør …)?

## Avklaring Lars må gjøre før start
- **(Anbefalt) To lister, tydelige navn.** «Jeg er» velger stillingsrolle, og «Arbeidsrolle» velges inne i Arbeidsflyter. Ingen endring i datamodellen.
- **Kobling.** Ny tabell som kobler arbeidsrolle til stillingsrolle. Dette er en endring i datamodellen, krever at Lars bygger, og må til `docs/DECISIONS.md` først.

## Indre sløyfe (0 tokens)
1. Les `arbeidsflyt.html` L24–L68 og svaret fra `/api/arbeidsflyt` og `/api/verktoykatalog`.

## Ytre sløyfe (skjønn)
- Oppgavene vises som kort. Ett klikk åpner verktøyet eller rapporten oppgaven peker på, inne i skallet.

## Guardrails
- Bare `ett-vindu.html`, med mindre Lars velger alternativet med kobling.

## Done når
1. Hver av de 7 arbeidsrollene viser sine oppgaver i midten, uten konsollfeil.
2. «Sjekk vakt» åpner vaktrommet fra 06 i skallet.
3. Validatoren gir 15/15, og pytest er grønn.
