# Utstillinger

102 utstillinger 2010–2026 med økonomi og innlån. Samlingen (16 verk, 12 kunstnere) står i `verk` og `kunstnere`.

## Tabeller

| Tabell | Nøkkel | Viktige kolonner | Merk |
|---|---|---|---|
| `utstillinger_historikk` | `utstilling_id` | `aar`, `sesong`, `tittel`, `kurator`, `periode_start`, `periode_slutt`, `besokstall_total`, `budsjett_nok`, `status` | 4 med status «Pågående / Planlagt sesong 2026» |
| `utstilling_okonomi` | `utstilling_id` | `budsjett_nok`, `faktisk_totalkostnad_nok`, `billettinntekter_nok`, `katalogsalg_nok`, `sponsorstotte_nok`, `netto_resultat_nok`, `avvik_forklaring` | 1:1 med historikken |
| `utstillingsinnlan` | `innlan_id` | `utstilling_id`, utlåner, forsikringsverdi | 50 lån |

## Spørringer

Resultat for én utstilling:
```sql
SELECT u.tittel, o.netto_resultat_nok, o.faktisk_totalkostnad_nok, o.budsjett_nok, o.avvik_forklaring
FROM utstillinger_historikk u JOIN utstilling_okonomi o USING (utstilling_id)
WHERE u.utstilling_id = 'KP-EXH-2026-FOKUS-2';
```

Utstillinger som gikk over budsjett:
```sql
SELECT utstilling_id, budsjett_nok, faktisk_totalkostnad_nok,
       faktisk_totalkostnad_nok - budsjett_nok AS over_budsjett_nok
FROM utstilling_okonomi
WHERE faktisk_totalkostnad_nok > budsjett_nok
ORDER BY over_budsjett_nok DESC LIMIT 10;
```

## Fallgruver

- **Besøk per utstilling er ikke museets besøk.** Utstillinger overlapper i tid.
- **Budsjett er plan:** sammenlign med `faktisk_totalkostnad_nok`, ikke med netto.
- **Status-tekst varierer:** «Gjennomført» finnes i tre varianter (med kapasitets- og smittevernmerknad). Bruk `LIKE 'Gjennomført%'`.
