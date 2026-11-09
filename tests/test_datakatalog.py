"""Skjult datakatalog i Datafinner (DECISIONS 2026-11-09, punkt 11).

Katalogen viser alle tabeller i museum.db med antall rader og et lite utdrag.
Den er skrivebeskyttet, godtar bare tabellnavn som faktisk finnes, og er ikke et
verktøy for språkmodellen. På siden nås den bare fra en diskret lenke i rapporten.
"""

from __future__ import annotations

import json
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from src.kunstpixel.adapters.datafinner import VERKTOY, DatafinnerHandler

SIDE = Path(__file__).resolve().parents[1] / "src/kunstpixel/adapters/datafinner/ett-vindu.html"


@pytest.fixture()
def url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DatafinnerHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _get(adresse: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(adresse) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def test_katalog_lister_alle_tabeller_med_antall(url: str) -> None:
    status, data = _get(f"{url}/api/katalog")
    assert status == 200
    tabeller = {t["navn"]: t for t in data["tabeller"]}
    assert len(tabeller) >= 50
    assert tabeller["verk"]["rader"] > 0
    assert "tittel" in tabeller["verk"]["kolonner"]
    assert not any(n.startswith("sqlite_") for n in tabeller)
    assert data["totalt_rader"] == sum(t["rader"] for t in data["tabeller"])


def test_katalog_viser_utdrag_av_en_tabell(url: str) -> None:
    status, data = _get(f"{url}/api/katalog?tabell=verk")
    assert status == 200
    assert data["tabell"] == "verk"
    assert "tittel" in data["kolonner"]
    assert 0 < len(data["rader"]) <= 25
    assert data["totalt"] >= len(data["rader"])


@pytest.mark.parametrize(
    "navn",
    [
        "finnes_ikke",
        "sqlite_master",
        "verk; DROP TABLE verk",
        "verk] --",
        "verk WHERE 1=1",
        "../museum.db",
        "",
    ],
)
def test_katalog_avviser_ukjente_og_ondsinnede_navn(url: str, navn: str) -> None:
    status, data = _get(f"{url}/api/katalog?tabell={urllib.parse.quote(navn)}")
    assert status == 404
    assert "error" in data
    # Ingen SQL eller stier i feilmeldingen.
    assert "SELECT" not in data["error"].upper() and "museum.db" not in data["error"]


def test_katalog_er_ikke_et_verktoy_for_sprakmodellen() -> None:
    assert not any("katalog" in navn or "tabell" in navn for navn in VERKTOY)


def test_katalog_er_skjult_fra_menyen_men_lenket_fra_rapporten() -> None:
    html = SIDE.read_text(encoding="utf-8")
    flater = re.search(r"var FLATER = \[(.*?)\];", html, re.DOTALL)
    assert flater and "katalog" not in flater.group(1).lower()
    rapport = re.search(r"function tegnRapport\(.*?\n  \}\n", html, re.DOTALL)
    assert rapport and "#katalog" in rapport.group(0)
