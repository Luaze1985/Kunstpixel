"""Syntetisk pandas-generator for daglig driftsinnboks & meldingssystem (2010–2026).

Genererer to deterministiske CSV-filer i 05_data/ basert på gyldige nøkler fra
05_data/museum.db (mode=ro):
  - arkiv_driftsmeldinger_2010_2026.csv  (e-post, SMS, vaktchat, alarmsystem)
  - arkiv_driftsmeldinger_tiltak.csv     (lov-/SOP-vurdering, tiltak, e-post/SMS-utkast)

Fordeling: 2010–2026 med tyngdepunkt (ca. 82 %) i 2020–2026 etter digitalisering
av vaktrom og daglig driftsoppfølging.

Kjøres med:
    py -3.13 src/kunstpixel/data/generer_driftsmeldinger_pandas.py
"""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "05_data"
DB_PATH = DATA_DIR / "museum.db"

EPOST_CSV = DATA_DIR / "arkiv_driftsmeldinger_2010_2026.csv"
TILTAK_CSV = DATA_DIR / "arkiv_driftsmeldinger_tiltak.csv"

DATAKILDE = "syntetisk (pandas_driftsmeldinger_2010_2026)"
SEED = 42

# Realistisk årlig volum: lavere i eldre e-postarkiv (2010–2019), høyt etter digitalisering (2020–2026)
AARLIG_ANTALL: dict[int, int] = {
    2010: 55,
    2011: 58,
    2012: 62,
    2013: 65,
    2014: 68,
    2015: 72,
    2016: 75,
    2017: 78,
    2018: 82,
    2019: 85,
    2020: 380,
    2021: 410,
    2022: 440,
    2023: 460,
    2024: 480,
    2025: 500,
    2026: 510,
}

MALER: list[dict[str, object]] = [
    # 1. vakt_og_hviletid
    {
        "kategori": "vakt_og_hviletid",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "avdelingsleder",
        "ansvarlig_rolle": "hr_og_bemanning",
        "handbok_punkt_id": "PERSONAL-3.2",
        "lovhjemmel": "AML § 10-8 (1) (11 timer sammenhengende hviletid)",
        "vurdering_utfall": "AVSLÅS_LOVSTRIDIG_OVERSTYRING",
        "inneholder_persondata": 0,
        "emne": "Forespørsel om tidligvakt etter kveldsvakt i {sal_id}",
        "meldingstekst": "Hei, {navn} avsluttet kveldsarrangement i {sal_id} kl. 22:30 og spør om å ta åpningssveip kl. {klokkeslett} ({dato}). Kan vi godkjenne dette i vaktplanen?",
        "foreslatt_tiltak": "Avslå vaktkombinasjonen umiddelbart (kun 9t hvile < 11t lovkrav). Sett inn uthvilt tilkallingsvikar på morgenvakten.",
        "epost_sms_utkast": "Hei {navn}, forespørselen om morgenvakt {dato} må dessverre avslås fordi hviletiden etter kveldsvakt blir under 11 timer (AML § 10-8). Vi kaller inn vikar til åpningen slik at du får full hvile.",
    },
    {
        "kategori": "vakt_og_hviletid",
        "hastegrad": "HOY",
        "mottaker_rolle": "avdelingsleder",
        "ansvarlig_rolle": "avdelingsleder",
        "handbok_punkt_id": "SOP-004-1",
        "lovhjemmel": "AML § 10-8, Virke Landsoverenskomst",
        "vurdering_utfall": "GODKJENN_MED_KOMPETANSESJEKK",
        "inneholder_persondata": 0,
        "emne": "Søknad om internt vaktbytte for {dato} ({sal_id})",
        "meldingstekst": "{navn} ønsker å bytte helgevakt i {sal_id} under «{utstilling}» med kollega. Begge har gyldig kurs og minst 11 timer hviletid.",
        "foreslatt_tiltak": "Kontroller stasjonskrav og hviletid i vaktrommet, bekreft byttet skriftlig uten ekstra overtidstillegg.",
        "epost_sms_utkast": "Hei {navn}, vaktbyttet for {dato} i {sal_id} er kontrollert mot hviletid og stasjonskrav og er nå godkjent i vaktplanen.",
    },
    {
        "kategori": "vakt_og_hviletid",
        "hastegrad": "HOY",
        "mottaker_rolle": "hr_og_bemanning",
        "ansvarlig_rolle": "hr_og_bemanning",
        "handbok_punkt_id": "PERSONAL-4.3",
        "lovhjemmel": "AML § 10-6 (vilkår for overtid og minst 40 % tillegg)",
        "vurdering_utfall": "KREVER_PAALAGT_OVERTIDSGODKJENNING",
        "inneholder_persondata": 0,
        "emne": "Varsel om passering av 9 timer daglig arbeidstid ({dato})",
        "meldingstekst": "Under rigging av «{utstilling}» i {sal_id} ser vi at vakten til {navn} passerer 9,5 timer kl. {klokkeslett}. Trenger ledergodkjenning for overtid.",
        "foreslatt_tiltak": "Bekreft særskilt og tidsavgrenset behov etter AML § 10-6 og registrer pålagt overtid (40 % tillegg) før vaktslutt.",
        "epost_sms_utkast": "Hei {navn}, pålagt overtid utover 9 timer den {dato} er godkjent for sluttføring av rigging i {sal_id}. Registrer timene med overtidskode før du stempler ut.",
    },
    {
        "kategori": "vakt_og_hviletid",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "avdelingsleder",
        "ansvarlig_rolle": "avdelingsleder",
        "handbok_punkt_id": "PERSONAL-3.3",
        "lovhjemmel": "AML § 10-3 (arbeidsplan og 14 dagers varslingsfrist)",
        "vurdering_utfall": "OVERHOLD_14_DAGERS_FRIST",
        "inneholder_persondata": 0,
        "emne": "Endring i publisert vaktplan for {sal_id}",
        "meldingstekst": "Kan vi flytte helgevakten til {navn} på kort varsel på grunn av omlegging i «{utstilling}»?",
        "foreslatt_tiltak": "Endring innenfor 14 dager krever skriftlig samtykke fra arbeidstaker jf. AML § 10-3.",
        "epost_sms_utkast": "Hei {navn}, siden endringen gjelder innenfor 14-dagersfristen (AML § 10-3) spør vi om du ønsker å samtykke til flyttingen, eller beholde opprinnelig vakt.",
    },
    # 2. sykefraver_og_vikar
    {
        "kategori": "sykefraver_og_vikar",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "avdelingsleder",
        "handbok_punkt_id": "SOP-004-2",
        "lovhjemmel": "AML § 10-8, Virke Landsoverenskomst",
        "vurdering_utfall": "IVERKSETT_SOP_003_VIKAR",
        "inneholder_persondata": 0,
        "emne": "Akutt morgenfravær før åpning i {sal_id} ({dato})",
        "meldingstekst": "{navn} melder akutt sykdom kl. {klokkeslett} og rekker ikke åpningen av {sal_id}. Vi mangler én sertifisert vert til salssveip.",
        "foreslatt_tiltak": "Ring eller send SMS til godkjent tilkallingsvikar fra vaktrommet (sjekk gyldig brann-/sikkerhetskurs). Registrer egenmelding uten diagnose.",
        "epost_sms_utkast": "Hei, vi har akutt behov for vikar i {sal_id} i dag {dato} fra kl. 09:30–17:00. Svar JA hvis du kan ta vakten etter Virke-tariff.",
    },
    {
        "kategori": "sykefraver_og_vikar",
        "hastegrad": "HOY",
        "mottaker_rolle": "avdelingsleder",
        "ansvarlig_rolle": "hr_og_bemanning",
        "handbok_punkt_id": "SOP-003-2",
        "lovhjemmel": "Folketrygdloven §§ 8-23 til 8-27 (egenmelding)",
        "vurdering_utfall": "KONTROLLER_EGENMELDINGSKVOTE",
        "inneholder_persondata": 0,
        "emne": "Spørsmål om egenmeldingsdag 4 fra {navn}",
        "meldingstekst": "{navn} er fortsatt borte på fjerde kalenderdag den {dato} og ber om å bruke én ny egenmelding.",
        "foreslatt_tiltak": "Veiled om at sykmelding fra lege kreves fra 4. kalenderdag etter gjeldende egenmeldingsregler (maks 3 dager per tilfelle).",
        "epost_sms_utkast": "Hei {navn}, god bedring! Husk at ved fravær utover 3 kalenderdager må lege kontaktes for sykmelding fra og med dag 4 (Folketrygdloven § 8-24).",
    },
    {
        "kategori": "sykefraver_og_vikar",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "avdelingsleder",
        "ansvarlig_rolle": "avdelingsleder",
        "handbok_punkt_id": "SOP-003-3",
        "lovhjemmel": "Folketrygdloven kap. 8, AML § 4-6",
        "vurdering_utfall": "PLANLEGG_OPPFOELGINGSPLAN_4_UKER",
        "inneholder_persondata": 0,
        "emne": "Påminnelse: oppfølgingsplan og dialogmøte ({dato})",
        "meldingstekst": "Fraværsløpet til {navn} nærmer seg 4 uker. Ber om status på tilretteleggingsmuligheter i resepsjon eller {sal_id}.",
        "foreslatt_tiltak": "Utarbeid oppfølgingsplan sammen med arbeidstaker innen 4 uker og book dialogmøte 1 før uke 7 (AML § 4-6).",
        "epost_sms_utkast": "Hei {navn}, vi ønsker å invitere deg til en uformell prat for å utarbeide oppfølgingsplan innen 4-ukersfristen og se på eventuell tilrettelegging.",
    },
    {
        "kategori": "sykefraver_og_vikar",
        "hastegrad": "HOY",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "driftsansvarlig",
        "handbok_punkt_id": "PERSONAL-5.1",
        "lovhjemmel": "AML § 2-3 og Folketrygdloven § 8-18",
        "vurdering_utfall": "OMDISPONER_STASJON_MIDLERTIDIG",
        "inneholder_persondata": 0,
        "emne": "Omdisponering av bemanning ved formiddagsfravær i {sal_id}",
        "meldingstekst": "Én vert måtte gå hjem syk kl. {klokkeslett} under omvisning for «{utstilling}». Kan formidler dekke {sal_id} midlertidig?",
        "foreslatt_tiltak": "Flytt reservevert fra hovedskranken til {sal_id} for å opprettholde vakthold ved utstilte verk, og åpne vikarforespørsel for ettermiddagen.",
        "epost_sms_utkast": "Driftsmelding: {sal_id} dekkes midlertidig av reservevert fra skranken frem til innkalt vikar ankommer kl. 12:30.",
    },
    # 3. personvern_og_gdpr
    {
        "kategori": "personvern_og_gdpr",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "kvalitetsvokter",
        "ansvarlig_rolle": "kvalitetsvokter",
        "handbok_punkt_id": "PERSONAL-9.1",
        "lovhjemmel": "Personopplysningsloven (GDPR art. 9 og art. 32)",
        "vurdering_utfall": "SLETT_SENSITIV_FRITEKST_GDPR",
        "inneholder_persondata": 1,
        "emne": "Sensitiv helseopplysning sendt i åpen vaktchat ({dato})",
        "meldingstekst": "I vaktchatten kl. {klokkeslett} skrev {navn} detaljert medisinsk diagnose og telefonnummer 000 00 000 i åpen kanal for {sal_id}.",
        "foreslatt_tiltak": "Slett meldingen fra åpen vaktchat umiddelbart, flytt eventuell lovpålagt dokumentasjon til lukket personalmappe og minn om taushetsplikt.",
        "epost_sms_utkast": "Hei {navn}, vi har fjernet meldingen med helseopplysninger og telefonnummer fra åpen kanal av hensyn til personvern (GDPR art. 9/32). Send fraværsmelding kun til nærmeste leder uten diagnose.",
    },
    {
        "kategori": "personvern_og_gdpr",
        "hastegrad": "HOY",
        "mottaker_rolle": "museumsdirektor",
        "ansvarlig_rolle": "kvalitetsvokter",
        "handbok_punkt_id": "PERSONAL-8.3",
        "lovhjemmel": "Forvaltningsloven § 13 og GDPR art. 15",
        "vurdering_utfall": "BEKREFT_INNSYN_30_DAGER",
        "inneholder_persondata": 1,
        "emne": "Krav om innsyn i adgangslogg og personalmappe ({dato})",
        "meldingstekst": "{navn} ber om innsyn i lagrede personopplysninger og vaktlogger tilknyttet arbeid i {sal_id}.",
        "foreslatt_tiltak": "Registrer innsynsbegjæringen (GDPR art. 15), kontroller identitet og utlever strukturert kopi innen 30 kalenderdager uten tredjepartsdata.",
        "epost_sms_utkast": "Hei {navn}, vi bekrefter mottak av ditt innsynskrav ({dato}). Du vil motta fullstendig oversikt over dine registrerte opplysninger innen 30 dager.",
    },
    {
        "kategori": "personvern_og_gdpr",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "kommunikasjon",
        "ansvarlig_rolle": "kommunikasjon",
        "handbok_punkt_id": "LEDER_BEREDSKAP-6.2",
        "lovhjemmel": "Personopplysningsloven (GDPR art. 5 dataminimering)",
        "vurdering_utfall": "SLADD_GJESTEDATA_FOER_ARKIV",
        "inneholder_persondata": 1,
        "emne": "Publikumshenvendelse med telefonnummer i delt innboks",
        "meldingstekst": "En gjest som besøkte «{utstilling}» i {sal_id} la igjen telefon 000 00 000 i felles driftsinnboks med spørsmål om gjenglemt jakke.",
        "foreslatt_tiltak": "Besvar gjesten og slett/sladd telefonnummeret når gjenstanden er utlevert (dataminimering etter GDPR art. 5).",
        "epost_sms_utkast": "Hei, takk for henvendelsen! Vi har funnet jakken din i garderoben. Kontaktinformasjonen slettes fra vår felles innboks så snart den er hentet.",
    },
    # 4. hms_og_sikkerhet
    {
        "kategori": "hms_og_sikkerhet",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "driftsansvarlig",
        "handbok_punkt_id": "SOP-006-1",
        "lovhjemmel": "Brann- og eksplosjonsvernloven § 11, Forskrift om brannforebygging § 12",
        "vurdering_utfall": "RYDD_ROMNINGSVEI_UMIDDELBART",
        "inneholder_persondata": 0,
        "emne": "Blokkert rømningsvei ved {sal_id} under rigg ({dato})",
        "meldingstekst": "Tomme transportkasser fra «{utstilling}» står stablet foran nødutgangen i {sal_id} kl. {klokkeslett}. Nødlyset er delvis skjult.",
        "foreslatt_tiltak": "Stans videre rigging til kassene er flyttet til godkjent lager (MAG-1) og rømningsvei er 100 % fri. Opprett RUH innen 24 timer.",
        "epost_sms_utkast": "AKUTT DRIFTSMELDING: Transportkasser foran nødutgang i {sal_id} må fjernes umiddelbart før publikum slippes inn. RUH-avvik loggføres i dag.",
    },
    {
        "kategori": "hms_og_sikkerhet",
        "hastegrad": "HOY",
        "mottaker_rolle": "museumsdirektor",
        "ansvarlig_rolle": "kvalitetsvokter",
        "handbok_punkt_id": "SOP-001-4",
        "lovhjemmel": "AML kap. 2 A (§§ 2 A-1 til 2 A-4 vern mot gjengjeldelse)",
        "vurdering_utfall": "ESKALER_VERNEOMBUD_AML_2A",
        "inneholder_persondata": 0,
        "emne": "Bekymringsmelding / varsel om stenging alene i {sal_id}",
        "meldingstekst": "Varsel fra ansatt: Måtte låse bygget og sveipe {sal_id} alene kl. {klokkeslett} uten radio på Kanal 1 eller fullført sikkerhetsopplæring.",
        "foreslatt_tiltak": "Skjerm varslerens identitet, behandle som varsel etter AML kap. 2 A med verneombud innen 48 timer, og innfør umiddelbart forbud mot alenestenging.",
        "epost_sms_utkast": "Takk for ditt varsel ({dato}). Forholdet følges opp konfidensielt etter AML kap. 2 A med verneombud, og du er fullt vernet mot enhver gjengjeldelse (AML § 2 A-4). Alenestenging er stanset.",
    },
    {
        "kategori": "hms_og_sikkerhet",
        "hastegrad": "HOY",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "driftsansvarlig",
        "handbok_punkt_id": "SOP-005-2",
        "lovhjemmel": "AML § 4-4, Arbeidsplassforskriften § 2-1, STAMI retningslinjer",
        "vurdering_utfall": "INNFØR_ERGONOMISK_ROTASJON",
        "inneholder_persondata": 0,
        "emne": "Belastning på terrazzogulv i {sal_id} ({dato})",
        "meldingstekst": "{navn} melder om smerter i rygg og knær etter 4 timer sammenhengende stående vakt på hardt gulv i {sal_id}.",
        "foreslatt_tiltak": "Iverksett umiddelbar stasjonsrotasjon til sittende billettskranke/pause og kontroller at avlastningsmatte og museumskrakk er på plass.",
        "epost_sms_utkast": "Hei {navn}, takk for beskjeden. Vi roterer deg over til sittende stasjon resten av vakten og legger inn fast rotasjon hvert 90. minutt etter STAMI-kravene.",
    },
    {
        "kategori": "hms_og_sikkerhet",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "driftsansvarlig",
        "handbok_punkt_id": "HMS_SIKKERHET-5.1",
        "lovhjemmel": "AML § 4-1 (3) (særskilt vern mot alenearbeid)",
        "vurdering_utfall": "STANS_ALENEARBEID_KVELD",
        "inneholder_persondata": 0,
        "emne": "Kveldsarrangement uten to vakter i {sal_id}",
        "meldingstekst": "Over 95 påmeldte til kveldsomvisning i «{utstilling}» ({dato}), men vaktlisten viser bare én vert etter kl. 20:00.",
        "foreslatt_tiltak": "Ved besøk over 80 personer eller etter kl. 20:00 er alenearbeid forbudt. Kall inn ekstra vert med aktiv radio før arrangementet starter.",
        "epost_sms_utkast": "Vaktvarsel for {dato}: Kveldsarrangementet i {sal_id} krever minimum to sertifiserte verter (AML § 4-1 / SOP-008-4). Ekstra vakt er kalt inn.",
    },
    # 5. klima_og_samling
    {
        "kategori": "klima_og_samling",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "samlingsforvalter",
        "ansvarlig_rolle": "samlingsforvalter",
        "handbok_punkt_id": "SOP-008-2",
        "lovhjemmel": "NS-EN 15757 (konserveringsklima 45–55 % RH) og ICOM sikkerhetsstandard",
        "vurdering_utfall": "STANS_OG_SIKRE_SAL",
        "inneholder_persondata": 0,
        "emne": "KLIMAALARM: Luftfuktighet under 40 % RH i {sal_id} ({dato})",
        "meldingstekst": "Sensor i {sal_id} («{utstilling}») melder 37 % RH og 23,1 °C kl. {klokkeslett}. Risiko for oppsprekking av treverk og lerret.",
        "foreslatt_tiltak": "Varsle samlingsforvalter/konservator og driftstekniker umiddelbart, juster befuktning og loggfør KLIMA-avvik i RUH.",
        "epost_sms_utkast": "KLIMAALARM {sal_id}: Målt 37 % RH kl. {klokkeslett}. Konservator og driftstekniker er varslet for umiddelbar justering av klimaanlegg jf. NS-EN 15757.",
    },
    {
        "kategori": "klima_og_samling",
        "hastegrad": "HOY",
        "mottaker_rolle": "samlingsforvalter",
        "ansvarlig_rolle": "samlingsforvalter",
        "handbok_punkt_id": "DRIFT_KVALITET-4.2",
        "lovhjemmel": "CIE 157:2004 / ICOM lysnorm (50 luks papir, 200 luks olje)",
        "vurdering_utfall": "DEMP_LYS_TIL_LUKSGRENSE",
        "inneholder_persondata": 0,
        "emne": "For høyt lysnivå målt på grafikk i {sal_id}",
        "meldingstekst": "Morgensjekk kl. {klokkeslett} viste 145 luks på innlånte akvareller og papirverk i «{utstilling}» ({sal_id}).",
        "foreslatt_tiltak": "Demp spottene til maks 50 luks umiddelbart og kontroller UV-filter og solskjerming før publikumsåpning.",
        "epost_sms_utkast": "Lysmelding {sal_id}: Spotter på papirverk skal ned til maks 50 luks umiddelbart (CIE 157:2004). Drift sjekker dimmerinnstilling før kl. 10:00.",
    },
    {
        "kategori": "klima_og_samling",
        "hastegrad": "HOY",
        "mottaker_rolle": "samlingsforvalter",
        "ansvarlig_rolle": "samlingsforvalter",
        "handbok_punkt_id": "DRIFT_KVALITET-10.2",
        "lovhjemmel": "SPECTRUM 5.0 (tilstandsgrad TG 1–4) og Kulturdirektoratets lånevilkår",
        "vurdering_utfall": "KONSERVERINGSINSPEKSJON_TG3",
        "inneholder_persondata": 0,
        "emne": "Observert løs ramme/avskalling i {sal_id} ({dato})",
        "meldingstekst": "{navn} oppdaget et lite malingsflak under rammen på verk i {sal_id} under «{utstilling}» kl. {klokkeslett}.",
        "foreslatt_tiltak": "Sperr av sonen rundt verket, ikke berør eller flytt verket, og tilkall konservator for TG-vurdering (TG 3/4) og fotodokumentasjon.",
        "epost_sms_utkast": "Tilstandsvarsel {sal_id}: Sone rundt verket er avsperret. Konservator rykker ut for inspeksjon etter SPECTRUM 5.0.",
    },
    {
        "kategori": "klima_og_samling",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "samlingsforvalter",
        "ansvarlig_rolle": "samlingsforvalter",
        "handbok_punkt_id": "DRIFT_KVALITET-10.1",
        "lovhjemmel": "ICOM Guidelines for Loans og statlig innlånsforsikring",
        "vurdering_utfall": "OVERHOLD_24T_AKKLIMATISERING",
        "inneholder_persondata": 0,
        "emne": "Ankomst av kunstkasse til {sal_id} — kan vi pakke ut i dag?",
        "meldingstekst": "Transportør leverte innlånt maleri til «{utstilling}» kl. {klokkeslett}. Kurator spør om utpakking i ettermiddag.",
        "foreslatt_tiltak": "Utsett åpning av transportkasse: kunstlån skal akklimatiseres uåpnet i utstillingsrommet i minimum 24 timer.",
        "epost_sms_utkast": "Hei, kassen til «{utstilling}» må stå uåpnet i {sal_id} i minst 24 timer for akklimatisering før konservator og kurer åpner den i morgen.",
    },
    # 6. kafe_og_allergen
    {
        "kategori": "kafe_og_allergen",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "kafeansvarlig",
        "ansvarlig_rolle": "kafeansvarlig",
        "handbok_punkt_id": "SOP-007-1",
        "lovhjemmel": "Matloven § 10 og Næringsmiddelhygieneforskriften § 5 (HACCP)",
        "vurdering_utfall": "SPERR_KJOLTE_VARER_CCP",
        "inneholder_persondata": 0,
        "emne": "HACCP-avvik: Kjøledisk måler 7,8 °C kl. {klokkeslett}",
        "meldingstekst": "Morgenkontroll i Museumskaféen ({dato}) viser 7,8 °C i kjøledisken med lunsjsalater og meierivarer.",
        "foreslatt_tiltak": "Stans salg fra disken umiddelbart, flytt holdbare varer til reservekjøl <= 4 °C, kasser eksponerte lettbedervelige varer og loggfør IK-Mat-avvik.",
        "epost_sms_utkast": "IK-Mat-varsel: Kjøledisk i kaféen er tatt ut av bruk pga. temperatur over 4 °C. Tekniker er bestilt, og berørte matvarer er sperret etter HACCP-rutine.",
    },
    {
        "kategori": "kafe_og_allergen",
        "hastegrad": "HOY",
        "mottaker_rolle": "kafeansvarlig",
        "ansvarlig_rolle": "kafeansvarlig",
        "handbok_punkt_id": "SOP-007-2",
        "lovhjemmel": "Matinformasjonsforskriften § 4 og vedlegg II (14 allergener)",
        "vurdering_utfall": "OPPDATER_ALLERGENSKILTING",
        "inneholder_persondata": 0,
        "emne": "Manglende nøtte- og glutenmerking på dagens bakst ({dato})",
        "meldingstekst": "{navn} melder at ny leveranse av gulrotkake og focaccia i kaféen mangler synlig skilt med nøtter, gluten, melk og egg.",
        "foreslatt_tiltak": "Sett ut skriftlig allergenskilting ved disken før servering starter, og kontroller at separat klype brukes for nøttefrie varer.",
        "epost_sms_utkast": "Kafémelding: Servering av ny bakst settes på pause i 5 min til skriftlig allergenmerking (nøtter, gluten, melk, egg) er satt frem jf. Matinformasjonsforskriften § 4.",
    },
    {
        "kategori": "kafe_og_allergen",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "museumsdirektor",
        "ansvarlig_rolle": "kafeansvarlig",
        "handbok_punkt_id": "SOP-007-4",
        "lovhjemmel": "Matloven § 10, Matinformasjonsforskriften vedlegg II, GDPR art. 9",
        "vurdering_utfall": "SIKRE_MATPROVE_OG_SLADD_EPOST",
        "inneholder_persondata": 1,
        "emne": "Gjesteklage om allergisk reaksjon etter besøk i kaféen ({dato})",
        "meldingstekst": "Gjest sendte e-post etter kafébesøk med påstand om udeklarerte nøtter i kake. E-posten inneholder telefonnummer 000 00 000 og helsedetaljer.",
        "foreslatt_tiltak": "Varsle kaféansvarlig og museumsdirektør samme dag, sikre prøve av varen i kjøleskap for Mattilsynet og sladd person-/helsedata før loggføring.",
        "epost_sms_utkast": "Hei, vi beklager på det sterkeste at du opplevde en allergisk reaksjon. Kaféansvarlig og direktør følger opp saken i dag, og vi har sikret prøve av produktet for kontroll. Helseopplysningene dine behandles strengt fortrolig.",
    },
    {
        "kategori": "kafe_og_allergen",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "kafeansvarlig",
        "ansvarlig_rolle": "kafeansvarlig",
        "handbok_punkt_id": "DRIFT_KVALITET-5.2",
        "lovhjemmel": "Bokføringsloven § 10 og Bokføringsforskriften § 5-3-2",
        "vurdering_utfall": "DOKUMENTER_KASSEAVVIK_OVER_50",
        "inneholder_persondata": 0,
        "emne": "Kasseoppgjør kafé viser differanse på kr 185 ({dato})",
        "meldingstekst": "Ved Z-rapport kl. {klokkeslett} i kaféen mangler kr 185,- mot kontantbeholdning etter travel lørdag.",
        "foreslatt_tiltak": "Tell kassen på nytt med to personer til stede, kontroller manuelle kvitteringer og loggfør avvik over kr 50,- i kasseboken (Bokføringsforskriften § 5-3-2).",
        "epost_sms_utkast": "Takk for registrering av kasseoppgjør ({dato}). Avviket på kr 185,- kontrolleres mot terminallogg og signeres i dagsoppgjøret.",
    },
    # 7. kundekontakt_og_epost
    {
        "kategori": "kundekontakt_og_epost",
        "hastegrad": "HOY",
        "mottaker_rolle": "museumsdirektor",
        "ansvarlig_rolle": "kvalitetsvokter",
        "handbok_punkt_id": "PERSONAL-8.1",
        "lovhjemmel": "ICOM Code of Ethics §§ 8.2–8.5 og Straffeloven § 387",
        "vurdering_utfall": "AVSLÅ_PRIVAT_VERDIVURDERING_OG_GAVE",
        "inneholder_persondata": 0,
        "emne": "Kunde-epost: Forespørsel om privat verdivurdering og honorar ({dato})",
        "meldingstekst": "En privat samler skriver på e-post kl. {klokkeslett} og spør om {navn} kan taksere et maleri mot et privat honorar før et auksjonssalg av «{utstilling}»-relatert kunst.",
        "foreslatt_tiltak": "Avslå privat taksering, ekthetsvurdering og ethvert privat honorar/gave umiddelbart i tråd med ICOM Code of Ethics §§ 8.2–8.5 og Personalhåndbok 8.1.",
        "epost_sms_utkast": "Hei, takk for din henvendelse til Kunstpixel Museum. I henhold til ICOMs etiske regler har våre ansatte ikke anledning til å utføre private takseringer eller ekthetsvurderinger, og vi kan heller ikke motta honorar eller gaver. Vi henviser i stedet til uavhengige, autoriserte takstmenn.",
    },
    {
        "kategori": "kundekontakt_og_epost",
        "hastegrad": "HOY",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "driftsansvarlig",
        "handbok_punkt_id": "DRIFT_KVALITET-2.1",
        "lovhjemmel": "Likestillings- og diskrimineringsloven §§ 17–18 og TEK17 kap. 12",
        "vurdering_utfall": "SIKRE_UNIVERSELL_TILGANG_OG_LEDSAGER",
        "inneholder_persondata": 1,
        "emne": "Kundehenvendelse om rullestoladkomst og ledsagerbevis til {sal_id}",
        "meldingstekst": "Publikummer med rullestol spør på e-post ({dato}) om heis til {sal_id} fungerer for «{utstilling}», og opplyser telefon 000 00 000 fordi billetter ble avkrevd gebyr for ledsager.",
        "foreslatt_tiltak": "Bekreft fri inngang ved fremvist offentlig ledsagerbevis, sjekk at heis til {sal_id} er operativ eller sett inn alternativ løsning via vakt, og sladd telefonnummer i logg.",
        "epost_sms_utkast": "Hei, hjertelig velkommen! Offentlig ledsagerbevis gir alltid gratis inngang for ledsager. Vi har kontrollert at heisadkomst til {sal_id} er klar, og ber deg kontakte resepsjonen ved ankomst for eventuell refusjon av feilbelastet billett. Telefonnummeret ditt er nå slettet fra innboksen.",
    },
    {
        "kategori": "kundekontakt_og_epost",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "kafeansvarlig",
        "ansvarlig_rolle": "avdelingsleder",
        "handbok_punkt_id": "DRIFT_KVALITET-5.1",
        "lovhjemmel": "Merverdiavgiftsloven § 6-19 og Kulturdepartementets retningslinjer",
        "vurdering_utfall": "BEKREFT_BILLETTVILKAAR_OG_REFUSJON",
        "inneholder_persondata": 0,
        "emne": "E-post fra kunde om billettpris, gratis søndag og MVA på årskort",
        "meldingstekst": "Kunde spør på e-post ({dato}) hvorfor første søndag i måneden hadde ulik rabatt for grupper til «{utstilling}» i {sal_id}, og ber om MVA-spesifikasjon på museumsbilletter.",
        "foreslatt_tiltak": "Forklar gjeldende billettkategorier (voksen 120 kr, student/pensjonist 80 kr, barn under 16 gratis, gratis første søndag) og opplys at museumsadgang er unntatt MVA jf. Merverdiavgiftsloven § 6-19.",
        "epost_sms_utkast": "Hei, takk for e-posten! Inngangsbillett koster kr 120 (voksen), kr 80 (student/pensjonist) og gratis for barn under 16 år, med gratis inngang for alle første søndag i måneden. Museumsbilletter er unntatt merverdiavgift etter mval. § 6-19.",
    },
    {
        "kategori": "kundekontakt_og_epost",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "kommunikasjon",
        "ansvarlig_rolle": "kommunikasjon",
        "handbok_punkt_id": "DRIFT_KVALITET-1.1",
        "lovhjemmel": "ICOM Code of Ethics § 4 og GDPR art. 5 (dataminimering)",
        "vurdering_utfall": "BESVAR_KUNDE_OG_SLADD_PERSONDATA",
        "inneholder_persondata": 1,
        "emne": "Kundemail om hittegods og åpningstid etter besøk i {sal_id}",
        "meldingstekst": "Besøkende fra «{utstilling}» skriver på e-post ({dato}) kl. {klokkeslett} om gjenglemt skjerf og kamera i {sal_id}, med fullt navn og telefonnummer 000 00 000 i e-posten.",
        "foreslatt_tiltak": "Kontroller hittegodsboksen i resepsjonen, svar gjesten vennlig med hentetider og sladd persondata etter utlevering (GDPR art. 5).",
        "epost_sms_utkast": "Hei, vi har funnet gjenstandene etter ditt besøk i {sal_id}! De kan hentes i resepsjonen i våre åpningstider (tir–fre 10–17, lør–søn 11–16). Personopplysningene dine fjernes fra innboksen så snart hittegodset er hentet.",
    },
    # 8. arrangement_og_booking
    {
        "kategori": "arrangement_og_booking",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "museumsdirektor",
        "handbok_punkt_id": "DRIFT_KVALITET-8.1",
        "lovhjemmel": "Alkoholloven §§ 1-5, 4-7 og 8-9 og Forskrift om brannforebygging § 11",
        "vurdering_utfall": "AVSLÅ_MEDBRAKT_ALKOHOL_OG_OVERKAPASITET",
        "inneholder_persondata": 0,
        "emne": "Bookingforespørsel kveldsarrangement i {sal_id}: medbrakt alkohol og overkapasitet",
        "meldingstekst": "Ekstern arrangør ber på e-post ({dato}) om å bruke {sal_id} etter stengetid til «{arrangement}» (maks {maks_deltakere} deltakere), men vil ta med egen vin og øke gjestetallet til det dobbelte.",
        "foreslatt_tiltak": "Avslå medbrakt alkohol (skjenkebevilling og Alkoholloven §§ 1-5/4-7 krever godkjent serveringsansvarlig og alderskontroll) og hold maks deltakertall strengt innenfor {maks_deltakere} og brannforskrift.",
        "epost_sms_utkast": "Hei, vi kan dessverre ikke godkjenne medbrakt alkohol eller deltakertall over godkjent salgrense ({maks_deltakere} personer) i {sal_id}. All servering må gå via museets godkjente kafé/skjenkebevilling i tråd med alkoholloven og brannsikkerhetskrav.",
    },
    {
        "kategori": "arrangement_og_booking",
        "hastegrad": "HOY",
        "mottaker_rolle": "formidler",
        "ansvarlig_rolle": "formidler",
        "handbok_punkt_id": "DRIFT_KVALITET-1.2",
        "lovhjemmel": "ICOM Code of Ethics § 4.1 og Forskrift om sikkerhet ved skole- og barnehagebesøk",
        "vurdering_utfall": "KREV_SKOLESIKKERHET_OG_GARDEROBE",
        "inneholder_persondata": 0,
        "emne": "Skolegruppebooking til {sal_id}: antall lærere og ryggsekker ({dato})",
        "meldingstekst": "Lærer bestiller omvisning kl. {klokkeslett} i {sal_id} for 32 elever under «{arrangement}» (maks {maks_deltakere}) med bare én voksen ledsager, og spør om elevene kan beholde sekkene i salen.",
        "foreslatt_tiltak": "Krev minimum 1 voksen per 10 elever (minst 3–4 ledsagere), påbudt låsing av ryggsekker i garderoben før innpassering i {sal_id}, og del eventuelt gruppen dersom antall overstiger {maks_deltakere}.",
        "epost_sms_utkast": "Hei, vi gleder oss til skolebesøket {dato}! Av hensyn til kunstsikkerhet og brannregler i {sal_id} krever vi minst én voksen per 10 elever og at alle ryggsekker plasseres i garderobeskap før omvisningen starter.",
    },
    {
        "kategori": "arrangement_og_booking",
        "hastegrad": "KRITISK",
        "mottaker_rolle": "driftsansvarlig",
        "ansvarlig_rolle": "driftsansvarlig",
        "handbok_punkt_id": "SOP-006-1",
        "lovhjemmel": "Brann- og eksplosjonsvernloven § 11 og Forskrift om brannforebygging §§ 11–12",
        "vurdering_utfall": "AVSLÅ_EKSTRASTOLER_I_ROMNINGSVEI",
        "inneholder_persondata": 0,
        "emne": "Fullbooket «{arrangement}» i {sal_id}: forespørsel om ekstrastoler ({dato})",
        "meldingstekst": "Formidler/arrangør spør kl. {klokkeslett} om å sette 15 ekstra klappstoler i midtgangen i {sal_id} til «{arrangement}» siden maks kapasitet ({maks_deltakere}) allerede er nådd.",
        "foreslatt_tiltak": "Avslå løse ekstrastoler i gang- eller rømningsarealer umiddelbart (SOP-006-1 / Brann- og eksplosjonsvernloven § 11). Opprett heller venteliste eller ekstra visningstid.",
        "epost_sms_utkast": "Driftsmelding for {dato}: Det er ikke tillatt å plassere ekstrastoler i gang- eller rømningsveier i {sal_id} utover godkjent kapasitet på {maks_deltakere}. Vi setter opp venteliste for interesserte gjester.",
    },
    {
        "kategori": "arrangement_og_booking",
        "hastegrad": "NORMAL",
        "mottaker_rolle": "formidler",
        "ansvarlig_rolle": "avdelingsleder",
        "handbok_punkt_id": "DRIFT_KVALITET-1.1",
        "lovhjemmel": "ICOM Code of Ethics § 4 og Virke Landsoverenskomst",
        "vurdering_utfall": "OPPDATER_ARRANGEMENTSPLAN_OG_FORMIDLER",
        "inneholder_persondata": 0,
        "emne": "Endring og flytting av booking for «{arrangement}» ({dato})",
        "meldingstekst": "Besøksgruppe ber om å flytte påmeldt deltakelse til «{arrangement}» i {sal_id} fra formiddag til ettermiddag ({dato}), med {navn} satt opp som kontakt.",
        "foreslatt_tiltak": "Kontroller kapasitet ({maks_deltakere}) og formidlerdekning i vaktplan før endringen bekreftes til gruppen.",
        "epost_sms_utkast": "Hei, vi har mottatt ønsket om å flytte bookingen for «{arrangement}» den {dato}. Formidleransvarlig bekrefter nytt tidspunkt i {sal_id} så snart vaktplanen er avstemt.",
    },
]

ANKER_CASER: list[tuple[dict[str, object], dict[str, object]]] = [
    (
        {
            "melding_id": "MELD-2026-9001",
            "dato": "2026-11-13",
            "klokkeslett": "22:35",
            "aar": 2026,
            "kanal": "epost",
            "kategori": "vakt_og_hviletid",
            "hastegrad": "KRITISK",
            "ansatt_id": "KP-ANS-006",
            "mottaker_rolle": "avdelingsleder",
            "sal_id": "SAL-A",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Forespørsel om morgenvakt 07:30 etter kveldsvakt til 22:30",
            "meldingstekst": "Hei, vi mangler folk før vernissasjen. Kan vakthavende som går av kl. 22:30 i kveld settes rett på morgenvakt kl. 07:30 i morgen tidlig (9 timer hvile)?",
            "inneholder_persondata": 0,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9001",
            "melding_id": "MELD-2026-9001",
            "ansvarlig_rolle": "hr_og_bemanning",
            "handbok_punkt_id": "PERSONAL-3.2",
            "lovhjemmel": "AML § 10-8 (1) (minst 11 timer sammenhengende arbeidsfri)",
            "vurdering_utfall": "AVSLÅS_LOVSTRIDIG_OVERSTYRING",
            "foreslatt_tiltak": "Avslå vaktkombinasjonen: 9 timer mellom 22:30 og 07:30 bryter AML § 10-8(1) (11t hviletid). Bruk godkjent tilkallingsvikar fra vaktrommet.",
            "epost_sms_utkast": "Hei, denne vaktkombinasjonen må avslås fordi den gir kun 9 timer hviletid (kravet i AML § 10-8(1) og PERSONAL-3.2 er minimum 11 timer). Vi henter inn uthvilt vikar til åpningen kl. 07:30.",
            "status": "APEN",
            "svartid_timer": 0.5,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9002",
            "dato": "2026-11-14",
            "klokkeslett": "06:55",
            "aar": 2026,
            "kanal": "sms",
            "kategori": "sykefraver_og_vikar",
            "hastegrad": "KRITISK",
            "ansatt_id": "KP-ANS-006",
            "mottaker_rolle": "driftsansvarlig",
            "sal_id": "SAL-A",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Akutt sykdom kl. 06:55 før åpning i SAL-A",
            "meldingstekst": "Hei, jeg våknet med høy feber og oppkast og klarer dessverre ikke morgenvakten i SAL-A i dag kl. 09:00.",
            "inneholder_persondata": 1,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9002",
            "melding_id": "MELD-2026-9002",
            "ansvarlig_rolle": "avdelingsleder",
            "handbok_punkt_id": "SOP-004-2",
            "lovhjemmel": "AML § 10-8, Folketrygdloven kap. 8, GDPR art. 9",
            "vurdering_utfall": "IVERKSETT_SOP_003_VIKAR",
            "foreslatt_tiltak": "Registrer egenmelding uten å loggføre medisinsk diagnose, send SMS til kvalifisert tilkallingsvikar for SAL-A og bekreft dekning før åpning kl. 10:00.",
            "epost_sms_utkast": "SMS til ansatt: God bedring! Egenmelding er registrert for i dag (uten diagnose). SMS til vikar: Hei, kan du ta akutt dagvakt i SAL-A i dag 2026-11-14 kl. 09:30–17:00?",
            "status": "UNDER_BEHANDLING",
            "svartid_timer": 0.25,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9003",
            "dato": "2026-11-14",
            "klokkeslett": "08:15",
            "aar": 2026,
            "kanal": "alarmsystem",
            "kategori": "klima_og_samling",
            "hastegrad": "KRITISK",
            "ansatt_id": "KP-ANS-003",
            "mottaker_rolle": "samlingsforvalter",
            "sal_id": "SAL-D",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Klimaalarm 36 % RH i SAL-D (ved Skrik) og blokkert nødutgang",
            "meldingstekst": "Sensor i SAL-D ved Munchs Skrik rapporterer 36 % RH (under 40 %-grense), og nattriggen har etterlatt en transportkasse foran nødutgangen.",
            "inneholder_persondata": 0,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9003",
            "melding_id": "MELD-2026-9003",
            "ansvarlig_rolle": "samlingsforvalter",
            "handbok_punkt_id": "SOP-008-2",
            "lovhjemmel": "NS-EN 15757 (45–55 % RH) og Forskrift om brannforebygging § 12",
            "vurdering_utfall": "STANS_OG_SIKRE_SAL",
            "foreslatt_tiltak": "Hold SAL-D stengt for publikum til transportkassen er fjernet fra nødutgang og luftfuktighet er stabilisert over 45 % RH under oppsyn av konservator.",
            "epost_sms_utkast": "AKUTT MELDING til sikkerhetsleder og konservator: SAL-D holdes stengt fra kl. 08:15 inntil rømningsvei er ryddet og klimaanlegg har løftet RH tilbake til 45–55 % ved Skrik.",
            "status": "APEN",
            "svartid_timer": 0.1,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9004",
            "dato": "2026-11-14",
            "klokkeslett": "09:10",
            "aar": 2026,
            "kanal": "epost",
            "kategori": "hms_og_sikkerhet",
            "hastegrad": "HOY",
            "ansatt_id": "KP-ANS-007",
            "mottaker_rolle": "museumsdirektor",
            "sal_id": "SAL-B",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Skriftlig varsel: Uforsvarlig alenearbeid ved kveldsstenging",
            "meldingstekst": "Jeg varsler skriftlig om at nyansatte blir satt til å stenge bygget og låse av SAL-B alene uten sikkerhetsopplæring eller to personer på sveip.",
            "inneholder_persondata": 0,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9004",
            "melding_id": "MELD-2026-9004",
            "ansvarlig_rolle": "kvalitetsvokter",
            "handbok_punkt_id": "SOP-001-4",
            "lovhjemmel": "AML kap. 2 A (§§ 2 A-1 til 2 A-4) og AML § 4-1 (3)",
            "vurdering_utfall": "ESKALER_VERNEOMBUD_AML_2A",
            "foreslatt_tiltak": "Registrer som formelt varsel (AML kap. 2 A), vern varsler mot gjengjeldelse, involver verneombud umiddelbart og sikre at minimum to sertifiserte verter alltid stenger sammen.",
            "epost_sms_utkast": "Takk for ditt skriftlige varsel. Saken behandles etter AML kap. 2 A i samarbeid med verneombud, og du har fullt lovfestet vern mot gjengjeldelse (AML § 2 A-4). Alenestenging stanses fra i dag.",
            "status": "UNDER_BEHANDLING",
            "svartid_timer": 1.0,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9005",
            "dato": "2026-11-14",
            "klokkeslett": "10:05",
            "aar": 2026,
            "kanal": "epost",
            "kategori": "kafe_og_allergen",
            "hastegrad": "HOY",
            "ansatt_id": "KP-ANS-004",
            "mottaker_rolle": "kafeansvarlig",
            "sal_id": "SAL-E",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Gjestespørsmål om nøtter/gluten i bakst (inneholder persondata)",
            "meldingstekst": "Hei, jeg har alvorlig nøtteallergi og cøliaki og lurer på om dagens bakst i kaféen er trygg. Ring meg på 000 00 000 før besøket kl. 12.",
            "inneholder_persondata": 1,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9005",
            "melding_id": "MELD-2026-9005",
            "ansvarlig_rolle": "kafeansvarlig",
            "handbok_punkt_id": "SOP-007-2",
            "lovhjemmel": "Matinformasjonsforskriften § 4 (vedlegg II) og GDPR art. 5/9",
            "vurdering_utfall": "SLADD_PERSONDATA_OG_OPPDATER_ALLERGEN",
            "foreslatt_tiltak": "Verifiser ingrediensliste i kafe_meny (gulrotkake inneholder nøtter/gluten), oppdater skilting i disk og sladd telefonnummer/helseopplysninger i saksloggen.",
            "epost_sms_utkast": "Hei, takk for henvendelsen! Dagens gulrotkake og bakst inneholder dessverre både gluten og spor av nøtter, så vi anbefaler vår sertifiserte nøtte- og glutenfrie meny i stedet. Telefonnummeret ditt er slettet fra vår sakslogg av personvernhensyn.",
            "status": "APEN",
            "svartid_timer": 0.5,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9006",
            "dato": "2026-11-14",
            "klokkeslett": "10:40",
            "aar": 2026,
            "kanal": "epost",
            "kategori": "kundekontakt_og_epost",
            "hastegrad": "HOY",
            "ansatt_id": "KP-ANS-001",
            "mottaker_rolle": "museumsdirektor",
            "sal_id": "SAL-C",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Kunde-epost: Privat verdivurdering og honorartilbud kr 15 000 før auksjon",
            "meldingstekst": "En privat samler skriver at han ønsker en rask ekthetsbekreftelse og verdivurdering fra vår kurator før auksjon i desember, og tilbyr kr 15 000 privat eller en gave til avdelingen.",
            "inneholder_persondata": 0,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9006",
            "melding_id": "MELD-2026-9006",
            "ansvarlig_rolle": "kvalitetsvokter",
            "handbok_punkt_id": "PERSONAL-8.1",
            "lovhjemmel": "ICOM Code of Ethics §§ 8.2–8.5 og Straffeloven § 387",
            "vurdering_utfall": "AVSLÅ_PRIVAT_VERDIVURDERING_OG_GAVE",
            "foreslatt_tiltak": "Avslå privat taksering, ekthetsvurdering og pengegave umiddelbart etter ICOM Code of Ethics §§ 8.2–8.5 og Straffeloven § 387. Loggfør henvendelsen skriftlig til direktør.",
            "epost_sms_utkast": "Hei, takk for din e-post. Av hensyn til ICOMs etiske regler (Code of Ethics §§ 8.2–8.5) og museets habilitetsregler har våre ansatte ikke lov til å gi private verdivurderinger/ekthetsattester eller motta honorar og gaver. Vi anbefaler at du kontakter en uavhengig, autorisert takstmann.",
            "status": "APEN",
            "svartid_timer": 0.5,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9007",
            "dato": "2026-11-14",
            "klokkeslett": "11:15",
            "aar": 2026,
            "kanal": "epost",
            "kategori": "kundekontakt_og_epost",
            "hastegrad": "HOY",
            "ansatt_id": "KP-ANS-002",
            "mottaker_rolle": "driftsansvarlig",
            "sal_id": "SAL-A",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Kundeklage: Stengt trappeheis til SAL-A og avkrevd ledsagerbillett",
            "meldingstekst": "Hei, jeg bruker elektrisk rullestol og skulle besøke SAL-A i dag med ledsagerbevis. Trappeheisen sto avstengt og vi ble likevel bedt om å betale full billett for ledsageren. Ring meg på 000 00 000.",
            "inneholder_persondata": 1,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9007",
            "melding_id": "MELD-2026-9007",
            "ansvarlig_rolle": "driftsansvarlig",
            "handbok_punkt_id": "DRIFT_KVALITET-2.1",
            "lovhjemmel": "Likestillings- og diskrimineringsloven §§ 17–18, TEK17 kap. 12 og GDPR art. 5",
            "vurdering_utfall": "SIKRE_UNIVERSELL_TILGANG_OG_LEDSAGER",
            "foreslatt_tiltak": "Refunder ledsagerbilletten umiddelbart (offentlig ledsagerbevis gir alltid gratis adgang), rykk ut med drift for å få trappeheis til SAL-A i drift i dag og sladd telefonnummer i loggen.",
            "epost_sms_utkast": "Hei, vi beklager på det sterkeste både driftsstansen på heisen til SAL-A og feilen ved billettsalget! Offentlig ledsagerbevis gir alltid gratis inngang for ledsager. Vi refunderer beløpet med en gang, drift setter i gang alternativ trinnfri adkomst i dag, og telefonnummeret ditt slettes fra saksloggen.",
            "status": "APEN",
            "svartid_timer": 0.4,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9008",
            "dato": "2026-11-14",
            "klokkeslett": "12:20",
            "aar": 2026,
            "kanal": "epost",
            "kategori": "arrangement_og_booking",
            "hastegrad": "KRITISK",
            "ansatt_id": "KP-ANS-005",
            "mottaker_rolle": "driftsansvarlig",
            "sal_id": "SAL-E",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Bookingforespørsel: Kveldsarrangement for 95 gjester i SAL-E med medbrakt vin",
            "meldingstekst": "Et eksternt eventbyrå ber om å leie SAL-E i kveld kl. 20:00–01:30 for 95 gjester, ønsker å ta med egen vin og spør om én museumsvakt holder til stenging kl. 01:30.",
            "inneholder_persondata": 0,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9008",
            "melding_id": "MELD-2026-9008",
            "ansvarlig_rolle": "museumsdirektor",
            "handbok_punkt_id": "DRIFT_KVALITET-8.1",
            "lovhjemmel": "Alkoholloven §§ 1-5/4-7/8-9, Forskrift om brannforebygging § 11 og AML § 4-1 (3)",
            "vurdering_utfall": "AVSLÅ_MEDBRAKT_ALKOHOL_OG_OVERKAPASITET",
            "foreslatt_tiltak": "Avslå tre regelbrudd samtidig: (1) maks 40 plasser i SAL-E (95 bryter brannkapasitet), (2) medbrakt alkohol er forbudt under skjenkebevilling, (3) etter kl. 20 og >80 personer er alenevakt ulovlig.",
            "epost_sms_utkast": "Hei, vi må dessverre avslå forespørselen slik den foreligger: SAL-E har godkjent kapasitet på maks 40 personer, medbrakt alkohol er ikke tillatt (all servering må gå via museets bevilling), og kveldsdrift krever alltid minimum to sertifiserte vakter. Vi kan tilby tilpasset opplegg for inntil 40 gjester via vår kafé/skjenkeansvarlig.",
            "status": "APEN",
            "svartid_timer": 0.5,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
    (
        {
            "melding_id": "MELD-2026-9009",
            "dato": "2026-11-14",
            "klokkeslett": "13:05",
            "aar": 2026,
            "kanal": "epost",
            "kategori": "arrangement_og_booking",
            "hastegrad": "HOY",
            "ansatt_id": "KP-ANS-003",
            "mottaker_rolle": "formidler",
            "sal_id": "SAL-A",
            "utstilling_id": "KP-EXH-2026-065",
            "emne": "Skolebooking SAL-A: 34 elever med 1 lærer og ryggsekker til Stille kraft",
            "meldingstekst": "En ungdomsskole melder på 34 elever til «Guidet omvisning: Stille kraft» i SAL-A (maks 20 deltakere) med bare 1 lærer som følge, og ber om at elevene får ha på store ryggsekker inne i salen.",
            "inneholder_persondata": 0,
            "datakilde": DATAKILDE,
        },
        {
            "tiltak_id": "TILT-2026-9009",
            "melding_id": "MELD-2026-9009",
            "ansvarlig_rolle": "formidler",
            "handbok_punkt_id": "DRIFT_KVALITET-1.2",
            "lovhjemmel": "ICOM Code of Ethics § 4.1 og Forskrift om sikkerhet ved skole- og barnehagebesøk",
            "vurdering_utfall": "KREV_SKOLESIKKERHET_OG_GARDEROBE",
            "foreslatt_tiltak": "Del klassen i to puljer (maks 20 per omvisning i SAL-A), krev minst 4 voksne ledsagere (1 per 10 elever) og pålegg låsing av alle ryggsekker i garderoben før adgang til verkene.",
            "epost_sms_utkast": "Hei, velkommen til «Guidet omvisning: Stille kraft»! Siden SAL-A har grense på 20 deltakere per omvisning deler vi klassen i to grupper, og etter våre sikkerhetsrutiner kreves det minst 1 voksen per 10 elever (4 ledsagere for 34 elever) samt at alle ryggsekker låses inn i garderoben før dere går inn i salene.",
            "status": "APEN",
            "svartid_timer": 0.5,
            "lost_dato": "",
            "datakilde": DATAKILDE,
        },
    ),
]


def _hent_referanser(
    db_path: Path,
) -> tuple[pd.DataFrame, dict[int, list[tuple[str, str, str]]], list[str], set[str], list[tuple[str, str, int]]]:
    con = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        ansatte = pd.read_sql_query(
            "SELECT ansatt_id, navn, stilling, avdeling, ansatt_fra, coalesce(ansatt_til, '2099-12-31') AS ansatt_til "
            "FROM hr_ansatte ORDER BY ansatt_id",
            con,
        )
        utst_df = pd.read_sql_query(
            "SELECT aar, utstilling_id, tittel, saler FROM utstillinger_historikk ORDER BY aar, utstilling_id",
            con,
        )
        saler = [r[0] for r in con.execute("SELECT id FROM saler ORDER BY id")]
        handbok_ids = {r[0] for r in con.execute("SELECT punkt_id FROM handbok_oppslag")}
        hendelser = [
            (str(r[0]), str(r[1]), int(r[2] or 20))
            for r in con.execute("SELECT tittel, sal_id, maks_deltakere FROM hendelser ORDER BY id")
        ]
    finally:
        con.close()

    utst_per_aar: dict[int, list[tuple[str, str, str]]] = {}
    for _, rad in utst_df.iterrows():
        forste_sal = str(rad["saler"]).split(",")[0].strip().upper().replace(" ", "-")
        utst_per_aar.setdefault(int(rad["aar"]), []).append(
            (str(rad["utstilling_id"]), str(rad["tittel"]), forste_sal)
        )
    return ansatte, utst_per_aar, saler, handbok_ids, hendelser


def generer() -> tuple[pd.DataFrame, pd.DataFrame]:
    ansatte_df, utst_per_aar, saler, handbok_ids, hendelser = _hent_referanser(DB_PATH)
    for m in MALER:
        if m["handbok_punkt_id"] not in handbok_ids:
            raise ValueError(f"Ugyldig handbok_punkt_id i mal: {m['handbok_punkt_id']}")

    rng = np.random.default_rng(SEED)
    epost_rader: list[dict[str, object]] = []
    tiltak_rader: list[dict[str, object]] = []

    for aar, antall in AARLIG_ANTALL.items():
        er_eldre = aar <= 2019
        kanaler = ["epost", "sms", "alarmsystem"] if er_eldre else ["epost", "vaktchat", "sms", "alarmsystem"]
        kanal_vekter = [0.75, 0.20, 0.05] if er_eldre else [0.40, 0.30, 0.20, 0.10]

        maks_dag = 310 if aar == 2026 else 364
        dager = np.sort(rng.integers(0, maks_dag, size=antall))
        start_dato = date(aar, 1, 1)
        utstillinger = utst_per_aar[aar]

        for idx, dag_offset in enumerate(dager, start=1):
            d = start_dato + timedelta(days=int(dag_offset))
            dato_str = d.isoformat()
            time_val = int(rng.integers(6, 22))
            min_val = int(rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]))
            klokkeslett = f"{time_val:02d}:{min_val:02d}"

            aktive = ansatte_df[
                (ansatte_df["ansatt_fra"] <= dato_str) & (ansatte_df["ansatt_til"] >= dato_str)
            ]
            if aktive.empty:
                aktive = ansatte_df.iloc[:1]
            ansatt = aktive.iloc[int(rng.integers(0, len(aktive)))]

            mal = MALER[int(rng.integers(0, len(MALER)))]
            utst_id, utst_tittel, utst_sal = utstillinger[int(rng.integers(0, len(utstillinger)))]
            arr_tittel, arr_sal, arr_maks = hendelser[int(rng.integers(0, len(hendelser)))]
            if mal["kategori"] == "arrangement_og_booking" and arr_sal in saler:
                sal_id = arr_sal
            else:
                sal_id = utst_sal if utst_sal in saler else saler[int(rng.integers(0, len(saler)))]
            kanal = str(rng.choice(kanaler, p=kanal_vekter))

            melding_id = f"MELD-{aar}-{idx:04d}"
            tiltak_id = f"TILT-{aar}-{idx:04d}"

            fmt = {
                "navn": str(ansatt["navn"]),
                "dato": dato_str,
                "klokkeslett": klokkeslett,
                "sal_id": sal_id,
                "utstilling": utst_tittel,
                "arrangement": arr_tittel,
                "maks_deltakere": arr_maks,
            }

            if aar <= 2025 or dato_str < "2026-11-01":
                status = "LUKKET" if rng.random() < 0.96 else "UNDER_BEHANDLING"
            else:
                status = str(rng.choice(["APEN", "UNDER_BEHANDLING", "LUKKET"], p=[0.45, 0.35, 0.20]))

            svartid = round(float(rng.uniform(0.2, 6.0 if mal["hastegrad"] == "KRITISK" else 24.0)), 2)
            lost_dato = (d + timedelta(days=1 if svartid > 8 else 0)).isoformat() if status == "LUKKET" else ""

            epost_rader.append(
                {
                    "melding_id": melding_id,
                    "dato": dato_str,
                    "klokkeslett": klokkeslett,
                    "aar": aar,
                    "kanal": kanal,
                    "kategori": mal["kategori"],
                    "hastegrad": mal["hastegrad"],
                    "ansatt_id": str(ansatt["ansatt_id"]),
                    "mottaker_rolle": mal["mottaker_rolle"],
                    "sal_id": sal_id,
                    "utstilling_id": utst_id,
                    "emne": str(mal["emne"]).format(**fmt),
                    "meldingstekst": str(mal["meldingstekst"]).format(**fmt),
                    "inneholder_persondata": int(mal["inneholder_persondata"]),
                    "datakilde": DATAKILDE,
                }
            )
            tiltak_rader.append(
                {
                    "tiltak_id": tiltak_id,
                    "melding_id": melding_id,
                    "ansvarlig_rolle": mal["ansvarlig_rolle"],
                    "handbok_punkt_id": mal["handbok_punkt_id"],
                    "lovhjemmel": mal["lovhjemmel"],
                    "vurdering_utfall": mal["vurdering_utfall"],
                    "foreslatt_tiltak": str(mal["foreslatt_tiltak"]).format(**fmt),
                    "epost_sms_utkast": str(mal["epost_sms_utkast"]).format(**fmt),
                    "status": status,
                    "svartid_timer": svartid,
                    "lost_dato": lost_dato,
                    "datakilde": DATAKILDE,
                }
            )

    for epost_ank, tiltak_ank in ANKER_CASER:
        if tiltak_ank["handbok_punkt_id"] not in handbok_ids:
            raise ValueError(f"Ugyldig handbok_punkt_id i ankercase: {tiltak_ank['handbok_punkt_id']}")
        epost_rader.append(epost_ank)
        tiltak_rader.append(tiltak_ank)

    df_epost = pd.DataFrame(epost_rader)
    df_tiltak = pd.DataFrame(tiltak_rader)
    return df_epost, df_tiltak


def main() -> int:
    df_epost, df_tiltak = generer()
    df_epost.to_csv(EPOST_CSV, index=False, encoding="utf-8", lineterminator="\n")
    df_tiltak.to_csv(TILTAK_CSV, index=False, encoding="utf-8", lineterminator="\n")
    andel_2020_2026 = (df_epost["aar"] >= 2020).mean() * 100
    print(
        f"Generert {len(df_epost)} driftsmeldinger og {len(df_tiltak)} tiltak "
        f"(2010–2026, {andel_2020_2026:.1f} % i 2020–2026) med pandas {pd.__version__}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
