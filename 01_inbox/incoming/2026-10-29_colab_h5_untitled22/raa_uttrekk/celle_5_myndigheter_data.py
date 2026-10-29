import os
import re

# Vi definerer de fylte dataene manuelt for å garantere 100% overholdelse av alle regler (inkludert absolutt ingen tall i noen fritekst, kun tillatte roller, og riktig lengde)

# 1. MYNDIGHETSKONTAKTER
myndigheter_data = {
    "MK-01": {
        "hva_de_vil": "Tilsynet krever dokumentasjon på systematisk helse-, miljø- og sikkerhetsarbeid samt oversikt over vernerunder.",
        "utloser": "Planlagte periodiske kontroller eller meldinger fra ansatte vedrørende arbeidsforhold.",
        "dokumentasyon": "Prosedyrer for risikovurdering, avvikslogger, møtereferater fra arbeidsmiljøutvalget og handlingsplaner."
    },
    "MK-02": {
        "hva_de_vil": "Tilsynet krever trygg mat håndtering og renhold på kjøkkenet samt god sporbarhet på råvarer.",
        "utloser": "Rutinemessige hygienekontroller eller bekymringsmeldinger fra gjester angående matsikkerhet.",
        "dokumentasyon": "Temperaturlogger for kjøleskap, rengjøringsplaner, rutiner for personlig hygiene og skadedyrkontroll."
    },
    "MK-03": {
        "hva_de_vil": "Etaten krever trygge rømningsveier, fungerende slukkeutstyr og dokumentert opplæring i brannvern.",
        "utloser": "Årlige inspeksjoner eller bekymringsmeldinger angående blokkerte nødutganger i lokalene.",
        "dokumentasyon": "Rapporter fra øvelser, servicebøker for brannalarmanlegg og oversikt over brannvernledere."
    },
    "MK-04": {
        "hva_de_vil": "Kommunen krever forsvarlig drift av serveringen samt overholdelse av vilkår for alkoholservering.",
        "utloser": "Søknad om fornyelse av bevillinger eller stikkprøver utført av skjenkekontrollen.",
        "dokumentasyon": "Oversikt over beståtte kunnskapsprøver, opplæringsplaner for ansatte og salgsrapporter."
    },
    "MK-05": {
        "hva_de_vil": "Datatilsynet krever sikker behandling av personopplysninger og tydelig informasjon til de registrerte.",
        "utloser": "Meldinger om brudd på datasikkerheten eller klager fra enkeltpersoner angående innsyn.",
        "dokumentasyon": "Prosedyrer for personvernkonsekvenser, oversikt over databehandlere og logger over tilganger."
    }
}

# 2. TILSYNSBESØK RUTINE
tilsynsbesok_data = {
    "forberedelse": [
        "Sjekke tidligere avvik og hente fram relevante logger for tilsynsobjektet.",
        "Innkalle og koordinere med verneombud og berørte ledere for felles gjennomgang.",
        "Gjøre en rask visuell inspeksjon av de fysiske områdene før kontrollørene ankommer."
    ],
    "gjennomforing": [
        "Vise kontrollørene rundt i lokalene og svare på faglige spørsmål underveis.",
        "Notere alle foreløpige tilbakemeldinger og observasjoner som blir diskutert.",
        "Presentere etterspurt dokumentasjon på en ryddig og oversiktlig måte."
    ],
    "etterarbeid": [
        "Opprette formelle avvik i systemet basert på tilbakemeldingene fra tilsynet.",
        "Utarbeide en konkret tiltaksplan og fordele ansvar for utbedringene.",
        "Sende skriftlig tilbakemelding med dokumentasjon på utbedringer til myndigheten."
    ]
}

# 3. RAPPORTERINGSKALENDER
rapportering_data = {
    "REP-01": {
        "formal": "Sikre oversikt over økonomisk status og gi styringsinformasjon til ledelsen.",
        "mottakere": ["Museumsdirektør", "Styret"],
        "kilder": ["månedsrapport", "regnskapsdata"]
    },
    "REP-02": {
        "formal": "Rapportere inn helse-, miljø- og sikkerhetsarbeidet samt eventuelle skader og avvik.",
        "mottakere": ["Museumsdirektør", "Verneombud"],
        "kilder": ["avvikslogg", "vernerunder"]
    },
    "REP-03": {
        "formal": "Rapportere om besøksutvikling og formidlingsaktiviteter for perioden.",
        "mottakere": ["Museumsdirektør", "Styret"],
        "kilder": ["billettsystem", "skolerapport"]
    },
    "REP-04": {
        "formal": "Gi en helhetlig oppsummering av museets drift, måloppnåelse og økonomi for året.",
        "mottakere": ["Styret", "Kommune"],
        "kilder": ["årsberetning", "revisjonsrapport"]
    }
}

# 4. RAPPORTMALER
rapportmaler_data = {
    "MAL-01": {
        "beskrivelse": "Standard oppsett for månedlig rapportering av økonomiske resultater og budsjettavvik.",
        "bruksanvisning": "Fyll inn faktiske inntekter og utgifter mot budsjett, og forklar vesentlige avvik skriftlig."
    },
    "MAL-02": {
        "beskrivelse": "Mal for registrering og oppfølging av ulykker, nestenulykker og farlige forhold.",
        "bruksanvisning": "Beskriv hendelsen, vurder alvorlighetsgrad, og registrer strakstiltak samt langsiktige løsninger."
    },
    "MAL-03": {
        "beskrivelse": "Strukturert skjema for månedlig rapportering av billettsalg og publikumsfordeling.",
        "bruksanvisning": "Hent data fra billettsystemet, fordel på billettkategorier, og kommenter trender i besøket."
    },
    "MAL-04": {
        "beskrivelse": "Mal for dokumentasjon av vernerunder på museet og i kafeen.",
        "bruksanvisning": "Gå gjennom sjekklisten for fysisk og psykososialt miljø, noter observasjoner og sett frister for tiltak."
    }
}

# 5. ARBEIDSOPPGAVER TIDSBRUK
arbeidsoppgaver_data = {
    "TAS-01": {
        "oppgave": "Daglig drift av kafeen, inkludert renhold, temperaturmåling og kundebehandling.",
        "kommentar": "Arbeidet krever kontinuerlig tilstedeværelse i åpningstiden og streng oppfølging av hygiene."
    },
    "TAS-02": {
        "oppgave": "Gjennomføring av vernerunder og oppfølging av registrerte avvik i HMS-systemet.",
        "kommentar": "Tidsbruken varierer ut fra antall avvik og kompleksiteten i tiltakene som må settes i verk."
    },
    "TAS-03": {
        "oppgave": "Utarbeidelse av vaktlister og generell oppfølging av ansatte på museet.",
        "kommentar": "Planleggingen krever koordinering på tvers av avdelinger for å sikre tilstrekkelig bemanning."
    },
    "TAS-04": {
        "oppgave": "Planlegging og gjennomføring av utstillinger og faglige arrangementer.",
        "kommentar": "Arbeidet innebærer tett samarbeid med eksterne aktører og koordinering av logistikk."
    }
}

# 6. HISTORIKK TEKST (2010 - 2026)
historikk_data = {
    2010: {
        "hendelse": "Etablering av felles rutiner for helse, miljø og sikkerhet på tvers av avdelingene.",
        "laerdom": "Felles standarder gir bedre oversikt og forenkler opplæring av nyansatte."
    },
    2011: {
        "hendelse": "Innføring av systematisk registrering av avvik på det fysiske arbeidsmiljøet.",
        "laerdom": "Tidlig registrering av feil reduserer risikoen for skader på personell."
    },
    2012: {
        "hendelse": "Gjennomgang og oppdatering av alle branninstrukser og rømningsplaner i bygget.",
        "laerdom": "Tydelige instrukser skaper trygghet og sikrer raskere tømming av lokalene."
    },
    2013: {
        "hendelse": "Implementering av digitalt system for temperaturkontroll i serveringsområdet.",
        "laerdom": "Automatisk måling gir bedre kontroll og reduserer faren for matsvinn."
    },
    2014: {
        "hendelse": "Gjennomføring av omfattende ergonomiske tilpasninger på arbeidsplassene.",
        "laerdom": "Riktig utstyr og varierte arbeidsstillinger reduserer sykefraværet blant ansatte."
    },
    2015: {
        "hendelse": "Etablering av faste rutiner for opplæring av verneombud.",
        "laerdom": "God skolering av tillitsvalgte styrker samarbeidet om et trygt arbeidsmiljø."
    },
    2016: {
        "hendelse": "Gjennomføring av ekstern revisjon av museets internkontrollsystem.",
        "laerdom": "Eksterne blikk avdekker svakheter i rutinene som vi selv har oversett."
    },
    2017: {
        "hendelse": "Sertifisering av kafeens rutiner for mathåndtering og hygiene.",
        "laerdom": "Standardiserte prosesser gir tryggere drift og færre avvik ved tilsyn."
    },
    2018: {
        "hendelse": "Oppdatering av risikovurderinger for enslig arbeid og kveldsarbeid.",
        "laerdom": "Tilpassede sikkerhetstiltak gir økt trygghet for ansatte på kveldstid."
    },
    2019: {
        "hendelse": "Gjennomføring av stor felles brannøvelse med alle ansatte og eksterne aktører.",
        "laerdom": "Praktisk trening er avgjørende for at alle skal kjenne sine oppgaver i en krise."
    },
    2020: {
        "hendelse": "Midlertidig stenging av publikumsområder og innføring av strenge smitteverntiltak.",
        "laerdom": "Smidig omstilling og klare instrukser sikrer kontinuitet under uforutsette kriser."
    },
    2021: {
        "hendelse": "Gradvis gjenåpning med begrensede besøkstall og økt fokus på hygiene.",
        "laerdom": "Tydelig kommunikasjon til publikum skaper trygghet og sikrer god flyt i lokalene."
    },
    2022: {
        "hendelse": "Full gjenåpning og evaluering av de midlertidige rutinene som ble innført.",
        "laerdom": "Noen av smitteverntiltakene, som hyppigere renhold, er hensiktsmessige å videreføre."
    },
    2023: {
        "hendelse": "Digitalisering av avvikssystemet for enklere registrering via mobil.",
        "laerdom": "Lavere terskel for rapportering gir bedre oversikt over mindre utfordringer i hverdagen."
    },
    2024: {
        "hendelse": "Revisjon av rutiner for onboarding og opplæring av sesongarbeidere.",
        "laerdom": "Strukturert opplæring fra første dag sikrer raskere integrering og færre feil."
    },
    2025: {
        "hendelse": "Innføring av nye retningslinjer for psykososialt arbeidsmiljø og konflikthåndtering.",
        "laerdom": "Tydelige kjøreregler forebygger misforståelser og fremmer et godt samarbeidsklima."
    },
    2026: {
        "hendelse": "Evaluering av den interne assistentens funksjonalitet og datakvalitet.",
        "laerdom": "Strukturert og oppdatert kildedata er en forutsetning for gode og pålitelige svar."
    }
}

# SKRIV FUNKSJONER FOR Å FINNE OG ERSTATTE
base_path = '/content/h5_bestilling'

def fill_myndighetskontakter():
    path = os.path.join(base_path, 'skjelett\\myndighetskontakter.yaml')
    if not os.path.exists(path):
        path = os.path.join(base_path, 'skjelett/myndighetskontakter.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    current_id = None
    for line in lines:
        id_match = re.search(r'-\s+id:\s+(\S+)', line)
        if id_match:
            current_id = id_match.group(1)

        if 'TODO_FYLL' in line and current_id in myndigheter_data:
            if 'hva_de_vil' in line:
                line = f"  hva_de_vil: '{myndigheter_data[current_id]['hva_de_vil']}'\n"
            elif 'utloser' in line:
                line = f"  utloser: '{myndigheter_data[current_id]['utloser']}'\n"
            elif 'dokumentasjon' in line:
                line = f"  dokumentasjon: '{myndigheter_data[current_id]['dokumentasyon']}'\n"
        new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Ferdig med myndighetskontakter.yaml")

def fill_tilsynsbesok_rutine():
    path = os.path.join(base_path, 'skjelett\\tilsynsbesok_rutine.yaml')
    if not os.path.exists(path):
        path = os.path.join(base_path, 'skjelett/tilsynsbesok_rutine.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    current_phase = None
    for line in lines:
        if 'forberedelse:' in line:
            current_phase = 'forberedelse'
        elif 'gjennomforing:' in line:
            current_phase = 'gjennomforing'
        elif 'etterarbeid:' in line:
            current_phase = 'etterarbeid'

        if 'TODO_FYLL_LISTE' in line and current_phase:
            bullet_lines = [f"  - '{item}'\n" for item in tilsynsbesok_data[current_phase]]
            new_lines.extend(bullet_lines)
            continue
        new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Ferdig med tilsynsbesok_rutine.yaml")

def fill_rapporteringskalender():
    path = os.path.join(base_path, 'skjelett\\rapporteringskalender.yaml')
    if not os.path.exists(path):
        path = os.path.join(base_path, 'skjelett/rapporteringskalender.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    current_id = None
    for line in lines:
        id_match = re.search(r'-\s+id:\s+(\S+)', line)
        if id_match:
            current_id = id_match.group(1)

        if 'TODO_FYLL' in line and current_id in rapportering_data:
            if 'formal' in line:
                line = f"  formal: '{rapportering_data[current_id]['formal']}'\n"
            elif 'mottakere' in line:
                mots = ", ".join([f'"{m}"' for m in rapportering_data[current_id]['mottakere']])
                line = f"  mottakere: [{mots}]\n"
            elif 'kilder' in line:
                kils = ", ".join([f'"{k}"' for k in rapportering_data[current_id]['kilder']])
                line = f"  kilder: [{kils}]\n"
        new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Ferdig med rapporteringskalender.yaml")

def fill_rapportmaler():
    path = os.path.join(base_path, 'skjelett\\rapportmaler.yaml')
    if not os.path.exists(path):
        path = os.path.join(base_path, 'skjelett/rapportmaler.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    current_id = None
    for line in lines:
        id_match = re.search(r'-\s+id:\s+(\S+)', line)
        if id_match:
            current_id = id_match.group(1)

        if 'TODO_FYLL' in line and current_id in rapportmaler_data:
            if 'beskrivelse' in line:
                line = f"  beskrivelse: '{rapportmaler_data[current_id]['beskrivelse']}'\n"
            elif 'bruksanvisning' in line:
                line = f"  bruksanvisning: '{rapportmaler_data[current_id]['bruksanvisning']}'\n"
        new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Ferdig med rapportmaler.yaml")

def fill_arbeidsoppgaver_tidsbruk():
    path = os.path.join(base_path, 'skjelett\\arbeidsoppgaver_tidsbruk.yaml')
    if not os.path.exists(path):
        path = os.path.join(base_path, 'skjelett/arbeidsoppgaver_tidsbruk.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    current_id = None
    for line in lines:
        id_match = re.search(r'-\s+id:\s+(\S+)', line)
        if id_match:
            current_id = id_match.group(1)

        if 'TODO_FYLL' in line and current_id in arbeidsoppgaver_data:
            if 'oppgave' in line:
                line = f"  oppgave: '{arbeidsoppgaver_data[current_id]['oppgave']}'\n"
            elif 'kommentar' in line:
                line = f"  kommentar: '{arbeidsoppgaver_data[current_id]['kommentar']}'\n"
        new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Ferdig med arbeidsoppgaver_tidsbruk.yaml")

def fill_historikk_tekst():
    path = os.path.join(base_path, 'skjelett\\historikk_tekst.yaml')
    if not os.path.exists(path):
        path = os.path.join(base_path, 'skjelett/historikk_tekst.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    current_year = None
    for line in lines:
        year_match = re.search(r'-\s+ar:\s+(\d+)', line)
        if year_match:
            current_year = int(year_match.group(1))

        if 'TODO_FYLL' in line and current_year in historikk_data:
            if 'hendelse' in line:
                line = f"  hendelse: '{historikk_data[current_year]['hendelse']}'\n"
            elif 'laerdom' in line:
                line = f"  laerdom: '{historikk_data[current_year]['laerdom']}'\n"
        new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Ferdig med historikk_tekst.yaml")

# Utfør all fylling
fill_myndighetskontakter()
fill_tilsynsbesok_rutine()
fill_rapporteringskalender()
fill_rapportmaler()
fill_arbeidsoppgaver_tidsbruk()
fill_historikk_tekst()
