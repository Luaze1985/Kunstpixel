"""Separate FastMCP tool adapter for the synthetic HR and rules demo.

Uses exactly the same deterministic functions as the local HTTP API.
Run via python -m src.kunstpixel.core.hrdemo_mcp.
"""
from mcp.server.fastmcp import FastMCP
from src.kunstpixel.core.hrdemo import (
    candidates,
    count_skill,
    find_rules,
    get_person,
    list_skills,
)
from src.kunstpixel.core.hr_eval import evaluate_staffing_proposal

mcp = FastMCP('Kunstpixel HR demo')

@mcp.tool()
def count_documented_skill(code: str, as_of: str = '2026-11-07') -> dict:
    """Tell exactly how many active staff have current VERIFIED skill evidence."""
    return count_skill(code,as_of)

@mcp.tool()
def propose_kiosk_staffing(work_date: str = '2026-11-07', start: str = '10:00',
                           end: str = '16:00', need: int = 5) -> dict:
    """Get explicit hard constraints, reproducible relevance score, full evidence and unknowns. Not a decision."""
    return candidates(work_date,start,end,need)

@mcp.tool()
def lookup_hr_hms_quality_rules(domain: str | None = None, topic: str | None = None,
                                as_of: str = '2026-11-07') -> list[dict]:
    """Search structured demo procedures by scope, trigger, owner, version and effective date."""
    return find_rules(domain,topic,as_of)

@mcp.tool()
def get_competence_catalog() -> list[dict]:
    """List all recognized skills, requirements, and expiration rules."""
    return list_skills()

@mcp.tool()
def get_staff_member(person_id: str, as_of: str = '2026-11-07') -> dict:
    """Get full record for an employee, including documented skills and availability."""
    res = get_person(person_id, as_of=as_of)
    if res is None:
        return {'error': 'PERSON_NOT_FOUND', 'person_id': person_id}
    return res

@mcp.tool()
def evaluate_kiosk_proposal(suggested_ids: list[str], work_date: str = '2026-11-07', need: int = 5) -> dict:
    """Deterministically audit a proposed staffing roster against safety constraints and cognitive traps."""
    return evaluate_staffing_proposal(suggested_ids, work_date=work_date, need=need)

if __name__ == '__main__':
    mcp.run()
