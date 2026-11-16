# CLAUDE.md: Kunstpixel

Les `AGENTS.md` først. Her står svarstilen (DECISIONS 11 og L1–L12).

## Svar på spørsmål om data (demo)

- Svaret først, i 1–3 linjer. Ta med tall, enhet og ID (`KP-ANS-143`, `VAKT-0054561`).
- Siste linje er kilden: `Kilde: <tabell eller verktøy>`.
- Ingen innledning, oppsummering, verktøyforklaring, tilbud om mer eller informasjon det ikke ble spurt om.
- Er spørsmålet tvetydig, still ett kort oppfølgingsspørsmål i stedet for å gjette.

## Definisjoner

Bruk skillen `kunstpixel-data` for tallspørsmål: «ansatte» = nåværende, «i år» = til og med i dag, og formlene for lønn, besøk, sykefravær og utstillingsøkonomi.

## Rolle i demoen

Lars spør som `museumsdirektor`. Bruk den rollen i verktøy som krever `requester_role`, og ikke spør om rolle.

## HR-feller (sjekk før du svarer)

- **Navn:** søk alltid opp alle ansatte med navnet (`hr_ansatte.navn`). Er det flere, list ID-ene kort og spør hvem det gjelder.
- **Finnes dataene?** Sjekk først at raden finnes (personalmappe, samtale, vakt). Finnes den ikke, si det. Ikke snakk om tilgang til noe som ikke finnes.

## Output-oversikt (layoutkrav)

Svar:
```
Netto resultat for KP-EXH-2026-FOKUS-2 var 657 556 kr.
Kilde: utstilling_okonomi
```

`/sjekk` når alt stemmer (én linje):
```
✅ 6 av 6 påstander stemmer.
```

`/sjekk` med avvik (bare avvikene, én linje hver, så bevis):
```
❌ Dato 12.11.2026 → 2026-11-13
⚠️ Anja Eriksen = KP-ANS-047 → to ansatte: KP-ANS-047 og KP-ANS-115
Bevis: SELECT dato FROM hr_vakter WHERE vakt_id='VAKT-0054561'
4 av 6 stemmer.
```

`Fritekst: <én setning>` kommer bare når svaret har utkast eller råd (e-post, SMS, anbefaling). Kilde-linjer telles ikke som påstander.
