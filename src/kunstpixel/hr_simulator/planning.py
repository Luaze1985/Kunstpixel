"""Regelstyrt ukeplan. Forslag endrer aldri gjeldende plan direkte."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from .context import Activity, Assignment, WeekContext


@dataclass
class CheckResult:
    violations: list[dict[str, Any]] = field(default_factory=list)
    unresolved: list[dict[str, Any]] = field(default_factory=list)
    uncovered: list[dict[str, Any]] = field(default_factory=list)

    @property
    def uncovered_count(self) -> int:
        return sum(item["missing"] for item in self.uncovered)

    def as_dict(self) -> dict[str, Any]:
        return {"violations": self.violations, "unresolved": self.unresolved,
                "uncovered": self.uncovered, "uncovered_count": self.uncovered_count}


@dataclass
class WeekProposal:
    source: str
    context_version: str
    assignments: list[Assignment]
    changes: list[dict[str, Any]]
    review: CheckResult
    rationale: str
    source_ids: list[str]
    missing_information: list[str]
    model: str | None = None
    usage: dict[str, int] | None = None


def _activity(week: WeekContext, activity_id: str) -> Activity:
    for activity in week.activities:
        if activity.id == activity_id:
            return activity
    raise ValueError("Ukjent aktivitet")


def _overlap(left: Activity, right: Activity) -> bool:
    return left.work_start < right.work_end and right.work_start < left.work_end


def _hours(week: WeekContext, assignments: list[Assignment], person_id: str) -> float:
    return sum((_activity(week, a.activity_id).work_end - _activity(week, a.activity_id).work_start).total_seconds() / 3600
               for a in assignments if a.person_id == person_id)


def _limit(person) -> float:
    return 40 * person.position_percent / 100 if person.person_type == "employee" else 40


def _contact_status(week: WeekContext, activity_id: str, person_id: str) -> str:
    contacts = [c for c in week.contacts if c.activity_id == activity_id and c.person_id == person_id]
    return contacts[-1].status if contacts else "ikke_kontaktet"


def _active(person, activity: Activity) -> bool:
    day = activity.starts_at.date()
    return ((person.employment_start is None or person.employment_start <= day)
            and (person.employment_end is None or day <= person.employment_end))


def _counts_for_coverage(week: WeekContext, assignment: Assignment) -> bool:
    person = next((p for p in week.persons if p.id == assignment.person_id), None)
    activity = next((a for a in week.activities if a.id == assignment.activity_id), None)
    return bool(person and activity and _active(person, activity)
                and assignment.skill in person.skills and person.training.get(assignment.skill) is True
                and _contact_status(week, assignment.activity_id, assignment.person_id) not in {"nei", "trukket"})


def candidate_status(week: WeekContext, assignments: list[Assignment], activity_id: str,
                     person_id: str, skill: str) -> dict[str, Any]:
    activity = _activity(week, activity_id)
    person = next((p for p in week.persons if p.id == person_id), None)
    if person is None or skill not in activity.requirements:
        raise ValueError("Ukjent kandidat eller rolle")
    contact = _contact_status(week, activity_id, person_id)
    reasons = []
    if not _active(person, activity):
        reasons.append("ikke ansatt på oppgavedato")
    if skill not in person.skills:
        reasons.append("mangler kompetanse")
    elif person.training.get(skill) is not True:
        reasons.append("opplæring er ikke dokumentert")
    if not any(a <= activity.work_start and b >= activity.work_end for a, b in person.availability):
        reasons.append("mangler kapasitet i hele tidsrommet")
    if any(a.person_id == person_id and _overlap(_activity(week, a.activity_id), activity)
           for a in assignments):
        reasons.append("allerede tildelt samtidig oppgave")
    adjacent = {a.id: a for a in week.adjacent_activities}
    if any(a.person_id == person_id and a.activity_id in adjacent and _overlap(adjacent[a.activity_id], activity)
           for a in week.adjacent_assignments):
        reasons.append("samtidig oppgave i nabouke")
    hours_after = _hours(week, assignments, person_id) + (activity.work_end - activity.work_start).total_seconds() / 3600
    if hours_after > _limit(person):
        reasons.append("overskrider øvelsens avtalte ukekapasitet")
    if contact in {"nei", "trukket"}:
        reasons.append("kontaktstatus er " + contact)
    if person.person_type == "agency_pool":
        reasons.append("ekstern innleie krever egen vurdering")
    return {"person_id": person_id, "name": person.name, "skill": skill, "has_skill": skill in person.skills,
            "training": person.training.get(skill), "available_hours": max(0, _limit(person) - _hours(week, assignments, person_id)),
            "contact_status": contact, "person_type": person.person_type,
            "eligible": not reasons, "reason": ", ".join(reasons) if reasons else "Kompetanse, opplæring og tid er dokumentert i øvingsdata",
            "source_ids": person.source_ids + activity.source_ids,
            "employment_start": person.employment_start, "employment_end": person.employment_end,
            "department": person.department, "title": person.title, "field_sources": person.field_sources,
            "active": _active(person, activity)}


def check_week(week: WeekContext, assignments: list[Assignment]) -> CheckResult:
    result = CheckResult()
    people = {p.id: p for p in week.persons}
    acts = {a.id: a for a in week.activities}
    for assignment in assignments:
        if assignment.activity_id not in acts or assignment.person_id not in people:
            result.violations.append({"kind": "unknown_reference", "fact_id": assignment.fact_id})
            continue
        activity = acts[assignment.activity_id]
        person = people[assignment.person_id]
        if not _active(person, activity):
            result.violations.append({"kind": "employment", "activity_id": activity.id, "person_id": person.id})
        if assignment.skill not in activity.requirements or assignment.skill not in person.skills:
            result.violations.append({"kind": "skill", "activity_id": activity.id, "person_id": person.id})
        if assignment.skill in person.skills and person.training.get(assignment.skill) is not True:
            result.unresolved.append({"kind": "training", "activity_id": activity.id, "person_id": person.id})
        if _contact_status(week, activity.id, person.id) in {"nei", "trukket"}:
            result.unresolved.append({"kind": "withdrawn_assignment", "activity_id": activity.id,
                                      "person_id": person.id, "reason": "Avmeldt vakt må behandles som egen endring"})
        if not any(a <= activity.work_start and b >= activity.work_end for a, b in person.availability):
            result.violations.append({"kind": "availability", "activity_id": activity.id, "person_id": person.id})
    by_person: dict[str, list[Assignment]] = {}
    for assignment in assignments:
        if assignment.activity_id in acts:
            by_person.setdefault(assignment.person_id, []).append(assignment)
    for pid, jobs in by_person.items():
        ordered = sorted(jobs, key=lambda job: acts[job.activity_id].work_start)
        for i, left in enumerate(ordered):
            for right in ordered[i + 1:]:
                a, b = acts[left.activity_id], acts[right.activity_id]
                if _overlap(a, b):
                    result.violations.append({"kind": "overlap", "person_id": pid, "activities": [a.id, b.id]})
                elif b.work_start - a.work_end < timedelta(hours=11):
                    result.unresolved.append({"kind": "rest", "person_id": pid, "activities": [a.id, b.id],
                                              "reason": "Kontroller lokalt avtalegrunnlag"})
        if pid in people and _hours(week, assignments, pid) > _limit(people[pid]):
            result.unresolved.append({"kind": "weekly_hours", "person_id": pid,
                                      "reason": "Mer enn øvelsens avtalte ukekapasitet; kontroller avtale"})
        adjacent = {a.id: a for a in week.adjacent_activities}
        for job in jobs:
            current_activity = acts[job.activity_id]
            for other in week.adjacent_assignments:
                if other.person_id != pid or other.activity_id not in adjacent:
                    continue
                next_activity = adjacent[other.activity_id]
                if _overlap(current_activity, next_activity):
                    result.violations.append({"kind": "overlap", "person_id": pid,
                                              "activities": [current_activity.id, next_activity.id]})
                else:
                    gap = (max(current_activity.work_start, next_activity.work_start) -
                           min(current_activity.work_end, next_activity.work_end))
                    if gap < timedelta(hours=11):
                        result.unresolved.append({"kind": "rest", "person_id": pid,
                                                  "activities": [current_activity.id, next_activity.id],
                                                  "reason": "Hvile over ukegrense må kontrolleres mot avtale"})
    for activity in week.activities:
        for skill, count in activity.requirements.items():
            qualified = sum(a.activity_id == activity.id and a.skill == skill and _counts_for_coverage(week, a)
                            for a in assignments)
            if qualified < count:
                result.uncovered.append({"activity_id": activity.id, "skill": skill, "missing": count - qualified})
            elif qualified > count:
                result.violations.append({"kind": "overstaffed", "activity_id": activity.id, "skill": skill,
                                          "excess": qualified - count})
    # Historikk utenfor fireukersgrunnlaget er ikke kjent.
    if not any(a.starts_at.date() < week.week_start for a in week.adjacent_activities):
        result.unresolved.append({"kind": "history_boundary", "reason": "Tidligere arbeidstid før datavinduet er ukjent"})
    return result


def propose_week(week: WeekContext, current: list[Assignment]) -> WeekProposal:
    planned = list(current)
    changes: list[dict[str, Any]] = []
    for assignment in current:
        if _contact_status(week, assignment.activity_id, assignment.person_id) in {"nei", "trukket"}:
            planned.remove(assignment)
            changes.append({"action": "remove", "activity_id": assignment.activity_id,
                            "person_id": assignment.person_id, "skill": assignment.skill,
                            "fact_id": assignment.fact_id, "reason": "Registrert avmelding krever godkjent fjerning av vakten",
                            "source_ids": _activity(week, assignment.activity_id).source_ids})
    for activity in sorted(week.activities, key=lambda a: a.work_start):
        for skill, count in activity.requirements.items():
            while sum(a.activity_id == activity.id and a.skill == skill and _counts_for_coverage(week, a)
                      for a in planned) < count:
                candidates = [candidate_status(week, planned, activity.id, p.id, skill) for p in week.persons]
                eligible = [c for c in candidates if c["eligible"]]
                eligible.sort(key=lambda c: (c["person_type"] != "employee", c["contact_status"] != "ja",
                                             _limit(next(p for p in week.persons if p.id == c["person_id"])) - c["available_hours"], c["person_id"]))
                if not eligible:
                    break
                candidate = eligible[0]
                fact_id = f"SIM-{activity.id}-{candidate['person_id']}-{skill}"
                planned.append(Assignment(activity_id=activity.id, person_id=candidate["person_id"],
                                          skill=skill, agreed=False, fact_id=fact_id))
                changes.append({"action": "assign", "activity_id": activity.id,
                                "person_id": candidate["person_id"], "skill": skill,
                                "fact_id": fact_id, "reason": candidate["reason"],
                                "source_ids": candidate["source_ids"]})
    review = check_week(week, planned)
    return WeekProposal(source="simulated", context_version=week.version, assignments=planned,
                        changes=changes, review=review,
                        rationale="Foreslår særskilt behandling av avmeldte vakter, beholder øvrige avtalte vakter og prioriterer bekreftet kontakt før jevn fordeling.",
                        source_ids=["R-08", "K-OLJE", "K-NOBEL", "K-TEKNISK-PROGRAM"],
                        missing_information=[i["reason"] for i in review.unresolved if "reason" in i])


def evaluate_proposal(week: WeekContext, current: list[Assignment], proposal: WeekProposal) -> CheckResult:
    if proposal.context_version != week.version:
        raise ValueError("Forslaget bygger på feil grunnlagsversjon")
    if any(change.get("action") not in {"assign", "remove"} for change in proposal.changes):
        raise ValueError("Forslag kan ikke flytte arrangementstid eller gjøre ukjent endring")
    removed = {c["fact_id"] for c in proposal.changes if c["action"] == "remove"}
    current_ids = {a.fact_id for a in current}
    if any(a.fact_id in removed and _contact_status(week, a.activity_id, a.person_id) not in {"nei", "trukket"}
           for a in current):
        raise ValueError("Kun dokumentert avmelding kan foreslås fjernet")
    if current_ids - removed != current_ids & {a.fact_id for a in proposal.assignments}:
        raise ValueError("Eksisterende vakt kan ikke fjernes uten egen endring")
    expected_added = {c["fact_id"] for c in proposal.changes if c["action"] == "assign"}
    if {a.fact_id for a in proposal.assignments} - current_ids != expected_added:
        raise ValueError("Tildeling mangler egen endring")
    review = check_week(week, proposal.assignments)
    if review.violations:
        raise ValueError("Forslaget har harde brudd")
    return review
