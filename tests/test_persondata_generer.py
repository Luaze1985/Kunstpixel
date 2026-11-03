"""Task 4: bygg persondata.db, eksporter til CSV og bygg på nytt fra CSV."""

import csv
import hashlib
import sqlite3

import pytest

from src.kunstpixel.persondata import config
from src.kunstpixel.persondata.generer import CSV_SKILLETEGN, bygg_database, bygg_fra_csv

TABELLER = {
    "kontakter", "medlemskapstyper", "fordeler", "medlemskapstype_fordel", "medlemskap",
    "medlemsbesok", "fordel_bruk", "gavekort", "gavekort_bruk", "arrangementer",
    "pameldinger", "skolebestillinger", "utleie", "henvendelser",
}


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _innhold(sti):
    with sqlite3.connect(sti) as c:
        return {t: c.execute(f'SELECT * FROM "{t}" ORDER BY 1, 2').fetchall() for t in TABELLER}


@pytest.fixture(scope="module")
def bygget(tmp_path_factory):
    d = tmp_path_factory.mktemp("bygg")
    antall = bygg_database(d / "p.db", skala="test", csv_dir=d / "csv")
    return d, antall


def test_bygger_alle_tabeller(bygget):
    _, antall = bygget
    assert set(antall) == TABELLER
    assert all(n > 0 for n in antall.values())


def test_nekter_overskriving(bygget):
    d, _ = bygget
    mtime = (d / "p.db").stat().st_mtime_ns
    with pytest.raises(FileExistsError, match="--overskriv"):
        bygg_database(d / "p.db", skala="test", csv_dir=d / "csv")
    assert (d / "p.db").stat().st_mtime_ns == mtime


def test_nekter_aa_overskrive_csv(tmp_path, bygget):
    d, _ = bygget
    with pytest.raises(FileExistsError, match="--overskriv"):
        bygg_database(tmp_path / "ny.db", skala="test", csv_dir=d / "csv")


def test_overskriv_flagg(tmp_path):
    bygg_database(tmp_path / "p.db", skala="test", csv_dir=tmp_path / "csv")
    assert bygg_database(tmp_path / "p.db", skala="test", csv_dir=tmp_path / "csv", overskriv=True)


def test_deterministisk_innhold(tmp_path, bygget):
    d, _ = bygget
    bygg_database(tmp_path / "b.db", skala="test", csv_dir=tmp_path / "csv")
    assert _innhold(d / "p.db") == _innhold(tmp_path / "b.db")


def test_ukjent_skala(tmp_path):
    with pytest.raises(ValueError):
        bygg_database(tmp_path / "x.db", skala="enorm", csv_dir=tmp_path / "csv")


def test_museum_db_uendret(tmp_path):
    for_ = _sha(config.MUSEUM_DB_STI)
    bygg_database(tmp_path / "p.db", skala="test", csv_dir=tmp_path / "csv")
    assert _sha(config.MUSEUM_DB_STI) == for_


def test_fremmednokler_gyldige(bygget):
    d, _ = bygget
    with sqlite3.connect(d / "p.db") as c:
        assert c.execute("PRAGMA foreign_key_check").fetchall() == []


def test_csv_per_tabell_med_like_mange_rader(bygget):
    d, antall = bygget
    for t in TABELLER:
        with open(d / "csv" / f"{t}.csv", encoding="utf-8-sig", newline="") as f:
            rader = list(csv.reader(f, delimiter=CSV_SKILLETEGN))
        assert len(rader) - 1 == antall[t], t


def test_fra_csv_gir_samme_innhold(tmp_path, bygget):
    d, _ = bygget
    bygg_fra_csv(tmp_path / "fra_csv.db", csv_dir=d / "csv")
    assert _innhold(tmp_path / "fra_csv.db") == _innhold(d / "p.db")


def test_fra_csv_bevarer_manuelle_endringer(tmp_path):
    csv_dir = tmp_path / "csv"
    bygg_database(tmp_path / "p.db", skala="test", csv_dir=csv_dir)
    sti = csv_dir / "medlemskapstyper.csv"
    tekst = sti.read_text(encoding="utf-8-sig").replace(f"enkelt{CSV_SKILLETEGN}450", f"enkelt{CSV_SKILLETEGN}495")
    sti.write_text(tekst, encoding="utf-8-sig")
    bygg_fra_csv(tmp_path / "justert.db", csv_dir=csv_dir)
    with sqlite3.connect(tmp_path / "justert.db") as c:
        assert c.execute("SELECT aarspris FROM medlemskapstyper WHERE type='enkelt'").fetchone() == (495,)


def test_norske_tegn_overlever_csv(tmp_path, bygget):
    d, _ = bygget
    bygg_fra_csv(tmp_path / "t.db", csv_dir=d / "csv")
    with sqlite3.connect(tmp_path / "t.db") as c:
        navn = " ".join(r[0] for r in c.execute("SELECT fornavn || ' ' || etternavn FROM kontakter"))
    assert any(t in navn for t in "æøåÆØÅ")
