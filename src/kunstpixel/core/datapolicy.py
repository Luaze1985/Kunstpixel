"""Datapolicy: ekte data kan bare behandles av lokal modell.

Fail-closed: alt som ikke er nøyaktig `syntetisk` (eller `syntetisk (<kilde>)` fra museum.db) regnes som `ekte`, og alt som ikke er
nøyaktig `local` regnes som `external`. Feilstavinger, store bokstaver, manglende felt og
ukjente verdier gir altså strengeste tolkning.
"""

from __future__ import annotations

import re
from typing import Any

SYNTETISK = "syntetisk"
EKTE = "ekte"

LOCAL = "local"
EXTERNAL = "external"

POLICY_REASON = "policy: ekte data kun lokal modell"

_SYNTETISK_RE = re.compile(r"^syntetisk(?: \([a-z0-9_]+\))?$")


def normalize_classification(value: Any) -> str:
    """Eksakt `syntetisk` eller `syntetisk (<kilde>)` er syntetisk. Alt annet er ekte."""
    if isinstance(value, str) and _SYNTETISK_RE.match(value):
        return SYNTETISK
    return EKTE


def normalize_locality(value: Any) -> str:
    """Eksakt `local` er lokal. Alt annet er ekstern."""
    return LOCAL if value == LOCAL else EXTERNAL


def overall_classification(entries: list[dict[str, Any]]) -> str | None:
    """Høyeste klassifisering blant verktøyresultatene. None hvis det ikke finnes noen."""
    if not entries:
        return None
    if any(normalize_classification(e.get("klassifisering")) == EKTE for e in entries):
        return EKTE
    return SYNTETISK


def check_policy(locality: Any, entries: list[dict[str, Any]]) -> str | None:
    """Returnerer årsak hvis modellen ikke får se dataene, ellers None."""
    if normalize_locality(locality) == LOCAL:
        return None
    if overall_classification(entries) == EKTE:
        return POLICY_REASON
    return None
