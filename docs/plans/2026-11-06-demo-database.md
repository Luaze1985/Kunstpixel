# Plan: Låst demo av Kunstpixel med én startkommando

## Context

Lars vil ha databasen som en demo som er lett å starte. Planen er grillet, og dette er låst:

| Beslutning | Valg |
|---|---|
| Første bruker | Lars, på sin egen PC (kurs og kundemøter) |
| Det som åpnes | Datafinner, `http://127.0.0.1:8010` |
| Versjon | Låst git-tagg (`demo-v1`), ikke hovedmappen |
| Plassering | Lars flytter mappen selv. Skriptet virker uansett hvor mappen ligger. |
| KI | Av som standard, egen bryter `-KI` slår den på |
| Python-pakker | Globale `py -3.13`, skriptet sjekker at `mcp` er 1.29.1 |
| Innhold i demo-v1 | Siste commit på main pluss startskriptet. De 18 ucommittede endringene venter til demo-v2. |

Fakta jeg har sjekket mot committet kode, ikke den ucommittede kopien:
- `main` står på `0ba51e4`. Worktree-grenen min, `7b77017`, ligger bak `main`. Startgrenen må derfor lages fra `0ba51e4`, ikke fra denne worktreen.
- `datafinner.py` og `db_status_gate.py` finnes i `main`.
- Den committede `museum.db` (`git show main:05_data/museum.db`) har 56 tabeller, blant annet `hr_people`. Den har 16 verk, 12 kunstnere og 6 saler.
- `anthropic` 0.107.0 er installert globalt.
- Ifølge ADR 004 ligger HR-dataene i `museum.db`. Steget `hr_cli init` trengs derfor ikke, og det tas ut av den forrige planen.
- Datafinner startes med `py -3.13 src/kunstpixel/adapters/datafinner.py`.
- `mcp` 1.29.1 og `fastmcp` 3.4.2 er installert globalt. Det finnes ingen venv.
- `docs/DECISIONS.md` og `PLAN.md` finnes ikke ennå. `scripts/db_status_gate.py` finnes.

## Steg

### 1. Lag startskriptet på en egen gren fra main
- Opprett `scripts/start_demo.ps1` på en gren som tar utgangspunkt i siste commit på main. Hovedmappens ucommittede arbeid røres ikke.
- Skriptet gjør dette i rekkefølge og stopper med en kort norsk feilmelding:
  0. Kjører `Set-Location` til sin egen repo-rot, siden koden importerer `src.kunstpixel...`.
  1. Sjekker at `py -3.13` finnes.
  2. Sjekker at `mcp` er 1.29.1. Med `-KI` sjekker det også at `anthropic` finnes. Er noe feil, viser skriptet hvilken kommando som retter det. Skriptet installerer ingenting selv.
  2b. Stopper hvis port 8010 allerede er i bruk, for eksempel av en Datafinner fra G:. Ellers ville nettleseren åpnet feil versjon.
  3. Kjører `py -3.13 scripts/db_status_gate.py`. Jeg sjekker først at den bare leser.
  4. Selvtest som bare leser: 16 verk, 12 kunstnere og 6 saler, med `mode=ro`.
  5. Setter `KUNSTPIXEL_LLM=off`. Med `-KI` settes den til `anthropic`, og nøkkelen hentes fra `.env`. Mangler nøkkelen, skriver skriptet en tydelig melding og går videre uten KI.
  6. Starter Datafinner, venter til port 8010 svarer og åpner nettleseren.
- Skriptet skriver aldri til `museum.db`.

### 2. (Utgår) Lars flytter demomappen selv

### 3. Lås `mcp` i `pyproject.toml`
- Endre `mcp>=1.29.1` til `mcp==1.29.1`, slik `AGENTS.md` krever.

### 4. Dokumentasjon
- `README.md` får en seksjon «Start demoen» med én kommando: `powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1` (legg til `-KI` for å slå på KI).
- `docs/DECISIONS.md` opprettes med beslutningene i tabellen over.
- `PLAN.md` opprettes som kort status med lenke til planen.

### 5. Tagg og installer
- Kjør `py -3.13 -m pytest -q` på grenen. Testene må være grønne.
- Lars merger grenen til main og godkjenner taggen `demo-v1`. Jeg tagger ikke uten ja.
- Lars sjekker ut `demo-v1` i mappen han selv har valgt.

## Filer
- `scripts/start_demo.ps1` (ny)
- `pyproject.toml`
- `README.md`
- `docs/DECISIONS.md` (ny)
- `PLAN.md` (ny)

## Verifisering
1. `pytest -q` er grønn på grenen.
2. `start_demo.ps1` fra grenen: selvtesten passerer, port 8010 svarer, og ett rapportspørsmål gir tall fra databasen.
3. Negativtester: endre `mcp`-sjekken midlertidig til en feil versjon, og start skriptet mens port 8010 er opptatt. Begge skal stoppe med en tydelig melding.
4. Kjør uten nett og uten `-KI`. Demoen skal virke.
5. `-KI` er bare testet hvis `.env` har en nøkkel. Ellers rapporteres den som UNTESTED.

## Fra den første planen
- Beholdt: lås `mcp`, ett startskript, Datafinner som flate, README-seksjon, `DECISIONS.md` og `PLAN.md`, og at hosting holdes utenfor.
- Tatt ut: `hr_cli init --reset`, fordi HR-dataene allerede ligger i `museum.db` (ADR 004). `pip install -e .` er også tatt ut, siden globale pakker ble valgt.
- Endret: testen «klon til tom mappe» er erstattet av start fra grenen pluss negativtester.

## Utenfor planen
- Flytting av mappen (Lars gjør det selv).
- VPS-hosting og offentlig lenke.
- Egen venv.
- Rydding i de andre inngangene.
- De 18 ucommittede endringene, som kommer i demo-v2.
