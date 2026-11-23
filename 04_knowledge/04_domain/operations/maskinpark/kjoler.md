# Kjøleenhet i rad (`kjoler`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Kjøler serverrackene fra kald gang til varm gang.

| Felt | Verdi |
|---|---|
| Kategori | KI-servere (`server`) |
| Leverandør (fiktiv) | Stabil Kraft AS |
| Serviceintervall | 90 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-SRV-08` | Kjøleenhet i rad (serverrom) | KI-serverrom (`SRV-1`, U1) | A | i_drift | 0 | 2027-01-05 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Tilluft | °C | 30 s |
| Returluft | °C | 30 s |
| Viftehastighet | % | 60 s |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `TEMP_AVVIK` | varsel | Tilluft over 25 °C |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="server")`, og se på radene med type `kjoler`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-SRV-08")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `sett_temperatur` | `temperatur_c`: 18–27 |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-SRV-08", "kommando": "sett_temperatur", "parametre": {"temperatur_c": 22}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
