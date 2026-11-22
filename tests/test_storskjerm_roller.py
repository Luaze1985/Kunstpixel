"""Rollevisningene på storskjermen (DECISIONS SC14–SC20). Tallene sjekkes mot egne SQL-spørringer."""

from __future__ import annotations

import json
from datetime import date, timedelta

import pytest
from src.kunstpixel.core import (
    db,
    driftsoversikt,
    frister,
    storskjerm,
    storskjerm_roller,
)
from src.kunstpixel.core.storskjerm_roller import lag_roller

IDAG = date(2026, 11, 19)  # torsdag
ROLLER = ["direktor", "drift", "hr", "okonomi", "publikum", "samling"]


@pytest.fixture(scope="module")
def roller() -> dict:
    mp = pytest.MonkeyPatch()
    for modul in (driftsoversikt, frister, storskjerm, storskjerm_roller):
        mp.setattr(modul, "_idag", lambda: IDAG)
    try:
        yield {r["id"]: r for r in lag_roller(IDAG.isoformat())}
    finally:
        mp.undo()


def _sql(sql: str, *args):
    with db.get_db_connection() as con:
        return con.execute(sql, args).fetchone()[0]


def _flis(rolle: dict, fid: str) -> dict:
    return next(f for f in rolle["fliser"] if f["id"] == fid)


SISTE_SONDAG = date(2026, 11, 15)
SISTE_MANDAG = SISTE_SONDAG - timedelta(days=6)


def test_seks_roller_i_fast_rekkefolge(roller: dict) -> None:
    assert list(roller) == ROLLER
    for r in roller.values():
        assert r["navn"] and r["forslag"] and len(r["forslag"]) == 4


@pytest.mark.parametrize("rid", ROLLER)
def test_hver_flis_har_tall_sammenligning_status_og_kilde(roller: dict, rid: str) -> None:
    fliser = roller[rid]["fliser"]
    assert 3 <= len(fliser) <= 4
    for f in fliser:
        assert f["kilde"], f["id"]
        if f["verdi"] is None:
            assert f["status"] == "Ukjent", f["id"]
            continue
        assert f["sammenligning"], f["id"]            # et tall uten sammenligning er et anti-mål i specen
        assert f["status"] in ("Normal", "Følg med", "Over terskel"), f["id"]
        if f.get("serie") is not None:
            assert len(f["serie"]) == len(f["serie_etiketter"]) >= 6, f["id"]


@pytest.mark.parametrize("rid", ROLLER)
def test_hver_rolle_har_flater_med_underlag_og_kilde(roller: dict, rid: str) -> None:
    flater = roller[rid]["flater"]
    assert 3 <= len(flater) <= 5
    for p in flater:
        assert p["type"] in ("linje", "stolper", "frister", "liste"), p["id"]
        assert p["kilde"] and p["tittel"]
        assert p["underlag"]["kolonner"], p["id"]


def test_besok_forrige_uke_stemmer(roller: dict) -> None:
    fasit = _sql("SELECT sum(besok_totalt) FROM dagsbesok WHERE dato BETWEEN ? AND ?",
                 SISTE_MANDAG.isoformat(), SISTE_SONDAG.isoformat())
    assert _flis(roller["direktor"], "besok_uke")["verdi"] == fasit
    assert _flis(roller["publikum"], "besok_uke")["verdi"] == fasit


def test_resultat_hittil_i_aar_stemmer(roller: dict) -> None:
    fasit = _sql("SELECT sum(CASE WHEN konto < '4000' THEN belop_nok ELSE -belop_nok END) FROM driftsregnskap "
                 "WHERE maaned BETWEEN '2026-01' AND '2026-10'")
    assert _flis(roller["okonomi"], "resultat")["verdi"] == round(fasit)
    assert _flis(roller["direktor"], "resultat")["verdi"] == round(fasit)


def test_framtidige_maaneder_telles_ikke(roller: dict) -> None:
    linje = next(p for p in roller["okonomi"]["flater"] if p["id"] == "resultat_maaned")
    assert "nov" not in [e.lower()[:3] for e in linje["data"]["etiketter"]]  # november er ikke ferdig 19.11


def test_sykefravaersdager_forrige_uke_stemmer(roller: dict) -> None:
    fasit = _sql("""SELECT coalesce(sum(julianday(min(til, ?)) - julianday(max(fra, ?)) + 1), 0) FROM hr_fravaer
                    WHERE type IN ('egenmelding', 'sykemelding') AND fra <= ? AND til >= ?""",
                 SISTE_SONDAG.isoformat(), SISTE_MANDAG.isoformat(), SISTE_SONDAG.isoformat(), SISTE_MANDAG.isoformat())
    assert _flis(roller["hr"], "fravaer_uke")["verdi"] == round(fasit)


def test_overtid_forrige_uke_stemmer(roller: dict) -> None:
    fasit = _sql("SELECT coalesce(sum(overtid_timer), 0) FROM hr_vakter WHERE dato BETWEEN ? AND ?",
                 SISTE_MANDAG.isoformat(), SISTE_SONDAG.isoformat())
    assert _flis(roller["hr"], "overtid_uke")["verdi"] == round(fasit, 1)


def test_uke_etter_sluttdato_er_tom_og_flisen_viser_uka_for(roller: dict) -> None:
    # Slutter kilden før siste hele uke, er den uka tom i kurven (ikke 0), og flisen sier hvilken uke den viser.
    slutt = _sql("SELECT max(dato) FROM avvik_hms_drift")
    f = _flis(roller["drift"], "hms_uke")
    if slutt < SISTE_SONDAG.isoformat():
        assert f["serie"][-1] is None
        siste_med_tall = max(i for i, v in enumerate(f["serie"]) if v is not None)
        assert f["navn"].endswith(f["serie_etiketter"][siste_med_tall])


@pytest.mark.parametrize("rid,fid", [("drift", "aapne"), ("samling", "klima_aapne")])
def test_beholdning_etter_sluttdato_sier_datoen(roller: dict, rid: str, fid: str) -> None:
    # Et hull skal ikke se ut som «ingen endring»: står tallet stille fordi kilden slutter, sier navnet hvilken dato det gjelder.
    slutt = _sql("SELECT max(dato) FROM driftsmeldinger_epost")
    f = _flis(roller[rid], fid)
    if slutt < (IDAG - timedelta(days=1)).isoformat():
        assert f"per {slutt[8:10]}.{slutt[5:7]}" in f["navn"], f["navn"]
        if slutt < SISTE_SONDAG.isoformat():
            assert f["serie"][-1] is None


def test_retning_og_status_folger_hva_som_er_bra() -> None:
    v = storskjerm_roller._vurder
    assert v(80, 100, +1)["status"] == "Følg med"      # 20 % færre besøk
    assert v(60, 100, +1)["status"] == "Over terskel"
    assert v(130, 100, -1)["status"] == "Over terskel"  # 30 % mer fravær
    assert v(95, 100, +1)["status"] == "Normal"
    assert v(0, 0, -1)["status"] == "Normal"
    assert v(3, 0, -1)["status"] == "Over terskel"


def test_ingen_navn_paa_skjermen(roller: dict) -> None:
    with db.get_db_connection() as con:
        navn = {r[0] for r in con.execute("SELECT navn FROM hr_ansatte") if r[0]}
    tekst = json.dumps(roller, ensure_ascii=False)
    funnet = sorted(n for n in navn if n in tekst)
    assert funnet == []


def test_hr_fristene_viser_id_ikke_navn(roller: dict) -> None:
    p = next(p for p in roller["hr"]["flater"] if p["type"] == "frister")
    syke = [r for r in p["data"]["rader"] if r["type"].startswith("sykefravaer")]
    for r in syke:
        assert r["ref"].startswith("KP-ANS-") and r["ref"] not in r["tittel"].split(":")[0]
        assert ":" not in r["tittel"]


def test_vet_ikke_bruker_vanlige_ord(roller: dict) -> None:
    for r in roller.values():
        for p in r["flater"]:
            if p["type"] == "liste":
                for linje in p["data"]["rader"]:
                    assert "_" not in linje, linje
