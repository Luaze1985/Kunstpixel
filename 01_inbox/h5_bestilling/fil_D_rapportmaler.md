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
