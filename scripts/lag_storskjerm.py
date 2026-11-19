"""Bygg storskjerm-dashbordet (spec docs/specs/2026-11-19-storskjerm-dashbord.md).

Skriver to filer: storskjerm.html (malen i deploy/claude-app/ med af.css lagt inn, fordi artifacts ikke
kan hente stilark fra andre steder) og data.json (tallene fra core/storskjerm.py). Claude Code publiserer
dem som én artifact til samme lenke hver gang.

Bruk:
    py -3.13 scripts/lag_storskjerm.py                 # skriver til .scratch/claude-app/
    py -3.13 scripts/lag_storskjerm.py --ut C:\\temp
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.kunstpixel.core.storskjerm import lag_storskjerm

MAL = ROOT / "deploy" / "claude-app" / "storskjerm.html"
AF_CSS = ROOT / "src" / "kunstpixel" / "adapters" / "datafinner" / "af.css"
PLASSHOLDER = "/*AF_CSS*/"


def bygg(ut: Path, dato: str | None = None) -> tuple[Path, Path]:
    dato = dato or date.today().isoformat()
    mal = MAL.read_text(encoding="utf-8")
    if mal.count(PLASSHOLDER) != 1:
        raise SystemExit(f"STOPP: malen må ha {PLASSHOLDER} nøyaktig én gang.")
    ut.mkdir(parents=True, exist_ok=True)
    side = ut / "storskjerm.html"
    data = ut / "data.json"
    side.write_text(mal.replace(PLASSHOLDER, AF_CSS.read_text(encoding="utf-8")), encoding="utf-8")
    data.write_text(json.dumps(lag_storskjerm(dato), ensure_ascii=False, indent=1), encoding="utf-8")
    return side, data


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Bygg storskjerm-dashbordet")
    p.add_argument("--ut", type=Path, default=ROOT / ".scratch" / "claude-app", help="mappe for filene")
    a = p.parse_args(argv)
    side, data = bygg(a.ut)
    print(f"OK: {side}\n    {data}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
