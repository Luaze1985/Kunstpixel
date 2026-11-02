# AP6 – sjekkpunkt 20.10.2026

1. **Avgrensning:** Kun område 6, A–G. AP7 ikke startet.
2. **Leveranse:** `AP6_rapport.md`, `AP6_kilder.md`, `AP6_datasett_forslag.yaml`, `AP6_regler_forslag.csv`, `AP6_fasit_sporsmal.csv`, `AP6_sjekkpunkt.md`.
3. **Mengde:** 22 kilder, 10 fasitspørsmål (inkl. 8 vanskelige), 8 YAML-tabeller, 20 kontrollregler og 10 fallback-regler.
4. **Kritisk regelendring:** 01.01.2026 psykososialt arbeidsmiljø (forskrift om utførelse av arbeid kap. 1A, 2A, 3A). Presisering av eksisterende plikter, ikke spesifikt påbud om surveyverktøy.
5. **Kritisk personvernfunn:** Ingen fast universell anonymitetsgrense. MUST eksempeldokumentasjon n<6 / 6–9 / ≥10 er verktøyspesifikk, datert 15.01.2024; må kontrolleres før operativ anvendelse. KS-10-FAKTOR-grense ikke hardkodet.
6. **Skille:** Avvik ≠ varsling. Intern varslingssak ≠ ekstern varsling til offentlig myndighet. Ingen universell dagfrist for å undersøke varsel.
7. **Statistikk:** STAMI/SSB LKU-A 2022: ca. 35 000 trukket og svarprosent 51 %; må ikke brukes som distribusjon for museum. Ingen oppdiktede individuelle svar, varseltekster eller diagnoser.
8. **Kvalitetstester:** YAML valideres med PyYAML. CSV feltskjema, ID-unikhet, fallback per spørsmål, filinnhold og ZIP verifiseres.
9. **Tidligere filer:** AP2–AP5 uendret. AP0/AP1 ikke tilgjengelige som komplett lokal baseline, ikke forsøkt rekonstruert.
10. **Stoppsignal:** Vent på eksplisitt «neste» før AP7.
