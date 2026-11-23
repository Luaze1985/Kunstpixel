# Hengerobot for bildebytte (`hengerobot`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Mobil robotarm med polstret rammegriper. Tar ned og henger opp malerier i salene, og legger dem i en kunstkasse. En konservator er alltid til stede.

| Felt | Verdi |
|---|---|
| Kategori | Roboter (`robot`) |
| Leverandør (fiktiv) | Varsom Logistikk AS |
| Serviceintervall | 45 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-HNG-01` | Hengerobot 1 (bildebytte, maks 120 kg) | Robotgarasje og ladestasjon (`ROB-1`, U1) | A | i_drift | 0 | 2026-11-02 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Gripekraft | N | 50 ms |
| Armposisjon | mm | 50 ms |
| Last i griperen | kg | 50 ms |
| Batteri | % | 30 s |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `GRIPER_KALIBRERT` | info | Griperen kalibrert mot testramme |
| `KRAFT_AVVIK` | varsel | Gripekraft over grensen, armen stoppet |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="robot")`, og se på radene med type `hengerobot`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-HNG-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `ta_ned_verk` | `rom_id`: en utstillingssal (SAL-A … SAL-E) |
| `heng_opp_verk` | `rom_id`: en utstillingssal (SAL-A … SAL-E) |
| `pakk_verk` | `kasse_id`: maskin-ID til en kunstkasse |
| `retur_til_lading` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-HNG-01", "kommando": "ta_ned_verk", "parametre": {"rom_id": "SAL-B"}, "tidspunkt": "2026-11-23T21:00"}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M4:** Kunst flyttes bare utenom åpningstid (17:00–10:00), med to personer ved S4 og via vareheisen mellom etasjer.
