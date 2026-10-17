"""Validerte, syntetiske kilder for en samlet bemanningsuke."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Person(StrictModel):
    id: str
    name: str
    person_type: Literal["employee", "internal_pool", "agency_pool"]
    position_percent: int = Field(ge=0, le=100)
    email: str
    phone: str
    skills: list[str]
    training: dict[str, bool]
    availability: list[tuple[datetime, datetime]]
    source_ids: list[str]
    synthetic: Literal[True]
    employment_start: date | None = None
    employment_end: date | None = None
    department: str | None = None
    title: str | None = None
    field_sources: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_person(self):
        if not self.email.endswith("@example.invalid") or not self.phone.startswith("000"):
            raise ValueError("Kun fiktive kontaktdata er tillatt")
        if any(a >= b for a, b in self.availability):
            raise ValueError("Ugyldig tilgjengelighetsrom")
        if not set(self.training).issubset(self.skills):
            raise ValueError("Opplæring uten dokumentert ferdighet")
        if self.employment_start and self.employment_end and self.employment_end < self.employment_start:
            raise ValueError("Ansettelsesperiode er ugyldig")
        return self


class Activity(StrictModel):
    id: str
    title: str
    kind: Literal["event", "fixed"]
    starts_at: datetime
    ends_at: datetime
    work_start: datetime
    work_end: datetime
    requirements: dict[str, int]
    source_ids: list[str]
    synthetic: Literal[True]

    @model_validator(mode="after")
    def check_times(self):
        if not self.work_start <= self.starts_at < self.ends_at <= self.work_end:
            raise ValueError("Ugyldig aktivitetsrom")
        if any(v <= 0 for v in self.requirements.values()):
            raise ValueError("Rollekrav må være positive")
        return self


class Assignment(StrictModel):
    activity_id: str
    person_id: str
    skill: str
    agreed: bool
    fact_id: str


class Contact(StrictModel):
    activity_id: str
    person_id: str
    status: Literal["ikke_kontaktet", "forespurt", "ja", "nei", "trukket"]
    recorded_at: datetime
    fact_id: str


class PlanningContext(StrictModel):
    version: str
    synthetic: Literal[True]
    weeks: list[date]
    persons: list[Person]
    activities: list[Activity]
    assignments: list[Assignment]
    contacts: list[Contact]
    source_ids: list[str]
    note: str

    @model_validator(mode="after")
    def check_references(self):
        if len(self.weeks) != 4 or any(self.weeks[i + 1] - self.weeks[i] != timedelta(days=7) for i in range(3)):
            raise ValueError("Fire sammenhengende uker er påkrevd")
        people = {p.id: p for p in self.persons}
        acts = {a.id: a for a in self.activities}
        if len(people) != len(self.persons) or len(acts) != len(self.activities):
            raise ValueError("Duplikat-ID")
        for item in [*self.persons, *self.activities]:
            if not set(item.source_ids).issubset(set(self.source_ids) | {"R-03"}):
                raise ValueError("Ukjent kilde-ID")
        for a in self.assignments:
            if a.person_id not in people or a.activity_id not in acts or a.skill not in acts[a.activity_id].requirements:
                raise ValueError("Ukjent tildelingsreferanse")
        for c in self.contacts:
            if c.person_id not in people or c.activity_id not in acts:
                raise ValueError("Ukjent kontaktreferanse")
        return self


class WeekContext(StrictModel):
    version: str
    week_start: date
    persons: list[Person]
    activities: list[Activity]
    assignments: list[Assignment]
    contacts: list[Contact]
    adjacent_assignments: list[Assignment]
    adjacent_activities: list[Activity]


def load_planning_context(path: Path) -> PlanningContext:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    context = PlanningContext.model_validate(data)
    registry_path = Path(__file__).resolve().parents[3] / "04_knowledge/04_domain/projects/hr_simulator/kilder.json"
    registered = {source["id"] for source in json.loads(registry_path.read_text(encoding="utf-8"))}
    if not set(context.source_ids).issubset(registered):
        raise ValueError("Ukjent kilde-ID i kilderegisteret")
    return context


def build_week_context(context: PlanningContext, week_start: date) -> WeekContext:
    if week_start not in context.weeks:
        raise ValueError("Uken finnes ikke i grunnlaget")
    end = week_start + timedelta(days=7)
    activities = [a for a in context.activities if week_start <= a.starts_at.date() < end]
    ids = {a.id for a in activities}
    return WeekContext(version=context.version, week_start=week_start, persons=context.persons,
                       activities=activities, assignments=[a for a in context.assignments if a.activity_id in ids],
                       contacts=[c for c in context.contacts if c.activity_id in ids],
                       adjacent_assignments=[a for a in context.assignments if a.activity_id not in ids],
                       adjacent_activities=[a for a in context.activities if a.id not in ids])
