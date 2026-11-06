# 04: Chat inn i midten

**Hva:** «Flater → Chat» viser chatten i midten av skallet i stedet for et «Åpne»-kort. Fasitpanelet viser verktøyene chatten brukte.
**Gren:** `ux/chat-inn` fra tuppen av `ux/ett-vindu` etter at 02 er merget dit · **Må gjøres først:** 02 (samme fil)
**Status:** done 2026-11-06 på `ux/chat-inn`, ikke merget. Krav 2 er testet med simulert `/api/chat`-svar. Ekte KI er STATUS: UNTESTED, fordi det ikke finnes noen `.env`.

> **Beslutninger under byggingen:**
> - Rollen fra «Jeg er» sendes som `rolle`. `/api/chat` setter den inn i systemteksten («Brukeren har rollen …»).
> - Samtalen holdes i minnet mens siden er åpen, så den er der når man går ut og inn av chatten. «Ny samtale» tømmer den.
> - Eksempelet «Hva står i personalmappen til KP-ANS-006?» fra `chat.html` er ikke med. Det passer ikke i en rollestyrt demo (se 01).

## Indre sløyfe (0 tokens)
1. Les `chat.html` L72–L156: kallet mot `/api/chat`, meldingsformatet og eksempelspørsmålene.
2. Les `ett-vindu.html` L339–L350 (`visFlate`) og L85–L97 (`fasit`).
3. `rg -n "/api/chat" tests/`: kontrakten for forespørsel og svar.

## Ytre sløyfe (skjønn)
- Midten: eksempelspørsmål som kort, en meldingsliste og et skrivefelt. Med KI av: teksten fra 03/F2, og feltet er deaktivert.
- Høyre: verktøyene og kildene fra svaret til `/api/chat` (samme felter som chat.html viser).
- Rollen fra «Jeg er» sendes med hvis `/api/chat` tar en rolle. Ellers ignoreres den.

## Guardrails
- Bare `ett-vindu.html`. Ikke rør `/api/chat` eller faktasjekken (`src/kunstpixel/core/fact_check.py`).
- `chat.html` blir stående til 08.

## Done når
1. `/ett-vindu#flate:chat` med KI av viser KI-av-teksten og et deaktivert felt, uten konsollfeil.
2. Med KI på (`-KI` og `.env`) gir et eksempelspørsmål et svar i midten, og verktøyene i fasitpanelet. Uten `.env`: STATUS: UNTESTED.
3. Validatoren gir 15/15, og pytest er grønn.
