# Feilmeldinger

Her melder du feil i dataene, uten chatbot og uten KI. Det skal fungere som når en ansatt er på jobb, oppdager at noe ikke stemmer og sier fra til den som har ansvaret for systemet.

## Slik melder du en feil (Windows/PowerShell)

Kjør fra rotmappa i repoet:

```powershell
py -3.13 scripts/meld_feil.py
```

Nettleseren åpner http://127.0.0.1:8770. Siden kan bare nås fra din egen maskin.

1. **Hvem er du?** Velg en ansatt som er i jobb i dag (fra `hr_ansatte`), og skriv kort hva du holdt på med.
2. **Hva gjelder feilen?** Klikk på en type: kunde, medlemskap, gavekort, arrangement, verk, ansatt, dagsbesøk, årsoversikt og så videre.
3. **Finn objektet.** Søk på ID eller navn, og klikk på det.
4. **Se originalen.** Raden vises slik den står i databasen nå, sammen med kildefila. Klikk på feltet som er feil.
5. **Beskriv feilen**, og send til systemansvarlig.

Du får et meldingsnummer (FM-0001, FM-0002 og så videre).

## Hva lagres

`feilmeldinger.csv` har én rad per melding. Den er semikolondelt og lagret som UTF-8, så den kan åpnes i Excel.

| Kolonne | Innhold |
| :--- | :--- |
| `melding_id`, `meldt` | nummer og tidspunkt |
| `melder_ansatt_id`, `melder_navn`, `oppgave` | hvem som meldte, og hva de holdt på med |
| `objekttype`, `objekt_id`, `objekt_visning`, `felt` | hva feilen gjelder |
| `verdi_da` | verdien i feltet da feilen ble meldt |
| `beskrivelse`, `forslag` | hva som er feil, og hva melderen tror er riktig |
| `kilde` | fila eller tabellen originalen kommer fra |
| `original` | øyeblikksbilde av hele raden (JSON), så feilen kan sjekkes selv om dataene er endret senere |
| `mottaker`, `status`, `status_dato`, `kommentar` | systemansvarlig (byggeteamet), og status: ny, under arbeid, rettet eller avvist |

## Følge opp

```powershell
py -3.13 scripts/meld_feil.py --liste
py -3.13 scripts/meld_feil.py --liste --status ny
py -3.13 scripts/meld_feil.py --sett-status FM-0001 rettet --kommentar "Rettet i 05_data/persondata/csv/gavekort.csv"
```

Selve rettingen gjøres alltid i kilden, aldri i databasen:
- **Kundedata:** CSV-filene i `05_data/persondata/csv/`. Bygg deretter med `--fra-csv --overskriv`.
- **Museumsdata:** datafilene i `05_data/`. Bygg deretter med `build_museum_db.py`.
