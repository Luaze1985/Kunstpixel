# Bestilling: Jobbe med tallene i VS Code
*Til: agenten i VS Code (Claude Code eller annen) og Lars · Fra: Claude Code · 2026-10-20*

**Slik bruker Lars den:** åpne mappen `G:\Min disk\Kunstpixel` i VS Code, og si til agenten:
> «Les `02_deliverables/opplaering/BESTILLING-opplaeringsarena.md` og gjør steg 1 til 3. Spør meg før hver installasjon.»

**Til agenten:**
- Les også `AGENTS.md` §7 og `docs/DATAPIPELINE.md`.
- Forklar i klarspråk, og still ett spørsmål om gangen.
- Kjør hver sjekk og vis resultatet. Ikke si at noe virker uten at du har kjørt det.
- PC-en er Windows med PowerShell, og Python er `py -3.13`.

---

## Steg 1: Installer det som trengs (spør Lars først)
Sjekk først hva som finnes, og installer bare det som mangler:
```powershell
py -3.13 -m pip list --format=freeze | Select-String '^(ipykernel|matplotlib|pandas)=='
code --list-extensions | Select-String 'jupyter|datawrangler|sqlite-viewer'
```
Installer det som mangler (per 2026-10-20 manglet `ipykernel`, `matplotlib` og alle tre utvidelsene):
```powershell
py -3.13 -m pip install ipykernel matplotlib
code --install-extension ms-toolsai.jupyter
code --install-extension ms-toolsai.datawrangler
code --install-extension qwtel.sqlite-viewer
```

| Hva | Hvorfor |
|---|---|
| `ipykernel` | Lar VS Code kjøre notatbøker (`.ipynb`) med Python 3.13 |
| `matplotlib` | Grafer |
| Jupyter (`ms-toolsai.jupyter`) | Notatbøker i VS Code |
| Data Wrangler (`ms-toolsai.datawrangler`) | Viser en pandas-tabell som et regneark du kan sortere og filtrere |
| SQLite Viewer (`qwtel.sqlite-viewer`) | Klikk deg rundt i `museum.db` uten å skrive SQL |

**Ferdig når:** de samme sjekkene viser alle fem. Start VS Code på nytt hvis utvidelsene ikke vises.

## Steg 2: Bygg museum.db på nytt (Lars kjører, eller sier ja til at agenten gjør det)
`05_data/rapport_regler.csv` ble rettet etter forrige bygg, så databasen er utdatert.
```powershell
py -3.13 src/kunstpixel/data/build_museum_db.py
py -3.13 src/kunstpixel/data/build_museum_db.py --check
py -3.13 scripts/db_status_gate.py
```
**Ferdig når:**
- `--check` gir LIK, og hashen starter med `93cfcdaa` (skal være lik et prøvebygg 2026-10-20).
- Statusporten gir KLAR.
- `05_data/museum.db` og `05_data/museum.db.sha256` er committet.

## Steg 3: Lag en notatbok for å utforske tallene
Lag `notebooks/utforsk.ipynb`, og velg Python 3.13 som kjerne (øverst til høyre i VS Code). Første celle:
```python
import sqlite3, pandas as pd
con = sqlite3.connect("file:05_data/museum.db?mode=ro", uri=True)   # mode=ro: kan ikke endre databasen
sql = lambda q: pd.read_sql(q, con)
sql("select name from sqlite_master where type='table' order by name")
```
Andre celle, en første kobling (vakter mot besøk per måned i 2026):
```python
df = sql("""
select d.maaned, sum(d.besok_totalt) as besok, v.vakter, v.timer
from dagsbesok d
join (select maaned, count(*) as vakter, sum(timer) as timer from hr_vakter where aar = 2026 group by maaned) v using (maaned)
where d.aar = 2026 and d.er_aapent = 1
group by d.maaned order by d.maaned
""")
df["besok_per_vakttime"] = (df.besok / df.timer).round(1)
df
```
**Ferdig når:** begge cellene kjører og viser tabeller. Åpne `df` i Data Wrangler (knappen over tabellen), og lag én graf med `df.plot(x="maaned", y="besok_per_vakttime")`.

---

## Slik jobber du med tallene videre (regler for agenten)
- **Utforsking er fritt.** Les med `mode=ro`, koble tabeller, lag grafer. Det kan ikke ødelegge noe.
- **Endringer i data går via filene**, aldri rett i databasen: endre CSV-en i `05_data/` (eller generatoren), kjør `py -3.13 -m pytest tests/test_data_csv.py -q`, bygg på nytt, og kjør statusporten. Oppskriften står i `docs/DATAPIPELINE.md`.
- **Ferdige funksjoner finnes** i `src/kunstpixel/core/db.py`, for eksempel `query_shift_cost`, `query_absence_report` og `query_working_hours`. Bruk dem før du skriver ny SQL.
- **Hvor tallene kommer fra:** hver tabell eller graf skal kunne spores til en SQL eller en funksjon. Språkmodellen skriver koden, men tallene kommer fra databasen.

### Eksempler på hva Lars kan be om
- «Vis hvilke tabeller som henger sammen, og hvilke kolonner de kobles på.»
- «Koble vakter, ansatte og tariff, og vis lønnskost per avdeling per måned i 2026 som graf.»
- «Hvilke dager har mange besøkende, men få vakter?»
- «Sammenlign museets sykefravær med SSB per kvartal.»
- «Legg til en ny kolonne i en CSV, bygg på nytt, og vis at testene og statusporten fortsatt er grønne.»

## Valgfritt senere: colab-mcp
`colab-mcp` er allerede lagt inn i Claude Code og Antigravity, men ikke testet. Den åpner en Colab-fane i nettleseren og lar agenten skrive og kjøre celler der.
Test den i en ny Claude Code-økt ved å be agenten «åpne en Colab-forbindelse». Kjører Colab med Google Drive koblet til, kan agenten nå hele Drive-en din.
