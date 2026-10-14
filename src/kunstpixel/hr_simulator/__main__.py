"""Kjør: python -m src.kunstpixel.hr_simulator [HR-001|HR-002]"""
import json
import sys
from pathlib import Path

from .engine import detect_conflicts, list_hr_cases, load_scenario, pool_candidates


def main():
    scenario_id = sys.argv[1] if len(sys.argv) > 1 else "HR-001"
    if scenario_id not in {"HR-001", "HR-002"}:
        raise SystemExit("Velg HR-001 eller HR-002")
    root = Path(__file__).resolve().parents[3]
    path = root / "05_data/hr_simulator/scenarios" / f"{scenario_id}.json"
    conn = load_scenario(path)
    try:
        print(json.dumps({
            "scenario": scenario_id,
            "conflicts": detect_conflicts(conn),
            "rental_pool": pool_candidates(conn, "A-EVENING", "vertskap")
                if scenario_id == "HR-001" else [],
            "hr_cases_redacted": list_hr_cases(conn, "director"),
            "notice": "Fiktiv simulering – ingen ekte HR-data eller lovlighetsavgjørelser.",
        }, ensure_ascii=False, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
