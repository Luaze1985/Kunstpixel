"""Domain models for Kunstpixel HR & AI evaluation cases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseDocument:
    """A synthetic case document (email, memo, schedule, incident report)."""
    document_id: str
    case_id: str
    doc_type: str
    data_class: str
    allowed_roles: list[str] = field(default_factory=list)
    untrusted_source: bool = False
    content: str = ""


@dataclass
class Case:
    """An operational HR & AI safety case scenario."""
    case_id: str
    legacy_id: str
    title: str
    sector: str
    theme: str
    priority_score: float
    museum_relevance: str  # SVÆRT HØY, HØY, MIDDELS, LAV
    brief: str
    red_team_trap: str
    expected_safe_response: str
    pass_criteria: str
    handbok_ref: str = ""
    sop_ref: str = ""
    ap9_questions: list[str] = field(default_factory=list)
    ap9_rules: list[str] = field(default_factory=list)
    conversation_refs: list[str] = field(default_factory=list)
    documents: list[CaseDocument] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Verdict and audit trail for a case response."""
    case_id: str
    verdict: str  # PASS or FAIL
    caller_role: str
    trapped_errors: list[dict[str, str]] = field(default_factory=list)
    safe_response_summary: str = ""
    pass_criteria: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "verdict": self.verdict,
            "caller_role": self.caller_role,
            "trapped_errors": self.trapped_errors,
            "safe_response_summary": self.safe_response_summary,
            "pass_criteria": self.pass_criteria,
        }
