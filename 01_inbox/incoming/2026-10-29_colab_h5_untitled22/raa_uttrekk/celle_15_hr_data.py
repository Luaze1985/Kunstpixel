import os
import yaml

# Definerer et rikt, høyt detaljert HR-datasett fullstendig uten tall i fritekstene
hr_data = {
    "klassifisering": "syntetisk",
    "syntetisk": True,
    "merknad": "Høydetaljert HR- og kompetansestatus for Kunstpixel, fri for tall i fritekst",
    "kompetanse_matrise": [
        {
          "rolle": "Verneombud",
          "sertifisering": "Grunnkurs i arbeidsmiljø",
          "status": "Godkjent",
          "merknad": "Kurset dekker psykososialt arbeidsmiljø og fysisk vernerunde"
        },
        {
          "rolle": "Kafeansvarlig",
          "sertifisering": "Etablererprøven og skjenkekontroll",
          "status": "Godkjent",
          "merknad": "Nødvendig godkjenning for daglig drift av serveringsstedet"
        },
        {
          "rolle": "Brannvernleder",
          "sertifisering": "Sertifikat for brannvernledere",
          "status": "Godkjent",
          "merknad": "Ansvarlig for dokumentasjon og koordinering av brannøvelser"
        }
    ],
    "onboarding_status": [
        {
          "rolle": "Museumsvert",
          "fase": "Introduksjon",
          "aktivitet": "Gjennomgang av rømningsveier og rutiner ved ulykker",
          "ansvarlig": "Driftsansvarlig"
        },
        {
          "rolle": "Konservator",
          "fase": "Fagopplæring",
          "aktivitet": "Sikkerhetskurs for kjemikaliehåndtering og verneutstyr",
          "ansvarlig": "Samlingsforvalter"
        }
    ],
    "hms_opplaering": [
        {
          "tema": "Ergonomi ved tunge løft",
          "maalgruppe": "Museumsvert",
          "beskrivelse": "Forebyggende opplæring for å unngå belastningsskader under utstillingsarbeid"
        },
        {
          "tema": "Konflikthåndtering og publikumskontakt",
          "maalgruppe": "Museumsvert",
          "beskrivelse": "Kurs i rolig kommunikasjon og deeskalering av krevende situasjoner"
        }
    ]
}

file_path = '/content/h5_bestilling/skjelett/hr_data_realisme.yaml'
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, 'w', encoding='utf-8') as f:
    yaml.dump(hr_data, f, allow_unicode=True, default_flow_style=False)

print("Syntetisk HR-datafil opprettet på:", file_path)
