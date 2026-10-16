# Leveransekontroll: museumsuke

Kildebranch: `feature/hr-simulator-syntetisk-innleie`, utgangspunkt `cc83db2`. Lokal arbeidskopi: `.worktrees/museum-week`. Ingen push, merge eller produksjonssetting er utført.

## Hva som er bygget

- Research, kilderegister, øvingsrutiner og datamangler i samme prosjekt som kode og data.
- Fire sammenhengende syntetiske uker med faste oppgaver, skolebesøk, montering og kveldsarrangement. Stillingsprosent, ferdigheter, opplæring, tilgjengelighet, avtalte vakter og kontaktstatus er eksplisitte.
- Deterministisk ukekontroll av rolledekning, overlapp, tilgjengelighet, kompetanse, opplæring, ukekapasitet og hvile over ukegrense. Ukjent historikk og avtaleforhold vises som uavklart.
- Lokal API og varig, isolert SQLite-state. Et ja er separat fra tildeling. Avmelding gjenåpner behovet, mens avtalt vakt beholdes til en egen foreslått fjerning er godkjent. Forslag og beslutninger bruker planversjon for å stoppe foreldede endringer.
- Arbeidsflate for uke, arrangement, kandidater, kontakt, simulert forslag og beslutning per endring. Demomodus har tre ulike syntetiske starttilstander, knyttet til temaene i de opprinnelige HR-001–003-scenarioene. Status lagres separat.
- OpenAI Responses API-kobling med strukturert output og etterkontroll. Feil eller ukjente referanser lager ikke tildeling. Ingen modellkjøring skjer uten eksplisitt klikk og serverkonfigurasjon.

## Bevis og avgrensning

- `py -3.13 -m pytest -v`: 153 tester besto etter at en eldre datofølsom omvisningstest ble gjort deterministisk. Nye regresjonstester dekker blant annet avmelding, nabo-uke, overbemanning, modellbegrunnelser og ulike demotilstander.
- `node --check src/kunstpixel/hr_simulator/web/app.js` og `git diff --check`: besto.
- Lokal HTTP `/api/planning/weeks/2026-10-12` svarte 200. Nettleserprøve: kontaktsvar «ja» overlevde serveromstart; nytt forslag prioriterte bekreftet kontakt; én godkjent endring overlevde arrangementsbytte og sideoppdatering. Etter siste omstart viste arbeidsflaten gjeldende udekkede behov etter delvis behandling av forslag. HR-003 viste avmeldt formidler og udekket skolebesøk. Mobilbredde ble visuelt kontrollert. Demomodus/reset er testet i API-test.
- SHA-256 for `05_data/museum.db` var identisk med original utsjekking: `9BAC0B02FE818A2AAA1770AE7956C7123E1F080AF3322F93C1F128CACF0DD36F`.
- OpenAI var ikke live-testet: `OPENAI_API_KEY` og `KUNSTPIXEL_OPENAI_MODEL` manglet i servermiljøet. Testene bruker simulerte API-svar. Dermed er faktisk modellkvalitet, kildebruk og kostnad ikke dokumentert.
- Kopien i `02_deliverables/referanse/` er hentet fra feature-branchen og har samme SHA-256 som dens HTML-demo. Den særskilte knappen «Last ned lokal HTML-demo» var ikke tilgjengelig i den åpne GitHub-kodevisningen, så en separat nedlasting via akkurat den knappen er ikke verifisert.

## Åpne punkter

1. Velg modell og konfigurer nøkkel lokalt; kjør tre ekte øvelser: normal uke, kompetansemangel og avbud. Vurder forklaringer og kilder manuelt.
2. Demomodus bruker et felles fireukers aktivitetsgrunnlag med tre ulike, isolerte starttilstander. De eldre enkeltscenarioene er koblet tematisk til ukeøvelsen, men ikke omskrevet til egne fireukers aktivitetskalendere.
3. Kapasitetsgrensen er en syntetisk øvingsregel. Faktisk tariff, innleiegrunnlag og arbeidshistorikk utenfor datavinduet krever menneskelig avklaring.
