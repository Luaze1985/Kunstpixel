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
