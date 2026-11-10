"""Colab-settet for personvern i Trondheim (revisjonsfunn 3, 4 og 5).

- Fødselsnumrene bruker Tenor-formatet (måned + 80), så de kan aldri tilhøre en ekte person.
- Angrepsdataene har bare rådata. Konklusjonene (fasiten) ligger i en egen fil utenfor 05_data.
- Colab-databasen og MintHCM-dumpen spores ikke i git.
"""

from __future__ import annotations

import csv
import sqlite3
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CSV_168 = ROOT / "05_data" / "ansatte_168_komplett_personvern_trondheim.csv"
COLAB_DB = ROOT / "05_data" / "colab_personvern_historikk.db"
FASIT = ROOT / "fasit" / "personvern_trondheim_fasit.csv"
NOTATBOK = ROOT / "02_deliverables" / "02_rapporter" / "personvern_time_for_time_colab.ipynb"

FASITKOLONNER = [
    "inntektsavvik_analyse",
    "kollektiv_avvik_kobling",
    "habilitet_flagg",
    "mosaikk_risikoscore",
    "risikonivaa",
    "avslort_sensitiv_innsikt",
]
# Navnene kolonnene har i databasetabellen ekstern_osint_trondheim.
FASITKOLONNER_DB = {
    "inntektsavvik_forklaring",
    "kollektiv_avvik_treff",
    "habilitet_flagg",
    "mosaikk_risikoscore",
    "risikonivaa",
    "avslort_sensitiv_innsikt",
}
STORE_FILER = [
    "05_data/colab_personvern_historikk.db",
    "01_inbox/raw/minthcm-minthcm-8a5edab282632443.txt",
]


def _rader(sti: Path) -> list[dict[str, str]]:
    with sti.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _tenor_ok(fnr: str, fodselsdato: str) -> bool:
    aar, mnd, dag = fodselsdato.split("-")
    return fnr[:6] == f"{dag}{int(mnd) + 80:02d}{aar[2:]}" and 81 <= int(fnr[2:4]) <= 92


# ---------- Funn 3: Tenor-format ----------


def test_fnr_er_tenor_format():
    rader = _rader(CSV_168)
    assert len(rader) == 168
    feil = [r["syntetisk_fnr"] for r in rader if not _tenor_ok(r["syntetisk_fnr"], r["fodselsdato"])]
    assert not feil, f"{len(feil)} fødselsnumre er ikke i Tenor-format, f.eks. {feil[:3]}"


def test_fnr_er_unike():
    fnr = [r["syntetisk_fnr"] for r in _rader(CSV_168)]
    assert len(set(fnr)) == len(fnr)


# ---------- Funn 5: fasiten ligger ikke i angrepsdataene ----------


def test_angrepsdata_har_ikke_fasit():
    kolonner = set(_rader(CSV_168)[0])
    assert not kolonner & set(FASITKOLONNER), f"Fasit i angrepsdataene: {sorted(kolonner & set(FASITKOLONNER))}"


def test_fasitfilen_ligger_utenfor_05_data_og_dekker_alle_ansatte():
    assert "05_data" not in FASIT.relative_to(ROOT).parts
    fasit = _rader(FASIT)
    assert list(fasit[0]) == ["ansatt_id", *FASITKOLONNER]
    assert [r["ansatt_id"] for r in fasit] == [r["ansatt_id"] for r in _rader(CSV_168)]
    assert {r["risikonivaa"] for r in fasit} <= {"KRITISK", "HØY", "MODERAT", "LAV"}


@pytest.mark.skipif(not COLAB_DB.exists(), reason="Colab-databasen er ikke generert (spores ikke i git)")
def test_colab_db_har_ikke_fasit_og_bruker_tenor():
    con = sqlite3.connect(COLAB_DB.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        kolonner = {r[1] for r in con.execute("PRAGMA table_info(ekstern_osint_trondheim)")}
        assert not kolonner & FASITKOLONNER_DB, f"Fasit i databasen: {sorted(kolonner & FASITKOLONNER_DB)}"
        rader = con.execute("SELECT syntetisk_fnr, fodselsdato FROM hr_utvidet_profil_trondheim").fetchall()
    finally:
        con.close()
    assert len(rader) == 168
    assert all(_tenor_ok(fnr, fdato) for fnr, fdato in rader)


def test_notatboken_henter_fasiten_fra_egen_fil():
    tekst = NOTATBOK.read_text(encoding="utf-8")
    assert "personvern_trondheim_fasit.csv" in tekst
    assert "HAR_FASIT" in tekst


# ---------- Funn 4: store filer spores ikke ----------


@pytest.mark.parametrize("sti", STORE_FILER)
def test_store_filer_spores_ikke(sti):
    sporet = subprocess.run(
        ["git", "ls-files", "--", sti], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert sporet == "", f"{sti} spores fortsatt i git"
    ignorert = subprocess.run(["git", "check-ignore", "-q", "--", sti], cwd=ROOT)
    assert ignorert.returncode == 0, f"{sti} står ikke i .gitignore"
