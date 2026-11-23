# GPU-node for KI (`gpu_node`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Kjører språkmodellene, MCP-serveren og telemetrien lokalt i serverrommet. Ingen data forlater bygget.

| Felt | Verdi |
|---|---|
| Kategori | KI-servere (`server`) |
| Leverandør (fiktiv) | Nordlys Compute AS |
| Serviceintervall | 90 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-SRV-01` | GPU-node 1 (inferens) | KI-serverrom (`SRV-1`, U1) | A | i_drift | 0 | 2026-12-13 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-SRV-02` | GPU-node 2 (inferens) | KI-serverrom (`SRV-1`, U1) | A | feil | 1 | 2026-11-05 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-SRV-03` | GPU-node 3 (trening og test) | KI-serverrom (`SRV-1`, U1) | B | i_drift | 0 | 2026-12-14 | driftsansvarlig |
| `KP-MASK-SRV-04` | GPU-node 4 (øvingsdager) | KI-serverrom (`SRV-1`, U1) | C | i_drift | 0 | 2027-01-03 | driftsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| GPU-temperatur | °C | 30 s |
| Effektforbruk | W | 30 s |
| GPU-last | % | 30 s |
| Aktive tjenester | liste | 60 s |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `GPU_TEMP_HOY` | varsel | GPU-temperatur over 83 °C |
| `NODE_RESTART` | info | Noden startet på nytt etter oppdatering |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="server")`, og se på radene med type `gpu_node`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-SRV-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `restart_tjeneste` | `tjeneste`: én av `inferens`, `mcp`, `telemetri` |
| `sett_effektgrense` | `watt`: 300–700 |
| `flytt_last` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-SRV-01", "kommando": "restart_tjeneste", "parametre": {"tjeneste": "inferens"}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
