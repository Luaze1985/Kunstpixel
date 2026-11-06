# 03: Tekst på sidene som ennå ikke er flyttet inn

**Hva:** Klarspråk og ett ord for KI på de gamle sidene, så demoen er ren også før de flyttes inn.
**Gren:** `ux/tekst` (flytt til tuppen av `ux/ett-vindu` med `git branch -f` før start) · **Må gjøres først:** ingen, kan gå parallelt med 02
**Status:** ready-for-agent · **Funn:** F2, F5, F8, F12, F15

## Indre sløyfe (0 tokens)
1. Lagre før-listen: `rg -n "LLM|AI-|Ingen sperrer|\"Live\"|Sett LLM_PROVIDER" src/kunstpixel/adapters/datafinner/{chat,arena,sok,vaktrom,arbeidsflyt}.html`.
2. For hver streng du endrer: `rg -n "<strengen>" tests/`. Får du treff, stopp og rapporter. Ikke endre testen.

## Ytre sløyfe (skjønn)
- `chat.html:82` (F2): «KI er av i denne demoen. Start med -KI for å slå den på.» Send-knappen og feltet deaktiveres når `/api/status` gir `llm: false`.
- `chat.html:37` og `arena.html:118` (F8): fjern «Ingen sperrer.» fra bannerne.
- `sok.html:89` (F5): «Slik spør LLM-en» blir «Fasit».
- `arena.html:265` (F12): «Live» blir «Kan kjøres».
- Grensemodus i `arena.html` (F15): merk casene «Krever KI», og vis KI-av-teksten fra F2 i stedet for feil 503.

## Guardrails
- Bare de fem filene over. Ikke `index.html` (erstattes i 08), ikke `ett-vindu.html` (eies av 02), ikke `af.css`.
- Bare tekstnoder og `disabled`. ID-er og klassenavn som JS bruker, endres ikke.

## Done når
1. Etter-søket fra indre sløyfe gir 0 treff i de fem filene.
2. Med KI av er Send-knappen i `/chat` deaktivert (`disabled: true`).
3. En grensecase i `/arena` med KI av viser KI-av-teksten og ingen 503-feil i konsollen.
4. Validatoren gir 15/15 på alle fem, og pytest er grønn.
