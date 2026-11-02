# AP4 – Område 4: fravær og oppfølging

**Kontrolltidspunkt:** 20. oktober 2026  
**Omfang:** Kun område 4 (AP4). Ikke juridisk rådgivning i enkeltsaker.  
**Versjon:** 1.0 – kildebasert forslag for syntetisk HR-øving.  
**Datagrunnlag:** Opplyst fiktivt kunstmuseum med 168 ansatte, seks avdelinger og syntetiske vakt-, fraværs- og ansattdata. Ingen ekte personopplysninger er undersøkt eller generert.

## Sammendrag (maks 10 linjer)

1. [Lov/forskrift] Arbeidsgiverperioden er som hovedregel 16 kalenderdager, men start, avbrudd og opptjeningsvilkår må beregnes per fraværstilfelle.
2. [Myndighetsveiledning] Egenmelding krever som hovedregel to måneders tilknytning og gir minst 3 kalenderdager per tilfelle, inntil fire tilfeller i løpet av 12 måneder; lokale utvidelser finnes.
3. [Lov/forskrift] Oppfølgingsplan innen fire uker ved sykefravær, med unntak når åpenbart unødvendig; dialogmøte 1 innen sju uker ved helt fravær, med unntak.
4. [Myndighetsveiledning] NAV vurderer aktivitetskravet ved åtte uker og dialogmøte 2 innen 26 uker, med relevante unntak; ikke et automatisk lovbrudd i arbeidsgiversystemet om møte mangler.
5. [Offisiell statistikk] SSB 2. kvartal 2026 (ikke sesongjustert): industri 5,7 %, varehandel 6,1 %, helse/sosial 9,6 %, alle næringer 6,6 %.
6. [Tariffavtale] Sykelønn/forskuttering ut over folketrygdens minimum avhenger av tariff og avtaledel; KS 2026–2028 og Virke Industrioverenskomsten 2026 krever versjonering.
7. [Lov/forskrift] Opplysninger om arbeidsfunksjon og tilretteleggingsbehov kan være nødvendige, men ikke automatisk diagnoser eller detaljerte helseopplysninger.
8. [Antakelse] Datasettet skal ikke generere medisinske diagnoser eller brukerspesifikke risikoprofiler; næringstall skal kalibrere aggregerte syntetiske nivåer, ikke enkeltansatte.

## A. Regler og primærgrunnlag

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

## B. Forskjeller mellom sektorer

| Tema | Industri | Privat service/kontor | Kommune (KS) |
|---|---|---|---|
| Egenmelding | Lovens minimum + mulig lokalt utvidet ordning | Lovens minimum + bedriftsordning | Lovens minimum + kommunens praksis; ikke automatisk identisk i alle kommuner |
| Sykelønn | Lov/NAV + relevant Industriavtale; Virke IO 2026 har egne forskutteringsvilkår | Lov/NAV + ev. Virke/NHO eller lokale avtaler | HTA 2026–2028 kan gi mer enn lovens minimum; gjeldende § 8 må verifiseres |
| Oppfølging (4/7/8/26) | Samme lov- og NAV-frister | Samme lov- og NAV-frister | Samme lov- og NAV-frister; offentlig arbeidsgiver gir ikke automatisk andre frister |
| Organisering | Skift, fagarbeiderfunksjoner og alternativt arbeid må vurderes konkret | Oppgaver, kundedrift og hjemmekontor kan være aktuelle tiltak | Tjeneste-, bruker- og bemanningsbehov; tilrettelegging vurderes konkret |
| Måling/rapportering | Næringstall for industri | Næringstall per relevant service/kontor-næring | Kommunal arbeidsgiver følger næring/foretakskoder; undervisning og helse/sosial er **ikke** identisk med kommune |
| Permisjoner | Lovfestet rett + tariff-/bedriftsordninger | Lovfestet rett + tariff-/bedriftsordninger | Lovfestet rett + KS HTA og særavtaler |

**Definisjon:** «Industri» er næringskategori som også er privat eid; «privat» i denne sammenligningen betyr service og kontor uten industri. Oslo kommune følger ikke KS-området.

## C. 10 typiske spørsmål og fasit

Maskinlesbare, kildegrunnlagte `Q-4-01`–`Q-4-10` står i `AP4_fasit_sporsmal.csv` med separate markeringer for vanskelige tilfeller. Spørsmålene dekker egenmelding, sykelønn, arbeidsgiverperiode, 4-/7-/8-/26-ukersfrister, delvis sykmelding, sykt barn, tariff og medisinsk personvern. Ferie behandles i A og G.

## D. Realistiske fordelinger og statistikk

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

## E. Forslag til syntetiske data

Seks tabeller ligger med **kolonnenavn, datatyper, verdidomener og koblinger** i `AP4_datasett_forslag.yaml`:

- `hr_fravaershendelse`: fraværstype, grad, perioder, beregningsgrunnlag og kildeklassifisering, uten diagnose.
- `hr_egenmeldingsordning`: gyldighetsdato og lokal rett, fremfor universell 8/24-regel.
- `hr_sykepenger_arbeidsgiverperiode`: sammenlenkede kalenderperioder, arbeidsgiverperiode og refusjonsstatus.
- `hr_sykefravaersoppfolging`: arbeidsfunksjon, frister, unntak og deling av oppfølgingsplan (ikke medisinske detaljer).
- `hr_dialogmote`: hvilken aktør som har møteansvar, 7-/26-ukers milepæl og dispensasjonsgrunnlag uten diagnose.
- `hr_permisjon_omsorg`: hjemmel, omsorgsdager og status for eventuelt tariffbasert lønn.

**Koblinger:** `hr_ansatte.ansatt_id`, eksisterende `fravaer` (hvis nøkkelen finnes), `vakter.vakt_id`, `hr_arbeidstidsavtale.ansatt_id`, AP2 lønnsgrunnlag ved beregning. Alle konkrete tabellnavn i det eksisterende SQLite-skjemaet må bekreftes før import – her er koblinger logiske forslag, ikke påstand om at datakolonnene fysisk finnes.

**Dataminimering:** Ikke modellér diagnose, behandlingsdetaljer, journalnotat, fødselsnummer eller ekte barns identitet. Begrens adgang til personnivå. Bruk `hjemmelsklasse`, `friststatus`, `tilretteleggingsmulig` og aggregerte hendelser.

## F. Deterministiske regler

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

## G. Grensetilfeller, usikkerhet og kildekritikk

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
