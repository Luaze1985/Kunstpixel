"""Fasade- og snittegninger tegnet fra bygningsmodellen (06_kart/fasader.py).

Høyder kommer fra kotene i bygning_geometri.json, bredder fra fotavtrykket, og snittene viser
rommene som snittlinja faktisk krysser.
"""

from __future__ import annotations

import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
KART = ROOT / "06_kart"
MODELL = json.loads((KART / "bygning_geometri.json").read_text(encoding="utf-8"))
FILER = ["fasade_sor.svg", "fasade_ost.svg", "snitt_a.svg", "snitt_b.svg"]


def _modul():
    spec = importlib.util.spec_from_file_location("kp_fasader", KART / "fasader.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _svg(navn: str) -> str:
    return (KART / navn).read_text(encoding="utf-8")


def _kote(v: float) -> str:
    return f"+{v:.2f}".replace(".", ",")


@pytest.mark.parametrize("navn", FILER)
def test_tegningen_finnes_og_er_gyldig_svg(navn: str) -> None:
    rot = ET.fromstring(_svg(navn))
    assert rot.tag.endswith("svg")
    assert "MÅLESTOKK 1:100" in _svg(navn)


@pytest.mark.parametrize("navn", FILER)
def test_kotene_kommer_fra_modellen(navn: str) -> None:
    m = MODELL["museum"]["matrikkel"]
    svg = _svg(navn)
    for kote in (m["kote_terreng_moh"], m["kote_p1_fg_moh"], m["kote_p2_fg_moh"], m["kote_gesims_moh"]):
        assert _kote(kote) in svg, (navn, _kote(kote))
    if navn.startswith("snitt"):
        assert _kote(m["kote_u1_fg_moh"]) in svg


def test_fasadebreddene_kommer_fra_fotavtrykket() -> None:
    assert "58 000 mm" in _svg("fasade_sor.svg") and "34 000 mm" in _svg("fasade_sor.svg")
    assert "25 000 mm" in _svg("fasade_ost.svg")


def test_takformen_folger_flyene() -> None:
    hoved, glass = MODELL["museum"]["fotavtrykk"]["volumer"]
    assert hoved["tak_topp_moh"] > MODELL["museum"]["matrikkel"]["kote_gesims_moh"]  # mansardtak
    assert glass["tak_topp_moh"] == MODELL["museum"]["matrikkel"]["kote_gesims_moh"]  # flatt sedumtak
    assert 'class="mansardtak"' in _svg("fasade_sor.svg") and 'class="mansardtak"' in _svg("snitt_a.svg")
    assert 'class="mansardtak"' not in _svg("snitt_b.svg")


@pytest.mark.parametrize("navn", ["snitt_a.svg", "snitt_b.svg"])
def test_snittet_viser_rommene_linja_krysser(navn: str) -> None:
    fasader = _modul()
    x = fasader.snitt_x(MODELL, navn)
    svg = _svg(navn)
    for e in MODELL["etasjer"]:
        krysset = [r["id"] for r in e["rom"] if r["x"] < x < r["x"] + r["w"]]
        assert krysset, (navn, e["kode"])
        for rid in krysset:
            assert f'data-room-id="{rid}"' in svg, (navn, rid)


def test_build_map_lager_fasader_og_snitt() -> None:
    kilde = (KART / "build_map.py").read_text(encoding="utf-8")
    assert "fasader" in kilde and "skriv_alle" in kilde
