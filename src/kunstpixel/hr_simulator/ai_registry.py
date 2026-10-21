"""Lesende KI-grunnlag og separate, append-only syntetiske suppleringer."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .staff_data import read_rows
from .store import StateError


class AIRegistry:
    def __init__(self, base: Path, state_path: Path):
        self.base, self.state_path = base, state_path
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS ai_observations (person_id TEXT NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(person_id, revision))')

    def connect(self):
        return sqlite3.connect(self.state_path, timeout=10)

    def dataset(self):
        from .ai_data import load_dataset
        return load_dataset()

    def profiles(self):
        staff = {r['ansatt_id']: r for r in read_rows(self.base / 'staff_source.csv')}
        with self.connect() as db:
            rows = db.execute('SELECT person_id, payload FROM ai_observations ORDER BY revision').fetchall()
        latest = {pid: json.loads(payload) for pid, payload in rows}
        result = []
        for profile in self.dataset()['profiles']:
            p = dict(profile)
            row = staff[p['person_id']]
            p.update(name=row['navn'], title=row['stilling'], position_percent=round(float(row['stillingsprosent']) * 100), revision=0)
            observation = latest.get(p['person_id'])
            if observation:
                p.update({key: observation[key] for key in ('description', 'source', 'competence', 'maturity', 'revision')})
                p['observation_status'] = 'supplemental'
                p['supplemental_date'] = observation['recorded_at']
            else:
                p['observation_status'] = None
            result.append(p)
        return result

    def person(self, pid):
        p = next((p for p in self.profiles() if p['person_id'] == pid), None)
        if p is None:
            raise StateError('unknown_person', 'Ukjent person-ID', 404)
        with self.connect() as db:
            p['history'] = [json.loads(row[0]) for row in db.execute('SELECT payload FROM ai_observations WHERE person_id=? ORDER BY revision', (pid,))]
        p['original_profile'] = next(x for x in self.dataset()['profiles'] if x['person_id'] == pid)
        context_path = self.base / 'hr_context.json'
        context = json.loads(context_path.read_text(encoding='utf-8')) if context_path.exists() else {}
        p['hr_context'] = next((x for x in context.get('people', []) if x['person_id'] == pid), None)
        return p

    def observe(self, pid, observation):
        self.person(pid)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            revision = db.execute('SELECT COALESCE(MAX(revision),0) FROM ai_observations WHERE person_id=?', (pid,)).fetchone()[0]
            if observation['expected_revision'] != revision:
                raise StateError('stale_revision', 'Personen er endret. Last inn på nytt.', 409)
            payload = {k: v for k, v in observation.items() if k != 'expected_revision'}
            payload.update(person_id=pid, revision=revision + 1, recorded_at=datetime.now(timezone.utc).isoformat(), synthetic=True, status='supplemental')
            db.execute('INSERT INTO ai_observations VALUES (?, ?, ?)', (pid, revision + 1, json.dumps(payload, ensure_ascii=False)))
        return self.person(pid)
