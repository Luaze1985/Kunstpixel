# 07: Arbeidsflyter inn i midten

**Hva:** Arbeidsflyter (oppgaver per arbeidsrolle) vises i midten.
**Gren:** `ux/arbeidsflyt-inn` fra tuppen av `ux/ett-vindu` etter 06 · **Må gjøres først:** 06 (samme fil)
**Status:** done 2026-11-06 på `ux/arbeidsflyt-inn`, ikke merget

> **Beslutninger under byggingen:**
> - B5 (Lars, 2026-11-06): to lister uten kobling. Arbeidsrollen velges inne i Arbeidsflyter, og datamodellen er uendret.
> - Adressene er `#flate:arbeidsflyt`, `…/<arbeidsrolle>` og `…/<arbeidsrolle>/<oppgave>`. Rollenavnet kodes for seg fordi navnene har skråstrek (Montør/drift).
> - «Sjekk vakt» og «Sjekk bemanning» åpner vaktrommet fra 06. Det skjemaet med fritekst-kandidat-ID fra `arbeidsflyt.html` er ikke tatt med. En dyplenke til vaktoppgaven bruker `location.replace`, så tilbakeknappen ikke havner i en løkke.
> - Felt og verktøykall er kopiert fra `arbeidsflyt.html`. Svaret vises med samme tabell som rapportene. Lokale utkast bruker samme nøkkel som før.
> - Verktøykatalogen fra `arbeidsflyt.html` er ikke tatt med. Høyre panel viser bare verktøyet som faktisk ble brukt.

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
