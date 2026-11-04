# Golden Prompt Spec til OpenAI Codex: Notatbok, arbeidsmappe og tall-verifikasjon
*Til: OpenAI Codex · Fra: Lars & Antigravity · 2026-10-20*

**Slik bruker Lars den i Codex:**
> «Les `02_deliverables/opplaering/BESTILLING-codex-tall-og-notatbok.md` og utfør oppdraget innenfor rammene.»

---

## MÅL
Klargjør og verifiser VS Code-arbeidsflaten for tall-utforsking ved å:
1. Opprette `.vscode/settings.json` med fast rotmappe for notatbøker.
2. Opprette og prøvekjøre `notebooks/utforsk.ipynb` med både fri SQL-utforsking (`mode=ro`) og museets autoritative fasit-kalkulatorer fra `src/kunstpixel/core/db.py`.
3. Kjøre deterministisk kontroll (`pytest`, `scripts/db_status_gate.py` og `pytest` for hele pakken) og rapportere faktisk utskrift.

## GRUNNLAG
- Les `AGENTS.md` §7, `docs/DATAPIPELINE.md` og `02_deliverables/opplaering/BESTILLING-opplaeringsarena.md`.
- Python-kjøretid på Windows: `py -3.13` (eller `python` i Linux/cloud-miljø).
- **Tillatte filer å opprette eller endre:**
  - `.vscode/settings.json` (`{"jupyter.notebookFileRoot": "${workspaceFolder}"}`)
  - `notebooks/utforsk.ipynb`
  - `00_felles/ordliste.yaml`
  - `02_deliverables/opplaering/BESTILLING-opplaeringsarena.md`

### Krav til `notebooks/utforsk.ipynb`
- **Celle 1 (Rotmappe-ankring, fasit-kalkulatorer og skrivebeskyttet kobling):**
  Må fungere uansett om kjernen starter i `notebooks/` eller i prosjektroten:
  ```python
  from pathlib import Path
  import os, sys, sqlite3, pandas as pd

  PROSJEKT = Path.cwd()
  if PROSJEKT.name == "notebooks":
      PROSJEKT = PROSJEKT.parent
  os.chdir(PROSJEKT)
  if str(PROSJEKT) not in sys.path:
      sys.path.insert(0, str(PROSJEKT))

  from src.kunstpixel.core import db  # Ferdige fasit-kalkulatorer

  con = sqlite3.connect("file:05_data/museum.db?mode=ro", uri=True)
  sql = lambda q: pd.read_sql(q, con)
  sql("select name from sqlite_master where type='table' order by name")
  ```
- **Celle 2 (Fri utforsking — vakter mot besøk per måned i 2026 + graf):**
  Kobler `dagsbesok` og `hr_vakter` for 2026 (`er_aapent = 1`), regner ut `besok_per_vakttime = (df.besok / df.timer).round(1)` og tegner stolpediagram med `df.plot(x="maaned", y="besok_per_vakttime", kind="bar")`.
- **Celle 3 (Autoritativ fasit-kalkulator fra `db.py`):**
  Kaller `db.query_shift_cost("2026-05")` og viser `pd.DataFrame(kost["avdelinger"])` slik at lønnskostnad med kvelds-, helge- og helligdagstillegg er 100 % identisk med Datafinner.

## FORBUDT
- **Rør ALDRI `05_data/museum.db`, `05_data/museum.db.sha256` eller `05_data/kilde/museum_base.db`** uten eksplisitt ordre fra Lars i en lokal økt. Codex skal kun bruke `--check` eller `scripts/db_status_gate.py` (som bygger til en midlertidig fil).
- Skriv aldri `INSERT`, `UPDATE`, `DELETE`, `DROP` eller `ALTER` mot databasen.
- Skriv ikke naiv SQL for lønnskostnad, overtid eller sykefravær når funksjonene i `src/kunstpixel/core/db.py` (`query_shift_cost`, `query_working_hours`, `query_absence_report`) dekker behovet.

## STOPP
Stopp arbeidet umiddelbart og rapporter til Lars hvis:
- `tests/test_data_csv.py` feiler.
- `scripts/db_status_gate.py` gir `BLOKKERT` (flere enn 0 feil).
- Prøvebygg i `build_museum_db.py --check` gir en annen ny-hash enn `93cfcdaa64d1d08e226b400ec60ca81e6b54b31ca4d6daeb7c38a71886168b7b`.

## VERIFISER
Kjør disse kommandoene og lim inn faktisk utskrift i sluttrapporten (skriv `UNTESTED` hvis en kommando ikke ble kjørt):
```powershell
py -3.13 -m pytest tests/test_data_csv.py -q
py -3.13 scripts/db_status_gate.py --uten-pytest
py -3.13 -m pytest -q
```
