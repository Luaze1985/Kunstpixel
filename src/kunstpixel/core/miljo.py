"""Les innstillinger fra en .env-fil i prosjektroten (KI-nøkkel og modell).

Filen ignoreres av git (.gitignore). Den leses bare når et program starter (Datafinner, scripts/chat_eval.py),
aldri ved import, så testene ikke plukker opp en ekte nøkkel. Variabler som alt er satt i miljøet, vinner.
Verdier skrives aldri ut.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FIL = PROJECT_ROOT / ".env"


def last_env_fil(sti: Path = ENV_FIL, miljo: dict[str, str] | None = None) -> list[str]:
    """Sett NAVN=verdi fra filen inn i miljøet. Returnerer navnene som ble satt (ikke verdiene).

    Tomme linjer og linjer som starter med # hoppes over. Anførselstegn rundt verdien fjernes.
    En tom verdi settes ikke, så en halvutfylt fil ikke slår på KI uten nøkkel.
    """
    miljo = os.environ if miljo is None else miljo
    if not sti.is_file():
        return []
    satt: list[str] = []
    for linje in sti.read_text(encoding="utf-8-sig").splitlines():
        linje = linje.strip()
        if not linje or linje.startswith("#") or "=" not in linje:
            continue
        navn, verdi = linje.split("=", 1)
        navn = navn.strip().removeprefix("export ").strip()
        verdi = verdi.strip()
        if len(verdi) >= 2 and verdi[0] == verdi[-1] and verdi[0] in "\"'":
            verdi = verdi[1:-1]
        if not navn or not verdi or navn in miljo:
            continue
        miljo[navn] = verdi
        satt.append(navn)
    return satt
