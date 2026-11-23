# Inergen-slokkeanlegg (`inergen`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Slokker brann med inert gass uten vann, så kunsten ikke skades.

| Felt | Verdi |
|---|---|
| Kategori | Sikkerhet (`sikkerhet`) |
| Leverandør (fiktiv) | Brannvern Midt AS |
| Serviceintervall | 365 dager |
| KI-tilgang | `les` (kan bare lese) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-SIK-01` | Inergen-sentral Magasin 1 | Magasin 1 – Klimastyrt lager (`MAG-1`, U1) | A | varsel | 1 | 2027-09-15 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-SIK-02` | Inergen-sentral Magasin 2 | Magasin 2 – Papirarkiv (`MAG-2`, U1) | A | i_drift | 0 | 2027-11-16 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-SIK-03` | Inergen-sentral Kunstmottak | Kunstmottak & Konservering (`VER-1`, U1) | A | i_drift | 0 | 2026-11-03 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-SIK-04` | Inergen-sentral Teknisk rom | Teknisk rom & Klimasentral (`TEK-1`, U1) | A | i_drift | 0 | 2027-06-28 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Flasketrykk | % | 15 min |
| Selvtest | resultat | ukentlig |
| Utløst | ja/nei | ved endring |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `SELVTEST_OK` | info | Ukentlig selvtest bestått |
| `TRYKK_LAVT` | varsel | Flasketrykk under 95 % |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="sikkerhet")`, og se på radene med type `inergen`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-SIK-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `kjor_selvtest` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-SIK-01", "kommando": "kjor_selvtest", "parametre": {}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M2:** Forbudte kommandoer avvises alltid (slå av slokking, alarm, kamera eller adgang, låse opp S4, overstyre heis).
- Bare lesbar for KI: bare selvtest kan foreslås.
