import os
import yaml
import re

base_path = '/content/h5_bestilling'
yaml_files = [
    'skjelett/myndighetskontakter.yaml',
    'skjelett/tilsynsbesok_rutine.yaml',
    'skjelett/rapporteringskalender.yaml',
    'skjelett/rapportmaler.yaml',
    'skjelett/arbeidsoppgaver_tidsbruk.yaml',
    'skjelett/historikk_tekst.yaml',
    'skjelett/hr_data_realisme.yaml'
]

def sjekk(v, f, fil):
    if not isinstance(v, str):
        return True
    r = v
    for p in [r'RP-\d+', r'\d+\s+(dager|timer)', r'Tilsynsbesøk\s+steg\s+\d+', r'MAL-\d+', r'MK-\d+', r'TAS-\d+']:
        r = re.sub(p, '', r)
    if re.search(r'\d', r):
        print('FEIL:', fil, '->', f, 'Inneholder ulovlige tall:', v)
        return False
    if 'TODO_FYLL' in v:
        print('FEIL:', fil, '->', f, 'Uerstattet felt:', v)
        return False
    return True

def valider_alle_tekster():
    alt_ok = True
    for rf in yaml_files:
        p = os.path.join(base_path, rf)
        if not os.path.exists(p):
            p = os.path.join(base_path, rf.replace('/', '\\'))
        if not os.path.exists(p):
            continue
        with open(p, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        def trav(node, sti=''):
            nonlocal alt_ok
            if isinstance(node, dict):
                for k, v in node.items():
                    if k in ['ar', 'id', 'versjon', 'timer', 'prioritet', 'maks_timer', 'tidsbruk_timer', 'gult_avvik_lukkes_innen', 'rodt_avvik_lukkes_innen', 'rapport_id']:
                        continue
                    if isinstance(v, str):
                        if not sjekk(v, f'{sti}.{k}', rf):
                            alt_ok = False
                    else:
                        trav(v, f'{sti}.{k}')
            elif isinstance(node, list):
                for i, el in enumerate(node):
                    if sti.endswith('mottakere') or sti.endswith('brukes_til') or sti.endswith('rapport_id'):
                        continue
                    if isinstance(el, str):
                        if not sjekk(el, f'{sti}[{i}]', rf):
                            alt_ok = False
                    else:
                        trav(el, f'{sti}[{i}]')
        trav(data)

    if alt_ok:
        print('Suksess: Alle fritekster er 100% validert og i samsvar med reglene!')
    else:
        print('Valideringen avdekket avvik i en eller flere filer.')

valider_alle_tekster()