import os
import re

base_path = '/content/h5_bestilling'

# Komplett og utvidet datasett for å dekke absolutt alle TODO_FYLL-forekomster i filene
myndigheter_data = {
    "MK-01": {
        "hva_de_vil": "Tilsynet krever dokumentasjon på systematisk helse-, miljø- og sikkerhetsarbeid samt oversikt over vernerunder.",
        "utloser": "Planlagte periodiske kontroller eller meldinger fra ansatte vedrørende arbeidsforhold.",
        "dokumentasjon": "Prosedyrer for risikovurdering, avvikslogger, møtereferater fra arbeidsmiljøutvalget og handlingsplaner."
    },
    "MK-02": {
        "hva_de_vil": "Tilsynet krever trygg mat håndtering og renhold på kjøkkenet samt god sporbarhet på råvarer.",
        "utloser": "Rutinemessige hygienekontroller eller bekymringsmeldinger fra gjester angående matsikkerhet.",
        "dokumentasjon": "Temperaturlogger for kjøleskap, rengjøringsplaner, rutiner for personlig hygiene og skadedyrkontroll."
    },
    "MK-03": {
        "hva_de_vil": "Etaten krever trygge rømningsveier, fungerende slukkeutstyr og dokumentert opplæring i brannvern.",
        "utloser": "Årlige inspeksjoner eller bekymringsmeldinger angående blokkerte nødutganger i lokalene.",
        "dokumentasjon": "Rapporter fra øvelser, servicebøker for brannalarmanlegg og oversikt over brannvernledere."
    },
    "MK-04": {
        "hva_de_vil": "Kommunen krever forsvarlig drift av serveringen samt overholdelse av vilkår for alkoholservering.",
        "utloser": "Søknad om fornyelse av bevillinger eller stikkprøver utført av skjenkekontrollen.",
        "dokumentasjon": "Oversikt over beståtte kunnskapsprøver, opplæringsplaner for ansatte og salgsrapporter."
    },
    "MK-05": {
        "hva_de_vil": "Datatilsynet krever sikker behandling av personopplysninger og tydelig informasjon til de registrerte.",
        "utloser": "Meldinger om brudd på datasikkerheten eller klager fra enkeltpersoner angående innsyn.",
        "dokumentasjon": "Prosedyrer for personvernkonsekvenser, oversikt over databehandlere og logger over tilganger."
    }
}

tilsynsbesok_data = {
    "forberedelse": [
        {
            "handling": "Verneombud og Driftsansvarlig går gjennom tidligere logger for å sikre at alle kjente avvik er utbedret.",
            "dokumentasjon": "Siste rapporterte avvikslogger, referat fra foregående vernerunder og oversikt over tiltak."
        },
        {
            "handling": "Eier av området varsler berørte ansatte og kaller inn nøkkelpersoner til å delta under selve befaringen.",
            "dokumentasjon": "Innkallinger, oversikt over roller og vaktlister for de aktuelle dagene."
        }
    ],
    "gjennomforing": [
        {
            "handling": "Museumsdirektør og Driftsansvarlig ledsager inspektørene rundt i utstillingene og svarer på spørsmål.",
            "dokumentasjon": "Fysiske plantegninger, skilting av rømningsveier og oversikt over slukkeutstyr."
        },
        {
            "handling": "Kafeansvarlig tar imot representanter i serveringsområdet og viser fram rutinene for mathåndtering.",
            "dokumentasjon": "Egenkontrollskjemaer, temperaturlogger for kjøleutstyr og renholdsprogrammer."
        }
    ],
    "etterarbeid": [
        {
            "handling": "Driftsansvarlig registrerer eventuelle påpekninger som formelle avvik i det interne kvalitetssystemet.",
            "dokumentasjon": "Foreløpig rapport fra tilsynsmyndigheten og opprettede avviksmeldinger."
        },
        {
            "handling": "Museumsdirektør presenterer en konkret tiltaksplan for Styret med tidsfrister og ansvarsfordeling.",
            "dokumentasjon": "Endelig tiltaksplan og skriftlig tilbakemelding til den aktuelle etaten."
        }
    ]
}

# En mer robust funksjon som erstatter linjer basert på nøkkel og mønster
def oppdater_fil(filnavn):
    path = os.path.join(base_path, filnavn)
    if not os.path.exists(path):
        path = os.path.join(base_path, filnavn.replace('\\', '/'))

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Behandle myndighetskontakter.yaml
    if 'myndighetskontakter.yaml' in filnavn:
        for mk_id, info in myndigheter_data.items():
            # Finn blokken for denne id-en og erstatt verdiene
            pattern = r"(- id: " + mk_id + r".*?)(hva_de_vil: '.*?')(.*?)(utloser: '.*?')(.*?)(dokumentasjon: '.*?')"
            def repl(m):
                return (f"{m.group(1)}hva_de_vil: '{info['hva_de_vil']}'"
                        f"{m.group(3)}utloser: '{info['utloser']}'"
                        f"{m.group(5)}dokumentasjon: '{info['dokumentasjon']}'")
            content = re.sub(pattern, repl, content, flags=re.DOTALL)

    # 2. Behandle tilsynsbesok_rutine.yaml
    elif 'tilsynsbesok_rutine.yaml' in filnavn:
        # Vi kan strukturere og bygge opp denne YAML-filen på nytt eller erstatte trinnene
        # Siden strukturen er fast, kan vi fylle inn spesifikt for hver fase
        for fase in ['forberedelse', 'gjennomforing', 'etterarbeid']:
            fase_data = tilsynsbesok_data[fase]
            # Finn alle forekomster av TODO_FYLL innenfor hver fase
            # For enkelthets skyld genererer vi fasene på nytt eller erstatter dem presist
            pattern = r"(id: " + fase[:3].upper() + r"-\d+\s+fase: " + fase + r".*?handling: '.*?'.*?dokumentasjon: '.*?')"
            matches = re.findall(pattern, content, flags=re.DOTALL)
            for idx, match in enumerate(matches):
                if idx < len(fase_data):
                    info = fase_data[idx]
                    new_block = match
                    new_block = re.sub(r"handling: '.*?'", f"handling: '{info['handling']}'", new_block)
                    new_block = re.sub(r"dokumentasjon: '.*?'", f"dokumentasjon: '{info['dokumentasjon']}'", new_block)
                    content = content.replace(match, new_block)

    # Skriv tilbake oppdatert innhold
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Oppdatert {os.path.basename(path)}")

oppdater_fil('skjelett\\myndighetskontakter.yaml')
oppdater_fil('skjelett\\tilsynsbesok_rutine.yaml')
