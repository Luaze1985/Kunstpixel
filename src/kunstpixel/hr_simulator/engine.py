"""Deterministisk HR-simulering: konfliktfunn, innleie-pool og menneskelig godkjenning.

Forslagene er regelbaserte eksempler, IKKE generert av en tilkoblet KI-modell.
All bruk gjelder syntetiske data i en separat øvingsdatabase.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .schema import open_simulation


def load_scenario(path: str | Path) -> sqlite3.Connection:
    """Last inn et 100 % syntetisk scenario i en isolert SQLite-database."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("synthetic") is not True:
        raise ValueError("Bare scenarioer merket synthetic=true er tillatt")
    conn = open_simulation()
    try:
        with conn:
            for vendor in data.get("providers", []):
                if vendor.get("synthetic") is not True:
                    raise ValueError("Leverandører må være syntetiske")
                conn.execute(
                    "INSERT INTO providers(id,name,simulated_approval,synthetic) VALUES(?,?,?,1)",
                    (vendor["id"], vendor["name"], vendor["simulated_approval"]),
                )
            for p in data.get("persons", []):
                if (
                    p.get("synthetic") is not True
                    or not p["email"].endswith("@example.invalid")
                    or not p["phone"].startswith("000")
                ):
                    raise ValueError("Personer må ha tydelige fiktive kontaktdata")
                if p["person_type"] == "agency_pool" and not p.get("provider_id"):
                    raise ValueError("Ekstern pool-kandidat må ha leverandør")
                conn.execute(
                    """INSERT INTO persons(
                        id,name,person_type,birth_year,email,phone,position_percent,
                        provider_id,synthetic
                    ) VALUES(?,?,?,?,?,?,?,?,1)""",
                    (
                        p["id"], p["name"], p["person_type"], p.get("birth_year"),
                        p["email"], p["phone"], p["position_percent"],
                        p.get("provider_id"),
                    ),
                )
                for skill in p.get("skills", []):
                    conn.execute(
                        "INSERT INTO person_skills(person_id,skill) VALUES(?,?)",
                        (p["id"], skill),
                    )
                for starts, ends in p.get("availability", []):
                    conn.execute(
                        "INSERT INTO availability(person_id,starts_at,ends_at) VALUES(?,?,?)",
                        (p["id"], starts, ends),
                    )
            for a in data.get("activities", []):
                conn.execute(
                    "INSERT INTO activities(id,title,starts_at,ends_at) VALUES(?,?,?,?)",
                    (a["id"], a["title"], a["starts_at"], a["ends_at"]),
                )
                for skill, count in a.get("requirements", {}).items():
                    conn.execute(
                        "INSERT INTO activity_requirements(activity_id,skill,min_count) VALUES(?,?,?)",
                        (a["id"], skill, count),
                    )
                for person_id in a.get("assigned", []):
                    conn.execute(
                        "INSERT INTO assignments(person_id,activity_id) VALUES(?,?)",
                        (person_id, a["id"]),
                    )
            for req in data.get("rental_requests", []):
                conn.execute(
                    """INSERT INTO rental_requests(
                        id,activity_id,reason,legal_basis,legal_basis_confirmed,
                        equal_treatment_reviewed,status
                    ) VALUES(?,?,?,?,?,?,?)""",
                    (
                        req["id"], req["activity_id"], req["reason"], req["legal_basis"],
                        int(req.get("legal_basis_confirmed", False)),
                        int(req.get("equal_treatment_reviewed", False)),
                        req.get("status", "review_required"),
                    ),
                )
            for case in data.get("hr_cases", []):
                conn.execute(
                    """INSERT INTO hr_cases(
                        id,category,title,summary,confidentiality,state,owner_role
                    ) VALUES(?,?,?,?,?,?,?)""",
                    (
                        case["id"], case["category"], case["title"], case["summary"],
                        case["confidentiality"], case["state"], case["owner_role"],
                    ),
                )
                for person_id in case.get("parties", []):
                    conn.execute(
                        "INSERT INTO hr_case_parties(case_id,person_id) VALUES(?,?)",
                        (case["id"], person_id),
                    )
        return conn
    except Exception:
        conn.close()
        raise


def _fully_available(conn: sqlite3.Connection, person_id: str, start: str, end: str) -> bool:
    return conn.execute(
        """SELECT 1 FROM availability
           WHERE person_id=? AND starts_at<=? AND ends_at>=? LIMIT 1""",
        (person_id, start, end),
    ).fetchone() is not None


def _skills(conn: sqlite3.Connection, person_id: str) -> set[str]:
    return {
        r["skill"] for r in conn.execute(
            "SELECT skill FROM person_skills WHERE person_id=?", (person_id,)
        )
    }


def detect_conflicts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Returner tekniske konflikter uten å fatte personalbeslutninger."""
    results: list[dict[str, Any]] = []
    assigned = conn.execute(
        """SELECT p.id person_id, a.id activity_id, a.starts_at, a.ends_at
           FROM assignments x
           JOIN persons p ON p.id=x.person_id
           JOIN activities a ON a.id=x.activity_id
           ORDER BY p.id, a.starts_at, a.id"""
    ).fetchall()
    by_person: dict[str, list[sqlite3.Row]] = {}
    for row in assigned:
        by_person.setdefault(row["person_id"], []).append(row)
        if not _fully_available(conn, row["person_id"], row["starts_at"], row["ends_at"]):
            results.append({
                "kind": "availability", "person_id": row["person_id"],
                "activity_id": row["activity_id"],
            })
    for pid, shifts in by_person.items():
        for i, left in enumerate(shifts):
            for right in shifts[i + 1:]:
                if left["starts_at"] < right["ends_at"] and right["starts_at"] < left["ends_at"]:
                    results.append({
                        "kind": "overlap", "person_id": pid,
                        "activities": [left["activity_id"], right["activity_id"]],
                    })
    for req in conn.execute("SELECT * FROM activity_requirements ORDER BY activity_id, skill"):
        people = conn.execute(
            "SELECT person_id FROM assignments WHERE activity_id=?", (req["activity_id"],)
        ).fetchall()
        qualified = sum(req["skill"] in _skills(conn, p["person_id"]) for p in people)
        if qualified < req["min_count"]:
            results.append({
                "kind": "staff_shortage", "activity_id": req["activity_id"],
                "skill": req["skill"], "missing": req["min_count"] - qualified,
            })
    return results


def pool_candidates(conn: sqlite3.Connection, activity_id: str, skill: str) -> list[dict[str, str]]:
    """Vis kompetanse og sperringer. Godkjent i scenario != kontrollert i norsk register."""
    activity = conn.execute(
        "SELECT * FROM activities WHERE id=?", (activity_id,)
    ).fetchone()
    if activity is None:
        raise ValueError("Ukjent aktivitet")
    req = conn.execute(
        "SELECT * FROM rental_requests WHERE activity_id=? LIMIT 1", (activity_id,)
    ).fetchone()
    candidates = []
    people = conn.execute(
        """SELECT p.*, v.simulated_approval
           FROM persons p LEFT JOIN providers v ON p.provider_id=v.id
           WHERE p.person_type IN ('agency_pool','internal_pool')
           ORDER BY p.id"""
    ).fetchall()
    for p in people:
        if skill not in _skills(conn, p["id"]):
            continue
        if not _fully_available(conn, p["id"], activity["starts_at"], activity["ends_at"]):
            status, reason = "unavailable", "Dekker ikke hele tidsrommet"
        elif p["person_type"] == "internal_pool":
            status, reason = "eligible", "Intern ekstravakt: vurder avtale og arbeidstidsregler"
        elif p["simulated_approval"] != "approved":
            status, reason = "blocked", "Bemanningsforetak ikke godkjent i scenarioet"
        elif (req is None or req["legal_basis"] == "unassessed" or not req["legal_basis_confirmed"] or not req["equal_treatment_reviewed"]):
            status, reason = "review_required", "Innleiehjemmel og likebehandling må vurderes av HR"
        else:
            status, reason = "eligible", "Kun godkjent i øvelsesdata; virkelig dokumentasjon kreves"
        candidates.append({
            "person_id": p["id"], "name": p["name"],
            "type": p["person_type"], "status": status, "reason": reason,
        })
    return candidates


def suggest_actions(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Lag forklarbare, regelbaserte utkast; ingen endringer gjøres.

    Dette er foreløpig ikke en LLM. Resultater må opprettes som forslag og
    godkjennes separat før noen aktivitet eller bemanning kan endres.
    """
    from datetime import datetime, timedelta

    suggestions: list[dict[str, Any]] = []
    for issue in detect_conflicts(conn):
        if issue["kind"] == "overlap":
            activities = [
                conn.execute("SELECT * FROM activities WHERE id=?", (aid,)).fetchone()
                for aid in issue["activities"]
            ]
            earlier, later = sorted(activities, key=lambda a: (a["starts_at"], a["id"]))
            end_earlier = datetime.fromisoformat(earlier["ends_at"])
            start_later = datetime.fromisoformat(later["starts_at"])
            end_later = datetime.fromisoformat(later["ends_at"])
            if end_earlier <= start_later:
                continue
            shifted_end = end_earlier + (end_later - start_later)
            new_start = end_earlier.isoformat(timespec="minutes")
            new_end = shifted_end.isoformat(timespec="minutes")
            people = conn.execute(
                "SELECT person_id FROM assignments WHERE activity_id=?", (later["id"],)
            ).fetchall()
            if all(_fully_available(conn, p["person_id"], new_start, new_end) for p in people):
                suggestions.append({
                    "kind": "move_activity",
                    "payload": {"activity_id": later["id"], "new_start": new_start, "new_end": new_end},
                    "explanation": f"Flytt {later['title']} etter {earlier['title']} for å redusere dobbeltbooking",
                    "requires_approval": "director",
                })
        if issue["kind"] == "staff_shortage":
            candidates = pool_candidates(conn, issue["activity_id"], issue["skill"])
            permitted = [p for p in candidates if p["status"] in ("eligible", "review_required")]
            permitted.sort(key=lambda p: (p["status"] != "eligible", p["type"] != "internal_pool", p["person_id"]))
            if permitted:
                pick = permitted[0]
                suggestions.append({
                    "kind": "assign_pool",
                    "payload": {
                        "activity_id": issue["activity_id"],
                        "person_id": pick["person_id"],
                        "skill": issue["skill"],
                    },
                    "explanation": f"Vurder {pick['name']} for {issue['activity_id']}. {pick['reason']}",
                    "candidate_status": pick["status"],
                    "requires_approval": "hr",
                })
    for case in conn.execute("SELECT id,title FROM hr_cases WHERE state='new' ORDER BY id"):
        suggestions.append({
            "kind": "hr_followup",
            "payload": {"case_id": case["id"]},
            "explanation": f"Start nøytral faktaundersøkelse for {case['id']}; hør alle involverte",
            "requires_approval": "hr",
            "confidential": True,
        })
    return suggestions


def list_hr_cases(conn: sqlite3.Connection, viewer_role: str) -> list[dict[str, str]]:
    """HR-only-felter utleveres aldri i generell bemanningsoversikt."""
    if viewer_role not in ("hr", "director", "manager"):
        return []
    rows = conn.execute("SELECT * FROM hr_cases ORDER BY id").fetchall()
    output = []
    for row in rows:
        if row["confidentiality"] == "hr_only" and viewer_role != "hr":
            output.append({"id": row["id"], "state": "restricted"})
        else:
            output.append({
                "id": row["id"], "title": row["title"],
                "summary": row["summary"], "state": row["state"],
            })
    return output


def create_proposal(
    conn: sqlite3.Connection, proposal_id: str, proposal_type: str,
    payload: dict[str, str], explanation: str,
) -> None:
    """Opprett utkast. En forslagstekst har ingen skrivetilgang til arbeidsplanen."""
    if proposal_type not in ("move_activity", "assign_pool", "hr_followup"):
        raise ValueError("Ikke tillatt forslagstype")
    with conn:
        conn.execute(
            """INSERT INTO proposals(id,proposal_type,payload_json,status,explanation)
               VALUES(?,?,?,'pending',?)""",
            (proposal_id, proposal_type, json.dumps(payload, ensure_ascii=False), explanation),
        )


def _apply_approved(conn: sqlite3.Connection, kind: str, payload: dict[str, str]) -> None:
    if kind == "move_activity":
        activity_id = payload["activity_id"]
        new_start, new_end = payload["new_start"], payload["new_end"]
        if new_start >= new_end:
            raise ValueError("Ugyldig tidsrom")
        current = conn.execute("SELECT * FROM activities WHERE id=?", (activity_id,)).fetchone()
        if current is None or new_start[:10] != current["starts_at"][:10]:
            raise ValueError("Flytting kan bare skje innen samme dag i MVP")
        participants = conn.execute(
            "SELECT person_id FROM assignments WHERE activity_id=?", (activity_id,)
        ).fetchall()
        if not all(_fully_available(conn, p["person_id"], new_start, new_end) for p in participants):
            raise ValueError("Ikke alle tildelte ansatte er tilgjengelige")
        before = len(detect_conflicts(conn))
        conn.execute(
            "UPDATE activities SET starts_at=?, ends_at=? WHERE id=?",
            (new_start, new_end, activity_id),
        )
        if len(detect_conflicts(conn)) >= before:
            raise ValueError("Forslaget reduserer ikke antall konflikter")
    elif kind == "assign_pool":
        candidate_id, activity_id, skill = (
            payload["person_id"], payload["activity_id"], payload["skill"]
        )
        candidate = next(
            (p for p in pool_candidates(conn, activity_id, skill) if p["person_id"] == candidate_id),
            None,
        )
        if not candidate or candidate["status"] != "eligible":
            raise ValueError("Kandidat kan ikke tildeles uten alle kontroller")
        needed = conn.execute(
            "SELECT 1 FROM activity_requirements WHERE activity_id=? AND skill=?",
            (activity_id, skill),
        ).fetchone()
        if not needed:
            raise ValueError("Kompetansen etterspørres ikke i aktiviteten")
        before = len(detect_conflicts(conn))
        conn.execute(
            "INSERT INTO assignments(person_id,activity_id) VALUES(?,?)",
            (candidate_id, activity_id),
        )
        if len(detect_conflicts(conn)) >= before:
            raise ValueError("Tildelingen fjerner ikke en konflikt")
    elif kind == "hr_followup":
        case_id = payload["case_id"]
        row = conn.execute("SELECT state FROM hr_cases WHERE id=?", (case_id,)).fetchone()
        if row is None or row["state"] != "new":
            raise ValueError("Saken finnes ikke eller er allerede behandlet")
        # Bare utredning – systemet avgjør ikke skyld eller personalreaksjoner.
        conn.execute("UPDATE hr_cases SET state='factfinding' WHERE id=?", (case_id,))
    else:
        raise ValueError("Ukjent forslagstype")


def decide_proposal(
    conn: sqlite3.Connection, proposal_id: str, decision: str,
    approver_id: str, approver_role: str, rationale: str,
) -> None:
    """Godkjenning skjer kun ved eksplisitt menneskelig handling i simulatoren.

    Role-parametere er demo-data og erstatter IKKE autentisering eller tilgangsstyring.
    """
    if not approver_id.strip() or not rationale.strip():
        raise ValueError("Beslutning krever identifikator og begrunnelse")
    if decision not in ("approved", "rejected") or approver_role not in ("hr", "director"):
        raise PermissionError("Beslutning krever autorisert HR- eller lederrolle")
    row = conn.execute("SELECT * FROM proposals WHERE id=?", (proposal_id,)).fetchone()
    if row is None or row["status"] != "pending":
        raise ValueError("Forslaget finnes ikke eller er allerede behandlet")
    if row["proposal_type"] in ("hr_followup", "assign_pool") and approver_role != "hr":
        raise PermissionError("HR-oppfølging og innleie krever HR-rolle i simuleringen")
    with conn:
        if decision == "approved":
            _apply_approved(conn, row["proposal_type"], json.loads(row["payload_json"]))
        conn.execute("UPDATE proposals SET status=? WHERE id=?", (decision, proposal_id))
        conn.execute(
            """INSERT INTO decision_log(proposal_id,decision,approver_id,approver_role,rationale)
               VALUES(?,?,?,?,?)""",
            (proposal_id, decision, approver_id, approver_role, rationale),
        )
