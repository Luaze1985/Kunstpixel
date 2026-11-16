# Nøkkeltall

Alle tall gjelder «i år» = til og med i dag, med mindre Lars ber om noe annet (SKILL.md).

## Lønnskostnad per avdeling

- **Definisjon:** hva vaktene kostet i lønn etter Virke-tariffen, per avdeling og måned.
- **Kilde:** `hr_vakter` × `hr_ansatte.lonnstrinn_virke` → `virke_tariff.lonnstrinn`, `norske_helligdager`, `arbeidstid_grenser.kveldstillegg_fra` (17,0).
- **Regel per vakt (første som slår til):**
  1. Helligdag (`norske_helligdager.dato`): `timer × timesats_helligdag`
  2. Lørdag/søndag (`strftime('%w')` 6 eller 0): `timer × timesats_helg`
  3. Ellers: kveldstimer (etter 17:00) × `timesats_kveld` + resten × `timesats_ordinar`
- **Avrunding:** rund hver vakt til 2 desimaler før summering. Ellers blir summen opptil 5 øre ulik fasit (G11).
- **Fasit:** `get_shift_cost_for_period(maaned)`. Statusporten P4d sjekker at SQL og verktøy er like.

```sql
SELECT v.avdeling,
       round(sum(round(
         CASE WHEN h.dato IS NOT NULL THEN v.timer * t.timesats_helligdag
              WHEN strftime('%w', v.dato) IN ('0','6') THEN v.timer * t.timesats_helg
              ELSE (v.timer - min(v.timer, max(0,
                     (CAST(substr(v.slutt,1,2) AS REAL) + CAST(substr(v.slutt,4,2) AS REAL)/60)
                     - max(CAST(substr(v.start,1,2) AS REAL) + CAST(substr(v.start,4,2) AS REAL)/60, 17.0))))
                     * t.timesats_ordinar
                   + min(v.timer, max(0,
                     (CAST(substr(v.slutt,1,2) AS REAL) + CAST(substr(v.slutt,4,2) AS REAL)/60)
                     - max(CAST(substr(v.start,1,2) AS REAL) + CAST(substr(v.start,4,2) AS REAL)/60, 17.0)))
                     * t.timesats_kveld
         END, 2)), 2) AS kostnad_nok
FROM hr_vakter v
JOIN hr_ansatte a USING (ansatt_id)
JOIN virke_tariff t ON t.lonnstrinn = a.lonnstrinn_virke
LEFT JOIN norske_helligdager h ON h.dato = v.dato
WHERE substr(v.dato, 1, 7) = '2026-10'
GROUP BY v.avdeling;
```

- **Fallgruve:** vakter etter i dag er planlagte. «Kostnad i november» før månedsslutt er delvis plan. Si det.

## Besøk og billettinntekt

- **Definisjon:** antall besøkende og billettinntekt per dag, måned eller år.
- **Kilde:** `dagsbesok` (én rad per dato, 2010–2026).
- **Formel:** `besok_totalt` = voksne + studenter + barn. `inntekt_nok` = voksne × `pris_voksen` + studenter × `pris_student`. Barn og gratisdager gir 0 kr. Begge er kontrollert: 0 avvik.
- **Snitt per dag:** bare åpne dager (`er_aapent = 1`).
- **MCP:** `get_daily_visitors`.

```sql
SELECT sum(besok_totalt) AS besok, sum(inntekt_nok) AS inntekt_nok,
       round(avg(CASE WHEN er_aapent = 1 THEN besok_totalt END), 1) AS snitt_per_apen_dag
FROM dagsbesok
WHERE dato BETWEEN '2026-01-01' AND date('now','localtime');
```

- **Fallgruve:** `utstillinger_historikk.besokstall_total` er besøk per utstilling. Summen av utstillingene er ikke lik museets besøk.

## Sykefravær

- **Eget fravær:** `hr_fravaer` med `type` = `sykemelding`, `egenmelding` eller `permisjon`. Mål i fraværstilfeller og dager (`julianday(til) - julianday(fra) + 1`).
- **Prosent:** bare fra `ssb_sykefraver_kultur.sykefraver_prosent` (SSB-snitt for kultursektoren per kvartal, ikke Kunstpixels eget). Statusporten P4c bruker siste kvartal.
- **Ikke regn ut en egen sykefraværsprosent.** Det finnes ingen avtalt nevner (stillingsprosent × arbeidsdager). Spør Lars hvis han vil ha det.
- **Permisjon er ikke sykefravær.**
- **MCP:** `get_absence_report`, `get_sickness_absence_statistics`.

```sql
SELECT type, count(*) AS tilfeller,
       sum(julianday(min(til, date('now','localtime'))) - julianday(fra) + 1) AS dager
FROM hr_fravaer
WHERE fra BETWEEN '2026-01-01' AND date('now','localtime')
  AND type IN ('sykemelding','egenmelding')
GROUP BY type;
```

```sql
SELECT periode, sykefraver_prosent, egenmeldt_prosent, legemeldt_prosent
FROM ssb_sykefraver_kultur ORDER BY aar DESC, kvartal DESC LIMIT 1;
```

## Utstillingsøkonomi

- **Definisjon:** resultatet for én utstilling.
- **Kilde:** `utstilling_okonomi` (1:1 med `utstillinger_historikk` på `utstilling_id`).
- **Formel:** `netto_resultat_nok` = `billettinntekter_nok` + `katalogsalg_nok` + `sponsorstotte_nok` − `faktisk_totalkostnad_nok` (0 avvik). `budsjett_nok` er plan, ikke kostnad.
- **Stjerner:** snitt av `anmeldelser.stjerner` på `utstilling_id`. 87 av 102 utstillinger har ingen anmeldelser, så svaret er tomt, ikke 0.
- **Fasit:** P4b sjekker `KP-EXH-2026-FOKUS-2` = 657 556 kr.
- **MCP:** `get_exhibition_economy`, `list_exhibitions_with_economy`.

```sql
SELECT u.utstilling_id, u.tittel, u.besokstall_total, o.netto_resultat_nok,
       round(avg(a.stjerner), 2) AS snitt_stjerner, count(a.anmeldelse_id) AS anmeldelser
FROM utstillinger_historikk u
JOIN utstilling_okonomi o USING (utstilling_id)
LEFT JOIN anmeldelser a ON a.utstilling_id = u.utstilling_id
WHERE u.aar = 2026
GROUP BY u.utstilling_id
ORDER BY o.netto_resultat_nok DESC;
```

- **Fallgruve:** 4 utstillinger har status «Pågående / Planlagt sesong 2026». Tallene deres kan være foreløpige.
