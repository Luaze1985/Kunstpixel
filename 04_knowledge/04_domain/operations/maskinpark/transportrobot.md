# Transportrobot (`transportrobot`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Frakter kunstkasser, emballasje og utstyr mellom magasin, kunstmottak og saler.

| Felt | Verdi |
|---|---|
| Kategori | Roboter (`robot`) |
| Leverandør (fiktiv) | Varsom Logistikk AS |
| Serviceintervall | 45 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-TRA-01` | Transportrobot 1 (kunst, løft 400 kg) | Robotgarasje og ladestasjon (`ROB-1`, U1) | A | i_drift | 0 | 2026-11-04 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-TRA-02` | Transportrobot 2 (emballasje og utstyr) | Robotgarasje og ladestasjon (`ROB-1`, U1) | B | i_drift | 0 | 2026-12-02 | driftsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Batteri | % | 30 s |
| Posisjon | rom-ID | 2 s |
| Last | kg | 1 s |
| Støt og vibrasjon | g | 1 s |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `LAST_SENSOR` | varsel | Avvik på lastsensor |
| `OPPDRAG_FULLFORT` | info | Transportoppdrag fullført |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="robot")`, og se på radene med type `transportrobot`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-TRA-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `flytt_verk` | `fra_rom`: rom-ID som finnes i bygget; `til_rom`: rom-ID som finnes i bygget |
| `retur_til_lading` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-TRA-01", "kommando": "flytt_verk", "parametre": {"fra_rom": "SAL-B", "til_rom": "SAL-E"}, "tidspunkt": "2026-11-23T21:00"}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M4:** Kunst flyttes bare utenom åpningstid (17:00–10:00), med to personer ved S4 og via vareheisen mellom etasjer.
