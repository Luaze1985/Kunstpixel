# Selvkjørende kunstkasse (`kunstkasse`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Klimastyrt kasse på eget hjulunderstell. Kjører et pakket verk fra salen til magasinet via vareheisen.

| Felt | Verdi |
|---|---|
| Kategori | Roboter (`robot`) |
| Leverandør (fiktiv) | Varsom Logistikk AS |
| Serviceintervall | 60 dager |
| KI-tilgang | `foresla` (kan lese og foreslå kommandoer) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-KAS-01` | Kunstkasse 1 (selvkjørende, klimastyrt) | Robotgarasje og ladestasjon (`ROB-1`, U1) | A | i_drift | 0 | 2026-12-11 | driftsansvarlig + sikkerhetsansvarlig |
| `KP-MASK-KAS-02` | Kunstkasse 2 (selvkjørende, klimastyrt) | Robotgarasje og ladestasjon (`ROB-1`, U1) | A | i_drift | 0 | 2027-01-14 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| RF i kassen | % | 60 s |
| Temperatur i kassen | °C | 60 s |
| Støt og vibrasjon | g | 1 s |
| Posisjon | rom-ID | 2 s |
| Lokk | låst/åpent | ved endring |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `KLIMA_I_KASSE` | varsel | RF i kassen utenfor K2 under transport |
| `OPPDRAG_FULLFORT` | info | Kasse levert i magasinet |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="robot")`, og se på radene med type `kunstkasse`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-KAS-01")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `kjor_kasse_til_magasin` | `fra_rom`: rom-ID som finnes i bygget; `til_rom`: én av `MAG-1`, `MAG-2` |
| `retur_til_lading` | ingen |

Eksempel på forslag (KI-en sender, et menneske godkjenner):

```json
{"maskin_id": "KP-MASK-KAS-01", "kommando": "kjor_kasse_til_magasin", "parametre": {"fra_rom": "SAL-B", "til_rom": "MAG-1"}, "tidspunkt": "2026-11-23T21:00"}
```

Svaret har `status: "venter_godkjenning"` eller `"avvist"` med grunner. Ingenting blir utført av verktøyet (`propose_machine_command`).

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- **SEC-M4:** Kunst flyttes bare utenom åpningstid (17:00–10:00), med to personer ved S4 og via vareheisen mellom etasjer.
