# 07: Krav per stasjon (syntetiske data)

**Hva som skal bygges:** Hver av de 10 stasjonene i vaktplanen har en liste over kurs som kreves for å stå der.
Listen ligger i databasen etter bygg.

**Må gjøres først:** 04 (for rekkefølgen i MVP; oppgaven rører ikke de samme filene). Lars godkjenner kravlisten
før dataene lages.

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Forslag til kravliste (Lars bekrefter eller endrer)
| Stasjon | Krav (skill_code) |
|---|---|
| Vaktrom / Sikkerhetssentral | vekter, forstehjelp |
| Magasin 1 (Klimastyrt lager) | kunsthandtering |
| Sal A–E | kundeservice |
| Resepsjon og billett | kasse, kundeservice |
| Museumskafé | allergen, mattrygghet |
| Museumsbutikk | kasse |

I dag har bare 3 aktive ansatte gyldig `kasse`, 5 har `vekter` og 5 har `mattrygghet`. Det gir reelle hull
i planen, og motoren skal vise dem som mangel. Den skal ikke fylle hullene med noen som ikke er egnet.

### Akseptansekriterier
- [ ] Lars har bekreftet kravlisten.
- [ ] `05_data/stasjon_krav.csv` har kolonnene `stasjon`, `skill_code` og `datakilde`. `datakilde` starter med
      «syntetisk». Stasjonsnavnene er nøyaktig som i `hr_vakter.stasjon`. `tests/test_data_csv.py` er grønn.
- [ ] Byggeskriptet laster tabellen `stasjon_krav` med fremmednøkkel til `org_ferdigheter`. `SKJEMAVERSJON` er
      økt til 5, og docstringen har fått et nytt steg.
- [ ] `core/bemanning.py` har `krav()`. Merket `@VENTER_PA_07` er fjernet i `tests/test_mvp_bemanning.py`, og
      sjekken består.
- [ ] `py -3.13 -m pytest -q` er grønn, og `py -3.13 scripts/db_status_gate.py` gir KLAR.
- [ ] Siste steg: be Lars bygge `museum.db`.
