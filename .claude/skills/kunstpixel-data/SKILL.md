---
name: kunstpixel-data
description: Datadefinisjoner for museum.db i Kunstpixel (SQLite). Hvem «ansatte» er, hvordan «i år» telles, formler for lønnskostnad, besøk, sykefravær og utstillingsøkonomi, og kjente fallgruver. Bruk før du svarer på et tallspørsmål om museet, og når kontrolløren i /sjekk skal regne fasit, slik at begge regner likt.
---

# Kunstpixel-data

Databasen er `05_data/museum.db` (SQLite, skrivebeskyttet). Tabellkatalog og JOIN-stier: `05_data/index.md`. Svarstil: `CLAUDE.md`.

## Standarddefinisjoner (DECISIONS D1–D2)

| Når Lars sier | Betyr det | SQL |
|---|---|---|
| «ansatte», «hvor mange jobber her» | nåværende: 74 av 168 | `hr_ansatte.status <> 'Sluttet'` |
| «tidligere», «historisk», et årstall før i år | alle 168 | ingen statusfilter |
| «i år», «2026», «hittil» | 1. januar til i dag | `dato BETWEEN '2026-01-01' AND date('now','localtime')` |
| «neste uke», «desember», «planlagt» | etter i dag (vaktplan, arrangementer) | `dato > date('now','localtime')` |

Dataene går til `2026-12-31`. Alt etter i dag er plan, ikke fakta. Si det når et tall inkluderer fremtiden.

## Nøkkeltall

Formler, kilder og fallgruver: [references/metrics.md](references/metrics.md).

| Nøkkeltall | Kort formel | MCP-verktøy |
|---|---|---|
| Lønnskostnad per avdeling | timer × tariffsats; helligdag > helg > kveld fra 17:00 > ordinær | `get_shift_cost_for_period` |
| Besøk og billettinntekt | `sum(besok_totalt)`, `sum(inntekt_nok)` fra `dagsbesok` | `get_daily_visitors` (krav K2, finnes ikke i alle versjoner) |
| Sykefravær | eget: dager i `hr_fravaer`; prosent bare fra SSB | `get_absence_report`, `get_sickness_absence_statistics` |
| Utstillingsøkonomi | `netto_resultat_nok` = inntekter − `faktisk_totalkostnad_nok` | `get_exhibition_economy` |

## Entiteter

Hvem er hvem, ID-er og navnelikhet: [references/entities.md](references/entities.md).

## Domener

| Domene | Fil | Brukes til |
|---|---|---|
| HR og vakter | [references/tables/hr.md](references/tables/hr.md) | ansatte, vakter, fravær, samtaler, innleie |
| Publikum og kafé | [references/tables/publikum.md](references/tables/publikum.md) | besøk, inntekt, anmeldelser, kafésalg |
| Utstillinger | [references/tables/utstilling.md](references/tables/utstilling.md) | historikk, økonomi, innlån |
| Drift og HMS | [references/tables/drift.md](references/tables/drift.md) | driftsinnboks, avvik, håndbok |

## Fallgruver (sjekk alltid)

- **Samme navn:** 6 navn deles av to ansatte (f.eks. Anja Eriksen: `KP-ANS-047`, `KP-ANS-115`). Slå opp på `ansatt_id`.
- **Bevarte testcaser, ikke feil:** `KP-ANS-155` har ingen personalmappe. 7 hviletidsbrudd og 1 287 vakter over døgnmaks er med vilje.
- **`timer` er etter lunsj:** `timer` = `slutt − start − 0,5` (`arbeidstid_grenser.lunsj_timer`). Bruk `timer` til kostnad og arbeidstid.
- **Stengte dager:** 979 dager har `er_aapent = 0` og 0 besøk. Snitt per dag skal bare regnes over åpne dager.
- **Anmeldelser mangler for de fleste utstillinger:** 87 av 102 har ingen. Snitt stjerner blir tomt, ikke 0.
- **Datakilde:** alle rader er syntetiske (`datakilde LIKE 'syntetisk%'`). Ingen filtrering trengs, men si aldri at tallene er ekte.
