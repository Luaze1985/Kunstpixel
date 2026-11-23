# Ventilasjonsaggregat (`ventilasjon`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Gir frisk luft til hele bygget og gjenvinner varmen.

| Felt | Verdi |
|---|---|
| Kategori | Bygningsanlegg (`anlegg`) |
| Leverandør (fiktiv) | Trøndelag Luft AS |
| Serviceintervall | 90 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-ANL-01` | Ventilasjonsaggregat med varmegjenvinner | Teknisk rom & Klimasentral (`TEK-1`, U1) | A | i_drift | 0 | 2027-01-12 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Luftmengde | % | 60 s |
| Trykkfall over filter | Pa | 5 min |
| Tilluftstemperatur | °C | 60 s |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `FILTER_SKITTENT` | varsel | Trykkfall over filter |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="anlegg")`, og se på radene med type `ventilasjon`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-ANL-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `sett_luftmengde` | `prosent`: 40–100 |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-ANL-01", "kommando": "sett_luftmengde", "parametre": {"prosent": 70}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
