"""Eksporter syntetisk HR-kontekst, aldri produktivitet eller effekt av KI.

Kjør fra repoet: python scripts/export_hr_context.py --database /sti/museum.db.
Kildelagets db.py/config.py hentes fra den låste konsolideringscommiten til en
midlertidig mappe. Alle uttrekk går gjennom execute_read_query (SQLite mode=ro)
i en isolert subprocess. Kildedatabasen endres aldri. Fravær teller unionen av
inklusive kalenderdager, klippet til perioden og ansettelsen, ikke arbeidsdager
eller sykefraværsprosent. Manglende tabell/person gir null; en dekket person
uten vakter/fravær gir 0. Registerets ID-er må alle finnes i kildepersonlisten.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = 'ce6fbfc7b3726527f01d3f29e7bc35a441e92059'
PERIOD_FROM = '2026-01-01'
PERIOD_TO = '2026-10-21'
SOURCE = 'origin/hr-konsolidering:05_data/museum.db'


def read_source(database: Path) -> dict:
    """Les kun via den versjonslåste branchens offentlige read-only-funksjon."""
    worker = '''import json, sys
from src.kunstpixel.core.db import execute_read_query
path = sys.argv[1]
def read(sql):
    return [dict(r) for r in execute_read_query(sql, db_path=path)]
tables = {r['name'] for r in read("SELECT name FROM sqlite_master WHERE type='table'")}
queries = {
 'people': ('hr_ansatte', 'SELECT ansatt_id, ansatt_fra, ansatt_til FROM hr_ansatte'),
 'shifts': ('hr_vakter', 'SELECT ansatt_id, dato, timer FROM hr_vakter'),
 'absences': ('hr_fravaer', 'SELECT ansatt_id, fra, til FROM hr_fravaer')}
print(json.dumps({k: read(sql) if table in tables else None for k,(table,sql) in queries.items()}))
'''
    with tempfile.TemporaryDirectory(prefix='kunstpixel-hr-export-') as temporary:
        target = Path(temporary)
        for relative in ['src/__init__.py', 'src/kunstpixel/__init__.py',
                         'src/kunstpixel/core/__init__.py', 'src/kunstpixel/core/db.py',
                         'src/kunstpixel/core/config.py']:
            content = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{relative}'], cwd=ROOT)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        output = subprocess.check_output([sys.executable, '-c', worker, str(database.resolve())], cwd=target)
    return json.loads(output)


def build_context(staff_ids: list[str], source: dict) -> dict:
    if len(staff_ids) != len(set(staff_ids)):
        raise ValueError('Duplikat-ID i personregisteret')
    people = {p['ansatt_id']: p for p in source['people'] or []}
    if source['people'] is not None and set(staff_ids) - people.keys():
        raise ValueError('Personregisteret har ID-er som mangler i kildegrunnlaget')
    first, last = date.fromisoformat(PERIOD_FROM), date.fromisoformat(PERIOD_TO)
    profiles = []
    for pid in staff_ids:
        person = people.get(pid)
        count = hours = absence = None
        if person is not None:
            start = max(first, date.fromisoformat(person['ansatt_fra'])) if person['ansatt_fra'] else first
            end = min(last, date.fromisoformat(person['ansatt_til'])) if person['ansatt_til'] else last
            if source['shifts'] is not None:
                shifts = [r for r in source['shifts'] if r['ansatt_id'] == pid and start <= date.fromisoformat(r['dato']) <= end]
                count, hours = len(shifts), round(sum(r['timer'] for r in shifts), 4)
            if source['absences'] is not None:
                days = set()
                for row in source['absences']:
                    if row['ansatt_id'] != pid:
                        continue
                    a, b = max(start, date.fromisoformat(row['fra'])), min(end, date.fromisoformat(row['til']))
                    days.update(a + timedelta(days=i) for i in range(max(0, (b-a).days + 1)))
                absence = len(days)
        profiles.append(dict(person_id=pid, period_from=PERIOD_FROM, period_to=PERIOD_TO,
                             shift_count=count, shift_hours=hours, absence_days=absence, source=SOURCE))
    return {'metadata': {'source_commit': SOURCE_COMMIT, 'source': SOURCE, 'synthetic': True,
                         'period_from': PERIOD_FROM, 'period_to': PERIOD_TO,
                         'note': 'Syntetiske vakter og fravær, ikke produktivitet eller effekt av KI. Fravær er union av kalenderdager klippet til periode og ansettelse, ikke sykefraværsprosent. Null betyr manglende kildegrunnlag; null vakter i dekket grunnlag gir 0.'},
            'people': profiles}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--staff', type=Path, default=ROOT / '05_data/hr_simulator/staff_source.csv')
    parser.add_argument('--output', type=Path, default=ROOT / '05_data/hr_simulator/hr_context.json')
    args = parser.parse_args()
    with args.staff.open(encoding='utf-8-sig', newline='') as stream:
        staff_ids = [row['ansatt_id'] for row in csv.DictReader(stream)]
    context = build_context(staff_ids, read_source(args.database))
    args.output.write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Eksportert {len(staff_ids)} profiler til {args.output}')


if __name__ == '__main__':
    main()
