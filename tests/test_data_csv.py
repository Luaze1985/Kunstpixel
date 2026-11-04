"""Vokter datafilene som bygges inn i museum.db.

En feil i en CSV (et komma uten anførselstegn, en manglende kolonne) blir ikke avvist av byggeskriptet:
feltene forskyves eller kuttes stille. Denne testen fanger det før noen bygger databasen.
Gjelder spesielt når datafilene redigeres av en språkmodell eller for hånd.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BYGGER = (ROOT / "src/kunstpixel/data/build_museum_db.py").read_text(encoding="utf-8")
# Alle CSV-filer byggeskriptet nevner, bortsett fra grunnlaget som ikke skal endres.
CSV_FILER = sorted(set(re.findall(r'"([a-z0-9_]+\.csv)"', BYGGER)))


def test_byggeskriptet_leser_minst_de_kjente_datafilene() -> None:
    assert {"rapport_regler.csv", "roller.csv", "arkiv_hr_fravaer.csv", "virke_tariff_tillegg.csv"} <= set(CSV_FILER)


@pytest.mark.parametrize("navn", CSV_FILER)
def test_alle_rader_har_like_mange_felt_som_overskriften(navn: str) -> None:
    sti = ROOT / "05_data" / navn
    assert sti.is_file(), f"{navn} er nevnt i build_museum_db.py men finnes ikke"
    with sti.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    antall = len(rader[0])
    feil = [(i, len(r)) for i, r in enumerate(rader[1:], start=2) if len(r) != antall]
    assert not feil, f"{navn}: forventet {antall} felt, men linje(r) {feil[:5]} har et annet antall. Komma i en tekst må stå i anførselstegn."


@pytest.mark.parametrize("navn", [n for n in CSV_FILER if n in {"rapport_regler.csv", "roller.csv"}])
def test_datakilde_er_merket_syntetisk_og_hel(navn: str) -> None:
    with (ROOT / "05_data" / navn).open(encoding="utf-8", newline="") as f:
        for rad in csv.DictReader(f):
            kilde = rad["datakilde"]
            assert kilde.startswith("syntetisk"), (navn, kilde)
            assert kilde.count("(") == kilde.count(")"), f"Avkortet datakilde i {navn}: {kilde}"
