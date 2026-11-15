"""Chat er en egen inngang og bruker bare hvitelistede verktøy.

Lederens faktiske menyrekkefølge og åpneflyt testes i test_ledervalidering.py.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.kunstpixel.adapters import datafinner_api
from src.kunstpixel.adapters.datafinner import VERKTOY

SIDE = Path(__file__).resolve().parents[1] / "src/kunstpixel/adapters/datafinner/ett-vindu.html"


def test_chat_er_ikke_lenger_under_flater() -> None:
    html = SIDE.read_text(encoding="utf-8")
    flater = re.search(r"var FLATER = \[(.*?)\];", html, re.DOTALL)
    assert flater and '"chat"' not in flater.group(1)


def test_chat_far_alle_hvitelistede_verktoy() -> None:
    navn = {v["navn"] for v in datafinner_api.verktoyskjema(VERKTOY)}
    assert navn == set(VERKTOY)
    assert len(navn) >= 45
