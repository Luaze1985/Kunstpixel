# 05: Åpen hosting av hovedversjonen

**Hva som skal bygges:** Siden kan publiseres på VPS uten innlogging, med filsøket på og AI-taket herdet.

**Må gjøres først:** 02 (bildet bruker allerede full `museum.db`) og 04 (siden skal ikke åpnes før grensen er
herdet).

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Akseptansekriterier
- [ ] `Caddyfile` er uten `basic_auth`. HTTPS, HSTS, `-Server` og `reverse_proxy` beholdes.
- [ ] `bruker.sh`, `BRUKERE_FIL` og volumet `brukere.caddy` er fjernet fra hostingoppsettet, og
      `.gitignore`/`.gitattributes` er ryddet.
- [ ] `compose.yaml` bruker `LLM_MAKS_PER_TIME: ${LLM_MAKS_PER_TIME:-20}`.
- [ ] `Dockerfile` kopierer mappene i `MAPPER` til bildet, skrivebeskyttet. Tillatelseslisten i
      `deploy/demo/Dockerfile.dockerignore` er utvidet tilsvarende, og testen i `tests/test_deploy_demo.py`
      (i dag låst til `{"src", "05_data/museum.db", "deploy/demo/requirements.txt"}`) er oppdatert.
- [ ] Et skript skriver ut alle filene som slipper gjennom `.dockerignore`, ikke bare innholdet i mappene.
      Filer som ikke er i git, for eksempel `01_inbox/raw/`, er med i listen. `deploy/demo/README.md` sier
      at Lars går gjennom listen før publisering.
- [ ] Beslutningen er skrevet inn i ADR-013 eller `decision_log.md`: Lars bestemte 2026-10-24 at filsøket er
      med på den åpne siden, og at fillisten før publisering er sikringen. Risikoavsnittet i ADR-013 nevner
      dette i tillegg til API-nøkkelen.
- [ ] `deploy/demo/README.md`, `AGENTS.md` §7 og `docs/DATAFINNER_API.md` beskriver en åpen side og
      utgiftstaket i Anthropic-konsollen som et manuelt steg.
- [ ] `py -3.13 -m pytest -q` er grønn.
- [ ] Manuelt: `scripts/test_demo_container.ps1` (krever Docker). Lars sjekker fillisten og kjører
      `/security-audit` på den. Lars setter utgiftstaket og publiserer.
