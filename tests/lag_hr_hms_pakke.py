"""Lager den syntetiske HR- og HMS-pakken (2010 til 2026) som zip.

    py -3.13 tests/lag_hr_hms_pakke.py                 # skriver 01_inbox/hr_hms_pakke.zip
    py -3.13 tests/lag_hr_hms_pakke.py --til ut.zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.kunstpixel.core.intern.hr_hms_pakke import pakke, zip_bytes  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--til", default=str(ROOT / "01_inbox" / "hr_hms_pakke.zip"))
    args = ap.parse_args(argv)
    ut = Path(args.til)
    ut.parent.mkdir(parents=True, exist_ok=True)
    ut.write_bytes(zip_bytes())
    print(f"Skrev {ut} ({ut.stat().st_size} byte, {len(pakke())} filer)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
