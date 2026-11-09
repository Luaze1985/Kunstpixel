# 05: Søk inn i midten

**Hva:** «Flater → Søk» gir søk i samling, arrangementer, publikumsinformasjon og interne sider i midten av skallet. Søket er ett felt, ikke en veiviser med tre steg.
**Gren:** `ux/sok-inn` fra tuppen av `ux/ett-vindu` etter 04 · **Må gjøres først:** 04 (samme fil)
**Status:** done 2026-11-06 på `ux/sok-inn`, ikke merget

> **Beslutninger under byggingen:**
> - Reglene (kategori → verktøy, argumenter og kolonner) er kopiert fra `sok.html`, så søket gir samme svar. Når `sok.html` arkiveres i 08, er `ett-vindu.html` eneste kilde.
> - Verk og Arrangementer kan søkes uten søkeord og viser da de første 50 treffene, som i `sok.html`. Kunstnere, Vanlige spørsmål og Interne sider krever søkeord. Saler krever valgt sal.
> - Verkskort (`get_artwork_details`) og filvisning (`les_fil`) vises under tabellen i samme vindu, og fasitpanelet følger med.

## Indre sløyfe (0 tokens)
1. Les `sok.html` L105–L331: hvilke verktøy de fem kategoriene kaller (`/api/verktoy?navn=…`) og med hvilke argumenter.
2. Sjekk at hvert verktøy finnes i `/api/verktoyskjema`.

## Ytre sløyfe (skjønn)
- Ett søkefelt og fem filterknapper (Verk, Kunstnere, Saler, Arrangementer, Vanlige spørsmål, Interne sider). Svaret vises med samme `tabell()` som rapportene.
- Fasitpanelet viser verktøyet og argumentene for søket.

## Guardrails
- Bare `ett-vindu.html`. Ingen nye verktøy i `datafinner.py`.

## Done når
1. Søk etter «Skrik» med filteret Verk gir minst ett treff i midten, og `search_collection` står i fasitpanelet.
2. Et tomt søk gir en tydelig beskjed, ikke en feil.
3. Validatoren gir 15/15, og pytest er grønn.
