# Bestilling: Jobbe med tallene i VS Code (Claude Code & Lars)
*Til: agenten i VS Code (Claude Code eller annen) og Lars · Oppdatert etter `/grill-with-docs` i Antigravity · 2026-10-20*

**Slik bruker Lars den:** åpne mappen `G:\Min disk\Kunstpixel` i VS Code, og si til agenten:
> «Les `02_deliverables/opplaering/BESTILLING-opplaeringsarena.md` og gjør steg 1 til 3. Spør meg før hver installasjon og før databasebygg.»

*(Skal oppgaven kjøres av OpenAI Codex, pek Codex til `02_deliverables/opplaering/BESTILLING-codex-tall-og-notatbok.md`.)*

**Til agenten:**
- Les også `AGENTS.md` §7 og `docs/DATAPIPELINE.md`.
- Forklar i klarspråk uten datasjargong, og still ett spørsmål om gangen.
- Kjør hver sjekk og vis resultatet. Ikke si at noe virker uten at du har kjørt det.
- PC-en er Windows med PowerShell, og Python er `py -3.13`.

---

## Steg 1: Sjekk at pakker og utvidelser er på plass (Allerede installert 2026-10-20)
Pakkene (`ipykernel==7.4.0`, `matplotlib==3.11.2`, `pandas==3.0.2`), Jupyter-kjernen `Python 3.13 (Kunstpixel)` (`kunstpixel-py313`) og de tre VS Code-utvidelsene ble installert og verifisert 2026-10-20. Kjør sjekken under for å bekrefte at alt vises:
```powershell
py -3.13 -m pip list --format=freeze | Select-String '^(ipykernel|matplotlib|pandas)=='
code --list-extensions | Select-String 'jupyter|datawrangler|sqlite-viewer'
```
Hvis noe skulle mangle på en ny maskin, spør Lars først og kjør:
```powershell
py -3.13 -m pip install ipykernel matplotlib
py -3.13 -m ipykernel install --user --name kunstpixel-py313 --display-name "Python 3.13 (Kunstpixel)"
code --install-extension ms-toolsai.jupyter
code --install-extension ms-toolsai.datawrangler
code --install-extension qwtel.sqlite-viewer
```

| Hva | Hvorfor |
|---|---|
| `ipykernel` | Lar VS Code og Antigravity kjøre notatbøker (`.ipynb`) med Python 3.13 |
| `matplotlib` | Tegner grafer rett i notatboken |
| Jupyter (`ms-toolsai.jupyter`) | Notatbøker i VS Code / Antigravity |
| Data Wrangler (`ms-toolsai.datawrangler`) | Viser en pandas-tabell som et regneark du kan sortere og filtrere |
| SQLite Viewer (`qwtel.sqlite-viewer`) | Klikk deg rundt i `museum.db` uten å skrive SQL |

**Ferdig når:** sjekkene øverst viser `ipykernel`, `matplotlib` og `pandas` i Python 3.13 samt de tre utvidelsene. Start VS Code / Antigravity på nytt hvis utvidelsene ikke vises med én gang.

---

## Steg 2: Bygg `museum.db` på nytt (Lars kjører, eller sier ja til at agenten gjør det)
`05_data/rapport_regler.csv` ble rettet etter forrige bygg, så hoveddatabasen (`05_data/museum.db`) må oppdateres. *(Vi bygger kun hoveddatabasen her, som avtalt.)*
```powershell
py -3.13 src/kunstpixel/data/build_museum_db.py
py -3.13 src/kunstpixel/data/build_museum_db.py --check
py -3.13 scripts/db_status_gate.py
```
**Ferdig når:**
- `--check` gir `LIK`, og hashen starter med `93cfcdaa` (`93cfcdaa64d1d08e226b400ec60ca81e6b54b31ca4d6daeb7c38a71886168b7b`).
- Statusporten gir `KLAR`.
- `05_data/museum.db` og `05_data/museum.db.sha256` er committet (spør Lars før `git commit`).

---

## Steg 3: Lag en notatbok for å utforske tallene (både fri utforsking og fasit-kalkulator)
1. Sørg for at `.vscode/settings.json` finnes og inneholder:
   ```json
   {
     "jupyter.notebookFileRoot": "${workspaceFolder}"
   }
   ```
2. Lag `notebooks/utforsk.ipynb`, og velg `Python 3.13 (Kunstpixel)` som kjerne (øverst til høyre i VS Code).

**Første celle (låser arbeidsmappe til prosjektroten, kobler på fasit-kalkulatorene i `db.py` og åpner databasen skrivebeskyttet):**
```python
from pathlib import Path
import os, sys, sqlite3, pandas as pd

PROSJEKT = Path.cwd()
if PROSJEKT.name == "notebooks":
    PROSJEKT = PROSJEKT.parent
os.chdir(PROSJEKT)
if str(PROSJEKT) not in sys.path:
    sys.path.insert(0, str(PROSJEKT))

from src.kunstpixel.core import db  # Ferdige fasit-kalkulatorer (lønn, overtid, sykefravær)

con = sqlite3.connect("file:05_data/museum.db?mode=ro", uri=True)   # mode=ro: kan ikke endre databasen
sql = lambda q: pd.read_sql(q, con)
sql("select name from sqlite_master where type='table' order by name")
```

**Andre celle (fri utforsking — vakter mot besøk per måned i 2026 + graf):**
```python
df = sql("""
select d.maaned, sum(d.besok_totalt) as besok, v.vakter, v.timer
from dagsbesok d
join (select maaned, count(*) as vakter, sum(timer) as timer from hr_vakter where aar = 2026 group by maaned) v using (maaned)
where d.aar = 2026 and d.er_aapent = 1
group by d.maaned order by d.maaned
""")
df["besok_per_vakttime"] = (df.besok / df.timer).round(1)
df.plot(x="maaned", y="besok_per_vakttime", kind="bar", title="Besøk per vakttime i 2026")
df
```

**Tredje celle (fasit-kalkulator fra `db.py` — lønnskostnad med kvelds-, helge- og helligdagstillegg):**
```python
# Bruker samme fasit-kalkulator som nettsiden (Datafinner), slik at kronebeløpene alltid er 100 % like
kost = db.query_shift_cost("2026-05")
df_kost = pd.DataFrame(kost["avdelinger"])
df_kost
```

**Ferdig når:** alle tre cellene kjører og viser tabeller og graf. Åpne `df` eller `df_kost` i Data Wrangler (knappen over tabellen) for å sortere og filtrere som et regneark.

---

## Slik jobber du med tallene videre (regler for agenten)
- **Utforsking er fritt.** Les med `mode=ro`, koble tabeller, lag grafer. Det kan ikke ødelegge noe.
- **Bruk fasit-kalkulatorene i `src/kunstpixel/core/db.py` først:** For lønnskostnad (`db.query_shift_cost`), sykefravær (`db.query_absence_report`) og arbeidstid/overtid (`db.query_working_hours`) skal du alltid bruke funksjonene i `db.py` fremfor å finne på ny SQL, så tallene i notatboken aldri avviker fra Datafinner.
- **Endringer i data går via filene**, aldri rett i databasen: endre CSV-en i `05_data/` (eller generatoren), kjør `py -3.13 -m pytest tests/test_data_csv.py -q`, bygg på nytt, og kjør statusporten. Oppskriften står i `docs/DATAPIPELINE.md`.
- **Hvor tallene kommer fra:** hver tabell eller graf skal kunne spores til en SQL eller en funksjon i `db.py`. Språkmodellen skriver koden, men tallene kommer fra databasen.

### Eksempler på hva Lars kan be om
- «Vis hvilke tabeller som henger sammen, og hvilke kolonner de kobles på.»
- «Bruk fasit-kalkulatoren (`db.query_shift_cost`) til å vise lønnskost per avdeling per måned i 2026 som graf.»
- «Hvilke dager har mange besøkende, men få vakter?»
- «Sammenlign museets sykefravær med SSB per kvartal (`db.query_absence_report`).»
- «Legg til en ny kolonne i en CSV, bygg på nytt, og vis at testene og statusporten fortsatt er grønne.»

## Valgfritt senere: colab-mcp
`colab-mcp` er allerede lagt inn i Claude Code og Antigravity, men ikke testet. Den åpner en Colab-fane i nettleseren og lar agenten skrive og kjøre celler der.
Test den i en ny Claude Code-økt ved å be agenten «åpne en Colab-forbindelse». Kjører Colab med Google Drive koblet til, kan agenten nå hele Drive-en din.
