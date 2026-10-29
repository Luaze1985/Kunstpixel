# H5: forslag til syntetisk fyll. Myndighetskontakt og rapportering

Status: **forslag, ikke laget.** Ingen datafiler er skrevet. Hver fil godkjennes for seg (Ja, Nei eller Endre).

> **Rettelse etter bygging (2026-10-26).** Forslaget regnet med 12 rapporter i kalenderen (fil C) men bare 7 rapportrader i tidsbruken (fil E). Det gikk ikke opp. Nå har fil E én rad per rapport, altså 19 oppgaver (7 myndighetskontakt og 12 rapportering). Rapportering blir **175 timer** (ikke 146) og totalen **287 timer** (ikke 258). Myndighetskontakt er uendret på 112. De faste tallene ligger i `src/kunstpixel/core/intern/leveranse.py`, og en test kontrollerer at fil C og fil E stemmer med hverandre.

## Hvorfor disse to områdene

Dagens data dekker HMS, IK-Mat, brann og en tilsynskalender med én linje per måned. Det som mangler er det folk faktisk bruker tid på: å forberede og følge opp myndigheter, og å lage rapporter. Eksisterende tiltak sier bare overskriften:

- NE-48: «Proaktiv og ryddig dialog med kommunen, fylkeskommunen og Kulturdirektoratet»
- NE-31: «Korte, konsise statusrapporter til direktør»

Forslaget gjør de to overskriftene til data assistenten kan svare ut fra, og viser hvor timene går.

## Rammer fra eierintensjonen (`owner_intent.md`)

- **Forenkling:** Ingen simulering av offentlig saksbehandling. Færre og mindre filer, ikke realisme for realismens skyld.
- **Menneskelig suverenitet:** KI lager utkast og søker, men sender aldri noe utad. Hver rapport til en ekstern mottaker har derfor `godkjenning: eier`.
- **Treningsverdi først:** Tidsbruken er laget for å vise hva som er verdt å automatisere.

## Regler for alle fem filer

1. Hver fil har `klassifisering: syntetisk` og `syntetisk: true` øverst.
2. **Bare roller, aldri personer.** Ingen navn, e-post, telefon eller adresser. Det finnes en test som skanner etter det.
3. Myndighetene har ekte navn (offentlig kunnskap). **Alle frister, terskler og timer er oppdiktet** og merkes «treningsdata, ikke rettesnor». Ingen paragrafhenvisninger og ingen sitater fra lovtekst.
4. Roller må finnes i `ROLLER` eller i teamoversikten. Frister som gjelder avvik må stemme med HMS-filen (14 dager gult, under 24 timer rødt).
5. Summer står ferdig regnet i filen og kontrolleres av en test. Modellen skal aldri regne.

## De fem filene

| # | Fil (under `05_data/governance/`) | Innhold | Omtrentlig størrelse | Tilgang (forslag) |
|---|---|---|---|---|
| A | `myndighetskontakter.yaml` | Hvem vi har kontakt med, hva de vil ha, hva som utløser kontakt, intern eier og vanlig dokumentasjon | 8 myndigheter | Alle roller |
| B | `tilsynsbesok_rutine.yaml` | Fra varsel om tilsyn til lukket avvik: steg, rolle og dokumentasjon per steg | 6 steg | Alle roller |
| C | `rapporteringskalender.yaml` | Hvilke rapporter som lages, til hvem, når, av hvilken rolle, fra hvilke datakilder og hvem som godkjenner | 12 rapporter | Alle roller |
| D | `rapportmaler.yaml` | Skjelett for driftsrapport, avviksrapport, tilskuddsrapport og svar til tilsyn, med felt og regler for hva som skal stå der | 4 maler | Alle roller |
| E | `arbeidsoppgaver_tidsbruk.yaml` | Gjentakende oppgaver med timer per år, rolle og automatiseringspotensial | 14 oppgaver | Bare ledelse |

Fil E er den som svarer på «hva bruker vi tid på». Den ligger hos ledelsen fordi den handler om ressursbruk, som tiltakene allerede gjør.

### A. Myndighetskontakter (utdrag)

Myndigheter: Arbeidstilsynet, Mattilsynet, Brann- og redningsetaten, kommunen (skjenke- og serveringsbevilling), fylkeskommunen, Kulturdirektoratet, Datatilsynet og Stiftelsestilsynet (samlingen er en allmenn stiftelse).

```yaml
- id: MK-02
  myndighet: Mattilsynet
  omrade: Kafé og IK-Mat
  hva_de_vil: Dokumentert internkontroll, temperaturlogger og avviksbehandling
  utloser: Varslet eller uvarslet tilsyn, klage fra gjest
  intern_eier: Kafeansvarlig
  dokumentasjon: Temperaturlogg, avvikslogg, hygieneplan
  merknad: treningsdata, ikke rettesnor
```

### B. Tilsynsbesøk (utdrag)

Steg: 1 Varsel kommer. 2 Samle dokumentasjon. 3 Under besøket. 4 Avslutning og muntlig tilbakemelding. 5 Skriftlig svar. 6 Lukke avvik. Frister følger HMS-filen.

### C. Rapporteringskalender (utdrag)

```yaml
- id: RP-07
  rapport: Tilskuddsrapport
  mottaker: Kulturdirektoratet
  mottakertype: ekstern
  frekvens: årlig
  maned: Mars
  eier: Museumsdirektør
  kilder: [besøkstall, utstillinger, regnskap]
  godkjenning: eier
  timer_per_gang: 36
```

Rapportene er: månedlig driftsrapport, besøkstall, tilskuddsrapport, årsregnskap og årsberetning, HMS-årsrapport, avviksrapport, IK-Mat-sammenstilling, vernerundeprotokoll, tilstandsrapporter for samlingen, brannøvelsesrapport, innlånsoversikt og styrerapport.

### E. Tidsbruk (utdrag, alle tall oppdiktet)

| Område | Oppgave | Timer per år | Automatiseringspotensial |
|---|---|---|---|
| Myndighetskontakt | Tilskuddssøknad | 40 | Middels |
| Myndighetskontakt | Følge opp avvik og pålegg | 20 | Middels |
| Myndighetskontakt | Forberede tilsyn, Arbeidstilsynet | 16 | Høy |
| Myndighetskontakt | Forberede tilsyn, Mattilsynet | 12 | Høy |
| Myndighetskontakt | Forberede brannøvelse og tilsyn | 10 | Høy |
| Myndighetskontakt | Fornye skjenkebevilling | 8 | Lav |
| Myndighetskontakt | Personvernhenvendelser | 6 | Lav |
| Rapportering | Tilskuddsrapport og årsrapport | 36 | Middels |
| Rapportering | Månedlig driftsrapport | 24 | Høy |
| Rapportering | Årsregnskap og årsberetning | 24 | Lav |
| Rapportering | Avviksrapportering | 20 | Høy |
| Rapportering | Sammenstilling av IK-Mat-logger | 18 | Høy |
| Rapportering | Besøkstall og statistikk | 14 | Høy |
| Rapportering | HMS-årsrapport | 10 | Høy |
| **Sum** | Myndighetskontakt 112 timer, rapportering 146 timer | **258** | |

Rekkefølgen viser det vi bør automatisere først: månedlig driftsrapport, avviksrapportering, IK-Mat-logger og besøkstall, fordi de er gjentakende, har kjente datakilder og lav risiko når et menneske godkjenner.

## Hva det gir assistenten

Tre nye verktøy, i samme stil som de seks vi har: `search_myndighet` (A og B), `search_rapportering` (C og D) og `search_arbeidsoppgaver` (E, bare ledelse). Hver får kilde og sti, rollefilter og klassifisering `syntetisk`.

**20 nye prøvespørsmål**, 14 som dataene dekker og 6 som de ikke dekker:

Dekket:
1. Hvem har kontakten med Mattilsynet?
2. Hva gjør vi første dagen etter varsel om tilsyn?
3. Hva trenger Arbeidstilsynet av dokumentasjon?
4. Hvem er kontaktpunkt mot Kulturdirektoratet?
5. Hvilken rapport skal leveres i mars?
6. Hvem godkjenner rapporter før de sendes ut?
7. Hvilke datakilder bruker driftsrapporten?
8. Hva skal stå i en avviksrapport?
9. Hvem skriver styrerapporten?
10. Hvilke rapporter går til eksterne mottakere?
11. Hvor mange timer bruker vi på tilskuddsrapportering? (ledelse)
12. Hva bruker vi mest tid på innen myndighetskontakt? (ledelse)
13. Hvilke oppgaver bør automatiseres først? (ledelse)
14. Hvor lenge har vi på å lukke et gult avvik etter tilsyn?

Ikke dekket, skal gi ærlig avslag:
15. Hva er telefonnummeret til Mattilsynet?
16. Hva stod i rapporten fra forrige tilsyn?
17. Hvor mye fikk vi i tilskudd i fjor?
18. Hva sier loven om oppbevaring av temperaturlogger?
19. Hvem kommer fra tilsynet neste gang?
20. Hvor mange timer bruker jeg personlig på rapporter?

## Nye tester

- **Summene stemmer:** Summene i fil E er lik summen av oppgavene, per område og totalt.
- **Ingen persondata:** Skanner alle fem filene etter e-post, telefonnummer og personnavn.
- **Krysskontroll:** Frister for avvik stemmer med HMS-filen. Alle roller finnes i teamoversikten.
- **Godkjenning:** Alle rapporter med ekstern mottaker har `godkjenning: eier`.
- **Merking:** Hver fil har `syntetisk: true`, og hver myndighetsoppføring har merknaden «treningsdata».
- **Tilgang:** Fil E er usynlig for ansatte som ikke er ledelse, også for modellen.
- **Prøvesett:** De 20 spørsmålene med forventet kilde og faktum hentet ordrett fra filene, på samme måte som i dag.

## Valgfritt senere (H5b): utkast til rapporter

Fil D gjør det mulig å la assistenten lage et **utkast** til for eksempel en driftsrapport fra databasen. Det er en ny type funksjon (generere, ikke bare svare) og trenger egne regler: tydelig merket «Utkast, ikke sendt», aldri sending, og faktakontroll på hver påstand. Jeg foreslår å vente med den til H5 er godkjent og testet.

## Det jeg trenger fra deg

1. Ja, Nei eller Endre per fil, A til E.
2. Er tilgangen riktig, særlig at fil E bare er for ledelsen?
3. Skal timetallene være utgangspunkt, eller har du egne anslag fra erfaring?
4. Vil du ha H5b (utkast) med nå eller vente?

## Tillegg: historikk 2010 til 2026 (bestilt 2026-10-27)

Du ba om at dataene skal dekke 2010 til 2026, årlig, med nok parametre til at det blir mye data. Det er bygget som to filer:

- **`historikk_tall.yaml` laget av koden.** Ett år per rad, 17 år og 35 parametre per år, til sammen 595 datapunkter: besøk, billettinntekter, tilskudd, kafé, kostnader og resultat, ansatte, tilsyn, avvik og pålegg, interne avviksmeldinger, sykefravær, IK-Mat-avvik, vernerunder, rapporter levert og for sent, tilskuddssøknader, timer på myndighetskontakt og rapportering, og automatiseringsgrad. Tallene henger sammen: regnskapet går opp, avvik lukket er aldri flere enn avvik funnet, og 2026 gir nøyaktig 287 timer, som i tidsbruksfilen. Historien har et rekordår i 2019, en pandemi i 2020 og 2021 med underskudd, og automatisering som starter i 2023. Alt er oppdiktet og merket som treningsdata. En modell rører ikke tallene, og kontrollen avviser enhver endring.
- **`historikk_tekst.yaml` (fil F) skrevet av en modell.** To korte tekster per år (`hendelse` og `laerdom`) som passer til temaet og nøkkeltallene for året. Teksten får ikke ha tall eller årstall.

Fil F og tallfilen er foreslått for ledelsen alene, siden de inneholder økonomi og sykefravær.