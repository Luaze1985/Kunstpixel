# Beslutninger

## 2026-11-06 — Demo-databasen med én startkommando

Bestemt av Lars etter grilling. Planen ligger i `docs/plans/2026-11-06-demo-database.md`.

| Beslutning | Valg | Hvorfor |
|---|---|---|
| Første bruker | Lars, på egen PC (kurs og kundemøter) | Ingen hosting eller installasjon hos andre trengs nå |
| Flaten som åpnes | Datafinner (port 8010) | Viser best «Fasit vs. Skjønn»: tallene kommer fra databasen, og KI bare formulerer |
| Versjon | Låst git-tagg (`demo-v1`, `demo-v2` …) | Halvferdig arbeid i hovedmappen skal ikke kunne knekke demoen |
| Plassering | Lars flytter demomappen selv | Skriptet går til sin egen repo-rot og virker derfor fra hvilken som helst mappe |
| KI | Av som standard, `-KI` slår den på | Demoen virker uten nett. KI vises bare når Lars ber om det |
| Python-pakker | Globale `py -3.13`. Skriptet sjekker `mcp==1.29.1` | Ingen venv å vedlikeholde. En feil versjon stopper skriptet med en tydelig melding |
| Innhold i demo-v1 | Siste commit på main pluss startskriptet | De 18 ucommittede endringene fra 2026-11-06 kommer i demo-v2 |

Rulings under byggingen:
- `hr_cli init --reset` er ikke med. HR-tabellene ligger i `museum.db` (ADR 004), og den committede databasen har `hr_people`.
- Oppstartsjekken bruker `scripts/db_kvalitet.py --uten-bygg` og sjekksummen i `05_data/museum.db.sha256`. Begge bare leser og tar rundt 6 sekunder. `db_status_gate.py` er ikke brukt, fordi den bygger databasen to ganger og kjører hele pytest. Den er laget som port før sammenslåing.
- Datafinners KI-lag bruker `urllib` og `.env` (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`), ikke `anthropic`-pakken. Skriptet slår av KI ved å sette `LLM_PROVIDER` til et mellomrom. En variabel som allerede er satt, vinner over `.env`.
- `mcp` er låst til `==1.29.1` i `pyproject.toml`, i tråd med `AGENTS.md`.
- Skriptet bruker `$ErrorActionPreference = 'Continue'`. Med `Stop` ble stderr fra `py` en rå feil i PowerShell 5.1, og STOPP-meldingen ble skjult. Datafinner startes med `python.exe` direkte, så det er selve serveren som stoppes.

## Linjeskift i en ny utsjekk (funnet og rettet 2026-11-06, Lars valgte å rette)
- Tre tester feilet i en ny utsjekk av main `0ba51e4`: `test_leveranse_kjoring` (2) og `test_publikum_data` (1). Årsaken var `core.autocrlf=true`, som ga CRLF ved utsjekk, mens generatorene skriver LF og testene sammenligner byte for byte.
- Rettet i `.gitattributes`: `*.csv`, `01_inbox/h5_colab/*.py` og `src/kunstpixel/core/intern/leveranse*.py` får `eol=lf`. `SJEKKSUM.txt` er unntatt, fordi `skriv_colab_pakke` skriver den med plattformens linjeskift.
- Ingen filinnhold er endret, bare hvordan git sjekker ut. Hele pytest er grønn i en ny utsjekk.
- Kjent støy: `test_org_builder` skriver fire `05_data/mock_*.csv` på nytt med `\r\n`, slik at `git status` viser dem som endret selv om `git diff` er tom. Dette skjedde også før. Rett eventuelt med `lineterminator="\n"` i `org_builder.write_csv`, eller ved å la testen skrive til en temp-mappe.
