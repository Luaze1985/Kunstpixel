# AP5 – Område 5: produktivitet, målinger og grensetilfeller

**Kontrolltidspunkt:** 20. oktober 2026  
**Versjon:** 1.0  
**Omfang:** Bare arbeidspakke AP5 / område 5. Ingen persondata eller simulerte tallverdier generert.  
**Virksomhet:** Fiktivt kunstmuseum med 168 ansatte, seks avdelinger og eksisterende syntetiske 54 994 vakter (2010–2026). Dette er brukeroppgitte scenarioopplysninger, ikke kontrollert databaseinnhold.  
**Sammenlikning:** Industri; privat service/kontor; kommune innen KS-området (Oslo kan avvike tariffmessig, men denne pakken handler ikke om tariffbeløp).

## Sammendrag (maks 10 linjer)

1. [Lov/forskrift] Arbeidsmiljøloven §§ 9-1 og 9-2: ansattkontroll krever saklig grunn, forholdsmessighet, drøfting, informasjon og løpende evaluering.
2. [Lov/forskrift] E-postforskriften § 2 andre ledd forbyr i utgangspunktet overvåking av ansattes elektroniske utstyrsbruk, med avgrensede nettverks- og sikkerhetsunntak.
3. [Myndighetsveiledning] GDPR krever særskilt formål, behandlingsgrunnlag, dataminimering, lagringsbegrensning og tilgang etter tjenstlig behov.
4. [Offisiell statistikk] SSBs arbeidskraftproduktivitet er bruttoprodukt per utført timeverk for næringer; det er ikke individprestasjon.
5. [Standard] OEE/ISO 22400 gjelder produksjonsutstyr og produksjonsprosesser, ikke en universell ansattkarakter.
6. [Offisiell statistikk] KOSTRA måler bl.a. kommunal enhetskostnad; høy kostnad kan skyldes kvalitet, behov, smådrift eller lønnsnivå.
7. [Forskning] STAMI finner at sykenærvær kan ha både gunstige og ugunstige virkninger; null fravær innebærer ikke dokumentert høy produktivitet.
8. [Antakelse] Tallfordelinger for museumsarbeideres produktivitet mangler. Vi foreslår derfor scenario- og observasjonsbaserte tabeller, ikke oppdiktede nasjonale normalverdier.

## A. Regler, definisjoner og kildekontroll

**A5-01 [Lov/forskrift] – saklig kontrollformål.** Arbeidsmiljøloven § 9-1 første ledd: kontrolltiltak krever saklig grunn i virksomhetens forhold og må ikke påføre arbeidstaker en uforholdsmessig belastning. Et tallgrunnlag som er nyttig i økonomistyring legitimerer **ikke automatisk** individsporing. Tiltak vurderes også samlet med annen kontroll. [Arbeidstilsynet – Arbeidsmiljøloven kapittel 9, særlig §§ 9-1 og 9-2](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Arbeidstilsynet – Kontroll og overvåking på arbeidsplassen](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/kontroll-og-overvakning/).

**A5-02 [Lov/forskrift] – prosesskrav.** § 9-2 krever så tidlig som mulig drøfting av behov, utforming, gjennomføring og vesentlige endringer med tillitsvalgte; opplysninger om formål, praktiske konsekvenser og antatt varighet til berørte ansatte **før** oppstart; deretter regelmessig evaluering. En ufullstendig drøfting betyr likevel ikke automatisk at hele tiltaket er ulovlig: foreta konkret vurdering. [Arbeidstilsynet – Arbeidsmiljøloven kapittel 9, særlig §§ 9-1 og 9-2](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Arbeidstilsynet – Kontroll og overvåking på arbeidsplassen](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/kontroll-og-overvakning/).

**A5-03 [Lov/forskrift] – særskilt digitalt overvåkingsforbud.** E-postforskriften § 2 andre ledd har som utgangspunkt at arbeidsgiver **ikke har rett til å overvåke arbeidstakers bruk av elektronisk utstyr, inkludert Internett**, unntatt når formålet er administrasjon av datanettverk eller å avdekke/oppklare nettverkssikkerhetsbrudd. Avgrensningen av hvilke data/tiltak som omfattes må vurderes konkret. Å omdøpe tastetrykk-, vindus-, skjerm- eller nettloggsporing til «produktivitets-KPI» gjør ikke tiltaket lovlig. [Datatilsynet – Overvåking av ansattes bruk av elektronisk utstyr; e-postforskriften § 2 andre ledd](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/overvaking-av-ansattes-bruk-av-elektronisk-utstyr/) · [Lovdata – Forskrift om arbeidsgivers innsyn i e-postkasse og annet elektronisk lagret materiale (e-postforskriften)](https://lovdata.no/dokument/SF/forskrift/2018-07-02-1108).

**A5-04 [Lov/forskrift] – personvern er tilleggsvilkår.** GDPR art. 5 og 6, gjennomført ved personopplysningsloven, stiller krav om lovlig behandlingsgrunnlag, spesifikt formål, nødvendige opplysninger, riktighet, begrenset lagring og sikkerhet. Personopplysninger kan ikke fritt gjenbrukes fra adgangs-, IT-sikkerhets- eller timeregistreringssystemer til prestasjonsrangering. Normalt må det gjøres konkret vurdering; ansattsamtykke kan ikke uten videre løse maktubalansen. [Datatilsynet – Personvernprinsippene; GDPR art. 5 og 6](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/) · [Datatilsynet – Personvern på arbeidsplassen, tilgangsbegrensning og lagring](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/).

**A5-05 [Lov/forskrift] – DPIA når høy risiko.** GDPR art. 35: ved planlagt behandling som sannsynligvis medfører høy personvernrisiko skal en vurdering av personvernkonsekvenser utføres **før** behandling. En DPIA erstatter ikke rettslig behandlingsgrunnlag og gjør ikke ulovlig kontroll lovlig. [Datatilsynet – Vurdering av personvernkonsekvenser (DPIA); GDPR art. 35](https://www.datatilsynet.no/rettigheter-og-plikter/virksomhetenes-plikter/vurdering-av-personvernkonsekvenser/).

**A5-06 [Myndighetsveiledning] – tilgang og formål.** Datatilsynet beskriver krav om tjenstlig behov og lagring bare så lenge nødvendig. Et avdelingsdashboard som muliggjør identifikasjon ved små grupper er ikke nødvendigvis anonymisert. Det er ingen verifisert, universell norsk lovfestet minimumsstørrelse (som «minst fem») som alene gjør slike rapporter trygge. [Datatilsynet – Personvern på arbeidsplassen, tilgangsbegrensning og lagring](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/) · [Datatilsynet – Personvernprinsippene; GDPR art. 5 og 6](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/).

**A5-07 [Myndighetsveiledning] – hvilke målinger passer til hvilket nivå?** Industrianlegg kan bruke OEE, kassasjon, stopp og leveransepresisjon; service kan bruke ventetid, ferdigstilte oppdrag og kvalitet; kommune kan bruke KOSTRA, saksbehandlingstid og kvalitets-/dekningsindikatorer. **Eksemplene er virksomhetsstyringsmål, ikke lovbestemte prestasjonsterskler.** [SSB – Produktivitetsberegninger for næringer: bruttoprodukt per utført timeverk](https://www.ssb.no/nasjonalregnskap-og-konjunkturer/nasjonalregnskap/artikler/produktivitetsberegninger-for-naeringer) · [SSB – KOSTRA dokumentasjon: produktivitet/enhetskostnader med kvalitetsforbehold](https://www.ssb.no/offentlig-sektor/kostra/statistikk/kostra-kommune-stat-rapportering/om-kostra/dokumentasjon-av-kostra) · [ISO – ISO 22400-1:2014; rammeverk for produksjons-KPI](https://www.iso.org/standard/56847.html).

**A5-08 [Standard] – OEE.** ISO 22400-1:2014 gir produksjons-KPI-rammeverket, ISO 22400-2:2014 definisjoner. En vanlig OEE-modell er tilgjengelighet × ytelse × kvalitetsandel (alle som forholdstall); presise definisjoner av planlagt tid, mikrostopp, omarbeiding m.m. må dokumenteres lokalt. ISO oppgir at ny ISO/DIS 22400-2 er **under utvikling** per kontrolltidspunktet: utkastet er ikke gjeldende standard. OEE beskriver utstyret/arbeidsenheten og må ikke betegnes som personens innsats. [ISO – ISO 22400-1:2014; rammeverk for produksjons-KPI](https://www.iso.org/standard/56847.html) · [ISO – ISO 22400-2:2014; produksjons-KPI/OEE](https://www.iso.org/standard/54497.html) · [ISO – ISO/DIS 22400-2: utgave 2 er under utvikling](https://www.iso.org/standard/87563.html).

**A5-09 [Offisiell statistikk] – næringsproduktivitet.** SSB definerer arbeidskraftproduktivitet normalt som **bruttoprodukt per utført timeverk**, der volum i faste priser brukes ved tidsserieanalyse. Målet påvirkes av kapital, teknologi, organisering og kapasitetsutnyttelse. Statistikkbanken tabell **09174** har år til og med 2025 og er oppdatert 28.05.2026. Den gjelder næringer, ikke ansatte eller avdelinger i et museum. [SSB – Produktivitetsberegninger for næringer: bruttoprodukt per utført timeverk](https://www.ssb.no/nasjonalregnskap-og-konjunkturer/nasjonalregnskap/artikler/produktivitetsberegninger-for-naeringer) · [SSB Statistikkbanken – Tabell 09174: lønn, sysselsetting og produktivitet etter næring](https://www.ssb.no/statbank/table/09174/).

**A5-10 [Offisiell statistikk] – KOSTRA.** SSB deler indikatorer i prioritering, dekning, produktivitet/enhetskostnader og tjenesteindikatorer. Enhetskostnad gir ikke alene svar på kvalitet, behov, pleietyngde, lønnsnivå eller geografi. Reviderte 2025-tall ble publisert 15.06.2026. [SSB – KOSTRA dokumentasjon: produktivitet/enhetskostnader med kvalitetsforbehold](https://www.ssb.no/offentlig-sektor/kostra/statistikk/kostra-kommune-stat-rapportering/om-kostra/dokumentasjon-av-kostra) · [SSB – Reviderte KOSTRA-tall 2025](https://www.ssb.no/offentlig-sektor/kostra/statistikk/kostra-kommune-stat-rapportering/artikler/nye-kostra-tall).

**A5-11 [Lov/forskrift] – hjemmekontor.** Hjemmekontorforskriften §§ 1–2 omfatter fast arbeid i eget hjem, ikke kortvarig/sporadisk arbeid med særskilte unntak. Når forskriften gjelder, kreves skriftlig tilleggsavtale om bl.a. omfang og arbeidstid. **Hjemmekontor er ikke et selvstendig rettsgrunnlag for skjermovervåking**. [Arbeidstilsynet – Forskrift om arbeid som utføres i arbeidstakers hjem, §§ 1–3](https://www.arbeidstilsynet.no/regelverk/forskrifter/hjemmekontorforskriften/) · [Arbeidstilsynet – Hjemmekontor: fast, sporadisk og kortvarig ordning](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/heimekontor) · [Datatilsynet – Overvåking av ansattes bruk av elektronisk utstyr; e-postforskriften § 2 andre ledd](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/overvaking-av-ansattes-bruk-av-elektronisk-utstyr/).

**A5-12 [Lov/forskrift] – tidsgrunnlaget.** Arbeidsgiver skal føre oversikt over hvor mye den enkelte har arbeidet (arbeidsmiljøloven § 10-7). Dette er grunnlag for arbeidstidskontroll og korrekt nevner i driftstall, ikke et generelt samtykke til å måle hver tastetrykkhendelse. Deltid, merarbeid og overtid må skilles. [Arbeidstilsynet – Registrering av arbeidstid; faktisk utført arbeidstid](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/registrering-av-arbeidstid/) · [Arbeidstilsynet – Arbeidsmiljøloven kapittel 9, særlig §§ 9-1 og 9-2](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).

**A5-13 [Forskning] – sykenærvær.** STAMI beskriver sykenærvær som å arbeide når man føler seg syk, og at følgene kan være både positive og negative. Det finnes ikke grunnlag for å bruke antatt sykenærvær som individvariabel utledet av antall besøk, vakter eller digitalt nærvær. [STAMI – Sykenærværstyper i norsk arbeidsliv](https://stami.no/prosjekt/sykenaervaerstyper-i-norsk-arbeidsliv/) · [STAMI – Kontorløsning og sykenærvær](https://stami.no/kontorlosning-kan-pavirke-om-man-er-hjemme-eller-pa-jobb-nar-man-er-syk/) · [STAMI – Hva er sykenærvær og hvorfor er det viktig?](https://stami.no/hva-er-sykenaervaer-og-hvorfor-er-det-viktig/).

**A5-14 [Tariffavtale] – sektorskille.** Ingen generell tariffbestemmelse for «OEE-grense», «antall saker per ansatt» eller «produktivitet per time» er bekreftet for Virke/NHO/KS. Lokale arbeidstids-, oppgave- eller medbestemmelsesavtaler kan påvirke innføringen av systemet, men tariffhjemmel og punkt er **ikke funnet** for universell produktivitetsgrense. Kilden må være konkret avtale-ID og gyldighetsdato før et slikt vilkår brukes. [Arbeidstilsynet – Arbeidsmiljøloven kapittel 9, særlig §§ 9-1 og 9-2](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Arbeidstilsynet – Kontroll og overvåking på arbeidsplassen](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/kontroll-og-overvakning/).

## B. Forskjeller mellom sektorene

| Tema | Industri | Privat service/kontor | Kommune |
|---|---|---|---|
| Vanlige driftsmål [Bransjepraksis] | OEE (maskin), kassasjon, energi per enhet, produksjonsstans | Køtid, kundesaker, leveringstid, gjenåpning/feilretting og kundetilfredshet | KOSTRA-dekning/enhetskostnader, kvalitetsindikatorer og tjenestetilgang |
| Riktig enhet [Antakelse] | Linje, maskin, batch, produkt | Team, prosess, sakstype | Tjeneste, kommune, institusjon, fagområde |
| Kvalitetskorreksjon [Antakelse] | Produktmiks, vedlikehold, skift, råvarefeil | Saksalvorlighet, kompleksitet, kundegrunnlag, samspill | Brukerbehov, kvalitet, bosetting, geografisk spredning |
| Arbeidstidsnevner [Lov/forskrift] | Faktiske timeverk, skift, innleie etter definisjon | Faktiske timeverk, deltid, kundeåpningstid | Årsverk/timeverk; ikke tell alle som 100 % |
| Kontrollgrenser [Lov/forskrift] | AML kap. 9 + GDPR + e-postforskriften | Samme; særlig digitale verktøy/aktivitetssporing | Samme; i tillegg tjeneste- og forvaltningskontekst |
| Offentlig sammenligning [Offisiell statistikk] | SSB 09174, korrekt næringskode | SSB 09174 for riktig service-/kontornæring | SSB KOSTRA; per tjeneste og med kvalitet/strukturforbehold |

**Viktig:** Industri er del av privat sektor. Her betyr «privat» service/kontor uten industri. KOSTRA må ikke likestilles med personvurdering i KS-systemet.

## C. Ti typiske spørsmål med fasit

Maskinlesbar fasit `Q-5-01`–`Q-5-10` ligger i `AP5_fasit_sporsmal.csv`. Minst fire spørsmål har vanskelighetsmarkering. Fasit besvarer blant annet «kan arbeidsgiver se tastetrykk/PC-bruk», «kan maskin-OEE brukes mot operatøren», «er høy KOSTRA-enhetskostnad ineffektivitet», «hvordan sammenligne deltid», «sykenærvær», «hjemmekontor», «må vi drøfte» og «er små team anonyme».

## D. Realistiske tall, fordelinger og statistisk avgrensning

**D5-01 [Offisiell statistikk] – næringsproduktivitet:** [SSB 09174](https://www.ssb.no/statbank/table/09174/) er en **årlig serie 1970–2025**, oppdatert **28.05.2026**, for næringer, timer og arbeidsproduktivitet. Den gir et empirisk grunnlag for **fordelinger av årsvekst over tid innen samme næring**, etter uttrekk og konsistent basisår. Ikke kopier én års endring som individfordeling; **konkrete 2025-rater er ikke uttrekt** i AP5 og er ikke oppdiktet.

**D5-02 [Offisiell statistikk] – KOSTRA:** Reviderte **2025**-tall ble publisert **15.06.2026**. Tabell [13502](https://www.ssb.no/statbank/table/13502/) har utvalgte barnehageindikatorer og [06804](https://www.ssb.no/statbank/table/06804/) er en nøkkeltallstabell for grunnskole. Ved senere uttrekk kan en velge **ett mål × år × kommunegruppe** og vise median, 25-/75-persentil og variasjonsbredde. I AP5 er **ikke** kommuneverdier tatt ut; ingen slike persentiler oppgis. Bruk funksjon og definisjon før sektorbenchmark.

**D5-03 [Offisiell statistikk] – illustrasjon av ulik nevner:** SSBs barnehagestatistikk for **2025** viser **264 210 barn** og **97 585 ansatte** nasjonalt. Dette er **ikke** et mål på barnehageansattes produktivitet: ansatte er personer, ikke standardiserte årsverk, og antall barn tar ikke høyde for alder, oppholdstid eller støttebehov. Tall brukes kun for å demonstrere nevnerproblemet. [SSB 2025](https://www.ssb.no/utdanning/barnehager/statistikk/barnehager).

**D5-04 [Standard] – avgrenset OEE-verdiområde:** Faktorene tilgjengelighet, ytelse og kvalitet er forholdstall, og en konsistent normert modell har komponenter mellom 0 og 1, slik at OEE presenteres **0–100 %**. Dette er et **matematisk domene**, ikke en empirisk nasjonal fordeling. Skift, linje, produkttype og definerte planlagte stopp skal dokumenteres før beregning. [ISO 22400-2](https://www.iso.org/standard/54497.html).

**D5-05 [Antakelse] – museum:** For fiktivt museum er fordelingene for sakstider, besøk per åpningstime, utstillingsvedlikehold, produksjonsstopp, kvalitet og individuelle resultat ikke tilgjengelige. **Ikke funnet** dokumentert mikrofordeling for de 168 ansatte eller seks avdelinger. Foreslått metode: registrer først syntetiske hendelser og sammenlign deretter *observerte syntetiske* aggregater mellom scenarier. Ikke trekk fordelingsparametere fra eksterne næringstall uten populasjonssamsvar.

**D5-06 [Antakelse] – ulik vekting:** Bruk **ikke** felles «produktivitetsscore 0–100» for undervisning, kundeservice, maskiner og HMS. Vekt må forankres i formål, kvalitetsmål og etterprøvbar definisjon. Fordeling/kalibrering kan ikke gis før slik definisjon er laget. Test heller nevner=0, svært små grupper, ekstremt lange vakter, stor oppgavemiks og mulig re-identifisering.

## E. Forslag til syntetiske data

Sju skjemaer i `AP5_datasett_forslag.yaml`:

1. `hr_maalekatalog`: godkjent måledefinisjon, enhet, aggregeringsnivå, beregning og kildeversjon.
2. `hr_maalestyring_vurdering`: kontrolltiltakets formål, nødvendighet, drøfting, informering, behandlingsgrunnlag, lagring, eventuelt DPIA og go/no-go.
3. `hr_team_kpi_periode`: måling på avdeling/team/periode, kvalitet, oppgavemiks og nevner.
4. `hr_industri_utstyrskjoring`: teknisk OEE, produksjon, stopp og kassasjon for maskin/linje (aldri personscore).
5. `hr_service_saksflyt`: serviceoppdrag og behandlingstid (syntetisk, uten kundenavn).
6. `hr_kommunal_kostra_referanse`: eksterne 2025-nøkkeltall med tabell, variabel, enhet og vedlikehold av kildeversjon (verdier kan stå tomme).
7. `hr_arbeidsinnsats_aggregat`: kun aggregert faktisk timeverk per periode og gruppe, avledet fra AP3 og vaktgrunnlaget uten helseprofil.

Ingen helsedetaljer, tastetrykk, skjermbilder, GPS-spor eller private opplysninger foreslås. Ansatt-ID brukes bare **internt ved nødvendig timeverksaggregering**, ikke som nøkkel i det offentlig synlige produktivitetsdashboardet. Reelle SQLite-feltnavn må bekreftes før implementering.

## F. Deterministiske kontrollregler

`AP5_regler_forslag.csv` inneholder `R-5-01`–`R-5-16` og `R-5-90`–`R-5-99` (én fallback per fasitspørsmål). Regelmotoren skal primært **validere måleoppsettet og datakvaliteten**, ikke konkludere om personen eller lovligheten i enkeltsaker.

- **F5-01:** Hvis `kontrolltiltak = ja` og `saklig_formaal_dokumentert != ja` → `STOPP_FOER_OPPSTART` og manuell juridisk/personvernfaglig vurdering.
- **F5-02:** Hvis `drøfting / informasjon / evaluering` mangler → `MANGLENDE_PROSESSDOKUMENTASJON`; ikke automatisk `ulovlig`.
- **F5-03:** Hvis `elektronisk_bruksovervaking = ja` og formål er produktivitet → `STOPP_DIGITAL_OVERVAKING` og kontroller e-postforskriften § 2 annet ledd.
- **F5-04:** Hvis identifiserbare persondata inngår og behandlingsgrunnlag mangler → `INGEN_AKTIVERING`.
- **F5-05:** Hvis personvernrisiko er `høy` og DPIA ikke fullført → `INGEN_AKTIVERING`.
- **F5-06:** Hvis `kpi_nivaa = person` og kildedefinisjon er maskin-OEE eller KOSTRA → `UGYLDIG_SAMMENLIGNING`.
- **F5-07:** Hvis nevner mangler eller er null → KPI ikke beregnbar; aldri automatisk `0`.
- **F5-08:** Hvis faktisk arbeidstid blandes med planlagt tid uten valg av målegrunnlag → `NEVNER_MA_AVKLARES`.
- **F5-09:** Hvis sammenlignede grupper har forskjellig oppgavemiks/kvalitet eller periode → `IKKE_SAMMENLIGNBAR`.
- **F5-10:** Hvis `identifiseringsrisiko = uavklart` → blokker deling av gruppetall. **Ingen fast gruppestørrelse = generell lovgrense.**
- **F5-11:** Hvis OEE-faktor ligger utenfor matematiske grenser eller mangler → `KVALITETSKONTROLL`; målemetode må dokumenteres.
- **F5-12:** Hvis individmåling/IT-logg gjenbrukes fra sikkerhets- eller arbeidstidssystem → sjekk spesifikt formål og regelgrunnlag før sekundærbruk.
- **F5-13:** Hvis `sykenaervaer_automatisk_avledet = ja` → `STOPP`: helseforhold kan ikke utledes automatisk av aktivitetsdata.
- **F5-14:** Hvis vedvarende hjemmekontor uten registrert avtale → `MANUELL_KONTROLL`, gitt forskriftens virkeområde.
- **F5-15:** Hvis aggregat har manglende kildeår, kommune, NACE eller måledefinisjon → `IKKE_RAPPORTER`.
- **F5-16:** Hvis faktisk arbeidstidsgrunnlag ikke er registrert → rapporter `DATAMANGEL`, ikke ansattfeil.

Sikkerhetsport: Ved ukjent faktisk forhold, privat/identifiserbar måling eller rettslig tvil returneres `MANUELL_KONTROLL` eller `UTILSTREKKELIG_GRUNNLAG`, aldri automatisert «dårlig ansatt», «misbruk», «lovlig» eller «ulovlig».

## G. Grensetilfeller, usikkerhet og djevelens advokat

1. **G5-01 [Lov/forskrift] – digital sporing:** En lovlig IT-sikkerhetslogg blir ikke uten videre lovlig som løpende individuell prestasjonslogg. Kontroll av faktisk formål og e-postforskriftens unntak går foran slagord om effektivisering. [Datatilsynet – Overvåking av ansattes bruk av elektronisk utstyr; e-postforskriften § 2 andre ledd](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/overvaking-av-ansattes-bruk-av-elektronisk-utstyr/) · [Datatilsynet – Personvernprinsippene; GDPR art. 5 og 6](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/). Metode M04/M10.
2. **G5-02 [Lov/forskrift] – kontroll vs. observasjon:** Vanlig aggregert driftstelling og kontroll over ansatte kan gli over i hverandre ved individ-ID, små grupper og sekundærbruk. Lovlighetsvurdering må gjøres per system og formål. [Arbeidstilsynet – Arbeidsmiljøloven kapittel 9, særlig §§ 9-1 og 9-2](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Arbeidstilsynet – Kontroll og overvåking på arbeidsplassen](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/kontroll-og-overvakning/). Metode M01/M04.
3. **G5-03 [Offisiell statistikk] – KOSTRA-proxy:** Lavere enhetskostnader kan skyldes lavere kvalitet eller andre behov. KOSTRA er ikke en ferdig justert effektivitetsrangering. [SSB – KOSTRA dokumentasjon: produktivitet/enhetskostnader med kvalitetsforbehold](https://www.ssb.no/offentlig-sektor/kostra/statistikk/kostra-kommune-stat-rapportering/om-kostra/dokumentasjon-av-kostra). Metode M04/M09.
4. **G5-04 [Standard] – OEE-fortolkning:** Standardutkastet i 2026 må ikke fremstilles som gjeldende standard; måleformel og stopptidsdefinisjon må følge dokumentert versjon. [ISO – ISO 22400-2:2014; produksjons-KPI/OEE](https://www.iso.org/standard/54497.html) · [ISO – ISO/DIS 22400-2: utgave 2 er under utvikling](https://www.iso.org/standard/87563.html). Metode M09.
5. **G5-05 [Antakelse] – deltid/overtid:** Sammenligning basert på totalt antall saker favoriserer mange arbeidstimer; per timeverk kan fortsatt skjevfordeles av oppgavemiks, hjelp fra andre og overtid. AP3 må levere kompatibelt timeverksgrunnlag. Metode M01/M07.
6. **G5-06 [Forskning] – sykenærvær:** En ansatt uten sykefravær kan arbeide mens vedkommende er syk, eller ha annen situasjon; det kan ikke utledes av antall arbeidede timer. [STAMI – Sykenærværstyper i norsk arbeidsliv](https://stami.no/prosjekt/sykenaervaerstyper-i-norsk-arbeidsliv/) · [STAMI – Hva er sykenærvær og hvorfor er det viktig?](https://stami.no/hva-er-sykenaervaer-og-hvorfor-er-det-viktig/). Metode M04/M09.
7. **G5-07 [Lov/forskrift] – hjemmekontor:** At arbeid utføres utenfor kontoret gir ikke større adgang til aktivitetssporing. Fast hjemmekontor kan kreve skriftlig avtale, mens sporadisk arbeid ikke nødvendigvis omfattes av samme plikt. [Arbeidstilsynet – Forskrift om arbeid som utføres i arbeidstakers hjem, §§ 1–3](https://www.arbeidstilsynet.no/regelverk/forskrifter/hjemmekontorforskriften/) · [Arbeidstilsynet – Hjemmekontor: fast, sporadisk og kortvarig ordning](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/heimekontor) · [Datatilsynet – Overvåking av ansattes bruk av elektronisk utstyr; e-postforskriften § 2 andre ledd](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/overvaking-av-ansattes-bruk-av-elektronisk-utstyr/). Metode M04/M10.
8. **G5-08 [Lov/forskrift] – små grupper:** Ingen kilde dokumenterer en universell lovlig anonymitetsgrense på n=5 eller n=7. En gruppe på ti kan også være identifiserbar ved kombinasjon av opplysninger. Undertrykk gruppevisning ved uavklart identifiserbarhet; terskel er kun lokalt risiko-/analysevalg. [Datatilsynet – Personvernprinsippene; GDPR art. 5 og 6](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/) · [Datatilsynet – Personvern på arbeidsplassen, tilgangsbegrensning og lagring](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/). Metode M04/M10.
9. **G5-09 [Antakelse] – museum:** Ingen offentlig, sammenlignbar produktivitetsfordeling for 168 fiktive ansatte er hentet ut. Unngå nasjonal «museumscore»; bruk dokumenterte syntetiske oppdrag og kvalitetsmål. Metode M09.
10. **G5-10 [Lov/forskrift] – dataminimering:** Selv et syntetisk design kan oppmuntre til uhjemlet innhenting hvis skjemaet foreslår tastetrykk, nettbruk eller diagnoser. Derfor er slike felt uttrykkelig utelatt. [Datatilsynet – Overvåking av ansattes bruk av elektronisk utstyr; e-postforskriften § 2 andre ledd](https://www.datatilsynet.no/personvern-pa-ulike-omrader/personvern-pa-arbeidsplassen/overvaking-av-ansattes-bruk-av-elektronisk-utstyr/) · [Datatilsynet – Personvernprinsippene; GDPR art. 5 og 6](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/). Metode M10/M12.
11. **G5-11 [Antakelse] – automatiserte individbeslutninger:** Målt saksmengde sier ikke nødvendigvis noe om arbeidsinnsats, lønnsrett, kompetanse eller ansattes ansvar. Ingen automatisk oppfølging/reaksjon uten separat faglig og rettslig prosess. Metode M01/M12.
12. **G5-12 [Offisiell statistikk] – to ulike nevnerbegrep:** SSBs nasjonale bruttoprodukt per timeverk må ikke forveksles med antall museumsbesøk eller kommunale mottakere per ansatt. Ulik definisjon gir misvisende sammenligning. [SSB – Produktivitetsberegninger for næringer: bruttoprodukt per utført timeverk](https://www.ssb.no/nasjonalregnskap-og-konjunkturer/nasjonalregnskap/artikler/produktivitetsberegninger-for-naeringer) · [SSB – KOSTRA dokumentasjon: produktivitet/enhetskostnader med kvalitetsforbehold](https://www.ssb.no/offentlig-sektor/kostra/statistikk/kostra-kommune-stat-rapportering/om-kostra/dokumentasjon-av-kostra). Metode M01/M09.

**AP5 stoppunkt:** Fortsett ikke til AP6 før ny eksplisitt melding «neste».
