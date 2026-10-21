"""Lokalt API for det syntetiske KI-personregisteret."""
from typing import Literal
from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .ai_registry import AIRegistry


class ObservationInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0, strict=True)
    description: str = Field(min_length=1, max_length=10000)
    source: str = Field(min_length=1, max_length=1000)
    competence: int | None = Field(default=None, ge=1, le=5, strict=True)
    maturity: int | None = Field(default=None, ge=1, le=5, strict=True)

    @field_validator('description', 'source')
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError('Tekst må inneholde mer enn mellomrom')
        return value.strip()


def create_router(registry: AIRegistry):
    router = APIRouter(prefix='/api/ai')

    def filtered(query, department, status, tool):
        needle = query.casefold().strip()
        return [p for p in registry.profiles()
                if (not department or department in (p['department_id'], p['department']))
                and (status == 'all' or p['employment_status'] == status)
                and (not tool or tool in p['tools'])
                and (not needle or needle in ' '.join(str(p.get(k, '')) for k in
                    ('person_id', 'name', 'title', 'department', 'description', 'source', 'task_types', 'tools')).casefold())]

    @router.get('/people')
    def people(query: str = Query(default='', max_length=500), department: str = '', status: Literal['all', 'active', 'historical', 'future'] = 'all', tool: str = '',
               page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)):
        rows = filtered(query, department, status, tool)
        start = (page - 1) * page_size
        return {'total': len(rows), 'page': page, 'page_size': page_size, 'people': rows[start:start + page_size]}

    @router.get('/summary')
    def summary(query: str = Query(default='', max_length=500), department: str = '', status: Literal['all', 'active', 'historical', 'future'] = 'all', tool: str = ''):
        data = registry.dataset()
        rows = filtered(query, department, status, tool)
        counts = {'total': len(rows), **{s: sum(p['employment_status'] == s for p in rows) for s in ('active', 'historical', 'future')}}
        counts.update({name: sum(p['knowledge_status'] == key for p in rows) for name, key in
                       [('reported', 'synthetic_report'), ('assumed', 'assumed'), ('unknown', 'unknown'), ('not_applicable', 'not_applicable')]})
        counts['supplemental'] = sum(p['observation_status'] == 'supplemental' for p in rows)
        averages = {}
        for key in ('competence', 'maturity'):
            values = [p[key] for p in rows if p[key] is not None and (p['observation_status'] == 'supplemental' or p['knowledge_status'] not in ('unknown', 'not_applicable'))]
            averages[key] = round(sum(values) / len(values), 2) if values else None
            averages[key + '_count'] = len(values)
        return {'metadata': data['metadata'], 'departments': data['departments'],
                'tools': sorted({t for p in data['profiles'] for t in p['tools']}), 'counts': counts,
                'averages': averages, 'frequencies': [{'frequency': f, 'count': sum(p['frequency'] == f for p in rows)}
                    for f in ('daily', 'weekly', 'monthly', 'never', 'unknown', 'not_applicable')]}

    @router.get('/people/{person_id}')
    def person(person_id: str):
        return registry.person(person_id)

    @router.post('/people/{person_id}/observations')
    def observation(person_id: str, body: ObservationInput):
        return registry.observe(person_id, body.model_dump())

    return router
