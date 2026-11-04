"""Breddeprøver mot syntetiske ansatte og kuraterte, etterprøvbare caser."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import pytest

from src.kunstpixel.core import db, vaktrom

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "05_data" / "ansatt_testcaser.csv").open(encoding="utf-8", newline="") as fil:
    CASER = list(csv.DictReader(fil))
with db.get_db_connection() as con:
    ANSATTE = [(r["ansatt_id"], r["navn"]) for r in con.execute(
        "SELECT ansatt_id, navn FROM hr_ansatte ORDER BY ansatt_id"
    )]
    VAKTER = [tuple(r) for r in con.execute(
        "SELECT v.ansatt_id, v.stasjon, v.dato, v.start, v.slutt FROM hr_vakter v "
        "JOIN (SELECT ansatt_id, MIN(vakt_id) vakt_id FROM hr_vakter "
        "WHERE dato BETWEEN '2026-01-01' AND '2026-12-31' AND start IS NOT NULL "
        "AND slutt IS NOT NULL GROUP BY ansatt_id) x ON x.vakt_id = v.vakt_id "
        "ORDER BY v.ansatt_id LIMIT 40"
    )]


def test_caseutvalget_er_bredt_og_etterproevbart() -> None:
    assert len(CASER) >= 30
    assert len({c["case_id"] for c in CASER}) == len(CASER)
    assert len({c["ansatt_id"] for c in CASER}) == len(CASER)
    assert {c["arbeidsrolle"] for c in CASER} == {
        "Salvert", "Montør/drift", "Kafé", "Formidling", "Samling/kurator", "Leder", "Verneombud"
    }
    kategorier = Counter(c["kategori"] for c in CASER)
    for kategori in ("navnelikhet", "sluttet", "personalmappe", "vaktbytte", "medarbeidersamtale"):
        assert kategorier[kategori] >= 2
    assert all(c["begrunnelse"] and c["datakilde"].startswith("syntetisk") for c in CASER)


@pytest.mark.parametrize("ansatt_id,navn", ANSATTE, ids=lambda x: x if isinstance(x, str) and x.startswith("KP-") else None)
def test_alle_ansatt_ider_kan_finnes_entydig(ansatt_id: str, navn: str) -> None:
    assert len(ANSATTE) >= 150
    treff = vaktrom.find_employee(ansatt_id)
    assert len(treff) == 1, ansatt_id
    assert treff[0]["ansatt_id"] == ansatt_id
    assert treff[0]["navn"] == navn


def test_ukjent_ansatt_id_gir_tomt_svar() -> None:
    assert vaktrom.find_employee("KP-ANS-999") == []


@pytest.mark.parametrize("case", CASER, ids=lambda c: c["case_id"])
def test_kuraterte_ansattcaser_stemmer_med_oppslaget(case: dict[str, str]) -> None:
    treff = vaktrom.find_employee(case["ansatt_id"])
    assert len(treff) == 1
    assert treff[0]["navn"] == case["forventet_navn"]
    if case["kategori"] == "sluttet":
        assert treff[0]["aktiv"] is False
    if case["kategori"] == "personalmappe":
        assert vaktrom.get_personnel_file(case["ansatt_id"])["antall_saker"] > 0
    if case["kategori"] == "medarbeidersamtale":
        assert vaktrom.get_employee_reviews(case["ansatt_id"])["antall"] > 0


@pytest.mark.parametrize("navn", ["Anja Eriksen", "Gunnar Viken", "Marit Sæther", "Mikkel Lindqvist", "Synnøve Myhre", "Thea Larsen"])
def test_like_navn_gir_flere_personer_som_maa_avklares(navn: str) -> None:
    treff = vaktrom.find_employee(navn)
    assert len(treff) == 2
    assert len({r["ansatt_id"] for r in treff}) == 2


def test_kjente_vaktcaser_bruker_faktiske_personer_og_avslag() -> None:
    stasjon = "Vaktrom / Sikkerhetssentral"
    vakt = {"stasjon": stasjon, "dato": "2026-11-07", "start": "08:00", "slutt": "16:00"}
    kandidater = vaktrom.get_staffing_candidates(**vakt)
    assert "KP-ANS-168" in {r["id"] for r in kandidater["egne"]}
    assert "KP-INN-P08" not in {r["id"] for r in kandidater["innleide"]}
    avslag = vaktrom.check_staffing_selection(stasjon, "2026-11-21", "15:00", "23:00", ["KP-ANS-096"])
    assert avslag["resultater"][0]["status"] == "avvik"
    assert len(avslag["resultater"][0]["funn"]) >= 2


@pytest.mark.parametrize("ansatt_id,stasjon,dato,start,slutt", VAKTER, ids=lambda x: x if isinstance(x, str) and x.startswith("KP-") else None)
def test_allerede_registrert_vakt_gir_overlapp_for_mange_ansatte(
    ansatt_id: str, stasjon: str, dato: str, start: str, slutt: str
) -> None:
    """En person må ikke kunne ta en ny vakt som overlapper egen registrerte vakt."""
    assert len(VAKTER) >= 30
    svar = vaktrom.check_staffing_selection(stasjon, dato, start, slutt, [ansatt_id])
    resultat = svar["resultater"][0]
    assert resultat["status"] == "avvik"
    assert any("overlapp" in funn.lower() for funn in resultat["funn"])
