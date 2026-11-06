# 08: Ett vindu blir forsiden

**Hva:** `/` serverer skallet. De gamle sidene (`index.html`, `chat.html`, `sok.html`, `vaktrom.html`, `arbeidsflyt.html`) flyttes til `arkiv/`. Gamle adresser videresendes til riktig visning (`/chat` → `/#flate:chat`).
**Gren:** `ux/forside` fra tuppen av `ux/ett-vindu` · **Må gjøres først:** 03, 04, 05, 06, 07 · **Status:** venter på Lars' godkjenning av skallet med alle flatene

## Indre sløyfe (0 tokens)
1. `rg -n "index.html|chat.html|sok.html|vaktrom.html|arbeidsflyt.html|/chat\b|/vaktrom\b" tests/ src/ deploy/`: liste over alt som peker på de gamle sidene.
2. `tests/test_datafinner_api.py:123` krever spørsmålslisten (`{ id: "…", tekst:`) i `index.html`. Testen må peke på den nye kilden. Lars godtar endringen i testen før den gjøres.

## Ytre sløyfe (skjønn)
- Videresending i `datafinner.py` (`ASSETS` og 302), ikke dupliserte sider.
- `start_demo.ps1` åpner `/`, og det er uendret.

## Guardrails
- Ingen sletting. Flytt med `git mv` til `arkiv/2026-11-datafinner-gamle-sider/` og legg ved en README som sier hvorfor.
- `deploy/demo` må fortsatt bestå `tests/test_deploy_demo.py`.

## Done når
1. `/` viser skallet. `/chat`, `/vaktrom`, `/sok.html` og `/arbeidsflyt` gir 302 til riktig visning.
2. `rg` fra indre sløyfe gir 0 treff utenfor `arkiv/` og videresendingene.
3. Hele pytest er grønn, og `start_demo.cmd` åpner skallet.
