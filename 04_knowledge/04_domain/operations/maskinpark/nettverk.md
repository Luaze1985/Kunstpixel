# Nettverkskjerne og brannmur (`nettverk`)

> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.

Knytter sammen servere, roboter og anlegg, og stenger alt som ikke er tillatt utenfra.

| Felt | Verdi |
|---|---|
| Kategori | KI-servere (`server`) |
| Leverandør (fiktiv) | Fjordlager Data AS |
| Serviceintervall | 180 dager |
| KI-tilgang | `les` (kan bare lese) |

## Enheter i Kunstpixel

| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |
|---|---|---|---|---|---|---|---|
| `KP-MASK-SRV-06` | Nettverkskjerne og brannmur | KI-serverrom (`SRV-1`, U1) | A | i_drift | 0 | 2027-01-19 | driftsansvarlig + sikkerhetsansvarlig |

## Datastrøm

Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i `maskinpark.json`.

| Signal | Enhet | Hvor ofte |
|---|---|---|
| Portstatus | opp/ned | 10 s |
| Trafikk | Mbit/s | 60 s |
| Brannmurregler | versjon | ved endring |

**Hendelseskoder** (havner i `hendelser[]`):

| Kode | Alvorlighet | Betyr |
|---|---|---|
| `LINK_FLAP` | varsel | Port gikk ned og opp |
| `FW_OPPDATERT` | info | Brannmurregler oppdatert |

## Slik følger du den

1. Hele typen: `get_machine_park(kategori="server")`, og se på radene med type `nettverk`.
2. Én enhet: `get_machine_health(maskin_id="KP-MASK-SRV-06")` gir status, åpne og siste hendelser, arbeidsordrer, neste service og kommandologg.
3. Service fremover: `get_maintenance_plan(dager=30)`.
4. I kartet: `06_kart/index.html`, sonen **Maskiner**.

## Slik styrer du den

| Kommando | Parametre og grenser |
|---|---|
| `restart_tjeneste` | `tjeneste`: én av `telemetri` |

KI-en kan ikke foreslå noen av disse kommandoene; de gjøres av et menneske. `propose_machine_command` avviser dem.

**Regler som gjelder:**

- **SEC-M1:** KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.
- Bare lesbar for KI: nettverket kan ikke styres av KI-en.
