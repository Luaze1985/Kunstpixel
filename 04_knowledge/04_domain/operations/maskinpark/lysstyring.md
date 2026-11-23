# Lysstyring (DALI) (`lysstyring`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Styrer spotter og arbeidslys i salene, og slukker utenom åpningstid.

| Felt | Verdi |
|---|---|
| Kategori | Bygningsanlegg (`anlegg`) |
| Leverandør (fiktiv) | Lysverk Nord AS |
| Serviceintervall | 365 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-ANL-07` | Lysstyring Sal A | Sal A – Mytologi og natur (`SAL-A`, P1) | C | i_drift | 0 | 2027-07-21 | driftsansvarlig |
| `KP-MASK-ANL-08` | Lysstyring Sal B | Sal B – Realisme og samfunn (`SAL-B`, P1) | C | i_drift | 0 | 2027-09-19 | driftsansvarlig |
| `KP-MASK-ANL-09` | Lysstyring Sal C | Sal C – Lys, farge og interiør (`SAL-C`, P2) | C | i_drift | 0 | 2027-07-06 | driftsansvarlig |
| `KP-MASK-ANL-10` | Lysstyring Sal D | Sal D – Eksistens og modernisme (`SAL-D`, P2) | B | i_drift | 0 | 2027-04-16 | driftsansvarlig |
| `KP-MASK-ANL-11` | Lysstyring Sal E | Sal E – Temporær utstilling (`SAL-E`, P1) | C | i_drift | 0 | 2027-06-30 | driftsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Lysnivå på verk | luks | 60 s |
| UV-andel | µW/lm | 15 min |
| DALI-buss | status | 10 s |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `LAMPE_DEFEKT` | info | Spot defekt |
| `DALI_FEIL` | varsel | DALI-buss svarer ikke |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="anlegg")`, og se på radene med type `lysstyring`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-ANL-07")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `sett_lysniva` | `luks`: innenfor klimasonen K2 |
| `slukk_utenom_apningstid` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-ANL-07", "kommando": "sett_lysniva", "parametre": {"luks": 200.0}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M3:** Settpunkt må ligge innenfor klimasonen til rommet.
