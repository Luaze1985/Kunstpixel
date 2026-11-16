"""ledelse.js (F2/F4): rene visningsfunksjoner uten DOM, testet i Node. Hoppes over hvis Node mangler."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDELSE_JS = ROOT / "src" / "kunstpixel" / "adapters" / "datafinner" / "ledelse.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")


def js(uttrykk: str):
    """Kjør ett uttrykk mot ledelse.js og returner svaret som JSON."""
    kode = f"const L=require({json.dumps(str(LEDELSE_JS))});process.stdout.write(JSON.stringify({uttrykk}));"
    ut = subprocess.run([NODE, "-e", kode], capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(ut.stdout)


@pytest.mark.parametrize("status,tekst,klasse", [
    ("Normal", "Normal", "go"),
    ("Følg med", "Følg med", "check"),
    ("Over terskel", "Over terskel", "stop"),
    ("Ukjent", "Mangler data", ""),
    ("Stengt", "Stengt", ""),
    (None, "Mangler data", ""),
    ("noe rart", "Mangler data", ""),
])
def test_status_gir_ord_og_form(status, tekst: str, klasse: str) -> None:
    assert js(f"L.statusVisning({json.dumps(status)})") == {"tekst": tekst, "klasse": klasse}


def test_ukjent_er_aldri_gronn() -> None:
    assert js('L.statusVisning("Ukjent").klasse') != "go"


@pytest.mark.parametrize("normalt,pst,forventet", [
    (412.3, -5.1, "Normalt 412 · −5,1 %"),
    (410, 6, "Normalt 410 · +6 %"),
    (410, 0, "Normalt 410 · 0 %"),
    (None, None, "Ingen sammenligning"),
])
def test_normalt_tekst(normalt, pst, forventet: str) -> None:
    assert js(f"L.normaltTekst({json.dumps(normalt)}, {json.dumps(pst)})") == forventet


def test_tall_per() -> None:
    assert js('L.tallPer("09:14")') == "Tall per kl. 09:14"
    assert js("L.tallPer(null)") == ""


def test_dato_kort() -> None:
    assert js('L.datoKort("2026-11-15")') == "søndag 15.11."
    assert js('L.datoKort("2026-11-16")') == "mandag 16.11."


@pytest.mark.parametrize("felt,etikett", [
    ("maaned", "Måned"), ("maned", "Måned"), ("formal", "Formål"), ("aar", "År"), ("ar", "År"),
    ("besok_totalt", "Besøk totalt"), ("ukedag_navn", "Ukedag"), ("kategori", "Kategori"),
    ("hastegrad", "Hastegrad"), ("mottaker_rolle", "Mottaker"), ("er_aapent", "Åpent"),
])
def test_etiketter_med_aeoeaa(felt: str, etikett: str) -> None:
    assert js(f"L.etikett({json.dumps(felt)})") == etikett
