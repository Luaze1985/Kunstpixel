"""Chat som egen inngang øverst i menyen (DECISIONS 2026-11-09, punkt 12).

Chatten står som «Spør KI» over rapportene, ikke gjemt under «Flater».
Den bruker alle hvitelistede verktøy og er slått av uten nøkkel.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.kunstpixel.adapters import datafinner_api
from src.kunstpixel.adapters.datafinner import VERKTOY

SIDE = Path(__file__).resolve().parents[1] / "src/kunstpixel/adapters/datafinner/ett-vindu.html"


def _meny() -> str:
    html = SIDE.read_text(encoding="utf-8")
    m = re.search(r"function tegnMeny\(\) \{.*?\n  \}\n", html, re.DOTALL)
    assert m
    return m.group(0)


def test_chat_er_ikke_lenger_under_flater() -> None:
    html = SIDE.read_text(encoding="utf-8")
    flater = re.search(r"var FLATER = \[(.*?)\];", html, re.DOTALL)
    assert flater and '"chat"' not in flater.group(1)


def test_spor_ki_star_over_rapportene_i_menyen() -> None:
    meny = _meny()
    spor = meny.find("Spør KI")
    rapporter = meny.find('gruppe("Rapporter for')
    assert spor != -1 and rapporter != -1 and spor < rapporter
    assert "flate:chat" in meny


def test_chat_far_alle_hvitelistede_verktoy() -> None:
    navn = {v["navn"] for v in datafinner_api.verktoyskjema(VERKTOY)}
    assert navn == set(VERKTOY)
    assert len(navn) >= 45
