"""Vokter publikumsdataene fra publikum_builder (anmeldelser, fornøydhet og kafésalg).

Sjekker at CSV-ene er det skriptet faktisk lager, at kaféomsetningen stemmer med årstallene,
og at persondata bare finnes som tydelig falske øvingsdata.
"""

from __future__ import annotations

import csv
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

import pytest

from src.kunstpixel.core import datapolicy
from src.kunstpixel.data import publikum_builder as pb

DATA = pb.DATA_DIR
FILER = ["kafe_meny.csv", "kafe_varesalg.csv", "besok_tilfredshet.csv", "anmeldelser.csv"]


def _les(navn: str) -> list[dict]:
    with (DATA / navn).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_csvene_er_akkurat_det_skriptet_lager(tmp_path: Path) -> None:
    pb.bygg(tmp_path)
    for navn in FILER:
        assert (tmp_path / navn).read_bytes() == (DATA / navn).read_bytes(), f"{navn} er endret for hånd eller utdatert"


@pytest.mark.parametrize("navn", FILER)
def test_alle_rader_er_merket_syntetisk(navn: str) -> None:
    assert all(datapolicy.normalize_classification(r["datakilde"]) == datapolicy.SYNTETISK for r in _les(navn))


def test_kafeomsetning_stemmer_med_aarstallene() -> None:
    _, maal, _ = pb.les_grunnlag()
    sum_aar: dict[int, float] = defaultdict(float)
    for r in _les("kafe_varesalg.csv"):
        sum_aar[int(r["dato"][:4])] += float(r["omsetning_nok"])
    for aar, m in maal.items():
        assert abs(sum_aar[aar] - m) / m < 0.01, (aar, sum_aar[aar], m)


def test_ingen_data_etter_sluttdatoen() -> None:
    for navn in ("kafe_varesalg.csv", "besok_tilfredshet.csv", "anmeldelser.csv"):
        assert max(r["dato"] for r in _les(navn)) <= pb.SISTE_DATO


def test_persondata_er_bare_falske_ovingsdata() -> None:
    telefon = re.compile(r"\b\d{3} ?\d{2} ?\d{3}\b|\b\d{8}\b")
    epost = re.compile(r"\S+@\S+")
    for r in _les("anmeldelser.csv"):
        assert not epost.search(r["tekst"])
        funn = [t for t in telefon.findall(r["tekst"]) if t.replace(" ", "") != "00000000"]
        assert not funn, (r["anmeldelse_id"], funn)
        if "000 00 000" in r["tekst"]:
            assert r["inneholder_persondata"] == "1"


def test_allergenpastander_kan_sjekkes_mot_menyen() -> None:
    meny = {r["produkt_id"]: set(filter(None, r["allergener"].split(";"))) for r in _les("kafe_meny.csv")}
    klager = [r for r in _les("anmeldelser.csv") if r["allergen_pastand"]]
    assert klager, "øvingsdataene skal ha allergenklager"
    for r in klager:
        stemmer = r["allergen_pastand"] in meny[r["produkt_id"]]
        assert r["allergen_stemmer_med_meny"] == ("1" if stemmer else "0")
        assert r["status"] == "eskalert"


def test_innebygde_sammenhenger_kan_finnes() -> None:
    anm = _les("anmeldelser.csv")
    per_utst: dict[str, list[int]] = defaultdict(list)
    for r in anm:
        if r["utstilling_id"]:
            per_utst[r["utstilling_id"]].append(int(r["stjerner"]))
    snitt = {u: sum(s) / len(s) for u, s in per_utst.items() if len(s) >= 20}
    assert min(snitt, key=snitt.get) == pb.SVAK_UTSTILLING

    def ubesvart_andel(rader: list[dict]) -> float:
        return sum(r["status"] == "ubesvart" for r in rader) / len(rader)

    neg = [r for r in anm if int(r["stjerner"]) <= 3 and not r["allergen_pastand"]]
    for_ = [r for r in neg if r["dato"] < pb.ETTERSLEP_FRA]
    etter = [r for r in neg if r["dato"] >= pb.ETTERSLEP_FRA]
    assert ubesvart_andel(etter) > ubesvart_andel(for_) + 0.2


def test_byggeskriptet_laster_tabellene(tmp_path: Path) -> None:
    from src.kunstpixel.data import build_museum_db as bygger

    db = tmp_path / "museum.db"
    bygger.bygg(db)
    con = sqlite3.connect(db)
    try:
        for tabell, csvfil in [("kafe_meny", "kafe_meny.csv"), ("anmeldelser", "anmeldelser.csv"),
                               ("kafe_varesalg", "kafe_varesalg.csv"), ("besok_tilfredshet", "besok_tilfredshet.csv")]:
            assert con.execute(f"SELECT count(*) FROM {tabell}").fetchone()[0] == len(_les(csvfil))
        assert con.execute("PRAGMA user_version").fetchone()[0] == bygger.SKJEMAVERSJON
    finally:
        con.close()


def test_ansvarlig_rolle_er_en_kjent_intern_rolle() -> None:
    """Ledelsens håndtering av anmeldelser skal peke på rollene i den interne assistenten og roller.csv."""
    from src.kunstpixel.core.intern.data import ROLLER, fold

    fra_roller_csv = {fold(r["navn"]) for r in csv.DictReader((DATA / "roller.csv").open(encoding="utf-8", newline=""))}
    brukt = {r["ansvarlig_rolle"] for r in _les("anmeldelser.csv")}
    assert brukt <= set(ROLLER), brukt - set(ROLLER)
    assert {fold(r) for r in brukt} <= fra_roller_csv
    assert {"kommunikasjon", "kafeansvarlig"} <= brukt
