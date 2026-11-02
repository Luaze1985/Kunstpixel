"""Task 1: skjema, konfigurasjon og innstillinger for kundedata (syntetisk)."""

import random
import re
import sqlite3

from src.kunstpixel.core.datapolicy import normalize_classification
from src.kunstpixel.persondata import config

TABELLER = {
    "kontakter", "medlemskapstyper", "fordeler", "medlemskapstype_fordel", "medlemskap",
    "medlemsbesok", "fordel_bruk", "gavekort", "gavekort_bruk", "arrangementer",
    "pameldinger", "skolebestillinger", "utleie", "henvendelser",
}


def _mem_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(config.SCHEMA_STI.read_text(encoding="utf-8"))
    return conn


def test_schema_lager_alle_tabeller():
    conn = _mem_db()
    navn = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert navn == TABELLER


def test_alle_tabeller_har_datakilde():
    conn = _mem_db()
    for t in TABELLER:
        kolonner = {r[1] for r in conn.execute(f'PRAGMA table_info("{t}")')}
        assert "datakilde" in kolonner, t


def test_ingen_forbudte_kolonner():
    conn = _mem_db()
    forbudt = re.compile(r"fodselsnummer|fnr|adresse|kontonummer|kortnummer|fodt|barn_navn")
    for t in TABELLER:
        for r in conn.execute(f'PRAGMA table_info("{t}")'):
            assert not forbudt.search(r[1]), f"{t}.{r[1]}"


def test_lag_epost():
    assert config.lag_epost("Bjørg", "Åsen", 7) == "bjorg.aasen.7@eksempel.invalid"
    assert config.lag_epost("Per-Ivar", "Faye Lund", 12) == "per.ivar.faye.lund.12@eksempel.invalid"


def test_lag_telefon():
    rng = random.Random(1)
    assert all(re.fullmatch(r"0\d{7}", config.lag_telefon(rng)) for _ in range(1000))


def test_datakilde_godtas_av_datapolicy():
    assert normalize_classification(config.DATAKILDE) == "syntetisk"


def test_fordeler_dekker_alle_typer():
    for type_ in config.MEDLEMSKAPSTYPER:
        assert type_ in config.FORDELER["fri_inngang"]["typer"], type_


def test_innstillinger_leses_fra_yaml():
    assert config.INNSTILLINGER_STI.name == "innstillinger.yaml"
    assert config.INNSTILLINGER_STI.is_file()
    assert config.MEDLEMSKAPSTYPER["enkelt"]["aarspris"] == 450
    assert config.VOLUM["kontakter"] == 5000


def test_gitignore():
    linjer = (config.PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "05_data/persondata/*.db" in linjer
    assert ".superpowers/" in linjer
