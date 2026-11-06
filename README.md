# 🏛️ Kunstpixel

> **Felles treningsarena for to gründere som bygger AI-agenter, automatiseringer og digitale løsninger.**

---

### Hva er Kunstpixel?

Kunstpixel er et mellomstort samtidskunstmuseum i en regional storby (som Kristiansand eller Trondheim), drevet i skjæringspunktet mellom offentlige tilskudd og egne kommersielle inntekter fra billetter og kafé.

Dette gir oss en realistisk treningsarena på vår felles hjemmebane, der hverdagen preges av spredte data, knappe ressurser og strenge rapporteringskrav.

Vårt mål er å teste hvor raskt vi to kan få full oversikt over en slik virksomhet, bygge en treffsikker data-arkitektur og rulle ut trygge automatiseringer og kampanjer med lav risiko.

Slik beviser vi i praksis hvordan vi sammen kan hjelpe virksomheter med å gå fra datakaos til målbar forretningsverdi.

---

### 📂 Hvordan prosjektet er bygget opp

* **`00_felles/`** — Vårt felles formål (`FORMAAL.md`) og en enkel begrepsordliste (`ordliste.yaml`).
* **`01_inbox/`** — Råmateriale, møtenotater og nye idéutkast.
* **`02_deliverables/`** — Ferdige kampanjer, søknader, artikler og rapporter.
* **`03_team/`** — Oversikt over hvem som gjør hva (mennesker og digitale assistenter).
* **`04_knowledge/`** — Kunnskapsbase: retningslinjer, rutiner og bygningsplaner.
* **`05_data/`** — Samlingsdatabasen (kunstverk, arrangementer, kafémeny og FAQ).
* **`src/`** — Maskinrommet: Python-skriptene som driver søk og automatisering.
* **`tests/`** — Sikkerhetsnett med automatiserte tester som garanterer at alt fungerer.

---

### ▶️ Start demoen

Dobbeltklikk på **`start_demo.cmd`** i prosjektmappen. Fra terminalen:

```powershell
.\start_demo.cmd          # eller: powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1
```

Skriptet sjekker Python 3.13, `mcp` 1.29.1, at port 8010 er ledig, sjekksummen til `museum.db`, datakvaliteten og en selvtest (16 verk, 12 kunstnere, 6 saler). Deretter åpner det Datafinner på `http://127.0.0.1:8010`. Stopp med Ctrl+C.

* KI er av som standard. Legg til `-KI` for å slå den på. Det krever `LLM_PROVIDER`, `LLM_MODEL` og `LLM_API_KEY` i `.env` i den samme mappen. Mangler de, starter demoen uten KI.
* Demoen kjøres fra en låst versjon. Sjekk ut taggen (for eksempel `git checkout demo-v1`) i en egen mappe, og start derfra.
* Skriptet leser bare. Det skriver aldri til databasen og installerer ingenting.

---

### ⚡ Rask test i terminalen

For å starte en samtale med den digitale museumsverten vår:

```powershell
py -3.13 src/cli.py
```

Eller still et direkte spørsmål:

```powershell
py -3.13 src/cli.py "Hvor finner jeg Skrik?"
```
