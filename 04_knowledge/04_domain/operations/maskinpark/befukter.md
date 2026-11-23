# Dampbefukter (`befukter`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Holder fuktigheten oppe om vinteren, så kunsten ikke tørker ut.

| Felt | Verdi |
|---|---|
| Kategori | Bygningsanlegg (`anlegg`) |
| Leverandør (fiktiv) | Trøndelag Luft AS |
| Serviceintervall | 90 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-ANL-02` | Dampbefukter | Teknisk rom & Klimasentral (`TEK-1`, U1) | A | i_drift | 0 | 2027-02-08 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Ytelse | % | 60 s |
| Ledningsevne i damptank | µS/cm | 15 min |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `VANNKVALITET` | varsel | Ledningsevne høy i damptank |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="anlegg")`, og se på radene med type `befukter`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-ANL-02")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `sett_ytelse` | `prosent`: 0–100 |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-ANL-02", "kommando": "sett_ytelse", "parametre": {"prosent": 50}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
