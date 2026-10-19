"""Isolert SQLite-datamodell for syntetisk HR- og bemanningssimulering.

Skal IKKE kobles til museets skrivebeskyttede samlingsdatabase.
"""
import sqlite3

DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    simulated_approval TEXT NOT NULL CHECK (
        simulated_approval IN ('approved', 'not_approved', 'unchecked')
    ),
    synthetic INTEGER NOT NULL CHECK (synthetic = 1)
);
CREATE TABLE IF NOT EXISTS persons (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    person_type TEXT NOT NULL CHECK (
        person_type IN ('employee', 'internal_pool', 'agency_pool')
    ),
    birth_year INTEGER,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    position_percent INTEGER NOT NULL CHECK (position_percent BETWEEN 0 AND 100),
    provider_id TEXT REFERENCES providers(id),
    synthetic INTEGER NOT NULL CHECK (synthetic = 1)
);
CREATE TABLE IF NOT EXISTS person_skills (
    person_id TEXT NOT NULL REFERENCES persons(id),
    skill TEXT NOT NULL,
    PRIMARY KEY (person_id, skill)
);
CREATE TABLE IF NOT EXISTS availability (
    id INTEGER PRIMARY KEY,
    person_id TEXT NOT NULL REFERENCES persons(id),
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    CHECK (starts_at < ends_at)
);
CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    CHECK (starts_at < ends_at)
);
CREATE TABLE IF NOT EXISTS activity_requirements (
    activity_id TEXT NOT NULL REFERENCES activities(id),
    skill TEXT NOT NULL,
    min_count INTEGER NOT NULL CHECK (min_count > 0),
    PRIMARY KEY (activity_id, skill)
);
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY,
    person_id TEXT NOT NULL REFERENCES persons(id),
    activity_id TEXT NOT NULL REFERENCES activities(id),
    UNIQUE(person_id, activity_id)
);
CREATE TABLE IF NOT EXISTS rental_requests (
    id TEXT PRIMARY KEY,
    activity_id TEXT NOT NULL REFERENCES activities(id),
    reason TEXT NOT NULL,
    legal_basis TEXT NOT NULL,
    legal_basis_confirmed INTEGER NOT NULL DEFAULT 0 CHECK (legal_basis_confirmed IN (0, 1)),
    equal_treatment_reviewed INTEGER NOT NULL DEFAULT 0 CHECK (equal_treatment_reviewed IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'review_required'
);
CREATE TABLE IF NOT EXISTS hr_cases (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    confidentiality TEXT NOT NULL CHECK (confidentiality IN ('hr_only', 'manager')),
    state TEXT NOT NULL,
    owner_role TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hr_case_parties (
    case_id TEXT NOT NULL REFERENCES hr_cases(id),
    person_id TEXT NOT NULL REFERENCES persons(id),
    PRIMARY KEY (case_id, person_id)
);
CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    proposal_type TEXT NOT NULL CHECK (proposal_type IN ('move_activity','assign_pool','hr_followup')),
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','approved','rejected')),
    explanation TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_log (
    id INTEGER PRIMARY KEY,
    proposal_id TEXT NOT NULL REFERENCES proposals(id),
    decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
    approver_id TEXT NOT NULL,
    approver_role TEXT NOT NULL,
    rationale TEXT NOT NULL,
    decided_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def open_simulation(path=":memory:"):
    """Åpne en egen skrivbar demo-DB. Lokal fil skal ikke legges i Git."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)
    return conn
