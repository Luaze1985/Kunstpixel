# 09: Rapporter for Samlingsforvalter og Formidler

**Hva:** Nye rapportmaler, så Samlingsforvalter og Formidler får egne rapporter. I dag passer ingen av de 16.
**Gren:** `ux/samlingsrapporter` · **Må gjøres først:** 01 (samme CSV) · **Status:** trenger-avklaring

## Avklaring Lars må gjøre før start
Hvilke 2–3 rapporter per rolle? Forslag:
- **Samlingsforvalter:** «Verk i en sal» (`get_room_artworks`), «Tilstandsrapport for et verk» (`get_condition_report`), «Innlån til en utstilling» (`search_loans`).
  `get_condition_report` og `search_loans` finnes i `src/mcp_server.py`, men **ikke** i Datafinners hviteliste (`datafinner.VERKTOY`). Å legge dem til er en Python-endring. MCP-vokteren (`mcp-team`) må se på den før den gjøres.
- **Formidler:** «Arrangementer neste uke» (`search_events`), «Verkskort» (`get_artwork_details`), «Vanlige spørsmål fra publikum» (`search_faq`).

## Indre sløyfe (0 tokens)
1. Bekreft at verktøyene finnes: `datafinner.VERKTOY` og `/api/verktoyskjema`.
2. `tests/test_datafinner_api.py:123` krever samme sett i `datafinner_api.SPORSMAL`, `index.html`, `rolle_sporsmal` og `rapport_regler`. Alle fire må oppdateres sammen. Etter 08 gjelder den nye kilden.

## Ytre sløyfe (skjønn)
- Hver ny rapport får en regel i `05_data/rapport_regler.csv` med fallback (se `tests/test_vakter_tools.py::test_bygget_db_rapport_regler_med_fallback`).

## Guardrails
- Lars bygger `museum.db`. Agenten kjører bare `build_museum_db.py --check`.

## Done når
1. `build_museum_db.py --check` gir ingen byggefeil (bare `ULIK` før bygget).
2. Etter at Lars har bygget: «Jeg er: Samlingsforvalter» og «Jeg er: Formidler» viser hver sine rapporter på forsiden (`/`), og hver gir svar med ett klikk.
3. `tests/test_datafinner_api.py` og hele pytest er grønne.
