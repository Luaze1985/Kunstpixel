# Hva bør stå på en ledelsesside for et museum?

*Research 2026-11-16 for Datafinner etappe 2–4. Bredt nettsøk + lovtekst (Lovdata). Kilderegister nederst.*

## Kort svar

En leder trenger tre ting fra en side som Datafinner. Bransjekildene og lovverket peker samme vei:

1. **Hva skjer nå** (i dag / denne uka): besøk mot forventet, hvem er på jobb, hva er planlagt, hva har gått galt. [K09, K10, K13]
2. **Hva må jeg gjøre** (frister og plikter): lovpålagte oppfølginger med dato. Sykefravær har harde frister (4 og 7 uker), og avvik må lukkes. [K03, K04, K05]
3. **Hvordan går det** (måned/kvartal/år): de tallene museet uansett må rapportere til Kulturdirektoratet/SSB og tilskuddsgiver, så rapporten bygges gjennom året, ikke i mars. [K07, K08]

Det som **ikke** hører hjemme på forsiden: lesecaser, øvingsscenarier og ting man ikke kan handle på. De kan ligge under «Mer».

---

## 1. Funn: hva lover og forskrifter krever av lederen (fakta)

| Krav | Hva lederen må ha oversikt over | Kilde |
|---|---|---|
| Arbeidsmiljøloven § 3-1 | Mål for HMS, kartlegging og risikovurdering, rutiner for å avdekke og rette avvik, **systematisk arbeid med å forebygge og følge opp sykefravær**, og jevnlig gjennomgang av HMS-arbeidet. | K02 |
| Internkontrollforskriften § 5 | Skriftlig dokumentasjon av HMS-mål, ansvar, risikovurdering, avviksrutiner og jevnlig gjennomgang (punkt 4–8). | K01 |
| AML § 4-6 | **Oppfølgingsplan senest etter 4 uker** sykefravær. **Dialogmøte innen 7 uker** ved fullt fravær. | K03 |
| AML § 10-7 | Oversikt over hvor mye hver ansatt har arbeidet. Tilgjengelig for Arbeidstilsynet og tillitsvalgte. | K04 |
| Brannforebyggingsforskriften §§ 9–13 | Eier og bruker skal ha systematisk sikkerhetsarbeid, rutiner for evakuering og opplæring, og **dokumentere** at pliktene er oppfylt. Forskriften sier ikke eksplisitt «brannøvelse» med fast frekvens. | K05 |
| Museumsstatistikken (Kulturdirektoratet → SSB, via Altinn, frist om våren) | Besøk (totalt, betalende, voksne, barn og unge), årsverk, samlinger etter type, utstillinger (faste, midlertidige, vandre), inntekter og utgifter. Besøkskategoriene ble endret fra 2025. | K07, K06 |
| Tilskudd fra Kulturdepartementet | Kulturdirektoratet vurderer hvert år måloppnåelse mot føringer i tilskuddsbrevet og museets egne mål. Svakeste punkter i rapporteringen er målgruppearbeid og at teksten blir ren aktivitetsliste. | K08 |

**Tolkning:** «Det systematiske» betyr i praksis at lederen trenger lister med status og frist, ikke bare tall. Avvik, sykefraværsoppfølging og årlig gjennomgang er oppgaver, ikke rapporter.

## 2. Funn: bransjepraksis (sekundærkilder, tolkning)

- **Besøk er hovedtallet, men alene villedende.** McKinsey peker på at mange bare rapporterer totalt besøk. De foreslår å sammenligne besøk med medlemskap og inntekt, og påpeker at høyere besøk ikke alltid er bedre. [K10]
- **Faktisk mot forventet.** Art Institute of Chicago bruker en graf med faktisk besøk mot forventet, og markerer bare avvik som er statistisk signifikante. [K11, sannsynlig] Dette passer en daglig visning: «I dag: 312 besøk, normalt 280–340 for en tirsdag i november».
- **Koble besøk med kafé og butikk.** Bransjeråd er å se travle dager sammen med salg, for å finne inntektshull. [K12]
- **Definisjoner må være like.** Museer teller ulikt: skoleklasser, barn og oppsøkende tilbud. [K11] Kunstpixel bør bruke statistikkens definisjoner (voksne / barn og unge) fra start.
- **Vaktlogg og hendelseslogg.** Museer fører løpende vaktlogg med hendelser, førstehjelp og vedlikehold, slik at neste skift vet hva som har skjedd. [K13, leverandørkilde] Dette er grunnlaget for «hva skjedde i går».
- **Samlingsforvaltning:** offentlige revisjoner og standarder måler tilstandsvurdering, utlån og innlån (dokumentasjon, behandlingstid), klimamåling og beredskap. [K14, K15]

## 3. Forslag: innhold på Datafinner, sortert etter tidshorisont

Merket ✅ = data finnes i `museum.db` i dag. 🟡 = data finnes, men verktøy eller rapport mangler. ❌ = finnes ikke.

### I dag (forsiden etter Hjem, eller toppen av «Driften denne uka»)
| Innhold | Hvorfor | Data |
|---|---|---|
| Besøk i dag og i går mot normalt for ukedagen | Hovedtall, faktisk mot forventet [K10, K11] | ✅ `dagsbesok` |
| Hvem er på jobb, per stasjon | Drift. Viser også datafeilen med kafévakter | ✅ `hr_vakter` |
| Arrangementer i dag | Planlegging | ✅ `hendelser` |
| Nye og åpne driftsmeldinger (haster først) | «Hva har gått galt» [K13] | ✅ `driftsmeldinger_*` |
| Nye HMS-avvik | AML § 3-1 e [K02] | ✅ `avvik_hms_drift`, `hms_avvik_tekst` |

### Denne uka (etappe 2: «Driften denne uka»)
| Innhold | Data |
|---|---|
| Besøk per dag, denne uka mot forrige uke og samme uke i fjor | ✅ `dagsbesok` (stopp ved dagens dato) |
| Publikumstilfredshet (utstilling, kafé, service) og nye anmeldelser med lav score | ✅ `besok_tilfredshet`, `anmeldelser` |
| Kafésalg mot besøk (kroner per besøkende) | ✅ `kafe_varesalg` + `dagsbesok` [K12] |
| Hendelser og avvik lukket mot åpnet | ✅ |

### Mine frister (ny, etappe 3 sammen med «Mine oppfølginger»)
Dette er det som gjør siden til et verktøy og ikke bare en rapport. Hver rad får knappene Følg opp, E-postutkast og Spør KI.
| Frist | Regel | Data |
|---|---|---|
| Oppfølgingsplan forfaller (uke 4 i sykefravær) | AML § 4-6 [K03] | 🟡 `hr_fravaer` (fra/til per ansatt), mangler verktøy |
| Dialogmøte forfaller (uke 7) | AML § 4-6 [K03] | 🟡 samme |
| Åpne HMS-avvik eldre enn X dager | IK-forskr. § 5 nr. 7 [K01] | ✅ |
| Rapporter med frist neste 30 dager | Rapporteringskalenderen | ✅ `search_rapportering` (mangler datofilter) |
| Tilstandsrapporter som bør fornyes | Samlingsforvaltning [K14] | 🟡 `tilstandsrapporter`, ikke hvitelistet |
| Innlån som går ut eller mangler dokumentasjon | [K14] | 🟡 `utstillingsinnlan` |

### Måned, kvartal og år
| Innhold | Data |
|---|---|
| Sykefravær mot bransjen (SSB kultur) | ✅ `get_absence_report`, `ssb_sykefraver_kultur` |
| Arbeidstid per ansatt (AML § 10-7) | ✅ `get_working_hours_report` |
| Økonomi per utstilling: budsjett mot faktisk | ✅ `utstilling_okonomi` |
| **Museumsstatistikk-forhåndsvisning:** årets tall i samme oppsett som Kulturdirektoratets skjema (besøk voksne / barn og unge, betalende, utstillinger, økonomi) | ✅ delvis. Ingen tabell for årsverk og samlingstall per type [K07] |
| Årlig HMS-gjennomgang: mål, risiko, avvik og tiltak samlet | IK-forskr. § 5 nr. 8 [K01]. ✅ delvis |

## 4. Hva dette betyr for dagens Datafinner (råd)

- **Behold:** Rapporteringskalender, Myndighetskrav, Sykefravær, Arbeidstid, Økonomi per utstilling, Vaktplan. Alle har lovgrunnlag eller rapporteringsbehov.
- **Flytt ned eller skjul:** Arena-casene (inkludert Personvern/GDPR-casene). De er øvingsmateriale, ikke ledelsesinformasjon. Personvern hører hjemme som en egenskap på data («inneholder persondata»), ikke som egen rapport.
- **Legg til, i denne rekkefølgen:**
  1. **«I dag»-kortet** og **«Driften denne uka»** (etappe 2). Høyest verdi, data finnes.
  2. **«Mine frister»** med sykefraværsfristene (etappe 3). Lovpålagt, konkret, og det er her handlingsknappene gir mening.
  3. **Museumsstatistikk-forhåndsvisning** (etappe 4). Gjør årsrapporteringen til et biprodukt.
- **Forbehold:** alt er syntetiske data. Fristene i «Mine frister» blir demo, ikke juridisk oppfølging.

## 5. Fakta, tolkning og antakelse

- **Fakta:** lovkravene i tabell 1 (Lovdata), og variablene i museumsstatistikken (SSB).
- **Tolkning:** at lederen trenger «lister med frister» mer enn grafer. Det følger av ordlyden «rutiner for å avdekke, rette opp», men er vår lesning.
- **Antakelse:** at en kunstmuseumsdirektør i Norge har samme behov som internasjonale museer i bransjekildene. Kildene er stort sett amerikanske og britiske.
- **Ikke funnet:** gjeldende 2026-skjema for museumsstatistikken og frist i Altinn. Ingen kilde til fast frekvens for brannøvelser (forskriften krever rutiner og dokumentasjon, ikke frekvens).

## Kilderegister

| ID | Påstand / funn | Primærkilde og hjemmel | URL | Dokumentasjonsgrad | Hva kilden beviser vs. tolkning |
|:---|:---|:---|:---|:---|:---|
| K01 | Skriftlig dokumentasjon av HMS-mål, ansvar, risiko, avviksrutiner og jevnlig gjennomgang | Internkontrollforskriften § 5 | [lovdata.no/…/1996-12-06-1127](https://lovdata.no/dokument/SF/forskrift/1996-12-06-1127) | Godt dokumentert | Beviser kravet. At det bør vises som oppgaveliste er tolkning. |
| K02 | Arbeidsgiver skal blant annet sikre systematisk oppfølging av sykefravær og rutiner for avvik | Arbeidsmiljøloven § 3-1 annet ledd a–h | [lovdata.no/lov/2005-06-17-62/§3-1](https://lovdata.no/lov/2005-06-17-62/§3-1) | Godt dokumentert | Beviser kravet. |
| K03 | Oppfølgingsplan senest etter 4 uker, dialogmøte innen 7 uker ved fullt fravær | Arbeidsmiljøloven § 4-6 | [lovdata.no/lov/2005-06-17-62/§4-6](https://lovdata.no/lov/2005-06-17-62/§4-6) | Godt dokumentert | Beviser fristene. «Med mindre det er åpenbart unødvendig». |
| K04 | Oversikt over arbeidstid per ansatt | Arbeidsmiljøloven § 10-7 | [lovdata.no/lov/2005-06-17-62/§10-7](https://lovdata.no/lov/2005-06-17-62/§10-7) | Godt dokumentert | Beviser kravet. |
| K05 | Eier og bruker: systematisk sikkerhetsarbeid, rutiner for evakuering og opplæring, dokumentasjon. Ingen eksplisitt øvelsesfrekvens. | Forskrift om brannforebygging §§ 9–13 (FOR-2015-12-17-1710) | [lovdata.no/…/2015-12-17-1710](https://lovdata.no/dokument/SF/forskrift/2015-12-17-1710) | Godt dokumentert | At brannøvelse er vanlig praksis er sekundært (helseforetak, NHO-sjekkliste), ikke lovtekst. |
| K06 | Besøkskategoriene i statistikken ble endret 2024–2025 (voksne / barn og unge) | Kulturdirektoratet, revisjon av skjema | [kulturdirektoratet.no (dok.)](https://kulturdirektoratet.no/documents/10157/21fb1522-124a-475d-a82f-fe83af744e9d) | Sannsynlig | Fra søkesammendrag. Selve 2025/2026-skjemaet er ikke lest. |
| K07 | Museumsstatistikken måler besøk, årsverk, samlinger etter type, bygninger, utstillinger og økonomi. Innsamling via Altinn, frist om våren. | SSB, statistikken Museer | [ssb.no/…/museer](https://www.ssb.no/kultur-og-fritid/statistikker/museer) | Godt dokumentert | Variablene er fakta. Nøyaktig frist for 2026 er ikke funnet. |
| K08 | Måloppnåelse vurderes mot tilskuddsbrev og egne mål. Svakhet: målgrupper og ren aktivitetsrapportering. | Kulturrådet/Kulturdirektoratet, statusrapport om museene | [kulturdirektoratet.no (dok.)](https://kulturdirektoratet.no/documents/10157/99b044b0-41eb-4ae3-b658-e7bce57eb664) | Sannsynlig | Eldre dokument. Gjeldende tilskuddsbrev for et konkret museum er ikke lest. |
| K09 | Typiske KPI-er for museumsdirektør: besøk, billettinntekt, medlemsvekst, utstillingsvurdering | ClickUp, mal | [clickup.com/…/museum-directors](https://clickup.com/templates/kpi/museum-directors) | Usikkert / svakt dokumentert | Leverandørmal, ikke standard. Brukes bare som eksempel. |
| K10 | Mange rapporterer bare totalt besøk. Sammenlign med medlemskap og inntekt. Høyere besøk er ikke alltid bedre. | McKinsey, «The art of data» | [mckinsey.com](https://www.mckinsey.com/industries/social-sector/our-insights/the-art-of-data-empowering-art-institutions-with-data-and-analytics) | Sannsynlig | Fra søkesammendrag. Siden tidsavbrøt ved direkte lesing. |
| K11 | Art Institute of Chicago: graf med faktisk mot forventet besøk. Museer teller ulikt (skole, barn, oppsøkende). | Univ. of Hertfordshire, «Data Driven Museums» (2023) | [uhra.herts.ac.uk (PDF)](https://uhra.herts.ac.uk/id/eprint/12597/1/Data_Driven_Museums_2023_FINAL_1.pdf) | Sannsynlig | Fra søkesammendrag. PDF-teksten kunne ikke leses maskinelt. |
| K12 | Se travle dager sammen med mat- og butikksalg for å finne inntektshull | CLA, artikkel om dashboards for kulturinstitusjoner | [claconnect.com](https://godigital.claconnect.com/insights/article/arts-and-culture-organizations-use-dashboards-for-better-reporting/) | Usikkert / svakt dokumentert | Rådgiverartikkel. |
| K13 | Løpende vaktlogg med patruljer, hendelser og vedlikehold for neste skift. Hendelser dokumenteres i eget system. | msshift (leverandør), Winterthur (stillingsannonse) | [msshift.com/museums](https://msshift.com/museums) | Usikkert / svakt dokumentert | Viser praksis, ikke krav. |
| K14 | Revisjon av museumssamlinger: miljøkontroll, utlån (behandlingstid, tilstandsrapport), beredskap | Riksrevisjonen New Zealand (2006) | [oag.parliament.nz/2006/heritage](https://oag.parliament.nz/2006/heritage/appendix.htm) | Sannsynlig | Offentlig revisjon, men utenlandsk og eldre. |
| K15 | Benchmark for samlingsforvaltning på tre nivåer, blant annet miljøkontroll | Arts Council England, benchmarks | [obs-traffic.museum (PDF)](https://www.obs-traffic.museum/sites/default/files/ressources/files/Arts_Council_benchmarks_collection_care.pdf) | Sannsynlig | Britisk standard, ikke norsk krav. |
