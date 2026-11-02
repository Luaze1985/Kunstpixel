"""Task 2: les eksisterende ansatte, dagsbesøk og hendelser skrivebeskyttet fra museum.db."""

import hashlib
from datetime import date

import pytest

from src.kunstpixel.persondata import ansattkilde as ak
from src.kunstpixel.persondata.config import MUSEUM_DB_STI


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def ansatte():
    return ak.hent_ansatte(MUSEUM_DB_STI)


def test_henter_168_ansatte(ansatte):
    assert len(ansatte) == 168
    assert all(a.ansatt_id.startswith("KP-ANS-") for a in ansatte)


def test_aktive_per_referansedato(ansatte):
    assert len(ak.aktive_paa(ansatte, date(2026, 11, 2))) == 72


def test_del_navn_dobbelt_etternavn(ansatte):
    assert ak.del_navn("Henrik Faye-Lund") == ("Henrik", "Faye-Lund")
    for a in ansatte:
        assert " ".join(ak.del_navn(a.navn)) == a.navn


def test_avdelingsfilter(ansatte):
    aktive = ak.aktive_paa(ansatte, date(2024, 6, 1), avdelinger={"Formidling"})
    assert aktive and all(a.avdeling == "Formidling" for a in aktive)


def test_dagsbesok_periode():
    d = ak.hent_dagsbesok(MUSEUM_DB_STI, date(2021, 11, 2), date(2026, 11, 2))
    assert len(d) == (date(2026, 11, 2) - date(2021, 11, 2)).days + 1
    besok, aapent = d[date(2024, 6, 1)]
    assert isinstance(besok, int) and isinstance(aapent, bool)


def test_hent_hendelser():
    h = ak.hent_hendelser(MUSEUM_DB_STI)
    assert len(h) == 45
    assert {"id", "type", "tittel", "dato", "maks_deltakere", "pris_voksen", "pris_barn"} <= set(h[0])


def test_museum_db_uendret():
    for_ = _sha(MUSEUM_DB_STI)
    ak.hent_ansatte(MUSEUM_DB_STI)
    ak.hent_dagsbesok(MUSEUM_DB_STI, date(2021, 11, 2), date(2026, 11, 2))
    ak.hent_hendelser(MUSEUM_DB_STI)
    assert _sha(MUSEUM_DB_STI) == for_
