"""Genererer gyldne svar for intern assistent (regelbasert baselinje).

    py -3.13 tests/make_golden_intern.py

Overskriver tests/golden/intern/golden.json. Gjennomgå diff før commit.
"""

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
logging.disable(logging.CRITICAL)

from src.kunstpixel.core.intern.agent import InternAgent  # noqa: E402
from tests.intern_questions import DEKKET, UBESVARBARE  # noqa: E402


def main() -> None:
    agent = InternAgent()
    golden = []
    for item in DEKKET + UBESVARBARE:
        r = agent.handle_message(item["sporsmal"], item["rolle"])
        golden.append(
            {
                "sporsmal": item["sporsmal"],
                "rolle": item["rolle"],
                "text": r.text,
                "category": r.category,
                "tools_used": r.tools_used,
                "kilder": r.kilder,
                "funnet": r.funnet,
            }
        )
    out = ROOT / "tests" / "golden" / "intern" / "golden.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(golden, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Skrev {len(golden)} gyldne svar til {out}")


if __name__ == "__main__":
    main()
