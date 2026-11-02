"""Meld feil uten chatbot (Kunstpixel).

    py -3.13 scripts/meld_feil.py                    # åpner nettsiden http://127.0.0.1:8770
    py -3.13 scripts/meld_feil.py --liste            # viser alle meldte feil
    py -3.13 scripts/meld_feil.py --liste --status ny
    py -3.13 scripts/meld_feil.py --sett-status FM-0001 rettet --kommentar "Rettet i kildefila"

Meldingene lagres i 05_data/feilmeldinger/feilmeldinger.csv (kan åpnes i Excel).
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.kunstpixel.feilmelding import register, web  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Meld feil i Kunstpixel-dataene, uten chatbot.")
    p.add_argument("--liste", action="store_true", help="vis meldte feil")
    p.add_argument("--status", choices=register.STATUSER, help="bare meldinger med denne statusen (sammen med --liste)")
    p.add_argument("--sett-status", nargs=2, metavar=("MELDING_ID", "STATUS"), help="endre status på en melding")
    p.add_argument("--kommentar", default="", help="kommentar ved --sett-status")
    p.add_argument("--port", type=int, default=web.STANDARD_PORT)
    p.add_argument("--ikke-aapne", action="store_true", help="ikke åpne nettleseren automatisk")
    a = p.parse_args(argv)

    if a.sett_status:
        try:
            register.oppdater_status(a.sett_status[0], a.sett_status[1], a.kommentar)
        except ValueError as e:
            print(f"Avbrutt: {e}")
            return 1
        print(f"{a.sett_status[0]} er satt til '{a.sett_status[1]}'.")
        return 0
    if a.liste:
        rader = register.liste(a.status)
        if not rader:
            print("Ingen meldte feil.")
        for r in rader:
            print(f"{r['melding_id']}  [{r['status']}]  {r['meldt'].replace('T', ' ')}  {r['melder_navn']}")
            print(f"    {r['objekttype']} {r['objekt_id']} ({r['objekt_visning']}), felt '{r['felt']}' = {r['verdi_da']!r}")
            print(f"    Feil: {r['beskrivelse']}" + (f"  | Forslag: {r['forslag']}" if r["forslag"] else ""))
            print(f"    Kilde: {r['kilde']}" + (f"  | Kommentar: {r['kommentar']}" if r["kommentar"] else ""))
        return 0

    server = web.lag_server(port=a.port)
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"Feilmelding er åpen på {url}  (Ctrl+C for å avslutte)")
    if not a.ikke_aapne:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAvsluttet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
