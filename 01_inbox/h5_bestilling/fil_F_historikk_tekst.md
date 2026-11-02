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
