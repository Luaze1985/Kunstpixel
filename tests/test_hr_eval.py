"""Unit and regression tests for deterministic LLM benchmark evaluation (L01-L03)."""
from __future__ import annotations

import pytest
from src.kunstpixel.core.hr_eval import evaluate_staffing_proposal


def test_evaluator_perfect_match():
    """Verify that the exact oracle answer produces a PASS with precision 1.0 and recall 1.0."""
    res = evaluate_staffing_proposal(['E101', 'E102', 'E106', 'E103', 'E111'])
    assert res['verdict'] == 'PASS'
    assert res['metrics']['precision'] == 1.0
    assert res['metrics']['recall'] == 1.0
    assert res['trapped_errors'] == []
    assert not res['ranking_mismatch']


def test_evaluator_traps_l02_crane_bias():
    """L02: Observer if AI overweights irrelevant skills (crane operator E110)."""
    res = evaluate_staffing_proposal(['E110', 'E101', 'E102'])
    assert res['verdict'] == 'FAIL'
    traps = [t['trap'] for t in res['trapped_errors']]
    assert 'L02_IRRELEVANT_SKILL_BIAS' in traps
    assert 'F07_F08_MISSING_OR_EXPIRED_ALLERGEN' in traps


def test_evaluator_traps_f09_inactive_staff():
    """F09: Inactive employee E112 must be identified and rejected."""
    res = evaluate_staffing_proposal(['E112', 'E101'])
    assert res['verdict'] == 'FAIL'
    traps = [t['trap'] for t in res['trapped_errors']]
    assert 'F09_INACTIVE_EMPLOYEE' in traps


def test_evaluator_traps_l03_unknown_availability():
    """L03: Model assumes missing/unknown availability (E107) means available."""
    res = evaluate_staffing_proposal(['E107', 'E101'])
    assert res['verdict'] == 'FAIL'
    traps = [t['trap'] for t in res['trapped_errors']]
    assert 'L03_UNKNOWN_AVAILABILITY_ASSUMPTION' in traps


def test_evaluator_traps_f05_partial_shift():
    """F05: Model assigns partial shift (E104) to a full 10-16 shift."""
    res = evaluate_staffing_proposal(['E104', 'E101'])
    assert res['verdict'] == 'FAIL'
    traps = [t['trap'] for t in res['trapped_errors']]
    assert 'F05_PARTIAL_SHIFT_MISMATCH' in traps


def test_evaluator_traps_l01_ranking_violation():
    """L01: Employees are eligible, but ranked in wrong order violating preference weights."""
    # E105 has score 1, E101 has score 7. Inverting them should trigger L01
    res = evaluate_staffing_proposal(['E105', 'E101'])
    assert res['verdict'] == 'FAIL'
    assert res['ranking_mismatch'] is True
    traps = [t['trap'] for t in res['trapped_errors']]
    assert 'L01_PREFERENCE_WEIGHTING_VIOLATION' in traps


def test_evaluator_handles_unknown_person_id():
    """Unknown person ID must be flagged safely without unhandled exception."""
    res = evaluate_staffing_proposal(['GHOST_999'])
    assert res['verdict'] == 'FAIL'
    traps = [t['trap'] for t in res['trapped_errors']]
    assert 'UNKNOWN_PERSON' in traps
