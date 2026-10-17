"""Kjør: python -m src.kunstpixel.hr_simulator [HR-001|HR-002|HR-003]"""
import json
import sys
from pathlib import Path

from .engine import detect_conflicts, list_hr_cases, load_scenario, pool_candidates, suggest_actions


def main():
    scenario_id = sys.argv[1] if len(sys.argv) > 1 else "HR-001"
    if scenario_id == "web":
        import uvicorn
        uvicorn.run("src.kunstpixel.hr_simulator.api:create_app", factory=True,
                    host="127.0.0.1", port=8001, reload=False)
        return
    if scenario_id not in {"HR-001", "HR-002", "HR-003"}:
        raise SystemExit("Velg web, HR-001, HR-002 eller HR-003")
    root = Path(__file__).resolve().parents[3]
    path = root / "05_data/hr_simulator/scenarios" / f"{scenario_id}.json"
    conn = load_scenario(path)
    try:
        print(json.dumps({
            "scenario": scenario_id,
            "conflicts": detect_conflicts(conn),
            "suggestions": suggest_actions(conn),
            "rental_pool": pool_candidates(conn, "A-EVENING", "vertskap")
                if scenario_id in ("HR-001", "HR-003") else [],
            "hr_cases_redacted": list_hr_cases(conn, "director"),
            "notice": "Fiktiv simulering – ingen ekte HR-data eller lovlighetsavgjørelser.",
        }, ensure_ascii=False, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
