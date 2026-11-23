# Ladestasjoner (`lading`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Lader robotene i robotgarasjen.

| Felt | Verdi |
|---|---|
| Kategori | Bygningsanlegg (`anlegg`) |
| Leverandør (fiktiv) | Ryddig Robotikk AS |
| Serviceintervall | 180 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-LAD-01` | Ladestasjoner (10 plasser) | Robotgarasje og ladestasjon (`ROB-1`, U1) | C | i_drift | 0 | 2027-04-22 | driftsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Ladeplass i bruk | plass-nr. | ved endring |
| Ladeeffekt | W | 60 s |
| Feil på lader | status | ved endring |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `LADER_FEIL` | varsel | Ladeplass 4 svarer ikke |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="anlegg")`, og se på radene med type `lading`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-LAD-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `test_lading` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-LAD-01", "kommando": "test_lading", "parametre": {}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
