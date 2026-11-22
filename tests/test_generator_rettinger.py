"""Regelbaserte rettinger i datageneratoren (DECISIONS S5 og F1).

R1: overtidsvakter som ikke er over døgnmaks skal ha timer = slutt − start − 0,5 slik byggeskriptet regner slutt.
R6: noen lange sykemeldinger (5–10 uker) slik at fristene uke 4 og uke 7 faktisk kan slå ut.
Testene skriver til tmp_path og leser bare museum_base.db (ikke museum.db).
"""

from __future__ import annotations

import csv
import sqlite3
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from src.kunstpixel.data import archive_generator as gen

ROT = Path(__file__).resolve().parent.parent
BASE_DB = ROT / "05_data" / "kilde" / "museum_base.db"

pytestmark = pytest.mark.skipif(not BASE_DB.is_file(), reason="mangler museum_base.db")


def _les(p: Path) -> list[dict]:
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _min(hhmm: str) -> int:
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


def _bygg_slutt(start: str, timer: float) -> str:
    """Samme regel som bygg_hr_vakter i build_museum_db.py (klemmer på time 23)."""
    slutt_m = _min(start) + round(timer * 60) + 30
    return f"{min(23, slutt_m // 60):02d}:{min(59, slutt_m % 60):02d}"


# ---------- R1 ----------

def test_overtid_under_dognmaks_stemmer_med_klokka(tmp_path: Path) -> None:
    ut = tmp_path / "just.csv"
    gen.generate_shift_adjustments(ut)
    start = {r["vakt_id"]: r["start"] for r in _les(gen.KLOKKESLETT_CSV)}
    korte_avvik, lange_avvik = [], []
    for r in _les(ut):
        timer = float(r["nye_timer"])
        s = start[r["vakt_id"]]
        beregnet = (_min(_bygg_slutt(s, timer)) - _min(s)) / 60 - 0.5
        if abs(beregnet - timer) > 1e-9:
            (korte_avvik if timer <= 9.0 else lange_avvik).append(r["vakt_id"])
    assert korte_avvik == []
    assert len(lange_avvik) == 66  # de lange står urørt (S5: Lars' valg)


# ---------- R6 ----------

def _lange_syke(rader: list[dict]) -> list[dict]:
    return [r for r in rader if r["type"] == "sykemelding"
            and (date.fromisoformat(r["til"]) - date.fromisoformat(r["fra"])).days + 1 >= 28]


def test_lange_sykemeldinger_finnes_og_kolliderer_ikke(tmp_path: Path) -> None:
    ut = tmp_path / "frav.csv"
    gen.generate_absence_records(ut)
    rader = _les(ut)
    lange = _lange_syke(rader)
    assert 3 <= len(lange) <= 5
    assert len({r["ansatt_id"] for r in lange}) == len(lange)

    con = sqlite3.connect(f"file:{BASE_DB.as_posix()}?mode=ro", uri=True)
    try:
        ansatte = {a: (fra, status) for a, fra, status in
                   con.execute("SELECT ansatt_id, ansatt_fra, status FROM hr_ansatte")}
        vakter = set(con.execute("SELECT ansatt_id, dato FROM hr_vakter").fetchall())
    finally:
        con.close()

    for r in lange:
        fra, til = date.fromisoformat(r["fra"]), date.fromisoformat(r["til"])
        assert 35 <= (til - fra).days + 1 <= 70, r
        a_fra, status = ansatte[r["ansatt_id"]]
        assert status != "Sluttet" and r["fra"] >= a_fra, r
        assert r["datakilde"].startswith("syntetisk")
        d = fra
        while d <= til:
            assert (r["ansatt_id"], d.isoformat()) not in vakter, r
            d += timedelta(days=1)
        for o in rader:
            if o is not r and o["ansatt_id"] == r["ansatt_id"]:
                assert o["til"] < r["fra"] or o["fra"] > r["til"], (r, o)

    def pagar(dag: str) -> list[dict]:
        grense = (date.fromisoformat(dag) - timedelta(days=28)).isoformat()
        return [r for r in lange if r["fra"] <= grense and r["til"] >= dag]

    assert pagar("2026-09-14"), "ingen lang sykemelding pågår testenes «i dag» etter 4 uker"
    assert pagar("2026-11-22"), "ingen lang sykemelding pågår 2026-11-22 etter 4 uker"

    # Høyst én lang sykemelding per kvartal, så kvartalet holder seg nær SSB (±1,5 pp).
    kvartaler = [{(d.year, (d.month - 1) // 3) for d in (date.fromisoformat(r["fra"]) + timedelta(days=i)
                  for i in range((date.fromisoformat(r["til"]) - date.fromisoformat(r["fra"])).days + 1))}
                 for r in lange]
    alle = [k for ks in kvartaler for k in ks]
    assert len(alle) == len(set(alle)), kvartaler


def test_fravaer_og_justering_er_deterministiske(tmp_path: Path) -> None:
    """To separate prosesser (ulik hash-seed) gir byte-like filer."""
    kode = ("import sys; from pathlib import Path; sys.path.insert(0, r'{rot}');"
            "from src.kunstpixel.data import archive_generator as g;"
            "g.generate_absence_records(Path(r'{d}') / 'frav.csv');"
            "g.generate_shift_adjustments(Path(r'{d}') / 'just.csv')")
    for navn in ("a", "b"):
        (tmp_path / navn).mkdir()
        subprocess.run([sys.executable, "-c", kode.format(rot=ROT, d=tmp_path / navn)], check=True, cwd=ROT)
    for fil in ("frav.csv", "just.csv"):
        assert (tmp_path / "a" / fil).read_bytes() == (tmp_path / "b" / fil).read_bytes(), fil
