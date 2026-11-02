"""Funn fra sluttgjennomgang: førstegangsbygg, atomisk bygg, CSV-validering, justerbar YAML, stengte dager."""

import copy
import random
import shutil
import sqlite3

import pytest
from faker import Faker

from src.kunstpixel.persondata import ansattkilde as ak
from src.kunstpixel.persondata import config
from src.kunstpixel.persondata.generer import CSV_KODING, CsvFeil, bygg_database, bygg_fra_csv

START, REF = config.KUNDER_START, config.REFERANSEDATO


@pytest.fixture(scope="module")
def kilde(tmp_path_factory):
    d = tmp_path_factory.mktemp("kilde")
    bygg_database(d / "p.db", skala="test", csv_dir=d / "csv")
    return d


def _kopi(kilde, tmp_path):
    shutil.copytree(kilde / "csv", tmp_path / "csv")
    shutil.copy(kilde / "p.db", tmp_path / "p.db")
    return tmp_path / "csv", tmp_path / "p.db"


def _rediger(sti, gammel, ny):
    tekst = sti.read_text(encoding=CSV_KODING)
    assert gammel in tekst
    sti.write_text(tekst.replace(gammel, ny, 1), encoding=CSV_KODING)


def _antall(db, tabell="kontakter"):
    with sqlite3.connect(db) as c:
        return c.execute(f"SELECT COUNT(*) FROM {tabell}").fetchone()[0]


# --- Funn 1: fersk klone har CSV men ikke database -------------------------
def test_fersk_klone_peker_til_fra_csv(kilde, tmp_path):
    csv_dir, _ = _kopi(kilde, tmp_path)
    with pytest.raises(FileExistsError, match="--fra-csv"):
        bygg_database(tmp_path / "mangler.db", skala="test", csv_dir=csv_dir)
    assert bygg_fra_csv(tmp_path / "mangler.db", csv_dir=csv_dir)["kontakter"] > 0


def test_mcp_feilmelding_peker_til_fra_csv(monkeypatch, tmp_path):
    monkeypatch.setenv("KUNSTPIXEL_PERSONDATA_DB", str(tmp_path / "finnes_ikke.db"))
    from src.kunstpixel.persondata import mcp_server
    with pytest.raises(FileNotFoundError, match="--fra-csv"):
        mcp_server.list_tabeller()


# --- Funn 2: feil i CSV skal ikke ødelegge databasen -----------------------
def test_tomme_rader_fra_excel_hoppes_over(kilde, tmp_path):
    csv_dir, db = _kopi(kilde, tmp_path)
    with open(csv_dir / "gavekort_bruk.csv", "a", encoding=CSV_KODING) as f:
        f.write(";;;;;;\r\n;;;;;;\r\n")
    assert bygg_fra_csv(db, csv_dir=csv_dir, overskriv=True)["gavekort_bruk"] == _antall(kilde / "p.db", "gavekort_bruk")


def test_ugyldig_rad_bevarer_gammel_database(kilde, tmp_path):
    csv_dir, db = _kopi(kilde, tmp_path)
    for_ = _antall(db)
    with open(csv_dir / "gavekort_bruk.csv", "a", encoding=CSV_KODING) as f:
        f.write(";;2024-01-01;10.0;butikk;syntetisk (persondata_generator)\r\n")
    with pytest.raises(CsvFeil):
        bygg_fra_csv(db, csv_dir=csv_dir, overskriv=True)
    assert _antall(db) == for_


def test_ugyldig_yaml_verdi_bevarer_gammel_database(kilde, tmp_path, monkeypatch):
    _, db = _kopi(kilde, tmp_path)
    for_ = _antall(db)
    monkeypatch.setattr(config, "MEDLEMSKAPSTYPER", {})
    with pytest.raises(Exception):
        bygg_database(db, skala="test", csv_dir=None, overskriv=True)
    assert _antall(db) == for_


# --- Funn 3: Excel-formater ------------------------------------------------
def test_desimalkomma_godtas_og_blir_tall(kilde, tmp_path):
    csv_dir, db = _kopi(kilde, tmp_path)
    _rediger(csv_dir / "fordel_bruk.csv", ";75.0;", ";75,5;")
    bygg_fra_csv(db, csv_dir=csv_dir, overskriv=True)
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT typeof(rabatt_belop) FROM fordel_bruk WHERE rabatt_belop = 75.5").fetchone() == ("real",)


def test_norsk_datoformat_avvises_med_rad_og_kolonne(kilde, tmp_path):
    csv_dir, db = _kopi(kilde, tmp_path)
    with sqlite3.connect(db) as c:
        dato = c.execute("SELECT dato FROM utleie LIMIT 1").fetchone()[0]
    aa, mm, dd = dato.split("-")
    _rediger(csv_dir / "utleie.csv", dato, f"{dd}.{mm}.{aa}")
    with pytest.raises(CsvFeil, match=r"utleie\.csv.*rad \d+.*dato"):
        bygg_fra_csv(db, csv_dir=csv_dir, overskriv=True)


def test_telefon_uten_null_avvises(kilde, tmp_path):
    csv_dir, db = _kopi(kilde, tmp_path)
    with sqlite3.connect(db) as c:
        tlf = c.execute("SELECT telefon FROM kontakter WHERE telefon IS NOT NULL LIMIT 1").fetchone()[0]
    _rediger(csv_dir / "kontakter.csv", f";{tlf};", f";{tlf[1:]};")
    with pytest.raises(CsvFeil, match="telefon"):
        bygg_fra_csv(db, csv_dir=csv_dir, overskriv=True)


# --- Funn 4: YAML kan endres uten å røre koden -----------------------------
def test_ny_fordel_i_yaml_virker(tmp_path, monkeypatch):
    fordeler = copy.deepcopy(config.FORDELER)
    fordeler["parkering"] = {"beskrivelse": "Gratis parkering", "typer": ["venn", "enkelt"], "verdi": 40}
    monkeypatch.setattr(config, "FORDELER", fordeler)
    bygg_database(tmp_path / "p.db", skala="full", csv_dir=None)
    with sqlite3.connect(tmp_path / "p.db") as c:
        assert c.execute("SELECT COUNT(*) FROM fordel_bruk WHERE fordel='parkering'").fetchone()[0] > 0


def test_nye_gavekortbelop_virker(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "GAVEKORT", {**config.GAVEKORT, "belop": [250, 750]})
    bygg_database(tmp_path / "p.db", skala="test", csv_dir=None)
    with sqlite3.connect(tmp_path / "p.db") as c:
        assert {r[0] for r in c.execute("SELECT DISTINCT belop FROM gavekort")} <= {250, 750}


def test_valider_innstillinger_gir_lesbar_feil():
    inn = copy.deepcopy(config.INNSTILLINGER)
    del inn["medlemskapstyper"]["ansatt"]
    with pytest.raises(ValueError, match="ansatt"):
        config.valider_innstillinger(inn)
    inn = copy.deepcopy(config.INNSTILLINGER)
    inn["fordeler"]["fri_inngang"]["typer"].append("finnes_ikke")
    with pytest.raises(ValueError, match="finnes_ikke"):
        config.valider_innstillinger(inn)
    config.valider_innstillinger(config.INNSTILLINGER)


# --- Funn 5: fysisk aktivitet bare på åpne dager ---------------------------
def test_fysisk_aktivitet_bare_paa_aapne_dager():
    museum = config.MUSEUM_DB_STI
    dagsbesok = ak.hent_dagsbesok(museum, START, REF)
    aapen = {d.isoformat() for d, (_, a) in dagsbesok.items() if a}
    fake = Faker("no_NO")
    fake.seed_instance(2026)
    from src.kunstpixel.persondata.kunder import generer_kunder
    d = generer_kunder(random.Random(2026), fake, ak.hent_ansatte(museum), dagsbesok, ak.hent_hendelser(museum), 1.0)
    sjekk = [
        ("gavekort_bruk", "dato", lambda r: r["sted"] != "arrangement"),
        ("fordel_bruk", "dato", lambda r: True),
        ("skolebestillinger", "dato", lambda r: True),
        ("gavekort", "utstedt", lambda r: r["kanal"] != "nettbutikk"),
        ("medlemskap", "startdato", lambda r: r["solgt_av_ansatt_id"] is not None and r["type"] != "ansatt"),
    ]
    for tabell, felt, gjelder in sjekk:
        stengt = [r[felt] for r in d[tabell] if gjelder(r) and r[felt] not in aapen]
        assert not stengt, f"{tabell}: {len(stengt)} rader på stengte dager"
