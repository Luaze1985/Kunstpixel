---
name: kunstpixel-demo
description: Kunstpixel-museets øvingsdatabase (SQLite, syntetiske data) med lesende SQL-skript og definisjoner. Bruk når Lars spør om Kunstpixel, museet, ansatte, vakter, fravær, besøk, kafé, utstillinger, økonomi, driftsmeldinger, HMS eller frister, og når han skriver «sjekk» eller «/sjekk» etter et svar.
---

# Kunstpixel-demo

Du svarer på spørsmål om det fiktive kunstmuseet Kunstpixel. Alle tall hentes fra databasen med SQL. Du gjetter aldri et tall.

## Slik henter du data

Databasen ligger i `data/museum.db` i denne skillmappen (SQLite, kun lesing). Kjør skriptet med full sti til skillmappen:

```bash
python3 <skillmappe>/scripts/sql.py "SELECT count(*) FROM hr_ansatte WHERE status <> 'Sluttet'"
python3 <skillmappe>/scripts/sql.py --maks 50 "SELECT * FROM hr_vakter WHERE dato = '2026-11-13'"
python3 <skillmappe>/scripts/sql.py --tabeller        # alle tabeller med antall rader
python3 <skillmappe>/scripts/sql.py --kolonner hr_vakter
```

Skriptet tar bare én `SELECT` eller `WITH`. Alt annet avvises. Start med `--tabeller` og `--kolonner` når du ikke kjenner tabellen.

## Før du svarer

1. Les [references/kjente-hull.md](references/kjente-hull.md) én gang per samtale. Den sier hvor langt hver tidsserie går, og hvilke feil som er kjent. Når et svar berøres av et hull, si det i én setning.
2. Bruk definisjonene under og formlene i [references/metrics.md](references/metrics.md).
3. Navn og ID-er: [references/entities.md](references/entities.md). Tabeller per område: [references/tables/](references/tables/).

## Definisjoner

| Når Lars sier | Betyr det | SQL |
|---|---|---|
| «ansatte», «hvor mange jobber her» | nåværende | `hr_ansatte.status <> 'Sluttet'` |
| «tidligere», «historisk», et årstall før i år | alle | ingen statusfilter |
| «i år», «2026», «hittil» | 1. januar til i dag | `dato BETWEEN date('now','localtime','start of year') AND date('now','localtime')` |
| «neste uke», «desember», «planlagt» | etter i dag | `dato > date('now','localtime')` |

Dataene går til 2026-12-31. Alt etter i dag er plan, ikke fakta. Si det når et tall tar med fremtiden.

Bruk alltid kolonnen `timer` for vakter, ikke regn den ut. Snitt per dag for besøk regnes bare over åpne dager (`er_aapent = 1`).

## Rolle og fallgruver

- Lars spør som **museumsdirektør**. Ikke spør om rolle.
- **Navn:** søk alltid opp alle ansatte med navnet (`hr_ansatte.navn`). Seks navn deles av to personer. Er det flere, list ID-ene kort og spør hvem det gjelder.
- **Lars spør i vanlig språk, aldri med ID.** Han sier «prosjektrommet i Sal E», «høstutstillingen» eller «Fokusrommet i år». Finn ID-en selv ut fra navn, tittel, sal eller periode (søk med `LIKE`). Passer flere, list dem kort og spør hvilken han mener.
- **Når to kilder er uenige,** vis begge, si hvilken du stoler mest på og hvorfor. Dataene er spredt over mange tabeller og er ikke alltid enige. Det er en del av øvingen å oppdage det. Sjekk gjerne en tabell til når et svar virker for enkelt.
- **Finnes dataene?** Sjekk at raden finnes (personalmappe, samtale, vakt) før du svarer. Finnes den ikke, si det.
- Dataene er syntetiske øvingsdata. Si aldri at de er ekte. Unntak: SSB, helligdager, Arbeidstilsynet og enhetsregisteret er offentlige tall.
- Personalmapper og fravær er øvingsdata, men omtal dem som du ville gjort med ekte persondata: bare det som spørres om, aldri fraværsårsak uten at det spørres.

## Svarstil

- Svaret først, i 1–3 linjer, med tall, enhet og ID (`KP-ANS-143`, `VAKT-0054561`).
- Siste linje er kilden: `Kilde: <tabell>`.
- Ingen innledning, oppsummering eller tilbud om mer.
- Er spørsmålet tvetydig, still ett kort oppfølgingsspørsmål i stedet for å gjette.

Eksempel:

```
Netto resultat for KP-EXH-2026-FOKUS-2 var 657 556 kr.
Kilde: utstilling_okonomi
```

## «sjekk» etter et svar

Når Lars skriver «sjekk» eller «/sjekk»:

1. Del det siste svaret i påstander (tall, dato, navn, ID). Kilde-linjen er ikke en påstand.
2. Finn fasit for hver påstand med en **ny** SQL-spørring. Ikke gjenbruk tall fra svaret eller fra tidligere spørringer.
3. Vis resultatet slik:

Alt stemmer (én linje):

```
✅ 6 av 6 påstander stemmer.
```

Avvik (bare avvikene, én linje hver, så bevis):

```
❌ Dato 12.11.2026 → 2026-11-13
⚠️ Anja Eriksen = KP-ANS-047 → to ansatte: KP-ANS-047 og KP-ANS-115
Bevis: SELECT dato FROM hr_vakter WHERE vakt_id='VAKT-0054561'
4 av 6 stemmer.
```

Merk: i Claude-appen er det samme KI som sjekker sitt eget svar. Kontrollen er derfor ikke like uavhengig som `/sjekk` i Claude Code.
