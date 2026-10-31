"""Drift og bunnlinje: tallene skal henge sammen med hverandre og aldri gå ned på personnivå."""

from __future__ import annotations

import pytest

from src.kunstpixel.core import bunnlinje, db


def test_dagsoversikt_summerer_vakter_per_avdeling() -> None:
    d = bunnlinje.get_day_overview("2026-06-13")
    assert d["vakter"] == sum(a["vakter"] for a in d["avdelinger"])
    assert d["vakttimer"] == pytest.approx(sum(a["timer"] for a in d["avdelinger"]))
    assert d["besok_per_vakttime"] == round(d["besok_totalt"] / d["vakttimer"], 2)


def test_ukjent_dag_er_ikke_funnet_og_feil_format_avvises() -> None:
    assert bunnlinje.get_day_overview("1999-01-01")["funnet"] is False
    with pytest.raises(ValueError):
        bunnlinje.get_day_overview("13.06.2026")


def test_periodens_differanse_er_inntekt_minus_vaktkostnad() -> None:
    r = bunnlinje.get_period_result("2026-06")
    assert r["differanse_nok"] == pytest.approx(r["billettinntekt_nok"] - r["vaktkostnad_nok"])
    assert r["vaktkostnad_nok"] == db.query_shift_cost("2026-06")["kostnad_nok_totalt"]
    assert "ikke driftsresultatet" in r["merknad"]


@pytest.mark.parametrize("maaned", ["2026-13", "2026-6", "juni"])
def test_ugyldig_maaned_avvises(maaned: str) -> None:
    with pytest.raises(ValueError):
        bunnlinje.get_period_result(maaned)
    with pytest.raises(ValueError):
        bunnlinje.get_team_efficiency(maaned)


def test_ingen_verktoy_gir_tall_per_ansatt() -> None:
    svar = [bunnlinje.get_day_overview("2026-06-13"), bunnlinje.get_team_efficiency("2026-06"),
            bunnlinje.get_period_result("2026-06"), bunnlinje.get_exhibition_ranking(2022)]
    tekst = str(svar).lower()
    assert "ansatt_id" not in tekst and "kp-ans" not in tekst


def test_rangeringen_er_sortert_og_begrenset() -> None:
    r = bunnlinje.get_exhibition_ranking(2022, limit=2)
    best = [x["netto_resultat_nok"] for x in r["best"]]
    svakest = [x["netto_resultat_nok"] for x in r["svakest"]]
    assert best == sorted(best, reverse=True) and len(best) == len(svakest) == 2
    assert min(best) >= max(svakest)


def test_resultatutviklingen_har_bare_okonomiske_kolonner() -> None:
    r = bunnlinje.get_result_trend(2018, 2022)
    assert [x["aar"] for x in r["aar"]] == [2018, 2019, 2020, 2021, 2022]
    assert set(r["aar"][0]) == {"aar", "besok_totalt", "billettinntekter_tkr", "kafeinntekter_tkr",
                                "inntekter_totalt_tkr", "kostnader_tkr", "resultat_tkr"}
    with pytest.raises(ValueError):
        bunnlinje.get_result_trend(2022, 2018)
