"""Vokter publikumsdataene fra publikum_builder (anmeldelser, fornøydhet og kafésalg).

Sjekker at CSV-ene er det skriptet faktisk lager, at kaféomsetningen stemmer med årstallene,
og at persondata bare finnes som tydelig falske øvingsdata.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
import sqlite3
import subprocess
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
    """Første leveranse (til og med ORIGINAL_SLUTT) treffer årstallene. Forlengelsen er ikke med her."""
    _, maal, _ = pb.les_grunnlag(pb.ORIGINAL_SLUTT)
    sum_aar: dict[int, float] = defaultdict(float)
    for r in _les("kafe_varesalg.csv"):
        if r["dato"] <= pb.ORIGINAL_SLUTT:
            sum_aar[int(r["dato"][:4])] += float(r["omsetning_nok"])
    for aar, m in maal.items():
        assert abs(sum_aar[aar] - m) / m < 0.01, (aar, sum_aar[aar], m)


def test_kafe_i_forlengelsen_har_samme_kroner_per_besok() -> None:
    """November–desember 2026 skal ha samme kafékroner per besøk som januar–oktober (±10 %),
    og hele 2026 skal ligge nær kafeinntekter_tkr i h5-kilden (innen 5 %). I bygget regnes kafeinntekter_tkr
    fra kafésalget (Lars 2026-11-22), så målet leses fra kilden, ikke fra museum.db."""
    con = sqlite3.connect(f"file:{pb.DB.as_posix()}?mode=ro", uri=True)
    try:
        besok = dict(con.execute("SELECT dato, besok_totalt FROM dagsbesok WHERE aar = 2026 AND er_aapent = 1"))
    finally:
        con.close()
    aarstall = pb.kafe_maal_per_aar()[2026]
    salg: dict[str, float] = defaultdict(float)
    for r in _les("kafe_varesalg.csv"):
        if r["dato"].startswith("2026"):
            salg[r["dato"]] += float(r["omsetning_nok"])

    def kr_per_besok(dager: list[str]) -> float:
        return sum(salg[d] for d in dager) / sum(besok[d] for d in dager)

    for_ = kr_per_besok([d for d in salg if d <= pb.ORIGINAL_SLUTT])
    etter = kr_per_besok([d for d in salg if d > pb.ORIGINAL_SLUTT])
    assert abs(etter / for_ - 1) < 0.10, (for_, etter)
    assert abs(sum(salg.values()) / aarstall - 1) < 0.05, (sum(salg.values()), aarstall)


def test_ingen_data_etter_sluttdatoen() -> None:
    for navn in ("kafe_varesalg.csv", "besok_tilfredshet.csv", "anmeldelser.csv"):
        assert max(r["dato"] for r in _les(navn)) <= pb.SISTE_DATO


SERIER = ["kafe_varesalg.csv", "besok_tilfredshet.csv", "anmeldelser.csv"]


@pytest.mark.parametrize("navn", SERIER)
def test_seriene_gaar_til_31_desember(navn: str) -> None:
    """Samme sluttdato som dagsbesok, hr_vakter og hr_fravaer (R5)."""
    assert max(r["dato"] for r in _les(navn)) == "2026-12-31"


@pytest.mark.parametrize("navn", FILER)
def test_radene_til_og_med_29_oktober_er_uendret(navn: str) -> None:
    """Forlengelsen legges etter de gamle radene. Fasit er filen slik den var i commit fc9452d."""
    gammel = subprocess.run(["git", "show", f"fc9452d:05_data/{navn}"], cwd=pb.PROJECT_ROOT,
                            capture_output=True, check=True).stdout
    ny = (DATA / navn).read_bytes()
    assert ny[: len(gammel)] == gammel, f"{navn}: gamle rader er endret"
    if navn != "kafe_meny.csv":
        assert all(r["dato"] > pb.ORIGINAL_SLUTT for r in csv.DictReader(io.StringIO(ny[len(gammel):].decode("utf-8"),
                   newline=""), fieldnames=list(_les(navn)[0])))


@pytest.mark.parametrize("navn", SERIER)
def test_ingen_rader_paa_stengte_dager(navn: str) -> None:
    con = sqlite3.connect(f"file:{pb.DB.as_posix()}?mode=ro", uri=True)
    try:
        aapne = {d for (d,) in con.execute("SELECT dato FROM dagsbesok WHERE er_aapent = 1")}
    finally:
        con.close()
    stengt = sorted({r["dato"] for r in _les(navn)} - aapne)
    assert not stengt, stengt[:10]


def test_anmeldelser_peker_paa_utstilling_som_pagaar() -> None:
    con = sqlite3.connect(f"file:{pb.DB.as_posix()}?mode=ro", uri=True)
    try:
        periode = {i: (s, e) for i, s, e in con.execute(
            "SELECT utstilling_id, periode_start, periode_slutt FROM utstillinger_historikk")}
    finally:
        con.close()
    feil = [(r["anmeldelse_id"], r["dato"], r["utstilling_id"]) for r in _les("anmeldelser.csv")
            if r["utstilling_id"] and not (periode[r["utstilling_id"]][0] <= r["dato"] <= periode[r["utstilling_id"]][1])]
    assert not feil, feil[:10]


def test_anmeldelse_id_er_unike_og_fortlopende() -> None:
    ider = [r["anmeldelse_id"] for r in _les("anmeldelser.csv")]
    assert ider == [f"ANM-{n:05d}" for n in range(1, len(ider) + 1)]


def test_to_kjoringer_gir_like_filer(tmp_path: Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    pb.bygg(a)
    pb.bygg(b)
    for navn in FILER:
        assert hashlib.sha256((a / navn).read_bytes()).digest() == hashlib.sha256((b / navn).read_bytes()).digest(), navn


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
