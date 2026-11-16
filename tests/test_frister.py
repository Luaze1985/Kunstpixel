"""Etappe 3a i spec datafinner-ledelse: «Mine frister» (B6 rene regler, B8 verktøy, B10 hviteliste).

Reglene (DECISIONS F1–F5): sykefravær uke 4/7 fra første fraværsdag, rapportfrist siste dag i måneden,
åpne saker over 14 dager, tilstandskontroll + 12 måneder, innlån ved utstillingens slutt.
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from src.kunstpixel.core import frister, ledelse

IDAG = date(2026, 11, 16)  # mandag


# ---------- B6: grupper ----------

@pytest.mark.parametrize("frist,gruppe", [
    (date(2026, 11, 15), "Forfalt"),
    (date(2026, 11, 16), "I dag"),
    (date(2026, 11, 17), "Denne uka"),
    (date(2026, 11, 22), "Denne uka"),   # søndag
    (date(2026, 11, 23), "Senere"),      # mandag neste uke
    (date(2027, 1, 15), "Senere"),       # 60 dager er med
    (date(2027, 1, 16), None),           # for langt fram
])
def test_gruppe_etter_frist(frist: date, gruppe: str | None) -> None:
    assert ledelse.frist_gruppe(frist, IDAG) == gruppe


def test_beregn_frister_sorterer_og_tar_bort_for_langt_fram() -> None:
    kandidater = [
        {"type": "rapport", "ref": "RP-1", "frist_dato": "2026-11-30"},
        {"type": "innlan", "ref": "LAN-1", "frist_dato": "2026-03-01"},
        {"type": "rapport", "ref": "RP-2", "frist_dato": "2027-06-30"},
    ]
    ut = ledelse.beregn_frister(kandidater, IDAG)
    assert [f["ref"] for f in ut] == ["LAN-1", "RP-1"]
    assert ut[0]["gruppe"] == "Forfalt" and ut[0]["dager_til"] == -260
    assert ut[1]["gruppe"] == "Senere" and ut[1]["dager_til"] == 14
    assert ut[0]["id"] == "innlan:LAN-1:2026-03-01"


# ---------- B7: reglene ----------

def test_sykefravaer_uke_4_og_7_fra_forste_fravaersdag() -> None:
    assert ledelse.sykefravaer_frister("2026-10-01", "2026-12-31", IDAG) == [
        ("sykefravaer_uke4", date(2026, 10, 29)), ("sykefravaer_uke7", date(2026, 11, 19))]


def test_sykefravaer_bare_frister_fravaeret_naar() -> None:
    # Varer til 2026-11-05: uke 4 (2026-10-29) er med, uke 7 (2026-11-19) ikke. Men fraværet er over, så ingenting vises.
    assert ledelse.sykefravaer_frister("2026-10-01", "2026-11-05", IDAG) == []
    # Pågår, men varer bare til 2026-11-20: uke 4 er nådd, uke 7 ikke.
    assert ledelse.sykefravaer_frister("2026-10-15", "2026-11-20", IDAG) == [("sykefravaer_uke4", date(2026, 11, 12))]


@pytest.mark.parametrize("maned,frist", [
    ("Månedlig", date(2026, 11, 30)),
    ("Kvartalsvis", date(2026, 12, 31)),
    ("November", date(2026, 11, 30)),
    ("Desember", date(2026, 12, 31)),
    ("Mars", date(2027, 3, 31)),    # mars er over i år, neste gang
    ("Løpende", None),
    ("noe rart", None),
])
def test_rapportfrist_er_siste_dag_i_maaneden(maned: str, frist: date | None) -> None:
    assert ledelse.rapport_frist(maned, IDAG) == frist


def test_reglene_ligger_ett_sted() -> None:
    assert ledelse.FRISTREGLER == {
        "sykefravaer_uker": (4, 7), "aapen_sak_dager": 14, "aapen_sak_maks_alder_dager": 365,
        "tilstand_maaneder": 12, "horisont_dager": 60,
    }


# ---------- B8: get_my_deadlines ----------

@pytest.fixture()
def idag(monkeypatch: pytest.MonkeyPatch) -> date:
    monkeypatch.setattr(frister, "_idag", lambda: IDAG)
    return IDAG


def test_samlingsforvalter_ser_forfalte_innlan(idag: date) -> None:
    d = frister.get_my_deadlines("Samlingsforvalter", "2026-11-16")
    innlan = [f for f in d["frister"] if f["type"] == "innlan"]
    assert {f["ref"] for f in innlan} == {"LAN-2026-016", "LAN-2026-033", "LAN-2026-050"}
    assert all(f["gruppe"] == "Forfalt" and f["frist_dato"] == "2026-03-01" for f in innlan)


def test_direktor_ser_innlan_men_ikke_tilstandskontroll(idag: date) -> None:
    typer = {f["type"] for f in frister.get_my_deadlines("Museumsdirektør", "2026-11-16")["frister"]}
    assert "innlan" in typer and "tilstandskontroll" not in typer


def test_driftsmeldinger_for_mottakerrollen_og_eldre_telles(idag: date) -> None:
    d = frister.get_my_deadlines("Driftsansvarlig", "2026-11-16")
    meld = [f for f in d["frister"] if f["type"] == "driftsmelding"]
    assert meld and all(f["gruppe"] in ("Forfalt", "I dag") for f in meld)  # åpen i 14 dager eller mer
    assert {"MELD-2026-0309", "MELD-2026-0472"} <= {f["ref"] for f in meld}
    assert "MELD-2026-0503" not in {f["ref"] for f in meld}  # formidler, ikke drift
    assert d["eldre_saker"] >= 1


def test_rapportfrister_for_eieren(idag: date) -> None:
    d = frister.get_my_deadlines("Driftsansvarlig", "2026-11-16")
    rapporter = [f for f in d["frister"] if f["type"] == "rapport"]
    assert rapporter and all(f["frist_dato"] >= "2026-11-16" for f in rapporter)
    assert any(f["ref"] == "RP-01" and f["frist_dato"] == "2026-11-30" for f in rapporter)


def test_antall_per_gruppe(idag: date) -> None:
    d = frister.get_my_deadlines("Driftsansvarlig", "2026-11-16")
    assert sum(d["antall"].values()) == len(d["frister"])
    assert set(d["antall"]) == {"Forfalt", "I dag", "Denne uka", "Senere"}


def test_frister_lekker_ikke_fravaerstype_eller_emne(idag: date) -> None:
    for rolle in ("HR og bemanning", "Avdelingsleder", "Driftsansvarlig", "Museumsdirektør", "Samlingsforvalter"):
        tekst = json.dumps(frister.get_my_deadlines(rolle, "2026-11-16"), ensure_ascii=False)
        for ord_ in ("sykemelding", "egenmelding", "permisjon", "emne", "meldingstekst", "diagnose"):
            assert ord_ not in tekst, f"{rolle}: {ord_}"


def test_sykefravaer_gir_navn_bare_til_hr_og_avdelingsleder(idag: date, monkeypatch: pytest.MonkeyPatch) -> None:
    rad = {"ansatt_id": "KP-ANS-999", "navn": "Test Testesen", "fra": "2026-10-01", "til": "2026-12-31"}
    monkeypatch.setattr(frister, "_pagaende_sykefravaer", lambda con, idag: [rad])
    hr = frister.get_my_deadlines("HR og bemanning", "2026-11-16")["frister"]
    syke = [f for f in hr if f["type"].startswith("sykefravaer")]
    assert [f["tittel"] for f in syke] == ["Oppfølgingsplan (uke 4): Test Testesen", "Dialogmøte (uke 7): Test Testesen"]
    drift = frister.get_my_deadlines("Driftsansvarlig", "2026-11-16")["frister"]
    assert not [f for f in drift if f["type"].startswith("sykefravaer")]
    assert "Test Testesen" not in json.dumps(drift, ensure_ascii=False)


@pytest.mark.parametrize("rolle", ["", "Admin'; DROP TABLE x", "Ukjent rolle"])
def test_ukjent_rolle_avvises(idag: date, rolle: str) -> None:
    with pytest.raises(ValueError):
        frister.get_my_deadlines(rolle, "2026-11-16")


def test_fremtidig_dato_avvises(idag: date) -> None:
    with pytest.raises(ValueError, match="fremtiden"):
        frister.get_my_deadlines("Driftsansvarlig", "2026-11-17")


# ---------- hvitelisten (B8 og B10) ----------

def test_frister_og_b10_er_hvitelistet() -> None:
    from src.kunstpixel.adapters.datafinner import VERKTOY

    assert VERKTOY["get_my_deadlines"][1] == {"rolle", "dato"}
    assert VERKTOY["get_condition_report"][1] == {"artwork_id"}
    assert VERKTOY["search_loans"][1] == {"exhibition_id", "query", "limit"}
