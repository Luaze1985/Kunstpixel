"""Synthetic HR/HMS/quality read model for Kunstpixel.

The checked-in museum.db is NEVER written to. init_demo backs it up to a
throwaway SQLite copy, then loads small deterministic fixtures and rules.
Rules are structured demo policies, not legal determinations.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
MASTER = ROOT / '05_data' / 'museum.db'
SEED = ROOT / '05_data' / 'hr_demo' / 'seed.json'
RUNTIME = ROOT / '.runtime' / 'kunstpixel_demo.db'
SKILL_WEIGHTS = {'kasse': 3, 'kundeservice': 2, 'allergen': 1, 'mattrygghet': 1}
VALID_STATES = {'available', 'unavailable', 'unknown'}

SCHEMA = '''
CREATE TABLE hr_people (
 id TEXT PRIMARY KEY CHECK(length(id)>0), name TEXT NOT NULL CHECK(length(name)>1),
 role TEXT NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)),
 employment TEXT NOT NULL CHECK(employment IN ('fast','deltid','innleie'))
);
CREATE TABLE hr_skills (
 code TEXT PRIMARY KEY, name TEXT NOT NULL, expires INTEGER NOT NULL CHECK(expires IN (0,1))
);
CREATE TABLE hr_person_skill (
 person_id TEXT NOT NULL REFERENCES hr_people(id), skill_code TEXT NOT NULL REFERENCES hr_skills(code),
 verified INTEGER NOT NULL CHECK(verified IN (0,1)), evidence TEXT,
 acquired TEXT, valid_to TEXT,
 PRIMARY KEY(person_id, skill_code),
 CHECK(acquired IS NULL OR acquired GLOB '????-??-??'),
 CHECK(valid_to IS NULL OR valid_to GLOB '????-??-??')
);
CREATE TABLE hr_availability (
 person_id TEXT NOT NULL REFERENCES hr_people(id), work_date TEXT NOT NULL,
 start_time TEXT NOT NULL, end_time TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('available','unavailable','unknown')),
 PRIMARY KEY(person_id,work_date,start_time,end_time),
 CHECK(start_time<end_time)
);
CREATE TABLE hr_rules (
 id TEXT NOT NULL, version INTEGER NOT NULL CHECK(version>0),
 domain TEXT NOT NULL CHECK(domain IN ('HR','HMS','KVALITET')),
 topic TEXT NOT NULL, condition_json TEXT NOT NULL, action_json TEXT NOT NULL,
 owner_role TEXT NOT NULL, deadline TEXT, exception_json TEXT NOT NULL,
 source TEXT NOT NULL, priority INTEGER NOT NULL,
 valid_from TEXT NOT NULL, valid_to TEXT,
 status TEXT NOT NULL CHECK(status IN ('active','draft','superseded')),
 PRIMARY KEY(id,version), CHECK(valid_to IS NULL OR valid_to>=valid_from)
);
CREATE INDEX hr_skills_idx ON hr_person_skill(skill_code,verified,valid_to);
CREATE INDEX hr_rules_idx ON hr_rules(domain,topic,status,valid_from);
'''


def _date(value: str) -> str:
    return date.fromisoformat(value).isoformat()


def _clock(value: str) -> str:
    if len(value) != 5 or value[2] != ':' or not value[:2].isdigit() or not value[3:].isdigit():
        raise ValueError('Klokkeslett må være HH:MM')
    hours, minutes = int(value[:2]), int(value[3:])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError('Ugyldig klokkeslett')
    return value


class ClosingConnection(sqlite3.Connection):
    """Ensure connection is closed on context exit to prevent Windows file lock issues."""
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.close()


def _open(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path or os.environ.get('KUNSTPIXEL_DEMO_DB', RUNTIME)).resolve()
    if not path.is_file():
        raise FileNotFoundError(f'Demobase mangler: {path}. Kjør init_demo først.')
    con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, factory=ClosingConnection)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA query_only=ON')
    return con


def validate_seed(seed: dict[str, Any]) -> None:
    """Validate types, uniqueness, foreign keys and temporal invariants before DB write."""
    required = {'people', 'skills', 'person_skills', 'availability', 'rules'}
    if set(seed) != required:
        raise ValueError(f'Forventet seed-felt: {sorted(required)}')
    def unique(rows: list[dict], fields: tuple[str,...]) -> None:
        seen: set[tuple] = set()
        for row in rows:
            key = tuple(row[f] for f in fields)
            if key in seen:
                raise ValueError(f'Duplikatnøkkel: {key}')
            seen.add(key)
    unique(seed['people'], ('id',))
    unique(seed['skills'], ('code',))
    unique(seed['person_skills'], ('person_id','skill_code'))
    unique(seed['availability'], ('person_id','work_date','start_time','end_time'))
    unique(seed['rules'], ('id','version'))
    people = {p['id'] for p in seed['people']}
    skills = {s['code']: s for s in seed['skills']}
    for p in seed['people']:
        if p['active'] not in (0,1) or p['employment'] not in ('fast','deltid','innleie') or not p['name'].strip():
            raise ValueError(f'Ugyldig person: {p["id"]}')
    for s in seed['skills']:
        if s['expires'] not in (0,1):
            raise ValueError(f'Ugyldig kompetanse: {s["code"]}')
    for item in seed['person_skills']:
        if item['person_id'] not in people or item['skill_code'] not in skills:
            raise ValueError(f'Brutt referanse i kompetanse: {item}')
        if item['verified'] not in (0,1):
            raise ValueError('verified må være 0/1')
        for field in ('acquired','valid_to'):
            if item.get(field) is not None:
                _date(item[field])
        if item['verified'] and not item.get('evidence'):
            raise ValueError('Verifisert kompetanse må ha dokumentasjonskilde')
        if item['verified'] and skills[item['skill_code']]['expires'] and not item.get('valid_to'):
            raise ValueError('Tidsbegrenset kompetanse må ha utløpsdato')
        if item.get('acquired') and item.get('valid_to') and item['valid_to'] < item['acquired']:
            raise ValueError('Kompetanse utløper før den er ervervet')
    for av in seed['availability']:
        if av['person_id'] not in people or av['state'] not in VALID_STATES:
            raise ValueError('Ugyldig tilgjengelighet')
        _date(av['work_date'])
        if _clock(av['start_time']) >= _clock(av['end_time']):
            raise ValueError('Slutt må komme etter start')
    for rule in seed['rules']:
        if rule['domain'] not in ('HR','HMS','KVALITET') or rule['status'] not in ('active','draft','superseded'):
            raise ValueError('Ugyldig regelkategori eller status')
        if type(rule['version']) is not int or rule['version'] < 1 or type(rule['priority']) is not int:
            raise ValueError('Ugyldig versjon eller prioritet')
        _date(rule['valid_from'])
        if rule.get('valid_to') and _date(rule['valid_to']) < rule['valid_from']:
            raise ValueError('Ugyldig gyldighetsintervall')
        if not isinstance(rule['condition'], dict) or not isinstance(rule['actions'], list) or not rule['actions']:
            raise ValueError('Vilkår må være objekt og handlinger ikke-tom liste')
        if not rule['source'] or not rule['owner_role']:
            raise ValueError('Regel mangler kilde eller eier')


def init_demo(target: Path | str = RUNTIME, master: Path | str = MASTER,
              seed_path: Path | str = SEED, reset: bool = False) -> Path:
    """Make one combined runtime DB while keeping tracked original DB untouched."""
    target, master = Path(target).resolve(), Path(master).resolve()
    if target == master:
        raise ValueError('Kan ikke skrive til originaldatabasen')
    if not master.is_file():
        raise FileNotFoundError(master)
    if target.exists() and not reset:
        raise FileExistsError(f'{target} finnes allerede; oppgi reset=True for eksplisitt tilbakestilling')
    seed = json.loads(Path(seed_path).read_text(encoding='utf-8'))
    validate_seed(seed)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + '.initializing')
    if temp.exists():
        temp.unlink()
    try:
        source = sqlite3.connect(master.as_uri() + '?mode=ro', uri=True)
        try:
            dest = sqlite3.connect(temp)
            try:
                source.backup(dest)
            finally:
                dest.close()
        finally:
            source.close()
        con = sqlite3.connect(temp)
        try:
            con.execute('PRAGMA foreign_keys=ON')
            with con:
                con.executescript(SCHEMA)
                con.executemany('INSERT INTO hr_people VALUES (?,?,?,?,?)', [
                    (p['id'],p['name'],p['role'],p['active'],p['employment']) for p in seed['people']])
                con.executemany('INSERT INTO hr_skills VALUES (?,?,?)', [
                    (s['code'],s['name'],s['expires']) for s in seed['skills']])
                con.executemany('INSERT INTO hr_person_skill VALUES (?,?,?,?,?,?)', [
                    (x['person_id'],x['skill_code'],x['verified'],x.get('evidence'),x.get('acquired'),x.get('valid_to'))
                    for x in seed['person_skills']])
                con.executemany('INSERT INTO hr_availability VALUES (?,?,?,?,?)', [
                    (x['person_id'],x['work_date'],x['start_time'],x['end_time'],x['state']) for x in seed['availability']])
                con.executemany('INSERT INTO hr_rules VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [
                    (r['id'],r['version'],r['domain'],r['topic'],json.dumps(r['condition'],ensure_ascii=False),
                     json.dumps(r['actions'],ensure_ascii=False),r['owner_role'],r.get('deadline'),
                     json.dumps(r.get('exceptions',[]),ensure_ascii=False),r['source'],r['priority'],
                     r['valid_from'],r.get('valid_to'),r['status']) for r in seed['rules']])
            if con.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Referanseintegritet feilet')
        finally:
            con.close()
        temp.replace(target)
    finally:
        if temp.exists():
            temp.unlink()
    return target


def count_skill(code: str, as_of: str, db_path: Path | str | None = None) -> dict:
    """Exact count of active people with VERIFIED and CURRENT competence."""
    as_of = _date(as_of)
    with _open(db_path) as con:
        skill = con.execute('SELECT * FROM hr_skills WHERE code=?',(code,)).fetchone()
        if skill is None:
            return {'code': code, 'as_of': as_of, 'count': 0, 'people': [], 'error': 'UNKNOWN_SKILL'}
        rows = con.execute('''SELECT p.id,p.name FROM hr_people p
            JOIN hr_person_skill ps ON ps.person_id=p.id
            WHERE p.active=1 AND ps.skill_code=? AND ps.verified=1
             AND (ps.acquired IS NULL OR ps.acquired<=?)
             AND (ps.valid_to IS NULL OR ps.valid_to>=?)
            ORDER BY p.id''', (code, as_of, as_of)).fetchall()
    return {'code':code,'as_of':as_of,'count':len(rows),'people':[dict(r) for r in rows]}


def candidates(work_date: str, start: str = '10:00', end: str = '16:00',
               need: int = 5, db_path: Path | str | None = None) -> dict:
    """Reproducible evidence, NOT an autonomous personnel decision.

    Synthetic scenario: kiosk shift requires verified current allergen orientation.
    Preference weights are declared, not LLM invented. Unknown != unavailable.
    """
    work_date, start, end = _date(work_date), _clock(start), _clock(end)
    if start >= end or not (1 <= need <= 100):
        raise ValueError('Ugyldig tidsrom eller bemanningsbehov')
    with _open(db_path) as con:
        persons = [dict(r) for r in con.execute('SELECT * FROM hr_people ORDER BY id')]
        skills = [dict(r) for r in con.execute('''SELECT ps.*,s.expires FROM hr_person_skill ps
                   JOIN hr_skills s ON s.code=ps.skill_code''')]
        avs = [dict(r) for r in con.execute('SELECT * FROM hr_availability WHERE work_date=?',(work_date,))]
    result = []
    for person in persons:
        owned = [s for s in skills if s['person_id']==person['id']]
        verified = sorted(s['skill_code'] for s in owned if s['verified']==1
                          and (s['acquired'] is None or s['acquired'] <= work_date)
                          and (s['valid_to'] is None or s['valid_to'] >= work_date))
        slots = [a for a in avs if a['person_id']==person['id']]
        if any(a['state']=='available' and a['start_time']<=start and a['end_time']>=end for a in slots):
            availability = 'available'
        elif any(a['state']=='unavailable' for a in slots):
            availability = 'unavailable'
        elif any(a['state']=='unknown' for a in slots) or not slots:
            availability = 'unknown'
        else:
            availability = 'partial'
        reasons = []
        if not person['active']:
            reasons.append('INACTIVE')
        if availability != 'available':
            reasons.append('AVAILABILITY_'+availability.upper())
        if 'allergen' not in verified:
            reasons.append('MISSING_VALID_ALLERGEN')
        relevant = [s for s in verified if s in SKILL_WEIGHTS]
        result.append({'id':person['id'],'name':person['name'],'availability':availability,
                       'documented_skills':verified,'relevant_skills':relevant,
                       'score':sum(SKILL_WEIGHTS[s] for s in relevant),
                       'eligible':not reasons,'reasons':reasons})
    ranked = sorted((p for p in result if p['eligible']),key=lambda p:(-p['score'],p['id']))
    return {'scenario':'museum_kiosk','work_date':work_date,'start':start,'end':end,
            'need':need,'eligible_count':len(ranked),'shortage':max(0,need-len(ranked)),
            'suggested_ids':[p['id'] for p in ranked[:need]],
            'criteria':{'required':['active','available_full_shift','allergen_verified_current'],
                        'preference_weights':SKILL_WEIGHTS},'people':result,
            'note':'Deterministisk demonstrasjonsrangering, ikke vedtak om bemanning.'}


def find_rules(domain: str | None = None, topic: str | None = None, as_of: str = '2026-11-07',
               db_path: Path | str | None = None) -> list[dict]:
    as_of = _date(as_of)
    if domain and domain not in ('HR','HMS','KVALITET'):
        raise ValueError('Ukjent fagområde')
    with _open(db_path) as con:
        rows = con.execute('''SELECT * FROM hr_rules WHERE status='active' AND valid_from<=?
              AND (valid_to IS NULL OR valid_to>=?) AND (? IS NULL OR domain=?)
              ORDER BY priority DESC,id,version DESC''',(as_of,as_of,domain,domain)).fetchall()
    found=[]
    for r in rows:
        x=dict(r)
        if topic and topic.casefold() not in x['topic'].casefold() and topic.casefold() not in x['id'].casefold():
            continue
        x['condition']=json.loads(x.pop('condition_json'))
        x['actions']=json.loads(x.pop('action_json'))
        x['exceptions']=json.loads(x.pop('exception_json'))
        found.append(x)
    return found


def list_skills(db_path: Path | str | None = None) -> list[dict]:
    """Return complete competence catalog with expiration requirements."""
    with _open(db_path) as con:
        rows = con.execute('SELECT code, name, expires FROM hr_skills ORDER BY code').fetchall()
        return [dict(r) for r in rows]


def list_people(active_only: bool = False, db_path: Path | str | None = None) -> list[dict]:
    """Return staff members with roles and activity status."""
    with _open(db_path) as con:
        query = 'SELECT * FROM hr_people' + (' WHERE active=1' if active_only else '') + ' ORDER BY id'
        rows = con.execute(query).fetchall()
        return [dict(r) for r in rows]


def get_person(person_id: str, as_of: str = '2026-11-07', db_path: Path | str | None = None) -> dict | None:
    """Return detailed person record with documented skills and availability."""
    as_of = _date(as_of)
    with _open(db_path) as con:
        p = con.execute('SELECT * FROM hr_people WHERE id=?', (person_id,)).fetchone()
        if not p:
            return None
        person = dict(p)
        skills = con.execute('''SELECT ps.skill_code, s.name as skill_name, s.expires,
                                       ps.verified, ps.evidence, ps.acquired, ps.valid_to
                                FROM hr_person_skill ps
                                JOIN hr_skills s ON s.code = ps.skill_code
                                WHERE ps.person_id=?
                                ORDER BY ps.skill_code''', (person_id,)).fetchall()
        enriched_skills = []
        for s in skills:
            sk = dict(s)
            is_current = (sk['verified'] == 1 and
                          (sk['acquired'] is None or sk['acquired'] <= as_of) and
                          (sk['valid_to'] is None or sk['valid_to'] >= as_of))
            sk['is_current'] = is_current
            enriched_skills.append(sk)
        person['skills'] = enriched_skills
        avs = con.execute('''SELECT work_date, start_time, end_time, state
                             FROM hr_availability
                             WHERE person_id=?
                             ORDER BY work_date, start_time''', (person_id,)).fetchall()
        person['availability'] = [dict(a) for a in avs]
        return person


HMS_GUIDANCE_FILE = ROOT / "04_knowledge" / "01_governance" / "hms_veiledning_nasjonal.yaml"
_HMS_GUIDANCE_CACHE: list[dict[str, Any]] | None = None


def get_all_hms_guidance() -> list[dict[str, Any]]:
    """Return all 344 authoritative national HMS guidance points from YAML (cached)."""
    global _HMS_GUIDANCE_CACHE
    if _HMS_GUIDANCE_CACHE is None:
        if not HMS_GUIDANCE_FILE.is_file():
            return []
        import yaml
        data = yaml.safe_load(HMS_GUIDANCE_FILE.read_text(encoding="utf-8"))
        _HMS_GUIDANCE_CACHE = data.get("oppslag", [])
    return _HMS_GUIDANCE_CACHE


def search_hms_guidance(
    query: str | None = None,
    topic: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Deterministically search the 344 authoritative national HMS guidance points.

    Args:
        query: Free text query (e.g. 'ergonomi', 'vernerunde', 'ulykke').
        topic: Specific theme filter (e.g. 'Lederansvar', 'Risikovurdering').
        limit: Max results to return (1-50, default 5).

    Returns:
        List of matching guidance entries with id, tema, sporsmal, kort_svar, detaljert_veiledning.
    """
    all_items = get_all_hms_guidance()
    if not all_items:
        return []

    clamped_limit = max(1, min(int(limit), 50))
    q_clean = query.strip().lower() if query and query.strip() else None
    t_clean = topic.strip().lower() if topic and topic.strip() else None

    if not q_clean and not t_clean:
        return all_items[:clamped_limit]

    scored: list[tuple[int, dict[str, Any]]] = []
    q_tokens = [w for w in q_clean.split() if len(w) >= 2] if q_clean else []

    for item in all_items:
        tema = (item.get("tema") or "").lower()
        sporsmal = (item.get("sporsmal") or "").lower()
        kort_svar = (item.get("kort_svar") or "").lower()
        veiledning = (item.get("detaljert_veiledning") or "").lower()
        item_id = (item.get("id") or "").lower()

        if t_clean and t_clean not in tema:
            continue

        score = 0
        if q_clean:
            if q_clean in item_id:
                score += 30
            if q_clean in sporsmal:
                score += 20
            if q_clean in tema:
                score += 15
            if q_clean in kort_svar:
                score += 10
            if q_clean in veiledning:
                score += 5

            for tok in q_tokens:
                if tok in sporsmal:
                    score += 5
                if tok in tema:
                    score += 4
                if tok in kort_svar:
                    score += 3
                if tok in veiledning:
                    score += 1

        if not q_clean:
            score = 10

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:clamped_limit]]


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description='Kunstpixel HR-demo')
    p.add_argument('--init',action='store_true')
    p.add_argument('--reset',action='store_true')
    p.add_argument('--db',default=str(RUNTIME))
    p.add_argument('--report',choices=['kiosk','rules','count','skills','people','person'])
    p.add_argument('--skill',default='kasse')
    p.add_argument('--id',default='E101')
    a=p.parse_args()
    if a.init:
        print(init_demo(a.db,reset=a.reset))
    if a.report:
        if a.report == 'kiosk':
            output = candidates('2026-11-07',db_path=a.db)
        elif a.report == 'rules':
            output = find_rules(db_path=a.db)
        elif a.report == 'skills':
            output = list_skills(db_path=a.db)
        elif a.report == 'people':
            output = list_people(db_path=a.db)
        elif a.report == 'person':
            output = get_person(a.id,db_path=a.db)
        else:
            output = count_skill(a.skill,'2026-11-07',db_path=a.db)
        print(json.dumps(output,ensure_ascii=False,indent=2))
