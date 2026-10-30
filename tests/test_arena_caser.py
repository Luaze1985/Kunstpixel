"""Arenaen: hver øvelsescase skal virke før den kan vises.

Fasiten er feltet «forventet» i 04_knowledge/07_arena/caser.yaml. Testene kjører hver case
deterministisk (KI av) og krever at alt som er forventet, står i svaret, og at avvisningene avvises.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from src.kunstpixel.core import arena

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASER = arena.last_caser()
KJORBARE = [c["id"] for c in CASER["caser"] if c["kjoring"]["type"] != "lesecase"]


def test_casefilen_har_gyldige_felt() -> None:
    omrader = {o["id"] for o in CASER["omrader"]}
    ids = [c["id"] for c in CASER["caser"]]
    assert len(ids) == len(set(ids)), "case-ID-er må være unike"
    for c in CASER["caser"]:
        for felt in ("id", "omrade", "tittel", "oppdrag", "kjoring", "gdpr", "gevinst", "se_etter"):
            assert c.get(felt), f"{c.get('id')}: mangler {felt}"
        assert c["omrade"] in omrader, f"{c['id']}: ukjent område {c['omrade']}"
        assert c["kjoring"]["type"] in arena.TYPER
        if c.get("lenke"):
            assert (PROJECT_ROOT / c["lenke"]).is_file(), f"{c['id']}: lenken finnes ikke"


@pytest.mark.parametrize("case_id", KJORBARE)
def test_casen_gir_forventet_svar(case_id: str) -> None:
    res = arena.kjor(case_id)
    for steg in res["steg"]:
        assert steg["ok"], f"{case_id}: {steg.get('mangler')} mangler i svaret, eller feil kategori"
    assert res["ok"]


def test_ukjent_case_avvises() -> None:
    with pytest.raises(ValueError):
        arena.kjor("X99")


def test_lesecase_kjores_ikke() -> None:
    res = arena.kjor("G5")
    assert res["steg"] == [] and res["ok"]


def test_datamerket_er_fail_closed() -> None:
    merker = {m["tabell"]: m for m in arena.datamerke(["hr_ansatte", "hr_fravaer", "ssb_sykefraver_kultur"])}
    assert merker["hr_fravaer"]["merke"] == "syntetisk"
    assert merker["hr_ansatte"]["merke"] == "umerket"
    assert merker["ssb_sykefraver_kultur"]["merke"] == "offentlig"


def test_g4_stopper_hele_pakken() -> None:
    res = arena.kjor("G4")
    assert res["policy"]["ekstern_ki"] is False


def test_t3_kan_sendes_til_ekstern_ki() -> None:
    assert arena.kjor("T3")["policy"]["ekstern_ki"] is True


def test_intern_case_viser_tilgangsnekt() -> None:
    steg = arena.kjor("T1")["steg"]
    assert [s["kategori"] for s in steg] == ["arbeidsoppgaver", "tilgang"]


# ----------------------------------------------------------------------------- rutene i Datafinner


@pytest.fixture()
def server():
    from src.kunstpixel.adapters.datafinner import DatafinnerHandler

    srv = ThreadingHTTPServer(("127.0.0.1", 0), DatafinnerHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def _post(url: str, body: bytes, headers: dict[str, str]) -> tuple[int, dict]:
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_api_lister_caser(server: str) -> None:
    with urllib.request.urlopen(f"{server}/api/arena/caser") as res:
        data = json.loads(res.read())
    assert {c["id"] for c in data["caser"]} >= {"T1", "G4"}


def test_api_kjorer_case(server: str) -> None:
    status, data = _post(f"{server}/api/arena/kjor", b'{"id": "P2"}', {"Content-Type": "application/json"})
    assert status == 200 and data["ok"]


def test_api_avviser_annen_side(server: str) -> None:
    status, _ = _post(
        f"{server}/api/arena/kjor",
        b'{"id": "P2"}',
        {"Content-Type": "application/json", "Origin": "https://ondsinnet.example"},
    )
    assert status == 403


def test_api_avviser_ukjent_case(server: str) -> None:
    status, _ = _post(f"{server}/api/arena/kjor", b'{"id": "X99"}', {"Content-Type": "application/json"})
    assert status == 400


def test_arenasiden_serveres(server: str) -> None:
    with urllib.request.urlopen(f"{server}/arena") as res:
        assert res.status == 200 and b"class=\"af\"" in res.read()


def test_k1_tallene_stemmer_med_databasen() -> None:
    """K1 påstår at to kilder er uenige. Da må tallene i casen være de som står i databasen i dag."""
    from src.kunstpixel.core import db

    with db.get_db_connection() as con:
        arkiv_besok = con.execute("SELECT SUM(besok_totalt) FROM dagsbesok WHERE aar = 2025").fetchone()[0]
        arkiv_inntekt = con.execute("SELECT SUM(inntekt_nok) FROM dagsbesok WHERE aar = 2025").fetchone()[0]
        utst_besok = con.execute("SELECT SUM(besokstall_total) FROM utstillinger_historikk WHERE aar = 2025").fetchone()[0]
        h5_besok, h5_tkr = con.execute("SELECT besok_totalt, billettinntekter_tkr FROM h5_historikk_2010_2026 WHERE ar = 2025").fetchone()
    assert arkiv_besok == utst_besok, "arkivet skal henge sammen internt"

    def tall(n: int) -> str:
        return f"{n:,}".replace(",", " ")

    tekst = next(c for c in CASER["caser"] if c["id"] == "K1")["se_etter"]
    for n in (arkiv_besok, arkiv_inntekt, h5_besok, h5_tkr * 1000):
        assert tall(n) in tekst, f"{tall(n)} står ikke i K1. Tallene har endret seg, og casen må oppdateres"
