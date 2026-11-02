"""Intern organisasjons- og databygger for Kunstpixel.

Bygger syntetiske interne HR-, kompetanse-, henvendelses- og HMS-data for museet
med 100 % fokus innover i egen organisasjon.

Prinsipper:
- Deterministisk generering med faste seeds (reproduserbart).
- Alle rader har kolonnen datakilde som starter med «syntetisk (colab_org_bygger)».
- Fulle sitattegn rundt fritekst med komma eller linjeskift.
- Ingen ekte personopplysninger.
- Ingen henvendelse eller avvik datert etter 2026-10-23.
- Ingen to HMS-avvik med identisk beskrivelse.
- sak_id og avvik_id nummereres i streng datorekkefølge.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

# Standardstier
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "05_data"

# Gjeldende dato-terskel: ingen henvendelse eller avvik kan dateres etter denne dagen
MAX_DATE = date(2026, 10, 23)
START_DATE = date(2026, 1, 5)

# Standard ferdighetskatalog for et kunstmuseum
SKILLS_CATALOG = [
    {"code": "kasse", "name": "Kassasystem og oppgjør", "expires": 0, "kategori": "drift"},
    {"code": "kundeservice", "name": "Kundebehandling og publikumsdialog", "expires": 0, "kategori": "vert"},
    {"code": "allergen", "name": "Allergenopplæring", "expires": 1, "kategori": "kafe"},
    {"code": "mattrygghet", "name": "Internkontroll mat og IK-Mat", "expires": 1, "kategori": "kafe"},
    {"code": "hms", "name": "Generell HMS-opplæring", "expires": 0, "kategori": "felles"},
    {"code": "kran", "name": "Kranførerbevis G4/G8", "expires": 0, "kategori": "drift"},
    {"code": "formidling", "name": "Kunstformidling og omvisning", "expires": 0, "kategori": "fag"},
    {"code": "forstehjelp", "name": "Akutt førstehjelp og hjertestarter", "expires": 1, "kategori": "sikkerhet"},
    {"code": "brannvern", "name": "Brannvernleder og evakueringsansvar", "expires": 1, "kategori": "sikkerhet"},
    {"code": "vekter", "name": "Vekterkurs og adgangskontroll FG", "expires": 0, "kategori": "sikkerhet"},
    {"code": "kunsthandtering", "name": "Presisjonshåndtering og montering av kunst", "expires": 0, "kategori": "samling"},
    {"code": "av_teknikk", "name": "AV-systemer, prosjektører og lysstyring", "expires": 0, "kategori": "drift"},
    {"code": "ergonomi_hms", "name": "Ergonomisk tilrettelegging og verneombud", "expires": 0, "kategori": "hms"},
    {"code": "universell_utforming", "name": "Tilrettelegging for funksjonshemmede", "expires": 0, "kategori": "vert"},
]

# Relevante kompetanser per avdeling
DEPARTMENT_SKILL_AFFINITY = {
    "Formidling": ["kundeservice", "formidling", "forstehjelp", "universell_utforming", "brannvern"],
    "Drift": ["hms", "brannvern", "kran", "av_teknikk", "kunsthandtering", "vekter", "forstehjelp"],
    "Samling": ["kunsthandtering", "hms", "forstehjelp", "ergonomi_hms"],
    "Kuratering": ["kunsthandtering", "formidling", "hms"],
    "Marked": ["kasse", "kundeservice", "allergen", "mattrygghet", "forstehjelp"],
    "Ledelse": ["hms", "brannvern", "ergonomi_hms", "forstehjelp"],
}

# Mal for interne henvendelser knyttet til de 14 etiske HR-casene
HENVELDELSER_TEMPLATES = [
    {
        "kategori": "vaktbytte",
        "tittel": "Vaktbytteforespørsel: Kveldsvakt før vernissage",
        "tekst": "Jeg er oppsatt på kveldsvakt til kl. 23:30 fredag før åpningen, og morgenvakt kl. 07:00 lørdag. Kan jeg få bytte slik at jeg overholder 11 timers hviletid?",
        "case_ref": "CASE-004",
        "paragraf": "aml. § 10-8 (hviletid)",
        "forventet_utfall": "GODKJENNES_MED_HVILETIDSJUSTERING",
    },
    {
        "kategori": "vaktbytte",
        "tittel": "Ønske om å overstyre hviletid under montering",
        "tekst": "Vi rekker ikke monteringen i Sal B før i morgen tidlig. Vi overstyrer 11 timers hviletid pga vernissage og stiller kl. 06:00.",
        "case_ref": "CASE-004",
        "paragraf": "aml. § 10-8 (hviletid)",
        "forventet_utfall": "AVSLÅS_LOVSTRIDIG_OVERSTYRING",
    },
    {
        "kategori": "tilrettelegging",
        "tittel": "Tilrettelegging: Steingulvbelastning i Sal A",
        "tekst": "Etter tre uker med lange vakter på steingulvet i Sal A har jeg store smerter i korsryggen. Søker om rotasjonsordning med maks 90 minutter ståtid og sitteavlastning.",
        "case_ref": "CASE-012",
        "paragraf": "aml. § 4-6 (tilrettelegging) / STAMI",
        "forventet_utfall": "GODKJENNES_TILRETTELEGGING",
    },
    {
        "kategori": "permisjon",
        "tittel": "Søknad om velferdspermisjon ved dåp",
        "tekst": "Søker herved om én dags velferdspermisjon med lønn fredag 14. november i anledning dåp av eget barn, jf. SOP-002 og personalhåndboken.",
        "case_ref": "CASE-015",
        "paragraf": "SOP-002 / Personalhåndbok kap. 4",
        "forventet_utfall": "GODKJENNES_TARIFF",
    },
    {
        "kategori": "varsling",
        "tittel": "Konfidensiell bekymringsmelding om sikkerhetsrutiner",
        "tekst": "Jeg melder fra i fortrolighet om at nødutganger i kjellermagasinet gjentatte ganger blokkeres av transportkasser under rigging.",
        "case_ref": "CASE-013",
        "paragraf": "aml. kap. 2 A (varsling) / SOP-001",
        "forventet_utfall": "KONFIDENSIELT_VARSEL_SKJERMET_IDENTITET",
    },
    {
        "kategori": "sykefraver",
        "tittel": "Egenmeldingsdialog etter 3 dagers fravær",
        "tekst": "Melder om fravær grunnet akutt influensa. Planlegger retur mandag. Ønsker samtale med leder om gradert opptrapping dersom formen ikke er 100 %.",
        "case_ref": "CASE-012",
        "paragraf": "SOP-003 / IA-avtalen",
        "forventet_utfall": "ORDINÆR_OPPFØLGING_UTEN_DIAGNOSEGJETTING",
    },
    {
        "kategori": "arbeidsmiljo",
        "tittel": "Innsynsbegjæring i medarbeiderundersøkelse for lite team",
        "tekst": "Leder i avdelingen ønsker innsyn i detaljerte trivselsresultater for Kuratering (3 ansatte).",
        "case_ref": "CASE-014",
        "paragraf": "Personvernforordningen art. 5 / K-anonymitet (k >= 5)",
        "forventet_utfall": "AVSLÅS_K_ANONYMITET_KREVER_MINST_FEM",
    },
]

# 40 unike HMS-hendelser for intern drift og arbeidsmiljø (ingen duplikate beskrivelser)
HMS_INCIDENT_TEMPLATES = [
    {
        "avdeling": "Formidling",
        "stasjon": "Sal B",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Salvert sto sammenhengende på marmorgulvet i Sal B i 2 timer og 45 minutter uten avløsning på grunn av uventet publikumstopp.",
        "strakstiltak": "Verten ble avløst og gitt 30 min sittepause i personalrommet. Rotasjonsliste strammet inn til 90 minutter.",
        "ansvarlig_rolle": "Formidlingsleder",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Magasin 1",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Løft av tung transportkasse (beregnet vekt 32 kg) utført manuelt i Magasin 1 uten løftebukk. Brudd på 15 kg grense.",
        "strakstiltak": "Arbeidet stanset umiddelbart. Tralle og jekketralle rekvirert. Ingen akutt personskade rapportert, men hendelsen logget som alvorlig avvik.",
        "ansvarlig_rolle": "Driftsansvarlig",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Sal A",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Alenearbeid i Sal A med over 95 samtidige publikummere i lokalet. Retningslinjen krever minimum 2 verter ved mer enn 80 gjester.",
        "strakstiltak": "Tilkalt ekstra salvert fra Vestibyle. Døren regulert midlertidig for puljeinnslipp.",
        "ansvarlig_rolle": "Seniorvert",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Vaktrom",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Flimmer i takarmatur over kassesystem og monitorer i Vaktrom som forårsaket tretthet og blendingsplager hos vert.",
        "strakstiltak": "LED-driver skiftet samme ettermiddag av bygningstekniker.",
        "ansvarlig_rolle": "Bygningstekniker",
    },
    {
        "avdeling": "Marked",
        "stasjon": "Kafé",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Vannsøl foran kakedisk i Kafé etter rens av kaffemaskin uten utplassering av gult varselskilt.",
        "strakstiltak": "Gulv tørket umiddelbart og sklisikringsmatte lagt ut ved vaskestasjon.",
        "ansvarlig_rolle": "Kaféleder",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Sal C",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Løst gulvteppe ved inngang til Sal C utgjorde snublerisiko for publikum og salverter under omvisning.",
        "strakstiltak": "Teppet festet forskriftsmessig med dobbelsidig scenetape umiddelbart.",
        "ansvarlig_rolle": "Seniorvert",
    },
    {
        "avdeling": "Samling",
        "stasjon": "Konserveringsverksted",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Mangelfull punktavsugfunksjon ved bruk av løsemidler under rensing av forgylt ramme på konserveringsverkstedet.",
        "strakstiltak": "Arbeid med kjemikalier innstilt inntil ventilasjonsfilter ble byttet og godkjent av drift.",
        "ansvarlig_rolle": "Malerikonservator NKF-N",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Vestibyle",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Trekk og lav temperatur (16 grader) ved informasjonsskranken i Vestibylen grunnet defekt luftport over ytterdør.",
        "strakstiltak": "Tilleggsvarmeovn montert bak skranken midlertidig og servicetekniker tilkalt.",
        "ansvarlig_rolle": "Driftsansvarlig",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Kjellergang Vest",
        "alvorlighetsgrad": "KRITISK",
        "beskrivelse": "Sperret rømningsvei i kjellerkorridor mot nødutgang Vest pga. midlertidig mellomlagring av transportemballasje.",
        "strakstiltak": "Kasser fjernet omgående av driftsvakt og plassert på anvist lagerplass.",
        "ansvarlig_rolle": "Sikkerhetsleder / RVR",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Foredragssal",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Overbelastet stikkontakt med seriekoblede skjøteledninger bak AV-racket i Foredragssalen under seminar.",
        "strakstiltak": "Ekstra kurser koblet inn og fast strømskinne montert av sertifisert elektriker.",
        "ansvarlig_rolle": "AV- og utstillingslystekniker",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Sal D",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Montering av spotlight i 4 meters høyde i Sal D utført fra ustø gardintrapp i stedet for godkjent rullestillas.",
        "strakstiltak": "Arbeidet stanset av verneombud. Stillas montert og sikringssele benyttet.",
        "ansvarlig_rolle": "Bygningstekniker / Montør",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Sal E",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Salvert rapporterte om akutte ryggsmerter etter 3 dagers sammenhengende vakt på steingulv i Sal E uten avlastningsmatte.",
        "strakstiltak": "Ergonomisk gummimatte lagt ut bak disk og rotasjon til sittende formidling iverksatt.",
        "ansvarlig_rolle": "Formidlingsleder",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Verksted",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Mangler førstehjelpsskrin i verksted for tre- og metallarbeid; bandasjer og øyeskyllevæske var oppbrukt.",
        "strakstiltak": "Nytt komplett førstehjelpsskrin montert på vegg og rutine for månedssjekk etablert.",
        "ansvarlig_rolle": "HMS- og organisasjonsrådgiver",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Publikumsmottak",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Varsellampe på hjertestarter i publikumsmottak blinket gult (batteri under 20 % restkapasitet).",
        "strakstiltak": "Ny elektrode- og batteripakke satt inn samme dag og funksjonstest loggført.",
        "ansvarlig_rolle": "Sikkerhetsleder / RVR",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Personalinngang",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Glatte trappetrinn av granitt ved personalinngang etter nattefrost; manglende strøing kl. 07:30.",
        "strakstiltak": "Vaktmester strødde med salt og singel umiddelbart. Vinterdriftsavtale presisert overfor entreprenør.",
        "ansvarlig_rolle": "Driftsansvarlig",
    },
    {
        "avdeling": "Marked",
        "stasjon": "Museumsbutikk",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Håndkjerre med defekt hjullager veltet under intern transport av tunge katalogkasser til museumsbutikken.",
        "strakstiltak": "Kjerren kassert og ny tohjuls sekketralle med pneumatiske dekk tatt i bruk.",
        "ansvarlig_rolle": "Museumsbutikkleder",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Sal A",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Høyt støynivå (86 dBA) fra betongsag under ombygging i tilstøtende rom uten utlevering av hørselvern til salvert.",
        "strakstiltak": "Støyende arbeid flyttet til etter stengetid og hørselvern hengt opp i vaktrom.",
        "ansvarlig_rolle": "Driftsansvarlig",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Infobenk Sal A",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Skadet stikkontakt med synlige ledere bak infobenk i Sal A etter påkjørsel av tung rengjøringsmaskin.",
        "strakstiltak": "Strømkurs slått av i sikringsskap, kontakt skiftet og metallbeskyttelsesbøyle montert.",
        "ansvarlig_rolle": "Bygningstekniker / Montør",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Bakgård / Nødutgang",
        "alvorlighetsgrad": "KRITISK",
        "beskrivelse": "Nødutgangsdør mot bakgård var kilt fast med trekloss for lufting under varm ettermiddag.",
        "strakstiltak": "Kloss fjernet og skriftlig påminnelse om forbud mot kiling sendt til alle avdelinger.",
        "ansvarlig_rolle": "Sikkerhetsleder / RVR",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Teknisk mesanin",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Manglende fallsikringskjetting ved lasteåpning på teknisk mesanin over Sal B.",
        "strakstiltak": "Selvlukkende sikkerhetsgrind montert og godkjent av verneombud.",
        "ansvarlig_rolle": "Bygningstekniker",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Hovedtavlerom",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Opphopning av brennbart papiravfall og pappkasser i teknisk rom kloss inntil hovedtavle.",
        "strakstiltak": "Rommet ryddet for brennbart materiale og skilt med 'Lagring forbudt' festet på dør.",
        "ansvarlig_rolle": "Driftsansvarlig",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Sal C",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Salvert i Sal C opplevde verbal hets og truende adferd fra beruset gjest uten at personlig alarm ble fanget opp umiddelbart.",
        "strakstiltak": "Gjest bortvist av vekter. Trådløst alarmsystem resatt og basestasjon testet på nytt.",
        "ansvarlig_rolle": "Seniorvert / Skrankeleder",
    },
    {
        "avdeling": "Kuratering",
        "stasjon": "Møterom Kuratering",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Dårlig ventilasjon og CO2-nivå målt over 1300 ppm i møterom Kuratering etter 4 timers maratonmøte.",
        "strakstiltak": "Ventilasjonsspjeld justert til høyere luftskifte ved full møteromsbooking.",
        "ansvarlig_rolle": "Driftsansvarlig",
    },
    {
        "avdeling": "Marked",
        "stasjon": "Kafékjøkken",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Kondenslekkasje fra kjøleaggregat i kafékjøkken som førte til vått, glatt flisegulv i serveringslinjen.",
        "strakstiltak": "Kondensslange avløpsrenset og tørkeklut stasjonert inntil aggregat var stabilt.",
        "ansvarlig_rolle": "Kaféleder",
    },
    {
        "avdeling": "Samling",
        "stasjon": "Sal A",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Knust glasskuppel på utstillingsmonter i Sal A; glasskår i gangbane ryddet uten foreskrevne kuttsikre hansker.",
        "strakstiltak": "Området avsperret, monter sikret, og kuttsikre hansker hengt opp i vaktbu.",
        "ansvarlig_rolle": "Samlingsforvalter / Registrar",
    },
    {
        "avdeling": "Marked",
        "stasjon": "Hovedinngang",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Feilplassert reklamebukk ved inngangsdør veltet i sterk vind og traff museumsvert i ankelen.",
        "strakstiltak": "Bukk flyttet til skjermet nisje og utstyrt med vanntank for økt ballast.",
        "ansvarlig_rolle": "Kommunikasjons- og markedssjef",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Sal B",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Brannslangepost i 2. etasje delvis blokkert av flyttbare skillevegger midlertidig hensatt etter utstillingsnedrigging.",
        "strakstiltak": "Skillevegger fraktet til fjernlager og 1 meter fri passasje etablert foran skapet.",
        "ansvarlig_rolle": "Sikkerhetsleder / RVR",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Vaktsentral",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Utslitt kontorstol med knekt korsryggstøtte i overvåkningsrom ga vert hodepine og feil sittestilling.",
        "strakstiltak": "Stolen skiftet ut med ergonomisk justerbar 24-timersstol med armlener.",
        "ansvarlig_rolle": "Formidlingsleder",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Trappehus B",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Gjennomtrekk og kraftig slamring med branndør i trappehus B grunnet ubalanse i overtrykksventilasjon.",
        "strakstiltak": "Dørlukker stilt inn med mykere endestopp og luftventiler kalibrert.",
        "ansvarlig_rolle": "Bygningstekniker",
    },
    {
        "avdeling": "Kuratering",
        "stasjon": "Sal B",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Løsemiddellukt fra hurtigtørkende gulvmaling sivet inn i Sal B under museets åpningstid.",
        "strakstiltak": "Malearbeid stanset umiddelbart og utsatt til etter stengetid med mobil avtrekksvifte.",
        "ansvarlig_rolle": "Kurator samtidskunst",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Kjellertrapp toaletter",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Svak belysning (under 40 lux) i trapperom ned til publikumstoaletter etter at to LED-pærer hadde røket.",
        "strakstiltak": "Nye lysrør satt inn innen 30 minutter etter melding.",
        "ansvarlig_rolle": "Bygningstekniker / Montør",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Sal E",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Løst metallokk over gulvboks i Sal E vippet opp og skapte snublerisiko for omvisningsgruppe.",
        "strakstiltak": "Lokk skrudd fast og gummipakning fornyet for å hindre fremtidig forskyvning.",
        "ansvarlig_rolle": "Seniorvert",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Mesanintrapp",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Sprukket håndlist på trapperekkverk mot mesanin ga fare for fliser i håndflaten under gange.",
        "strakstiltak": "List pusset ned, sparklet og lakkert samme kveld.",
        "ansvarlig_rolle": "Bygningstekniker",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Gassrom kjeller",
        "alvorlighetsgrad": "KRITISK",
        "beskrivelse": "Ureglementert oppbevaring av to tomme gassflasker for ugressbrenning i sjaktdør i kjelleren.",
        "strakstiltak": "Gassflasker overført til godkjent låst utendørs gasskap med forskriftsmessig merking.",
        "ansvarlig_rolle": "Drifts- og eiendomssjef",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Renholdsrom 1",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Kjemisk avkalkingsmiddel omstekt på umerket sprayflaske uten datablad eller advarselsmerke.",
        "strakstiltak": "Flaske kassert som farlig avfall. Originalflasker med GHS-faremerking gjeninnført.",
        "ansvarlig_rolle": "Driftsansvarlig",
    },
    {
        "avdeling": "Marked",
        "stasjon": "Varemottak Kafé",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Overfylt spilloljedunk på kjøkkenet medførte fettsøl og akutt sklifare ved varemottaket.",
        "strakstiltak": "Oljesøl sanert med absorberingspulver og ekstra henteavtale bestilt fra renovatør.",
        "ansvarlig_rolle": "Kaféleder",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Sal D",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "To nødlysarmaturer i Sal D slo ikke inn under halvårlig funksjonstest av nødlysanlegget.",
        "strakstiltak": "Batterimoduler i armaturene byttet og godkjent i anleggslogg innen 24 timer.",
        "ansvarlig_rolle": "Sikkerhetsleder / RVR",
    },
    {
        "avdeling": "Formidling",
        "stasjon": "Skranke Vestibyle",
        "alvorlighetsgrad": "LAV",
        "beskrivelse": "Kraftig lav ettermiddagssol mot overvåkingsmonitorer i skranken ga blendingsskjerm og dårlig sikt.",
        "strakstiltak": "Blendingsgardin trukket ned og vinkling på monitorarm justert.",
        "ansvarlig_rolle": "Seniorvert / Skrankeleder",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Lasterampe",
        "alvorlighetsgrad": "HØY",
        "beskrivelse": "Truckfører kjørte med tung kasse inn i sving på varegate uten å avgi varselsignal ved uoversiktlig blindsone.",
        "strakstiltak": "Speil montert i hjørnet og sikkerhetsinstruks for kjøring i fellesareal repetert.",
        "ansvarlig_rolle": "Drifts- og eiendomssjef",
    },
    {
        "avdeling": "Drift",
        "stasjon": "Kjellermagasin",
        "alvorlighetsgrad": "MIDDELS",
        "beskrivelse": "Vekter på kveldsrunde meldte om manglende radiosignal (dødpunkt) i det innerste arkivhvelvet.",
        "strakstiltak": "Ekstern repeater for toveisradio montert i hvelvinngang for å sikre kontinuerlig kontakt.",
        "ansvarlig_rolle": "Sikkerhetsleder / RVR",
    },
]


def load_raw_employees(csv_path: Path | None = None) -> list[dict[str, Any]]:
    """Leser inn listen over ansatte fra arkiv_hr_ansatte.csv."""
    path = csv_path or (DATA_DIR / "arkiv_hr_ansatte.csv")
    if not path.is_file():
        raise FileNotFoundError(f"Fant ikke ansattfil: {path}")

    employees = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            employees.append(row)
    return employees


def generate_skills_matrix(
    employees: list[dict[str, Any]],
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Genererer en fullstendig og deterministisk kompetansematrise for alle ansatte."""
    rng = random.Random(seed)

    # 1. Ferdighetskatalog (14 ferdigheter)
    skills_rows = []
    for s in SKILLS_CATALOG:
        skills_rows.append({
            "skill_code": s["code"],
            "name": s["name"],
            "expires": s["expires"],
            "kategori": s["kategori"],
            "datakilde": "syntetisk (colab_org_bygger)",
        })

    # 2. Personkompetanser (596 rader)
    person_skill_rows = []
    for emp in employees:
        ansatt_id = emp["ansatt_id"]
        avdeling = emp.get("avdeling", "Drift")
        affinities = DEPARTMENT_SKILL_AFFINITY.get(avdeling, ["hms", "forstehjelp"])

        # Hver ansatt får 2-4 kompetanser basert på avdeling
        num_skills = rng.randint(2, min(4, len(affinities)))
        chosen_codes = rng.sample(affinities, num_skills)

        # Alle får generell HMS
        if "hms" not in chosen_codes:
            chosen_codes.append("hms")

        for code in chosen_codes:
            skill_def = next(s for s in SKILLS_CATALOG if s["code"] == code)
            expires = skill_def["expires"]

            if expires:
                # 90 % sjanse for gyldig til 2027/2028, 10 % utløpt (for avvikstesting)
                if rng.random() < 0.10:
                    valid_to = f"2025-{rng.randint(1,12):02d}-15"
                else:
                    valid_to = f"2027-{rng.randint(1,12):02d}-15"
            else:
                valid_to = ""

            certified_date = f"2024-{rng.randint(1,12):02d}-10"

            person_skill_rows.append({
                "ansatt_id": ansatt_id,
                "navn": emp.get("navn", ""),
                "avdeling": avdeling,
                "stilling": emp.get("stilling", ""),
                "skill_code": code,
                "skill_name": skill_def["name"],
                "sertifisert_dato": certified_date,
                "gyldig_til": valid_to,
                "status": "utlopt" if (valid_to and valid_to < "2026-10-01") else "gyldig",
                "datakilde": "syntetisk (colab_org_bygger)",
            })

    return skills_rows, person_skill_rows


def generate_internal_requests(
    employees: list[dict[str, Any]],
    count: int = 60,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Genererer realistiske interne henvendelser forankret i de 14 HR-casene.

    Krav:
    1. Ingen henvendelse datert etter 2026-10-23.
    2. sak_id nummereres i streng datorekkefølge.
    3. Behold kolonner, antall rader (60) og case_ref-fordeling.
    """
    rng = random.Random(seed)
    raw_requests = []
    max_days = (MAX_DATE - START_DATE).days  # Antall dager fram til 2026-10-23

    for _ in range(count):
        emp = rng.choice(employees)
        tpl = rng.choice(HENVELDELSER_TEMPLATES)
        offset = rng.randint(0, max_days)
        d = START_DATE + timedelta(days=offset)
        hour = rng.randint(8, 16)
        minute = rng.choice([0, 15, 30, 45])
        timestamp = f"{d.isoformat()} {hour:02d}:{minute:02d}"

        raw_requests.append({
            "dato_tid": timestamp,
            "ansatt_id": emp["ansatt_id"],
            "navn": emp.get("navn", ""),
            "avdeling": emp.get("avdeling", "Drift"),
            "kategori": tpl["kategori"],
            "tittel": tpl["tittel"],
            "fritekst": tpl["tekst"],
            "case_ref": tpl["case_ref"],
            "paragraf_hjemmel": tpl["paragraf"],
            "forventet_utfall": tpl["forventet_utfall"],
            "datakilde": "syntetisk (colab_org_bygger)",
        })

    # Sorter strengt etter dato_tid for å sikre korrekt kronologi
    raw_requests.sort(key=lambda r: r["dato_tid"])

    # Nummerer sak_id i datorekkefølge
    requests = []
    for i, r in enumerate(raw_requests, start=1):
        ordered_entry = {
            "sak_id": f"SAK-2026-{i:03d}",
            "dato_tid": r["dato_tid"],
            "ansatt_id": r["ansatt_id"],
            "navn": r["navn"],
            "avdeling": r["avdeling"],
            "kategori": r["kategori"],
            "tittel": r["tittel"],
            "fritekst": r["fritekst"],
            "case_ref": r["case_ref"],
            "paragraf_hjemmel": r["paragraf_hjemmel"],
            "forventet_utfall": r["forventet_utfall"],
            "datakilde": r["datakilde"],
        }
        requests.append(ordered_entry)

    return requests


def generate_hms_incidents(count: int = 40, seed: int = 42) -> list[dict[str, Any]]:
    """Genererer detaljerte HMS-avvik for intern drift og arbeidsmiljø.

    Krav:
    1. Ingen avvik datert etter 2026-10-23.
    2. Ingen to HMS-avvik med identisk beskrivelse (alle 40 er unike).
    3. avvik_id nummereres i streng datorekkefølge.
    4. Behold kolonner og antall rader (40).
    """
    rng = random.Random(seed)
    raw_incidents = []
    max_days = (MAX_DATE - START_DATE).days

    if count > len(HMS_INCIDENT_TEMPLATES):
        raise ValueError(f"Forventet maksimalt {len(HMS_INCIDENT_TEMPLATES)} unike HMS-maler, ba om {count}")

    # Bruk de 40 unike malene direkte
    chosen_templates = list(HMS_INCIDENT_TEMPLATES[:count])

    for tpl in chosen_templates:
        offset = rng.randint(0, max_days)
        d = START_DATE + timedelta(days=offset)

        raw_incidents.append({
            "dato": d.isoformat(),
            "avdeling": tpl["avdeling"],
            "stasjon": tpl["stasjon"],
            "alvorlighetsgrad": tpl["alvorlighetsgrad"],
            "beskrivelse": tpl["beskrivelse"],
            "strakstiltak": tpl["strakstiltak"],
            "ansvarlig_rolle": tpl["ansvarlig_rolle"],
            "status": rng.choice(["LUKKET", "LUKKET", "UNDER_OPPFOLGING"]),
            "datakilde": "syntetisk (colab_org_bygger)",
        })

    # Sorter strengt etter dato for å sikre korrekt kronologi
    raw_incidents.sort(key=lambda x: (x["dato"], x["stasjon"]))

    # Nummerer avvik_id i datorekkefølge
    incidents = []
    for i, inc in enumerate(raw_incidents, start=1):
        ordered_entry = {
            "avvik_id": f"AVV-2026-{i:03d}",
            "dato": inc["dato"],
            "avdeling": inc["avdeling"],
            "stasjon": inc["stasjon"],
            "alvorlighetsgrad": inc["alvorlighetsgrad"],
            "beskrivelse": inc["beskrivelse"],
            "strakstiltak": inc["strakstiltak"],
            "ansvarlig_rolle": inc["ansvarlig_rolle"],
            "status": inc["status"],
            "datakilde": inc["datakilde"],
        }
        incidents.append(ordered_entry)

    return incidents


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Skriver en liste av ordbøker til CSV med minimal quoting og UTF-8."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def build_all_internal_datasets(output_dir: Path | None = None) -> dict[str, int]:
    """Hovedfunksjon for å bygge og lagre alle interne organisasjonsdatasett."""
    out = output_dir or DATA_DIR
    out.mkdir(parents=True, exist_ok=True)

    employees = load_raw_employees(out / "arkiv_hr_ansatte.csv")
    skills_catalog, person_skills = generate_skills_matrix(employees)
    requests = generate_internal_requests(employees)
    incidents = generate_hms_incidents()

    write_csv(out / "mock_interne_ferdigheter.csv", skills_catalog)
    write_csv(out / "mock_ansatt_kompetanser.csv", person_skills)
    write_csv(out / "mock_interne_henvendelser.csv", requests)
    write_csv(out / "mock_avvik_hms_tekst.csv", incidents)

    return {
        "ferdigheter": len(skills_catalog),
        "ansatt_kompetanser": len(person_skills),
        "interne_henvendelser": len(requests),
        "hms_avvik": len(incidents),
    }


if __name__ == "__main__":
    result = build_all_internal_datasets()
    print("✅ Genererte interne organisasjonsdata:")
    for k, v in result.items():
        print(f"  - {k}: {v} rader")
