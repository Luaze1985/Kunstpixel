# HR og vakter

Ansatte, vakter 2010–2026, fravær, medarbeidersamtaler, personalmapper og innleie. Personopplysningene er syntetiske.

## Tabeller

| Tabell | Nøkkel | Viktige kolonner | Merk |
|---|---|---|---|
| `hr_ansatte` | `ansatt_id` | `navn`, `avdeling`, `stilling`, `status`, `ansatt_fra`, `ansatt_til`, `lonnstrinn_virke`, `kontor_sal` | `status`: Fast, Deltid / Sesong, Sluttet |
| `hr_vakter` | `vakt_id` | `ansatt_id`, `dato`, `start`, `slutt`, `timer`, `stasjon`, `avdeling`, `rolle`, `utstilling_id` | `timer` er etter 0,5 t lunsj. Planlagte vakter etter i dag. |
| `hr_fravaer` | `fravaer_id` | `ansatt_id`, `fra`, `til`, `type` | `type`: sykemelding, egenmelding, permisjon |
| `hr_medarbeidersamtaler` | `samtale_id` | `ansatt_id`, `dato`, `samlet_vurdering`, `utviklingsomrade` | Bare nåværende har samtaler. 2 nåværende mangler (`KP-ANS-166` m.fl.). |
| `hr_personalmapper` | `saksnr` | `ansatt_id`, `kategori`, `tittel`, `gradering` | Alle `LEDER_FORTROLIG`. `KP-ANS-155` har ingen. |
| `arbeidstid_grenser` | `navn` | `verdi` | døgnmaks 9, hvile 11, ukenorm 37,5, lunsj 0,5, kveld fra 17 |
| `hr_innleie` / `hr_innleide_personer` / `hr_innleide_kompetanse` | `innleie_id` / `innleid_id` | | Innleide er ikke ansatte |

## Spørringer

Hvem jobbet i en sal på en dato:
```sql
SELECT v.vakt_id, a.ansatt_id, a.navn, v.start, v.slutt, v.timer
FROM hr_vakter v JOIN hr_ansatte a USING (ansatt_id)
WHERE v.dato = '2026-11-13' AND v.stasjon LIKE 'Sal C%';
```

Nåværende ansatte uten medarbeidersamtale:
```sql
SELECT a.ansatt_id, a.navn, a.avdeling
FROM hr_ansatte a
WHERE a.status <> 'Sluttet'
  AND NOT EXISTS (SELECT 1 FROM hr_medarbeidersamtaler s WHERE s.ansatt_id = a.ansatt_id);
```

Antall nåværende ansatte per avdeling:
```sql
SELECT avdeling, count(*) AS ansatte FROM hr_ansatte WHERE status <> 'Sluttet' GROUP BY avdeling;
```

## Fallgruver

- **Navnelikhet:** spør alltid om `ansatt_id` når navnet deles (se entities.md).
- **Stasjon eller avdeling:** «vakt i kafeen» betyr `stasjon = 'Museumskafé'`, ikke `avdeling = 'Marked'`.
- **Brudd som skal stå:** hviletid under 11 t (7) og vakter over 9 t (1 287) er bevisste. Rapporter dem, men kall dem ikke datafeil.
