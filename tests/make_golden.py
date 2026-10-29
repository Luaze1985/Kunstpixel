"""Genererer gyldne svar fra regelbasert agent. Kjøres bevisst for hånd:

    py -3.13 tests/make_golden.py

Overskriver tests/golden/regelbasert/golden.json. Gjennomgå diff før commit.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["AURA_TODAY"] = "2026-09-14"

from tests.canonical_questions import CANONICAL_QUESTIONS  # noqa: E402
from src.kunstpixel.core.agent import MuseumsvertAgent  # noqa: E402


def main() -> None:
    agent = MuseumsvertAgent()
    golden = []
    for q in CANONICAL_QUESTIONS:
        r = agent.handle_message(q)
        golden.append(
            {
                "question": q,
                "text": r.text,
                "category": r.category,
                "tools_used": r.tools_used,
                "artworks_referenced": r.artworks_referenced,
                "rooms_referenced": r.rooms_referenced,
            }
        )
    out = ROOT / "tests" / "golden" / "regelbasert" / "golden.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(golden, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Skrev {len(golden)} gyldne svar til {out}")


if __name__ == "__main__":
    main()

