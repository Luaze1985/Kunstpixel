"""Koblingssjekk: finner datalagene hverandre (A), og forteller de samme historie (B)?

    py -3.13 scripts/koblingssjekk.py
    py -3.13 scripts/koblingssjekk.py --vis-kjente      # med forklaring på hvert kjent avvik

Bruker 05_data/museum.db og 05_data/persondata/persondata.db. Mangler persondata.db, bygges en midlertidig
kopi fra CSV-ene (ingenting i repoet endres). Exit 1 hvis en kontroll er verre enn forventet.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.kunstpixel.data import koblinger as K  # noqa: E402
from src.kunstpixel.persondata import config as pd  # noqa: E402
from src.kunstpixel.persondata.generer import bygg_fra_csv  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--museum-db", type=Path, default=pd.MUSEUM_DB_STI)
    ap.add_argument("--persondata-db", type=Path, default=pd.STANDARD_DB_STI)
    ap.add_argument("--vis-kjente", action="store_true")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as tmp:
        pd_db = a.persondata_db
        if not pd_db.is_file():
            pd_db = Path(tmp) / "persondata.db"
            bygg_fra_csv(pd_db)
            print(f"(persondata.db manglet, bygget midlertidig fra {pd.CSV_DIR})")
        res = K.kjor(a.museum_db, pd_db)
    teller: dict[str, int] = {}
    for niva, navn in (("A", "A. Kobling: finner nøklene hverandre?"), ("B", "B. Samsvar: forteller tabellene samme historie?")):
        print(f"\n{navn}")
        for r in (r for r in res if r.kontroll.niva == niva):
            teller[r.status] = teller.get(r.status, 0) + 1
            antall = "-" if r.antall is None else str(r.antall)
            print(f"  [{r.status:<11}] {r.kontroll.id}  {r.kontroll.beskrivelse}  ({antall})")
            if r.status in ("FEIL", "BEDRE") or (a.vis_kjente and r.status == "KJENT AVVIK"):
                print(f"               forventet {r.kontroll.forventet}. {r.kontroll.forklaring}")
                if r.eksempel:
                    print(f"               eksempel: {r.eksempel}")
    print("\nResultat: " + ", ".join(f"{n} {s}" for s, n in sorted(teller.items())))
    return 1 if teller.get("FEIL") or teller.get("BEDRE") else 0


if __name__ == "__main__":
    raise SystemExit(main())
