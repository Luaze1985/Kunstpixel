#!/usr/bin/env python3
"""Offline integritetssjekk for Kunstpixel-casepakken. Python 3.10+; standardbibliotek."""
from pathlib import Path
import json, re
root=Path(__file__).resolve().parents[1]
original=json.loads((root/'scenario_catalog.json').read_text(encoding='utf-8'))
conversations=json.loads((root/'conversation_training'/'scenario_catalog.json').read_text(encoding='utf-8'))
links=json.loads((root/'conversation_training'/'links_to_hr_cases.json').read_text(encoding='utf-8'))
base=original['cases']; entries=conversations['cases']
assert len(base)==14, len(base)
assert len(entries)==113, len(entries)
assert len({x['id'] for x in entries})==113
assert sum(x['source_status']=='metadata_complete' for x in entries)==112
assert [x['id'] for x in entries if x['source_status']=='incomplete_source']==['VANS-07']
assert len([x for x in entries if x['catalog_group']=='Salg og kundedialog'])==16
assert len(links['links'])==14
known={x['id'] for x in entries}; map_by_id={x['hr_case_id']:x for x in links['links']}
for b in base:
 sid=b['id']; assert sid in map_by_id
 assert re.fullmatch(r'HR-0(?:0[4-9]|1[0-7])',sid)
 assert b['conversation_training_refs']==map_by_id[sid]['conversation_ids']
 single=json.loads((root/'scenarios'/f'{sid}.json').read_text(encoding='utf-8'))
 assert single['id']==sid and single['conversation_training_refs']==b['conversation_training_refs']
 assert all(t in known for t in b['conversation_training_refs'])
for c in entries:
 single=json.loads((root/'conversation_training'/'scenarios'/f"{c['id']}.json").read_text(encoding='utf-8'))
 assert single==c
assert (root/'conversation_training'/'oversikt.html').is_file()
print('OK – 14 HR-case, 113 samtalecase (112 komplette katalogoppføringer, 1 ufullstendig), 14 krysskoblinger.')
