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
* **`tests/`** — Automatiske tester for museumskilder, API og bemanningsøvelsen. Testene dekker avgrensede regler og er ikke en garanti for drift med ekte data.

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

### Lokal museumsuke (fiktiv bemanning)

Arbeidsflaten kjøres separat fra museumsverten. Den bruker kun syntetiske personer og en egen lokal SQLite-fil. Samlingsdatabasen `05_data/museum.db` åpnes ikke for skriving.

```powershell
py -3.13 -m pip install -e .
py -3.13 -m src.kunstpixel.hr_simulator web
```

Åpne `http://127.0.0.1:8001/`. Velg uke, vurder arrangementer og faste oppgaver, registrer kontaktsvar og lag et simulert forslag. Hver endring kan godkjennes eller avvises. Ved avmelding blir behovet synlig igjen, mens fjerning av en avtalt vakt krever egen godkjenning. Plan og beslutninger bevares i `05_data/hr_simulator/local_state.sqlite3`, som ikke legges i Git. Demomodus har tre isolerte syntetiske starttilstander knyttet til temaene i HR-001–003; variantene ligger i `05_data/hr_simulator/demo_seed.json`. `02_deliverables/referanse/hr-simulator-demo-feature-cc83db2.html` er en byte-lik kopi av HTML-prototypen fra feature-branchen.

Kildegrunnlag og egne øvingsregler finnes i `04_knowledge/04_domain/projects/hr_simulator/`. Fireukersdatasettet er `05_data/hr_simulator/planning_week.json`. Kjør `py -3.13 -m pytest` for automatiserte kontroller.

For KI-forslag må `OPENAI_API_KEY` være tilgjengelig som serverens miljøvariabel og `KUNSTPIXEL_OPENAI_MODEL` settes til et eksplisitt valgt OpenAI-modellnavn før serveren startes. Ikke legg nøkkelen i repoet eller nettleseren. Knappen «Lag KI-forslag» er deaktivert uten begge verdier. Modellsvaret kontrolleres mot samme lokale regler og endrer aldri gjeldende plan direkte. [OpenAIs dokumentasjon for strukturert output](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) beskriver metoden som brukes.
