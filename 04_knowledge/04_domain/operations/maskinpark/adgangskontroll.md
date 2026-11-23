# Adgangskontroll (`adgangskontroll`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Kort, PIN og biometri på dører til magasiner, kunstmottak og teknikk.

| Felt | Verdi |
|---|---|
| Kategori | Sikkerhet (`sikkerhet`) |
| Leverandør (fiktiv) | Låsesmed Nidaros AS |
| Serviceintervall | 180 dager |
| KI-tilgang | `les` (kan bare lese) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-SIK-05` | Adgangskontroll (kort, PIN og biometri) | Teknisk rom for sikkerhetsanlegg (`SIK-P2`, P2) | A | i_drift | 0 | 2026-12-12 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Dørhendelser | inn/ut | ved endring |
| Dør holdt åpen | sekunder | ved endring |
| Selvtest | resultat | daglig |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `SELVTEST_OK` | info | Selvtest bestått |
| `DOR_HOLDT_APEN` | varsel | Dør holdt åpen over 60 s |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="sikkerhet")`, og se på radene med type `adgangskontroll`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-SIK-05")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `kjor_selvtest` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-SIK-05", "kommando": "kjor_selvtest", "parametre": {}}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M2:** Forbudte kommandoer avvises alltid (slå av slokking, alarm, kamera eller adgang, låse opp S4, overstyre heis).
- Bare lesbar for KI: bare selvtest kan foreslås.
