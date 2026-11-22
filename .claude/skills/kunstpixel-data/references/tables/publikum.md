# Publikum og kafé

Daglige besøkstall og billettinntekter, tilfredshet, anmeldelser og kafésalg.

## Tabeller

| Tabell | Nøkkel | Viktige kolonner | Merk |
|---|---|---|---|
| `dagsbesok` | `dato` | `er_aapent`, `antall_voksne`, `antall_student`, `antall_barn`, `besok_totalt`, `gratis_dag`, `inntekt_nok` | 979 stengte dager, 201 gratisdager |
| `besok_tilfredshet` | `dato` | `antall_svar`, `score_utstilling`, `score_kafe`, `score_service`, `score_totalt` | Ikke hver dag |
| `anmeldelser` | `anmeldelse_id` | `dato`, `kanal`, `stjerner`, `utstilling_id`, `produkt_id`, `tekst` | `kanal`: google, egen_undersokelse, tripadvisor. 1 286 uten utstilling. |
| `kafe_meny` | `produkt_id` | navn, pris, allergener | |
| `kafe_varesalg` | `dato`, `produkt_id` | `antall`, `omsetning_nok` | |

## Spørringer

Besøk og inntekt per måned i år:
```sql
SELECT substr(dato, 1, 7) AS maaned, sum(besok_totalt) AS besok, sum(inntekt_nok) AS inntekt_nok
FROM dagsbesok
WHERE dato BETWEEN date('now','localtime','start of year') AND date('now','localtime')
GROUP BY maaned ORDER BY maaned;
```

Snitt stjerner per kanal siste 12 måneder:
```sql
SELECT kanal, count(*) AS antall, round(avg(stjerner), 2) AS snitt
FROM anmeldelser
WHERE dato > date('now','localtime','-12 months')
GROUP BY kanal;
```

Kafeens omsetning i år:
```sql
SELECT sum(omsetning_nok) AS omsetning_nok FROM kafe_varesalg
WHERE dato BETWEEN date('now','localtime','start of year') AND date('now','localtime');
```

## Fallgruver

- **Snitt per dag:** bare over `er_aapent = 1`.
- **Billettinntekt er ikke kafé:** kafésalg står i `kafe_varesalg`, ikke i `inntekt_nok`.
- **Anmeldelser:** de fleste gjelder kafé eller museet generelt. Filtrer på `utstilling_id` eller `produkt_id` før du knytter dem til noe.
