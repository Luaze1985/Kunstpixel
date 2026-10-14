"""Syntetisk treningssimulator for HR, arbeidsfordeling og innleie."""

from .engine import (
    create_proposal, decide_proposal, detect_conflicts,
    list_hr_cases, load_scenario, pool_candidates, suggest_actions,
)

__all__ = [
    "create_proposal", "decide_proposal", "detect_conflicts",
    "list_hr_cases", "load_scenario", "pool_candidates", "suggest_actions",
]
