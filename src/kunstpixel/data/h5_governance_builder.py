"""H5 & Governance Databygger for Kunstpixel.

Bygger, validerer og eksporterer H5-datasett (A-F, T) og HR-onboarding/realisme
både til 05_data/governance/*.yaml og 05_data/*.csv.

Prinsipper:
1. 100 % overholdelse av skrive- og skjelettregler i leveranse.py:
   - Ingen sifre eller tall i fritekst (heller ikke årstall).
   - Kun godkjente roller.
   - Alle tekster er unike.
   - Ingen personnavn, e-post, telefoner eller paragrafer i fritekst.
   - Faste felt (frister 14 dager / 24 timer, og sum 287 timer) er bevart.
2. Deterministisk generering og eksport.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import yaml

# Legg til modulen for leveranse.py
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "05_data"
GOV_DIR = DATA_DIR / "governance"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.intern import leveranse


# -----------------------------------------------------------------------------
# 1. FYLLDATA (BEVART FRA COLAB OG UTVIDET TIL Å VÆRE 100 % UNIKE OG REGELRETTE)
# -----------------------------------------------------------------------------

# Fil A: Myndighetskontakter (MK-01 til MK-08)
MYNDIGHETER_FYLL = {
    "MK-01": {
        "hva_de_vil": "Tilsynet krever dokumentasjon på systematisk helse-, miljø- og sikkerhetsarbeid samt oversikt over vernerunder.",
        "utloser": "Planlagte periodiske kontroller eller meldinger fra ansatte vedrørende arbeidsforhold.",
        "dokumentasjon": "Prosedyrer for risikovurdering, avvikslogger, møtereferater fra arbeidsmiljøutvalget og handlingsplaner.",
    },
    "MK-02": {
        "hva_de_vil": "Tilsynet krever trygg mathåndtering og renhold på kjøkkenet samt god sporbarhet på råvarer.",
        "utloser": "Rutinemessige hygienekontroller eller bekymringsmeldinger fra gjester angående matsikkerhet.",
        "dokumentasjon": "Temperaturlogger for kjøleskap, rengjøringsplaner, rutiner for personlig hygiene og skadedyrkontroll.",
    },
    "MK-03": {
        "hva_de_vil": "Etaten krever trygge rømningsveier, fungerende slukkeutstyr og dokumentert opplæring i brannvern.",
        "utloser": "Årlige inspeksjoner eller bekymringsmeldinger angående blokkerte nødutganger i lokalene.",
        "dokumentasjon": "Rapporter fra øvelser, servicebøker for brannalarmanlegg og oversikt over brannvernledere.",
    },
    "MK-04": {
        "hva_de_vil": "Kommunen krever forsvarlig drift av serveringen samt overholdelse av vilkår for alkoholservering.",
        "utloser": "Søknad om fornyelse av bevillinger eller stikkprøver utført av skjenkekontrollen.",
        "dokumentasjon": "Oversikt over beståtte kunnskapsprøver, opplæringsplaner for ansatte og salgsrapporter.",
    },
    "MK-05": {
        "hva_de_vil": "Fylkeskommunen krever dokumentert regional forankring, samarbeid med skoler og god måloppnåelse for tilskudd.",
        "utloser": "Årlig rapportering på benyttede midler eller revisjon av regionale formidlingstiltak.",
        "dokumentasjon": "Årsrapport for pedagogisk virksomhet, deltakeroversikter fra fylket og prosjektregnskap.",
    },
    "MK-06": {
        "hva_de_vil": "Kulturdirektoratet krever fullstendig museumsstatistikk, oversikt over samlingsvekst og faglig forsvarlig forvaltning.",
        "utloser": "Faste årlige statistikkinnleveringer og søknader om statlig drifts- og utviklingstilskudd.",
        "dokumentasjon": "Statistikkskjema, samlingsgjennomganger, katalogiseringsoversikter og faglige årsberetninger.",
    },
    "MK-07": {
        "hva_de_vil": "Datatilsynet krever sikker behandling av personopplysninger og tydelig informasjon til de registrerte.",
        "utloser": "Meldinger om brudd på datasikkerheten eller klager fra enkeltpersoner angående innsyn.",
        "dokumentasjon": "Prosedyrer for personvernkonsekvenser, oversikt over databehandlere og logger over tilganger.",
    },
    "MK-08": {
        "hva_de_vil": "Stiftelsestilsynet krever etterlevelse av stiftelsens formål, betryggende formuesforvaltning og revisorgodkjent regnskap.",
        "utloser": "Årlig innsending av årsregnskap og årsberetning eller varsel om endringer i vedtekter.",
        "dokumentasjon": "Revisjonsberetning, protokoll fra styremøter, årsregnskap og oppdatert stiftelsesdokument.",
    },
}

# Fil B: Tilsynsbesøk rutine (steg 1 til 6)
TILSYNSSTEG_FYLL = {
    1: {
        "handling": "Driftsansvarlig mottar og registrerer varselet i kvalitetssystemet og varsler umiddelbart berørte ledere.",
        "dokumentasjon": "Mottatt varselbrev fra tilsynsmyndigheten og opprettet saksmappe i arkivet.",
    },
    2: {
        "handling": "Verneombud og Driftsansvarlig gjennomgår logger og samler alle etterspurte rutiner og sjekklister.",
        "dokumentasjon": "Gjeldende avvikslogger, referater fra vernerunder og oppdaterte instrukser for fagområdet.",
    },
    3: {
        "handling": "Museumsdirektør og Driftsansvarlig tar imot inspektørene, orienterer om virksomheten og ledsager dem på befaringen.",
        "dokumentasjon": "Fysiske plantegninger over bygget, skilting av nødutganger og oversikt over tekniske anlegg.",
    },
    4: {
        "handling": "Museumsdirektør deltar i oppsummeringsmøte med inspektørene og noterer foreløpige tilbakemeldinger og observasjoner.",
        "dokumentasjon": "Møtereferat fra oppsummeringsmøtet med inspektørenes muntlige kommentarer.",
    },
    5: {
        "handling": "Museumsdirektør utarbeider et formelt skriftlig tilsvar med tiltaksplan basert på den endelige tilsynsrapporten.",
        "dokumentasjon": "Endelig tilsynsrapport fra myndigheten, styrevedtak og oversendelsesbrev med utbedringsplan.",
    },
    6: {
        "handling": "Driftsansvarlig verifiserer at samtlige korrigerende tiltak er utført og lukker avvikene formelt i systemet.",
        "dokumentasjon": "Bilder av utbedringer, kvitteringer for utført arbeid og bekreftelse fra tilsynet.",
    },
}

# Fil C: Rapporteringskalender (RP-01 til RP-12)
RAPPORTER_FYLL = {
    "RP-01": {
        "formal": "Gi ledelsen en månedlig status på drift, vedlikehold og gjennomførte aktiviteter.",
        "kilder": ["driftslogg", "avviksregister"],
    },
    "RP-02": {
        "formal": "Levere pålagte årlige publikumstall og demografisk fordeling til nasjonale myndigheter.",
        "kilder": ["besøkstall", "utstillinger"],
    },
    "RP-03": {
        "formal": "Dokumentere oppnådde faglige mål og ressursbruk som grunnlag for statlig støtte.",
        "kilder": ["regnskap", "utstillinger", "besøkstall"],
    },
    "RP-04": {
        "formal": "Fremlegge lovpålagt finansiell status og styrets beretning om virksomhetens drift.",
        "kilder": ["regnskap", "styrereferat"],
    },
    "RP-05": {
        "formal": "Oppsummere årets systematiske arbeidsmiljøarbeid, sykefravær og vernetiltak for styret.",
        "kilder": ["avviksregister", "vernerunder"],
    },
    "RP-06": {
        "formal": "Loggføre enkelthendelser og uønskede hendelser for kontinuerlig forbedring og læring.",
        "kilder": ["avviksregister", "driftslogg"],
    },
    "RP-07": {
        "formal": "Dokumentere at kafeen overholder krav til hygiene, temperaturer og matsikkerhet.",
        "kilder": ["temperaturlogg", "avviksregister"],
    },
    "RP-08": {
        "formal": "Protokollføre fysiske inspeksjonsrunder i publikums- og personalarealer.",
        "kilder": ["vernerunder", "avviksregister"],
    },
    "RP-09": {
        "formal": "Gi status på bevaringstilstand og klimatiske forhold for kunstverk i samlingen.",
        "kilder": ["samlingsdatabase", "temperaturlogg"],
    },
    "RP-10": {
        "formal": "Evaluere evakueringstider og funksjon på varslingsanlegg etter øvelser.",
        "kilder": ["brannøvelser", "driftslogg"],
    },
    "RP-11": {
        "formal": "Sikre kontroll og forsikringsmessig oversikt over innlånte verk fra andre institusjoner.",
        "kilder": ["innlån", "samlingsdatabase"],
    },
    "RP-12": {
        "formal": "Fremlegge kvartalsvis helhetlig orientering om økonomi, drift og kunstnerisk program.",
        "kilder": ["regnskap", "utstillinger", "styrereferat"],
    },
}

# Fil D: Rapportmaler (ML-01 til ML-04) med felt og regler
MALER_FYLL = {
    "ML-01": {
        "formal": "Sikre en ensartet månedlig struktur for rapportering av operativ drift og avvik til ledelsen.",
        "felt": {
            "Periode": {
                "beskrivelse": "Angi hvilken måned og tidsramme driftsrapporten omfatter.",
                "kilde": ["driftslogg"],
            },
            "Gjennomførte arrangementer": {
                "beskrivelse": "Kort sammendrag av avholdte omvisninger, foredrag og verksteder i perioden.",
                "kilde": ["hendelser"],
            },
            "Kommende arrangementer": {
                "beskrivelse": "Oversikt over planlagte aktiviteter og publikumsrettede hendelser neste måned.",
                "kilde": ["hendelser"],
            },
            "Avvik og tiltak": {
                "beskrivelse": "Oppsummering av registrerte tekniske og driftsmessige avvik samt iverksatte tiltak.",
                "kilde": ["avviksregister"],
            },
            "Vedlikehold": {
                "beskrivelse": "Status på planlagt bygningsmessig service og utført tilsyn med tekniske anlegg.",
                "kilde": ["driftslogg"],
            },
        },
        "regler": [
            "Rapporten ferdigstilles innen utgangen av første uke i påfølgende måned.",
            "Alle avvik av vesentlig art skal ha en navngitt ansvarlig rolle for utbedring.",
        ],
    },
    "ML-02": {
        "formal": "Sikre grundig registrering, umiddelbar sikring og systematisk oppfølging av uønskede hendelser.",
        "felt": {
            "Hva skjedde": {
                "beskrivelse": "Nøktern og presis beskrivelse av selve hendelsesforløpet og berørte personer.",
                "kilde": ["avviksregister"],
            },
            "Når og hvor": {
                "beskrivelse": "Tidspunkt for hendelsen samt nøyaktig lokasjon i bygget eller salene.",
                "kilde": ["driftslogg"],
            },
            "Alvorlighetsgrad": {
                "beskrivelse": "Klassifisering av hendelsens alvorlighet i henhold til etablerte risikokriterier.",
                "kilde": ["avviksregister"],
            },
            "Umiddelbart tiltak": {
                "beskrivelse": "Beskrivelse av strakstiltak som ble utført på stedet for å avverge ytterligere skade.",
                "kilde": ["driftslogg"],
            },
            "Varig tiltak": {
                "beskrivelse": "Beskrivelse av langsiktige forbedringer for å forhindre gjentakelse av hendelsen.",
                "kilde": ["avviksregister"],
            },
            "Frist for lukking": {
                "beskrivelse": "Dato for når permanente tiltak skal være gjennomført og kontrollert.",
                "kilde": ["driftslogg"],
            },
        },
        "regler": [
            "Kritiske avvik krever umiddelbar varsling av Driftsansvarlig og Verneombud.",
            "Rapporten kan ikke arkiveres før alle tiltak er verifisert og godkjent.",
        ],
    },
    "ML-03": {
        "formal": "Gi tilskuddsyter en etterprøvbar redegjørelse for aktivitet, måloppnåelse og ressursbruk.",
        "felt": {
            "Periode": {
                "beskrivelse": "Angi hvilket tilskuddsår og hvilken avtale rapporteringen gjelder for.",
                "kilde": ["regnskap"],
            },
            "Besøkstall": {
                "beskrivelse": "Samlet publikumsoppslutning fordelt på ordinære gjester, skoler og frikort.",
                "kilde": ["besøkstall"],
            },
            "Gjennomførte aktiviteter": {
                "beskrivelse": "Redegjørelse for formidlingsopplegg og pedagogiske prosjekter støttet av midlene.",
                "kilde": ["hendelser"],
            },
            "Utstillinger": {
                "beskrivelse": "Oversikt over realiserte utstillinger i perioden og deres faglige profil.",
                "kilde": ["utstillinger"],
            },
            "Måloppnåelse": {
                "beskrivelse": "Vurdering av hvordan virksomheten har levert i henhold til tildelingsbrevet.",
                "kilde": ["styrereferat"],
            },
        },
        "regler": [
            "Rapporten må godkjennes av Museumsdirektør før oversendelse til myndigheten.",
            "Tall og oppsummeringer skal stemme overens med offisielt revisorgodkjent årsregnskap.",
        ],
    },
    "ML-04": {
        "formal": "Fremlegge en formell og forpliktende tilbakemelding på pålegg og merknader etter offentlig tilsyn.",
        "felt": {
            "Saksreferanse": {
                "beskrivelse": "Tilsynsmyndighetens saksnummer og dato for mottatt tilsynsrapport.",
                "kilde": ["driftslogg"],
            },
            "Kort oppsummering": {
                "beskrivelse": "Kortfattet sammendrag av tilsynets omfang og hovedfunn under besøket.",
                "kilde": ["styrereferat"],
            },
            "Funn og vår vurdering": {
                "beskrivelse": "Museets faglige kommentarer og vurdering av påpekte avvik.",
                "kilde": ["avviksregister"],
            },
            "Tiltak med frist": {
                "beskrivelse": "Konkret handlingsplan med tidsfrister for retting av hvert enkelt avvik.",
                "kilde": ["driftslogg"],
            },
            "Ansvarlig rolle": {
                "beskrivelse": "Angivelse av hvilken intern lederrolle som har ansvaret for gjennomføringen.",
                "kilde": ["styrereferat"],
            },
        },
        "regler": [
            "Svaret skal forankres i ledergruppen og godkjennes skriftlig av Museumsdirektør.",
            "Dokumentasjon på utbedringer skal vedlegges brevet som verifiserbare vedlegg.",
        ],
    },
}

# Fil E: Arbeidsoppgaver tidsbruk (begrunnelser for de 19 oppgavene)
BEGRUNNELSER_FYLL = {
    "AO-01": "Søknadsarbeid krever betydelig faglig og strategisk skjønn tilpasset politiske prioriteringer.",
    "AO-02": "Oppfølging krever skjønnsmessige risikovurderinger og fysiske befaringer på stedet.",
    "AO-03": "Dokumentasjonskravene er standardiserte og kan i stor grad hentes automatisk fra logger.",
    "AO-04": "Kjøkkenrutiner og egenkontrollskjemaer følger faste maler som enkelt kan sammenstilles.",
    "AO-05": "Inspeksjonslister for brannvern er rutinepregede og egner seg godt for sjekklisteautomatisering.",
    "AO-06": "Kommunale søknader krever personlige vandelsattester og politiske vedtak som krever manuell saksgang.",
    "AO-07": "Henvendelser om innsyn krever individuelle juridiske vurderinger av personvernhensyn.",
    "AO-08": "Driftsdata og hendelseslogger kan aggregeres automatisk til ferdige månedsoppsummeringer.",
    "AO-09": "Billettstatistikk genereres direkte fra salgssystemet og kan eksporteres maskinelt.",
    "AO-10": "Rapporten krever faglige vurderinger og tilpasning mot overordnede strategiske målsetninger.",
    "AO-11": "Finansiell rapportering og årsberetning krever revisorkontroll og grundig styrebehandling.",
    "AO-12": "Data fra vernerunder og fraværsstatistikk kan trekkes ut og oppsummeres digitalt.",
    "AO-13": "Hendelsesmeldinger registreres digitalt og kan struktureres i rapporter uten manuell bearbeiding.",
    "AO-14": "Sensorer og manuelle målinger i serveringen mates inn i faste oversikter automatisk.",
    "AO-15": "Protokollen bygger på en fast sjekkliste, men krever noen manuelle prioriteringer.",
    "AO-16": "Klimadata fra salene samles maskinelt, men vurdering av verk krever konservatorskjønn.",
    "AO-17": "Øvelseslogger kan sammenstilles raskt i standardiserte rapportmaler for beredskap.",
    "AO-18": "Innlånsoversikter er ferdig registrert i samlingsbasen og kan trekkes ut med et tastetrykk.",
    "AO-19": "Orienteringen forutsetter en helhetlig strategisk oppsummering fra toppledelsen.",
}

# Fil F: Historikk tekster (2010 - 2026) hentet fra Colab og kvalitetssikret
HISTORIKK_TEKSTER_FYLL = {
    2010: {
        "hendelse": "Etablering av felles rutiner for helse, miljø og sikkerhet på tvers av avdelingene.",
        "laerdom": "Felles standarder gir bedre oversikt og forenkler opplæring av nyansatte.",
    },
    2011: {
        "hendelse": "Innføring av systematisk registrering av avvik på det fysiske arbeidsmiljøet.",
        "laerdom": "Tidlig registrering av feil reduserer risikoen for skader på personell.",
    },
    2012: {
        "hendelse": "Gjennomgang og oppdatering av alle branninstrukser og rømningsplaner i bygget.",
        "laerdom": "Tydelige instrukser skaper trygghet og sikrer raskere tømming av lokalene.",
    },
    2013: {
        "hendelse": "Implementering av digitalt system for temperaturkontroll i serveringsområdet.",
        "laerdom": "Automatisk måling gir bedre kontroll og reduserer faren for matsvinn.",
    },
    2014: {
        "hendelse": "Gjennomføring av omfattende ergonomiske tilpasninger på arbeidsplassene.",
        "laerdom": "Riktig utstyr og varierte arbeidsstillinger reduserer sykefraværet blant ansatte.",
    },
    2015: {
        "hendelse": "Etablering av faste rutiner for opplæring av verneombud.",
        "laerdom": "God skolering av tillitsvalgte styrker samarbeidet om et trygt arbeidsmiljø.",
    },
    2016: {
        "hendelse": "Gjennomføring av ekstern revisjon av museets internkontrollsystem.",
        "laerdom": "Eksterne blikk avdekker svakheter i rutinene som vi selv har oversett.",
    },
    2017: {
        "hendelse": "Sertifisering av kafeens rutiner for mathåndtering og hygiene.",
        "laerdom": "Standardiserte prosesser gir tryggere drift og færre avvik ved tilsyn.",
    },
    2018: {
        "hendelse": "Oppdatering av risikovurderinger for enslig arbeid og kveldsarbeid.",
        "laerdom": "Tilpassede sikkerhetstiltak gir økt trygghet for ansatte på kveldstid.",
    },
    2019: {
        "hendelse": "Gjennomføring av stor felles brannøvelse med alle ansatte og eksterne aktører.",
        "laerdom": "Praktisk trening er avgjørende for at alle skal kjenne sine oppgaver i en krise.",
    },
    2020: {
        "hendelse": "Midlertidig stenging av publikumsområder og innføring av strenge smitteverntiltak.",
        "laerdom": "Smidig omstilling og klare instrukser sikrer kontinuitet under uforutsette kriser.",
    },
    2021: {
        "hendelse": "Gradvis gjenåpning med begrensede besøkstall og økt fokus på hygiene.",
        "laerdom": "Tydelig kommunikasjon til publikum skaper trygghet og sikrer god flyt i lokalene.",
    },
    2022: {
        "hendelse": "Full gjenåpning og evaluering av de midlertidige rutinene som ble innført.",
        "laerdom": "Noen av smitteverntiltakene, som hyppigere renhold, er hensiktsmessige å videreføre.",
    },
    2023: {
        "hendelse": "Digitalisering av avvikssystemet for enklere registrering via mobil.",
        "laerdom": "Lavere terskel for rapportering gir bedre oversikt over mindre utfordringer i hverdagen.",
    },
    2024: {
        "hendelse": "Revisjon av rutiner for onboarding og opplæring av sesongarbeidere.",
        "laerdom": "Strukturert opplæring fra første dag sikrer raskere integrering og færre feil.",
    },
    2025: {
        "hendelse": "Innføring av nye retningslinjer for psykososialt arbeidsmiljø og konflikthåndtering.",
        "laerdom": "Tydelige kjøreregler forebygger misforståelser og fremmer et godt samarbeidsklima.",
    },
    2026: {
        "hendelse": "Evaluering av den interne assistentens funksjonalitet og datakvalitet.",
        "laerdom": "Strukturert og oppdatert kildedata er en forutsetning for gode og pålitelige svar.",
    },
}

# Utvidet HR-datasett (onboarding, kompetanse, HMS)
HR_REALISME_DATA = {
    "klassifisering": "syntetisk",
    "syntetisk": True,
    "merknad": "Høydetaljert HR- og kompetansestatus for Kunstpixel, fri for tall i fritekst",
    "versjon": 1,
    "kompetanse_matrise": [
        {
            "opplaering_id": "OPP-001",
            "kategori": "kompetanse_matrise",
            "rolle": "Verneombud",
            "tema_eller_sertifisering": "Grunnkurs i arbeidsmiljø",
            "fase_eller_status": "Godkjent",
            "aktivitet_eller_beskrivelse": "Kurset dekker psykososialt arbeidsmiljø og fysisk vernerunde",
            "ansvarlig_rolle": "Driftsansvarlig",
        },
        {
            "opplaering_id": "OPP-002",
            "kategori": "kompetanse_matrise",
            "rolle": "Kafeansvarlig",
            "tema_eller_sertifisering": "Etablererprøven og skjenkekontroll",
            "fase_eller_status": "Godkjent",
            "aktivitet_eller_beskrivelse": "Nødvendig godkjenning for daglig drift av serveringsstedet",
            "ansvarlig_rolle": "Museumsdirektør",
        },
        {
            "opplaering_id": "OPP-003",
            "kategori": "kompetanse_matrise",
            "rolle": "Brannvernleder",
            "tema_eller_sertifisering": "Sertifikat for brannvernledere",
            "fase_eller_status": "Godkjent",
            "aktivitet_eller_beskrivelse": "Ansvarlig for dokumentasjon og koordinering av brannøvelser",
            "ansvarlig_rolle": "Driftsansvarlig",
        },
        {
            "opplaering_id": "OPP-004",
            "kategori": "kompetanse_matrise",
            "rolle": "Museumsvert",
            "tema_eller_sertifisering": "Førstehjelp og hjertestarter",
            "fase_eller_status": "Godkjent",
            "aktivitet_eller_beskrivelse": "Livreddende førstehjelp og håndtering av publikumsakutt",
            "ansvarlig_rolle": "Driftsansvarlig",
        },
        {
            "opplaering_id": "OPP-005",
            "kategori": "kompetanse_matrise",
            "rolle": "Samlingsforvalter",
            "tema_eller_sertifisering": "Sikker kunsthåndtering og pakkemetoder",
            "fase_eller_status": "Godkjent",
            "aktivitet_eller_beskrivelse": "Teknikker for skånsom flytting og sikring av malerier og skulptur",
            "ansvarlig_rolle": "Konservator",
        },
        {
            "opplaering_id": "OPP-006",
            "kategori": "kompetanse_matrise",
            "rolle": "Kvalitetsvokter",
            "tema_eller_sertifisering": "Internrevisjon og avviksmetodikk",
            "fase_eller_status": "Godkjent",
            "aktivitet_eller_beskrivelse": "Metodikk for systematisk revisjon av etterlevelse og rutiner",
            "ansvarlig_rolle": "Museumsdirektør",
        },
    ],
    "onboarding_status": [
        {
            "opplaering_id": "OPP-007",
            "kategori": "onboarding_status",
            "rolle": "Museumsvert",
            "tema_eller_sertifisering": "Generell introduksjon",
            "fase_eller_status": "Introduksjon",
            "aktivitet_eller_beskrivelse": "Gjennomgang av rømningsveier og rutiner ved ulykker",
            "ansvarlig_rolle": "Driftsansvarlig",
        },
        {
            "opplaering_id": "OPP-008",
            "kategori": "onboarding_status",
            "rolle": "Konservator",
            "tema_eller_sertifisering": "Laboratorie- og kjemikaliesikkerhet",
            "fase_eller_status": "Fagopplæring",
            "aktivitet_eller_beskrivelse": "Sikkerhetskurs for kjemikaliehåndtering og verneutstyr",
            "ansvarlig_rolle": "Samlingsforvalter",
        },
        {
            "opplaering_id": "OPP-009",
            "kategori": "onboarding_status",
            "rolle": "Kafeansvarlig",
            "tema_eller_sertifisering": "IK-Mat og rutiner for servering",
            "fase_eller_status": "Oppstart",
            "aktivitet_eller_beskrivelse": "Opplæring i temperaturlogging og allergenmerking av mat",
            "ansvarlig_rolle": "Driftsansvarlig",
        },
        {
            "opplaering_id": "OPP-010",
            "kategori": "onboarding_status",
            "rolle": "Kurator",
            "tema_eller_sertifisering": "Samlingssystemer og utstillingssikkerhet",
            "fase_eller_status": "Fagopplæring",
            "aktivitet_eller_beskrivelse": "Gjennomgang av rutiner for innlån og klimakrav i salene",
            "ansvarlig_rolle": "Samlingsforvalter",
        },
        {
            "opplaering_id": "OPP-011",
            "kategori": "onboarding_status",
            "rolle": "Formidler",
            "tema_eller_sertifisering": "Pedagogiske opplegg og publikumsflyt",
            "fase_eller_status": "Praksis",
            "aktivitet_eller_beskrivelse": "Observasjon av skoleomvisninger og introduksjon til materiell",
            "ansvarlig_rolle": "Museumsdirektør",
        },
        {
            "opplaering_id": "OPP-012",
            "kategori": "onboarding_status",
            "rolle": "Driftsansvarlig",
            "tema_eller_sertifisering": "Nøkkel- og adgangssystemer",
            "fase_eller_status": "Lederonboarding",
            "aktivitet_eller_beskrivelse": "Opplæring i overvåking og alarmoverføring til alarmsentral",
            "ansvarlig_rolle": "Museumsdirektør",
        },
    ],
    "hms_opplaering": [
        {
            "opplaering_id": "OPP-013",
            "kategori": "hms_opplaering",
            "rolle": "Museumsvert",
            "tema_eller_sertifisering": "Ergonomi ved stående arbeid",
            "fase_eller_status": "Obligatorisk kurs",
            "aktivitet_eller_beskrivelse": "Forebyggende opplæring for å unngå belastningsskader under salvakt",
            "ansvarlig_rolle": "Verneombud",
        },
        {
            "opplaering_id": "OPP-014",
            "kategori": "hms_opplaering",
            "rolle": "Museumsvert",
            "tema_eller_sertifisering": "Konflikthåndtering og publikumskontakt",
            "fase_eller_status": "Obligatorisk kurs",
            "aktivitet_eller_beskrivelse": "Kurs i rolig kommunikasjon og deeskalering av krevende situasjoner",
            "ansvarlig_rolle": "Driftsansvarlig",
        },
        {
            "opplaering_id": "OPP-015",
            "kategori": "hms_opplaering",
            "rolle": "Driftsansvarlig",
            "tema_eller_sertifisering": "Arbeid i høyden og stillasbygging",
            "fase_eller_status": "Sikkerhetssertifisering",
            "aktivitet_eller_beskrivelse": "Sikker bruk av stige og personløfter ved rigg av belysning",
            "ansvarlig_rolle": "Verneombud",
        },
        {
            "opplaering_id": "OPP-016",
            "kategori": "hms_opplaering",
            "rolle": "Samlingsforvalter",
            "tema_eller_sertifisering": "Tunge løft og ergonomiske hjelpemidler",
            "fase_eller_status": "HMS-modul",
            "aktivitet_eller_beskrivelse": "Bruk av jekketralle og løftebord under montering av skulptur",
            "ansvarlig_rolle": "Verneombud",
        },
        {
            "opplaering_id": "OPP-017",
            "kategori": "hms_opplaering",
            "rolle": "Kafeansvarlig",
            "tema_eller_sertifisering": "Brannvern på storkjøkken",
            "fase_eller_status": "Obligatorisk kurs",
            "aktivitet_eller_beskrivelse": "Bruk av slukketeppe og frityrslukker ved branntilløp",
            "ansvarlig_rolle": "Brannvernleder",
        },
        {
            "opplaering_id": "OPP-018",
            "kategori": "hms_opplaering",
            "rolle": "Museumsdirektør",
            "tema_eller_sertifisering": "Psykososialt arbeidsmiljø og lederansvar",
            "fase_eller_status": "Ledermodul",
            "aktivitet_eller_beskrivelse": "Forebygging av stress og oppfølging av arbeidsmiljøundersøkelser",
            "ansvarlig_rolle": "Styret",
        },
    ],
}


# -----------------------------------------------------------------------------
# 2. BYGGING AV KOMPLETTE STRUKTURER (YAML)
# -----------------------------------------------------------------------------

def bygg_fil_a() -> dict[str, Any]:
    """Fil A: Myndighetskontakter."""
    skel = leveranse.skjelett("A")
    for m in skel["myndigheter"]:
        mid = m["id"]
        info = MYNDIGHETER_FYLL[mid]
        m["hva_de_vil"] = info["hva_de_vil"]
        m["utloser"] = info["utloser"]
        m["dokumentasjon"] = info["dokumentasjon"]
    return skel


def bygg_fil_b() -> dict[str, Any]:
    """Fil B: Tilsynsbesøk rutine."""
    skel = leveranse.skjelett("B")
    for steg in skel["steg"]:
        nr = steg["nr"]
        info = TILSYNSSTEG_FYLL[nr]
        steg["handling"] = info["handling"]
        steg["dokumentasjon"] = info["dokumentasjon"]
    return skel


def bygg_fil_c() -> dict[str, Any]:
    """Fil C: Rapporteringskalender."""
    skel = leveranse.skjelett("C")
    for r in skel["rapporter"]:
        rid = r["id"]
        info = RAPPORTER_FYLL[rid]
        r["formal"] = info["formal"]
        r["kilder"] = list(info["kilder"])
    return skel


def bygg_fil_d() -> dict[str, Any]:
    """Fil D: Rapportmaler."""
    skel = leveranse.skjelett("D")
    for mal in skel["maler"]:
        mid = mal["id"]
        info = MALER_FYLL[mid]
        mal["formal"] = info["formal"]
        for f in mal["felt"]:
            f_navn = f["navn"]
            f_info = info["felt"][f_navn]
            f["beskrivelse"] = f_info["beskrivelse"]
            f["kilde"] = list(f_info["kilde"])
        mal["regler"] = list(info["regler"])
    return skel


def bygg_fil_e() -> dict[str, Any]:
    """Fil E: Arbeidsoppgaver og tidsbruk."""
    skel = leveranse.skjelett("E")
    for oppg in skel["oppgaver"]:
        oid = oppg["id"]
        oppg["begrunnelse"] = BEGRUNNELSER_FYLL[oid]
    return skel


def bygg_fil_f() -> dict[str, Any]:
    """Fil F: Historikk tekst per år (2010 - 2026)."""
    skel = leveranse.skjelett("F")
    for post in skel["historikk"]:
        aar = post["ar"]
        post["hendelse"] = HISTORIKK_TEKSTER_FYLL[aar]["hendelse"]
        post["laerdom"] = HISTORIKK_TEKSTER_FYLL[aar]["laerdom"]
    return skel


def bygg_fil_t() -> dict[str, Any]:
    """Fil T: Historikk tall (kodegenerert)."""
    return leveranse.skjelett("T")


# -----------------------------------------------------------------------------
# 3. KONTROLL OG VALIDERING MOT LEVERANSE.PY
# -----------------------------------------------------------------------------

def valider_alle_yaml_strukturer() -> None:
    """Validerer alle 6 modell-filer og tallfilen mot reglene i leveranse.py."""
    byggere = {
        "A": bygg_fil_a(),
        "B": bygg_fil_b(),
        "C": bygg_fil_c(),
        "D": bygg_fil_d(),
        "E": bygg_fil_e(),
        "F": bygg_fil_f(),
        "T": bygg_fil_t(),
    }
    for kode, data in byggere.items():
        tekst = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)
        funn = leveranse.kontroller_tekst(kode, tekst)
        feil = [f for f in funn if f.alvor == "FEIL"]
        if feil:
            print(f"❌ Validering feilet for fil {kode} ({leveranse.FILNAVN[kode]}):")
            for f in feil:
                print(f"   [{f.kode}] {f.sti}: {f.melding}")
            raise ValueError(f"Fil {kode} oppfyller ikke reglene i leveranse.py")
        print(f"✅ Fil {kode} ({leveranse.FILNAVN[kode]}): 100 % validert mot skjelett- og skriveregler")


# -----------------------------------------------------------------------------
# 4. EKSPORT TIL YAML I 05_DATA/GOVERNANCE/
# -----------------------------------------------------------------------------

def eksporter_yaml_filer(output_dir: Path | None = None) -> None:
    out = output_dir or GOV_DIR
    out.mkdir(parents=True, exist_ok=True)

    filer = {
        "myndighetskontakter.yaml": bygg_fil_a(),
        "tilsynsbesok_rutine.yaml": bygg_fil_b(),
        "rapporteringskalender.yaml": bygg_fil_c(),
        "rapportmaler.yaml": bygg_fil_d(),
        "arbeidsoppgaver_tidsbruk.yaml": bygg_fil_e(),
        "historikk_tekst.yaml": bygg_fil_f(),
        "historikk_tall.yaml": bygg_fil_t(),
        "hr_data_realisme.yaml": HR_REALISME_DATA,
    }

    for filnavn, data in filer.items():
        sti = out / filnavn
        tekst = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)
        sti.write_text(tekst, encoding="utf-8")
        print(f"  Skrev YAML: {sti}")


# -----------------------------------------------------------------------------
# 5. EKSPORT TIL CSV I 05_DATA/ FOR DATABASEBYGGING
# -----------------------------------------------------------------------------

def eksporter_csv_filer(output_dir: Path | None = None) -> None:
    out = output_dir or DATA_DIR
    out.mkdir(parents=True, exist_ok=True)
    kilde_merke = "syntetisk (h5_governance_builder)"

    # 1. h5_myndighetskontakter.csv
    fil_a = bygg_fil_a()
    rader_a = []
    for m in fil_a["myndigheter"]:
        rader_a.append({
            "id": m["id"],
            "myndighet": m["myndighet"],
            "omrade": m["omrade"],
            "intern_eier": m["intern_eier"],
            "kontaktperson": m["kontaktperson"],
            "kontakt_epost": m["kontakt_epost"],
            "intern_eier_navn": m["intern_eier_navn"],
            "intern_eier_epost": m["intern_eier_epost"],
            "hva_de_vil": m["hva_de_vil"],
            "utloser": m["utloser"],
            "dokumentasjon": m["dokumentasjon"],
            "merknad": m["merknad"],
            "datakilde": kilde_merke,
        })
    _skriv_csv(out / "h5_myndighetskontakter.csv", rader_a)

    # 2. h5_tilsynsbesok_rutine.csv
    fil_b = bygg_fil_b()
    rader_b = []
    for s in fil_b["steg"]:
        rader_b.append({
            "steg_nr": s["nr"],
            "navn": s["navn"],
            "ansvarlig": s["ansvarlig"],
            "handling": s["handling"],
            "dokumentasjon": s["dokumentasjon"],
            "gult_avvik_frist": fil_b["avvik_frister"]["gult_avvik_lukkes_innen"],
            "rodt_avvik_frist": fil_b["avvik_frister"]["rodt_avvik_lukkes_innen"],
            "datakilde": kilde_merke,
        })
    _skriv_csv(out / "h5_tilsynsbesok_rutine.csv", rader_b)

    # 3. h5_rapporteringskalender.csv
    fil_c = bygg_fil_c()
    rader_c = []
    for r in fil_c["rapporter"]:
        rader_c.append({
            "id": r["id"],
            "rapport": r["rapport"],
            "mottaker": r["mottaker"],
            "mottakertype": r["mottakertype"],
            "frekvens": r["frekvens"],
            "antall_per_ar": r["antall_per_ar"],
            "maned": r["maned"],
            "eier": r["eier"],
            "timer_per_gang": r["timer_per_gang"],
            "timer_per_ar": int(r["antall_per_ar"] * r["timer_per_gang"]),
            "godkjenning": r["godkjenning"],
            "formal": r["formal"],
            "kilder_json": json.dumps(r["kilder"], ensure_ascii=False),
            "datakilde": kilde_merke,
        })
    _skriv_csv(out / "h5_rapporteringskalender.csv", rader_c)

    # 4. h5_rapportmaler.csv
    fil_d = bygg_fil_d()
    rader_d = []
    for mal in fil_d["maler"]:
        for idx, f in enumerate(mal["felt"], start=1):
            rader_d.append({
                "id": mal["id"],
                "mal_navn": mal["navn"],
                "brukes_til_json": json.dumps(mal["brukes_til"], ensure_ascii=False),
                "godkjenning": mal["godkjenning"],
                "status_ved_opprettelse": mal["status_ved_opprettelse"],
                "formal": mal["formal"],
                "felt_rekkefolge": idx,
                "felt_navn": f["navn"],
                "felt_beskrivelse": f["beskrivelse"],
                "felt_kilder_json": json.dumps(f["kilde"], ensure_ascii=False),
                "regler_json": json.dumps(mal["regler"], ensure_ascii=False),
                "datakilde": kilde_merke,
            })
    _skriv_csv(out / "h5_rapportmaler.csv", rader_d)

    # 5. h5_arbeidsoppgaver_tidsbruk.csv
    fil_e = bygg_fil_e()
    rader_e = []
    for oppg in fil_e["oppgaver"]:
        rader_e.append({
            "id": oppg["id"],
            "omrade": oppg["omrade"],
            "oppgave": oppg["oppgave"],
            "myndighet": oppg.get("myndighet", ""),
            "rapport_id": oppg.get("rapport_id", ""),
            "rolle": oppg["rolle"],
            "timer_per_ar": oppg["timer_per_ar"],
            "automatiseringspotensial": oppg["automatiseringspotensial"],
            "begrunnelse": oppg["begrunnelse"],
            "datakilde": kilde_merke,
        })
    _skriv_csv(out / "h5_arbeidsoppgaver_tidsbruk.csv", rader_e)

    # 6. h5_historikk_2010_2026.csv
    fil_t = bygg_fil_t()
    fil_f = bygg_fil_f()
    tekster_f = {p["ar"]: p for p in fil_f["historikk"]}
    rader_historikk = []
    for aar_post in fil_t["aar"]:
        aar = aar_post["ar"]
        rad = dict(aar_post)
        rad["hendelse"] = tekster_f[aar]["hendelse"]
        rad["laerdom"] = tekster_f[aar]["laerdom"]
        rad["datakilde"] = kilde_merke
        rader_historikk.append(rad)
    _skriv_csv(out / "h5_historikk_2010_2026.csv", rader_historikk)

    # 7. hr_opplaering_onboarding.csv
    rader_hr = []
    for seksjon in ["kompetanse_matrise", "onboarding_status", "hms_opplaering"]:
        for item in HR_REALISME_DATA[seksjon]:
            rader_hr.append({
                "opplaering_id": item["opplaering_id"],
                "kategori": item["kategori"],
                "rolle": item["rolle"],
                "tema_eller_sertifisering": item["tema_eller_sertifisering"],
                "fase_eller_status": item["fase_eller_status"],
                "aktivitet_eller_beskrivelse": item["aktivitet_eller_beskrivelse"],
                "ansvarlig_rolle": item["ansvarlig_rolle"],
                "datakilde": kilde_merke,
            })
    _skriv_csv(out / "hr_opplaering_onboarding.csv", rader_hr)


def _skriv_csv(sti: Path, rader: list[dict[str, Any]]) -> None:
    if not rader:
        return
    fieldnames = list(rader[0].keys())
    with sti.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rader)
    print(f"  Skrev CSV: {sti} ({len(rader)} rader)")


def main() -> None:
    print("=== 1. VALIDERER LEVERANSE MOT REGLER ===")
    valider_alle_yaml_strukturer()

    print("\n=== 2. EKSPORTERER YAML-FILER TIL 05_DATA/GOVERNANCE/ ===")
    eksporter_yaml_filer()

    print("\n=== 3. EKSPORTERER CSV-FILER TIL 05_DATA/ ===")
    eksporter_csv_filer()

    print("\n✅ Alle H5- og Governance-data er ferdig bygget og validert!")


if __name__ == "__main__":
    main()
