# Publikumsheis (`publikumsheis`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Glassheis for besøkende mellom 1. og 2. etasje.

| Felt | Verdi |
|---|---|
| Kategori | Heiser (`heis`) |
| Leverandør (fiktiv) | Løft Trondheim AS |
| Serviceintervall | 90 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-HEI-02` | Publikumsheis | Publikumsheis P1 (`HEIS-P1`, P1) | B | i_drift | 0 | 2027-02-14 | driftsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Etasje | nr. | ved endring |
| Turer per dag | antall | daglig |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `SERVICE_VARSEL` | info | Service nærmer seg |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="heis")`, og se på radene med type `publikumsheis`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-HEI-02")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `kall_til_etasje` | `etasje`: 1–2 |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-HEI-02", "kommando": "kall_til_etasje", "parametre": {"etasje": 1}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M2:** Forbudte kommandoer avvises alltid (slå av slokking, alarm, kamera eller adgang, låse opp S4, overstyre heis).
