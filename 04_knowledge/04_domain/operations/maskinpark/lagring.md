# Lagringsserver (`lagring`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Lagrer samlingsdata, bilder og logger, og tar nattlig sikkerhetskopi.

| Felt | Verdi |
|---|---|
| Kategori | KI-servere (`server`) |
| Leverandør (fiktiv) | Fjordlager Data AS |
| Serviceintervall | 180 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-SRV-05` | Lagringsserver (samling og logg) | KI-serverrom (`SRV-1`, U1) | A | i_drift | 0 | 2026-12-26 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Diskhelse (SMART) | status | 1 t |
| Ledig plass | % | 15 min |
| Siste sikkerhetskopi | tidspunkt | daglig |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `DISK_SMART` | varsel | SMART-varsel på disk |
| `BACKUP_OK` | info | Nattlig sikkerhetskopi fullført |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="server")`, og se på radene med type `lagring`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-SRV-05")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `restart_tjeneste` | `tjeneste`: én av `telemetri` |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-SRV-05", "kommando": "restart_tjeneste", "parametre": {"tjeneste": "telemetri"}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
