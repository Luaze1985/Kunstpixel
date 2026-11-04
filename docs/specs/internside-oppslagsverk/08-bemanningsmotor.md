# 08: Bemanningsmotor og vurdering av ansatte (uten AI)

**Hva som skal bygges:** For en dato får Lars et forslag for hver vakt. Forslaget består av en egnet person
eller «mangel» hvis ingen er egnet. Han får også en kontroll som stopper ulovlige eller umulige forslag, og
svar på om en bestemt ansatt er egnet for en stasjon, med grunnen hvis ikke.

**Må gjøres først:** 07, fordi motoren trenger kravene.

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Akseptansekriterier
- [ ] `core/bemanning.py` har `kandidater()`, `vurder_ansatt()` og `vurder_forslag()` etter kontrakten i
      `tests/test_mvp_bemanning.py`, og `foreslaa()` virker med `konfig=None`. Merket `@VENTER_PA_08` er
      fjernet, og sjekkene består.
- [ ] Reglene kommer fra databasen: krav fra `stasjon_krav`, kurs fra `org_ansatt_kompetanse` (gyldig på
      datoen), fravær fra `hr_fravaer`, status fra `hr_ansatte` og hviletid fra
      `arbeidstid_grenser.daglig_hvile_timer`. Ingen tall er skrevet rett inn i koden.
- [ ] Fraværsårsaken (egenmelding eller sykmelding) vises aldri. Den vises bare som `FRAVAER`.
- [ ] Det deterministiske forslaget velger bare egnede personer og setter aldri samme person på to vakter som
      overlapper. Rekkefølgen er stabil: samme dato gir samme forslag.
- [ ] Verktøyene `foreslaa_bemanning(dato)` og `vurder_ansatt(ansatt_id, dato, stasjon)` er lagt i
      `mcp_server.py` og i hvitelisten i Datafinner.
- [ ] `py -3.13 -m pytest -q` er grønn, og `py -3.13 scripts/db_status_gate.py` gir KLAR.
