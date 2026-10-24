# 03: Oppslagsside uten AI

**Hva som skal bygges:** En side med ett søkefelt i midten. Et spørsmål gir håndbokpunkter med punkt-ID,
håndbok, kapittel, avsnitt og innhold. Siden virker uten AI.

**Må gjøres først:** 02, fordi begge endrer `datafinner.py` og ellers kolliderer.

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Akseptansekriterier
- [ ] `lookup_handbook` er i `VERKTOY` med de tillatte argumentene `query`, `handbok`, `role` og `limit`, og er
      med i `/api/verktoyskjema`.
- [ ] Oppslagssiden er nåbar fra forsiden og bruker `af.css`. Innholdet settes inn med `textContent`, ikke
      `innerHTML`, og `SIKKERHETSHODER`/CSP gjelder uendret.
- [ ] En tom søkestreng gir en tydelig beskjed, ikke en feil.
- [ ] Test mot temp-bygget database: et kjent spørsmål (for eksempel «egenmelding») gir treff med alle feltene,
      og et tull-spørsmål gir en tom liste.
- [ ] `/api/status` og oppslaget virker når `LLM_PROVIDER` ikke er satt. Det er testet.
- [ ] Manuelt: Lars åpner siden lokalt (`py -3.13 src/kunstpixel/adapters/datafinner.py`) og prøver tre
      spørsmål.
- [ ] `py -3.13 -m pytest -q` er grønn.
