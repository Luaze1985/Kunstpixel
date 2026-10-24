# 06: Arbeidsroller i oppslagsverket (ADR-013 punkt 5)

**Hva som skal bygges:** 6–8 arbeidsroller som syntetiske data, koblet fra stilling og fra håndbokenes
målgruppe. Oppslaget kan avgrenses til én rolle.

**Må gjøres først:** 01 (håndbokindeksen bygges i bygget) og 03 (oppslagssiden finnes). Lars bekrefter
rollelisten før dataene lages.

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Akseptansekriterier
- [ ] Lars har bekreftet rollelisten. Forslaget i ordlisten er Salvert, Montør/drift, Kafé, Formidling,
      Samling/kurator, Leder og Verneombud.
- [ ] Det finnes CSV-er i `05_data/` for roller, stilling→rolle og målgruppe→rolle. `datakilde` starter med
      «syntetisk», og `tests/test_data_csv.py` er grønn.
- [ ] Byggeskriptet laster tabellene med fremmednøkler der det går. `SKJEMAVERSJON` økes. Alle stillinger i
      `hr_ansatte` og alle målgrupper i `handbok_oppslag` har minst én rolle, og en test sjekker det.
- [ ] Oppslaget tar en arbeidsrolle som filter (verktøy og side). En test viser at filteret avgrenser treffene.
- [ ] Begrepet `arbeidsrolle` i `00_felles/ordliste.yaml` er i samsvar med det som er bygget.
- [ ] `py -3.13 -m pytest -q` er grønn. Siste steg: be Lars bygge `museum.db`.
