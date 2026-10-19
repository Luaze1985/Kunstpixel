# Mission: Samlingsdata og KI i drift (RAG, Fasit og Skjønn)

## Why
Lars Erik Brekne Johnsen skal beherske og trygt kunne formidle hvordan man bruker data til KI i praktisk drift. Målet er å kunne forklare forskjellen på RAG og SQL-databaser, hvorfor tall og fakta krever 100 % determinisme ("Fasit"), og hvor KI-ens resonnering og språktilpasning faktisk hører hjemme ("Skjønn"), med Kunstpixel som levende case.

## Success looks like
- Kunne forklare arkitekturen i Kunstpixel (SQLite `museum.db` + FastMCP + persona) på under 3 minutter til en kollega eller kunde.
- Tydelig kunne skille mellom når man skal bruke RAG/vektorsøk og når man må bruke deterministisk databaseoppslag/verktøykall.
- Kunne demonstrere hvordan man forhindrer KI-hallusinering på tall (telling, priser, åpningstider, bemanning) gjennom fasit-regler.
- Eie en pedagogisk modell ("Fasit vs. Skjønn") som kan gjenbrukes i kurs, foredrag og systemdesign.

## Constraints
- Bruk Kunstpixels faktiske data (16 verk, 12 kunstnere, 6 saler, HR-regler).
- Hold det pragmatisk, lokalt og uten unødvendige skytjenester.
- Læringen skal produseres som etterprøvbare, vakre HTML-leksjoner og referansedokumenter.

## Out of scope
- Tung matematisk dypdykk i LLM-oppmerksomhetsmekanismer (transformer-arkitektur).
- Sky-deployments (AWS/Azure/GCP RAG-pipelines).
