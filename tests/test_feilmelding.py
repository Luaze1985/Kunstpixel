"""Feilmelding uten chatbot: en ansatt velger et objekt, ser originalen og melder fra til systemansvarlig."""

import csv
import json
import threading
import urllib.request
from datetime import date

import pytest

from src.kunstpixel.feilmelding import objekter, register
from src.kunstpixel.persondata.generer import bygg_database


@pytest.fixture(scope="module")
def persondata(tmp_path_factory):
    d = tmp_path_factory.mktemp("pd")
    bygg_database(d / "p.db", skala="test", csv_dir=None)
    return d / "p.db"


@pytest.fixture()
def miljo(monkeypatch, persondata, tmp_path):
    monkeypatch.setenv("KUNSTPIXEL_PERSONDATA_DB", str(persondata))
    monkeypatch.setattr(register, "REGISTER_STI", tmp_path / "feilmeldinger.csv")
    return tmp_path / "feilmeldinger.csv"


def _melding(**endre):
    m = {
        "melder_ansatt_id": next(
            a["ansatt_id"] for a in objekter.alle_ansatte() if a["ansatt_til"] is None and a["ansatt_fra"] <= "2026-11-02"
        ),
        "oppgave": "Sjekket gavekort for en kunde i skranken",
        "objekttype": "verk",
        "objekt_id": objekter.list_objekter("verk")[0]["id"],
        "felt": "tittel",
        "beskrivelse": "Tittelen stemmer ikke med skiltet i salen",
        "forslag": "",
    }
    m.update(endre)
    return m


def test_objekttyper_dekker_kundedata_og_museum():
    typer = {t["type"] for t in objekter.objekttyper()}
    assert {"kontakt", "medlemskap", "gavekort", "arrangement", "verk", "ansatt", "dagsbesok", "arsoversikt"} <= typer


def test_list_og_sok_objekter(miljo):
    alle = objekter.list_objekter("gavekort", limit=5)
    assert len(alle) == 5 and all(o["id"].startswith("GK-") for o in alle)
    treff = objekter.list_objekter("gavekort", sok=alle[0]["id"][:7])
    assert any(o["id"] == alle[0]["id"] for o in treff)


def test_hent_original_viser_rad_og_kilde(miljo):
    oid = objekter.list_objekter("medlemskap", limit=1)[0]["id"]
    o = objekter.hent_objekt("medlemskap", oid)
    assert o["felt"]["medlemskap_id"] == int(oid) and "persondata" in o["kilde"]
    assert objekter.hent_objekt("arsoversikt", "2024")["felt"]["besok_totalt"] == 145156


def test_ukjent_type_og_injeksjon_avvises(miljo):
    with pytest.raises(ValueError):
        objekter.list_objekter("sqlite_master")
    assert objekter.hent_objekt("verk", "1' OR '1'='1") is None


def test_aktive_ansatte_er_i_jobb():
    aktive = objekter.aktive_ansatte(date(2026, 11, 2))
    assert len(aktive) == 72 and all(a["navn"] for a in aktive)


def test_registrer_lagrer_melding_med_original(miljo):
    mid = register.registrer(_melding(), naa="2026-11-02T10:15")
    assert mid == "FM-0001"
    rader = register.liste()
    assert rader[0]["status"] == "ny" and rader[0]["mottaker"] == register.MOTTAKER
    assert json.loads(rader[0]["original"])["tittel"]
    assert register.registrer(_melding(), naa="2026-11-02T10:20") == "FM-0002"


def test_registrer_krever_gyldig_melder_objekt_og_felt(miljo):
    sluttet = next(a for a in objekter.alle_ansatte() if a["ansatt_til"] and a["ansatt_til"] < "2020-01-01")
    for feil in [
        _melding(melder_ansatt_id=sluttet["ansatt_id"]),
        _melding(objekttype="tull"),
        _melding(objekt_id="finnes-ikke"),
        _melding(felt="finnes_ikke"),
        _melding(beskrivelse="   "),
    ]:
        with pytest.raises(ValueError):
            register.registrer(feil, naa="2026-11-02T10:00")
    assert register.liste() == []


def test_oppdater_status(miljo):
    mid = register.registrer(_melding(), naa="2026-11-02T10:15")
    register.oppdater_status(mid, "rettet", "Tittelen rettet i kildefila", naa="2026-11-03T09:00")
    r = register.liste()[0]
    assert (r["status"], r["kommentar"], r["status_dato"]) == ("rettet", "Tittelen rettet i kildefila", "2026-11-03T09:00")
    with pytest.raises(ValueError):
        register.oppdater_status(mid, "glemt", "")


def test_registerfila_kan_aapnes_i_excel(miljo):
    register.registrer(_melding(beskrivelse="Feil; med semikolon og æøå"), naa="2026-11-02T10:15")
    with open(miljo, encoding="utf-8-sig", newline="") as f:
        rader = list(csv.DictReader(f, delimiter=";"))
    assert rader[0]["beskrivelse"] == "Feil; med semikolon og æøå"


def test_nettsiden_tar_imot_en_melding(miljo):
    from src.kunstpixel.feilmelding import web
    server = web.lag_server(port=0)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        assert b"Meld en feil" in urllib.request.urlopen(base + "/").read()
        typer = json.loads(urllib.request.urlopen(base + "/api/objekttyper").read())
        assert any(t["type"] == "verk" for t in typer)
        req = urllib.request.Request(base + "/api/meld", data=json.dumps(_melding()).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        svar = json.loads(urllib.request.urlopen(req).read())
        assert svar["melding_id"] == "FM-0001"
        ugyldig = urllib.request.Request(base + "/api/meld", data=json.dumps(_melding(felt="x")).encode(), method="POST")
        with pytest.raises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(ugyldig)
        assert e.value.code == 400
    finally:
        server.shutdown()
