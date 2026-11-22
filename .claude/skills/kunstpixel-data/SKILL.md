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
| «i år», «2026», «hittil» | 1. januar til i dag | `dato BETWEEN date('now','localtime','start of year') AND date('now','localtime')` |
| «neste uke», «desember», «planlagt» | etter i dag (vaktplan, arrangementer) | `dato > date('now','localtime')` |

Dataene går til `2026-12-31`. Alt etter i dag er plan, ikke fakta. Si det når et tall inkluderer fremtiden.

## Nøkkeltall

Formler, kilder og fallgruver: [references/metrics.md](references/metrics.md).

| Nøkkeltall | Kort formel | MCP-verktøy |
|---|---|---|
| Lønnskostnad per avdeling | timer × tariffsats; helligdag > helg > kveld fra 17:00 > ordinær | `get_shift_cost_for_period` |
| Besøk og billettinntekt | `sum(besok_totalt)`, `sum(inntekt_nok)` fra `dagsbesok` | `get_daily_visitors` (bare MCP, ikke i Datafinner) |
| Sykefravær | eget: dager i `hr_fravaer`; prosent bare fra SSB | `get_absence_report`, `get_sickness_absence_statistics` |
| Utstillingsøkonomi | `netto_resultat_nok` = inntekter − `faktisk_totalkostnad_nok` | `get_exhibition_economy` |
| Driftsregnskap (museet) | `driftsregnskap` per måned; konto 3xxx = inntekter, 4xxx–7xxx = kostnader | `get_operating_accounts` (bare MCP) |

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
- **Bevarte testcaser, ikke feil:** `KP-ANS-155` har ingen personalmappe. 7 hviletidsbrudd er med vilje. De 1 287 vakter over døgnmaks er overtid (`hr_vakter.overtid_timer`, 40 % tillegg).
- **Bruk alltid kolonnen `timer`, ikke regn den ut:** som regel er `timer` = `slutt − start − 0,5` (`arbeidstid_grenser.lunsj_timer`), men 66 vakter avviker. 66 av dem er døgnmaks-vaktene over. Bruk `timer` til kostnad og arbeidstid.
- **Vaktene og dagsdataene er fasit (Lars 2026-11-22):** lønn i `driftsregnskap` (5000) er vaktlønnen, billett (3000) er `dagsbesok`. I `h5_historikk_2010_2026` er besøk, billett, kafé, inntekter, kostnader, resultat og årsverk regnet fra disse. Kafésalg (3100) før 2024 er h5-tall fordelt på måneder, fordi `kafe_varesalg` starter 2024.
- **Stengte dager:** 979 dager har `er_aapent = 0` og 0 besøk. Snitt per dag skal bare regnes over åpne dager.
- **Anmeldelser mangler for de fleste utstillinger:** 87 av 102 har ingen. Snitt stjerner blir tomt, ikke 0.
- **Offentlige data:** `ssb_sykefraver_kultur`, `norske_helligdager`, `arbeidstilsynet_renhold` og `leverandor_enhetsregister` er merket offentlig (`arena.datamerke`). De kan omtales som offentlige tall. Resten er øvingsdata: 32 tabeller har `datakilde LIKE 'syntetisk%'`, og 25 tabeller har ingen `datakilde`-kolonne (bl.a. `hr_ansatte`, `hr_vakter`, `dagsbesok`). Si aldri at øvingsdataene er ekte.
