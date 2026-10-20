"""Start Datafinner i demomodus på din egen PC, slik den vil kjøre hostet.

Bruker demokopien av databasen (uten fødselsår, e-post og telefon) og uten filverktøyene.
Bygger demokopien først hvis den mangler. museum.db røres ikke.

    py -3.13 scripts/start_demo.py            # http://127.0.0.1:8011
    py -3.13 scripts/start_demo.py --port 9000
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8011)
    args = ap.parse_args()

    from src.kunstpixel.data import build_demo_db

    if not build_demo_db.STANDARD_UT.is_file():
        info = build_demo_db.bygg_demo(build_demo_db.KILDE_DB, build_demo_db.STANDARD_UT)
        print(f"Bygde demokopien ({info['bytes'] / 1e6:.1f} MB, sha256 {info['sha256'][:12]})")

    # Miljøet må settes før datafinner importeres: demomodus leses ved import.
    os.environ["DATAFINNER_DEMO"] = "1"
    os.environ["DATAFINNER_PORT"] = str(args.port)
    os.environ["KUNSTPIXEL_DB_PATH"] = str(build_demo_db.STANDARD_UT)

    from src.kunstpixel.adapters import datafinner

    datafinner.main()


if __name__ == "__main__":
    main()
