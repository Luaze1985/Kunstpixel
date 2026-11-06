# 01: Rapportforslag tilpasset rolle (data)

**Hva:** Ny fordeling av de 16 rapportene per rolle i `05_data/rolle_sporsmal.csv`. Museumsvert mister personalmappe.
**Gren:** `ux/rolletekster` (`b78a5a0`, ferdig kodet) · **Må gjøres først:** ingen
**Status:** venter-paa-lars. Lars bygger `museum.db`. Ingen agent bygger.

## Indre sløyfe (0 tokens)
1. `git show ux/rolletekster:05_data/rolle_sporsmal.csv`: alle 16 `sporsmal_id` fra `datafinner_api.SPORSMAL` finnes minst én gang.
2. `py -3.13 src/kunstpixel/data/build_museum_db.py --check` gir `ULIK` før bygget og `LIK` etter.

## Ytre sløyfe (skjønn)
- Begrunnelsen per rolle står i `docs/DECISIONS.md` («Rapportforslag tilpasset rolle»).
- Åpne spørsmål for Lars: skal direktøren også ha personalmappe? Passer «Økonomi per utstilling» for Kommunikasjon?

## Guardrails
- Bare Lars kjører `build_museum_db.py` uten `--check`.
- Personalmappe foreslås bare for K (HR) og O (Avdelingsleder). Det voktes av `tests/test_vakter_tools.py::test_personalmappe_bare_for_hr_og_avdelingsleder`.

## Done når
1. Lars har bygget, og `--check` gir `LIK`.
2. `py -3.13 -m pytest -q` er grønn etter bygget.
3. I `/ett-vindu` med «Jeg er: Museumsvert» står «Hvem har vakt i dag?» øverst, og «Personalmappe» finnes ikke.
