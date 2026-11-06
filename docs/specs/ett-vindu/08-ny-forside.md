# 08: Ett vindu blir forsiden

**Hva:** `/` serverer skallet. De gamle sidene (`index.html`, `chat.html`, `sok.html`, `vaktrom.html`, `arbeidsflyt.html`) flyttes til `arkiv/`. Gamle adresser videresendes til riktig visning (`/chat` → `/#flate:chat`).
**Gren:** `ux/ny-forside` fra tuppen av `ux/ett-vindu` · **Må gjøres først:** 03, 04, 05, 06, 07 · **Status:** done 2026-11-06 på `ux/ny-forside`, ikke merget

> **Beslutninger under byggingen:**
> - Lars godkjente skallet («merge og 08») og de tre testendringene, 2026-11-06.
> - `vaktrom.html` er ikke arkivert. Den har fått navnet `vaktrom-innhold.html` og serveres på `/vaktrom-innhold`, fordi skallet henter vaktrommets markup derfra (06). De fire andre sidene ligger i `arkiv/2026-11-datafinner-gamle-sider/`.
> - `/ett-vindu` og `/index.html` sendes til `/`. Videresendingene står i `VIDERESEND` i `datafinner.py`.
> - `/arena` er ikke en del av oppgaven og står uendret.
> - Testendringer: spørsmålstesten sjekker API == `rolle_sporsmal` == `rapport_regler`, uten HTML-kopi. Sidetesten sjekker `/vaktrom-innhold` og at `/` er skallet. Arbeidsflyttesten sjekker 302 fra `/arbeidsflyt`.
> - Avvik som ikke er rettet: `deploy/demo/README.md:104` sier at `/sok.html` gir 404, men `scripts/test_demo_container.ps1:98` sjekker 200. Nå gir adressen 302 og så 200. Containertesten er ikke kjørt.

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
