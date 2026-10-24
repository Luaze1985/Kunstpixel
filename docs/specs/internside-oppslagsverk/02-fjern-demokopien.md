# 02: Fjern demokopien (ADR-013 punkt 1)

**Hva som skal bygges:** Datafinner har én utgave. Docker-bildet kjører mot full `museum.db`. Innloggingen
i Caddy blir stående til oppgave 05.

**Må gjøres først:** Ingen. Dette er første oppgave i MVP.

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Akseptansekriterier
- [ ] Disse er fjernet: `src/kunstpixel/data/build_demo_db.py`, `scripts/start_demo.py`,
      `tests/test_build_demo_db.py` og `tests/test_datafinner_demo.py`.
- [ ] I `adapters/datafinner.py` er `bruk_demomodus`, `DEMO`, `FILVERKTOY`, `DEMO_SKJULTE_SIDER`, `demo`-feltet i
      `/api/status` og demoteksten i docstringen fjernet. Docstringen beskriver ikke lenger siden som
      «kun 127.0.0.1».
- [ ] Testen for demomodus i `tests/test_datafinner_api.py` er fjernet.
- [ ] `deploy/demo/Dockerfile` kopierer `05_data/museum.db` direkte, uten demotrinn og uten
      `DATAFINNER_DEMO`. `tests/test_deploy_demo.py` og `scripts/test_demo_container.ps1` er oppdatert.
- [ ] Et søk etter `DATAFINNER_DEMO`, `build_demo_db`, `bruk_demomodus`, `museum_demo` og `BEHOLD` i `src/`,
      `tests/`, `scripts/`, `deploy/`, `docs/` og `AGENTS.md` gir ingen treff, bortsett fra ADR-013 og
      historiske handoff-filer.
- [ ] `AGENTS.md` §7 og `docs/DATAPIPELINE.md` er uten demokopi og demomodus.
- [ ] MVP-fasit: merket `@VENTER_PA_02` er fjernet i `tests/test_mvp_oppslag.py`, og sjekken består.
- [ ] `py -3.13 -m pytest -q` er grønn.
