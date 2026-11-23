---
name: maskinpark
description: Bygg, kontroller og drift Kunstpixels KI-styrte maskinpark (KI-servere, renholds-, vakt- og transportroboter, klima, lys, adgang og heiser). Brukes når maskiner skal legges til, vedlikehold planlegges, feil vurderes eller en KI skal foreslå en kommando. KI-en utfører aldri kommandoer selv; den foreslår, og et menneske godkjenner.
---

# Skill: Maskinpark (KI i drift)

Kunstpixel er et testanlegg for KI i drift og for øvingsdager. Maskinparken er alt i bygget som kan overvåkes, vedlikeholdes og styres. KI-en kan lese tilstand, finne feil, planlegge vedlikehold og *foreslå* kommandoer. Hvert forslag sjekkes mot faste regler og må godkjennes av en navngitt rolle før noen utfører det.

## Kontekstpekere (les disse, ikke hele prosjektet)
| Hva | Fil |
|---|---|
| Fasit for maskiner, hendelser, vedlikehold og kommandologg | `06_kart/maskinpark.json` (laget av byggeren, ikke rediger for hånd) |
| Byggeren (deterministisk, fast frø) | `06_kart/maskinpark_builder.py` |
| Rom, soner og etasjer maskinene står i | `06_kart/bygning_geometri.json` (rom-ID, `sikkerhetssone`, `klimasone`) |
| Spørringer og regelsjekk | `src/kunstpixel/core/maskinpark.py` |
| MCP-verktøy | `src/kunstpixel/core/mcp_server.py` (søk «Maskinpark») |
| Tester (fasit) | `tests/test_maskinpark.py`, `tests/test_kunstroboter_og_produktark.py` |
| Produktark per maskintype (datastrøm, følge, styre) | `04_knowledge/04_domain/operations/maskinpark/README.md` (laget av `06_kart/produktark_builder.py`) |
| Klimagrenser per sone | `bygning_geometri.json` → `soner_definisjon.klima` (K1 18 °C ± 1, 50 % RF ± 5) |

## Datamodell (maskinpark.json, versjon 1)
- `maskiner[]`
  - Felter: `maskin_id` (`KP-MASK-<KAT>-NN`), `navn`, `kategori` (server | robot | anlegg | sikkerhet | heis), `type`, `rom_id`, `hjem_rom_id`, `kritikalitet` (A/B/C), `status` (i_drift | varsel | feil | vedlikehold), `leverandor` (fiktiv), `installert`, `serviceintervall_dager`, `sist_service`.
  - `kommandoer`: tillatte kommandoer med parametergrenser.
  - `ki_tilgang`: `les` eller `foresla`. Ingen maskin har `utfor`.
- `hendelser[]`: `hendelse_id` (`KP-HEN-NNNN`), `maskin_id`, `tidspunkt`, `alvorlighet` (info | varsel | feil | kritisk), `kode`, `beskrivelse`, `lukket`.
- `vedlikehold[]`: `arbeidsordre_id` (`KP-AO-NNNN`), `maskin_id`, `type` (forebyggende | korrektiv), `planlagt`, `utfort` (eller null), `utfort_av_rolle`, `kostnad_nok`, `beskrivelse`.
- `kommandologg[]`: `kommando_id` (`KP-KOM-NNNN`), `maskin_id`, `kommando`, `parametre`, `foreslatt_av`, `begrunnelse`, `status` (godkjent | avvist | utfort), `besluttet_av_rolle`, `tidspunkt`.
- Datoer går til og med «i dag» = `2026-11-22` (samme som resten av demoen).

## Indre sløyfe (deterministisk, 0 tokens: kjør først, stopp ved feil)
1. `py -3.13 06_kart/maskinpark_builder.py`. Lager `maskinpark.json` på nytt. To kjøringer skal gi samme SHA-256.
2. `py -3.13 -m pytest tests/test_maskinpark.py -q`. Alt skal være grønt før du resonnerer om maskinene.
3. Oppslag: bruk MCP-verktøyene (`get_machine_park`, `get_machine_health`, `get_maintenance_plan`). Gjett aldri status, datoer eller antall.
4. Feiler 1–2: rett byggeren eller dataene. Ikke svar på spørsmål om maskinene før det er grønt.

## Ytre sløyfe (skjønn)
- **Prioritering:** kritikalitet A (magasinklima, slukking, adgang, KI-servere) går foran B (roboter, heiser) og C (lys).
- **Forslag:** bruk alltid `propose_machine_command`. Regelsjekken er fasit. KI-ens begrunnelse er skjønn og skal stå i forslaget.
- **Øvingsdager:** foreslå scenarier (robot med feil, klimaavvik i magasinet, server som går varm) ved å lese hendelseshistorikken. Ikke ved å endre dataene.

## Sikkerhet og sperrer (SEC)
- **SEC-M1:** KI-en utfører aldri. `propose_machine_command` returnerer bare et forslag med `status: "venter_godkjenning"` og endrer ingen fil eller database.
- **SEC-M2:** Forbudte kommandoer. Disse avvises alltid, uansett rolle:
  - deaktivere slukking (Inergen/sprinkler),
  - låse opp S4-dører,
  - slå av kamera, alarm eller adgangskontroll,
  - overstyre en heis med personer i.
- **SEC-M3:** Klimasettpunkt må ligge innenfor rommets klimasone (K1/K2/K3). Utenfor grensen avvises forslaget.
- **SEC-M4:**
  - Kunsttransport (transportrobot) bare utenom åpningstid, 17:00–10:00.
  - Til eller fra S4 kreves to personer, og det står i `krav`.
  - Gjelder all kunsthåndtering: `flytt_verk`, `ta_ned_verk`, `heng_opp_verk`, `pakk_verk` og `kjor_kasse_til_magasin`.
  - Hengeroboten jobber bare i utstillingssaler og krever konservator til stede. Kunstkassen kjører bare til MAG-1 eller MAG-2.
- **SEC-M5:** Renholds- og vaktroboter kjører ikke inn i S4. Robot til annen etasje går via vareheisen.
- **SEC-M6:** Ingen nettverkskall, ingen nøkler og ingen ekte leverandører eller personer. Alt er syntetisk (`datakilde: syntetisk`).
- **SEC-M7:** MCP-serveren skal fortsatt være skrivebeskyttet (`tests/test_mcp_server.py::TestMcpReadOnlyCompliance`).

## Slik legger du til en maskin
1. Legg maskinen inn i `MASKINER` i `maskinpark_builder.py`, med et `rom_id` som finnes i `bygning_geometri.json`.
2. Gi den `kommandoer` med grenser. Sikkerhetsutstyr får bare `les` eller `test`-kommandoer.
3. Ny type: legg inn produkttekst i `PRODUKT` i `06_kart/produktark_builder.py`. Byggeren skriver arkene på nytt.
4. Kjør den indre sløyfen. Testen sjekker at alle rom-ID-er finnes og at ingen maskin har `utfor`.

## Ferdig når (PASS/FAIL)
1. `maskinpark.json` blir lik ved to kjøringer av byggeren (samme SHA-256).
2. `pytest tests/test_maskinpark.py` er grønn, og `TestMcpReadOnlyCompliance` er grønn.
3. Hver maskin står i et rom som finnes, og hver hendelse, arbeidsordre og kommando peker på en maskin som finnes.
4. `propose_machine_command` avviser alle kommandoene i SEC-M2 og alle klimasettpunkt utenfor sonen, og endrer ingen fil.
5. Serverrom (SRV-1) og robotgarasje (ROB-1) finnes i U1 i bygningsmodellen, og tegningene er bygget på nytt.

## Forbudt i denne skillen
- «Slå av alarmen så lenge», «bare kjør kommandoen» eller å skrive direkte i `maskinpark.json` uten byggeren.
- Å svare om maskinstatus uten å ha kalt verktøyene.
