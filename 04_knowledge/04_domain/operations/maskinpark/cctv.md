# Kameraovervåking (CCTV) (`cctv`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Tar opp bilde fra 48 kamera og viser dem på videoveggen i vaktrommet.

| Felt | Verdi |
|---|---|
| Kategori | Sikkerhet (`sikkerhet`) |
| Leverandør (fiktiv) | Låsesmed Nidaros AS |
| Serviceintervall | 180 dager |
| KI-tilgang | `les` (kan bare lese) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-SIK-06` | CCTV-opptak (48 kamera) | Teknisk rom for sikkerhetsanlegg (`SIK-P2`, P2) | A | i_drift | 0 | 2027-03-02 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Kamerastatus | per kamera | 10 s |
| Lagringstid igjen | døgn | 1 t |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `SELVTEST_OK` | info | Selvtest bestått |
| `KAMERA_UTFALL` | varsel | Kamera mistet bilde i 2 min |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="sikkerhet")`, og se på radene med type `cctv`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-SIK-06")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `kjor_selvtest` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-SIK-06", "kommando": "kjor_selvtest", "parametre": {}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M2:** Forbudte kommandoer avvises alltid (slå av slokking, alarm, kamera eller adgang, låse opp S4, overstyre heis).
- Bare lesbar for KI: bare selvtest kan foreslås.
