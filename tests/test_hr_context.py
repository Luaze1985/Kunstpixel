"""Kildelåst HR-snapshot og grenseverdier for kalenderdager."""
import csv
import json
from pathlib import Path

import pytest

from scripts.export_hr_context import SOURCE_COMMIT, build_context

ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_metadata_coverage_and_known_source_values():
    context = json.loads((ROOT / '05_data/hr_simulator/hr_context.json').read_text())
    with (ROOT / '05_data/hr_simulator/staff_source.csv').open(newline='', encoding='utf-8-sig') as stream:
        ids = {r['ansatt_id'] for r in csv.DictReader(stream)}
    profiles = {r['person_id']: r for r in context['people']}
    assert len(context['people']) == len(ids) == 168
    assert profiles.keys() == ids
    assert context['metadata']['source_commit'] == SOURCE_COMMIT
    assert context['metadata']['synthetic'] is True
    assert context['metadata']['period_from'] == '2026-01-01'
    assert context['metadata']['period_to'] == '2026-10-21'
    # Verifisert separat via konsolideringsgrenens execute_read_query:
    # KP-ANS-003: COUNT(*)=32, SUM(timer)=240; fravær 6+2+2+8 kalenderdager.
    assert profiles['KP-ANS-003']['shift_count'] == 32
    assert profiles['KP-ANS-003']['shift_hours'] == 240
    assert profiles['KP-ANS-003']['absence_days'] == 18
    assert profiles['KP-ANS-001']['shift_count'] == 0
    assert profiles['KP-ANS-001']['shift_hours'] == 0
    assert profiles['KP-ANS-001']['absence_days'] == 34
    assert all(r['source'] == context['metadata']['source'] for r in profiles.values())


def test_absence_union_clips_period_and_employment():
    source = {'people': [{'ansatt_id': 'p', 'ansatt_fra': '2026-01-03', 'ansatt_til': '2026-10-19'}],
              'shifts': [], 'absences': [
                  {'ansatt_id': 'p', 'fra': '2025-12-20', 'til': '2026-01-04'},
                  {'ansatt_id': 'p', 'fra': '2026-01-04', 'til': '2026-01-05'},
                  {'ansatt_id': 'p', 'fra': '2026-10-19', 'til': '2026-11-01'}]}
    profile = build_context(['p'], source)['people'][0]
    assert profile['absence_days'] == 4  # 3., 4., 5. januar og 19. oktober
    assert profile['shift_count'] == profile['shift_hours'] == 0


def test_missing_source_is_unknown_and_id_coverage_is_required():
    assert build_context(['p'], {'people': None, 'shifts': None, 'absences': None})['people'][0]['shift_hours'] is None
    profile = build_context(['p'], {'people': [{'ansatt_id': 'p', 'ansatt_fra': '', 'ansatt_til': ''}],
                                    'shifts': None, 'absences': None})['people'][0]
    assert profile['shift_count'] is None
    assert profile['absence_days'] is None
    with pytest.raises(ValueError, match='mangler'):
        build_context(['p'], {'people': [], 'shifts': [], 'absences': []})
    with pytest.raises(ValueError, match='Duplikat'):
        build_context(['p', 'p'], {'people': None, 'shifts': None, 'absences': None})
