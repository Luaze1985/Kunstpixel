"""Kontrakt, tidsavgrensing og reproduserbarhet for syntetiske KI-profiler."""
import csv
from datetime import date
from pathlib import Path

from src.kunstpixel.hr_simulator import ai_data


ROOT = Path(__file__).resolve().parents[1]


def source_rows():
    with (ROOT / '05_data/hr_simulator/staff_source.csv').open(encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def test_full_source_coverage_and_published_reproducibility():
    rows = source_rows()
    generated = ai_data.generate_dataset(rows)
    assert generated == ai_data.generate_dataset(list(reversed(rows)))
    assert generated == ai_data.load_dataset()
    assert len(generated['profiles']) == 168
    assert {p['person_id'] for p in generated['profiles']} == {r['ansatt_id'] for r in rows}
    assert generated['metadata']['synthetic'] is True
    assert generated['metadata']['reference_date'] == '2026-10-21'


def test_dates_and_nonresponses_do_not_invent_usage():
    dataset = ai_data.load_dataset()
    original = {r['ansatt_id']: r for r in source_rows()}
    statuses = set()
    for p in dataset['profiles']:
        row = original[p['person_id']]
        statuses.add(p['knowledge_status'])
        assert p['synthetic'] is True
        assert p['source'] and p['method'] and p['description']
        if p['observation_date']:
            assert row['ansatt_fra'] <= p['observation_date'] <= (row['ansatt_til'] or '2026-10-21')
        if row['ansatt_til'] and row['ansatt_til'] < '2022-01-01':
            assert p['knowledge_status'] == 'not_applicable'
        if p['knowledge_status'] in {'unknown', 'not_applicable'}:
            assert p['tools'] == []
            assert p['competence'] is None and p['maturity'] is None
            assert p['frequency'] in {'unknown', 'not_applicable'}
        else:
            assert 1 <= p['competence'] <= 5
            assert 1 <= p['maturity'] <= 5
        if p['employment_status'] == 'historical':
            assert p['observation_date'] is None or p['observation_date'] < '2026-10-21'
    assert {'unknown', 'assumed', 'synthetic_report', 'not_applicable'} <= statuses


def test_profile_variation_and_department_grounding():
    d = ai_data.load_dataset()
    departments = {x['id']: x for x in d['departments']}
    assert len(departments) > 3
    assert len({p['frequency'] for p in d['profiles']}) >= 5
    assert len({p['competence'] for p in d['profiles'] if p['competence']}) >= 4
    for p in d['profiles']:
        assert departments[p['department_id']]['name'] == p['department']
        assert departments[p['department_id']]['assumptions']


def test_generation_uses_no_demographics_and_keeps_ids_independent():
    rows = source_rows()
    original = ai_data.generate_dataset(rows)
    changed = [{**r, 'navn': 'Annet navn', 'kjonn': 'annet', 'fodselsaar': '1900'} for r in rows]
    assert ai_data.generate_dataset(changed) == original
    one = ai_data.generate_dataset(rows[:1])['profiles'][0]
    assert one == next(p for p in original['profiles'] if p['person_id'] == one['person_id'])


def test_future_employment_has_no_current_report():
    row = {**source_rows()[0], 'ansatt_fra': '2027-01-01', 'ansatt_til': ''}
    p = ai_data.generate_dataset([row])['profiles'][0]
    assert p['employment_status'] == 'future'
    assert p['observation_date'] is None
    assert p['knowledge_status'] == 'not_applicable'


def test_csv_contains_same_profiles():
    with (ROOT / '05_data/hr_simulator/ai_profiles.csv').open(encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    assert {r['person_id'] for r in rows} == {p['person_id'] for p in ai_data.load_dataset()['profiles']}
