# Renholdsrobot (`renholdsrobot`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Vasker og støvsuger publikumsarealer etter stengetid. Kjører selv til lading.

| Felt | Verdi |
|---|---|
| Kategori | Roboter (`robot`) |
| Leverandør (fiktiv) | Ryddig Robotikk AS |
| Serviceintervall | 60 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-REN-01` | Renholdsrobot 1 (1. etasje vest) | Robotgarasje og ladestasjon (`ROB-1`, U1) | B | i_drift | 0 | 2026-11-24 | driftsansvarlig |
| `KP-MASK-REN-02` | Renholdsrobot 2 (1. etasje øst) | Robotgarasje og ladestasjon (`ROB-1`, U1) | B | i_drift | 0 | 2026-12-24 | driftsansvarlig |
| `KP-MASK-REN-03` | Renholdsrobot 3 (2. etasje) | Gang hovedfløy P2 (`GANG-P2`, P2) | B | vedlikehold | 1 | 2026-12-06 | driftsansvarlig |
| `KP-MASK-REN-04` | Renholdsrobot 4 (kjeller) | Robotgarasje og ladestasjon (`ROB-1`, U1) | C | i_drift | 0 | 2026-12-12 | driftsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Batteri | % | 30 s |
| Posisjon | rom-ID | 5 s |
| Børsteslitasje | % | per runde |
| Hjulmotor | status | 5 s |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `BATTERI_LAVT` | info | Batteri under 15 %, kjørte til lading |
| `HJUL_BLOKKERT` | feil | Hjul blokkert |
| `BORSTE_SLITT` | varsel | Børste slitt |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="robot")`, og se på radene med type `renholdsrobot`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-REN-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `send_til_rom` | `rom_id`: rom-ID som finnes i bygget |
| `start_runde` | ingen |
| `pause` | ingen |
| `retur_til_lading` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-REN-01", "kommando": "send_til_rom", "parametre": {"rom_id": "SAL-B"}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M5:** Kjører ikke inn i sikringssone S4. Til annen etasje via vareheisen.
