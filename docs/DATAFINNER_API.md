# Datafinner-API

Et lite, lesende HTTP-API over museum.db. Det er laget slik at en språkmodell eller et annet program kan bruke det uten å kjenne koden.
Alle svar er JSON. Ingenting kan skrives til databasen.

**Prinsippet:** tall og regler kommer alltid fra databasen og faste regler (deterministisk). Et valgfritt KI-lag kan *forklare* rapportene, men
bestemmer aldri tallene, og er alltid merket **AI-forslag**.

## Hva som er testet
Alt under er testet i `tests/test_datafinner_api.py`, `tests/test_llm.py` og `scripts/test_demo_container.ps1` (Docker). KI-laget er testet mot en falsk
KI-server som etterligner formatene til OpenAI og Claude. **Det er ikke prøvd mot en ekte leverandør.**

## Innlogging
Serveren har ingen innlogging selv. Hostet ligger den bak Caddy med innlogging (se `deploy/demo/README.md`). Programmer bruker vanlig Basic-innlogging:
```bash
curl -u navn:passord https://demo.eksempel.no/api/status
```

## Adresser

| Metode | Adresse | Hva den gir |
|---|---|---|
| GET | `/api/status` | `{"llm": false, "llm_modell": null, "verktoy": 19}` |
| GET | `/api/verktoyskjema` | Alle verktøy med parametere (JSON Schema), og de seks spørsmålene |
| GET | `/api/verktoy?navn=<verktøy>&args=<json>` | Kjører ett hvitelistet verktøy |
| GET | `/api/rapport?sporsmal=<id>&args=<json>` | Deterministisk rapport: fakta, regel, vurdering, forslag, merker |
| POST | `/api/forklar` | Valgfritt. KI forklarer rapporten. 503 hvis KI-laget er av |

`args` er et URL-kodet JSON-objekt, for eksempel `%7B%22aar%22%3A2025%2C%22kvartal%22%3A2%7D`.

### Spørsmålene (`sporsmal`)
| id | Verktøy | Parametere |
|---|---|---|
| `vakt-i-dag` | `get_staff_on_shift` | (valgfritt: `dato`, `klokkeslett`) |
| `vaktplan` | `get_shifts_for_date` | `dato` (ÅÅÅÅ-MM-DD) |
| `arbeidstid` | `get_working_hours_report` | `maaned` (ÅÅÅÅ-MM) |
| `sykefravaer` | `get_absence_report` | `aar`, `kvartal` |
| `utstilling` | `get_exhibition_economy` | `exhibition_id` |
| `vaktkostnad` | `get_shift_cost_for_period` | `maaned` |

## Eksempel: deterministisk rapport
`GET /api/rapport?sporsmal=sykefravaer&args={"aar":2025,"kvartal":2}` (forkortet):
```json
{
  "sporsmal_id": "sykefravaer",
  "verktoy": "get_absence_report",
  "args": {"aar": 2025, "kvartal": 2},
  "fakta": {"periode": "2025-Q2", "aktive_ansatte": 68, "sykedager_totalt": 199, "egen_prosent": 5.55},
  "regelverdier": {"egen_prosent": 5.55},
  "vurdering": {
    "regel_id": "R-FRAV-01", "felt": "egen_prosent", "operator": "<=", "terskel": 7.0,
    "vurdering": "Museets sykefravær ligger innenfor akseptabel ramme sett opp mot kultursektoren.",
    "forslag": "Fortsett forebyggende ergonomiske tiltak og nærværsarbeid.",
    "kilde": "Personalhåndbok / HMS", "versjon": "1.0", "datakilde": "syntetisk (rapport_regler)"
  },
  "merker": {"fakta": "Bør verifiseres", "vurdering": "Systemforslag", "forslag": "Systemforslag"},
  "status": "Utkast"
}
```
Samme input gir alltid nøyaktig samme svar. Reglene ligger i tabellen `rapport_regler` (`05_data/rapport_regler.csv`): første regel som treffer vinner, ellers fallback.
`merker` bruker samme ord som designsystemet Arbeidsflyt. Ingenting er «Bekreftet» før et menneske har sett på det.

## Bruk som verktøy i en språkmodell
`/api/verktoyskjema` gir hvert verktøy som `{navn, beskrivelse, parametre}`, der `parametre` er JSON Schema. Det kan oversettes direkte:
```python
import json, urllib.request
skjema = json.load(urllib.request.urlopen("https://demo.eksempel.no/api/verktoyskjema"))["verktoy"]   # legg til innlogging ved behov

claude_verktoy = [{"name": v["navn"], "description": v["beskrivelse"], "input_schema": v["parametre"]} for v in skjema]
openai_verktoy = [{"type": "function", "function": {"name": v["navn"], "description": v["beskrivelse"], "parameters": v["parametre"]}} for v in skjema]
```
Når modellen ber om et verktøykall, kjør `GET /api/verktoy?navn=<navn>&args=<json>` og gi svaret tilbake til modellen. For en hel rapport med regel og vurdering: bruk `/api/rapport`.
Filverktøyene (`grep_mappe`, `les_fil`) er på verktøylisten. De kan bare lese tillatte mapper som faktisk er kopiert inn i kjøreområdet.

## Valgfritt KI-lag (`POST /api/forklar`)
Av som standard. Slås på med miljøvariabler på serveren:

| Variabel | Betydning |
|---|---|
| `LLM_PROVIDER` | `openai` (OpenAI og alt som snakker samme språk: Ollama, LM Studio, vLLM) eller `anthropic` (Claude). Tom = av |
| `LLM_MODEL` | Modellnavn. Påkrevd når leverandør er satt |
| `LLM_API_KEY` | Nøkkel. Kan mangle for en lokal modell. **Hemmelighet: settes bare i `.env` på serveren** |
| `LLM_BASE_URL` | Overstyrer adressen, f.eks. `http://host.docker.internal:11434/v1` for Ollama |
| `LLM_MAX_TOKENS` / `LLM_TIMEOUT` / `LLM_MAKS_PER_TIME` | 600 / 30 sekunder / 30 kall per time for hele serveren |

Kall: `POST /api/forklar` med `Content-Type: application/json` og kroppen `{"sporsmal": "vaktplan", "args": {"dato": "2026-10-20"}}`. Svaret (forkortet):
```json
{
  "tekst": "Vaktplanen viser 10 vakter ...",
  "merke": "AI-forslag",
  "status": "Utkast",
  "modell": "...", "leverandor": "anthropic",
  "tallkontroll": {"ok": true, "ukjente_tall": []},
  "rapport": { "...": "den deterministiske rapporten" }
}
```

**Sperrene (alle testet):**
- KI-en får bare den ferdige rapporten som JSON. Aldri databasen, filer eller verktøy.
- `navn`, `epost`, `telefon`, `fodselsaar`, `ansatt_id` og `godkjent_av_navn` fjernes før noe sendes ut, og lister kortes til 12 rader.
- **Tallkontroll:** hvert tall i teksten sjekkes mot rapporten. Et tall som ikke finnes der (avrunding godtas) står i `ukjente_tall`, og siden viser en advarsel. Det kan ikke sies at teksten er riktig, bare at tallene stemmer.
- Svaret er alltid `AI-forslag`. I siden blir det Bekreftet først når en person har krysset av for å godta det, og rapporten er Utkast til da.
- Maks 4 096 byte inn, grense per time for hele serveren, og avvisning av kall som kommer fra en annen nettside (Origin/Sec-Fetch-Site), så innloggingen din ikke kan brukes til å trigge kall på din regning.
- Feilmeldinger fra leverandøren sendes aldri videre (bare statuskoden), og nøkkelen vises aldri i svar eller logger.

**Feilkoder:** 400 ugyldig spørsmål eller argumenter · 403 fra en annen side · 413 for stor kropp · 415 feil Content-Type · 429 for mange kall · 502 leverandørfeil · 503 KI-laget er av · 504 tidsavbrudd.

**Risiko du bør kjenne til:**
- Teksten sendes til en ekstern leverandør. Dagens data er syntetiske. Med ekte personopplysninger trengs en vurdering (GDPR, databehandleravtale) først. En lokal modell (Ollama) holder alt på egen maskin.
- Data i rapporten sendes til modellen som tekst. En «instruksjon» skjult i en databaseverdi kunne forsøkt å styre den. Systemprompten sier at slikt skal ignoreres, men det er ikke en garanti. Derfor er tallkontrollen og godkjenningen der.
- Hver kall koster penger. Sett grensen (`LLM_MAKS_PER_TIME`) lavt, og sett en utgiftsgrense hos leverandøren.

## Ikke med (ennå)
Skriving til databasen, strømming av svar, samtale med flere runder, og egne brukere i selve API-et (innlogging gjøres foran, i Caddy).
