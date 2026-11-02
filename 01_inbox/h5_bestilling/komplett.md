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

### myndighetskontakter.yaml  (Myndighetskontakter)
```yaml
klassifisering: syntetisk
syntetisk: true
merknad: Treningsdata, ikke rettesnor. Alle frister, terskler og timer er oppdiktet.
versjon: 1
myndigheter:
- id: MK-01
  myndighet: Arbeidstilsynet
  omrade: HMS og arbeidsmiljø
  intern_eier: Museumsdirektør
  kontaktperson: Harald Oskar Vinje
  kontakt_epost: harald.oskar.vinje@arbeidstilsynet.example.test
  intern_eier_navn: Thorvald Berntsen
  intern_eier_epost: thorvald.berntsen@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
- id: MK-02
  myndighet: Mattilsynet
  omrade: Kafé og IK-Mat
  intern_eier: Kafeansvarlig
  kontaktperson: Theodor Sæther
  kontakt_epost: theodor.sather@mattilsynet.example.test
  intern_eier_navn: Astrid Moe
  intern_eier_epost: astrid.moe@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
- id: MK-03
  myndighet: Brann- og redningsetaten
  omrade: Brannsikkerhet og beredskap
  intern_eier: Driftsansvarlig
  kontaktperson: Kristian Hovland
  kontakt_epost: kristian.hovland@brann.example.test
  intern_eier_navn: Edvard Rønning
  intern_eier_epost: edvard.ronning@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
- id: MK-04
  myndighet: Kommunen
  omrade: Skjenke- og serveringsbevilling
  intern_eier: Kafeansvarlig
  kontaktperson: Gunnar Eilif Lunde
  kontakt_epost: gunnar.eilif.lunde@kommunen.example.test
  intern_eier_navn: Astrid Moe
  intern_eier_epost: astrid.moe@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
- id: MK-05
  myndighet: Fylkeskommunen
  omrade: Tilskudd og regionalt kulturarbeid
  intern_eier: Museumsdirektør
  kontaktperson: Harriet Dahlen
  kontakt_epost: harriet.dahlen@fylkeskommunen.example.test
  intern_eier_navn: Thorvald Berntsen
  intern_eier_epost: thorvald.berntsen@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
- id: MK-06
  myndighet: Kulturdirektoratet
  omrade: Museumsstatistikk, tilskudd og samlingsforvaltning
  intern_eier: Museumsdirektør
  kontaktperson: Frits Strømme
  kontakt_epost: frits.stromme@kulturdirektoratet.example.test
  intern_eier_navn: Thorvald Berntsen
  intern_eier_epost: thorvald.berntsen@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
- id: MK-07
  myndighet: Datatilsynet
  omrade: Personvern
  intern_eier: Driftsansvarlig
  kontaktperson: Oda Marie Skogen
  kontakt_epost: oda.marie.skogen@datatilsynet.example.test
  intern_eier_navn: Edvard Rønning
  intern_eier_epost: edvard.ronning@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
- id: MK-08
  myndighet: Stiftelsestilsynet
  omrade: Årsregnskap og tilsyn med stiftelsen
  intern_eier: Museumsdirektør
  kontaktperson: Gerhard Nygaard
  kontakt_epost: gerhard.nygaard@stiftelsestilsynet.example.test
  intern_eier_navn: Thorvald Berntsen
  intern_eier_epost: thorvald.berntsen@kunstpixel.example.test
  hva_de_vil: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva myndigheten ber om fra oss'
  utloser: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som utløser kontakt'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon de vanligvis ber om'
  merknad: treningsdata, ikke rettesnor
```

### tilsynsbesok_rutine.yaml  (Tilsynsbesøk)
```yaml
klassifisering: syntetisk
syntetisk: true
merknad: Treningsdata, ikke rettesnor. Alle frister, terskler og timer er oppdiktet.
versjon: 1
avvik_frister:
  gult_avvik_lukkes_innen: 14 dager
  rodt_avvik_lukkes_innen: 24 timer
steg:
- nr: 1
  navn: Varsel kommer
  ansvarlig: Driftsansvarlig
  handling: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som gjøres i dette steget'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon som trengs'
- nr: 2
  navn: Samle dokumentasjon
  ansvarlig: Driftsansvarlig
  handling: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som gjøres i dette steget'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon som trengs'
- nr: 3
  navn: Under besøket
  ansvarlig: Museumsdirektør
  handling: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som gjøres i dette steget'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon som trengs'
- nr: 4
  navn: Tilbakemelding
  ansvarlig: Museumsdirektør
  handling: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som gjøres i dette steget'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon som trengs'
- nr: 5
  navn: Skriftlig svar
  ansvarlig: Museumsdirektør
  handling: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som gjøres i dette steget'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon som trengs'
- nr: 6
  navn: Lukke avvik
  ansvarlig: Driftsansvarlig
  handling: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som gjøres i dette steget'
  dokumentasjon: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hvilken dokumentasjon som trengs'
```

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

### rapportmaler.yaml  (Rapportmaler)
```yaml
klassifisering: syntetisk
syntetisk: true
merknad: Treningsdata, ikke rettesnor. Alle frister, terskler og timer er oppdiktet.
versjon: 1
maler:
- id: ML-01
  navn: Driftsrapport
  brukes_til:
  - RP-01
  godkjenning: ingen
  status_ved_opprettelse: Utkast
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva malen brukes til'
  felt:
  - navn: Periode
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Periode'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Gjennomførte arrangementer
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Gjennomførte arrangementer'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Kommende arrangementer
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Kommende arrangementer'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Avvik og tiltak
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Avvik og tiltak'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Vedlikehold
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Vedlikehold'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  regler: 'TODO_FYLL_LISTE (2 eller 3 korte regler, uten tall): regler for utfylling og bruk av malen'
- id: ML-02
  navn: Avviksrapport
  brukes_til:
  - RP-06
  godkjenning: ingen
  status_ved_opprettelse: Utkast
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva malen brukes til'
  felt:
  - navn: Hva skjedde
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Hva skjedde'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Når og hvor
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Når og hvor'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Alvorlighetsgrad
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Alvorlighetsgrad'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Umiddelbart tiltak
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Umiddelbart tiltak'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Varig tiltak
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Varig tiltak'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Frist for lukking
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Frist for lukking'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  regler: 'TODO_FYLL_LISTE (2 eller 3 korte regler, uten tall): regler for utfylling og bruk av malen'
- id: ML-03
  navn: Tilskuddsrapport
  brukes_til:
  - RP-02
  - RP-03
  godkjenning: eier
  status_ved_opprettelse: Utkast
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva malen brukes til'
  felt:
  - navn: Periode
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Periode'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Besøkstall
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Besøkstall'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Gjennomførte aktiviteter
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Gjennomførte aktiviteter'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Utstillinger
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Utstillinger'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Måloppnåelse
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Måloppnåelse'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  regler: 'TODO_FYLL_LISTE (2 eller 3 korte regler, uten tall): regler for utfylling og bruk av malen'
- id: ML-04
  navn: Svar til tilsyn
  brukes_til:
  - Tilsynsbesøk steg 5
  godkjenning: eier
  status_ved_opprettelse: Utkast
  formal: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva malen brukes til'
  felt:
  - navn: Saksreferanse
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Saksreferanse'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Kort oppsummering
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Kort oppsummering'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Funn og vår vurdering
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Funn og vår vurdering'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Tiltak med frist
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Tiltak med frist'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  - navn: Ansvarlig rolle
    beskrivelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hva som skal stå i feltet Ansvarlig rolle'
    kilde: 'TODO_FYLL_KILDER (1 eller 2 av: besøkstall, utstillinger, regnskap, hendelser, avviksregister, temperaturlogg, vernerunder, samlingsdatabase, brannøvelser, innlån, styrereferat, driftslogg, manuell)'
  regler: 'TODO_FYLL_LISTE (2 eller 3 korte regler, uten tall): regler for utfylling og bruk av malen'
```

### arbeidsoppgaver_tidsbruk.yaml  (Arbeidsoppgaver og tidsbruk)
```yaml
klassifisering: syntetisk
syntetisk: true
merknad: Treningsdata, ikke rettesnor. Alle frister, terskler og timer er oppdiktet.
versjon: 1
oppgaver:
- id: AO-01
  omrade: Myndighetskontakt
  oppgave: Tilskuddssøknad
  myndighet: Kulturdirektoratet
  rolle: Museumsdirektør
  timer_per_ar: 40
  automatiseringspotensial: Middels
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-02
  omrade: Myndighetskontakt
  oppgave: Følge opp avvik og pålegg
  myndighet: Flere
  rolle: Driftsansvarlig
  timer_per_ar: 20
  automatiseringspotensial: Middels
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-03
  omrade: Myndighetskontakt
  oppgave: Forberede tilsyn fra Arbeidstilsynet
  myndighet: Arbeidstilsynet
  rolle: Museumsdirektør
  timer_per_ar: 16
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-04
  omrade: Myndighetskontakt
  oppgave: Forberede tilsyn fra Mattilsynet
  myndighet: Mattilsynet
  rolle: Kafeansvarlig
  timer_per_ar: 12
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-05
  omrade: Myndighetskontakt
  oppgave: Forberede brannøvelse og brannsyn
  myndighet: Brann- og redningsetaten
  rolle: Driftsansvarlig
  timer_per_ar: 10
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-06
  omrade: Myndighetskontakt
  oppgave: Fornye skjenkebevilling
  myndighet: Kommunen
  rolle: Kafeansvarlig
  timer_per_ar: 8
  automatiseringspotensial: Lav
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-07
  omrade: Myndighetskontakt
  oppgave: Svare på personvernhenvendelser
  myndighet: Datatilsynet
  rolle: Driftsansvarlig
  timer_per_ar: 6
  automatiseringspotensial: Lav
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-08
  omrade: Rapportering
  oppgave: Månedlig driftsrapport
  rapport_id: RP-01
  rolle: Driftsansvarlig
  timer_per_ar: 24
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-09
  omrade: Rapportering
  oppgave: Besøkstall og statistikk
  rapport_id: RP-02
  rolle: Driftsansvarlig
  timer_per_ar: 14
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-10
  omrade: Rapportering
  oppgave: Tilskuddsrapport
  rapport_id: RP-03
  rolle: Museumsdirektør
  timer_per_ar: 36
  automatiseringspotensial: Middels
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-11
  omrade: Rapportering
  oppgave: Årsregnskap og årsberetning
  rapport_id: RP-04
  rolle: Museumsdirektør
  timer_per_ar: 24
  automatiseringspotensial: Lav
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-12
  omrade: Rapportering
  oppgave: HMS-årsrapport
  rapport_id: RP-05
  rolle: Museumsdirektør
  timer_per_ar: 10
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-13
  omrade: Rapportering
  oppgave: Avviksrapport
  rapport_id: RP-06
  rolle: Driftsansvarlig
  timer_per_ar: 20
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-14
  omrade: Rapportering
  oppgave: IK-Mat-sammenstilling
  rapport_id: RP-07
  rolle: Kafeansvarlig
  timer_per_ar: 18
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-15
  omrade: Rapportering
  oppgave: Vernerundeprotokoll
  rapport_id: RP-08
  rolle: Driftsansvarlig
  timer_per_ar: 4
  automatiseringspotensial: Middels
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-16
  omrade: Rapportering
  oppgave: Tilstandsrapport samling
  rapport_id: RP-09
  rolle: Samlingsforvalter
  timer_per_ar: 6
  automatiseringspotensial: Middels
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-17
  omrade: Rapportering
  oppgave: Brannøvelsesrapport
  rapport_id: RP-10
  rolle: Driftsansvarlig
  timer_per_ar: 3
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-18
  omrade: Rapportering
  oppgave: Innlånsoversikt
  rapport_id: RP-11
  rolle: Samlingsforvalter
  timer_per_ar: 4
  automatiseringspotensial: Høy
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
- id: AO-19
  omrade: Rapportering
  oppgave: Styrerapport
  rapport_id: RP-12
  rolle: Museumsdirektør
  timer_per_ar: 12
  automatiseringspotensial: Middels
  begrunnelse: 'TODO_FYLL (1 setning, norsk, maks 140 tegn, uten tall): hvorfor potensialet er som angitt'
sum:
  myndighetskontakt: 112
  rapportering: 175
  totalt: 287
```

### historikk_tekst.yaml  (Historikk, tekst per år)
```yaml
klassifisering: syntetisk
syntetisk: true
merknad: Treningsdata, ikke rettesnor. Alle frister, terskler og timer er oppdiktet.
versjon: 1
historikk:
- ar: 2010
  status_ar: endelig
  tema: oppstart
  nokkeltall:
    besok_totalt: 21400
    resultat_tkr: 120
    tilsyn_antall: 2
    avvik_funnet: 5
    timer_totalt: 134
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2011
  status_ar: endelig
  tema: vekst
  nokkeltall:
    besok_totalt: 23100
    resultat_tkr: 150
    tilsyn_antall: 2
    avvik_funnet: 6
    timer_totalt: 144
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2012
  status_ar: endelig
  tema: vekst
  nokkeltall:
    besok_totalt: 24800
    resultat_tkr: 90
    tilsyn_antall: 3
    avvik_funnet: 7
    timer_totalt: 156
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2013
  status_ar: endelig
  tema: vekst
  nokkeltall:
    besok_totalt: 26200
    resultat_tkr: 160
    tilsyn_antall: 3
    avvik_funnet: 6
    timer_totalt: 172
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2014
  status_ar: endelig
  tema: digital samlingsdatabase
  nokkeltall:
    besok_totalt: 28900
    resultat_tkr: 140
    tilsyn_antall: 3
    avvik_funnet: 6
    timer_totalt: 192
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2015
  status_ar: endelig
  tema: vekst
  nokkeltall:
    besok_totalt: 30500
    resultat_tkr: 210
    tilsyn_antall: 4
    avvik_funnet: 5
    timer_totalt: 206
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2016
  status_ar: endelig
  tema: ombygging
  nokkeltall:
    besok_totalt: 29800
    resultat_tkr: -60
    tilsyn_antall: 3
    avvik_funnet: 5
    timer_totalt: 216
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2017
  status_ar: endelig
  tema: ny kafé
  nokkeltall:
    besok_totalt: 33600
    resultat_tkr: 180
    tilsyn_antall: 4
    avvik_funnet: 4
    timer_totalt: 230
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2018
  status_ar: endelig
  tema: vekst
  nokkeltall:
    besok_totalt: 36200
    resultat_tkr: 230
    tilsyn_antall: 4
    avvik_funnet: 4
    timer_totalt: 244
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2019
  status_ar: endelig
  tema: rekordår
  nokkeltall:
    besok_totalt: 38400
    resultat_tkr: 310
    tilsyn_antall: 5
    avvik_funnet: 3
    timer_totalt: 260
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2020
  status_ar: endelig
  tema: pandemi og stengt
  nokkeltall:
    besok_totalt: 11200
    resultat_tkr: -420
    tilsyn_antall: 2
    avvik_funnet: 2
    timer_totalt: 216
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2021
  status_ar: endelig
  tema: pandemi og gjenåpning
  nokkeltall:
    besok_totalt: 15900
    resultat_tkr: -180
    tilsyn_antall: 3
    avvik_funnet: 3
    timer_totalt: 230
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2022
  status_ar: endelig
  tema: gjenoppbygging
  nokkeltall:
    besok_totalt: 31200
    resultat_tkr: 60
    tilsyn_antall: 4
    avvik_funnet: 4
    timer_totalt: 274
    automatiseringsgrad_prosent: 0
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2023
  status_ar: endelig
  tema: digital satsing
  nokkeltall:
    besok_totalt: 35400
    resultat_tkr: 140
    tilsyn_antall: 5
    avvik_funnet: 3
    timer_totalt: 286
    automatiseringsgrad_prosent: 5
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2024
  status_ar: endelig
  tema: nye rapporteringsrutiner
  nokkeltall:
    besok_totalt: 37900
    resultat_tkr: 220
    tilsyn_antall: 5
    avvik_funnet: 3
    timer_totalt: 296
    automatiseringsgrad_prosent: 10
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2025
  status_ar: endelig
  tema: første automatisering
  nokkeltall:
    besok_totalt: 39800
    resultat_tkr: 260
    tilsyn_antall: 6
    avvik_funnet: 2
    timer_totalt: 294
    automatiseringsgrad_prosent: 18
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
- ar: 2026
  status_ar: foreløpig
  tema: KI-pilot
  nokkeltall:
    besok_totalt: 41200
    resultat_tkr: 190
    tilsyn_antall: 6
    avvik_funnet: 2
    timer_totalt: 287
    automatiseringsgrad_prosent: 25
  hendelse: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene'
  laerdom: 'TODO_FYLL (1 setning, norsk, maks 160 tegn, uten tall): hva museet lærte det året, ut fra temaet og nøkkeltallene'
```
