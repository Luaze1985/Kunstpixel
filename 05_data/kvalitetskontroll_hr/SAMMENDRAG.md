# Lokal kvalitetskontroll av syntetisk HR-arkiv

Referansedato: 2026-10-17. Kilder: CSV-filene i `05_data/`.
Originalfilene er ikke endret. Ingen rader er automatisk rettet eller slettet.

## Omfang

- ansatte: 168
- vakter: 54994
- innleie: 318
- utstillinger: 102

## Funn

- fremtidig_vakt: 662

## Vakter i arbeidskopien

- ingen_funn_i_disse_reglene: 54332
- planlagt_fremtidig: 662

Detaljene med ID-er ligger i `avvik.csv`. Persondager over 24 timer er umulige
som faktisk arbeid. Persondager over 13 timer trenger kontroll, men er ikke alene
bevis for regelbrudd. Flere poster samme dag er ikke nødvendigvis overlapp,
fordi materialet mangler klokkeslett. Fremtidige vakter er merket som informasjon
fordi arkivet er syntetisk. Ingen avvik gir grunnlag for å gjette nye tider.

`vakter_arbeidskopi.csv` inneholder alle originalradene med kontrollstatus.
`sperret` betyr dokumentert datakonflikt, `manuell_kontroll` betyr høy
dagsum, og `ingen_funn_i_disse_reglene` betyr bare at disse kontrollene
ikke fant avvik. Kopien beviser ikke klokkeslett, hvile eller lovlighet.

## Neste bruk

Retting bør skje i datageneratoren eller i en egen, gjennomgått arbeidskopi.
Dette arkivet er fortsatt ikke koblet til ukeplan-demoens personer og kandidater.
