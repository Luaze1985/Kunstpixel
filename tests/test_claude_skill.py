"""Skill-pakken for Claude-appen (DECISIONS C1–C5): museum.db + lesende SQL-skript + definisjoner i én zip.

Pakken bygges av scripts/lag_claude_skill.py og lastes opp av Lars i claude.ai (Customize > Skills).
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "05_data" / "museum.db"
NAVN = "kunstpixel-demo"
MAKS_UKOMPRIMERT = 30 * 1024 * 1024  # grensen i Anthropics skill-dokumentasjon


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def pakke(tmp_path_factory) -> Path:
    ut = tmp_path_factory.mktemp("skill")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "lag_claude_skill.py"), "--ut", str(ut)],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    zipfil = ut / f"{NAVN}.zip"
    assert zipfil.exists()
    return zipfil


@pytest.fixture(scope="module")
def utpakket(pakke: Path, tmp_path_factory) -> Path:
    mappe = tmp_path_factory.mktemp("utpakket")
    with zipfile.ZipFile(pakke) as z:
        z.extractall(mappe)
    return mappe / NAVN


def test_zip_har_en_mappe_med_skillnavnet(pakke: Path) -> None:
    with zipfile.ZipFile(pakke) as z:
        toppnivaa = {n.split("/")[0] for n in z.namelist()}
    assert toppnivaa == {NAVN}


def test_skill_md_har_riktig_navn_og_beskrivelse(utpakket: Path) -> None:
    tekst = (utpakket / "SKILL.md").read_text(encoding="utf-8")
    assert tekst.startswith("---\n")
    hode = tekst.split("---")[1]
    assert f"name: {NAVN}" in hode
    assert "description:" in hode


def test_skill_md_peker_bare_paa_filer_i_pakken(utpakket: Path) -> None:
    tekst = (utpakket / "SKILL.md").read_text(encoding="utf-8")
    assert "05_data/" not in tekst and "mcp__" not in tekst
    for ref in ["scripts/sql.py", "references/kjente-hull.md", "references/metrics.md"]:
        assert ref in tekst
        assert (utpakket / ref).exists(), ref


def test_skill_md_slaar_opp_titler_selv(utpakket: Path) -> None:
    """Lars spør med tittel, sal eller periode, aldri med ID (DECISIONS C7)."""
    tekst = (utpakket / "SKILL.md").read_text(encoding="utf-8")
    assert "aldri med ID" in tekst
    assert "tittel" in tekst and "sal" in tekst


def test_skill_md_viser_begge_kilder_ved_uenighet(utpakket: Path) -> None:
    """Hullene står ikke som fasit. Claude skal oppdage motsigelser selv og vise begge kildene (C7)."""
    tekst = (utpakket / "SKILL.md").read_text(encoding="utf-8")
    assert "to kilder er uenige" in tekst
    hull = (utpakket / "references" / "kjente-hull.md").read_text(encoding="utf-8")
    assert "Stille kraft" not in hull and "Lys innenfra" not in hull


def test_databasen_er_lik_den_i_repoet(utpakket: Path) -> None:
    assert _sha(utpakket / "data" / "museum.db") == _sha(DB)


def test_pakken_er_under_grensen(pakke: Path) -> None:
    with zipfile.ZipFile(pakke) as z:
        assert sum(i.file_size for i in z.infolist()) < MAKS_UKOMPRIMERT


def test_kjente_hull_er_regnet_fra_databasen(utpakket: Path) -> None:
    tekst = (utpakket / "references" / "kjente-hull.md").read_text(encoding="utf-8")
    # Tidsdekning per tabell, regnet ved bygging (ikke skrevet for hånd).
    for tabell in ["dagsbesok", "besok_tilfredshet", "kafe_varesalg", "hr_vakter"]:
        assert tabell in tekst
    assert "2026-10-29" in tekst  # tilfredshet, anmeldelser og kafé slutter her
    assert "1 287" in tekst or "1287" in tekst  # vakter over døgnmaks


def _sql(utpakket: Path, sql: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(utpakket / "scripts" / "sql.py"), sql],
                          capture_output=True, text=True, encoding="utf-8")


def test_sql_skriptet_leser(utpakket: Path) -> None:
    r = _sql(utpakket, "SELECT count(*) AS n FROM hr_ansatte WHERE status <> 'Sluttet'")
    assert r.returncode == 0, r.stderr
    assert "74" in r.stdout


@pytest.mark.parametrize("sql", [
    "DELETE FROM hr_ansatte",
    "UPDATE hr_ansatte SET navn = 'x'",
    "SELECT 1; DROP TABLE hr_ansatte",
    "ATTACH DATABASE 'x.db' AS x",
    "PRAGMA writable_schema = 1",
])
def test_sql_skriptet_avviser_skriving(utpakket: Path, sql: str) -> None:
    for_ = _sha(utpakket / "data" / "museum.db")
    r = _sql(utpakket, sql)
    assert r.returncode != 0
    assert "AVVIST" in r.stderr
    assert _sha(utpakket / "data" / "museum.db") == for_


def test_sql_skriptet_virker_uten_prosjektet(utpakket: Path, tmp_path: Path) -> None:
    """I Claude-appen finnes bare pakken. Skriptet kan ikke importere noe fra repoet."""
    kode = (utpakket / "scripts" / "sql.py").read_text(encoding="utf-8")
    assert "src." not in kode and "kunstpixel.core" not in kode
    r = subprocess.run([sys.executable, str(utpakket / "scripts" / "sql.py"), "SELECT 1 AS en"],
                       cwd=tmp_path, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and "1" in r.stdout


def test_sql_skriptet_viser_tabeller_og_kolonner(utpakket: Path) -> None:
    s = str(utpakket / "scripts" / "sql.py")
    t = subprocess.run([sys.executable, s, "--tabeller"], capture_output=True, text=True, encoding="utf-8")
    assert t.returncode == 0 and "hr_vakter" in t.stdout
    k = subprocess.run([sys.executable, s, "--kolonner", "hr_vakter"], capture_output=True, text=True, encoding="utf-8")
    assert k.returncode == 0, k.stderr
    assert "timer" in k.stdout and "ansatt_id" in k.stdout


def test_sql_skriptet_skriver_norske_tegn_som_utf8(utpakket: Path) -> None:
    r = subprocess.run([sys.executable, str(utpakket / "scripts" / "sql.py"), "SELECT 'Sæther øå' AS t"],
                       capture_output=True)
    assert "Sæther øå".encode() in r.stdout
