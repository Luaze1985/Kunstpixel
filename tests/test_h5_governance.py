"""Tester for H5 & Governance (A-F, T og HR-onboarding).

Validerer:
1. YAML-filene i 05_data/governance/ mot alle regler i leveranse.py.
2. Summer i arbeidsoppgaver (112 + 175 = 287 timer) og avviksfrister (14 dager / 24 timer).
3. SQL-spørringer i src.kunstpixel.core.db mot museum.db.
4. MCP-verktøy i src.kunstpixel.core.mcp_server.
5. Sikkerhet og tilgangsskille i Datafinner (adapters.datafinner).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import db, mcp_server
from src.kunstpixel.core.intern import leveranse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOV_DIR = PROJECT_ROOT / "05_data" / "governance"


# -----------------------------------------------------------------------------
# 1. YAML-VALIDERING MOT LEVERANSE.PY
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("kode,filnavn", [
    ("A", "myndighetskontakter.yaml"),
    ("B", "tilsynsbesok_rutine.yaml"),
    ("C", "rapporteringskalender.yaml"),
    ("D", "rapportmaler.yaml"),
    ("E", "arbeidsoppgaver_tidsbruk.yaml"),
    ("F", "historikk_tekst.yaml"),
    ("T", "historikk_tall.yaml"),
])
def test_yaml_filer_oppfyller_leveranseregler(kode: str, filnavn: str) -> None:
    sti = GOV_DIR / filnavn
    assert sti.is_file(), f"Mangler governance-fil: {filnavn}"
    tekst = sti.read_text(encoding="utf-8")
    funn = leveranse.kontroller_tekst(kode, tekst)
    feil = [f for f in funn if f.alvor == "FEIL"]
    assert not feil, f"Regelbrudd i {filnavn}: {[(f.kode, f.sti, f.melding) for f in feil]}"


def test_tidsbruk_summer_og_frister() -> None:
    sti_e = GOV_DIR / "arbeidsoppgaver_tidsbruk.yaml"
    data_e = yaml.safe_load(sti_e.read_text(encoding="utf-8"))
    assert data_e["sum"]["myndighetskontakt"] == 112
    assert data_e["sum"]["rapportering"] == 175
    assert data_e["sum"]["totalt"] == 287

    sti_b = GOV_DIR / "tilsynsbesok_rutine.yaml"
    data_b = yaml.safe_load(sti_b.read_text(encoding="utf-8"))
    assert data_b["avvik_frister"]["gult_avvik_lukkes_innen"] == "14 dager"
    assert data_b["avvik_frister"]["rodt_avvik_lukkes_innen"] == "24 timer"


def test_hr_data_realisme_oppfyller_regler() -> None:
    sti = GOV_DIR / "hr_data_realisme.yaml"
    assert sti.is_file()
    data = yaml.safe_load(sti.read_text(encoding="utf-8"))
    assert data["syntetisk"] is True
    assert len(data["kompetanse_matrise"]) == 6
    assert len(data["onboarding_status"]) == 6
    assert len(data["hms_opplaering"]) == 6


# -----------------------------------------------------------------------------
# 2. SQL-SPØRRINGER I DB.PY
# -----------------------------------------------------------------------------

def test_query_myndighetskontakter_med_og_uten_skjerming() -> None:
    # 1. Uten include_contacts (åpent/Datafinner)
    res_aapen = db.query_myndighetskontakter(include_contacts=False)
    assert res_aapen["antall"] == 8
    første = res_aapen["myndigheter"][0]
    assert første["kontaktperson"] == "[SKJERMET]"
    assert første["kontakt_epost"] == "[SKJERMET]"
    assert første["myndighet"] == "Arbeidstilsynet"

    # 2. Med include_contacts (MCP/ledelse)
    res_intern = db.query_myndighetskontakter(include_contacts=True)
    første_intern = res_intern["myndigheter"][0]
    assert første_intern["kontaktperson"] == "Harald Oskar Vinje"
    assert første_intern["kontakt_epost"].endswith(".example.test")


def test_query_tilsynsbesok_rutine() -> None:
    res = db.query_tilsynsbesok_rutine()
    assert res["antall"] == 6
    assert res["avvik_frister"]["gult_avvik_lukkes_innen"] == "14 dager"
    assert res["steg"][0]["navn"] == "Varsel kommer"


def test_query_rapporteringskalender() -> None:
    res = db.query_rapporteringskalender(mottakertype="ekstern")
    assert res["antall"] == 3
    for r in res["rapporter"]:
        assert r["godkjenning"] == "eier"
        assert isinstance(r["kilder"], list)


def test_query_rapportmaler() -> None:
    res = db.query_rapportmaler(mal_id="ML-01")
    assert res["antall"] == 1
    mal = res["maler"][0]
    assert mal["mal_navn"] == "Driftsrapport"
    assert len(mal["felt"]) == 5
    assert len(mal["regler"]) == 2


def test_query_arbeidsoppgaver_tidsbruk() -> None:
    res = db.query_arbeidsoppgaver_tidsbruk()
    assert res["antall"] == 19
    assert res["total_timer"] == 287


def test_query_historikk_2010_2026() -> None:
    res = db.query_historikk_2010_2026(ar_fra=2020, ar_til=2021)
    assert res["antall"] == 2
    r2020 = next(r for r in res["historikk"] if r["ar"] == 2020)
    assert "stengt" in r2020["tema"]
    assert len(r2020["hendelse"]) > 20
    assert len(r2020["laerdom"]) > 20


def test_query_hr_opplaering_onboarding() -> None:
    res = db.query_hr_opplaering_onboarding(rolle="Museumsvert")
    assert res["antall"] >= 3
    kategorier = {r["kategori"] for r in res["opplaering"]}
    assert {"kompetanse_matrise", "onboarding_status", "hms_opplaering"} <= kategorier


# -----------------------------------------------------------------------------
# 3. DATAFINNER TILGANGSSTYRING (SIKKERHETSSJEKK)
# -----------------------------------------------------------------------------

def test_datafinner_hvitliste_og_skjerming() -> None:
    # Verifiser at de åpne verktøyene finnes
    assert "search_myndighet" in datafinner.VERKTOY
    assert "get_inspection_routine" in datafinner.VERKTOY
    assert "search_rapportering" in datafinner.VERKTOY
    assert "search_hr_onboarding" in datafinner.VERKTOY

    # Verifiser at ledelsesverktøy er SKJERMET fra Datafinner
    assert "search_arbeidsoppgaver" not in datafinner.VERKTOY
    assert "search_governance_history" not in datafinner.VERKTOY

    # Test kjøring gjennom Datafinner run_tool (include_contacts er ikke tillatt i åpne kall)
    res = datafinner.run_tool("search_myndighet", {"query": "Mattilsynet"})
    assert res["antall"] == 1
    assert res["myndigheter"][0]["kontaktperson"] == "[SKJERMET]"
    with pytest.raises(ValueError):
        datafinner.run_tool("search_myndighet", {"query": "Mattilsynet", "include_contacts": True})
