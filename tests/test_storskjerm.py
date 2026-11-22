"""Tallene til storskjerm-dashbordet (spec docs/specs/2026-11-19-storskjerm-dashbord.md, DECISIONS D1–D8)."""

from __future__ import annotations

import json
from datetime import date

import pytest
from src.kunstpixel.core import (
    db,
    driftsoversikt,
    frister,
    storskjerm,
    storskjerm_roller,
)
from src.kunstpixel.core.storskjerm import lag_storskjerm

IDAG = date(2026, 11, 19)  # torsdag
MANDAG = date(2026, 11, 16)


def _las(monkeypatch: pytest.MonkeyPatch, dag: date) -> None:
    for modul in (driftsoversikt, frister, storskjerm, storskjerm_roller):
        monkeypatch.setattr(modul, "_idag", lambda: dag)


@pytest.fixture()
def idag(monkeypatch: pytest.MonkeyPatch) -> dict:
    _las(monkeypatch, IDAG)
    return lag_storskjerm(IDAG.isoformat())


@pytest.fixture()
def idag_mandag(monkeypatch: pytest.MonkeyPatch) -> dict:
    _las(monkeypatch, MANDAG)
    return lag_storskjerm(MANDAG.isoformat())


def _flate(data: dict, fid: str) -> dict:
    return next(f for f in data["flater"] if f["id"] == fid)


def _sql(sql: str, *args) -> list:
    with db.get_db_connection() as con:
        return con.execute(sql, args).fetchall()


def test_fire_flater_med_kilde(idag: dict) -> None:
    assert [f["id"] for f in idag["flater"]] == ["besok", "besok_uke", "saker", "tilfredshet"]
    assert all(f["kilde"] for f in idag["flater"])


def test_besok_er_lik_datafinner(idag: dict) -> None:
    assert _flate(idag, "besok")["verdi"] == driftsoversikt.get_today_overview("2026-11-19")["besok"]["verdi"]


def test_besok_sier_hvilken_dag(idag: dict) -> None:
    assert _flate(idag, "besok")["gjelder"] == driftsoversikt.get_today_overview("2026-11-19")["besok"]["dato"]


def test_tilfredshet_er_ukjent_naar_kilden_slutter(idag: dict) -> None:
    f = _flate(idag, "tilfredshet")
    mangler = _tilfredshet_slutter() < "2026-11-18"
    assert (f["status"] == "Ukjent" and f["verdi"] is None) == mangler


def test_tilfredshet_uten_tall_blir_ukjent_aldri_tall() -> None:
    """Fast vern (I3/D5) med kunstige data: en kilde som ikke dekker perioden vises som Ukjent, ikke som tall."""
    tom = {"verdi": None, "normalt": None, "status": None, "dato": "2026-11-18", "kilde": "x"}
    i_dag = {"besok": tom, "dato": "2026-11-19", "driftsmeldinger": {"verdi": 0}, "hms_avvik": {"verdi": 0},
             "driftsmeldinger_eldre": {"verdi": 0}}
    uke = {"besok": tom, "viser_forrige_uke": False, "fra": "2026-11-16", "til": "2026-11-19",
           "tilfredshet": {"verdi": None, "kilde": "besok_tilfredshet"}}
    f = next(x for x in storskjerm._flater(i_dag, uke, "2026-11-18") if x["id"] == "tilfredshet")
    assert f["status"] == "Ukjent" and f["verdi"] is None and "dekker ikke" in f["sammenligning"]


def test_mandag_viser_forrige_uke(idag_mandag: dict) -> None:
    assert "forrige uke" in _flate(idag_mandag, "besok_uke")["navn"].lower()


def test_ingen_navn_i_data(idag: dict) -> None:
    tekst = json.dumps(idag, ensure_ascii=False)
    navn = [r[0] for r in _sql("SELECT navn FROM hr_ansatte")]
    assert navn and not [n for n in navn if n in tekst]


def test_ingen_epost(idag: dict) -> None:
    assert all("epost" not in r for r in idag["frister"]["rader"])


def test_innlansfrister_vises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lars 2026-11-22: regelen for retur av innlån er godkjent, så innlånsfristene skjules ikke lenger (U6 opphevet)."""
    falsk = [
        {"type": "innlan", "ref": "LAN-1", "tittel": "Retur av innlån: X (Y)", "frist_dato": "2026-03-01",
         "gruppe": "Forfalt", "kilde": "utstillingsinnlan", "epost": {"overskrift": "o"}},
        {"type": "rapport", "ref": "RP-1", "tittel": "Rapport", "frist_dato": "2026-11-30",
         "gruppe": "Senere", "kilde": "h5_rapporteringskalender", "epost": {"overskrift": "o"}},
    ]
    monkeypatch.setattr(frister, "get_my_deadlines", lambda rolle, dato: {"frister": falsk})
    ut = storskjerm._frister("2026-11-19")
    assert [r["ref"] for r in ut["rader"]] == ["LAN-1", "RP-1"]
    assert ut["skjult"] == 0 and ut["antall"]["Forfalt"] == 1
    assert all("epost" not in r for r in ut["rader"])


def test_besok_uker_er_8_og_lik_sql(idag: dict) -> None:
    uker = idag["besok_uker"]
    assert len(uker) == 8
    siste = uker[-1]
    # Bare hele uker: uka som pågår står i flaten «Besøk denne uka».
    assert (siste["fra"], siste["til"]) == ("2026-11-09", "2026-11-15")
    assert siste["i_aar"] == _sql("SELECT sum(besok_totalt) FROM dagsbesok WHERE dato BETWEEN '2026-11-09' AND '2026-11-15'")[0][0]
    assert uker[0]["fra"] == "2026-09-21"


def test_utstillinger_i_aar(idag: dict) -> None:
    u = {x["utstilling_id"]: x for x in idag["utstillinger"]}
    assert len(u) == 6
    assert u["KP-EXH-2026-FOKUS-2"]["netto_resultat_nok"] == 657556
    assert idag["utstillinger"][0]["utstilling_id"] == "KP-EXH-2026-067"  # størst resultat først


def _tilfredshet_slutter() -> str:
    """Siste dato i besok_tilfredshet i museum.db. R5 forlenget serien, så testene følger dataene."""
    return db.execute_read_query("SELECT max(dato) AS m FROM besok_tilfredshet")[0]["m"]


def test_hull_finner_tilfredshet_og_utstillingstabeller(idag: dict) -> None:
    tekst = " ".join(h["tekst"] for h in idag["hull"])
    slutt = _tilfredshet_slutter()
    assert (slutt in tekst) == (slutt < "2026-11-18")  # hull bare når serien slutter før i går
    assert "utstillinger" in tekst
    assert all(h["kilde"] for h in idag["hull"])


def test_oppmerksomhet_teller_status_og_forfalt(idag: dict) -> None:
    status = sum(f["status"] in ("Følg med", "Over terskel") for f in idag["flater"])
    assert idag["oppmerksomhet"] == status + idag["frister"]["antall"]["Forfalt"]


def test_fremtidig_dato_avvises(monkeypatch: pytest.MonkeyPatch) -> None:
    _las(monkeypatch, IDAG)
    with pytest.raises(ValueError):
        lag_storskjerm("2026-11-20")


def test_uka_gjelder_bare_til_i_gaar(idag: dict) -> None:
    assert _flate(idag, "besok_uke")["gjelder"] == "2026-11-16–2026-11-18"


def test_sammenligning_har_norske_heltall(idag: dict) -> None:
    tekster = " ".join(f["sammenligning"] for f in idag["flater"])
    assert ".0" not in tekster


# --- Task 2: byggeskriptet ---------------------------------------------------------------------------------

def _bygg_modul():
    import importlib.util
    from pathlib import Path
    sti = Path(__file__).resolve().parents[1] / "scripts" / "lag_storskjerm.py"
    spec = importlib.util.spec_from_file_location("lag_storskjerm", sti)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_bygg_skriver_side_og_data(tmp_path, idag: dict) -> None:
    side, data = _bygg_modul().bygg(tmp_path, "2026-11-19")
    assert side.name == "storskjerm.html" and data.name == "data.json"
    assert json.loads(data.read_text("utf-8"))["dato"] == "2026-11-19"


def test_af_css_er_lagt_inn(tmp_path, idag: dict) -> None:
    tekst = _bygg_modul().bygg(tmp_path, "2026-11-19")[0].read_text("utf-8")
    assert "/*AF_CSS*/" not in tekst and "--blue:" in tekst


def test_siden_henter_ingen_eksterne_filer(tmp_path, idag: dict) -> None:
    import re
    tekst = _bygg_modul().bygg(tmp_path, "2026-11-19")[0].read_text("utf-8")
    assert not re.search(r'(src|href)="https?://(?!fonts\.googleapis\.com)', tekst)


def test_hull_har_tabell_og_sluttdato(idag: dict) -> None:
    slutter = [h for h in idag["hull"] if h["type"] == "slutter"]
    slutt = _tilfredshet_slutter()
    assert {h["tabell"]: h["slutter"] for h in slutter}.get("besok_tilfredshet") == (slutt if slutt < "2026-11-18" else None)
    assert [h for h in idag["hull"] if h["type"] == "uenige"]
