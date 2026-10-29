# Bestilling: syntetisk fyll for et kunstmuseum

## Oppdraget
Du skal skrive **fritekst** i ferdige YAML-skjelett. Dataene er trenings- og demodata for en intern assistent
hos et fiktivt museum (Kunstpixel). De handler om to ting museet bruker tid på: **kontakt med myndigheter** og
**rapportering**. Alt er oppdiktet. Ingenting er ekte, og ingenting skal ligne på ekte personer eller saker.

Historikkfilen (`historikk_tekst.yaml`) har ett år per oppføring, fra 2010 til 2026. Temaet og nøkkeltallene for hvert år
står ferdig. Skriv `hendelse` og `laerdom` slik at de passer til temaet og tallene for akkurat det året, for eksempel
lavt besøk og stengte perioder når temaet er pandemi. Ikke skriv tall eller årstall i teksten. Tekstene må være ulike fra
år til år, og tonen skal være nøktern og konkret.

## Slik jobber du
1. Du får ett eller flere skjelett. Alle faste felt er allerede fylt ut: id-er, navn, roller, tall, valg og strukturen.
2. Du skriver bare der det står `TODO_FYLL`. Teksten i parentesen forteller hva som skal stå der.
3. Erstatt HELE verdien, inkludert `TODO_FYLL` og parentesen. Verdien skal bare inneholde den ferdige teksten.
4. Der det står `TODO_FYLL_KILDER`: skriv en liste med verdier fra listen i parentesen, og ingen andre.
5. Der det står `TODO_FYLL_LISTE`: skriv en liste med 2 eller 3 korte regler.
6. Lever hele filen på nytt. Ikke utelat noe, ikke legg til felt, ikke endre rekkefølge.

## Skriveregler (kontrolleres automatisk, brudd gir feil)
- Norsk bokmål. Korte, konkrete setninger som beskriver, ikke setninger som snakker til leseren.
- **Ingen tall i fritekst.** Ikke sifre, ikke datoer, ikke frister, ikke prosent, ikke beløp, ikke antall. Tall er allerede satt i de faste feltene.
- **Ingen personnavn i fritekst.** Bruk roller, og bare disse: Museumsdirektør, Samlingsforvalter, Kurator, Formidler, Museumsvert, Driftsansvarlig, Kvalitetsvokter, Kafeansvarlig, Verneombud, Brannvernleder, Konservator, Styret. Feltene `kontaktperson`, `intern_eier_navn` og e-postfeltene er oppdiktede og ferdig utfylt av koden. Ikke endre dem, og ikke gjenta navnene i fritekst.
- **Ingen kontaktdetaljer i fritekst:** ingen e-post, telefonnummer, adresser eller lenker.
- **Ingen paragrafer og ingen sitater fra lover eller forskrifter.** Du kan beskrive hva en myndighet vanligvis ber om, uten å vise til lovtekst.
- Ingen emoji, ingen overskrifter, ingen markdown i verdiene, ingen kodegjerder rundt filen.
- Hver tekst skal være **unik**. Ikke kopier setninger mellom felt eller oppføringer.
- Hver tekst skal være mellom 20 og 160 tegn, med mindre skjelettet sier noe annet.
- Ikke skriv som en chat-assistent. Ingen «Her er», «Selvfølgelig» eller forklaringer før eller etter filen.
- Ikke finn på nye myndigheter, roller, frister eller rapporter.

## Eksempler
Bra:
- `hva_de_vil`: Dokumentert internkontroll og oversikt over hvordan avvik følges opp.
- `utloser`: Varslet tilsyn, uvarslet besøk eller klage fra en gjest.
- `begrunnelse`: Rapporten bygger på data som allerede finnes og kan settes sammen uten skjønn.

Dårlig, og hvorfor:
- «Frist: 30 dager etter besøket.» (tall)
- «Ta kontakt med Kari på kari@eksempel.no.» (personnavn og e-post)
- «I henhold til § 5 skal virksomheten...» (paragraf)
- «Selvfølgelig! Her er teksten du ba om.» (chat-snakk)

## Selvsjekk før du leverer
- Står det noen `TODO_FYLL` igjen? Da er du ikke ferdig.
- Finnes det sifre i noen av tekstene dine? Fjern dem.
- Er to tekster like eller nesten like? Skriv om en av dem.
- Har du endret en id, et navn, en rolle eller et tall? Endre det tilbake.
- Er filen ren YAML uten tekst rundt?

## Hva skjer etterpå
En kontroll sammenligner leveransen din med skjelettet og sender deg en liste over feil. Du retter og leverer hele filene på nytt.
Det tas høyst tre runder. Deretter vurderer et menneske resultatet. Ingenting tas i bruk uten menneskelig godkjenning.

## Levering
Lever hver fil som en egen blokk, merket med filnavnet:

### filnavn.yaml
```yaml
...
```

## Skjelettene

### rapporteringskalender.yaml  (Rapporteringskalender)
```yaml
klassifisering: syntetisk
syntetisk: true
merknad: Treningsdata, ikke rettesnor. Alle frister, terskler og timer er oppdiktet.
versjon: 1
rapporter:
- id: RP-01
  rapport: Månedlig driftsrapport
  mottaker: Museumsdirektør
  mottakertype: intern
  frekvens: månedlig
  antall_per_ar: 12
  maned: Månedlig
  eier: Driftsansvarlig
  timer_per_gang: 2
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-02
  rapport: Besøkstall og statistikk
  mottaker: Kulturdirektoratet
  mottakertype: ekstern
  frekvens: årlig
  antall_per_ar: 1
  maned: Mars
  eier: Driftsansvarlig
  timer_per_gang: 14
  godkjenning: eier
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-03
  rapport: Tilskuddsrapport
  mottaker: Kulturdirektoratet
  mottakertype: ekstern
  frekvens: årlig
  antall_per_ar: 1
  maned: Mars
  eier: Museumsdirektør
  timer_per_gang: 36
  godkjenning: eier
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-04
  rapport: Årsregnskap og årsberetning
  mottaker: Stiftelsestilsynet
  mottakertype: ekstern
  frekvens: årlig
  antall_per_ar: 1
  maned: Juni
  eier: Museumsdirektør
  timer_per_gang: 24
  godkjenning: eier
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-05
  rapport: HMS-årsrapport
  mottaker: Styret
  mottakertype: intern
  frekvens: årlig
  antall_per_ar: 1
  maned: Januar
  eier: Museumsdirektør
  timer_per_gang: 10
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-06
  rapport: Avviksrapport
  mottaker: Internt arkiv
  mottakertype: intern
  frekvens: løpende
  antall_per_ar: 10
  maned: Løpende
  eier: Driftsansvarlig
  timer_per_gang: 2
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-07
  rapport: IK-Mat-sammenstilling
  mottaker: Internt arkiv
  mottakertype: intern
  frekvens: månedlig
  antall_per_ar: 12
  maned: Månedlig
  eier: Kafeansvarlig
  timer_per_gang: 1.5
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-08
  rapport: Vernerundeprotokoll
  mottaker: Verneombud
  mottakertype: intern
  frekvens: kvartalsvis
  antall_per_ar: 4
  maned: Kvartalsvis
  eier: Driftsansvarlig
  timer_per_gang: 1
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-09
  rapport: Tilstandsrapport samling
  mottaker: Museumsdirektør
  mottakertype: intern
  frekvens: årlig
  antall_per_ar: 1
  maned: November
  eier: Samlingsforvalter
  timer_per_gang: 6
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-10
  rapport: Brannøvelsesrapport
  mottaker: Internt arkiv
  mottakertype: intern
  frekvens: årlig
  antall_per_ar: 1
  maned: Mars
  eier: Driftsansvarlig
  timer_per_gang: 3
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-11
  rapport: Innlånsoversikt
  mottaker: Museumsdirektør
  mottakertype: intern
  frekvens: årlig
  antall_per_ar: 1
  maned: Desember
  eier: Samlingsforvalter
  timer_per_gang: 4
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
- id: RP-12
  rapport: Styrerapport
  mottaker: Styret
  mottakertype: intern
  frekvens: kvartalsvis
  antall_per_ar: 4
  maned: Kvartalsvis
  eier: Museumsdirektør
  timer_per_gang: 3
  godkjenning: ingen
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva rapporten brukes til'
  kilder: 'TODO_FYLL_KILDER (2 eller 3 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
```
