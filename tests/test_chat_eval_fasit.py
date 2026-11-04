"""Vokter eval-settet for chatten uten KI: formatet stemmer, og fasiten finnes i dataene.

Kjører hvert «fasit»-steg i 04_knowledge/07_arena/chat_eval.yaml gjennom Datafinners hviteliste og krever at
hvert «forventet»-punkt står i verktøysvaret. Glir dataene etter en ombygging, feiler denne testen før evalen
gir misvisende poeng.
"""

from __future__ import annotations

import json

import pytest

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import chat_eval

DATA = chat_eval.last()
OPPGAVER = DATA["oppgaver"]


def test_formatet_er_gyldig() -> None:
    ider = [o["id"] for o in OPPGAVER]
    assert len(ider) == len(set(ider)), "id-ene må være unike"
    assert 20 <= len(OPPGAVER) <= 50
    for o in OPPGAVER:
        assert o["kategori"] in chat_eval.KATEGORIER, o["id"]
        assert o["turer"] and all(isinstance(t, str) and t.strip() for t in o["turer"]), o["id"]
        navn = [s["verktoy"] for s in o["fasit"]] + [a["verktoy"] for a in o["args_krav"]]
        navn += [v for sett in o["verktoy_krav"] for v in sett]
        for v in navn:
            assert v in datafinner.VERKTOY, f"{o['id']}: {v} er ikke på hvitelisten"
        assert o["tallkontroll"] in ("ok", "ignorer"), o["id"]
        if o["kategori"] != "observasjon":
            assert o["forventet"] or o["utregnet"] or o["forbudt"], f"{o['id']} har ingenting å sjekke"


@pytest.mark.parametrize("oppgave", [o for o in OPPGAVER if o["fasit"]], ids=lambda o: o["id"])
def test_fasiten_finnes_i_dataene(oppgave: dict) -> None:
    svar = json.dumps([datafinner.run_tool(s["verktoy"], s.get("args", {})) for s in oppgave["fasit"]],
                      ensure_ascii=False, default=str)
    mangler = [p for p in oppgave["forventet"] if not chat_eval.finnes(p, svar)]
    assert not mangler, f"{oppgave['id']}: står ikke i verktøysvaret: {mangler}"


@pytest.mark.parametrize("oppgave", [o for o in OPPGAVER if o["utregnet"]], ids=lambda o: o["id"])
def test_utregningene_stemmer(oppgave: dict) -> None:
    for u in oppgave["utregnet"]:
        assert round(chat_eval.regn_ut(u["uttrykk"]), 2) == float(u["verdi"]), u


def test_observasjoner_peker_pa_grensecaser() -> None:
    obs = [o for o in OPPGAVER if o["kategori"] == "observasjon"]
    assert obs and all(o.get("fra_grense") and o["turer"][0] for o in obs)


def test_dato_i_dag_er_fast() -> None:
    from datetime import date
    assert date.fromisoformat(DATA["dato_i_dag"]).weekday() == 0, "K4 forutsetter at «i dag» er en mandag"


def test_hr_case_eval_krever_baade_funn_og_undersoekelse() -> None:
    """Fanger at en HR-eval kan bestås ved å svare fra hukommelsen uten å undersøke caset."""
    case = next(o for o in OPPGAVER if o["id"] == "H1")
    assert [s["verktoy"] for s in case["fasit"]] == ["discover_hr_cases", "investigate_hr_case"]
    assert ["discover_hr_cases", "investigate_hr_case"] in case["verktoy_krav"]
