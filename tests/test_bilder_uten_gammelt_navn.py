"""Vakttest: bildene i 06_kart/bilder skal ikke vise det gamle museumsnavnet (DECISIONS punkt 10).

Den eksisterende navnevakten leser bare tekst. Navnet sto også på skilt, disker og fasader i åtte bilder.
Denne testen feiler hvis en av de gamle bildefilene (kjent SHA-256) kommer tilbake.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

BILDER = Path(__file__).resolve().parents[1] / "06_kart" / "bilder"

# SHA-256 for de åtte originalene med navnet synlig i bildet (fra commit 1c4d9a4).
GAMLE_BILDER = {
    "ad03bd55d53d1ea60b953bd2edb9e5b0f8a2dca0b34f2972155d93ad300ad4f0": "01_eksterior_fasade.jpg",
    "123fbfd557ff1957b356fa27ccba636863f2558411f5f6ca1d136ae7e70f0c3b": "02_eksterior_tilbygg_nidelva.jpg",
    "79f0ed8d757c5ad27b9178158dee76fc1c16ba29400233858addb80f0e1f3d2b": "02_vestibyle_ankomst.jpg",
    "2ed84ceae4450eb18ff17025f795f8d8664d59c3901990841cf4a4300387be91": "03_sal_a_mytologi.jpg",
    "5c62df7be2d4fa34f2626f78f20a1d28a2ef90938df55e050cacae8b9ab65162": "04_sal_d_munch.jpg / 11_sal_d_munch.jpg",
    "56bfda538d33897de31c5c5e48bdab162096116245741427eb0b158d2afeebbb": "04_vestibyle_resepsjon.jpg",
    "baf083d2d9a238e9c81f3976c7e1b5c973d56d79b6b6b401c057b262320e8274": "05_museumsbutikk.jpg",
    "3e57c0d6038720fb685f9737eab39bd828a77c80b97300fa2b2ca50f8fa1c3dd": "06_museumskafe.jpg",
}


@pytest.mark.parametrize("bilde", sorted(p.name for p in BILDER.glob("*.jpg")))
def test_bildet_er_ikke_en_gammel_versjon_med_navnet(bilde: str) -> None:
    sha = hashlib.sha256((BILDER / bilde).read_bytes()).hexdigest()
    assert sha not in GAMLE_BILDER, f"{bilde} er originalen med gammelt navn i bildet ({GAMLE_BILDER[sha]})"
