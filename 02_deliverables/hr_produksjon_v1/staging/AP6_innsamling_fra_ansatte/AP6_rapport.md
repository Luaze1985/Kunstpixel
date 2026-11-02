# AP6 – innsamling fra ansatte

**Dato/kildekontroll:** 20.10.2026  
**Omfang:** Kun område 6 i originalbestillingen; ingen AP7-arbeid.  
**Kontekst:** Fiktivt museum med 168 ansatte, seks avdelinger, syntetisk SQLite-data og eksisterende personalhåndbok, vakt-, fraværs- og kompetansemodeller.  
**Metode:** M01 påstandsisolering, M04 kilde-/relevanstest, M09 aktualitetskontroll, M10 motbevis, M12 automatisk beslutningssperre.

## Sammendrag (maks 10 linjer)

1. **Kritisk:** «Anonym» kan ikke avgjøres ved en universell gruppestørrelse; koblings- og differanseangrep kan avsløre personer. [Lov/forskrift] [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-20](https://www.datatilsynet.no/globalassets/global/dokumenter-pdfer-skjema-ol/regelverk/veiledere/anonymisering-veileder-041115.pdf)
2. **Kritisk:** Anonyme varsler krever undersøkelse, men kan være vanskelige å opplyse; vern av varsler og kontradiksjon må balanseres. [Lov/forskrift] [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-11](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/slik-bor-arbeidsgiver-handtere-varsling/)
3. **Oppdatert 2026:** Nye forskriftspresiseringer om psykososial kartlegging trådte i kraft 01.01.2026. [Lov/forskrift] [K6-03](https://www.arbeidstilsynet.no/regelverk/forskrifter/forskrift-om-utforelse-av-arbeid/) · [K6-04](https://www.arbeidstilsynet.no/arbeidsmiljo/psykososialt-arbeidsmiljo)
4. **Lovkrav:** Minst fem jevnlig ansatte utløser plikt til skriftlige varslingsrutiner; små virksomheter kan også være omfattet. [Lov/forskrift] [K6-09](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/virksomheten-skal-ha-rutiner-for-intern-varsling/)
5. **Sektor:** Industri, service/kontor og kommune har samme hovedlovgivning, men varierer i risiko og undersøkelsesmetoder. [Bransjepraksis] [K6-13](https://www.arbeidstilsynet.no/arbeidsmiljo/vold-og-trusler/) · [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/)
6. **Testdesign:** Bare syntetiske data, aggregering, prosessmetadata og tjenstlig tilgang; varselsinnhold lagres separat. [Antakelse] [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38)
7. **Statistikk:** LKU-A 2022 oppgir 51 % svarandel i en representativ nasjonal undersøkelse – ikke som norm for interne pulsmålinger. [Offisiell statistikk] [K6-18](https://noa.stami.no/metode/datakilder/levekarsundersokelsen-om-arbeidsmiljo/)
8. **Ingen automatisk dom:** Faste kontroller markerer mangel eller sperrer publisering; de avgjør ikke om arbeidsgiver «har brutt loven». [Antakelse]

## A. Regler og kildegrunnlag

### A6-01. Kartlegging og ansattes medvirkning

- **[Lov/forskrift]** Arbeidsmiljøloven § 3-1, § 4-3 og internkontrollforskriften §§ 4–5 krever systematisk HMS-arbeid, kartlegging, risikovurdering, dokumenterte tiltak og medvirkning. Dette er **ikke** et generelt påbud om én årlig spørreundersøkelse. [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-02](https://www.arbeidstilsynet.no/regelverk/forskrifter/internkontrollforskriften)
- **[Lov/forskrift]** Fra **1. januar 2026** er forskrift om utførelse av arbeid, andre del kap. **1A** (psykososialt arbeidsmiljø) med § 1A-2 om kartlegging/risikovurdering og § 1A-3 om tiltak presisert. Nye kap. 2A/3A gjelder blant annet trakassering og vold/trusler. Arbeidstilsynet presiserer at endringene tydeliggjør allerede gjeldende arbeidsgiverplikter. **Ikke bland kapittel 2A i forskriften med kapittel 2 A om varsling i loven.** [K6-03](https://www.arbeidstilsynet.no/regelverk/forskrifter/forskrift-om-utforelse-av-arbeid/) · [K6-04](https://www.arbeidstilsynet.no/arbeidsmiljo/psykososialt-arbeidsmiljo)
- **[Myndighetsveiledning]** Arbeidstilsynet nevner arbeidsmiljøundersøkelser, vernerunder, avviksmeldinger og samtaler som **mulige kilder**, ikke obligatoriske spesifikke verktøy. [K6-04](https://www.arbeidstilsynet.no/arbeidsmiljo/psykososialt-arbeidsmiljo)

### A6-02. GDPR og innsamling

- **[Lov/forskrift]** Identifiserbare opplysninger krever et relevant behandlingsgrunnlag etter GDPR artikkel **6** og formålsbegrensning/dataminimering i artikkel **5**. Helseopplysninger og andre særlige kategorier krever i tillegg vurdering av artikkel **9**. Oppfyll også informasjons-/innsynsplikter etter artikkel **12–15**, tilgang og sikkerhet etter artikkel **32**, og artikkel **28** ved databehandler. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-07](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/)
- **[Lov/forskrift]** Samtykke er **ikke automatisk** egnet grunnlag i ansettelsesforhold på grunn av ubalansen mellom partene; det må være reelt frivillig. Om det brukes, må vilkårene faktisk være oppfylt. Nødvendighet for arbeidsgivers lovpålagte HMS-plikter kan peke mot andre grunnlag, men konkret hjemmels-/formålsvurdering kreves. For offentlig myndighetsutøvelse er art. 6(1)(f) ikke tillatt som grunnlag; det følger ikke at en kommunal arbeidsgiver aldri kan vurdere bokstav f i en annen kapasitet. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-22](https://lovdata.no/nav/lov/2018-06-15-38/kapii)
- **[Lov/forskrift]** Bruk av ekstern undersøkelsesplattform krever konkret rolleavklaring; dersom leverandør er databehandler, kreves databehandleravtale (artikkel 28). Personvernkonsekvensvurdering (DPIA, artikkel 35) kreves ved sannsynlig høy risiko, ikke generelt for alle undersøkelser. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-08](https://www.datatilsynet.no/rettigheter-og-plikter/virksomhetenes-plikter/vurdering-av-personvernkonsekvenser/)
- **[Myndighetsveiledning]** Pseudonyme respondent-ID-er er fortsatt personopplysninger hvis noen med rimelighet kan koble dem til personer. Et minimumsantall i en rapport er **ikke bevis** for faktisk anonymitet. [K6-20](https://www.datatilsynet.no/globalassets/global/dokumenter-pdfer-skjema-ol/regelverk/veiledere/anonymisering-veileder-041115.pdf) · [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38)

### A6-03. Avvik, vold og varsling

- **[Lov/forskrift]** Internkontrollforskriften § 5 nr. 7 krever dokumenterte rutiner for å avdekke, rette opp og forebygge overtredelser. Arbeidstilsynet anbefaler å registrere nestenulykker. Registre over arbeidsrelatert skade/sykdom har særskilte krav, og alvorlige hendelser kan utløse egen meldeplikt. Dette er forskjellig fra «alt er varsling». [K6-02](https://www.arbeidstilsynet.no/regelverk/forskrifter/internkontrollforskriften) · [K6-12](https://www.arbeidstilsynet.no/hms/avvik-og-avvikshandtering/) · [K6-21](https://www.arbeidstilsynet.no/hms/roller-i-hms-arbeidet/arbeidsgiver/registrere-skader-og-sykdom/)
- **[Lov/forskrift]** Arbeidsmiljøloven kapittel **2 A**, særlig § 2 A-1 (kritikkverdige forhold), § 2 A-3 (tilstrekkelig undersøkelse innen rimelig tid), § 2 A-4 (forbud mot gjengjeldelse) og § 2 A-6 (skriftlige rutiner ved jevnlig minst **5** arbeidstakere, også færre ved behov). Ytring kun om eget arbeidsforhold er ikke automatisk varsling med vern etter dette kapitlet. [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-09](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/virksomheten-skal-ha-rutiner-for-intern-varsling/)
- **[Myndighetsveiledning]** Også **anonyme** varsler må håndteres. Internt varslingsmottak må ikke love absolutt anonymitet eller innsynsfrihet; § 2 A-7 om særskilt taushetsplikt gjelder varsling til ekstern offentlig tilsynsmyndighet eller annen offentlig myndighet. Innsyn/partsrettigheter må vurderes konkret for den interne varslingssaken. [K6-10](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/ansvar-rettigheter-og-roller/) · [K6-11](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/slik-bor-arbeidsgiver-handtere-varsling/) · [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/)

### A6-04. Samtaler, pulsmåling og kompetanse

- **[Lov/forskrift]** Referater fra medarbeidersamtaler som kan knyttes til en ansatt er personopplysninger; formål, tilgang, innsyn, retting og sletting/lagring må vurderes. Arbeidsmiljøloven pålegger ikke generelt et bestemt antall medarbeidersamtaler per år. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/)
- **[Bransjepraksis]** KS **10-FAKTOR** bruker svarskala 1–5 og sikter mot organisasjonsutvikling. STAMI **MUST** er laget for statlig tariffområde og har en **37-spørsmåls kjerne** med valgfrie moduler i nyere versjoner. Disse er **ikke** lovhjemmel for lokal innsamling og har **ikke** direkte sammenlignbar skala eller rapporteringsavtale. [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/) · [K6-16](https://stami.no/vare-tjenester/medarbeiderundersokelsen-i-staten-must/temaomrader-i-must/)
- **[Bransjepraksis]** STAMIs offentlig tilgjengelige **MUST-vilkår versjon 15.01.2024**: under **6 svar** = ingen rapport, **6–9** = bare gjennomsnitt, minst **10** = også fordelinger; enkelte sensitive temaer bare virksomhetsnivå og restriksjoner selv ved n≥10. Dette er et **verktøyeksempel**, ikke en norsk rettslig anonymitetsgrense. Gjeldende avtaleversjon må sjekkes ved bruk. [K6-17](https://static.stami.no/files/MUST/NO_MUST_Vilkaar_150124.pdf)

## B. Forskjeller mellom sektorer

| Tema | Industri | Privat service/kontor | Kommune |
|:--|:--|:--|:--|
| Relevante risikoområder | [Bransjepraksis] Maskinsikkerhet, kjemi, skift, nestenulykker; forhold avhenger av konkret drift | [Bransjepraksis] Kundekontakt, tidspress, hjemmekontor, organisatorisk arbeidsmiljø | [Bransjepraksis] Tjenestekvalitet, vold/trusler, emosjonelle krav og tidspress i aktuelle enheter |
| Undersøkelse | [Bransjepraksis] Lokalt arbeidsmiljø-/sikkerhetsskjema | [Bransjepraksis] Lokal puls-/medarbeiderundersøkelse | [Bransjepraksis] For eksempel KS 10-FAKTOR; ikke pålagt metode |
| Varsling/HMS | [Lov/forskrift] Samme AML/IK-regler | [Lov/forskrift] Samme AML/IK-regler | [Lov/forskrift] Samme AML/IK-regler + arkiv/offentlighet må vurderes konkret |
| Datagrunnlag | [Antakelse] Skifte- og maskinavvik på teamnivå | [Antakelse] Teamresultater uten digitale aktivitetslogger | [Antakelse] Gruppeaggregater med særskilt smågrupperisiko |
| Behandlingsgrunnlag | [Lov/forskrift] Per formål og behandling | [Lov/forskrift] Per formål og behandling | [Lov/forskrift] Per formål og behandling; myndighetsutøvelse setter egen grense for art. 6(1)(f) |

[Myndighetsveiledning] Støttekilder: [K6-03](https://www.arbeidstilsynet.no/regelverk/forskrifter/forskrift-om-utforelse-av-arbeid/) · [K6-13](https://www.arbeidstilsynet.no/arbeidsmiljo/vold-og-trusler/) · [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/) · [K6-22](https://lovdata.no/nav/lov/2018-06-15-38/kapii).

## C. Ti fasitspørsmål

Alle ti spørsmål er registrert med fulltekst, sektor, svar, kilde og vanskelig-flag i `AP6_fasit_sporsmal.csv`.

| ID | Tema | Vanskelig? | Kilde |
|:--|:--|:--|:--|
| Q-6-01 | Er det lov å gjennomføre en anonym medarbeiderundersøkelse uten at ansatte samtykker til alt? | ja | [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) |
| Q-6-02 | Kan leder se enkeltansattes svar i en pulsmåling fordi det er lederens avdeling? | ja | [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) |
| Q-6-03 | Gjelder en fempersonsgrense for anonymitet i alle undersøkelser? | ja | [K6-20](https://www.datatilsynet.no/globalassets/global/dokumenter-pdfer-skjema-ol/regelverk/veiledere/anonymisering-veileder-041115.pdf) |
| Q-6-04 | Må arbeidsgiver registrere nestenulykker, selv når ingen ble skadet? | nei | [K6-12](https://www.arbeidstilsynet.no/hms/avvik-og-avvikshandtering/) |
| Q-6-05 | Har alle bedrifter plikt til skriftlige varslingsrutiner? | nei | [K6-09](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/virksomheten-skal-ha-rutiner-for-intern-varsling/) |
| Q-6-06 | Kan en ansatt varsle anonymt, og må arbeidsgiveren undersøke? | ja | [K6-11](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/slik-bor-arbeidsgiver-handtere-varsling/) |
| Q-6-07 | Er varslers identitet alltid taushetsbelagt når vedkommende varsler til egen kommune som arbeidsgiver? | ja | [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) |
| Q-6-08 | Kan jeg be om innsyn i notatene fra min medarbeidersamtale? | ja | [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) |
| Q-6-09 | Er 10-FAKTOR et krav i arbeidsmiljøloven? | ja | [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/) |
| Q-6-10 | Kan kompetansekartlegging brukes til en automatisk liste over svake ansatte? | ja | [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) |

**Fasitprinsipp:** Ikke svar «ja/nei» på systeminnføring, anonymitet eller innsyn uten sektor, konkret formål, systemversjon og faktisk mottakerrolle. Ikke bruk fritekst fra varslingssak i søketester.

## D. Realistiske tall, fordelinger og kildespor

- **[Offisiell statistikk]** LKU-A 2022: omtrent **35 000** trukket i utvalget, om lag **51 %** svarprosent. Dette er en nasjonal, representativ kartlegging med endret metode i 2022, **ikke** forventet svarprosent for museets pulsmåling. Kilde: STAMI NOA LKU-A, 2022. [K6-18](https://noa.stami.no/metode/datakilder/levekarsundersokelsen-om-arbeidsmiljo/)
- **[Bransjepraksis]** KS 10-FAKTOR: **1–5 svarskala**. Dette gir gyldig verdiområde i syntetisk skjema for *dette* instrumentet, ikke en empirisk sannsynlighetsfordeling for ansatte. Publisert KS 2020. [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/)
- **[Bransjepraksis]** MUST-vilkår **n<6**, **6–9**, **n≥10** bestemmer detaljnivå i STAMIs konkrete rapporteringssystem. Tallene er **tekniske rapporteringsregler, ikke svarfrekvenser** og ikke nasjonale anonymitetsgrenser. Vilkårsversjon 15.01.2024; må oppdateres ved reell avtale. [K6-17](https://static.stami.no/files/MUST/NO_MUST_Vilkaar_150124.pdf)
- **[Offisiell statistikk]** STAMI NOA har nærings- og yrkesfordelte LKU-A-indikatorer, eksempelvis jobbkontroll. Uten definert næring/yrke, uttrekk og metode/år finnes det **ingen pålitelig museumsfordeling** å importere. Skal ikke konstrueres. [K6-19](https://noa.stami.no/arbeidsmiljofaktorer/krav-kontroll-og-belonning/jobbkontroll/)
- **[Antakelse]** For museet (168 ansatte/seks avdelinger) skal syntetisk antall inviterte komme fra eksisterende fiktiv bemanningsliste. Svarantall skal holde seg mellom 0 og inviterte. Velg ikke automatisk 51 % fra LKU-A; det ville være en feilaktig overføring fra en annen undersøkelse og populasjon.
- **[Antakelse]** Avviks-, varslings- og medarbeidersamtalerater er **ikke funnet som sammenlignbare nasjonale fordelinger** for denne casen. Bruk scenarioetiketter/parameter som må oppgis eksplisitt, ikke oppdiktede prosenter.

## E. Forslag til syntetiske data

Det følger **8 maskinlesbare tabellforslag** i `AP6_datasett_forslag.yaml`, med kolonner, datatyper, tillatte verdier, kilder og referanser til ansatt/avdeling/eksisterende kompetanse. Hovedgrep:

1. En katalog over innsamlingsformål, ansvar, grunnlag, tilgang og DPIA.
2. Én adskilt aggregattabell for offentliggjørbare/ledelsesrettede gruppetall. Ingen individuelle svar lagres her.
3. Tiltak fra medarbeidersamtaler, med medarbeider-ID bare der formål krever det.
4. Strukturerte HMS-avvik uten sensitive navn, diagnoser og fritekst.
5. En **separat varslingsprosess** med saksstatus og autorisert rolle; ingen kobling til individuell prestasjon.
6. Dokumenterte kompetansekrav og sertifikatstatus, uten automatisk personrangering.
7. Proveniens/kildeversjon, så rapportutlevering kan spores.

**[Antakelse]** Eksisterende faktiske SQLite-tabellnavn er ikke tilgjengelige; `hr_ansatte` / `hr_avdelinger` / `hr_sertifikater` er **logiske referanser** som må avstemmes før implementering. Ingen reelle eller syntetiske identifiserbare medarbeidersvar, varseltekster eller helsedata er generert.

## F. Faste regler og fallback

**20 kontrollregler**, pluss **10 individuelle fallback-regler** (`operator = fallback`), er levert i `AP6_regler_forslag.csv`.

Kritiske regler:

- `R-6-01`: Manglende artikkel 6-grunnlag → ikke start persondatainnsamling.
- `R-6-03`: Særlig kategori uten relevant artikkel 9-unntak → blokkert.
- `R-6-06` og `R-6-11`: Rapport uten vellykket identifiseringskontroll, eller med høy/uklar risiko → ikke publiser.
- `R-6-07` til `R-6-09`: Leverandørstyrt minimum for rapport og fordeling med eksplisitt versjon. STAMI MUST (n=6/10) er bare **illustrasjon**, ikke gyldig standard for kommune eller museum.
- `R-6-10`: Ukjent lokal verktøyregel → sperr aggregering fremfor å gjette.
- `R-6-12`: Sekundærbruk av survey til personalrangering → ingen automatisk bruk.
- `R-6-14`: Jevnlig minst fem arbeidstakere → sjekk skriftlige varslingsrutiner.
- `R-6-16`: Varslingssak i generell HR-KPI → sperr kobling.
- `R-6-20`: Identifisert psykososial risiko uten risikovurdering → oppgave til HMS, ikke automatisk lovbruddsdom.

Alle maskinreglene er **forslag**, ikke implementert kode. Sammensatte operatorer som `requires`, `between` og `true_and_art9_unntak_mangler` krever deterministisk definisjon og test før de kan kjøres. `R-6-07..09` krever dokumenterte, konfigurerbare terskler og korrekt gjeldende verktøyversjon. MUST er statlig instrument, og MUST-eksemplets 6/10-grenser skal **ikke kopieres** som standard i museum eller kommune.

## G. Grensetilfeller og usikkerhet (djevelens advokat)

1. **[Lov/forskrift] G6-01 – terskel vs anonymitet.** Selv 10 svar kan i noen grupper identifiseres ved rolle eller differansen mellom to delrapporter; k=5/k=6 er ikke en universell rettsregel. **Status:** Godt dokumentert. **Sikkerhet:** Høy. Metode M04/M10. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-20](https://www.datatilsynet.no/globalassets/global/dokumenter-pdfer-skjema-ol/regelverk/veiledere/anonymisering-veileder-041115.pdf)
2. **[Bransjepraksis] G6-02 – KS vs STAMI.** 10-FAKTOR og MUST har ulike målgrupper og leverandørregler. MUST-vilkår 2024 kan være erstattet; innstillingen må versjonsstyres og kontrolleres på ny. **Status:** Sannsynlig. **Sikkerhet:** Middels. Metode M09. [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/) · [K6-17](https://static.stami.no/files/MUST/NO_MUST_Vilkaar_150124.pdf)
3. **[Lov/forskrift] G6-03 – samtykkefellen.** «Anonym og frivillig» er ikke bevis for lovlig innsamling: hvem som kan se raw-svar og gjenbruke data, og om behandling faktisk er nødvendig, må prøves selvstendig. **Status:** Godt dokumentert. **Sikkerhet:** Høy. Metode M04. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38)
4. **[Lov/forskrift] G6-04 – intern varsling.** Arbeidsgiver har ikke samme uttrykkelige taushetspliktsregel for en intern varslingskanal som offentlig tilsynsmyndighet ved ekstern varsling; samtidig må varsleren beskyttes, og berørte personer kan ha rettigheter til opplysninger. Ikke lov absolutt hemmelighold. **Status:** Godt dokumentert hovedskille; konkret innsyn uavklart. **Sikkerhet:** Middels. Metode M01/M10. [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-10](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/ansvar-rettigheter-og-roller/)
5. **[Lov/forskrift] G6-05 – avvik vs varsel.** Nestenulykke uten kritikkverdig forhold kan være ordinært HMS-avvik, mens alvorlige kritikkverdige forhold kan være varsling. Kategorien avgjøres av innhold og forhold, ikke bare hvilken knapp arbeidstaker brukte. **Status:** Godt dokumentert. **Sikkerhet:** Høy. Metode M01. [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-12](https://www.arbeidstilsynet.no/hms/avvik-og-avvikshandtering/)
6. **[Lov/forskrift] G6-06 – 2026-forskriften.** Nye presiseringer innebærer ikke plikt til 10-FAKTOR, MUST eller fast spørsmålsliste. Arbeidsgiver må faktisk kartlegge relevante risikoer. **Status:** Godt dokumentert. **Sikkerhet:** Høy. Metode M09. [K6-03](https://www.arbeidstilsynet.no/regelverk/forskrifter/forskrift-om-utforelse-av-arbeid/) · [K6-04](https://www.arbeidstilsynet.no/arbeidsmiljo/psykososialt-arbeidsmiljo)
7. **[Antakelse] G6-07 – pulsdata og sanksjon.** Svak score fra seks respondenter er ikke årsaksbevis mot en leder eller representativt individbevis. Nye formål, skjevhet og lav svarprosent må kontrolleres. **Status:** Sannsynlig. **Sikkerhet:** Middels. Metode M01/M10.
8. **[Lov/forskrift] G6-08 – helseinformasjon.** Et åpent kommentarfelt kan uforutsett inneholde diagnoser, medlemskap, anklager eller opplysninger om elever/brukere. Fritekst kan ikke behandles som ufarlige aggregater. **Status:** Godt dokumentert. **Sikkerhet:** Høy. Metode M04. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-13](https://www.arbeidstilsynet.no/arbeidsmiljo/vold-og-trusler/)
9. **[Lov/forskrift] G6-09 – offentlig vs privat.** Kommunale dokumenter kan kreve separat vurdering av arkiv, innsyn og taushetsplikt; ikke behandle alle interne ledersvar som offentlig, men heller ikke anta automatisk hemmelighold. **Status:** Usikkert uten konkret sak. **Sikkerhet:** Middels. Metode M04/M10. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38)
10. **[Antakelse] G6-10 – opplæringskrav.** Sertifikater kan være lovpålagt, frivillig eller arbeidsgiverdefinert. «Utløpt» gir grunnlag for kontroll, men ikke automatisk konklusjon om udugelighet eller oppsigelse. **Status:** Sannsynlig. **Sikkerhet:** Middels. Metode M01. [K6-02](https://www.arbeidstilsynet.no/regelverk/forskrifter/internkontrollforskriften)
11. **[Offisiell statistikk] G6-11 – fordelingsoverføring.** Nasjonal LKU-A svarprosent 51 % i 2022 kan ikke begrunne intern pulsmåling med 51 % eller sannsynligheter per avdeling. **Status:** Godt dokumentert som statistisk avgrensning. **Sikkerhet:** Høy. Metode M04/M09. [K6-18](https://noa.stami.no/metode/datakilder/levekarsundersokelsen-om-arbeidsmiljo/)
12. **[Lov/forskrift] G6-12 – automatisering.** Systemet må ha menneskelig gjennomgang ved risiko for personidentifisering, personalsak, sanksjon, varslingssak, helsespor eller usikkerhet om formål. **Status:** Sannsynlig som designkrav, konkret lovhjemmel per tilfelle. **Sikkerhet:** Middels. Metode M10/M12. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-08](https://www.datatilsynet.no/rettigheter-og-plikter/virksomhetenes-plikter/vurdering-av-personvernkonsekvenser/)

**AP6 stoppunkt:** Kilde- og strukturkontroll gjennomført. AP7 (likelønn og redegjørelse) **ikke startet**. Vent på nytt eksplisitt «neste».
