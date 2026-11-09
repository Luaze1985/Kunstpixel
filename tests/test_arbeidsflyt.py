"""Rolleoppgaver kommer fra data og kan utføres gjennom Datafinner."""

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.parse import quote
from urllib.request import urlopen

import pytest

from src.kunstpixel.adapters.datafinner import VERKTOY, DatafinnerHandler


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
        # Arbeidsflyter ligger i skallet (oppgave 08). Den gamle adressen sendes dit med 302.
        con = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=10)
        con.request("GET", "/arbeidsflyt")
        svar = con.getresponse()
        assert svar.status == 302 and svar.getheader("Location") == "/#flate:arbeidsflyt"
        con.close()
        with urlopen(base + "/") as response:
            side = response.read().decode("utf-8")
        assert "Velg arbeidsrolle" in side
        assert "localStorage" in side
        args = quote(json.dumps({"query": "brann", "limit": 2}))
        with urlopen(base + f"/api/verktoy?navn=lookup_handbook&args={args}") as response:
            treff = json.load(response)["resultat"]
        assert treff and "punkt_id" in treff[0]
    finally:
        server.shutdown()
        server.server_close()
