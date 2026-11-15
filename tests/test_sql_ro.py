"""Tester for scripts/sql_ro.py: kontrollørens eneste vei inn i museum.db (L7)."""

import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
SKRIPT = ROT / "scripts" / "sql_ro.py"


def kjor(sql: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SKRIPT), sql],
        cwd=ROT, capture_output=True, text=True, encoding="utf-8",
    )


def test_select_gir_rader():
    r = kjor("SELECT count(*) AS antall FROM verk")
    assert r.returncode == 0, r.stderr
    assert "antall" in r.stdout
    assert "16" in r.stdout


def test_with_er_tillatt():
    r = kjor("WITH x AS (SELECT 1 AS n) SELECT n FROM x")
    assert r.returncode == 0, r.stderr


def test_skriving_avvises_og_endrer_ingenting():
    for sql in (
        "DELETE FROM verk",
        "UPDATE verk SET id = id",
        "DROP TABLE verk",
        "INSERT INTO saler(id) VALUES ('X')",
        "SELECT 1; DELETE FROM verk",
        "ATTACH DATABASE 'x.db' AS x",
        "PRAGMA writable_schema = 1",
    ):
        r = kjor(sql)
        assert r.returncode != 0, f"Ble ikke avvist: {sql}"
    assert "16" in kjor("SELECT count(*) FROM verk").stdout


def test_ukjent_tabell_gir_lesbar_feil():
    r = kjor("SELECT * FROM finnes_ikke")
    assert r.returncode != 0
    assert "finnes_ikke" in r.stderr
