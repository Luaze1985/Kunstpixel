"""Styringsfilene i 05_data/governance er generert av h5_governance_builder.py (revisjonsfunn 11).

Kilden er koden. En håndretting i en YAML-fil blir overskrevet ved neste generering,
så filene sier det selv øverst, og testen feiler hvis noen har rettet for hånd.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.kunstpixel.data.h5_governance_builder import (
    GENERERT_MERKE,
    GOV_DIR,
    eksporter_yaml_filer,
)

GENERERTE = [
    "myndighetskontakter.yaml",
    "tilsynsbesok_rutine.yaml",
    "rapporteringskalender.yaml",
    "rapportmaler.yaml",
    "arbeidsoppgaver_tidsbruk.yaml",
    "historikk_tekst.yaml",
    "historikk_tall.yaml",
    "hr_data_realisme.yaml",
]


@pytest.fixture(scope="module")
def nybygg(tmp_path_factory) -> Path:
    ut = tmp_path_factory.mktemp("governance")
    eksporter_yaml_filer(ut)
    return ut


def test_generatoren_skriver_akkurat_disse_filene(nybygg):
    assert sorted(p.name for p in nybygg.iterdir()) == sorted(GENERERTE)


@pytest.mark.parametrize("navn", GENERERTE)
def test_filen_sier_selv_at_den_er_generert(navn):
    forste = (GOV_DIR / navn).read_text(encoding="utf-8").splitlines()[0]
    assert forste == GENERERT_MERKE
    assert forste.startswith("# GENERERT av h5_governance_builder.py")


@pytest.mark.parametrize("navn", GENERERTE)
def test_lagret_fil_er_lik_det_generatoren_lager(navn, nybygg):
    lagret = (GOV_DIR / navn).read_bytes().replace(b"\r\n", b"\n")
    ny = (nybygg / navn).read_bytes().replace(b"\r\n", b"\n")
    assert lagret == ny, f"{navn} er rettet for hånd eller utdatert. Rett i h5_governance_builder.py og kjør den."
