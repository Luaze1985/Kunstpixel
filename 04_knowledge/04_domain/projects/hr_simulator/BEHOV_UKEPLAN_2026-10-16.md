# Behov og beslutninger: KI-støttet ukeplanlegging

Dato: 2026-10-16
Status: Planlagt, ikke implementert. Bekreftede brukerbehov fra samtalen.

## Mål
Øve på KI-støttet bemanningsplanlegging og kontekstforståelse ved et fiktivt museum. KI skal foreslå én samlet ukeplan for flere arrangementer og faste oppgaver. Brukeren vurderer anbefalingen gjennom begrunnelser, kildegrunnlag, automatiske kontroller og udekkede behov.

## Avtalte valg
- Lokal kjøring med Python 3.13, fiktive data og egen SQLite-state.
- Gjenbruk arbeidet på feature/hr-simulator-syntetisk-innleie; ikke bygg en parallell simulator fra main.
- Museumsdatabasen 05_data/museum.db forblir skrivebeskyttet og uendret.
- Research og kontrollert datagrunnlag leveres først. Researchfunn skal omsettes til sporbare prosjektkilder før API, brukerflate og KI bygges videre.
- Én uke planlegges om gangen. Fire sammenhengende uker gir historikk og kontekst for belastning og arbeidstid.
- Avtalte arrangementstider beholdes. KI kan fordele ansatte og foreslå ekstravakter.
- Prioriter minst mulig endring i avtalte vakter, deretter jevn fordeling av belastning, innenfor kontrollerte krav.
- KI lager forslag automatisk uten avklaringsspørsmål. Manglende fakta markeres og kan hindre godkjenning.
- Ett anbefalt forslag viser endringer fra gjeldende plan, begrunnelser, kilder og udekkede behov.
- Brukeren godkjenner/avviser hver endring; avhengige endringer behandles som én beslutningsgruppe. Hele uka kontrolleres før lagring.
- Kontakt og svar registreres manuelt. Forespurt, ja og bekreftet tildeling er forskjellige statuser.
- Status bevares ved arrangementsbytte, sideoppdatering og omstart.
- Demomodus har isolerte scenarioer som kan nullstilles uten å påvirke arbeidsoversikten.
- HR omfatter arbeidstid, opplæring, tilgjengelighet og belastningsfordeling. Personalsaker utsettes.
- OpenAI API kobles til som siste trinn etter lokal testing. Modellnavn konfigureres eksplisitt før første modellkjøring.
- Enkel brukerflyt avklares tidlig; visuell finpuss følger etter at en hel arbeidsflyt er prøvd.

## Hva som er repoets sannhet
1. Kilderegister med primærkilde, URL, tittel, publiserings-/oppdateringsdato når kjent, kontrollert dato, støttet påstand og kildeavgrensning.
2. Museumsrutiner med egne ID-er og skille mellom dokumentert eksempel, regelverkskrav og valgt rutine for det fiktive museet.
3. Maskinlesbare fiktive personer, vakter, aktiviteter, krav og kontaktforløp. Oppdiktede verdier merkes som øvingsdata.
4. Beslutningslogg og mangelliste. Ukjente forhold er ikke bekreftede fakta.
5. Lagret arbeidsplan er gjeldende driftstilstand. KI-svar og nettleseren er ikke selvstendige sannhetskilder.

Museumsrutiner fra én virksomhet skal ikke omtales som universell sedvane. Rettslige forhold og tariffavhengige unntak dokumenteres med anvendelsesområde; simulatoren påstår ikke full juridisk godkjenning. Modellens forkunnskap kan forklare, men skal ikke etablere nye fakta om museet.

## Første fase er ferdig når
- Eksisterende feature-arbeid og HTML-referanse er tilgjengelige i implementeringsutsjekkingen.
- Researchnotat, kilderegister, museumsrutiner og mangelliste er lagret i Git-sporbare filer.
- Det finnes minst tre direkte kontrollerte museumseksempler, samt relevante primærkilder om arbeidstid, arbeidsplan og innleie.
- Fiktive data dekker fire sammenhengende uker, med kompetanse, opplæring, faste oppgaver, arrangementer, kontaktforløp og avbud.
- Hver regel peker til en kilde eller en uttrykkelig fiktiv prosjektbeslutning. Ingen nye museumstall eller personalopplysninger presenteres som observerte fakta.
- Mangler som gjør en kontroll umulig er eksplisitte; kontrollstatus kan være uavklart.

## Leveransebevis
Automatiske tester av data, motor, API og lagring, visuell gjennomgang av arbeidsflyten og en separat ekte OpenAI-kjøring. Dokumenter hva som faktisk er kjørt, hva som besto og hva som gjenstår. Ingen produksjonssetting inngår.
