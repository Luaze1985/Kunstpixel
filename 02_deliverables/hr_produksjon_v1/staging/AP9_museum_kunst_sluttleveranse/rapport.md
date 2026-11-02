# Sluttrapport – HR og arbeidsliv for fiktivt kunstmuseum (AP9)

**Sammenstilt:** 20.10.2026. **Caset:** 168 syntetiske ansatte, seks avdelinger, 54 994 syntetiske vakter 2010–2026, 27 personalhåndbokoppslag og lokal SQLite-modell, slik de er oppgitt i forskningsbestillingen. **Ingen faktiske ansatte eller kunstobjekter er lastet inn.**

## Sammendrag (maks 10 linjer)

1. Øvingsmuseet er hovedcase; industri, privat service og kommune beholdes som sammenligningssektorer.
2. Virke HUK – museer og andre kulturinstitusjoner (2026–2028) er relevant museumsavtale, men faktisk binding må dokumenteres.
3. Generelle Virke–HK-varehandelssatser må ikke brukes som museets lønnssatser.
4. Kveld, natt, helg, vernissage og utstillingsomrigg krever særskilt arbeidstid-/tariffvurdering.
5. Publikumsdrift, kunsthåndtering, konservering, magasin og formidling er ulike arbeidsprosesser.
6. Besøkstall og samlingsarbeid er virksomhetsmål; de må ikke ukritisk bli individuelle prestasjonspoeng.
7. Kunstnere, eksterne teknikere og frivillige krever egen rolle-, sikkerhets- og avtaleklassifisering.
8. Små kunstfaglige miljøer øker identifiseringsrisikoen i ansattundersøkelser og lønnskartlegging.
9. AP2–AP8 er samlet fra faktiske lokale leveranser; original AP0/AP1 ble ikke funnet. Område 1 er derfor rekonstruert og merket.
10. Alle data- og regeltillegg er forslag til syntetisk øvingsbruk, ikke automatisk rettsanvendelse.

## Grunnlag og kildekritisk avgrensning

**[Antakelse]** 168 ansatte, seks avdelinger, 54 994 vakter og 27 oppslag er brukerdefinerte syntetiske scenarioforhold. De er **ikke dokumentert som museumsstatistikk** og gir ikke grunnlag for fordelingsprosenter, tariffplikt eller lovlighet.

**[Tariffavtale]** Virke-oversikten omtaler museums-/kulturoverenskomsten; HUK-vilkår, gruppe og lokale lønnsplaner må knyttes til faktisk juridisk arbeidsgiver. Satsene i generelle AP2-eksempler for Virke–HK er bare sammenligningsgrunnlag.

**[Offisiell statistikk]** Kulturdirektoratets 2024-statistikk (publisert 2025) gjelder det nasjonale museumsnettverket og er ikke en tilfeldig eller representativ fordeling av HR-data for dette øvingsmuseet.

**[Antakelse]** De seks avdelingenes navn, eksakte SQLite-feltnavn og tariffbinding foreligger ikke. Nye funksjonskategorier er kun eksempler og krever manuell kobling.

---

## Område 1 – Personalhåndbok for museum og kunst

### A. Regler og kildegrunnlag

[Bransjepraksis] Del personalhåndboken i tydelige innganger for publikumsverter/billett, formidling, kuratorer/registrarer, konservering, utstillingsteknikk, sikkerhet/drift og administrasjon. Dette er **rolleeksempler**, ikke dokumentasjon av de seks eksisterende avdelingene. [Kulturdirektoratet](https://www.kulturdirektoratet.no/fag/museum-og-kulturarv/museumsutvikling/samlingsforvaltning) beskriver samlingsforvaltning som innsamling, bevaring, dokumentasjon, registrering og tilgjengeliggjøring.

[Tariffavtale] Personalhåndboken må slå opp arbeidsavtale **og konkret tariffbinding**. Virkes HUK-overenskomst for museer er ikke det samme som Virke–HKs varehandelsoverenskomst. [Virke](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/landsoverenskomst-for-museer-og-andre-kulturinstitusjoner/).

[Bransjepraksis] Lag egne FAQ-emner for utstillingsåpninger, helgevakter, omrigg og kunsthåndtering, tilstandskontroll, publikumsulykker, museumsbutikk, fotografi og rettighetsklarering. Slike rutiner er ikke generelle lovpålagte HR-frister. [Kulturdirektoratet](https://www.kulturdirektoratet.no/fag/museum-og-kulturarv/museumsutvikling/samlingsforvaltning), [Kopinor](https://kopinor.no/om-opphavsrett/).

[Myndighetsveiledning] Frivillige og eksterne kunstnere kan være til stede på samme arena som ansatte, men arbeidsrettslig status og arrangørens sikkerhetsansvar må vurderes separat. [Arbeidstilsynet](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/frivillig-arbeid/).

[Lov/forskrift] Skriftlig arbeidsavtale, HMS og arbeidstidskrav gjelder etter arbeidsmiljøloven også når arbeid skjer i utstillingsrom, magasin eller publikumsarealer. [Arbeidstilsynet](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).

### B. Industri, privat, kommune og kunstmuseum

- Industri: skift, maskin/HMS, yrkes- og tariffspesifikke rutiner.
- Privat service/kontor: kunde-/publikumsdrift, avtalevilkår og interne ordninger.
- Kommune: KS/kommunale rutiner, offentlig styring, lokal medbestemmelse.
- **Kunstmuseum:** publikum + arrangement, kuratering, samlings-/kunstforvaltning, konservering, utstillingsmontasje og eksterne aktører; faktisk eierform og tariffbinding må verifiseres.

### C. Ti fasitspørsmål

Spørsmål **Q-1-01–Q-1-10** er rekonstruert i sluttfilen, ikke gjenfunnet som original AP1-leveranse. De omfatter museumsvakter, museets tariff, håndtering av verk, avvik, frivillige og rettigheter.

### D. Statistikk og fordelinger

[Offisiell statistikk] Kulturdirektoratets **2024-tall, utgitt 2025**, dekker 61 museer i det nasjonale museumsnettverket. Kan belyse aktivitet, årsverk og besøk; er **ikke** representativ mikrofordeling for museets HR-ansatte. [Kulturdirektoratet](https://www.kulturdirektoratet.no/publikasjoner/det-nasjonale-museumsnettverket-i-2024).

### E. Syntetiske datatabeller

`museum_handbok_rolletema` refererer eksisterende 27 personalhåndbokoppslag, uten å endre originaldatabasen. Virkelige avdelingsnavn og oppslags-ID må mappes før import.

### F. Faste regler og fallback

Ingen nye automatiske juridiske utfall for område 1. 10 fallback-rader **R-1-01–R-1-10** varsler ved manglende tariff, rolle eller lokal prosedyre.

### G. Grensetilfeller og usikkerhet

[Antakelse] Museets juridiske organisasjonsform, de faktiske navnene på seks avdelinger, lokal HMS-rutine og tariffparter er **ikke funnet** i tilgjengelig dokumentasjon. Rekonstruert AP1 kan derfor ikke likestilles med original, utestående AP1-forskning.


## Område 2 – Museumsavtale og kunstfaglige lønnsgrupper

### Museum og kunst – anvendelse i øvingscaset

[Tariffavtale] **Kritisk korreksjon til AP2s generelle Virke-eksempel:** lønnstrinnene fra Virke–HK varehandel må **ikke overføres** til museumsansatte. For museumscaset skal standardprofilen være *Virke HUK – Landsoverenskomst for museer og andre kulturinstitusjoner 2026–2028*, men bindende avtale per ansatt/gruppe er fortsatt uavklart. [Virke](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/landsoverenskomst-for-museer-og-andre-kulturinstitusjoner/), [Fagforbundet](https://www.fagforbundet.no/lonn-og-avtaler/virke/museer-og-andre-kulturinstitusjoner/).

[Tariffavtale] Virkes veileder for lokale HUK-forhandlinger skiller faste/variable tillegg fra overtid i museumsavtalens beregningsgrunnlag. Lokal lønnsdannelse og innplassering kan ikke erstattes av ett automatisk handelstrinn. [Virke](https://www.virke.no/tariff-og-lonn/huk-omradet/veileder-lokale-forhandlinger-huk-avtalene/forberedelser/).

[Antakelse] Relevante syntetiske lønnsgrupper kan være konservator, samlingsregistrar, kurator, formidler, vert/billett og utstillingstekniker. Ikke tildel lønnstrinn eller satser før gyldig tarifftekst, lokal lønnsplan og kontrakt er knyttet til gruppen.

### Opprinnelig sektorsammenligning og A–G (AP2, bevart)

#### AP2 – Lønn og lønnsarter, område 2

**Kontrolldato:** 20.10.2026. **Omfang:** generelt faktagrunnlag for syntetiske HR-data og kunnskapsbase, med sektorer industri, privat service/kontor og kommune. **Status:** AP2 selvstendig leveranse; tidligere AP0/AP1-artefakter er ikke endret. Dette er ikke individuell juridisk rådgivning.

#### Sammendrag (maks 10 linjer)

1. [Lov/forskrift] Det finnes ingen generell lovfestet minstelønn for alle norske yrker; enkelte bransjer har allmenngjorte minstelønnssatser. Kilde: [lonn](https://www.arbeidstilsynet.no/lonn-og-ansettelse/lonn/).
2. [Lov/forskrift] Lovens overtidstillegg er minst **40 %**, men rett til overtid må skilles fra merarbeid og tariffmessig overtid. Kilde: [overtid](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/).
3. [Tariffavtale] **KS har nye helge-/kvelds-/nattsatser fra 01.10.2026**, ikke fra 01.05.2026; avtalens virkeområde og type vakt må sjekkes. Kilde: [kstillegg](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/endringer-i-tilleggene-i-hta-kapittel-1--5-fra-forste-oktober/).
4. [Tariffavtale] Virke–HKs Landsoverenskomst har lønnstrinn og satser per 01.04.2026, men dekker ikke alle private virksomheter. Kilde: [virke](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/landsoverenskomsten-hk/).
5. [Tariffavtale] Industrioverenskomsten har flere avtaledeler, og NHO- og Virke-versjonene må holdes adskilt. Kilder: [industri](https://www.fellesforbundet.no/lonn-og-tariff/tariffavtaler/industrioverenskomst/), [verkstedvirke](https://www.fellesforbundet.no/lonn-og-tariff/lonnsoppgjorene/hovedoppgjoret-2026/uravstemming/industrioverenskomsten-virke/).
6. [Lov/forskrift] Feriepenger er som hovedregel minst **10,2 %** (tariff ofte 12 %); arbeidstakere over 60 år har særregler. Kilde: [ferie](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/ferie/feriepenger/).
7. [Myndighetsveiledning] Normal arbeidsgiverperiode for sykepenger er inntil **16 kalenderdager**; NAVs sykepengegrunnlag er normalt begrenset til 6 G. Kilder: [nav](https://www.nav.no/arbeidsgiver/sykepenger-i-arbeidsgiverperioden), [nav6g](https://www.nav.no/sykepenger).
8. [Lov/forskrift] Arbeidsgiveravgiften i 2026 varierer mellom soner; ordinær sone I er **14,1 %**, sone V **0 %**. Kilde: [aga](https://www.skatteetaten.no/satser/arbeidsgiveravgift/?year=2026).
9. [Myndighetsveiledning] Fra 2026 betales forskuddstrekk direkte, normalt senest første virkedag etter utbetaling; a-melding har normalt frist den 5. Kilder: [skatt2026](https://www.skatteetaten.no/bedrift-og-organisasjon/arbeidsgiver/skattekort-og-skattetrekk/skattetrekkskonto/), [frister](https://www.skatteetaten.no/skjema/direkte-levering-av-a-meldingen/).

#### A. Regler og kildegrunnlag

**A1. Lønn, lønnsslipp og trekk**

- [Lov/forskrift] Lønn avtales i arbeidsavtalen. Arbeidsmiljøloven §§ 14-6 og 14-15 stiller krav til opplysninger om lønn, betaling, lønnsslipp ved utbetaling og begrensninger for trekk i lønn/feriepenger. En intern lønnskode kan ikke i seg selv gi grunnlag for trekk. Kilde: [aml](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- [Myndighetsveiledning] Vanlig lønnsslipp skal skille lønnselementer, bruttobeløp, fradrag/forskuddstrekk og nettoutbetaling. Betalingsmåte/tid skal følge avtalt ordning. Kilde: [lonn](https://www.arbeidstilsynet.no/lonn-og-ansettelse/lonn/).
- [Lov/forskrift] Arbeidsmiljøloven § 10-6 (11) fastsetter minst 40 % tillegg ved overtid; loven åpner for skriftlig avtale om å ta ut overtidstimer som fritid, men overtidstillegget må utbetales. Kilde: [overtid](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/).
- [Myndighetsveiledning] Det finnes ikke noe universelt lovpålagt tillegg for ordinært kveld-, natt- og helgearbeid; tillegg må sjekkes i relevant tariff, avtale eller særregel. Arbeid 1. og 17. mai følger særskilt lov § 3, med minst 50 % dersom tillegget ikke er fastsatt ved avtale/regulativ. Kilder: [lonn](https://www.arbeidstilsynet.no/lonn-og-ansettelse/lonn/), [hellig](https://www.arbeidstilsynet.no/regelverk/lover/lov-om-1-og-17-mai//).

**A2. Tariff – versjoner og gyldighet**

- [Tariffavtale] **Industri/NHO–Fellesforbundet:** Industrioverenskomsten **2026–2028** finnes hos Fellesforbundet. Avtalen har ulike deler og lokale bestemmelser. Ingen samlet skiftsats eller generell minstelønn kan tas fra én avtaledel og brukes på hele industrien. Kilde: [industri](https://www.fellesforbundet.no/lonn-og-tariff/tariffavtaler/industrioverenskomst/).
- [Tariffavtale] **Industri/Virke–Fellesforbundet:** Separat Virke-variant; for verkstedoverenskomst-delen (VO) oppgis minste timefortjeneste fra **01.04.2026** til bl.a. fagarbeider **232,55 kr**, spesialarbeider **221,95 kr**, hjelpearbeider **211,49 kr**. *Dette er et konkret avtaleeksempel, ikke nasjonal industriminstelønn.* Kilde: [verkstedvirke](https://www.fellesforbundet.no/lonn-og-tariff/lonnsoppgjorene/hovedoppgjoret-2026/uravstemming/industrioverenskomsten-virke/).
- [Tariffavtale] **Privat service/kontor, Virke–HK:** Landsoverenskomsten (varehandel/service) og Kontoroverenskomsten har satser fra **01.04.2026**. Landsoverenskomstens minstelønn: trinn 1 **195,04 kr/t**, trinn 2 **195,88 kr/t**, trinn 3 **197,96 kr/t**, trinn 4 **203,55 kr/t**, trinn 5 **221,31 kr/t**, trinn 6 **271,64 kr/t**. Bruk tariff-ID, ansiennitet, gjeldende lønnsgruppe og virkningsdato ved syntetisering. Kilder: [virke](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/landsoverenskomsten-hk/), [virkekontor](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/kontoroverenskomsten-hk/).
- [Tariffavtale] **Kommune, KS HTA 2026–2028:** KS kap. 1 § 5.2, fra **01.10.2026**: ordinært arbeid lørdag/søndag tillegg minst **23 % av timelønn**, likevel minst **73 kr/t**. § 5.4.1 for arbeid etter skift-/turnusplan: mellom **17–21** minst **20 %**, likevel **60 kr/t**; mellom **21–06** minst **25 %**, likevel **70 kr/t**. § 5.4.2 for øvrige berettigede: **17–06** minst **20 %**, likevel **56 kr/t**. Særregel for lærlinger/unge ansatte, bl.a. minst 32 kr etter de oppgitte punktene. Kilde: [kstillegg](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/endringer-i-tilleggene-i-hta-kapittel-1--5-fra-forste-oktober/).
- [Tariffavtale] Disse KS-satsene gjelder **ordinært arbeid for grupper omfattet av § 5**, og må ikke automatisk legges til overtid eller personer/ordninger uten rett til tillegget. Lokale avtaler og særavtaler kan gi særregler. Kilde: [kstillegg](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/endringer-i-tilleggene-i-hta-kapittel-1--5-fra-forste-oktober/).

**A3. Feriepenger, sykepenger og arbeidsgiveravgift**

- [Lov/forskrift] Ferieloven § 10: feriepengegrunnlaget bygger på arbeidsvederlag i opptjeningsåret; hovedsats **10,2 %**, forhøyet sats over 60 år **12,5 %** for lovens ferieordning. Ved fem ukers tariffestet ferie er vanlig sats **12 %** og vanligvis **14,3 %** over 60 år (merk at ekstra 2,3 prosentpoeng har særskilt begrensning ved feriepengegrunnlag over 6 G). Ikke beregn feriepenger av utgiftsrefusjoner. Kilde: [ferie](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/ferie/feriepenger/).
- [Myndighetsveiledning] NAV: arbeidsgiver betaler sykepenger for planlagte arbeidsdager innenfor de første **16 kalenderdagene** i arbeidsgiverperioden etter vilkårene. NAVs sykepengedekning er normalt begrenset til **6 G = 819 294 kr** per 20.10.2026; tariff/avtale om full lønn kan gi høyere faktisk utbetaling og refusjon må skilles fra lønn. Overtidsinntekt inngår normalt ikke i sykepengegrunnlaget. Kilder: [nav](https://www.nav.no/arbeidsgiver/sykepenger-i-arbeidsgiverperioden), [nav6g](https://www.nav.no/sykepenger).
- [Lov/forskrift] Arbeidsgiveravgift for ordinære næringer, 2026: sone I **14,1 %**, Ia **14,1 %** med fribeløpsordning, II **10,6 %**, III **6,4 %**, IV **5,1 %**, IVa **7,9 %**, V **0 %**. Ia-fribeløp **850 000 kr** for 2026. Avgiften er arbeidsgivers kostnad og ikke et trekk i ansattes nettolønn. Kilde: [aga](https://www.skatteetaten.no/satser/arbeidsgiveravgift/?year=2026).
- [Myndighetsveiledning] Arbeidsgiver rapporterer lønn og arbeidsforhold månedlig i **a-meldingen** normalt senest den **5. i påfølgende måned**. Fra **01.01.2026** går forskuddstrekk direkte til Skatteetaten, med betalingsfrist senest første virkedag etter lønnsutbetalingen; gamle skattetrekkskontoregler må ikke kopieres inn i 2026-oppsett. Kilder: [frister](https://www.skatteetaten.no/skjema/direkte-levering-av-a-meldingen/), [skatt2026](https://www.skatteetaten.no/bedrift-og-organisasjon/arbeidsgiver/skattekort-og-skattetrekk/skattetrekkskonto/).

#### B. Sektorforskjeller

| Tema | Industri | Privat service/kontor | Kommune |
|---|---|---|---|
| Tariff | [Tariffavtale] Industrioverenskomst etter avtalepart, avtaledel og lokale tillegg. | [Tariffavtale] Virke–HK er eksempel, **ikke** universell privat tariff. | [Tariffavtale] KS HTA 2026–2028; særavtaler/lokale avtaler og tariffkapittel må spesifiseres. |
| Lønnsstruktur | [Bransjepraksis] Tidslønn, fagarbeiderkategori, skift, eventuelt akkord. | [Bransjepraksis] Avtalefestede lønnstrinn, faste tillegg, provisjon/bonus. | [Tariffavtale] Stillingskode, ansiennitet, kapitler, garantilønn og lokale forhandlinger. |
| Ubekvem arbeidstid | [Tariffavtale] Skift/natt etter rett industridel og lokal avtale. | [Tariffavtale] Kveld/helg avhenger av tariff/avtale; ingen ensartet privatsats. | [Tariffavtale] Spesifikke § 5-satser **fra 01.10.2026**, inkludert prosentsats med gulv. |
| Feriepenger, AGA, 16 dager | [Lov/forskrift] Felles nasjonale regler; konkrete tariffavvik mulig. | [Lov/forskrift] Samme generelle regler. | [Lov/forskrift] Samme regler; lønn utover NAV-grense kan følge HTA. |

Grunnlag: [industri](https://www.fellesforbundet.no/lonn-og-tariff/tariffavtaler/industrioverenskomst/), [virke](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/landsoverenskomsten-hk/), [kstillegg](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/endringer-i-tilleggene-i-hta-kapittel-1--5-fra-forste-oktober/), [nav](https://www.nav.no/arbeidsgiver/sykepenger-i-arbeidsgiverperioden), [aga](https://www.skatteetaten.no/satser/arbeidsgiveravgift/?year=2026).

#### C. Ti fasitspørsmål

Se full maskinlesbar fasit i **`AP2_fasit_sporsmal.csv`**. `Q-2-01`–`Q-2-10` dekker overtidsbetaling, merarbeid/deltid, natt/helg, feriepenger, sykepenger og 6 G, lønnsslipp, rapportering, 1./17. mai, Virke-lønnstrinn og KS-tillegg. **Vanskelige:** `Q-2-02`, `Q-2-03`, `Q-2-05`, `Q-2-10` fordi anvendelig tariff, stilling, tidspunkt og kontrakt kan endre fasiten.

#### D. Realistiske fordelingstall

- [Offisiell statistikk] SSB, **2025** månedslønn per **heltidsekvivalent**, SSB-artikkel oppdatert **27.05.2026**: nasjonal **Q1 45 470 kr**, **median 55 800 kr**, **Q3 69 490 kr**, gjennomsnitt **62 070 kr**. Dette er *ikke* sektorens minstelønn og må ikke brukes ukritisk på en bestemt stilling. Kilde: [ssb](https://www.ssb.no/arbeid-og-lonn/lonn-og-arbeidskraftkostnader/artikler/hva-er-vanlig-lonn-i-norge).
- [Offisiell statistikk] Yrkesfordeling SSB **2025** for **kontormedarbeidere STYRK 4110**: Q1 **44 440**, median **49 430**, Q3 **57 590** kr/mnd; **butikkmedarbeidere STYRK 5223**: Q1 **34 230**, median **42 020**, Q3 **45 240**. Kilde: [ssb](https://www.ssb.no/arbeid-og-lonn/lonn-og-arbeidskraftkostnader/artikler/hva-er-vanlig-lonn-i-norge).
- [Offisiell statistikk] Yrkesfordeling **2025** for **grunnskolelærere STYRK 2341**: Q1 **54 710**, median **58 750**, Q3 **62 930**; **sykepleiere STYRK 2223**: Q1 **52 030**, median **57 830**, Q3 **63 040** kr/mnd. *Yrke er ikke det samme som institusjonell sektor; filtrer på sektor i SSB-tabell 11418 før du lager kommune- eller industrispesifikke syntetiske fordelinger.* Kilder: [ssb](https://www.ssb.no/arbeid-og-lonn/lonn-og-arbeidskraftkostnader/artikler/hva-er-vanlig-lonn-i-norge), [ssb11418](https://www.ssb.no/statbank/table/11418/).
- [Offisiell statistikk] SSB tabell **11418** (yrke × sektor × statistikkmål) og **11419** (yrke × sektor × næring) er riktig grunnlag for direkte sektorvise kvartiler og tillegg. Kontroller populasjon, år, arbeidstid og om tallene er *totale månedslønninger*, *avtalte lønninger*, *uregelmessige tillegg*, *bonus* eller *overtid* før de brukes. Kilder: [ssb11418](https://www.ssb.no/statbank/table/11418/), [ssb11419](https://www.ssb.no/statbank/table/11419/).
- [Antakelse] Ved syntetisering kan målkvantilene brukes som kontrollpunkter etter trekning av lønn innen samme **STYRK × sektor × heltid**, men en eksakt parametrisk lønnsfordeling (for eksempel lognormal) er ikke identifisert av tre kvartiler. Ikke kall en valgt simulering «SSBs fordeling» eller legg til vilkårlige sektorspesifikke spredninger.

#### E. Forslag til syntetiske data

Maskinlesbare felter og kildebegrunnelser finnes i **`AP2_datasett_forslag.yaml`**. Fire tabeller foreslås: `hr_lonnsavtale_versjon`, `hr_lonnsarter`, `hr_lonnslinjer`, `hr_arbeidsgiveravgift_grunnlag`. Koblinger: `ansatt_id`, `dato`, `avdeling`, `lonnstrinn`, eksisterende 54 994 vakter via `vakt_id` etter validering. Persondata er **syntetiske**. Tariff-/regelverdier er verifiserte referanseverdier med virkningsdato.

#### F. Deterministiske regler

Se **`AP2_regler_forslag.csv`** for `R-2-01`–`R-2-11` og én fallback per spørsmål (`R-2-90`–`R-2-99`). Sentrale beregninger: `overtidstillegg_prosent >= 40` når **lovlig klassifisert overtid**; `ks_helgtillegg >= max(0.23 × timelonn, 73)` for berettiget ordinært arbeid fra 01.10.2026; `ks_kveld_turnus >= max(0.20 × timelonn, 60)` og `ks_natt_turnus >= max(0.25 × timelonn, 70)` med riktig tidssegment; `skattetrekk_innbetalt_dato <= første_virkedag_etter_utbetaling`. Ikke gjenbruk skift-/turnusregler på ubekreftede vakttyper. Juridisk fastsettelse av overtidsklassifikasjon behandles først grundig i AP3.

#### G. Grensetilfeller, usikkerhet og «Ikke funnet»

- [Antakelse] **Deltid og merarbeid:** timer over avtalt deltid, men under fulltid/lovens overtidsterskel, kan ikke uten videre behandles som overtid etter samme regel. Den konkrete tariffen og rettsutviklingen må undersøkes før automatisering. `R-2-91` er fallback for dette spørsmålet og hindrer falske lønnskrav.
- [Tariffavtale] **To industriavtaler:** Virke–Fellesforbundet sin VO-sats er ikke automatisk satsen i NHO–Fellesforbundets Industrioverenskomst. Kilder: [industri](https://www.fellesforbundet.no/lonn-og-tariff/tariffavtaler/industrioverenskomst/), [verkstedvirke](https://www.fellesforbundet.no/lonn-og-tariff/lonnsoppgjorene/hovedoppgjoret-2026/uravstemming/industrioverenskomsten-virke/).
- [Tariffavtale] **2026 KS-regelendring:** For datoer før 01.10.2026 må tidligere gyldige § 5-satser brukes. Overlapp mellom helge-/natt-/helligdagstillegg krever konkret avtaletolkning. Kilde: [kstillegg](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/endringer-i-tilleggene-i-hta-kapittel-1--5-fra-forste-oktober/).
- [Myndighetsveiledning] **Sykepenger:** 6 G er NAVs refusjons-/dekningsgrense, ikke et generelt tak på den lønnen arbeidsgiver kan utbetale etter tariff/avtale. Kilde: [nav6g](https://www.nav.no/sykepenger).
- [Antakelse] **Ikke funnet:** Én nasjonal prosentfordeling av lønnsartene «kveld, natt, helg, helligdag, overtid» på tvers av virksomheter, og én entydig skiftsats for all industri. Må modelleres avtalespesifikt, ikke gis falsk presisjon.
- [Antakelse] **Ikke verifisert:** Full ordlyd/punktnummer for enhver relevant overtidssats i Industrioverenskomsten 2026–2028 og alle Virke-avtaler. Derfor er ikke påståtte enhetlige industrisatser på 50/100 % lagt inn som hardkodede regler.

**Stopp før AP3.**

## Område 3 – Åpningstider, vernissage og utstillingsomrigg

### Museum og kunst – anvendelse i øvingscaset

[Myndighetsveiledning] Museets åpningstid er **ikke** i seg selv dokumentasjon for at alle ansatte kan planlegges på søndag/natt. Søndags- og nattarbeid må oppfylle lovens vilkår; nattarbeid er normalt arbeid kl. 21–06. [Arbeidstilsynet – natt](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/nattarbeid/), [søndag](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/sondagsarbeid/).

[Antakelse] Knytt vakt til *sted, aktivitet, publikumsåpning/vernissage, utstillingsrigg, kunsttransport og nødvendig kompetanse*, slik at vakter for én utstilling ikke tolkes som permanent arbeidstidsordning. Den eksisterende basen oppgis å ha 54 994 vakter 2010–2026 og 168 ansatte; tallene er **syntetisk scenario**, ikke sektornorm.

[Myndighetsveiledning] Tunge kunstgjenstander, arbeid i høyden, publikumsareal og nattlig sikring må risikovurderes før bemanning, også ved eksterne teknikere/frivillige. [Arbeidstilsynet](https://www.arbeidstilsynet.no/hms/roller-i-hms-arbeidet/arbeidsgiver/).

### Opprinnelig sektorsammenligning og A–G (AP3, bevart)

#### AP3 – Område 3: arbeidstid og bemanning

**Kontrolldato:** 20.10.2026  
**Omfang:** kun AP3 i serien AP0–AP9. Generell kunnskapsbase for syntetiske HR-data, ikke individuell juridisk rådgivning.  
**Utgangspunkt:** 168 syntetiske ansatte, seks avdelinger og 54 994 syntetiske vakter (2010–2026). Originaldatabase er ikke tilgangskontrollert i denne leveransen; verken vakter eller avvik er faktisk beregnet.

#### Sammendrag (8 linjer)

1. [Lov/forskrift] Arbeidsmiljøloven skiller **alminnelig tid, merarbeid, overtid og samlet tid**; samme vakt kan ikke klassifiseres uten avtalegrunnlag.
2. [Lov/forskrift] Normal lovgrense er 9 timer per 24 timer og 40 per 7 dager, men særordninger og tariff kan gi kortere eller avtalte andre grenser.
3. [Myndighetsveiledning] Standardgrenser for overtid er 10 timer/7 dager, 25 timer/4 sammenhengende uker og 200 timer/52 uker.
4. [Lov/forskrift] Utgangspunktet for hvile er 11 sammenhengende timer per 24 timer og 35 per 7 dager.
5. [Tariffavtale] KS opererer blant annet med 37,5, 35,5 og 33,6 uketimer; industri har også 36,5 i enkelte skiftordninger.
6. [Offisiell statistikk] AKU 2025: 25 % deltidsarbeid totalt, men 72 % blant butikkmedarbeidere og 52 % blant helsefagarbeidere.
7. [Antakelse] Simulering skal utlede vakter fra yrke, stillingsprosent, faktisk avtale, kalender og bemanningsbehov – ikke tilfeldig velge lovbrudd.
8. [Myndighetsveiledning] Deltidsansattes kompensasjon for merarbeid er under rettslig utvikling; ikke lag en definitiv automatisk lønnsregel per oktober 2026.

#### A. Regler med kilder – gjeldende per 20.10.2026

- **A3-01 [Lov/forskrift]** AML § 10-1: Arbeidstid er tid arbeidstakeren står til disposisjon for arbeidsgiver; arbeidsfri er tid arbeidstakeren ikke står til disposisjon. Juridiske arbeidsminutter avhenger derfor av faktisk pause/disposisjon. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- **A3-02 [Lov/forskrift]** AML § 10-2: Ordningen må være forsvarlig; retten til blant annet fleksibel/redu­sert arbeidstid og fritak må vurderes med vilkår. Ikke la en «lovlig timeterskel» alene godkjenne risikofylt turnus. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- **A3-03 [Lov/forskrift]** AML § 10-3: Ved arbeid til ulike tider kreves arbeidsplan med uker, dager og klokkeslett; drøftes med tillitsvalgte senest **14 dager** før oppstart dersom tariff ikke bestemmer annet. Tilkallingsvikarer uten arbeidsplan har ikke automatisk samme krav. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/arbeidsplan-vaktliste-skift-og-turnus/).
- **A3-04 [Lov/forskrift]** AML § 10-4 (1): Alminnelig arbeidstid normalt maks **9 timer/24 timer** og **40 timer/7 dager**. For lovbestemte skift-/turnuskategorier gjelder kortere ukenormer, blant annet 38/36 timer. Det er lovens grenser – ikke en generell avtale om 37,5 timer. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Veiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/).
- **A3-05 [Lov/forskrift]** AML § 10-5: Skriftlig avtale mellom arbeidsgiver og arbeidstaker kan tillate gjennomsnittsberegning over inntil 52 uker: inntil 10 timer/24t og 48 timer/7d; 48 kan gjennomsnittsberegnes over 8 uker, med maksimalt 50 i enkeltuke. Tariffbundet arbeidsgiver og tillitsvalgte kan skriftlig avtale inntil 12,5 timer/24t, 48/7d gjennomsnitt (8 uker), maksimalt 54 i enkeltuke. Arbeidstilsynet kan på søknad tillate særskilte løsninger (bl.a. 13 timer/døgn). Dette er **ulike hjemler**, ikke én felles automatgrense. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Veiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/gjennomsnittsberegning/).
- **A3-06 [Lov/forskrift]** AML § 10-6: Overtid forutsetter særlig og tidsavgrenset behov, skal ikke være fast ordning. Uten utvidelse: maks **10 timer/7d**, **25 timer/4 sammenhengende uker**, **200 timer/52 uker**. Med skriftlig lokal tariffavtale kan rammer økes til 20/50/300; med Arbeidstilsynets tillatelse kan annen utvidelse gjelde, og grensen er aldri mer enn 400 timer/52 uker. Samlet arbeidstid normalt maks 13 timer/24t og gjennomsnitt 48 timer/uke over 8 uker; særskilte avtaler kan gi avvik. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Veiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/overtid/).
- **A3-07 [Lov/forskrift]** AML § 10-7: Arbeidsgiver skal ha oversikt over *faktisk* arbeidet tid per ansatt. Arbeidsplan er ikke timeregistrering. Inkluder start/slutt, pauser, faktisk arbeidet tid og avvik; oversikten må være etterprøvbar. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/registrering-av-arbeidstid/).
- **A3-08 [Lov/forskrift]** AML § 10-8: Minst **11 timer sammenhengende** arbeidsfri per 24t og **35 timer** per 7d. Skriftlig tariffbasert avtale kan på vilkår redusere til **8 timer/24t** og **28 timer/7d**, med kompenserende hvile/annet vern. Det finnes ytterligere snevre lovunntak – ikke hardkod 8/28 universelt som lovlig minimum. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Veiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/).
- **A3-09 [Lov/forskrift]** AML § 10-9: Ved mer enn 5,5 timers arbeid skal pauser gis; ved 8 timer eller mer minst 30 minutter samlet. Pause er arbeidstid dersom arbeidstaker ikke fritt kan forlate arbeidsplassen eller tilfredsstillende pauserom mangler. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Veiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/).
- **A3-10 [Lov/forskrift]** AML §§ 10-10 og 10-11: Søndags- og nattarbeid er som utgangspunkt ikke tillatt med mindre arbeidets art gjør det nødvendig. Lovens nattperiode er **21:00–06:00**; merk at SSBs statistiske definisjon av nattarbeid er annen. Vurder unntak og drøftinger konkret. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Nattveiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/nattarbeid/).
- **A3-11 [Lov/forskrift]** AML § 10-12: Unntak for ledende/særlig uavhengige stillinger og adgang til tariffavtalte unntak har detaljerte vilkår. Stillingstittel alene er ikke bevis for unntak, og forsvarlighetsvurdering gjelder fortsatt. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- **A3-12 [Tariffavtale]** KS HTA **01.05.2026–30.04.2028** er etablert. KS bruker 37,5, 35,5 og 33,6 uketimer i beregningsveiledning oppdatert 01.10.2026. Vilkårene for hvilken ansatt som tilhører hvilken kategori må fastslås fra **HTA kap. 1 § 4**, relevant særavtale og faktisk turnus; full 2026-avtaletekst ble ikke gjennomgått linje for linje. [KS HTA](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/hovedtariffavtalen-01.05.2026-30) · [KS beregning](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/beregning-av-tilleggslonn/).
- **A3-13 [Tariffavtale]** NHO–Fellesforbundets Industrioverenskomst 2026–2028: Fellesforbundets oppgjørsmelding 13.05.2026 omtaler satsomregning for **36,5/35,5/33,6** uketimer. Dette dokumenterer eksistensen av slike skiftkategorier, men ikke at alle industriansatte har dem. Sjekk **avtaledel (VO/TD/TEKO), turnus og lokal avtale**. [Oppgjørsmelding](https://www.fellesforbundet.no/globalassets/lonn-og-tariffsaker/tariffavtaler/overenskomster-20262028/industrioverenskomsten---resultater-og-endringer-i-taroffoppgjoret-2026.pdf).
- **A3-14 [Tariffavtale]** Private kontor-/servicevirksomheter følger arbeidsmiljøloven, eventuelt Virke- eller NHO-tariff, egne avtaler og arbeidskontrakt. Ingen dokumentert felles lovfestet 37,5-timersnorm for all privat sektor; den er vanlig som avtale. [Lovtekst](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [Veiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/).
- **A3-15 [Myndighetsveiledning]** Rett til overtids*betaling* for deltidsansattes merarbeid er under utvikling: Arbeids- og inkluderingsdepartementet opplyste **15.09.2026** at arbeidsgruppen ikke var enig om løsningen. Uten oppdatert doms-/tariffvurdering skal systemet gi «juridisk kontroll», ikke fasitsvar om kompensasjon. Dette endrer ikke automatisk lovens arbeidstidsgrenser. [Regjeringen](https://www.regjeringen.no/no/aktuelt/arbeidsgruppe-om-overtid-for-deltidsansatte-ikke-omforent-om-losning/id3172625/) · [Rapport](https://www.regjeringen.no/no/dokumenter/deltid-merarbeid-og-overtidsbetaling/id3172543/?ch=1).

#### B. Forskjeller mellom sektorer

| Tema | Industri | Privat: service/kontor | Kommune (KS-området) |
|---|---|---|---|
| Arbeidstidsnorm | [Tariffavtale] 37,5 i mange dagtidsavtaler; skiftkategorier bl.a. 36,5/35,5/33,6 etter avtalebinding | [Lov/forskrift] Lov 9/40; [Bransjepraksis] avtalt 37,5 vanlig, men ikke universell | [Tariffavtale] HTA har 37,5/35,5/33,6 etter ordning og særregler |
| Planlegging | [Bransjepraksis] produksjonsplan, skift og bemanningsbehov | [Bransjepraksis] åpningstider, bemanningsplan, fleksi eller vaktliste | [Bransjepraksis] turnus for pleie/omsorg; SFO/skole og brann kan ha særavtale |
| Lokal avtale | [Tariffavtale] bedriftsklubb/skiftplan, gjennomsnittsberegning | [Tariffavtale] avtaledekning varierer; individuelle/felles lokale ordninger | [Tariffavtale] HTA + særavtaler + lokale protokoller |
| Klassifisering overtid | [Lov/forskrift] AML + spesifikk industridel, også tariffvilkår | [Lov/forskrift] AML + relevant avtale eller individuell kontrakt | [Lov/forskrift] AML + HTA + relevant særavtale |
| Databehov | [Antakelse] maskin-/skiftkode, kompetanse, linjekapasitet | [Antakelse] åpningstid, kundetrykk, bemanningsbehov | [Antakelse] tjenestebehov, hviletidsunntak og deltidsmønster |

**Presisering:** «Privat» og «industri» overlapper som eierskapskategorier; her betyr «industri» produksjonsnæring og «privat» øvrige service/kontor. Oslo kommune og KS-området er ikke samme tariffområde.

#### C. 10 testspørsmål

`Q-3-01`–`Q-3-10` med kilde, kort fasit og minst fire krevende grensetilfeller er lagret i `AP3_fasit_sporsmal.csv`. Spørsmål dekker arbeidsplan, hviletid, overtid, timeføring, gjennomsnittsberegning, nattarbeid, pauser, KS/industriavtaler og deltid.

#### D. Realistiske fordelinger og begrensninger

- **D3-01 [Offisiell statistikk]** SSB AKU **2025**, omtale revidert **15.04.2026**: 75 % heltid og **25 % deltid** blant alle sysselsatte. Dette er ikke andelen i en konkret kommune eller industribedrift. [SSB](https://www.ssb.no/arbeid-og-lonn/sysselsetting/artikler/dette-er-de-vanligste-jobbene-i-norge).
- **D3-02 [Offisiell statistikk]** SSB AKU **2025**: butikkmedarbeidere **72 % deltid**, helsefagarbeidere **52 %**, andre pleiemedarbeidere **69 %**, barnehage-/SFO-assistenter **43 %**, renholdere **50 %**. Det er yrker på tvers av sektorer, med ulike yrkesfordelinger og utvalgsusikkerhet. [SSB](https://www.ssb.no/arbeid-og-lonn/sysselsetting/artikler/dette-er-de-vanligste-jobbene-i-norge).
- **D3-03 [Offisiell statistikk]** SSB AKU **2025**: høyere saksbehandlere i offentlig og privat virksomhet **93 % heltid**, grunnskolelærere **81 % heltid**. Viser hvor misvisende uniform 25 % deltidsandel ville være for alle grupper. [SSB](https://www.ssb.no/arbeid-og-lonn/sysselsetting/artikler/dette-er-de-vanligste-jobbene-i-norge).
- **D3-04 [Offisiell statistikk]** SSB tabell **14757** (næring × heltid/deltid × yrke, 2016–2025), **14756** (sektor × heltid/deltid × yrke, 2016–2025) kan brukes for *kalibrering* etter nedlasting og filtrering. Vi har **ikke hentet ut** celler for industri/KS-spesifikke andeler; de tallene oppgis derfor **ikke**. [14757](https://www.ssb.no/statbank/table/14757/) · [14756](https://www.ssb.no/statbank/table/14756/).
- **D3-05 [Antakelse]** Foreslått syntetisk fordeling: for yrker med publisert AKU-andel brukes andelen som **målintervall ved kalibrering**, ikke som hver ansatts sannsynlighet uten hensyn til virksomhet. For resterende yrker: andel **ikke funnet**, ingen oppdiktet sektorverdi. Antall årsverk må stemme med summen av stillingsprosenter, ikke med antall personer.
- **D3-06 [Antakelse]** Overtid/skiftfordeling: **ikke funnet** offentlig, representativ 2025/2026 fordeling for akkurat museets seks avdelinger; simuler mønstre betinget av arbeidstidsavtale, åpningstid, lovlig maksimum, sesong og lokale hendelser. Merk datagenererte avvik med scenario-ID og behold fraværende avvik som null, ikke oppdiktet prevalens.

#### E. Forslag til syntetiske data

YAML-en beskriver **fem** koblede tabeller: `hr_arbeidstidsordning`, `hr_arbeidstidsavtale`, `hr_vaktplan_versjon`, `hr_tidregistrering`, `hr_bemanningsbehov`. Alle har `omraade: 3`, definert nøkkel, status for kilde og avtale, tidssone og gyldighetsperiode. Viktige koblinger til eksisterende `hr_ansatte.ansatt_id`, `vakter.vakt_id`, `hr_lonnsavtale_versjon.tariff_id` og sektorkoder. **Ingen syntetiske vakter er generert.**

#### F. Deterministiske kontroller

`AP3_regler_forslag.csv` inneholder **14 kontroller** (`R-3-01`–`R-3-14`) og **10 fallback** (`R-3-90`–`R-3-99`). De operative tersklene gjelder kun når versjonert avtalegrunnlag og unntaksstatus er kjent. Brudd på 10/25/200-timersrammen i *standardløpet* kan kontrolleres mekanisk; et mulig tariff- eller dispensasjonsunntak må gi kontrollstatus, aldri automatisk «godkjent». Rolige turnusuker med mange vakter må vurderes over korrekt avregningsperiode.

**Kritisk implementeringsregel:** Kombiner separate valideringer (avtaleversion, overtid, samlet tid, hvile, pauser og planversjon), og bevar logg. En enkelt «vaktlengde > 9» er **ikke** dokumentert overtidsbrudd ved gyldig gjennomsnittsberegning. Alle kalenderberegninger skal bruke arbeidstakerens lokale datoer og faktiske, tidssonekorrigerte tidsstempler.

#### G. Grensetilfeller og usikkerhet

1. **G3-01 [Myndighetsveiledning]** Merarbeid/overtid for deltid har pågående rettsutvikling etter EU- og norske avgjørelser. Regjeringens arbeidsgruppe 15.09.2026 leverte uten enighet. **Ikke hardkod en ensartet betalingsklassifisering.** [Kilde](https://www.regjeringen.no/no/aktuelt/arbeidsgruppe-om-overtid-for-deltidsansatte-ikke-omforent-om-losning/id3172625/).
2. **G3-02 [Tariffavtale]** KS 2026–2028 er bekreftet, og KS oppgir ukenormene 37,5/35,5/33,6. **Ikke endelig verifisert:** samtlige særvilkår i HTA 2026 § 4 og alle særavtaler; derfor trengs `tariff_id`, `tariff_avtaledel`, `arbeidstidsordning_id` og `gyldig_fra`. [Kilde](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/beregning-av-tilleggslonn/).
3. **G3-03 [Tariffavtale]** NHO Industrioverenskomsten og Virke Industrioverenskomsten er ikke automatisk identiske. **Ikke funnet:** en felles, generell skiftplanperiode og detaljert lokal skiftsats for alle industrivirksomheter. [Kilde](https://www.fellesforbundet.no/globalassets/lonn-og-tariffsaker/tariffavtaler/overenskomster-20262028/industrioverenskomsten---resultater-og-endringer-i-taroffoppgjoret-2026.pdf).
4. **G3-04 [Lov/forskrift]** Daglige/ukentlige arbeidsfri- og overtidsgrenser kan endres ved gyldige avtale- eller myndighetsunntak; en påstand om ulovlighet må testes mot konkret dokumentasjon. [Kilde](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
5. **G3-05 [Antakelse]** Planlagt vakt er ikke faktisk arbeidet tid. Eksisterende 54 994 syntetiske vakter må kontrolleres for: ugyldige tidsstempler, nattskift over dato, tidsomstilling, pauser, doble vakter, overlapp, ansatte ansatt fra/til og manglende lokal avtale.
6. **G3-06 [Myndighetsveiledning]** 14-dagersfristen kan påvirkes av tariff eller uforutsette forhold; en vakt som flyttes samme dag er ikke alene bevis for ulovlig endring. [Kilde](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/arbeidstid/arbeidsplan-vaktliste-skift-og-turnus/).
7. **G3-07 [Antakelse]** Det er **ikke funnet** direkte 2025/2026 kildetall for fordeling av 9–11 timers vakter hos de 168 syntetiske museumsansatte. Ikke presenter syntetisk scenarioandel som offisiell statistikk.
8. **G3-08 [Antakelse]** Risikopolicy ved manglende gyldig dokumentasjon: `MANUELL_KONTROLL` og «manglende grunnlag», ikke `LOVLIG` eller `ULOVLIG`.

**Neste steg:** AP4 først etter ny melding «neste». Ikke endre AP2 uten egen godkjenning.

## Område 4 – Fravær der nøkkelkompetansen er smal

### Museum og kunst – anvendelse i øvingscaset

[Antakelse] Museet kan ha enkeltpersonkompetanse i konservering, magasin, sikkerhet, kunsttransport og omvisning. Fravær kan derfor påvirke arrangement, åpningstid eller gjenstandssikkerhet uten at dette gir nye lovbestemte sykmeldingsfrister.

[Bransjepraksis] Følg opp **kompetansedekning per oppgave**, ikke sykefraværsårsak for identifiserbare ansatte i publikums- eller prosjektplan. Kun syntetisk kompetanse-/bemanningsstatus anbefales. [Kulturdirektoratet](https://www.kulturdirektoratet.no/fag/museum-og-kulturarv/museumsutvikling/samlingsforvaltning), [Arbeidstilsynet](https://www.arbeidstilsynet.no/hms/roller-i-hms-arbeidet/arbeidsgiver/).

[Offisiell statistikk] SSBs generelle næringssykefravær er ikke direkte representativt for «museum og kunstmuseum» uten korrekt næringskode og nevner. Museumsstatistikk om besøk/årsverk må ikke brukes som sykefraværsstatistikk. [Kulturdirektoratet](https://www.kulturdirektoratet.no/publikasjoner/det-nasjonale-museumsnettverket-i-2024).

### Opprinnelig sektorsammenligning og A–G (AP4, bevart)

#### AP4 – Område 4: fravær og oppfølging

**Kontrolltidspunkt:** 20. oktober 2026  
**Omfang:** Kun område 4 (AP4). Ikke juridisk rådgivning i enkeltsaker.  
**Versjon:** 1.0 – kildebasert forslag for syntetisk HR-øving.  
**Datagrunnlag:** Opplyst fiktivt kunstmuseum med 168 ansatte, seks avdelinger og syntetiske vakt-, fraværs- og ansattdata. Ingen ekte personopplysninger er undersøkt eller generert.

#### Sammendrag (maks 10 linjer)

1. [Lov/forskrift] Arbeidsgiverperioden er som hovedregel 16 kalenderdager, men start, avbrudd og opptjeningsvilkår må beregnes per fraværstilfelle.
2. [Myndighetsveiledning] Egenmelding krever som hovedregel to måneders tilknytning og gir minst 3 kalenderdager per tilfelle, inntil fire tilfeller i løpet av 12 måneder; lokale utvidelser finnes.
3. [Lov/forskrift] Oppfølgingsplan innen fire uker ved sykefravær, med unntak når åpenbart unødvendig; dialogmøte 1 innen sju uker ved helt fravær, med unntak.
4. [Myndighetsveiledning] NAV vurderer aktivitetskravet ved åtte uker og dialogmøte 2 innen 26 uker, med relevante unntak; ikke et automatisk lovbrudd i arbeidsgiversystemet om møte mangler.
5. [Offisiell statistikk] SSB 2. kvartal 2026 (ikke sesongjustert): industri 5,7 %, varehandel 6,1 %, helse/sosial 9,6 %, alle næringer 6,6 %.
6. [Tariffavtale] Sykelønn/forskuttering ut over folketrygdens minimum avhenger av tariff og avtaledel; KS 2026–2028 og Virke Industrioverenskomsten 2026 krever versjonering.
7. [Lov/forskrift] Opplysninger om arbeidsfunksjon og tilretteleggingsbehov kan være nødvendige, men ikke automatisk diagnoser eller detaljerte helseopplysninger.
8. [Antakelse] Datasettet skal ikke generere medisinske diagnoser eller brukerspesifikke risikoprofiler; næringstall skal kalibrere aggregerte syntetiske nivåer, ikke enkeltansatte.

#### A. Regler og primærgrunnlag

**A4-01 [Lov/forskrift] – egenmelding og dokumentasjon.** Folketrygdloven kapittel 8, særlig §§ 8-23–8-27. NAV oppgir minst **to måneders** ansettelse for bruk av egenmelding, innenfor arbeidsgiverperioden. Minimumsordningen er inntil **tre kalenderdager per tilfelle** og **fire tilfeller i en tolvmånedersperiode**; utvidelser (ofte åtte kalenderdager og 24 dager per 12 måneder) er mulig. Dette er ikke en generell universell åtte-dagersrett. [NAV](https://www.nav.no/egenmelding).

**A4-02 [Lov/forskrift] – arbeidsgiverperioden.** Folketrygdloven §§ 8-18 og 8-19. Som hovedregel betaler arbeidsgiver for planlagte arbeidsdager innenfor de første **16 kalenderdagene**. Første fraværsdag, opphold, ferie og gjentatte tilfeller har særregler; 16 er ikke alltid 16 arbeidsdager. Krav til opptjening er normalt **fire uker** for sykepenger i arbeidsgiverperioden. [NAV](https://www.nav.no/arbeidsgiver/sykepenger-i-arbeidsgiverperioden).

**A4-03 [Lov/forskrift] – etter arbeidsgiverperioden.** Folketrygdloven kapittel 8: NAV behandler sykepenger etter arbeidsgiverperioden; arbeidsgiver må sende inntektsmelding. Ved gyldig refusjonskrav kan arbeidsgiver forskuttere og få refusjon. NAV oppgir inntil **52 uker** for ansatte under 67 år, men maksdato forskyves bl.a. av ferie og perioder i arbeid. Ikke la `start + 364 dager` utløse automatisk endelig konklusjon. [NAV](https://www.nav.no/arbeidsgiver/sykepenger-etter-arbeidsgiverperioden) · [Inntektsmelding, revidert juni 2026](https://www.nav.no/arbeidsgiver/sende-inntektsmelding).

**A4-04 [Lov/forskrift] – tilrettelegging og oppfølgingsplan.** Arbeidsmiljøloven § 4-6 (1) og (3) krever tilrettelegging så langt det er mulig og en oppfølgingsplan innen **fire uker** når arbeidstaker har vært helt eller delvis borte, med unntak dersom det er **åpenbart unødvendig**. Oppfølgingsplanen skal også formidles til sykmelder innen fristen. [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/tilrettelegging/oppfolging-av-sykmeldte/) · [NAV](https://www.nav.no/arbeidsgiver/oppfolgingsplan).

**A4-05 [Lov/forskrift] – dialogmøte 1.** Arbeidsmiljøloven § 4-6 (4): ved **helt** fravær skal arbeidsgiver som hovedregel innkalle til dialogmøte innen **sju uker**, med unntak dersom møtet er åpenbart unødvendig. Ved **delvis/gradert** fravær skal møtet holdes når en av de relevante partene anser det hensiktsmessig. Standardregelen er derfor ikke at alle graderte fravær krever møte automatisk innen 7 uker. [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/tilrettelegging/oppfolging-av-sykmeldte/) · [NAV dialogmøte, oppdatert 08.09.2026](https://www.nav.no/dialogmote).

**A4-06 [Lov/forskrift] – aktivitetskravet etter 8 uker.** Folketrygdloven kapittel 8: NAV vurderer arbeidsrelatert aktivitet etter åtte uker; medisinsk begrunnelse eller manglende mulighet for tilrettelegging kan gi unntak. Regelmotoren kan varsle at vurdering nærmer seg, **ikke** beslutte tap av sykepenger. [NAV](https://www.nav.no/arbeidsgiver/oppfolging-sykmeldte) · [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/tilrettelegging/oppfolging-av-sykmeldte/).

**A4-07 [Myndighetsveiledning] – dialogmøte 2.** NAV har ansvaret for dialogmøte 2 innen **26 uker**, med unntak når åpenbart unødvendig. Arbeidsgiver skal delta når NAV kaller inn; manglende møtebokføring i eget HR-system betyr ikke uten videre at arbeidsgiver har misligholdt en plikt. [NAV](https://www.nav.no/dialogmote) · [NAV arbeidsgiver](https://www.nav.no/arbeidsgiver/oppfolging-sykmeldte).

**A4-08 [Lov/forskrift] – medvirkning og medisinske opplysninger.** Arbeidsmiljøloven § 4-6 og § 2-3: arbeidstaker skal medvirke til funksjons- og tilretteleggingsvurdering, men behøver ikke dele diagnose eller private medisinske opplysninger med arbeidsgiver. Opplysninger om sykefravær har personvernrisiko; kun rollebegrensede, nødvendige opplysninger inngår i syntetiske skjema. [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/tilrettelegging/oppfolging-av-sykmeldte/).

**A4-09 [Lov/forskrift] – lovfestede permisjoner.** Arbeidsmiljøloven kapittel 12 har regler om bl.a. foreldrepermisjon og omsorgspermisjoner. Rett til permisjon må skilles fra rett til **lønn/ytelse**, som ofte bygger på folketrygd og tariff. Ifølge Arbeidstilsynet er det særlig svangerskapskontroll og ammefri som gir lovfestet lønnet permisjon etter selve arbeidsmiljøloven (med vilkår); andre lønnede permisjoner krever annet grunnlag. [Arbeidstilsynet](https://www.arbeidstilsynet.no/lonn-og-ansettelse/permisjoner/) · [Foreldrepermisjon](https://www.arbeidstilsynet.no/lonn-og-ansettelse/permisjoner/foreldrepermisjon/).

**A4-10 [Lov/forskrift] – barn sykt.** Folketrygdloven kapittel 9 og arbeidsmiljøloven § 12-9. NAV oppgir som hovedregel **10 omsorgsdager** per kalenderår ved ett eller to barn, **15** ved tre eller flere, og egne regler for aleneomsorg, sykdom/funksjonsnedsettelse og barns alder. Disse er **dager**, ikke generell fraværstimekvote; sektor kan ha tillegg. [NAV](https://www.nav.no/arbeidsgiver/omsorgspenger).

**A4-11 [Lov/forskrift] – ferie under sykdom.** Ferieloven § 9: krav om utsatt lovbestemt ferie på grunn av sykdom forutsetter at arbeidstakeren har vært **helt arbeidsufør**, har legeerklæring og overholder krav til når kravet fremsettes. Ikke gi automatisk utsettelse ved 50 % gradert sykmelding. [Ferieloven hos Arbeidstilsynet](https://www.arbeidstilsynet.no/regelverk/lover/ferieloven--feriel/) · [Veiledning](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/ferie/).

**A4-12 [Tariffavtale] – kommune.** KS HTA er oppdatert for **1.5.2026–30.4.2028**. Forrige HTA 2024–2026 kapittel 1 § 8 hadde bestemmelser om full lønn under sykdom og 50 uker samt arbeidsgiverperioder. **Forbehold:** Full ordlyd i kap. 1 § 8 i gjeldende 2026–2028 er ikke verifisert i denne gjennomgangen. Ikke viderefør et gammelt punkt eller varighet automatisk uten ny tekstkontroll. [KS gjeldende avtale](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/hovedtariffavtalen-01.05.2026-30) · [KS historisk PDF, 2024–2026](https://www.ks.no/globalassets/fagomrader/lonn-og-tariff/tariff-2024/Hovedtariffavtalen-2024-2026.pdf) · [KS forklaring](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/opptjening-av-rett-til-ny-arbeidsgiverperiode-og-ny-rett-til-sykelonn/).

**A4-13 [Tariffavtale] – industri.** Fellesforbundet oppgir for **Industrioverenskomsten (Virke), 2026** at bedriftene skal forskuttere syke-, pleie- og foreldrepenger i **inntil fire måneder**, med nærmere vilkår. Dette kan ikke generaliseres til NHO-industribedrifter eller annen tariffdel. Avtaledokument og lokal bedriftsavtale må kobles eksplisitt. [Fellesforbundet, 2026](https://www.fellesforbundet.no/lonn-og-tariff/lonnsoppgjorene/hovedoppgjoret-2026/uravstemming/industrioverenskomsten-virke/).

**A4-14 [Bransjepraksis] – øvrig privat sektor.** Organisering av egenmeldinger, avtalefestet betalt velferdspermisjon og forskuttering varierer med tariff, virksomhet og lokale rutiner. Samme lovbaserte minimum gjelder, men ikke et ensartet privat «standardvilkår». [NAV](https://www.nav.no/egenmelding) · [Arbeidstilsynet](https://www.arbeidstilsynet.no/lonn-og-ansettelse/permisjoner/) · [NAV](https://www.nav.no/arbeidsgiver/sykmeldt-ansatt).

#### B. Forskjeller mellom sektorer

| Tema | Industri | Privat service/kontor | Kommune (KS) |
|---|---|---|---|
| Egenmelding | Lovens minimum + mulig lokalt utvidet ordning | Lovens minimum + bedriftsordning | Lovens minimum + kommunens praksis; ikke automatisk identisk i alle kommuner |
| Sykelønn | Lov/NAV + relevant Industriavtale; Virke IO 2026 har egne forskutteringsvilkår | Lov/NAV + ev. Virke/NHO eller lokale avtaler | HTA 2026–2028 kan gi mer enn lovens minimum; gjeldende § 8 må verifiseres |
| Oppfølging (4/7/8/26) | Samme lov- og NAV-frister | Samme lov- og NAV-frister | Samme lov- og NAV-frister; offentlig arbeidsgiver gir ikke automatisk andre frister |
| Organisering | Skift, fagarbeiderfunksjoner og alternativt arbeid må vurderes konkret | Oppgaver, kundedrift og hjemmekontor kan være aktuelle tiltak | Tjeneste-, bruker- og bemanningsbehov; tilrettelegging vurderes konkret |
| Måling/rapportering | Næringstall for industri | Næringstall per relevant service/kontor-næring | Kommunal arbeidsgiver følger næring/foretakskoder; undervisning og helse/sosial er **ikke** identisk med kommune |
| Permisjoner | Lovfestet rett + tariff-/bedriftsordninger | Lovfestet rett + tariff-/bedriftsordninger | Lovfestet rett + KS HTA og særavtaler |

**Definisjon:** «Industri» er næringskategori som også er privat eid; «privat» i denne sammenligningen betyr service og kontor uten industri. Oslo kommune følger ikke KS-området.

#### C. 10 typiske spørsmål og fasit

Maskinlesbare, kildegrunnlagte `Q-4-01`–`Q-4-10` står i `AP4_fasit_sporsmal.csv` med separate markeringer for vanskelige tilfeller. Spørsmålene dekker egenmelding, sykelønn, arbeidsgiverperiode, 4-/7-/8-/26-ukersfrister, delvis sykmelding, sykt barn, tariff og medisinsk personvern. Ferie behandles i A og G.

#### D. Realistiske fordelinger og statistikk

**Kilde:** SSBs sykefraværsstatistikk, **publisert 3. september 2026**, data **2. kvartal 2026**, tabell 2 (SSB Statistikkbanken **13935**) for næring. Tall under er **ikke sesongjustert**, egen- og legemeldt kombinert, **prosent av avtalte dagsverk**, ikke prosent ansatte eller «sannsynlighet for diagnose». [SSB](https://www.ssb.no/arbeid-og-lonn/arbeidsmiljo-sykefravaer-og-arbeidskonflikter/statistikk/sykefravaer) · [Statistikkbanken 13935](https://www.ssb.no/statbank/table/13935/).

| Næring | 2. kv. 2025 | 2. kv. 2026 | Bruk i øvingsdata |
|---|---:|---:|---|
| Alle næringer | 6,4 % | 6,6 % | Kun nasjonal referanse |
| Industri | 5,5 % | 5,7 % | Aggregatkalibrering av industri |
| Varehandel | 6,0 % | 6,1 % | Service, hvis tilsvarende næring |
| Informasjon/kommunikasjon | 3,9 % | 4,0 % | Kontor/IKT, kun relevant NACE |
| Overnatting/servering | 6,1 % | 6,3 % | Service hvis tilsvarende næring |
| Undervisning | 6,6 % | 6,8 % | Næringsreferanse, **ikke** kommune totalt |
| Helse-/sosialtjenester | 9,4 % | 9,6 % | Næringsreferanse, **ikke** kommune totalt |
| Personlig tjenesteyting | 6,0 % | 6,0 % | Mulig referanse for museum, men næringskode må sjekkes |

**D4-02 [Offisiell statistikk]** SSB 2. kv. 2026 oppgir også egen- og legemeldt samlet **6,68 % sesongjustert** for alle næringer (tabell 1, kilde 12439). Dette må ikke blandes direkte med næringstabellens ikke sesongjusterte 6,6 %. [SSB](https://www.ssb.no/arbeid-og-lonn/arbeidsmiljo-sykefravaer-og-arbeidskonflikter/statistikk/sykefravaer).

**D4-03 [Antakelse]** Syntetisk generering må treffe rimelige **næring × kvartal × fraværstype**-nivåer innen valideringstoleranse valgt av bruker. Selv for næring med publisert aggregat sier tallet ikke hvordan fravær er fordelt på ansatte, varighet, alder eller seks avdelinger.

**D4-04 [Antakelse]** Fraværsvarighet, andel gradert sykmelding, permisjonsandel, andel egenmelding og saksflytfordeling for museets 168 ansatte: **Ikke funnet som dokumentert mikrofordeling**. Ikke trekk tilfeldige personvekter ut fra næringsprosentene; behold forslagene som simulering med tydelig `syntetisk_scenario_id` og kontroller aggregerte dager mot valgt referanse.

**D4-05 [Antakelse]** De rapporterte SSB-nivåene er **kvartalsgjennomsnitt**, ikke en fraværsgrense. En avdeling som avviker fra næringssnitt skal ikke klassifiseres som lovbrudd, dårlig ledelse eller medisinsk risiko uten selvstendig evidens.

#### E. Forslag til syntetiske data

Seks tabeller ligger med **kolonnenavn, datatyper, verdidomener og koblinger** i `AP4_datasett_forslag.yaml`:

- `hr_fravaershendelse`: fraværstype, grad, perioder, beregningsgrunnlag og kildeklassifisering, uten diagnose.
- `hr_egenmeldingsordning`: gyldighetsdato og lokal rett, fremfor universell 8/24-regel.
- `hr_sykepenger_arbeidsgiverperiode`: sammenlenkede kalenderperioder, arbeidsgiverperiode og refusjonsstatus.
- `hr_sykefravaersoppfolging`: arbeidsfunksjon, frister, unntak og deling av oppfølgingsplan (ikke medisinske detaljer).
- `hr_dialogmote`: hvilken aktør som har møteansvar, 7-/26-ukers milepæl og dispensasjonsgrunnlag uten diagnose.
- `hr_permisjon_omsorg`: hjemmel, omsorgsdager og status for eventuelt tariffbasert lønn.

**Koblinger:** `hr_ansatte.ansatt_id`, eksisterende `fravaer` (hvis nøkkelen finnes), `vakter.vakt_id`, `hr_arbeidstidsavtale.ansatt_id`, AP2 lønnsgrunnlag ved beregning. Alle konkrete tabellnavn i det eksisterende SQLite-skjemaet må bekreftes før import – her er koblinger logiske forslag, ikke påstand om at datakolonnene fysisk finnes.

**Dataminimering:** Ikke modellér diagnose, behandlingsdetaljer, journalnotat, fødselsnummer eller ekte barns identitet. Begrens adgang til personnivå. Bruk `hjemmelsklasse`, `friststatus`, `tilretteleggingsmulig` og aggregerte hendelser.

#### F. Deterministiske regler

Reglene `R-4-01`–`R-4-15` og én fallback for hvert spørsmål `R-4-90`–`R-4-99` ligger i `AP4_regler_forslag.csv`. Disse er **forslag til logiske valideringer**, ikke en juridisk domsmotor:

1. Ved 28 kalenderdager uten oppfølgingsplan **og uten dokumentert åpenbart-unødvendig-unntak** → mulig fristavvik, manuell kontroll.
2. Ved 49 dager helt sykmeldt uten dialogmøte 1, og uten dokumentert unntak → mulig fristavvik, manuell kontroll.
3. Ved gradert fravær → kun behovsstyrt vurdering av møte 1; ingen automatisk fristbruddsmelding uten behovsgrunnlag.
4. Etter 56 dager → varsel om NAVs aktivitetsvurdering, aldri automatisk avslag på ytelse.
5. Ved 182 dager → NAV-eid dialogmøte 2; spør om møte eller gyldig unntak, ikke skyldfordel HR-systemet.
6. Ved «egenmelding overskrider minimum» → sjekk bedriftsordning, opptjening og fraværstype før flagging.
7. Ved sykelønn/tariffvurdering → krev avtale-ID, avtaledel og gyldighetsdato.
8. Ved fraværsstatistikk → bruk faktisk avtalte dagsverk og fraværsdagsverk, ikke en enkel telling av ansatte.

**Sikkerhetsport:** Ved manglende opplysninger gi `MANUELL_KONTROLL` eller `UTILSTREKKELIG_GRUNNLAG`, aldri `LOVLIG`, `ULOVLIG` eller `MISBRUK`.

#### G. Grensetilfeller, usikkerhet og kildekritikk

1. **G4-01 [Lov/forskrift]** «Fjorten sykefraværsdager = fjorten dagers arbeidsgiverperiode» er feil: arbeidsgiverperioden er kalenderdagbasert med spesifikke start-/avbruddsregler. [NAV](https://www.nav.no/arbeidsgiver/sykepenger-i-arbeidsgiverperioden). Metode M01/M04.
2. **G4-02 [Myndighetsveiledning]** Graderte sykefravær gir ikke automatisk sjuukerskrav til dialogmøte 1. Arbeidstilsynets presise forklaring har forrang fremfor forkortet veiledning som kan gi inntrykk av en universell frist. [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/tilrettelegging/oppfolging-av-sykmeldte/) · [NAV](https://www.nav.no/dialogmote). Metode M04/M05.
3. **G4-03 [Tariffavtale]** KS HTA 2026–2028 er bekreftet, men eksakt lønnsbestemmelse § 8 i 2026-utgaven er **ikke verifisert direkte** her. 2024–2026-teksten må ikke gjenbrukes som gjeldende ordlyd. [KS 2026](https://www.ks.no/fagomrader/lonn-og-tariff/hovedtariffavtalen/hovedtariffavtalen-01.05.2026-30) · [KS 2024–26](https://www.ks.no/globalassets/fagomrader/lonn-og-tariff/tariff-2024/Hovedtariffavtalen-2024-2026.pdf). Metode M09/M11.
4. **G4-04 [Tariffavtale]** Virke Industrioverenskomsten 2026 har dokumentert forskuttering «inntil fire måneder», men dette dokumenterer ikke hva *alle* NHO/LO-overenskomster eller lokale industribedrifter gjør. [Fellesforbundet](https://www.fellesforbundet.no/lonn-og-tariff/lonnsoppgjorene/hovedoppgjoret-2026/uravstemming/industrioverenskomsten-virke/). Metode M04/M10.
5. **G4-05 [Offisiell statistikk]** SSB næring er **ikke det samme som eierform**: næringen undervisning er blandet offentlig/privat; næringen helse/sosial kan ikke stå som «kommunal sykefraværsprosent». SSB-statistikken er aggregert prosent dagsverk, ikke personrisiko. [SSB](https://www.ssb.no/arbeid-og-lonn/arbeidsmiljo-sykefravaer-og-arbeidskonflikter/statistikk/sykefravaer). Metode M01/M09.
6. **G4-06 [Lov/forskrift]** Velferdspermisjon (begravelser, flytting, private ærender) er ikke universelt lønnet etter arbeidsmiljøloven. Betaling må hjemles i tariff/avtale. [Arbeidstilsynet](https://www.arbeidstilsynet.no/lonn-og-ansettelse/permisjoner/). Metode M04.
7. **G4-07 [Lov/forskrift]** Det er rett til funksjonssamtale og tilrettelegging, **ikke** generelt krav om å oppgi medisinsk diagnose. Ikke legg inn diagnose som påkrevd felt. [Arbeidstilsynet](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/tilrettelegging/oppfolging-av-sykmeldte/). Metode M10/M12.
8. **G4-08 [Lov/forskrift]** Ferie under gradert sykmelding og ferie under hel sykmelding har ulike rettslige utfall; ferieutsettelse forutsetter hel arbeidsuførhet. [Ferieloven](https://www.arbeidstilsynet.no/regelverk/lover/ferieloven--feriel/). Metode M01/M04.
9. **G4-09 [Antakelse]** Lokal egenmeldingsordning ved museet er ukjent. Ikke anta 8/24-dagers ordning på grunnlag av IA-tilhørighet eller organisasjonstype.
10. **G4-10 [Antakelse]** Periodeforskyvning (ferie, retur, stans, gradert sykmelding), lokale avtaler, aldersregler og refusjon gir behov for eksplisitt modell av kalenderhendelser. Ingen automatisk sykepengerettslig maksdato avgjøres på disse syntetiske feltene alene.

**AP4 stoppunkt:** Behandle ikke AP5 før et nytt eksplisitt «neste».

## Område 5 – Hva museumsproduktivitet faktisk kan måle

### Museum og kunst – anvendelse i øvingscaset

[Offisiell statistikk] Kulturdirektoratet publiserer museumsstatistikk, bl.a. besøk, aktivitet og årsverk i det nasjonale museumsnettverket (61 tilskuddsmuseer, data 2024, rapport 2025). Dette kan brukes som sektorbakgrunn, ikke som fasit for personproduktivitet. [Kulturdirektoratet](https://www.kulturdirektoratet.no/publikasjoner/det-nasjonale-museumsnettverket-i-2024).

[Bransjepraksis] Skille minst fire virksomhetsmål: **publikum/formidling** (besøk og programmer), **utstilling/produksjon** (leveranser og milepæler), **samlingsforvaltning** (tilstandsdokumentasjon/registrering) og **bevaring/kvalitet** (risiko og konservatorfaglig arbeid). Tall som besøk per årsverk alene kan premierer feil atferd og overser samlingsansvaret. [Kulturdirektoratet](https://www.kulturdirektoratet.no/fag/museum-og-kulturarv/museumsutvikling/samlingsforvaltning).

[Lov/forskrift] Bruk ikke individuelle adgangs-, museumbutikk- eller IT-logger til skjult prestasjonsrangering; eventuell ansattkontroll må vurderes konkret etter arbeidsmiljølovens kontrolltiltaksregler og personvernprinsippene. [Arbeidstilsynet](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/), [Datatilsynet](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/).

### Opprinnelig sektorsammenligning og A–G (AP5, bevart)

#### AP5 – Område 5: produktivitet, målinger og grensetilfeller

**Kontrolltidspunkt:** 20. oktober 2026  
**Versjon:** 1.0  
**Omfang:** Bare arbeidspakke AP5 / område 5. Ingen persondata eller simulerte tallverdier generert.  
**Virksomhet:** Fiktivt kunstmuseum med 168 ansatte, seks avdelinger og eksisterende syntetiske 54 994 vakter (2010–2026). Dette er brukeroppgitte scenarioopplysninger, ikke kontrollert databaseinnhold.  
**Sammenlikning:** Industri; privat service/kontor; kommune innen KS-området (Oslo kan avvike tariffmessig, men denne pakken handler ikke om tariffbeløp).

#### Sammendrag (maks 10 linjer)

1. [Lov/forskrift] Arbeidsmiljøloven §§ 9-1 og 9-2: ansattkontroll krever saklig grunn, forholdsmessighet, drøfting, informasjon og løpende evaluering.
2. [Lov/forskrift] E-postforskriften § 2 andre ledd forbyr i utgangspunktet overvåking av ansattes elektroniske utstyrsbruk, med avgrensede nettverks- og sikkerhetsunntak.
3. [Myndighetsveiledning] GDPR krever særskilt formål, behandlingsgrunnlag, dataminimering, lagringsbegrensning og tilgang etter tjenstlig behov.
4. [Offisiell statistikk] SSBs arbeidskraftproduktivitet er bruttoprodukt per utført timeverk for næringer; det er ikke individprestasjon.
5. [Standard] OEE/ISO 22400 gjelder produksjonsutstyr og produksjonsprosesser, ikke en universell ansattkarakter.
6. [Offisiell statistikk] KOSTRA måler bl.a. kommunal enhetskostnad; høy kostnad kan skyldes kvalitet, behov, smådrift eller lønnsnivå.
7. [Forskning] STAMI finner at sykenærvær kan ha både gunstige og ugunstige virkninger; null fravær innebærer ikke dokumentert høy produktivitet.
8. [Antakelse] Tallfordelinger for museumsarbeideres produktivitet mangler. Vi foreslår derfor scenario- og observasjonsbaserte tabeller, ikke oppdiktede nasjonale normalverdier.

#### A. Regler, definisjoner og kildekontroll

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

#### B. Forskjeller mellom sektorene

| Tema | Industri | Privat service/kontor | Kommune |
|---|---|---|---|
| Vanlige driftsmål [Bransjepraksis] | OEE (maskin), kassasjon, energi per enhet, produksjonsstans | Køtid, kundesaker, leveringstid, gjenåpning/feilretting og kundetilfredshet | KOSTRA-dekning/enhetskostnader, kvalitetsindikatorer og tjenestetilgang |
| Riktig enhet [Antakelse] | Linje, maskin, batch, produkt | Team, prosess, sakstype | Tjeneste, kommune, institusjon, fagområde |
| Kvalitetskorreksjon [Antakelse] | Produktmiks, vedlikehold, skift, råvarefeil | Saksalvorlighet, kompleksitet, kundegrunnlag, samspill | Brukerbehov, kvalitet, bosetting, geografisk spredning |
| Arbeidstidsnevner [Lov/forskrift] | Faktiske timeverk, skift, innleie etter definisjon | Faktiske timeverk, deltid, kundeåpningstid | Årsverk/timeverk; ikke tell alle som 100 % |
| Kontrollgrenser [Lov/forskrift] | AML kap. 9 + GDPR + e-postforskriften | Samme; særlig digitale verktøy/aktivitetssporing | Samme; i tillegg tjeneste- og forvaltningskontekst |
| Offentlig sammenligning [Offisiell statistikk] | SSB 09174, korrekt næringskode | SSB 09174 for riktig service-/kontornæring | SSB KOSTRA; per tjeneste og med kvalitet/strukturforbehold |

**Viktig:** Industri er del av privat sektor. Her betyr «privat» service/kontor uten industri. KOSTRA må ikke likestilles med personvurdering i KS-systemet.

#### C. Ti typiske spørsmål med fasit

Maskinlesbar fasit `Q-5-01`–`Q-5-10` ligger i `AP5_fasit_sporsmal.csv`. Minst fire spørsmål har vanskelighetsmarkering. Fasit besvarer blant annet «kan arbeidsgiver se tastetrykk/PC-bruk», «kan maskin-OEE brukes mot operatøren», «er høy KOSTRA-enhetskostnad ineffektivitet», «hvordan sammenligne deltid», «sykenærvær», «hjemmekontor», «må vi drøfte» og «er små team anonyme».

#### D. Realistiske tall, fordelinger og statistisk avgrensning

**D5-01 [Offisiell statistikk] – næringsproduktivitet:** [SSB 09174](https://www.ssb.no/statbank/table/09174/) er en **årlig serie 1970–2025**, oppdatert **28.05.2026**, for næringer, timer og arbeidsproduktivitet. Den gir et empirisk grunnlag for **fordelinger av årsvekst over tid innen samme næring**, etter uttrekk og konsistent basisår. Ikke kopier én års endring som individfordeling; **konkrete 2025-rater er ikke uttrekt** i AP5 og er ikke oppdiktet.

**D5-02 [Offisiell statistikk] – KOSTRA:** Reviderte **2025**-tall ble publisert **15.06.2026**. Tabell [13502](https://www.ssb.no/statbank/table/13502/) har utvalgte barnehageindikatorer og [06804](https://www.ssb.no/statbank/table/06804/) er en nøkkeltallstabell for grunnskole. Ved senere uttrekk kan en velge **ett mål × år × kommunegruppe** og vise median, 25-/75-persentil og variasjonsbredde. I AP5 er **ikke** kommuneverdier tatt ut; ingen slike persentiler oppgis. Bruk funksjon og definisjon før sektorbenchmark.

**D5-03 [Offisiell statistikk] – illustrasjon av ulik nevner:** SSBs barnehagestatistikk for **2025** viser **264 210 barn** og **97 585 ansatte** nasjonalt. Dette er **ikke** et mål på barnehageansattes produktivitet: ansatte er personer, ikke standardiserte årsverk, og antall barn tar ikke høyde for alder, oppholdstid eller støttebehov. Tall brukes kun for å demonstrere nevnerproblemet. [SSB 2025](https://www.ssb.no/utdanning/barnehager/statistikk/barnehager).

**D5-04 [Standard] – avgrenset OEE-verdiområde:** Faktorene tilgjengelighet, ytelse og kvalitet er forholdstall, og en konsistent normert modell har komponenter mellom 0 og 1, slik at OEE presenteres **0–100 %**. Dette er et **matematisk domene**, ikke en empirisk nasjonal fordeling. Skift, linje, produkttype og definerte planlagte stopp skal dokumenteres før beregning. [ISO 22400-2](https://www.iso.org/standard/54497.html).

**D5-05 [Antakelse] – museum:** For fiktivt museum er fordelingene for sakstider, besøk per åpningstime, utstillingsvedlikehold, produksjonsstopp, kvalitet og individuelle resultat ikke tilgjengelige. **Ikke funnet** dokumentert mikrofordeling for de 168 ansatte eller seks avdelinger. Foreslått metode: registrer først syntetiske hendelser og sammenlign deretter *observerte syntetiske* aggregater mellom scenarier. Ikke trekk fordelingsparametere fra eksterne næringstall uten populasjonssamsvar.

**D5-06 [Antakelse] – ulik vekting:** Bruk **ikke** felles «produktivitetsscore 0–100» for undervisning, kundeservice, maskiner og HMS. Vekt må forankres i formål, kvalitetsmål og etterprøvbar definisjon. Fordeling/kalibrering kan ikke gis før slik definisjon er laget. Test heller nevner=0, svært små grupper, ekstremt lange vakter, stor oppgavemiks og mulig re-identifisering.

#### E. Forslag til syntetiske data

Sju skjemaer i `AP5_datasett_forslag.yaml`:

1. `hr_maalekatalog`: godkjent måledefinisjon, enhet, aggregeringsnivå, beregning og kildeversjon.
2. `hr_maalestyring_vurdering`: kontrolltiltakets formål, nødvendighet, drøfting, informering, behandlingsgrunnlag, lagring, eventuelt DPIA og go/no-go.
3. `hr_team_kpi_periode`: måling på avdeling/team/periode, kvalitet, oppgavemiks og nevner.
4. `hr_industri_utstyrskjoring`: teknisk OEE, produksjon, stopp og kassasjon for maskin/linje (aldri personscore).
5. `hr_service_saksflyt`: serviceoppdrag og behandlingstid (syntetisk, uten kundenavn).
6. `hr_kommunal_kostra_referanse`: eksterne 2025-nøkkeltall med tabell, variabel, enhet og vedlikehold av kildeversjon (verdier kan stå tomme).
7. `hr_arbeidsinnsats_aggregat`: kun aggregert faktisk timeverk per periode og gruppe, avledet fra AP3 og vaktgrunnlaget uten helseprofil.

Ingen helsedetaljer, tastetrykk, skjermbilder, GPS-spor eller private opplysninger foreslås. Ansatt-ID brukes bare **internt ved nødvendig timeverksaggregering**, ikke som nøkkel i det offentlig synlige produktivitetsdashboardet. Reelle SQLite-feltnavn må bekreftes før implementering.

#### F. Deterministiske kontrollregler

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

#### G. Grensetilfeller, usikkerhet og djevelens advokat

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

## Område 6 – Rollebaserte undersøkelser, avvik og frivillige

### Museum og kunst – anvendelse i øvingscaset

[Lov/forskrift] I små kunstfaglige grupper kan stillingskombinasjoner røpe identitet selv om resultater presenteres samlet. Minimumsantall svar fra ett verktøy er derfor **ikke et universelt GDPR-frikort**. Bruk konkret identifiseringsvurdering, ikke bare `n >= X`. [Datatilsynet](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/).

[Myndighetsveiledning] Frivillige må ha eget HMS-spor. De skal ikke automatisk behandles som ansatte i lønn, sykefravær eller personalundersøkelser; arrangør/arbeidsgiver kan likevel ha sikkerhetsansvar. [Arbeidstilsynet](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/frivillig-arbeid/).

[Bransjepraksis] Lag egne **syntetiske avvikskategorier** for kunsthåndtering, magasin/miljø, rigging, publikumsinteraksjon og arrangement. Ikke knytt museumsgjenstander, rettigheter og HR-personopplysninger sammen i ett generisk rådatabord uten formålskontroll. [Kulturdirektoratet](https://www.kulturdirektoratet.no/fag/museum-og-kulturarv/museumsutvikling/samlingsforvaltning), [Datatilsynet](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/).

### Opprinnelig sektorsammenligning og A–G (AP6, bevart)

#### AP6 – innsamling fra ansatte

**Dato/kildekontroll:** 20.10.2026  
**Omfang:** Kun område 6 i originalbestillingen; ingen AP7-arbeid.  
**Kontekst:** Fiktivt museum med 168 ansatte, seks avdelinger, syntetisk SQLite-data og eksisterende personalhåndbok, vakt-, fraværs- og kompetansemodeller.  
**Metode:** M01 påstandsisolering, M04 kilde-/relevanstest, M09 aktualitetskontroll, M10 motbevis, M12 automatisk beslutningssperre.

#### Sammendrag (maks 10 linjer)

1. **Kritisk:** «Anonym» kan ikke avgjøres ved en universell gruppestørrelse; koblings- og differanseangrep kan avsløre personer. [Lov/forskrift] [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-20](https://www.datatilsynet.no/globalassets/global/dokumenter-pdfer-skjema-ol/regelverk/veiledere/anonymisering-veileder-041115.pdf)
2. **Kritisk:** Anonyme varsler krever undersøkelse, men kan være vanskelige å opplyse; vern av varsler og kontradiksjon må balanseres. [Lov/forskrift] [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-11](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/slik-bor-arbeidsgiver-handtere-varsling/)
3. **Oppdatert 2026:** Nye forskriftspresiseringer om psykososial kartlegging trådte i kraft 01.01.2026. [Lov/forskrift] [K6-03](https://www.arbeidstilsynet.no/regelverk/forskrifter/forskrift-om-utforelse-av-arbeid/) · [K6-04](https://www.arbeidstilsynet.no/arbeidsmiljo/psykososialt-arbeidsmiljo)
4. **Lovkrav:** Minst fem jevnlig ansatte utløser plikt til skriftlige varslingsrutiner; små virksomheter kan også være omfattet. [Lov/forskrift] [K6-09](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/virksomheten-skal-ha-rutiner-for-intern-varsling/)
5. **Sektor:** Industri, service/kontor og kommune har samme hovedlovgivning, men varierer i risiko og undersøkelsesmetoder. [Bransjepraksis] [K6-13](https://www.arbeidstilsynet.no/arbeidsmiljo/vold-og-trusler/) · [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/)
6. **Testdesign:** Bare syntetiske data, aggregering, prosessmetadata og tjenstlig tilgang; varselsinnhold lagres separat. [Antakelse] [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38)
7. **Statistikk:** LKU-A 2022 oppgir 51 % svarandel i en representativ nasjonal undersøkelse – ikke som norm for interne pulsmålinger. [Offisiell statistikk] [K6-18](https://noa.stami.no/metode/datakilder/levekarsundersokelsen-om-arbeidsmiljo/)
8. **Ingen automatisk dom:** Faste kontroller markerer mangel eller sperrer publisering; de avgjør ikke om arbeidsgiver «har brutt loven». [Antakelse]

#### A. Regler og kildegrunnlag

##### A6-01. Kartlegging og ansattes medvirkning

- **[Lov/forskrift]** Arbeidsmiljøloven § 3-1, § 4-3 og internkontrollforskriften §§ 4–5 krever systematisk HMS-arbeid, kartlegging, risikovurdering, dokumenterte tiltak og medvirkning. Dette er **ikke** et generelt påbud om én årlig spørreundersøkelse. [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-02](https://www.arbeidstilsynet.no/regelverk/forskrifter/internkontrollforskriften)
- **[Lov/forskrift]** Fra **1. januar 2026** er forskrift om utførelse av arbeid, andre del kap. **1A** (psykososialt arbeidsmiljø) med § 1A-2 om kartlegging/risikovurdering og § 1A-3 om tiltak presisert. Nye kap. 2A/3A gjelder blant annet trakassering og vold/trusler. Arbeidstilsynet presiserer at endringene tydeliggjør allerede gjeldende arbeidsgiverplikter. **Ikke bland kapittel 2A i forskriften med kapittel 2 A om varsling i loven.** [K6-03](https://www.arbeidstilsynet.no/regelverk/forskrifter/forskrift-om-utforelse-av-arbeid/) · [K6-04](https://www.arbeidstilsynet.no/arbeidsmiljo/psykososialt-arbeidsmiljo)
- **[Myndighetsveiledning]** Arbeidstilsynet nevner arbeidsmiljøundersøkelser, vernerunder, avviksmeldinger og samtaler som **mulige kilder**, ikke obligatoriske spesifikke verktøy. [K6-04](https://www.arbeidstilsynet.no/arbeidsmiljo/psykososialt-arbeidsmiljo)

##### A6-02. GDPR og innsamling

- **[Lov/forskrift]** Identifiserbare opplysninger krever et relevant behandlingsgrunnlag etter GDPR artikkel **6** og formålsbegrensning/dataminimering i artikkel **5**. Helseopplysninger og andre særlige kategorier krever i tillegg vurdering av artikkel **9**. Oppfyll også informasjons-/innsynsplikter etter artikkel **12–15**, tilgang og sikkerhet etter artikkel **32**, og artikkel **28** ved databehandler. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-07](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/)
- **[Lov/forskrift]** Samtykke er **ikke automatisk** egnet grunnlag i ansettelsesforhold på grunn av ubalansen mellom partene; det må være reelt frivillig. Om det brukes, må vilkårene faktisk være oppfylt. Nødvendighet for arbeidsgivers lovpålagte HMS-plikter kan peke mot andre grunnlag, men konkret hjemmels-/formålsvurdering kreves. For offentlig myndighetsutøvelse er art. 6(1)(f) ikke tillatt som grunnlag; det følger ikke at en kommunal arbeidsgiver aldri kan vurdere bokstav f i en annen kapasitet. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-22](https://lovdata.no/nav/lov/2018-06-15-38/kapii)
- **[Lov/forskrift]** Bruk av ekstern undersøkelsesplattform krever konkret rolleavklaring; dersom leverandør er databehandler, kreves databehandleravtale (artikkel 28). Personvernkonsekvensvurdering (DPIA, artikkel 35) kreves ved sannsynlig høy risiko, ikke generelt for alle undersøkelser. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-08](https://www.datatilsynet.no/rettigheter-og-plikter/virksomhetenes-plikter/vurdering-av-personvernkonsekvenser/)
- **[Myndighetsveiledning]** Pseudonyme respondent-ID-er er fortsatt personopplysninger hvis noen med rimelighet kan koble dem til personer. Et minimumsantall i en rapport er **ikke bevis** for faktisk anonymitet. [K6-20](https://www.datatilsynet.no/globalassets/global/dokumenter-pdfer-skjema-ol/regelverk/veiledere/anonymisering-veileder-041115.pdf) · [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38)

##### A6-03. Avvik, vold og varsling

- **[Lov/forskrift]** Internkontrollforskriften § 5 nr. 7 krever dokumenterte rutiner for å avdekke, rette opp og forebygge overtredelser. Arbeidstilsynet anbefaler å registrere nestenulykker. Registre over arbeidsrelatert skade/sykdom har særskilte krav, og alvorlige hendelser kan utløse egen meldeplikt. Dette er forskjellig fra «alt er varsling». [K6-02](https://www.arbeidstilsynet.no/regelverk/forskrifter/internkontrollforskriften) · [K6-12](https://www.arbeidstilsynet.no/hms/avvik-og-avvikshandtering/) · [K6-21](https://www.arbeidstilsynet.no/hms/roller-i-hms-arbeidet/arbeidsgiver/registrere-skader-og-sykdom/)
- **[Lov/forskrift]** Arbeidsmiljøloven kapittel **2 A**, særlig § 2 A-1 (kritikkverdige forhold), § 2 A-3 (tilstrekkelig undersøkelse innen rimelig tid), § 2 A-4 (forbud mot gjengjeldelse) og § 2 A-6 (skriftlige rutiner ved jevnlig minst **5** arbeidstakere, også færre ved behov). Ytring kun om eget arbeidsforhold er ikke automatisk varsling med vern etter dette kapitlet. [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K6-09](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/virksomheten-skal-ha-rutiner-for-intern-varsling/)
- **[Myndighetsveiledning]** Også **anonyme** varsler må håndteres. Internt varslingsmottak må ikke love absolutt anonymitet eller innsynsfrihet; § 2 A-7 om særskilt taushetsplikt gjelder varsling til ekstern offentlig tilsynsmyndighet eller annen offentlig myndighet. Innsyn/partsrettigheter må vurderes konkret for den interne varslingssaken. [K6-10](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/ansvar-rettigheter-og-roller/) · [K6-11](https://www.arbeidstilsynet.no/arbeidsmiljo/varsling/slik-bor-arbeidsgiver-handtere-varsling/) · [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/)

##### A6-04. Samtaler, pulsmåling og kompetanse

- **[Lov/forskrift]** Referater fra medarbeidersamtaler som kan knyttes til en ansatt er personopplysninger; formål, tilgang, innsyn, retting og sletting/lagring må vurderes. Arbeidsmiljøloven pålegger ikke generelt et bestemt antall medarbeidersamtaler per år. [K6-05](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K6-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/)
- **[Bransjepraksis]** KS **10-FAKTOR** bruker svarskala 1–5 og sikter mot organisasjonsutvikling. STAMI **MUST** er laget for statlig tariffområde og har en **37-spørsmåls kjerne** med valgfrie moduler i nyere versjoner. Disse er **ikke** lovhjemmel for lokal innsamling og har **ikke** direkte sammenlignbar skala eller rapporteringsavtale. [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/) · [K6-16](https://stami.no/vare-tjenester/medarbeiderundersokelsen-i-staten-must/temaomrader-i-must/)
- **[Bransjepraksis]** STAMIs offentlig tilgjengelige **MUST-vilkår versjon 15.01.2024**: under **6 svar** = ingen rapport, **6–9** = bare gjennomsnitt, minst **10** = også fordelinger; enkelte sensitive temaer bare virksomhetsnivå og restriksjoner selv ved n≥10. Dette er et **verktøyeksempel**, ikke en norsk rettslig anonymitetsgrense. Gjeldende avtaleversjon må sjekkes ved bruk. [K6-17](https://static.stami.no/files/MUST/NO_MUST_Vilkaar_150124.pdf)

#### B. Forskjeller mellom sektorer

| Tema | Industri | Privat service/kontor | Kommune |
|:--|:--|:--|:--|
| Relevante risikoområder | [Bransjepraksis] Maskinsikkerhet, kjemi, skift, nestenulykker; forhold avhenger av konkret drift | [Bransjepraksis] Kundekontakt, tidspress, hjemmekontor, organisatorisk arbeidsmiljø | [Bransjepraksis] Tjenestekvalitet, vold/trusler, emosjonelle krav og tidspress i aktuelle enheter |
| Undersøkelse | [Bransjepraksis] Lokalt arbeidsmiljø-/sikkerhetsskjema | [Bransjepraksis] Lokal puls-/medarbeiderundersøkelse | [Bransjepraksis] For eksempel KS 10-FAKTOR; ikke pålagt metode |
| Varsling/HMS | [Lov/forskrift] Samme AML/IK-regler | [Lov/forskrift] Samme AML/IK-regler | [Lov/forskrift] Samme AML/IK-regler + arkiv/offentlighet må vurderes konkret |
| Datagrunnlag | [Antakelse] Skifte- og maskinavvik på teamnivå | [Antakelse] Teamresultater uten digitale aktivitetslogger | [Antakelse] Gruppeaggregater med særskilt smågrupperisiko |
| Behandlingsgrunnlag | [Lov/forskrift] Per formål og behandling | [Lov/forskrift] Per formål og behandling | [Lov/forskrift] Per formål og behandling; myndighetsutøvelse setter egen grense for art. 6(1)(f) |

[Myndighetsveiledning] Støttekilder: [K6-03](https://www.arbeidstilsynet.no/regelverk/forskrifter/forskrift-om-utforelse-av-arbeid/) · [K6-13](https://www.arbeidstilsynet.no/arbeidsmiljo/vold-og-trusler/) · [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/) · [K6-22](https://lovdata.no/nav/lov/2018-06-15-38/kapii).

#### C. Ti fasitspørsmål

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

#### D. Realistiske tall, fordelinger og kildespor

- **[Offisiell statistikk]** LKU-A 2022: omtrent **35 000** trukket i utvalget, om lag **51 %** svarprosent. Dette er en nasjonal, representativ kartlegging med endret metode i 2022, **ikke** forventet svarprosent for museets pulsmåling. Kilde: STAMI NOA LKU-A, 2022. [K6-18](https://noa.stami.no/metode/datakilder/levekarsundersokelsen-om-arbeidsmiljo/)
- **[Bransjepraksis]** KS 10-FAKTOR: **1–5 svarskala**. Dette gir gyldig verdiområde i syntetisk skjema for *dette* instrumentet, ikke en empirisk sannsynlighetsfordeling for ansatte. Publisert KS 2020. [K6-14](https://www.ks.no/fagomrader/arbeidsgiverpolitikk/ledelse-og-organisering/et-vellykket-10-faktor-arbeid/om-10-faktor/)
- **[Bransjepraksis]** MUST-vilkår **n<6**, **6–9**, **n≥10** bestemmer detaljnivå i STAMIs konkrete rapporteringssystem. Tallene er **tekniske rapporteringsregler, ikke svarfrekvenser** og ikke nasjonale anonymitetsgrenser. Vilkårsversjon 15.01.2024; må oppdateres ved reell avtale. [K6-17](https://static.stami.no/files/MUST/NO_MUST_Vilkaar_150124.pdf)
- **[Offisiell statistikk]** STAMI NOA har nærings- og yrkesfordelte LKU-A-indikatorer, eksempelvis jobbkontroll. Uten definert næring/yrke, uttrekk og metode/år finnes det **ingen pålitelig museumsfordeling** å importere. Skal ikke konstrueres. [K6-19](https://noa.stami.no/arbeidsmiljofaktorer/krav-kontroll-og-belonning/jobbkontroll/)
- **[Antakelse]** For museet (168 ansatte/seks avdelinger) skal syntetisk antall inviterte komme fra eksisterende fiktiv bemanningsliste. Svarantall skal holde seg mellom 0 og inviterte. Velg ikke automatisk 51 % fra LKU-A; det ville være en feilaktig overføring fra en annen undersøkelse og populasjon.
- **[Antakelse]** Avviks-, varslings- og medarbeidersamtalerater er **ikke funnet som sammenlignbare nasjonale fordelinger** for denne casen. Bruk scenarioetiketter/parameter som må oppgis eksplisitt, ikke oppdiktede prosenter.

#### E. Forslag til syntetiske data

Det følger **8 maskinlesbare tabellforslag** i `AP6_datasett_forslag.yaml`, med kolonner, datatyper, tillatte verdier, kilder og referanser til ansatt/avdeling/eksisterende kompetanse. Hovedgrep:

1. En katalog over innsamlingsformål, ansvar, grunnlag, tilgang og DPIA.
2. Én adskilt aggregattabell for offentliggjørbare/ledelsesrettede gruppetall. Ingen individuelle svar lagres her.
3. Tiltak fra medarbeidersamtaler, med medarbeider-ID bare der formål krever det.
4. Strukturerte HMS-avvik uten sensitive navn, diagnoser og fritekst.
5. En **separat varslingsprosess** med saksstatus og autorisert rolle; ingen kobling til individuell prestasjon.
6. Dokumenterte kompetansekrav og sertifikatstatus, uten automatisk personrangering.
7. Proveniens/kildeversjon, så rapportutlevering kan spores.

**[Antakelse]** Eksisterende faktiske SQLite-tabellnavn er ikke tilgjengelige; `hr_ansatte` / `hr_avdelinger` / `hr_sertifikater` er **logiske referanser** som må avstemmes før implementering. Ingen reelle eller syntetiske identifiserbare medarbeidersvar, varseltekster eller helsedata er generert.

#### F. Faste regler og fallback

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

#### G. Grensetilfeller og usikkerhet (djevelens advokat)

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

## Område 7 – Likelønn ved ulike kunstfaglige stillinger

### Museum og kunst – anvendelse i øvingscaset

[Lov/forskrift] Sammenlign ikke bare identiske stillingstitler. For relevant virksomhet må arbeid av **lik verdi** vurderes ved lønnskartlegging og redegjørelse, med dokumenterte kriterier. [Likestillings- og diskrimineringsloven § 26](https://lovdata.no/lov/2017-06-16-51/rdkn/a4).

[Antakelse] Museumsfaglige eksempler: registrering/samling, konservering, formidling, publikum, teknikk, økonomi. Én prosjektstilling kan omfatte flere funksjoner; klassifisering må gjøres før aggregert lønnsanalyse. Ikke bruk besøkstall eller antall kunstverk som forklaring på lønnsforskjell uten analyse.

[Tariffavtale] Forskjeller mellom tariffgrupper, lokal lønn og stillingsinnplassering må dokumenteres, ikke brukes som automatisk bevis på saklig lønnsforskjell. [Virke](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/landsoverenskomst-for-museer-og-andre-kulturinstitusjoner/).

### Opprinnelig sektorsammenligning og A–G (AP7, bevart)

#### AP7 – Likelønn og redegjørelse (område 7)

**Status:** Arbeidspakke AP7 alene, kontrollert 20.10.2026. **Sammenligning:** industri, privat service/kontor og kommune. **Viktige avgrensninger:** Dette er et verifisert grunnlag for syntetiske øvingsdata og regler; det fastslår ikke diskriminering hos personer eller konkrete arbeidsgivere. Tidligere arbeidspakker er ikke endret. **Kildespor:** K7-01–K7-18 i `AP7_kilder.md`.

#### Sammendrag (maks 10 linjer)

1. [Lov/forskrift] Alle arbeidsgivere har aktivitetsplikt etter § 26 første ledd; utvidet aktivitet, lønnskartlegging annethvert år og redegjørelse gjelder alle offentlige virksomheter og private med **mer enn 50** ansatte.
2. [Lov/forskrift] Private med 20–50 ansatte omfattes av den utvidede plikten når en av arbeidslivets parter i virksomheten krever det; færre enn 20 har generell aktivitetsplikt.
3. [Lov/forskrift] § 34 gjelder **lik lønn for samme arbeid eller arbeid av lik verdi**, også på tvers av fag og tariffavtaler innen virksomheten.
4. [Myndighetsveiledning] Kartlegging omfatter alle ansatte, kjønnsfordeling, stillingsgrupper og flere lønnskomponenter; lønnsdata for deltid må gjøres sammenlignbare.
5. [Lov/forskrift] Redegjørelsen er offentlig, men ikke identifiserende; innsyn i underliggende resultat kan likevel følge av § 26 a med nødvendighets- og taushetsvilkår.
6. [Offisiell statistikk] SSB: kvinner hadde **87,9 %** av menns gjennomsnittlige månedslønn per heltidsekvivalent i **2025**; medianforholdet var **93,4 %**.
7. [Antakelse] Lønnsforskjell er et **undersøkelsessignal**, aldri maskinell diskrimineringsdom; sektor, fag, ansvar, arbeidstid og tillegg kan forklare noe, men må dokumenteres.
8. [Myndighetsveiledning] Likelønnsdirektiv (EU) 2023/970 var per kontroll **ikke innlemmet i EØS**; EUs frist 7. juni 2026 er ikke en norsk ikrafttredelsesdato.

#### A. Regler og kildegrunnlag

##### A7-01. Hvem er omfattet?

- **[Lov/forskrift]** Likestillings- og diskrimineringsloven **§ 26 første ledd**: alle arbeidsgivere, også små industribedrifter, private kontorer og kommuner, skal jobbe aktivt, målrettet og planmessig for likestilling og mot diskriminering. [K7-01](https://lovdata.no/lov/2017-06-16-51/rdkn/a4).
- **[Lov/forskrift]** **§ 26 andre ledd**: den lovbestemte firetrinnsmetoden og lønnskartlegging minst annethvert år gjelder offentlige virksomheter uansett størrelse og private arbeidsgivere som jevnlig har **mer enn 50** ansatte. Privat med **20–50** ansatte får samme utvidede plikt hvis **en av arbeidslivets parter på arbeidsplassen** krever det. Selve juridiske arbeidsgiveren, ikke bransjen, er vurderingsenheten. [K7-01](https://lovdata.no/lov/2017-06-16-51/rdkn/a4) · [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/).
- **[Myndighetsveiledning]** Bufdir tar utgangspunkt i årsgjennomsnitt ved varierende antall ansatte. For en fiktiv virksomhet med **168 ansatte** er størrelseskriteriet oppfylt dersom den er en privat, juridisk arbeidsgiver; kommunen omfattes uansett antall. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/).
- **[Lov/forskrift]** **§ 26 a** gir redegjørelsesplikt for virksomhetene under § 26 andre ledd. **§ 26 b** gjelder dokumentasjon og innsyn i likestillingsarbeid. **§ 26 c** om styrets forankring i AS/ASA; regnskapslovens tidligere § 3-3 c-henvisning er en kjent inkurie, ikke bevis for at § 26 c bortfaller. [K7-02](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_4) · [K7-15](https://www.regjeringen.no/no/dokumenter/prop.-106-l-20252026/id3166344/?ch=8).

##### A7-02. Hva skal kartlegges og redegjøres?

- **[Lov/forskrift]** § 26 og § 26 a: kartlegging av lønnsforhold etter kjønn og **ufrivillig deltid minst annethvert år**. Redegjørelse årlig for faktisk kjønnslikestilling og aktivitet; redegjørelsen publiseres i årsberetning eller annet tilgjengelig dokument med henvisning der loven krever det. [K7-01](https://lovdata.no/lov/2017-06-16-51/rdkn/a4) · [K7-02](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_4).
- **[Myndighetsveiledning]** Bufdirs presisering: årlig kartlegges/redegjøres for kjønnsbalanse, deltid, midlertidighet og foreldrepermisjon. Minst annethvert år lønn og ufrivillig deltid; ved år uten ny lønnskartlegging kan siste kartlegging henvises til. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/).
- **[Lov/forskrift]** § 34: vurder likt arbeid og arbeid av lik verdi ut fra blant annet krav til kompetanse, anstrengelse, ansvar og arbeidsforhold. Forskjellige tariffområder er ikke i seg selv et unntak. Dette er en vurdering av sammenlignbare jobber **innen samme virksomhet**. [K7-05](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_5).
- **[Myndighetsveiledning]** Lønnskartleggingen omfatter alle ansatte og stillingsgrupper, basert på **likt arbeid og arbeid av lik verdi**, i samarbeid med ansattes representanter. Sammenlign kvinner og menn på hvert nivå og samlet; gi ansatte reell mulighet til sammenligning med gruppens gjennomsnitt. Inkluder avtalt lønn, uregelmessige tillegg, bonuser, overtid og skattepliktige naturalytelser (samlet eller spesifisert). Deltid omregnes slik at lønnen er sammenlignbar. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/) · [K7-04](https://ldo.no/bli-betre-pa-likestilling-og-mangfald/aktivitets-og-redegjorelsesplikt/).
- **[Lov/forskrift]** **§ 32**: ved mistanke om lønnsdiskriminering kan en ansatt kreve skriftlig opplysning om lønnsnivå og kriterier for sammenligningsperson(er). Mottaker skal undertegne taushetserklæring; arbeidsgiver skal informere den berørte som opplysningene gjelder. [K7-05](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_5).

##### A7-03. Personvern og automatisering

- **[Lov/forskrift]** § 26 a: offentlig redegjørelse skal være anonymisert. Berettiget innsyn i resultater kan gis selv om anonymisering ikke er mulig, når det er **nødvendig** og med lovens taushetskrav; dette er **ikke** allmenn publiseringsrett. [K7-02](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_4).
- **[Myndighetsveiledning]** Bufdir angir at grupper med færre enn **fem av ett kjønn** ikke bør offentliggjøre forskjeller i kroner; også prosent kan avsløre personer ved små grupper. Dette er en veiledning for lønnskartlegging, ikke universell GDPR-anonymitetsregel og ikke et unntak fra lovfestet innsyn. Automatisk publisering av smågruppeceller sperres i modellforslaget. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/) · [K7-04](https://ldo.no/bli-betre-pa-likestilling-og-mangfald/aktivitets-og-redegjorelsesplikt/).
- **[Lov/forskrift]** Personopplysningsloven/GDPR: behandlingsgrunnlag, dataminimering, formålsbegrensning, tilgangsstyring og dokumentasjon ved håndtering av identifiserbare lønnsdata. [K7-06](https://lovdata.no/dokument/NL/lov/2018-06-15-38) · [K7-07](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/).
- **[Tariffavtale]** **Ikke funnet:** En nasjonal tariffbestemmelse som overstyrer lovens generelle likelønns- eller ARP-plikter. Industriens/privates/KS' lønnsdannelse og stillingskoder er viktige **forklaringsvariabler**, men det er ikke verifisert én felles tariffpunktliste som gjelder alle. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/) · [K7-05](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_5).

##### A7-04. EU-direktiv under utvikling

- **[Myndighetsveiledning]** Kultur- og likestillingsdepartementet og EFTA viser direktiv (EU) **2023/970** som EØS-relevant, men uten innlemmelsesbeslutning. **EU-fristen 07.06.2026 gjelder ikke Norge**; derfor ingen automatisk norsk regel for f.eks. ny direktivbasert rapporteringsfrekvens per 20.10.2026. Overvåk framtidige lovendringer. [K7-13](https://www.regjeringen.no/no/tema/likestilling-og-mangfold/likestilling-og-inkludering/om-likelonnsdirektivet/id3140297/) · [K7-14](https://www.efta.int/eea-lex/32023l0970).

#### B. Forskjeller mellom sektorene

| Tema | Industri | Privat service/kontor | Kommune |
|---|---|---|---|
| Generell aktivitetsplikt | Ja, alle størrelser | Ja, alle størrelser | Ja, alle størrelser |
| Utvidet ARP og lønnskartlegging | Privat >50 automatisk; 20–50 ved krav fra part | Samme som industri | Offentlig arbeidsgiver: uansett størrelse |
| Lønnsmodell i analysen | Tariff/minstelønn, akkord, skift og tillegg kan variere | Bonus, provisjon, individuelt avtalt lønn og tillegg kan variere | Lønnskapitler, stillingskode, sentrale/lokale tillegg og turnus |
| Sammenligningsgrupper | Kompetanse, anstrengelse, ansvar og arbeidsforhold; ikke tariff alene | Samme kriterier; ta hensyn til bonusmodeller | Samme kriterier; ulike fag/stillingskoder kan være av lik verdi |
| Offentlighet | Privat: personvern og lovbestemt innsyn | Privat: personvern og lovbestemt innsyn | I tillegg vurdere offentleglova; ikke automatisk publisering av individlønn i ARP-redegjørelse |
| Datagrunnlag | Stillingsnivå, fag, akkord, timer, overtids-/skifttillegg | Individuell lønn, timer, provisjon, bonus | Stillingskode, kapittel, ansiennitet, stillingsprosent, tillegg |

**Kildekategori:** Første to rader [Lov/forskrift] (K7-01–02), tredje og siste rader [Bransjepraksis] som modellvariabler (K7-03–04), øvrige [Lov/forskrift]/[Myndighetsveiledning]. Ingen lokal KS/NHO/Virke-tariffpunkt er blitt kontrollert i AP7; variablene er **ikke** normative satser.

#### C. Ti spørsmål med fasit

| ID | Spørsmål / svar (kort) | Sektor | Vanskelig? |
|---|---|---|---|
| Q-7-01 | **Har alle bedrifter plikt til lønnskartlegging annethvert år?** Nei: alle har generell aktivitetsplikt, men den spesifiserte kartleggingsplikten har størrelse-/sektorkrav. | alle | ja: skiller to pliktnivåer |
| Q-7-02 | **Vi har 50 ansatte: må vi kartlegge lønn annethvert år?** Ikke automatisk som privat bedrift; kravet kan utløses av en arbeidslivspart. Kontroller om offentlig arbeidsgiver. | privat | ja: grenseverdien 50 |
| Q-7-03 | **Gjelder plikten en kommunal enhet med 12 ansatte?** Ja for offentlig arbeidsgiver. Avklar juridisk arbeidsgiver og rapporteringsnivå. | kommune | ja: enhet vs arbeidsgiver |
| Q-7-04 | **Må bonuser, helgetillegg og overtid tas med?** Ja, lønnskartlegging skal omfatte ulike lønnskomponenter; kartlegg også skattepliktige goder. | alle | nei |
| Q-7-05 | **Er to jobber med forskjellige tariffavtaler umulige å sammenligne?** Nei. § 34 åpner for arbeid av lik verdi på tvers av fag og tariff. | industri | ja: tariff er ikke unntak |
| Q-7-06 | **Er 8 % lønnsgap bevis på ulovlig diskriminering?** Nei. Undersøk arbeidsoppgaver, kvalifikasjoner, tillegg og saklige forklaringer; vurder konkret. | alle | ja: deskriptivt mot årsak |
| Q-7-07 | **Kan vi publisere kroner og prosent for en gruppe med én kvinne og to menn?** Ikke automatisk. Vurder identifisering; Bufdir fraråder kronesummer ved færre enn fem av ett kjønn. | alle | ja: smågruppepersonvern |
| Q-7-08 | **Har ansatte krav på sammenligningsinformasjon om lønn?** Ja på ulike rettslige grunnlag. § 26 a gir særskilt innsyn; § 32 gjelder ved mistanke. Nødvendighet og taushetsplikt må vurderes. | alle | ja: offentlig rapport vs konkret innsyn |
| Q-7-09 | **Skal deltidslønn sammenlignes mot heltidslønn uten justering?** Nei, gjør lønnsdata sammenlignbare, bl.a. med heltidsekvivalenter; se arbeidstid og tillegg separat. | kommune | nei |
| Q-7-10 | **Må norsk arbeidsgiver allerede følge EUs frist 7. juni 2026?** Nei, fristen gjelder EU-medlemsstater; direktivet er ikke dokumentert innlemmet i EØS per kontroll. | alle | ja: framtidig regelverk |

Alle svar finnes også i `AP7_fasit_sporsmal.csv`, med kilde-URL og forklaring for vanskelige tilfeller.

#### D. Realistiske tall, fordelinger og kildespor

- **[Offisiell statistikk] D7-01, SSB 2025 (tabell 11419):** Kvinners gjennomsnittlige månedslønn per heltidsekvivalent **57 690 kr** og menns **65 610 kr**; **87,9 %** kvinners/menns lønn, dvs. et gap på **12,1 % av menns nivå**. Dette er et nasjonalt gjennomsnitt, ikke diskrimineringsandel og ikke en museumpopulasjon. [K7-09](https://www.ssb.no/statbank/table/11419/) · [K7-12](https://www.bufdir.no/statistikk-og-analyse/kjonnslikestilling/okonomi-kjonn/).
- **[Offisiell statistikk] D7-02, SSB 2025:** Medianlønnsforhold kvinner/menn **93,4 %**, dvs. gap **6,6 %**. Gapet endrer størrelse etter mål (gjennomsnitt/median). [K7-11](https://www.ssb.no/arbeid-og-lonn/lonn-og-arbeidskraftkostnader/statistikk/lonn/artikler/slik-kan-lonnsforskjellen-mellom-kvinner-og-menn-forklares).
- **[Offisiell statistikk] D7-03, SSB 2025, heltidsansatte (ikke alle heltidsekvivalenter):** Privat sektor kvinner **61 970** og menn **67 740 kr/måned**; kommuneforvaltningen kvinner **56 030** og menn **59 320 kr/måned**. Kilde: SSBs kjønnssammenstilling, **avgrenset til heltidsansatte**. Må ikke blandes med D7-01. [K7-08](https://www.ssb.no/statbank/table/11418/) · [K7-16](https://www.ssb.no/befolkning/faktaside/likestilling).
- **[Offisiell statistikk] D7-04, kilde til fordelinger:** SSB **tabell 11418** har statistikkmål bl.a. **gjennomsnitt, median, nedre og øvre kvartil** etter yrke, sektor, kjønn og arbeidstid for 2015–2025. **11419** gir næringsdimensjon; **14756/14757** viser lønnsintervaller fordelt på sektor/næring, kjønn, heltid/deltid og yrke. Kildene gir grunnlag for faktiske fordelinger ved senere målrettet uttrekk. **Disse detaljerte gruppefordelingene er ikke hentet ut her**; ingen kunstige skjevhetsfordelinger er oppgitt. [K7-08](https://www.ssb.no/statbank/table/11418/) · [K7-09](https://www.ssb.no/statbank/table/11419/) · [K7-10](https://www.ssb.no/statbank/table/14756/) · [K7-17](https://www.ssb.no/statbank/table/14757/).
- **[Myndighetsveiledning] D7-05:** Bufdir oppgir at sektorsammenligning krever avklaringer om stillings-/yrkesfordeling, arbeidstid og lønnsart. **87,9 % nasjonalt er ikke en generatorverdi for museum med 168 ansatte**. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/).

**Designregel:** For å lage en realistisk syntetisk fordelingsmodell må man først velge kompatibel SSB-tabell, næringskode og lønnsdefinisjon; deretter kalibrere mot fordeling, ikke kun gjennomsnittet. Ingen oppdiktede kjønnsbestemte lønnsforskjeller genereres i AP7.

#### E. Forslag til syntetiske data (ikke faktiske rader)

Detaljer per felt, datatype, tillatte verdier, fremmednøkler og kilde finnes i `AP7_datasett_forslag.yaml`. Foreslåtte tabeller:

1. `hr_arp_virksomhet` – juridisk arbeidsgiver, sektor, periode, gjennomsnittlig antall ansatte og dokumentert krav fra part.
2. `hr_arp_kartlegging` – rapportperiode, status, aktivitet, dato, samarbeidsprosess og signering.
3. `hr_arp_stillingsgrupper` – kompetanse, anstrengelse, ansvar og arbeidsforhold med manuell gruppebegrunnelse.
4. `hr_arp_stillingsplassering` – ansatt–arbeidsforhold–gruppe med gyldighetsperiode (hindrer dobbelttelling).
5. `hr_arp_lonnsgrunnlag` – lønnsarter, sammenlignbar lønn/FTE, komponent og periode, knyttet til eksisterende ansatt-/lønnstrinn-/vaktkilder.
6. `hr_arp_aggregat` – aggregert kjønnssammensetning og lønnsforskjell per gruppe; egen publiseringsstatus.
7. `hr_arp_arlig_kjonnsbalanse` – årlige opptellinger for deltid, midlertidighet, foreldrepermisjon.
8. `hr_arp_ufrivillig_deltid` – dokumentert kartlegging annenhvert år uten private helsedetaljer.
9. `hr_arp_innsyn` – rettsgrunnlag, mottakerrolle, nødvendighetsvurdering og taushetserklæring; ingen rå lønn i loggen.
10. `hr_arp_tiltak` – funn, årsaksanalyse, ansvar, tiltak og evaluering; ikke individstempling.

**[Antakelse]** Bruk `hr_ansatte.ansatt_id` og `hr_avdelinger.avdeling_id` som **logiske koblingsnavn**, ikke påstått faktisk SQLite-skjema. `Kjønn` for lovens todelte rapporteringskategori er ikke en oppfordring til å konstruere følsomme opplysninger om kjønnsidentitet; håndter eventuell annen/ukjent kategori etter lokal datadokumentasjon, lovformål og personvernvurdering. Lønnskartlegging må ta med arbeidsforhold og full-/deltid uten at samme ansatt feilaktig regnes flere ganger totalt.

#### F. Faste regler og fallback

**Kjernen er deterministiske kontrollsignaler, ikke juridisk vedtak:**

- `R-7-01..03`: pliktnivå basert på **offentlig/privat**, **antall ansatte** og **krav fra en part**. **50 akkurat** gir ikke automatisk privat utvidet plikt.
- `R-7-04..06`: krav til årlig redegjørelse og kartlegging av lønn/ufrivillig deltid minst annethvert år (med sist kartlagt dato).
- `R-7-07..10`: manglende samarbeid, gruppedefinisjon, alle relevante lønnsarter og FTE-korrigering gir datakvalitets-/etterlevelsessignal.
- `R-7-11..14`: smågruppe-/individopplysninger gir **publiseringsstopp og manuell kontroll**, ikke et offentlig avslag på lovlig innsyn.
- `R-7-15..20`: innsyn, anonymitet, utredning av lønnsforskjell, juridisk arbeidsgiver og EU-regelstatus.
- `FB-7-01..10`: én fallback per `Q-7-xx`. Konklusjonen er «manglende opplysninger; oppgi hva som må avklares»; aldri beregn skyld eller diskrimineringsdom automatisk.

**Teknisk merknad:** Operatorer i CSV (`eq`, `gt`, `and`, `missing`, `days_since_gt`, `fallback`) er **spesifikasjon** som må tolkes deterministisk og testes av regelmotoren før bruk. Ingen vilkårlige lønnsgapgrenser (f.eks. > 5 %) er satt som lovbruddsterskel.

#### G. Grensetilfeller og usikkerhet (djevelens advokat)

1. **[Lov/forskrift] G7-01 – 50 ansatte.** Ordlyden «mer enn 50» gir et annet utfall enn «50 eller flere» i privat sektor. For 20–50 avklares krav fra arbeidslivspart; uklar faktisk årsmiddel blir **ikke automatisk lovbrudd**. **Status:** Godt dokumentert; **sikkerhet:** høy. Metode M01/M04. [K7-01](https://lovdata.no/lov/2017-06-16-51/rdkn/a4).
2. **[Lov/forskrift] G7-02 – juridisk status.** Kommunalt eid AS er ikke automatisk en kommunal administrativ enhet. Offentligrettslig status og juridisk arbeidsgiver må fastslås; ikke klassifiser etter museumsnavn eller eier alene. **Status:** Usikkert uten selskapsopplysninger; **sikkerhet:** middels. Metode M04. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/).
3. **[Myndighetsveiledning] G7-03 – stillingskoder.** Samme STYRK-08 eller KS-kode er ikke nødvendigvis tilstrekkelig for arbeid av lik verdi; forskjellige koder kan være sammenlignbare. Gruppering må begrunnes med faktisk arbeid. **Status:** Godt dokumentert prinsipp; **sikkerhet:** høy. Metode M01. [K7-04](https://ldo.no/bli-betre-pa-likestilling-og-mangfald/aktivitets-og-redegjorelsesplikt/).
4. **[Lov/forskrift] G7-04 – forskjell ≠ diskriminering.** Forskjell kan ha flere forklaringer og kan være lovlig eller ulovlig. Kontrollmotor skal peke på behov for årsaksvurdering, ikke utstede dom. **Status:** Godt dokumentert; **sikkerhet:** høy. Metode M10. [K7-05](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_5).
5. **[Myndighetsveiledning] G7-05 – k-fellen.** «Færre enn fem» er veiledningsnivå for publisering av lønnsforskjeller i kroner, ikke universal anonymitetsgaranti. Ett kjønn alene i gruppe, små totalsummer og differansekoblinger kan identifisere personer selv i prosent. **Status:** Godt dokumentert; **sikkerhet:** høy. Metode M04/M10. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/).
6. **[Lov/forskrift] G7-06 – innsyn vs publisering.** § 26 a-informasjon til berettiget mottaker kan kreve taushetserklæring også når aggregatet ikke lar seg anonymisere. Ikke la offentlig publiseringsfilter blokkere lovlig lukket innsyn. **Status:** Godt dokumentert; **sikkerhet:** høy. Metode M01. [K7-02](https://lovdata.no/nav/lov/2017-06-16-51/KAPITTEL_4).
7. **[Offisiell statistikk] G7-07 – definisjonsmismatch.** SSBs månedslønn ekskluderer overtid og naturalytelser, mens lønnskartleggingen omfatter slike ytelser. SSBs 87,9 % kan derfor ikke brukes som virksomhetens forventede ARP-resultat. **Status:** Godt dokumentert; **sikkerhet:** høy. Metode M04/M09. [K7-12](https://www.bufdir.no/statistikk-og-analyse/kjonnslikestilling/okonomi-kjonn/).
8. **[Myndighetsveiledning] G7-08 – EU-fristen.** Direktivets EU-frist er ikke dokumentert som norsk plikt. EFTA viser fortsatt ventende innlemmelse. **Status:** Godt dokumentert per dato; **sikkerhet:** høy. Metode M09. [K7-14](https://www.efta.int/eea-lex/32023l0970).
9. **[Antakelse] G7-09 – ufrivillig deltid.** Stillingsprosent alene viser ikke om arbeidstakeren ønsker mer arbeid. Kartlegg behov på måte som ikke overfører privat helseinformasjon til analyse. **Status:** Sannsynlig metodisk forbehold; **sikkerhet:** middels. Metode M04. [K7-03](https://www.bufdir.no/fagstotte/produkter/aktivitets__og_redegjorelsesplikt_for_arbeidsgivere/).
10. **[Bransjepraksis] G7-10 – tariff og marked.** Industrielle skift-/akkordtillegg, private bonusordninger og kommunale lønnskapitler kan påvirke kartlagte gap. Eksakt tariffpunkt og stillingsgruppe må dokumenteres før en gitt lønnsforskjell forklares bort. **Status:** Usikkert i konkret sak; **sikkerhet:** middels. Metode M10.
11. **[Offisiell statistikk] G7-11 – fordelinger.** Reell statistisk fordeling varierer mellom yrker, næring, heltid/deltid, gjennomsnitt/median. Et nasjonalt tall er ikke direkte generatorparameter per avdeling. **Status:** Godt dokumentert; **sikkerhet:** høy. Metode M04. [K7-08](https://www.ssb.no/statbank/table/11418/) · [K7-10](https://www.ssb.no/statbank/table/14756/).
12. **[Lov/forskrift] G7-12 – personalopplysning.** En ARP-database skal ikke generere kjønnskodet lønn, smågruppeaggregater eller intern dokumentasjon for sanksjoner uten kvalitetssikret rolle-/tilgangsmodell. **Status:** Sannsynlig som sikker datadesign; **sikkerhet:** middels. Metode M10. [K7-06](https://lovdata.no/dokument/NL/lov/2018-06-15-38).

##### Ikke funnet / åpne punkter

- **Ikke funnet:** Ett nasjonalt tariffpunkt i KS, NHO eller Virke som alene gir gyldig gruppedefinisjon av arbeid av lik verdi på tvers av virksomheter. Søk: Bufdir, LDO, lovens § 34; tariffavtalenes detaljer ikke kontrollert i AP7.
- **Ikke funnet:** Virksomhetsspesifikk lønnsfordeling per kjønn og stillingsgruppe for et kunstmuseum med 168 ansatte. Søk: SSB tabell 11418, 11419, 14756, 14757. Nasjonale data er **ikke** lokalt facit.
- **Ikke funnet:** Dokumentasjon på at EU-direktiv 2023/970 har trådt i kraft som norsk lov per 20.10.2026. Søk: Regjeringen, EFTA. Registreres som framtidsrisiko – ikke operativ norsk regel.
- **Uavklart:** Nærmere rettslig status for kommunalt eid museumsforetak, lokal gruppestruktur og faktisk dataskjema; krever arbeidsgiverens organisasjonsform og lønns-/stillingsregistre.

**AP7 stoppunkt:** Leveransen omfatter bare område 7. Ikke gå videre til AP8 før ny eksplisitt «neste».

## Område 8 – Kunstnere, eksterne, prosjekt- og sesongstillinger

### Museum og kunst – anvendelse i øvingscaset

[Myndighetsveiledning] Skill arbeidsforhold (ansatt), ekstern oppdragstaker og frivillig **etter faktisk tilknytning**, ikke bare betalingsmåte eller tittel. Arbeidstilsynet omtaler særskilt grensen for frivilliges status og HMS-ansvar. [Arbeidstilsynet](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/frivillig-arbeid/).

[Antakelse] Museumsdrift kan omfatte sesongvertskap, prosjektkurator, utstillingsmontør, konservator, ekstern formidler og kunstner på oppdrag. Ansettelsesform, midlertidighetsgrunnlag, arbeidsavtale, innleie og rettigheter må dokumenteres per sak. Dette er eksempler, ikke påviste ansatte i øvingsmuseet. [Arbeidstilsynet](https://www.arbeidstilsynet.no/lonn-og-ansettelse/arbeidsavtale/).

[Bransjepraksis] Planlegg overgang mellom prosjekter med kunnskapsoverlevering om verk, magasiner, tilstandsrapporter og sikkerhetstilgang. Opphavsrett/utstillingsavtale er en egen avtaleproblemstilling, ikke et HR-lønnstrinn. [Kulturdirektoratet](https://www.kulturdirektoratet.no/fag/museum-og-kulturarv/museumsutvikling/samlingsforvaltning), [Kopinor](https://kopinor.no/om-opphavsrett/).

### Opprinnelig sektorsammenligning og A–G (AP8, bevart)

#### AP8 – Livsløp: rekruttering til oppsigelse (område 8)

**Omfang:** Kun AP8, ført i forlengelse av AP7. Kontroll: **20.10.2026**. De eksisterende AP2–AP7-filene er ikke endret. **Formål:** grunnlag for syntetiske øvingsdata og deterministiske indikatorer, ikke individuell juridisk avgjørelse. Primærkildene er identifisert K8-01–K8-22 i `AP8_kilder.md`.

#### Sammendrag (maks 10 linjer)

1. [Lov/forskrift] **Fast og heltid er hovedregelen**; midlertidighet og deltid krever egne vurderinger etter arbeidsmiljøloven kapittel 14. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
2. [Lov/forskrift] Skriftlig arbeidsavtale senest innen **sju dager** ved mer enn én måneds varighet, ellers umiddelbart. Fra 01.07.2024. [K8-02](https://www.arbeidstilsynet.no/lonn-og-ansettelse/arbeidsavtale/).
3. [Lov/forskrift] **Prøvetid høyst seks måneder**; ved midlertidig ansettelse maksimalt halvparten av ansettelsestiden. Ny prøvetid hos samme arbeidsgiver krever konkret vurdering. [K8-03](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/).
4. [Lov/forskrift] Rekruttering er omfattet av diskrimineringsforbud; lovens § 30 begrenser hvilke opplysninger arbeidsgiver kan hente inn. [K8-08](https://lovdata.no/lov/2017-06-16-51/%C2%A730).
5. [Lov/forskrift] Nødvendig, risikotilpasset sikkerhetsopplæring skal gis; **30/60/90-dagers onboarding er ingen generell lovfrist**. [K8-10](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/generelle-krav-til-opplaring/).
6. [Lov/forskrift] Oppsigelse fra arbeidsgiver krever saklig grunn, drøfting og formkrav; prøvetid er ikke fritt oppsigelsesrom. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
7. [Tariffavtale] KS Hovedavtale gjelder **2026–2029**, NHO–LO Hovedavtale **2026–2029**; partsdekning og lokale avtaler må avklares før vilkår brukes. [K8-11](https://www.ks.no/fagomrader/lonn-og-tariff/hovedavtalen/hovedavtalen-1.1.2026--31.12.2029) · [K8-12](https://lovdata.no/dokument/TARH/tariff/tarh-1/KAPITTEL_6-1-1).
8. [Offisiell statistikk] KS/PAI 2025: **12,4 %** gikk ut av kommunal sektor på ett år; for fastlønte **10,0 %**. Ingen av disse er et museumstall. [K8-14](https://www.ks.no/fagomrader/statistikk-og-analyse/turnover/kommuner-og-fylkeskommuner/).
9. [Offisiell statistikk] SSBs **jobbstrømmer** og **sykefravær** beskriver forskjellige størrelser og kan ikke konverteres direkte til virksomhetens turnover. [K8-15](https://www.ssb.no/arbeid-og-lonn/sysselsetting/statistikk/antall-arbeidsforhold-og-lonn/) · [K8-17](https://www.ssb.no/arbeid-og-lonn/arbeidsmiljo-sykefravaer-og-arbeidskonflikter/statistikk/sykefravaer/).
10. [Antakelse] Syntetiske hendelser, prøvetidsrutiner og årsakskoder skal genereres med **kildemerket scenario**, ikke ukildede sannsynligheter.

#### A. Regler med hjemmel, gyldighet og kilde

##### A8-01. Rekruttering og prioritet før utlysning

- **[Lov/forskrift]** Arbeidsmiljøloven **§§ 14-1, 14-1 a, 14-2 og 14-3**: informer om ledige stillinger; fast/heltid som hovedregel; dokumenter og drøft behov for deltid; vurder fortrinnsrett ved nedbemanning og kvalifiserte deltidsansatte før ekstern tilsetting. Reglenes personkrets og vilkår er forskjellige. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K8-07](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/fortrinnsrett-til-utvidet-stilling-for-deltidsansatte/).
- **[Lov/forskrift]** **§ 14-9** tillater midlertidig ansettelse på nærmere bestemte grunnlag, blant annet vikariat og arbeid av midlertidig karakter. Prosjektbetegnelse eller drift med varig bemanningsbehov er ikke i seg selv lovlig hjemmel. Rett til fast ansettelse ved tilstrekkelig lang sammenhengende midlertidighet krever perioder og grunnlag vurdert etter riktig rettsversjon. [K8-04](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/midlertidig-ansettelse/).
- **[Lov/forskrift]** Likestillings- og diskrimineringsloven **§§ 29 og 30**: forbud mot diskriminering under hele ansettelsesprosessen; arbeidsgiver skal som hovedregel ikke innhente opplysninger om bl.a. graviditet/familieplaner, religion, etnisitet, funksjonsnedsettelse og seksuell orientering, med lovens avgrensede unntak for enkelte opplysningstyper. [K8-08](https://lovdata.no/lov/2017-06-16-51/%C2%A730) · [K8-09](https://ldo.no/diskrimineringsgrunnlag/graviditet/).
- **[Lov/forskrift / rettskildeprinsipp]** Kommunal ansettelse omfattes av **ulovfestet kvalifikasjonsprinsipp**. Statsansatteloven er **ikke** den generelle ansettelsesloven for kommunalt ansatte. [K8-20](https://www.regjeringen.no/no/dokumenter/prop.-94-l-20162017/id2547960/?ch=2).
- **[Myndighetsveiledning]** Søkerdata skal ha behandlingsgrunnlag, avgrenset formål, dataminimering og nødvendig lagringstid. Ved rekrutteringsmodell bruk prosess-/statuskoder fremfor innsamling av sensitive kandidatopplysninger. [K8-21](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/) · [K8-22](https://lovdata.no/lov/2018-06-15-38).

##### A8-02. Arbeidsavtale, prøvetid og onboarding

- **[Lov/forskrift]** **§§ 14-5, 14-6 og 14-8**: skriftlig arbeidsavtale; lengre enn en måned senest sju dager etter tiltredelse, kortere varighet eller utleie umiddelbart. Skriftlige endringer senest når endringen trer i kraft. **1. juli 2024** er sentral versjonsdato. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K8-02](https://www.arbeidstilsynet.no/lonn-og-ansettelse/arbeidsavtale/).
- **[Lov/forskrift]** **§ 15-6**: prøvetid må avtales skriftlig, maksimalt seks måneder og ved midlertidig ansettelse maksimalt halvparten av kontraktens varighet. Ved påfølgende arbeidsforhold hos samme arbeidsgiver kan ny prøvetid være begrenset; fraværsforlengelse krever lovens dokumenterte vilkår. [K8-03](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/) · [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- **[Lov/forskrift]** **§ 15-3 sjuende ledd**: gjensidig oppsigelsesfrist normalt **14 dager under gyldig prøvetid**, med mindre annet er skriftlig avtalt eller tariffestet; fristen løper fra mottak, i motsetning til hovedregelen om første dag neste måned. [K8-05](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/).
- **[Lov/forskrift]** **§§ 3-2 og 4-2**: arbeidsgiver skal sørge for nødvendig instruksjon/opplæring for forsvarlig arbeid, inkludert teknisk utstyr og endrede oppgaver. [K8-10](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/generelle-krav-til-opplaring/).
- **[Bransjepraksis]** Opplæringsplan, fadder, rollebasert IT-tilgang og 30/60/90-dagers samtaler er hensiktsmessige syntetiske prosesshendelser, men disse tidspunktene er **ikke universelle lovfrister**. [K8-10](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/generelle-krav-til-opplaring/).

##### A8-03. Omorganisering, nedbemanning og overdragelse

- **[Lov/forskrift]** Arbeidsmiljøloven **§ 8-2** kan gi plikt til informasjon og drøfting om beslutninger som kan føre til vesentlig endring i arbeidsorganisering eller ansettelsesforhold. **§ 15-1** krever før oppsigelse drøfting med arbeidstaker og eventuelt tillitsvalgte så langt praktisk mulig. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- **[Lov/forskrift]** **§ 15-7** krever saklig grunn. Ved nedbemanning: vurder **annet passende arbeid** i virksomheten og, der konsernregel gjelder, andre konsernselskap, samt interesseavveining. Endringer utenfor arbeidsgivers styringsrett kan kreve **endringsoppsigelse** med korrekt prosess. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K8-06](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/endringsoppsigelse/).
- **[Lov/forskrift]** **§ 15-2**: minst **10 oppsigelser innen 30 dager** av virksomhetsrelaterte grunner utløser regelsettet for masseoppsigelser og tidlig informasjon/drøfting; NAV-melding og virkningstidspunkt etter bestemmelsene. Tallet 10 er **ikke** en generell grense for drøftingsplikt ved færre oppsigelser. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K8-19](https://www.nav.no/arbeidsgiver/nedbemanne).
- **[Lov/forskrift]** **§§ 14-2 og 16-1 til 16-6**: fortrinnsrett ved virksomhetsrelatert oppsigelse etter konkrete kvalifikasjons-/ansiennitetsvilkår; rettigheter ved virksomhetsoverdragelse forutsetter overføring av selvstendig enhet som beholder identitet – ikke enhver omorganisering. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- **[Tariffavtale]** **KS Hovedavtale 2026–2029** og **NHO–LO Hovedavtale 2026–2029** har prosessregler om informasjon og drøfting. NHO–LO særlig **§§ 9-4 og 9-5** om driftsomlegginger og selskapsendringer. **Virke–LO** har egen hovedavtale for 2026–2029; den aktuelle tariffbindingen må avklares før punkter programmeres. [K8-11](https://www.ks.no/fagomrader/lonn-og-tariff/hovedavtalen/hovedavtalen-1.1.2026--31.12.2029) · [K8-12](https://lovdata.no/dokument/TARH/tariff/tarh-1/%C2%A79-4) · [K8-13](https://www.virke.no/tariff-og-lonn/finn-tariffavtale/hovedavtalen-virke-lo/).

##### A8-04. Oppsigelse og rettssikkerhet

- **[Lov/forskrift]** **§§ 15-1, 15-3, 15-4, 15-6 og 15-7**: drøfting, korrekt frist, skriftlighet, formkrav og saklig grunn skal vurderes adskilt. I gyldig prøvetid gjelder egne mulige oppsigelsesgrunner: tilpasning, faglig dyktighet, pålitelighet, med mulighet for § 15-7-grunner. **Prøvetid innebærer ikke adgang til oppsigelse uten begrunnelse.** [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/) · [K8-05](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/).
- **[Lov/forskrift]** Vanlig frist er **minst én måned**, ved minst fem års sammenhengende tilsetting to måneder, ved minst ti år tre måneder; oppsigelse **fra arbeidsgiver** har ytterligere lovbestemte aldersgrenser for eldre arbeidstakere med minst ti års ansettelse. Tariff og gyldig avtale kan påvirke konkret frist. [K8-05](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/).
- **[Lov/forskrift]** **§ 15-8** gir særlig sykdomsvern ved oppsigelser begrunnet i sykefraværet de første tolv måneder. Dette innebærer ikke generelt immunitet mot virksomhetsbegrunnet oppsigelse. [K8-05](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/).
- **[Antakelse]** Systemet skal **aldri automatisk avgjøre** saklighet, utvelgelse, kvalifikasjonskrav, styringsrett eller juridisk oppsigelsesgrunn. Faste regler kan kun flagge manglende dokumentasjon, overskredne frister og behov for manuell vurdering.

#### B. Forskjeller mellom sektorene

| Tema | Industri | Privat service/kontor | Kommune |
|---|---|---|---|
| Rekruttering | Aml. og ev. NHO–LO, krav til fagkompetanse/sikkerhet | Aml. og ev. Virke; stor variasjon i tariffdekning | Aml. + offentlig **ulovfestet kvalifikasjonsprinsipp**; lokale rutiner |
| Ledig stilling | Vurder fortrinnsrett og deltid; kompetansekrav | Samme lovgrunnlag | Samme + særskilt offentlig begrunnelse/kvalifikasjonsvurdering |
| Midlertidig | Krever konkret § 14-9-grunnlag | Samme, også ved sesongarbeid/vikariat | Samme; kommunal praksis kan ha andre bemanningsmønstre |
| Prøvetid | Samme lovmaksimum | Samme lovmaksimum | Samme lovmaksimum; lokale avtaler vurderes |
| Onboarding | Typisk sikkerhet, maskin og sertifikater | Typisk system-, kunde- og arbeidsoppgaveopplæring | Typisk tjeneste- og rolle-/risikorettet opplæring |
| Omstilling | NHO–LO §§ 9-4/9-5 hvis partene bundet | Virke/annen hovedavtale eller lovens krav | KS Hovedavtale 2026–2029 om partsmedvirkning |
| Turnoverindikator | SSB jobbstrømmer ≠ turnover | Kan ikke overføre kommunetall | KS/PAI egen definisjon 2025; forskjellig fra intern avgang |

**Presisering:** Disse sektorforskjellene er [Lov/forskrift], [Tariffavtale] og [Bransjepraksis] slik de er beskrevet i A. Ingen generell forskjell i arbeidsmiljølovens individuelle stillingsvern er lagt til grunn.

#### C. 10 spørsmål til fasit for personalhåndbok

Fullstendige felt og kilder ligger i `AP8_fasit_sporsmal.csv` (Q-8-01–Q-8-10). Kortoversikt:

1. **Q-8-01:** Når må kontrakten være underskrevet? Over én måned senest sju dager etter start, ellers samme dag. [K8-02](https://www.arbeidstilsynet.no/lonn-og-ansettelse/arbeidsavtale/).
2. **Q-8-02:** Er behov på ubestemt tid grunn til midlertidig stilling? Nei, ikke uten eget lovgrunnlag. [K8-04](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/midlertidig-ansettelse/).
3. **Q-8-03:** Prøvetid fire måneder ved fem måneders kontrakt? Nei, maksimalt halvparten (2,5 måneder). [K8-03](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/).
4. **Q-8-04:** Ny prøvetid ved overgang til fast arbeid hos samme arbeidsgiver? Ikke automatisk; se tidligere prøvetid og oppgavenes endring. [K8-03](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/).
5. **Q-8-05:** Kan vi spørre om planer for barn ved intervju? Som hovedregel nei. [K8-08](https://lovdata.no/lov/2017-06-16-51/%C2%A730).
6. **Q-8-06:** Kan ny maskinoperatør settes direkte på jobb uten sikkerhetsopplæring? Nei, nødvendig opplæring må gis. [K8-10](https://www.arbeidstilsynet.no/arbeidstid-og-organisering/generelle-krav-til-opplaring/).
7. **Q-8-07:** Kan arbeidsgiver ensidig redusere lønn og flytte arbeidssted? Vesentlige endringer kan kreve avtale eller endringsoppsigelse. [K8-06](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/endringsoppsigelse/).
8. **Q-8-08:** Må NAV varsles ved 10 virksomhetsbegrunnede oppsigelser på 30 dager? Ja, masseoppsigelsesreglene utløses, men de konkrete vilkårene kontrolleres. [K8-19](https://www.nav.no/arbeidsgiver/nedbemanne).
9. **Q-8-09:** Betyr prøvetid alltid 14 dagers oppsigelsesfrist uten begrunnelse? Nei; frist og grunnlag er ulike spørsmål. [K8-05](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/).
10. **Q-8-10:** Betyr kommunal turnover på 12,4 % at vårt museum bør ha 12,4 %? Nei, ulik populasjon og definisjon. [K8-14](https://www.ks.no/fagomrader/statistikk-og-analyse/turnover/kommuner-og-fylkeskommuner/).

**Minst to tvetydige:** Q-8-02, -04, -07, -08, -09 og -10 kan ikke avgjøres uten faktum eller definisjonskontroll. Fasitspørsmålene har feltet `hvorfor_vanskelig`.

#### D. Realistiske tall og fordelinger – med år og begrensning

##### D8-01. Turnover i kommunal sektor – flere sammenlignbare delpopulasjoner

**[Offisiell statistikk]** KS/PAI, måletidspunkter **01.12.2024–01.12.2025**, publisert **16.02.2026**:

- Alle omfattet av PAI-definisjonen: **12,4 %** forlot kommunesektoren; fastlønte **10,0 %**; fastlønte uten utdanningsstillinger **9,9 %**; tap målt i årsverk **10,1 %**. Dette er **fire forskjellige måledefinisjoner**, ikke fire anslag for ett og samme forhold.
- Aldersfordeling: **55–60 år: 5,2 %**, **65–67 år: 37,0 %**, **under 20 år: over 60 %**. Stillingskode **6572 Assistent: 28,0 %**. Tallene kan brukes som scenarioillustrasjon **bare for kommunesektor med tilsvarende avgrensninger**.
- **4,9 %** ble værende i samme kommune men endret stillingskode; dette er **ikke** del av 12,4 % som sluttet i kommunesektoren. [K8-14](https://www.ks.no/fagomrader/statistikk-og-analyse/turnover/kommuner-og-fylkeskommuner/).

##### D8-02. Jobbstrømmer som indikator for næringsdynamikk – ikke turnover

**[Offisiell statistikk]** SSB, **2. kvartal 2026**, tabell **11654**:

- **Industri:** **233 314** arbeidsforhold, **16 089** i bedrifter med jobbnedgang og **17 434** i bedrifter med jobboppgang (SSBs jobbstrømdefinisjon).
- **Alle næringer:** **3 166 971** arbeidsforhold, **267 492** jobbnedgang og **292 205** jobboppgang.
- Disse størrelsene kan brukes til **scenariokontroll av næringsdynamikk**, men **ikke** som prosentfordeling for hvem som sier opp, hvem som er nyansatt, eller frivillig turnover ved museet. Kortvarige jobber mellom måletidspunktene kan mangle. [K8-15](https://www.ssb.no/arbeid-og-lonn/sysselsetting/statistikk/antall-arbeidsforhold-og-lonn/) · [K8-16](https://www.ssb.no/statbank/table/11654/).

##### D8-03. Sammenligningsfordeling: sykefravær næring, ikke kommune

**[Offisiell statistikk]** SSB **2. kvartal 2026**, **ikke-sesongjustert** samlet egen- og legemeldt sykefravær: industri **5,7 %**, varehandel **6,1 %**, informasjon/kommunikasjon **4,0 %**, offentlig administrasjon **5,6 %**, undervisning **6,8 %**, helse-/sosialtjenester **9,6 %**. Tallene er **næringsaggregater**, ikke separate tall for kommunal sektor eller museet. For kvartal-mot-kvartal-sammenligning må sesong og målemetode ivaretas. [K8-17](https://www.ssb.no/arbeid-og-lonn/arbeidsmiljo-sykefravaer-og-arbeidskonflikter/statistikk/sykefravaer/) · [K8-18](https://www.ssb.no/statbank/table/13935/).

**[Antakelse]** For et fiktivt museum med 168 ansatte finnes **ikke** et verifisert representativt mikrodatagrunnlag for fordeling av prøvetid, frivillig vs. ufrivillig turnover, interne stillingsbytter, rekrutteringstid og konkrete slutthendelser. Ingen slike prosenter legges inn uten uttrykkelig scenariomerking. Scenarioverdier kan styres manuelt eller fra en framtidig dokumentert mikrodatakilde.

#### E. Forslag til syntetiske data – kobles til eksisterende museum

Detaljert og maskinlesbar spesifikasjon i `AP8_datasett_forslag.yaml`:

1. `hr_rekrutteringsbehov`: åpning, grunnlag, sektor, stillingskode og ansvarlig avdeling.
2. `hr_rekrutteringsprosess`: prosess-ID og status, **uten** reelle søkernes identitet eller sensitive intervjudata.
3. `hr_ansettelseskontrakt`: kobling til `ansatt_id`, oppstart, avtaletype, juridisk grunnlag og prøvetid.
4. `hr_onboarding_tiltak`: risikovurdert opplæring, krav, dato og ferdigstatus; ingen universell 30-dagerslovfrist.
5. `hr_provetid_oppfolging`: dokumenterte oppfølgingshendelser og manuell vurdering, ikke oppsigelsesdom.
6. `hr_omstillingssak`: bakgrunn, drøfting, dokumentasjon av annet passende arbeid og tariffkontekst.
7. `hr_oppsigelse_sak`: historikk og formkrav, uten å maskinkonkludere med saklighet.
8. `hr_fortrinnsrett_sak`: håndtering av krav, kvalifikasjonsvurdering og frister.
9. `hr_turnover_definisjon`: versjonert teller/nevner, populasjon og kildenivå.
10. `hr_livslope_aggregerte_maal`: sektor/år/alder/yrkeskode, teller/nevner og kildeidentifikator.

**[Antakelse]** Alle foreslåtte tabeller inneholder kun syntetiske registreringer. Koble mot eksisterende ansatt-ID, dato, avdeling og STYRK-08 der oppgaven krever det; ikke skriv over ansatte, vakter, fravær eller lønn.

#### F. Faste regler – ikke-juridiske indikatorer og fallback

`AP8_regler_forslag.csv` inneholder numererte `R-8-*`-regler. Prinsipp:

- **[Lov/forskrift]** Kontroller dokumentert kontraktfrist (sju dager / oppstart), prøvetid (maksimum seks måneder og halvparten av midlertidig kontrakt), signert avtale og opplæringsstatus. Kilder [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/), [K8-02](https://www.arbeidstilsynet.no/lonn-og-ansettelse/arbeidsavtale/).
- **[Lov/forskrift]** Før ansettelse: status for fortrinnsrett og deltid; flagg **til vurdering** når sak mangler, ikke velg kandidat automatisk. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
- **[Lov/forskrift]** Oppsigelse: drøfting, saklighetsvurdering, alternativer og formkrav må dokumenteres; manglende registrering utløser sperre for automatisk «godkjent». [K8-05](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/).
- **[Lov/forskrift]** 10 virksomhetsbegrunnede oppsigelser på 30 dager utløser kontroll av masseoppsigelse/NAV. [K8-19](https://www.nav.no/arbeidsgiver/nedbemanne).
- **[Antakelse]** Enkeltpersoners utvalg i nedbemanning, årsaksforklaringer om hvorfor noen slutter, prøvetidsoppsigelse, kvalifikasjonsbedømmelse og reell virksomhetsoverdragelse **har ingen deterministisk juridisk ja/nei-regel** i modellen. Uklare felt går til manuell vurdering.
- **[Antakelse]** For spørsmål Q-8-01–Q-8-10 ligger nøyaktig én fallback-rad per spørsmål, med `operator=fallback`, også når det mangler opplysninger.

#### G. Grensetilfeller og usikkerhet

1. **[Lov/forskrift]** Om en intern endring er styringsrett eller endringsoppsigelse er konkret skjønn; stillingskode alene er ikke tilstrekkelig. [K8-06](https://www.arbeidstilsynet.no/lonn-og-ansettelse/oppsigelse/endringsoppsigelse/).
2. **[Lov/forskrift]** Ny prøvetid i påfølgende ansettelsesforhold kan ikke automatisk settes til seks måneder. Kontroller oppgavene, historikken og den skriftlige avtalen. [K8-03](https://www.arbeidstilsynet.no/lonn-og-ansettelse/ansettelse/).
3. **[Lov/forskrift]** Fortrinnsrett ved nedbemanning og fortrinnsrett for deltid gjelder etter ulike kriterier og prioritetsregler. Automatisk sammenblanding kan gi feil ansettelse. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
4. **[Lov/forskrift]** Omorganisering innad i virksomheten er ikke nødvendigvis en virksomhetsoverdragelse etter kapittel 16. [K8-01](https://www.arbeidstilsynet.no/regelverk/lover/arbeidsmiljoloven--aml/).
5. **[Tariffavtale]** Tariffbindingsområde, konsernforhold, stillingskategori og KS/LO/NHO/Virke-part er ukjent for den fiktive virksomheten; ingen tariffbasert oppsigelsesfrist antas. Virke har bekreftet ny landsoverenskomst for **museer og andre kulturinstitusjoner** i juli 2026, men det dokumenterer ikke at akkurat denne øvingsvirksomheten er tariffbundet. [K8-23](https://www.virke.no/tariff-og-lonn/tariffoppgjor-2026-dette-ma-du-vite/gjennomforte-forhandlinger/) · [K8-11](https://www.ks.no/fagomrader/lonn-og-tariff/hovedavtalen/hovedavtalen-1.1.2026--31.12.2029) · [K8-12](https://lovdata.no/dokument/TARH/tariff/tarh-1/KAPITTEL_6-1-1).
6. **[Offisiell statistikk]** KS' 12,4 % er **ut av kommunesektoren** og teller ikke bytte mellom kommuner eller internt; en bedrifts HR-system vil ofte telle slike skifter annerledes. [K8-14](https://www.ks.no/fagomrader/statistikk-og-analyse/turnover/kommuner-og-fylkeskommuner/).
7. **[Offisiell statistikk]** SSB jobbnedgang/-oppgang kan ikke tilordnes frivillige oppsigelser eller sluttdatoer for ansatte. [K8-15](https://www.ssb.no/arbeid-og-lonn/sysselsetting/statistikk/antall-arbeidsforhold-og-lonn/).
8. **[Myndighetsveiledning]** Rettslig grunnlag og sletting av søkerdata må vurderes konkret; én generell lovbestemt lagringstid er **ikke funnet**. [K8-21](https://www.datatilsynet.no/rettigheter-og-plikter/personvernprinsippene/).
9. **[Antakelse]** Bedriftsfordeling av «time to hire», onboarding etter x dager og prøvetidsutfall: **ikke funnet** i offentlig, sammenlignbar 2025–2026-statistikk for industri, service og museum. Ikke legg inn påståtte nasjonale prosenter.
10. **[Antakelse]** Dette er kildebasert øvingsgrunnlag, ikke rettslig konklusjon om en reell ansatts oppsigelse; risiko for falske positiver tilsier dokumentasjonssperre og manuell vurdering.

#### Metodemerknad

**M-08-SRC:** kildeverifisering (hjemmel/gyldighetsperiode/part); **M-08-DEF:** definisjonskontroll mellom kommunal sektor/bedrift/arbeidsforhold; **M-08-ADV:** djevelens advokat (alternative tolkninger av prøvetid, turnover og omstilling). Høy sikkerhet i lovens generelle terskler, middels sikkerhet når tariffdekning eller faktisk organisasjonsmodell ikke foreligger. **Ingen global AP0–AP8-konklusjon:** AP0/AP1-grunnlaget ligger ikke komplett lokalt. Stopp ved AP8; AP9 er ikke påbegynt.
---

## AP9 – konsistens og resterende mangler

- AP2–AP8 er kopiert fra tilgjengelige originalrapporter uten å omskrive deres generelle A–G-vurderinger; museumstilpasning er tydelig lagt til foran hver del.
- AP0-kildekart og original AP1-leveranse ble ikke funnet i tilgjengelige filer eller filsøket; en kildeoversikt og avgrenset AP1-erstatning er opprettet og tydelig merket.
- Tidligere AP6/AP7-fallback-ID-er `FB-6-*`/`FB-7-*` er normalisert til `R-6-90..99` og `R-7-90..99` i masterfilen, med endringslogg i sjekkpunktet.
- Regelterskler er forslag til deterministiske kontroller, men de forutsetter at begreper og tariff knyttes til lokale konfigurasjoner. De må testes før bruk i museum.db.
- **Ikke funnet:** pålitelig ansattfordeling i kunstmuseum for overtidsmengder, lønnsfordeling per museumsfunksjon, sykenærvær, korttidsengasjement og små-team-undersøkelser. Ingen slike fordelinger er oppdiktet.
- Egnede neste steg er manuell mapping av tariff/lønnsplan, verifisering av faktiske avdelinger og SQLite-skjema, og test av alle Q-/R-ID-er før Antigravity-generering.
