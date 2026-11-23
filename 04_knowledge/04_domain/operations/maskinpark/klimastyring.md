# Klimastyring per sone (`klimastyring`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Styrer temperatur og fukt i magasiner og montre etter klimasonen til rommet.

| Felt | Verdi |
|---|---|
| Kategori | Bygningsanlegg (`anlegg`) |
| Leverandør (fiktiv) | Trøndelag Luft AS |
| Serviceintervall | 90 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-ANL-04` | Klimastyring Magasin 1 | Magasin 1 – Klimastyrt lager (`MAG-1`, U1) | A | varsel | 1 | 2027-02-10 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-ANL-05` | Klimastyring Magasin 2 (papirarkiv) | Magasin 2 – Papirarkiv (`MAG-2`, U1) | A | i_drift | 0 | 2027-01-10 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-ANL-06` | Klimamontre Sal D (papirverk) | Sal D – Eksistens og modernisme (`SAL-D`, P2) | A | i_drift | 0 | 2027-01-31 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Temperatur | °C | 60 s |
| Relativ fuktighet | % | 60 s |
| Settpunkt | °C og % | ved endring |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `RF_AVVIK` | varsel | Relativ fuktighet utenfor sonen |
| `TEMP_AVVIK` | varsel | Temperatur utenfor sonen |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="anlegg")`, og se på radene med type `klimastyring`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-ANL-04")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `sett_klima` | `temperatur_c`: innenfor klimasonen K1; `rf_prosent`: innenfor klimasonen K1 |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-ANL-04", "kommando": "sett_klima", "parametre": {"temperatur_c": 18.0, "rf_prosent": 50.0}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M3:** Settpunkt må ligge innenfor klimasonen til rommet.
