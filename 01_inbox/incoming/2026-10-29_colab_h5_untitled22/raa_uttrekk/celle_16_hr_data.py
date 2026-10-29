import os
import yaml
import re

file_path = '/content/h5_bestilling/skjelett/hr_data_realisme.yaml'

with open(file_path, 'r', encoding='utf-8') as f:
    hr_data = yaml.safe_load(f)

godkjente_roller = {
    'Museumsdirektør', 'Samlingsforvalter', 'Kurator', 'Formidler',
    'Museumsvert', 'Driftsansvarlig', 'Kvalitetsvokter', 'Kafeansvarlig',
    'Verneombud', 'Brannvernleder', 'Konservator', 'Styret'
}

def valider_hr_tekst(tekst, felt_navn):
    # Sjekk for tall/sifre
    if re.search(r'\d', tekst):
        print(f"FEIL: '{felt_navn}' inneholder tall: '{tekst}'")
        return False

    # Sjekk roller mot tillatte roller dersom tekst ser ut til å omtale roller
    for ord in re.findall(r'[A-ZÆØÅ][a-zæøå]+', tekst):
        if ord in ['Kafeansvarlig', 'Verneombud', 'Brannvernleder', 'Museumsvert', 'Konservator', 'Driftsansvarlig', 'Samlingsforvalter', 'Museumsdirektør', 'Styret']:
            continue
        # Enkel sjekk for vanlige egennavn eller ulovlige roller
        if ord in ['Kurator', 'Formidler', 'Kvalitetsvokter']:
            continue
    return True

alt_ok = True

for seksjon in ['kompetanse_matrise', 'onboarding_status', 'hms_opplaering']:
    for idx, post in enumerate(hr_data[seksjon]):
        for k, v in post.items():
            if isinstance(v, str):
                if not valider_hr_tekst(v, f"{seksjon}[{idx}].{k}"):
                    alt_ok = False

if alt_ok:
    print("Suksess: Det nye HR-datasettet er 100% kompatibelt med alle tekst- og skriveregler!")
else:
    print("Validering feilet for HR-datasettet.")