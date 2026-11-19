# Design: Kunstpixel på storskjerm

Status: utkast til godkjenning (2026-11-19). Beslutninger føres i `docs/DECISIONS.md` som D1–D8 når Lars har godkjent.

## Hvorfor

Lars vil «komme på jobb» som museumsdirektør og vise hvordan dagen ser ut, på storskjerm, til andre.
Det skal være **så enkelt som mulig å hente fram og vise**: én lenke, ett trykk til fullskjerm.
Kunstpixel er en treningsarena for å gå fra datakaos til oversikt, så det som mangler i dataene skal vises, ikke skjules.

## Mål

- Én skjerm (16:9) som viser dagen, lesbar fra ca. 3 meter, uten rulling.
- Åpnes fra «Festet» i claude.ai-menyen eller fra en lenke i prosjektet Kunstpixel. Knappen **Fullskjerm** gjør resten.
- Samme tall som Datafinner, regnet med de samme funksjonene.
- Hvert tall har en kildelinje (`Kilde: tabell`), slik svarstilen i Kunstpixel krever.

## Ikke-mål

- Ingen skriving tilbake til `museum.db`. Ingen «Fulgt opp»-knapper. Det er Datafinner sin jobb.
- Ingen chat eller KI inne i siden.
- Ingen automatisk oppdatering. Tallene er et øyeblikksbilde.
- Ikke bygd for mobil først. Den skal virke på mobil, men storskjerm er målet.

## Anti-mål (feiler selv om den virker)

- Et tall uten sammenligning eller status (sier ikke om noe er galt).
- Et datahull som ser ut som 0 eller «alt er fint».
- Navn på syke eller fraværende ansatte på en skjerm andre ser.
- Tekst som ikke kan leses på avstand.

## Tilnærminger

| | Valgt? | Fordeler | Ulemper |
|---|---|---|---|
| **B. Vanlig nettside med Arbeidsflyt** | **Ja** (Lars: «så enkelt som mulig å hente fram og vise») | Én lenke, åpnes i fullskjerm uten sidepanel. Full kontroll over storskjermoppsettet. Gjenbruker `af.css` og `core/ledelse.py`. | Kilden er en tekstlinje, ikke klikkbar. Ingen automatisk kontroll av at tallene stemmer, så det må testene gjøre. |
| A. Claudes Data-type | Nei | Klikkbare kilder og innebygd kontroll av tallene. | Typens ramme og kildepanel tar plass på storskjerm. Flere deler som kan gå galt. |
| Datafinner på nett | Nei | Appen finnes allerede. | Krever ny tjeneste, innlogging og trolig kostnad. |

## Slik ser den ut

```
┌──────────────────────────────────────────────────────────────────────┐
│ Kunstpixel  Torsdag 19. november  Tall per 19.11  2 krever oppmerksomhet [Fullskjerm]│
├───────────────┬───────────────┬───────────────┬──────────────────────┤
│ Besøk i går   │ På jobb i dag │ Åpne saker    │ Sykefravær           │
│ tall          │ tall          │ tall          │ tall                 │
│ normalt: …    │ …             │ eldste: …     │ normalt: …           │
│ Status-ord    │ Status-ord    │ Status-ord    │ Status-ord           │
│ Kilde: …      │ Kilde: …      │ Kilde: …      │ Kilde: …             │
├───────────────┴───────────────┴──────┬────────┴──────────────────────┤
│ Besøk siste 8 uker mot i fjor        │ Frister                       │
│ (linje: i år blå, i fjor grå)        │ Forfalt · I dag · Denne uka   │
├──────────────────────────────────────┼───────────────────────────────┤
│ Utstillingene i år: resultat         │ Dette vet vi ikke             │
│ (stolper, sesong i navnet)           │ kilder som slutter tidlig,    │
│                                      │ tabeller som er uenige        │
└──────────────────────────────────────┴───────────────────────────────┘
```

## Det som er bestemt

1. **Plassering:** egen artifact i claude.ai, festet i menyen. Lenken legges i prosjektet Kunstpixel og i guiden.
2. **Data:** et skript i repoet regner alle tall fra `museum.db` med funksjonene i `src/kunstpixel/core/ledelse.py` (`normalt_for_ukedag`, `vurder`, `beregn_frister`) og skriver én datafil (JSON). Siden leser datafilen.
3. **Oppdatering:** Lars sier «oppdater dashbordet». Claude Code kjører skriptet og publiserer siden og datafilen på nytt til samme lenke.
4. **«I dag»** er datoen skriptet kjøres. Rader etter i dag er plan og telles ikke.
5. **Status** som ord: Normal, Følg med, Over terskel, Ukjent. Ukjent brukes når kilden ikke dekker dagen.
6. **«Dette vet vi ikke»** regnes av skriptet ved hver kjøring: tidsserier som slutter før i dag, og utstillingstabeller som er uenige om hva som vises nå.
7. **Personvern på skjerm:** frister for sykefravær vises som antall og ansatt-ID, aldri navn eller årsak.
8. **Utseende:** Arbeidsflyt (én blå for handling, status som ord, ingen pynt eller emoji, Inter). Storskjermtillegg: minst 20 px tekst, store tall, seks flater.

## Overlatt til den som bygger

- Nøyaktig hvilke tall som går i de fire nøkkelflatene, valgt blant det Datafinners «I dag» allerede regner.
- Diagrambibliotek eller håndtegnet SVG.
- Filplassering: siden i `deploy/claude-app/`, datafilen i `.scratch/claude-app/` (ingen nye mapper).

## Tester (røde først)

- Skriptet: hver flate har verdi, normalt, status og kilde. Tallene er lik en egen SQL-spørring. Ingen navn i fristene.
- «Dette vet vi ikke» finner hullet i tilfredshet (slutter 2026-10-29) og uenigheten mellom utstillingstabellene.
- Siden: lastes uten feil i nettleseren, ingen sidelengs rulling på 1920×1080 og 400 px bredde.
