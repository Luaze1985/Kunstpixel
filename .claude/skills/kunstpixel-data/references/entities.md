# Entiteter

## «Ansatt» kan bety

- **Fast ansatt (nåværende):** `hr_ansatte`, `status IN ('Fast','Deltid / Sesong')`, 74 personer. Standard.
- **Tidligere ansatt:** `status = 'Sluttet'` og `ansatt_til` satt, 94 personer.
- **Innleid:** `hr_innleide_personer` (`KP-INN-Pxx`, 8 personer) med kontrakter i `hr_innleie` (`KP-INN-YYYY-xxxx`). Ikke i `hr_ansatte`.
- **Demoperson:** `hr_people` (`E101`–`E112`) er en liten demokjerne som peker til `hr_ansatte` via `ansatt_id`. Bruk `hr_ansatte` for navn og stilling.

46 ansatte har ingen vakter (ledelse og kontor). «Ingen vakter» betyr ikke «ikke ansatt».

## ID-er

| Entitet | ID | Tabell | Merk |
|---|---|---|---|
| Ansatt | `KP-ANS-001`–`KP-ANS-168` | `hr_ansatte` | Navn er ikke unikt (6 navn deles av to) |
| Vakt | `VAKT-0000001` | `hr_vakter` | `stasjon` er stedet, `avdeling` er ansattes avdeling |
| Utstilling | `KP-EXH-YYYY-xxx`, `KP-EXH-YYYY-FOKUS-n` | `utstillinger_historikk` | |
| Sal | `SAL-A`–`SAL-E` | `saler.id` | I `hr_vakter.stasjon` står salnavnet som tekst, f.eks. «Sal C (Lys, farge og interiør)» |
| Driftsmelding | `MELD-YYYY-xxxx` | `driftsmeldinger_epost` | Tiltak: `TILT-YYYY-xxxx` |
| Håndbokpunkt | `PERSONAL-8.1`, `SOP-004-2` | `handbok_oppslag.punkt_id` | |

## Relasjoner

- Ansatt → vakter, fravær, samtaler, kompetanse: 1:mange på `ansatt_id`.
- Ansatt → personalmappe: 1:0..1 (`KP-ANS-155` har ingen, med vilje).
- Utstilling → økonomi: 1:1 på `utstilling_id`. Utstilling → anmeldelser: 1:mange, ofte 0.
- Driftsmelding → tiltak: 1:1 på `melding_id`. Tiltak → håndbokpunkt: mange:1.

## Navnelikhet

```sql
SELECT navn, group_concat(ansatt_id || ' (' || stilling || ', ' || status || ')', '; ') AS treff
FROM hr_ansatte GROUP BY navn HAVING count(*) > 1;
```
