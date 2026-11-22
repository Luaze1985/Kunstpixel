"""Driftsregnskap per måned 2010–2026 (Ø1, Lars 2026-11-22: vaktene og dagsdataene er fasit).

Hver regel i regnskap_builder har sin egen test mot et midlertidig bygg. Testen for konto 5000
sørger for at driftsregnskap.csv ikke glir fra vaktene: endres vaktene, må CSV-en lages på nytt.
"""

from __future__ import annotations

import csv
import hashlib
import shutil
import sqlite3
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

from src.kunstpixel.core import db
from src.kunstpixel.data import build_museum_db as bmd
from src.kunstpixel.data import regnskap_builder as rb

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "05_data" / "driftsregnskap.csv"
MAANEDER = [f"{a}-{m:02d}" for a in range(2010, 2027) for m in range(1, 13)]
KONTOER = {"3000", "3100", "3400", "3900", "4000", "5000", "5400", "6300", "6340", "6600", "6700", "6800", "7500"}
FASTE = ("6300", "6600", "6800", "7500")


def _kr(x: float) -> int:
    return int(Decimal(str(round(x, 2))).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _tkr(nok: int) -> int:
    return (nok + 500) // 1000


@pytest.fixture(scope="module")
def bygget(tmp_path_factory: pytest.TempPathFactory) -> Path:
    mappe = tmp_path_factory.mktemp("driftsregnskap")
    for navn in ("arkiv_cv_personas.json", "arkiv_hr_innleide_personer.csv"):
        shutil.copyfile(ROOT / "05_data" / navn, mappe / navn)
    sti = mappe / "museum.db"
    bmd.bygg(sti)
    return sti


@pytest.fixture(scope="module")
def con(bygget: Path):
    c = sqlite3.connect(f"file:{bygget.as_posix()}?mode=ro", uri=True)
    yield c
    c.close()


@pytest.fixture(scope="module")
def regnskap(con) -> dict[tuple[str, str], int]:
    return {(m, k): b for m, k, b in con.execute("SELECT maaned, konto, belop_nok FROM driftsregnskap")}


def belop(regnskap: dict, maaned: str, konto: str) -> int:
    return regnskap.get((maaned, konto), 0)  # beløp 0 har ingen rad


@pytest.fixture(scope="module")
def h5_kilde() -> dict[int, dict]:
    with open(ROOT / "05_data" / "h5_historikk_2010_2026.csv", encoding="utf-8", newline="") as f:
        return {int(r["ar"]): r for r in csv.DictReader(f)}


# ---------- CSV og tabell ----------


def test_csv_har_riktige_kolonner_og_bare_positive_heltall() -> None:
    with open(CSV, encoding="utf-8", newline="") as f:
        rader = list(csv.DictReader(f))
    assert list(rader[0]) == ["maaned", "konto", "kontonavn", "belop_nok", "datakilde"]
    for r in rader:
        assert r["konto"] in KONTOER and r["datakilde"] == "syntetisk (regnskap_builder)"
        assert r["belop_nok"].isdigit() and int(r["belop_nok"]) > 0
        assert r["maaned"] in MAANEDER
    assert len({(r["maaned"], r["konto"]) for r in rader}) == len(rader)


def test_tabellen_er_lik_csv_en(con) -> None:
    with open(CSV, encoding="utf-8", newline="") as f:
        fra_csv = [(r["maaned"], r["konto"], r["kontonavn"], int(r["belop_nok"]), r["datakilde"]) for r in csv.DictReader(f)]
    i_db = con.execute("SELECT maaned, konto, kontonavn, belop_nok, datakilde FROM driftsregnskap ORDER BY maaned, konto").fetchall()
    assert i_db == sorted(fra_csv)


def test_tabellen_avviser_ukjent_konto_og_dobbel_rad(bygget: Path, tmp_path: Path) -> None:
    kopi = tmp_path / "kopi.db"
    shutil.copyfile(bygget, kopi)
    c = sqlite3.connect(kopi)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO driftsregnskap VALUES ('2026-01', '9999', 'x', 1, 'syntetisk (regnskap_builder)')")
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO driftsregnskap VALUES ('2026-01', '5000', 'x', 1, 'syntetisk (regnskap_builder)')")
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO driftsregnskap VALUES ('2009-01', '5000', 'x', 0, 'syntetisk (regnskap_builder)')")
    finally:
        c.close()


def test_bygget_feiler_hoyt_uten_csv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(bmd, "DRIFTSREGNSKAP_CSV", tmp_path / "finnes_ikke.csv")
    with pytest.raises(FileNotFoundError, match="regnskap_builder"):
        bmd.bygg(tmp_path / "museum.db")


def test_generatoren_er_deterministisk_og_lik_csv_en(bygget: Path, tmp_path: Path) -> None:
    a = rb.skriv_csv(bygget, tmp_path / "a")
    b = rb.skriv_csv(bygget, tmp_path / "b")
    sha = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (a, b, CSV)]
    assert sha[0] == sha[1], "to kjøringer gir ulik fil"
    assert sha[0] == sha[2], "05_data/driftsregnskap.csv er utdatert: kjør py -3.13 src/kunstpixel/data/regnskap_builder.py"


# ---------- Regler som skal holde nøyaktig ----------


def test_5000_er_vaktlonn_for_maaneden(regnskap, bygget: Path) -> None:
    for m in MAANEDER:
        svar = db.query_shift_cost(m, bygget)
        assert svar["vakter_uten_tariff"] == 0
        assert belop(regnskap, m, "5000") == _kr(svar["kostnad_nok_totalt"]), m


def test_5400_er_141_promille_av_5000(regnskap) -> None:
    for m in MAANEDER:
        assert belop(regnskap, m, "5400") == (belop(regnskap, m, "5000") * 141 + 500) // 1000, m


def test_3000_er_billettinntekt_fra_dagsbesok(regnskap, con) -> None:
    fasit = dict(con.execute("SELECT substr(dato, 1, 7), SUM(inntekt_nok) FROM dagsbesok GROUP BY 1"))
    for m in MAANEDER:
        assert belop(regnskap, m, "3000") == fasit.get(m, 0), m


def test_3100_er_kafesalg_der_det_finnes_og_h5_ellers(regnskap, con, h5_kilde) -> None:
    salg = {m: _kr(s) for m, s in con.execute("SELECT substr(dato, 1, 7), SUM(omsetning_nok) FROM kafe_varesalg GROUP BY 1")}
    dekket = {int(m[:4]) for m in salg}
    assert dekket == {2024, 2025, 2026}
    for aar in range(2010, 2027):
        mnd = [f"{aar}-{i:02d}" for i in range(1, 13)]
        if aar in dekket:
            for m in mnd:
                assert belop(regnskap, m, "3100") == salg[m], m
        else:  # agentens valg: ingen kafésalg i dagsdataene før 2024, så h5 fordeles på 12 måneder
            total = int(h5_kilde[aar]["kafeinntekter_tkr"]) * 1000
            assert sum(belop(regnskap, m, "3100") for m in mnd) == total, aar
            assert {belop(regnskap, m, "3100") for m in mnd[:11]} == {total // 12}, aar


def test_4000_er_35_prosent_av_3100(regnskap) -> None:
    for m in MAANEDER:
        assert belop(regnskap, m, "4000") == (belop(regnskap, m, "3100") * 35 + 50) // 100, m


def test_6700_er_innleie_for_maaneden(regnskap, con) -> None:
    fasit = dict(con.execute("SELECT substr(periode_fra, 1, 7), SUM(totalbelop_nok) FROM hr_innleie GROUP BY 1"))
    for m in MAANEDER:
        assert belop(regnskap, m, "6700") == fasit.get(m, 0), m


@pytest.mark.parametrize("konto,felt", [("3400", "tilskudd_tkr"), ("3900", "andre_inntekter_tkr")])
def test_tilskudd_og_andre_inntekter_er_h5_fordelt_jevnt(regnskap, h5_kilde, konto: str, felt: str) -> None:
    for aar in range(2010, 2027):
        mnd = [belop(regnskap, f"{aar}-{i:02d}", konto) for i in range(1, 13)]
        total = int(h5_kilde[aar][felt]) * 1000
        assert sum(mnd) == total, aar
        assert set(mnd[:11]) == {total // 12}, aar


def test_strom_er_hoyere_om_vinteren_og_i_stromkrisa(regnskap) -> None:
    def aar_sum(a: int) -> int:
        return sum(belop(regnskap, f"{a}-{i:02d}", "6340") for i in range(1, 13))

    for aar in range(2010, 2027):
        vinter = [belop(regnskap, f"{aar}-{i:02d}", "6340") for i in (1, 2, 12)]
        sommer = [belop(regnskap, f"{aar}-{i:02d}", "6340") for i in (6, 7, 8)]
        assert min(vinter) > max(sommer), aar
    for krise in (2022, 2023):
        assert aar_sum(krise) > 1.3 * aar_sum(2021) and aar_sum(krise) > 1.2 * aar_sum(2024), krise


@pytest.mark.parametrize("konto", FASTE)
def test_faste_kostnader_er_like_hele_aaret_og_vokser_3_prosent(regnskap, konto: str) -> None:
    forrige = None
    for aar in range(2010, 2027):
        mnd = {belop(regnskap, f"{aar}-{i:02d}", konto) for i in range(1, 13)}
        assert len(mnd) == 1 and min(mnd) > 0, (konto, aar)
        (verdi,) = mnd
        if forrige is not None:
            assert 1.025 < verdi / forrige < 1.035, (konto, aar)
        forrige = verdi


# ---------- h5 regnet fra fasit ----------


def test_h5_er_regnet_fra_regnskapet_og_vaktene_alle_17_aar(con, regnskap, h5_kilde) -> None:
    vakttimer = dict(con.execute("SELECT CAST(substr(dato, 1, 4) AS INTEGER), SUM(timer) FROM hr_vakter GROUP BY 1"))
    besok = dict(con.execute("SELECT aar, SUM(besok_totalt) FROM dagsbesok GROUP BY aar"))
    kol = ("ar", "besok_totalt", "ansatte_arsverk", "billettinntekter_tkr", "tilskudd_tkr", "kafeinntekter_tkr",
           "andre_inntekter_tkr", "inntekter_totalt_tkr", "kostnader_tkr", "resultat_tkr", "tema", "skoleelever")
    rader = [dict(zip(kol, r)) for r in con.execute(f"SELECT {', '.join(kol)} FROM h5_historikk_2010_2026 ORDER BY ar")]
    assert [r["ar"] for r in rader] == list(range(2010, 2027))
    for r in rader:
        a = r["ar"]

        def s(konto: str) -> int:
            return sum(belop(regnskap, f"{a}-{i:02d}", konto) for i in range(1, 13))

        kost = sum(s(k) for k in KONTOER if k[0] in "4567")
        assert r["kostnader_tkr"] == _tkr(kost), a
        assert r["billettinntekter_tkr"] == _tkr(s("3000")), a
        assert r["kafeinntekter_tkr"] == _tkr(s("3100")), a
        assert r["tilskudd_tkr"] == int(h5_kilde[a]["tilskudd_tkr"]) == _tkr(s("3400")), a
        assert r["andre_inntekter_tkr"] == int(h5_kilde[a]["andre_inntekter_tkr"]) == _tkr(s("3900")), a
        assert r["inntekter_totalt_tkr"] == r["billettinntekter_tkr"] + r["tilskudd_tkr"] + r["kafeinntekter_tkr"] + r["andre_inntekter_tkr"]
        assert r["resultat_tkr"] == r["inntekter_totalt_tkr"] - r["kostnader_tkr"], a
        assert r["besok_totalt"] == besok[a], a
        assert r["ansatte_arsverk"] == round(vakttimer[a] / 1700, 1), a
        assert r["tema"] == h5_kilde[a]["tema"] and r["skoleelever"] == int(h5_kilde[a]["skoleelever"]), a  # resten beholdes


# ---------- Lesing ----------


def test_query_driftsregnskap_gir_summer_for_aaret(bygget: Path, regnskap) -> None:
    svar = db.query_driftsregnskap(aar=2026, db_path=bygget)
    inn = sum(b for (m, k), b in regnskap.items() if m.startswith("2026") and k[0] == "3")
    kost = sum(b for (m, k), b in regnskap.items() if m.startswith("2026") and k[0] != "3")
    assert svar["sum_inntekter_nok"] == inn and svar["sum_kostnader_nok"] == kost
    assert svar["resultat_nok"] == inn - kost
    assert {k["konto"] for k in svar["per_konto"]} == KONTOER
    assert svar["datakilde"].startswith("syntetisk")


def test_query_driftsregnskap_filtrerer_paa_maaned_og_konto(bygget: Path, regnskap) -> None:
    svar = db.query_driftsregnskap(maaned="2026-06", konto="5000", db_path=bygget)
    assert svar["rader"] == [{"maaned": "2026-06", "konto": "5000", "kontonavn": "Lønn", "belop_nok": regnskap[("2026-06", "5000")]}]
    assert svar["sum_kostnader_nok"] == regnskap[("2026-06", "5000")] and svar["sum_inntekter_nok"] == 0


@pytest.mark.parametrize("args", [{"konto": "9999"}, {"maaned": "2026-13"}, {"aar": 1999}, {"konto": "5000' OR 1=1 --"}])
def test_query_driftsregnskap_avviser_ugyldige_filtre(bygget: Path, args: dict) -> None:
    with pytest.raises(ValueError):
        db.query_driftsregnskap(db_path=bygget, **args)


def test_query_driftsregnskap_sier_mangler_uten_tabell(tmp_path: Path) -> None:
    tom = tmp_path / "tom.db"
    sqlite3.connect(tom).close()
    assert "mangler" in db.query_driftsregnskap(aar=2026, db_path=tom)


def test_mcp_get_operating_accounts_2026(bygget: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.kunstpixel.core import mcp_server

    monkeypatch.setenv("KUNSTPIXEL_DB_PATH", str(bygget))
    svar = mcp_server.get_operating_accounts(aar=2026)
    assert {"sum_inntekter_nok", "sum_kostnader_nok", "resultat_nok"} <= set(svar)
    assert svar["resultat_nok"] == svar["sum_inntekter_nok"] - svar["sum_kostnader_nok"]


def test_get_operating_accounts_er_ikke_i_datafinner() -> None:
    from src.kunstpixel.adapters import datafinner

    assert "get_operating_accounts" not in datafinner.VERKTOY
