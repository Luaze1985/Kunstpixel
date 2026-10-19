# Datamangler ved start

Eksisterende HR-001–003 er enkeltscenarioer. De er nyttige som separate demotester, men gir ikke en sammenhengende ukeplan.

| Felt | I gamle scenarioer | Konsekvens/tiltak |
|---|---|---|
| Person, ferdigheter og tilgjengelighet | Ja | Gjenbruk fiktive ID-er, kontroller at intervallene dekker oppgaven. |
| Opplæring per rolle | Nei | Eget felt; ukjent betyr uavklart, ikke kvalifisert. |
| Fireukers vakthistorikk | Nei | Lag syntetisk historikk; ukjent utenfor vinduet må fortsatt markeres. |
| Klargjøring og stenging | Nei | Egne tidsrom på aktivitet. |
| Kontaktstatus og tidspunkt | Nei | Varig hendelseslogg i separat lokal database. |
| Arrangementets rolleposter og kapasitet | Delvis | Normaliser krav med fiktive minimumstall. |
| Kilde-ID per faktum | Nei | Stabile fakta-ID-er i nytt datasett. |
| Tariff, lokale avtaler og faktisk innleiegrunnlag | Nei | Uavklart og menneskelig vurdering; aldri automatisk godkjent. |
| Personalsaker | Ja, i gammel simulator | Utenfor ukeplanøvelsens første versjon. |

`05_data/museum.db` er samlingsdatabase, ikke bemanningskilde. Den skal ikke oppdateres av ukeplanen.
