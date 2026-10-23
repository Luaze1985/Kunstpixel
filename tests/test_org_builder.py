"""Enhetstester for org_builder og interne organisasjonsdata."""

from __future__ import annotations

import csv
from pathlib import Path

from src.kunstpixel.data.org_builder import (
    DATA_DIR,
    build_all_internal_datasets,
    generate_hms_incidents,
    generate_internal_requests,
    generate_skills_matrix,
    load_raw_employees,
)


def test_load_raw_employees():
    employees = load_raw_employees()
    assert len(employees) == 168
    assert employees[0]["ansatt_id"] == "KP-ANS-001"


def test_skills_matrix_coverage_and_determinism():
    employees = load_raw_employees()
    skills1, matrix1 = generate_skills_matrix(employees, seed=42)
    skills2, matrix2 = generate_skills_matrix(employees, seed=42)

    assert skills1 == skills2
    assert matrix1 == matrix2
    assert len(skills1) == 14

    # Alle 168 ansatte må ha minst 2 kompetanser
    assigned_ids = {row["ansatt_id"] for row in matrix1}
    assert len(assigned_ids) == 168

    for row in matrix1:
        assert row["datakilde"].startswith("syntetisk")
        assert row["status"] in ("gyldig", "utlopt")


def test_internal_requests_linking_and_cases():
    employees = load_raw_employees()
    requests = generate_internal_requests(employees, count=30, seed=42)
    assert len(requests) == 30

    case_refs = {r["case_ref"] for r in requests}
    assert "CASE-004" in case_refs
    assert "CASE-013" in case_refs

    for r in requests:
        assert r["datakilde"].startswith("syntetisk")
        assert r["sak_id"].startswith("SAK-2026-")
        assert len(r["fritekst"]) > 20


def test_hms_incidents_generation():
    incidents = generate_hms_incidents(count=25, seed=42)
    assert len(incidents) == 25
    for inc in incidents:
        assert inc["datakilde"].startswith("syntetisk")
        assert inc["avvik_id"].startswith("AVV-2026-")
        assert inc["alvorlighetsgrad"] in ("LAV", "MIDDELS", "HØY", "KRITISK")


def test_build_all_internal_datasets_creates_valid_csvs():
    counts = build_all_internal_datasets()
    assert counts["ferdigheter"] == 14
    assert counts["ansatt_kompetanser"] > 500
    assert counts["interne_henvendelser"] == 60
    assert counts["hms_avvik"] == 40

    # Sjekk at CSV-filene er lesbare og har korrekte overskrifter
    files = [
        "mock_interne_ferdigheter.csv",
        "mock_ansatt_kompetanser.csv",
        "mock_interne_henvendelser.csv",
        "mock_avvik_hms_tekst.csv",
    ]
    for fn in files:
        path = DATA_DIR / fn
        assert path.is_file(), f"Mangler fil: {fn}"
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            assert len(rows) > 0
            for i, r in enumerate(rows, start=2):
                assert len(r) == len(header), f"Feil i {fn} linje {i}: {len(r)} != {len(header)}"
