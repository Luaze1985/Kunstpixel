from fastapi.testclient import TestClient
from src.kunstpixel.hr_simulator.api import create_app


def client(tmp_path):
    return TestClient(create_app(state_path=tmp_path / 'planning.sqlite3'))


def test_ai_search_summary_filters_and_validation(tmp_path):
    c = client(tmp_path)
    response = c.get('/api/ai/people')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 168
    assert len(data['people']) == 20
    person = data['people'][0]
    assert person['name'] and person['revision'] == 0
    found = c.get('/api/ai/people', params={'query': person['person_id']}).json()
    assert found['total'] == 1
    summary = c.get('/api/ai/summary').json()
    assert summary['counts']['total'] == 168
    assert sum(x['count'] for x in summary['frequencies']) == 168
    filtered = c.get('/api/ai/people', params={'department': person['department_id']}).json()
    assert all(p['department_id'] == person['department_id'] for p in filtered['people'])
    for params in ({'status': 'bogus'}, {'page': 0}, {'page_size': 101}):
        assert c.get('/api/ai/people', params=params).status_code == 422
    assert c.get('/api/ai/people/DOES-NOT-EXIST').status_code == 404


def test_observations_preserve_base_and_survive_restart(tmp_path):
    c = client(tmp_path)
    p = c.get('/api/ai/people').json()['people'][0]
    url = '/api/ai/people/' + p['person_id']
    before = c.get(url).json()
    body = {'expected_revision': 0, 'description': 'Syntetisk supplering zebra',
            'source': 'Fiktivt intervju', 'competence': 4, 'maturity': None}
    saved = c.post(url + '/observations', json=body)
    assert saved.status_code == 200, saved.text
    assert c.post(url + '/observations', json=body).status_code == 409
    after = client(tmp_path).get(url).json()
    assert after['revision'] == 1 and len(after['history']) == 1
    assert after['original_profile']['description'] == before['description']
    assert after['description'] == body['description']
    assert after['observation_status'] == 'supplemental'
    assert after['history'][0]['synthetic'] is True
    assert client(tmp_path).get('/api/ai/people?query=zebra').json()['total'] == 1
    assert c.post(url + '/observations', json={**body, 'competence': 6}).status_code == 422
    assert c.post(url + '/observations', json={**body, 'description': ' '}).status_code == 422
    assert c.post('/api/ai/people/UNKNOWN/observations', json=body).status_code == 404
    second = c.post(url + '/observations', json={**body, 'expected_revision': 1, 'description': 'Andre syntetiske notat'}).json()
    assert second['revision'] == 2
    restarted = client(tmp_path).get(url).json()
    assert [h['revision'] for h in restarted['history']] == [1, 2]
    assert restarted['history'][0]['description'] == body['description']
    assert restarted['original_profile'] == before['original_profile']


def test_supplemental_score_on_unknown_counts_without_changing_usage_status(tmp_path):
    c = client(tmp_path)
    unknown = next(p for p in c.get('/api/ai/people?page_size=100').json()['people'] if p['knowledge_status'] == 'unknown')
    url = '/api/ai/people/' + unknown['person_id']
    before = c.get('/api/ai/summary').json()['averages']['competence_count']
    saved = c.post(url + '/observations', json={'expected_revision': 0, 'description': 'Fiktiv kompetansebeskrivelse',
        'source': 'Syntetisk egenrapport', 'competence': 4, 'maturity': None}).json()
    assert saved['knowledge_status'] == 'unknown'
    assert saved['frequency'] == unknown['frequency']
    assert saved['original_profile']['competence'] is None
    summary = c.get('/api/ai/summary').json()
    assert summary['averages']['competence_count'] == before + 1
    assert summary['counts']['supplemental'] == 1


def test_search_length_is_bounded(tmp_path):
    assert client(tmp_path).get('/api/ai/people', params={'query': 'a' * 501}).status_code == 422


def test_future_employees_can_be_filtered_separately(tmp_path):
    c = client(tmp_path)
    listed = c.get('/api/ai/people', params={'status': 'future'})
    assert listed.status_code == 200
    data = listed.json()
    assert data['total'] == 1
    assert all(p['employment_status'] == 'future' for p in data['people'])
    summary = c.get('/api/ai/summary', params={'status': 'future'})
    assert summary.status_code == 200
    assert summary.json()['counts']['total'] == 1
    assert summary.json()['counts']['future'] == 1
