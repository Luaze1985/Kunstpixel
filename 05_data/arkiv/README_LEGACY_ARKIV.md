# Dokumentasjon av Legacy Stresstest-arkiv (2010–2026)

## 1. Proveniens og Historikk
Dette arkivet inneholder de opprinnelige rådataene for syntetisk vakt- og skifthistorikk for Kunstpixel i perioden 2010–2026:
- `arkiv_hr_vakt_historikk_legacy_stresstest.csv` (48 298 rader)
- `arkiv_hr_vakt_historikk_legacy_stresstest.parquet`

Filene representerer generatordesignet før systemrevisjonen i oktober 2026.

---

## 2. Formål med Bevisbevaring (Linse p3 – Compliance og Tilsynsansvarlig)
I henhold til prinsipper for god revisjonsskikk, arbeidsrettslig etterrettelighet og compliance:
1. **Unngå bevisforspillelse:** Historiske data, selv med kjente simuleringsfeil, skal ikke destrueres sporløst ved oppdatering av kjernesystemer.
2. **Revisjonsspor:** Eventuelle historiske rapporter, stresstester og evalueringer som refererer til disse 48 298 radene skal forbli etterprøvbare.
3. **Kvalitetssikring:** Fungerer som referansepunkt (baseline) for å dokumentere forbedringer oppnådd ved ny kalender- og behovsbasert generatormodell.

---

## 3. Kjente Avvik i dette Datasettet (Kartlagt av Revisjonsteamet)
- **Kalender-blackout:** Generatoren benyttet `randint(1, 28)`. Dagene 29, 30 og 31 mangler i samtlige måneder i hele 16-årsperioden (8,8 % av dagene manglet).
- **Fantoombemanning på stengte dager:** 2 093 vakter ble planlagt på mandager på publikumsstasjoner (resepsjon, kafé, butikk) til tross for at museet er stengt for publikum.
- **Døgnovertredelser:** 4 759 persondager med registrert arbeidstid > 13 timer, hvorav 36 persondager overskred 24 timer (opptil 35,5 timer per døgn).
- **Fiktiv stasjon:** 4 686 vakter ble feilaktig tilordnet «Sal F (Skulptur)», som ikke eksisterer i museumsbygget eller i samlingsdatabasen.
- **Underdekning:** 99,5 % av dagene hadde utilstrekkelig bemanningsdekning (< 10 stasjoner).
- **Stillingsandel-skjevhet:** Heltidsansatte ble tildelt 8–12 vakter per måned (30–60 % FTE) i stedet for forventede ~21–22 vakter.

---

## 4. Gjeldende Operativt Arkiv
Det aktive og kvalitetssikrede driftsarkivet finnes i rotmappen for data:
- `05_data/arkiv_hr_vakt_historikk.csv`
- `05_data/arkiv_hr_vakt_historikk.parquet`
- `05_data/kunstpixel_historikk.db` (tabell `hr_vakter`)
