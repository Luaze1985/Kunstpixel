"""Rolleoppgaver kommer fra data og kan utføres gjennom Datafinner."""

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.parse import quote
from urllib.request import urlopen

from src.kunstpixel.adapters.datafinner import DatafinnerHandler, VERKTOY
import pytest


@pytest.mark.parametrize("rolle, forventede", [
    ("Kafé", {"Kafeansvarlig"}),
    ("Samling/kurator", {"Samlingsforvalter", "Konservator", "Kurator"}),
])
def test_opplaering_finner_databasens_roller(rolle, forventede):
    resultat = VERKTOY["search_hr_onboarding"][0](rolle=rolle)
    assert {rad["rolle"] for rad in resultat["opplaering"]} == forventede


def test_rolleflyt_og_verktoykatalog():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DatafinnerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with urlopen(base + "/api/arbeidsflyt") as response:
            oppgaver = json.load(response)["oppgaver"]
        assert {r["rolle"] for r in oppgaver} == {
            "Salvert", "Montør/drift", "Kafé", "Formidling", "Samling/kurator", "Leder", "Verneombud"
        }
        assert all(r["verktoy"] in VERKTOY for r in oppgaver)
        assert all("ansatt_id" not in r for r in oppgaver)
        with urlopen(base + "/api/verktoykatalog") as response:
            katalog = json.load(response)["verktoy"]
        assert {r["navn"] for r in katalog} == set(VERKTOY)
        with urlopen(base + "/arbeidsflyt") as response:
            side = response.read().decode("utf-8")
        assert "Velg en arbeidsrolle" in side
        assert "localStorage" in side
        args = quote(json.dumps({"query": "brann", "limit": 2}))
        with urlopen(base + f"/api/verktoy?navn=lookup_handbook&args={args}") as response:
            treff = json.load(response)["resultat"]
        assert treff and "punkt_id" in treff[0]
    finally:
        server.shutdown()
        server.server_close()
