"""Objective regression suite: deterministic truth vs uncertain LLM judgements."""
from __future__ import annotations
import copy
import json
import sqlite3
from pathlib import Path
import pytest
from src.kunstpixel.core.hrdemo import init_demo,validate_seed,count_skill,candidates,find_rules

SEED = Path(__file__).resolve().parents[1] / '05_data' / 'hr_demo' / 'seed.json'

@pytest.fixture
def seed():
    return json.loads(SEED.read_text(encoding='utf-8'))

@pytest.fixture
def env(tmp_path):
    master=tmp_path/'master.db'
    with sqlite3.connect(master) as c:
        c.execute('CREATE TABLE museum_invariant(id INTEGER PRIMARY KEY,label TEXT)')
        c.execute("INSERT INTO museum_invariant VALUES (1,'Behold')")
    target=tmp_path/'combined.db'
    init_demo(target,master,SEED)
    return master,target

def test_source_master_immutable(env):
    master,target=env
    with sqlite3.connect(master) as c:
        assert c.execute('SELECT count(*) FROM sqlite_master WHERE name LIKE "hr_%"').fetchone()[0]==0
        assert c.execute('SELECT label FROM museum_invariant').fetchone()[0]=='Behold'
    with sqlite3.connect(target) as c:
        assert c.execute('SELECT count(*) FROM hr_people').fetchone()[0]==12
        assert c.execute('SELECT label FROM museum_invariant').fetchone()[0]=='Behold'

def test_refuses_overwrite(env):
    master,target=env
    with pytest.raises(FileExistsError): init_demo(target,master,SEED)
    with pytest.raises(ValueError): init_demo(master,master,SEED,reset=True)

def test_repeatable_reset(env):
    master,target=env
    before=candidates('2026-11-07',db_path=target)
    init_demo(target,master,SEED,reset=True)
    assert before==candidates('2026-11-07',db_path=target)

def test_skill_deterministic_oracle(env):
    _,target=env
    response=count_skill('kasse','2026-11-07',target)
    assert response['count']==7
    assert len(set(x['id'] for x in response['people']))==7
    assert 'E112' not in [p['id'] for p in response['people']]  # inactive excluded

def test_unknown_skill_explicit(env):
    assert count_skill('xyz','2026-11-07',env[1])['error']=='UNKNOWN_SKILL'

def test_expired_skill_not_counted(env):
    r=count_skill('allergen','2026-11-07',env[1])
    assert 'E109' not in [p['id'] for p in r['people']]
    assert 'E108' not in [p['id'] for p in r['people']]  # unverified

def test_staffing_known_answer(env):
    r=candidates('2026-11-07',db_path=env[1])
    assert r['suggested_ids']==['E101','E102','E106','E103','E111']
    assert r['eligible_count']==6
    assert r['shortage']==0
    assert r['people'][0]['score']==7

def test_crane_qualification_irrelevant(env):
    r=candidates('2026-11-07',db_path=env[1])
    person=next(x for x in r['people'] if x['id']=='E110')
    assert 'kran' in person['documented_skills']
    assert person['relevant_skills']==[]
    assert not person['eligible']

def test_missing_availability_is_unknown(env):
    r=candidates('2026-11-07',db_path=env[1]); p=next(x for x in r['people'] if x['id']=='E107')
    assert p['availability']=='unknown' and 'AVAILABILITY_UNKNOWN' in p['reasons']

def test_partial_shift_is_not_full(env):
    r=candidates('2026-11-07',db_path=env[1]); p=next(x for x in r['people'] if x['id']=='E104')
    assert p['availability']=='partial' and not p['eligible']

def test_verified_vs_unverified(env):
    r=candidates('2026-11-07',db_path=env[1]); p=next(x for x in r['people'] if x['id']=='E108')
    assert 'MISSING_VALID_ALLERGEN' in p['reasons']

def test_shortage_is_explicit(env):
    r=candidates('2026-11-07',need=10,db_path=env[1]);assert r['shortage']==4

def test_rules_cover_domains_and_source(env):
    rules=find_rules(db_path=env[1]);assert len(rules)==8
    assert {r['domain'] for r in rules}=={'HR','HMS','KVALITET'}
    assert all(r['source'] and r['owner_role'] and r['version'] for r in rules)

def test_rules_search_and_dates(env):
    assert [r['id'] for r in find_rules(topic='allergener ved servering',db_path=env[1])]==['KVAL-001']
    assert find_rules(as_of='2025-12-31',db_path=env[1])==[]
    assert len(find_rules(domain='HMS',db_path=env[1]))==3

def test_sql_injection_does_not_mutate(env):
    _,db=env
    assert count_skill("kasse'; DROP TABLE hr_people;--",'2026-11-07',db)['error']=='UNKNOWN_SKILL'
    with sqlite3.connect(db) as c:assert c.execute('SELECT count(*) FROM hr_people').fetchone()[0]==12

def test_invalid_input_rejected(env):
    for req in [('2026-13-40','10:00','16:00'),('2026-11-07','25:00','16:00'),('2026-11-07','16:00','10:00')]:
        with pytest.raises(ValueError): candidates(*req,db_path=env[1])

def test_duplicate_ids_fail(seed):
    seed['people'].append(copy.deepcopy(seed['people'][0]))
    with pytest.raises(ValueError,match='Duplikat'): validate_seed(seed)

def test_dangling_foreign_key_fail(seed):
    seed['person_skills'][0]['person_id']='MISSING'
    with pytest.raises(ValueError,match='referanse'): validate_seed(seed)

def test_missing_evidence_fail(seed):
    seed['person_skills'][0]['evidence']=None
    with pytest.raises(ValueError,match='dokumentasjonskilde'): validate_seed(seed)

def test_unknown_verified_expiring_without_date_fail(seed):
    row=next(x for x in seed['person_skills'] if x['skill_code']=='allergen' and x['verified'])
    row['valid_to']=None
    with pytest.raises(ValueError,match='utløpsdato'): validate_seed(seed)

def test_duplicate_rule_version_fail(seed):
    seed['rules'].append(copy.deepcopy(seed['rules'][0]))
    with pytest.raises(ValueError,match='Duplikat'):validate_seed(seed)

def test_bad_interval_fails(seed):
    seed['availability'][0]['start_time']='17:00'
    with pytest.raises(ValueError,match='Slutt'): validate_seed(seed)

def test_no_db_write_via_query(env):
    _,db=env
    from src.kunstpixel.core.hrdemo import _open
    with _open(db) as c:
        with pytest.raises(sqlite3.OperationalError):c.execute("DELETE FROM hr_people")
