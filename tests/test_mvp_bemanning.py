"""MVP-fasit for bemanning og vurdering av ansatte (docs/specs/internside-oppslagsverk.md, oppgave 07–09).

Vitale sjekker, skrevet 2026-10-24 FØR koden finnes. Lars har bestemt:
  - «Vurdere ansatte» = egnethet for vakt/stasjon ut fra dokumenterte fakta (ikke prestasjon eller atferd).
  - Omfang: alle vakter i vaktplanen, alle 168 i hr_ansatte (bare aktive kan settes på vakt).
  - AI foreslår, faste regler kontrollerer, et menneske godkjenner. Alt er «AI-forslag», aldri vedtak.
  - Åpent på nett (alt er syntetisk), men navn, fraværsårsak og andre persondata sendes aldri til AI.

  B1 Krav per stasjon finnes          B4 Fraværsårsak og navn går aldri til AI (CASE-012)
  B2 «Egnet» betyr egnet              B5 AI-forslaget kontrolleres og må godkjennes
  B3 Kontrollen avviser feil forslag  B6 Uten AI vises et forslag som består kontrollen

Regel for den som bygger: Endre koden, ikke sjekkene. Fjern bare merket (@VENTER_PA_07 osv.)
når delen er bygget. Merket er strict. Endringer i selve sjekkene avtales med Lars.

Kontrakten koden må oppfylle (core/bemanning.py, kompetanse fra org_ferdigheter/org_ansatt_kompetanse):
  krav(stasjon, db_path=None) -> list[str]                      skill_code som stasjonen krever
  kandidater(dato, stasjon, db_path=None) -> dict
      {"dato", "stasjon", "start", "slutt", "krav": [...],
       "personer": [{"ansatt_id", "stilling", "egnet": bool, "mangler": [grunn, ...]}]}
  vurder_ansatt(ansatt_id, dato, stasjon, db_path=None) -> {"ansatt_id", "egnet": bool, "mangler": [...]}
  vurder_forslag(dato, forslag: dict[stasjon, ansatt_id | None], db_path=None) -> dict
      {"godkjent": bool, "feil": [{"stasjon", "ansatt_id", "grunn"}], "mangel": [stasjon]}
      Bare stasjonene i forslaget kontrolleres. None = ingen egnet (mangel), ikke feil.
      grunn ∈ UKJENT_PERSON, UKJENT_STASJON, SLUTTET, FRAVAER, MANGLER_KURS, DOBBELTBOOKET, HVILETID
  foreslaa(dato, konfig, begrenser, apne=urllib.request.urlopen, db_path=None) -> dict
      {"status": "ok" | "ai_av" | "grense_naadd" | "ai_feil",
       "deterministisk_forslag": {stasjon: ansatt_id | None},
       "ai": None | {"merke": "AI-forslag", "forslag": {stasjon: ansatt_id | None}, "tekst": str},
       "kontroll": vurder_forslag(...) av AI-forslaget (eller det deterministiske når ai er None),
       "krever_godkjenning": True}
      AI-en svarer med et JSON-objekt som har nøkkelen "forslag".
Vaktene (stasjon, start, slutt) for en dato er dem som står i hr_vakter. Hviletid: minst
arbeidstid_grenser.daglig_hvile_timer mellom vakter, også mot vakter dagen før og dagen etter.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest

from src.kunstpixel.core import llm

VENTER_PA_07 = pytest.mark.xfail(strict=True, reason="MVP: bygges i oppgave 07 (krav per stasjon)")
VENTER_PA_08 = pytest.mark.xfail(strict=True, reason="MVP: bygges i oppgave 08 (bemanningsmotor uten AI)")
VENTER_PA_09 = pytest.mark.xfail(strict=True, reason="MVP: bygges i oppgave 09 (AI-forslag til bemanning)")

KONFIG = llm.LlmKonfig(leverandor="anthropic", modell="test-modell", api_key="falsk")
DATO = "2026-11-12"  # har vakter på alle stasjoner og sykmeldte ansatte i dagens data


def _bemanning():
    from src.kunstpixel.core import bemanning

    return bemanning


class _Svar:
    def __init__(self, kropp: bytes) -> None:
        self._kropp = kropp

    def read(self) -> bytes:
        return self._kropp

    def __enter__(self) -> _Svar:
        return self

    def __exit__(self, *exc) -> bool:
        return False


class FalskLeverandor:
    """Later som Claude. Husker hva som ble sendt, og svarer med fast tekst. Ingen nettverk."""

    def __init__(self, tekst: str) -> None:
        self.tekst = tekst
        self.kall: list[dict] = []

    def __call__(self, foresporsel, timeout=None):
        self.kall.append(json.loads(foresporsel.data.decode("utf-8")))
        return _Svar(json.dumps({"content": [{"type": "text", "text": self.tekst}]}).encode("utf-8"))


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("mvp-bemanning") / "museum.db"
    bygg(db)
    return db


def _sql(db: Path, sql: str, *params) -> list[tuple]:
    con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def _vakter(db: Path, dato: str) -> list[tuple[str, str, str, str]]:
    return _sql(db, "SELECT stasjon, ansatt_id, start, slutt FROM hr_vakter WHERE dato = ? ORDER BY start", dato)


def _aktive(db: Path) -> list[str]:
    return [r[0] for r in _sql(db, "SELECT ansatt_id FROM hr_ansatte WHERE status != 'Sluttet' ORDER BY ansatt_id")]


def _fravaerende(db: Path, dato: str) -> list[str]:
    return [r[0] for r in _sql(db, """SELECT f.ansatt_id FROM hr_fravaer f JOIN hr_ansatte a USING (ansatt_id)
                                      WHERE ? BETWEEN f.fra AND f.til AND a.status != 'Sluttet'""", dato)]


def _har_gyldig(db: Path, ansatt_id: str, kode: str, dato: str) -> bool:
    return bool(_sql(db, """SELECT 1 FROM org_ansatt_kompetanse WHERE ansatt_id = ? AND skill_code = ?
                            AND status = 'gyldig' AND (gyldig_til IS NULL OR gyldig_til >= ?)""", ansatt_id, kode, dato))


def _grunner(kontroll: dict, stasjon: str) -> set[str]:
    return {f["grunn"] for f in kontroll["feil"] if f["stasjon"] == stasjon}


# ---------- B1 Krav per stasjon finnes ----------

@VENTER_PA_07
def test_b1_alle_stasjoner_i_vaktplanen_har_krav_som_finnes(bygget_db: Path) -> None:
    kjente = {r[0] for r in _sql(bygget_db, "SELECT skill_code FROM org_ferdigheter")}
    stasjoner = [r[0] for r in _sql(bygget_db, "SELECT DISTINCT stasjon FROM hr_vakter WHERE aar = '2026'")]
    assert stasjoner
    for stasjon in stasjoner:
        krav = _bemanning().krav(stasjon, db_path=bygget_db)
        assert krav, f"{stasjon} mangler krav"
        assert set(krav) <= kjente, f"{stasjon} krever ukjent kurs: {set(krav) - kjente}"


# ---------- B2 «Egnet» betyr egnet ----------

@VENTER_PA_08
def test_b2_alle_som_merkes_egnet_er_aktive_til_stede_og_har_gyldige_kurs(bygget_db: Path) -> None:
    aktive, borte = set(_aktive(bygget_db)), set(_fravaerende(bygget_db, DATO))
    egnede_totalt = 0
    for stasjon, *_ in _vakter(bygget_db, DATO):
        res = _bemanning().kandidater(DATO, stasjon, db_path=bygget_db)
        for p in res["personer"]:
            if not p["egnet"]:
                assert p["mangler"], "en som ikke er egnet skal ha en grunn"
                continue
            egnede_totalt += 1
            assert p["ansatt_id"] in aktive
            assert p["ansatt_id"] not in borte
            assert all(_har_gyldig(bygget_db, p["ansatt_id"], k, DATO) for k in res["krav"])
    assert egnede_totalt > 0


@VENTER_PA_08
def test_b2_vurder_ansatt_gir_fravaer_uten_arsak(bygget_db: Path) -> None:
    borte = _fravaerende(bygget_db, DATO)[0]
    stasjon = _vakter(bygget_db, DATO)[0][0]
    vurdering = _bemanning().vurder_ansatt(borte, DATO, stasjon, db_path=bygget_db)
    assert vurdering["egnet"] is False
    assert "FRAVAER" in vurdering["mangler"]
    tekst = json.dumps(vurdering, ensure_ascii=False).lower()
    assert "sykemelding" not in tekst and "egenmelding" not in tekst


# ---------- B3 Kontrollen avviser feil forslag ----------

@VENTER_PA_08
def test_b3_ukjent_sluttet_og_fravaerende_avvises(bygget_db: Path) -> None:
    vakter = _vakter(bygget_db, DATO)
    sluttet = _sql(bygget_db, "SELECT ansatt_id FROM hr_ansatte WHERE status = 'Sluttet' LIMIT 1")[0][0]
    borte = _fravaerende(bygget_db, DATO)[0]
    forslag = {vakter[0][0]: "KP-ANS-999", vakter[1][0]: sluttet, vakter[2][0]: borte}
    kontroll = _bemanning().vurder_forslag(DATO, forslag, db_path=bygget_db)
    assert kontroll["godkjent"] is False
    assert "UKJENT_PERSON" in _grunner(kontroll, vakter[0][0])
    assert "SLUTTET" in _grunner(kontroll, vakter[1][0])
    assert "FRAVAER" in _grunner(kontroll, vakter[2][0])


@VENTER_PA_08
def test_b3_manglende_eller_utlopt_kurs_avvises(bygget_db: Path) -> None:
    for stasjon, *_ in _vakter(bygget_db, DATO):
        krav = _bemanning().krav(stasjon, db_path=bygget_db)
        uten = [a for a in _aktive(bygget_db) if not all(_har_gyldig(bygget_db, a, k, DATO) for k in krav)]
        if uten:
            kontroll = _bemanning().vurder_forslag(DATO, {stasjon: uten[0]}, db_path=bygget_db)
            assert "MANGLER_KURS" in _grunner(kontroll, stasjon)
            return
    pytest.fail("fant ingen aktiv ansatt som mangler kurs for noen stasjon")


@VENTER_PA_08
def test_b3_samme_person_pa_to_vakter_samtidig_avvises(bygget_db: Path) -> None:
    vakter = _vakter(bygget_db, DATO)
    (s1, _, start1, slutt1), (s2, _, start2, slutt2) = next(
        (a, b) for i, a in enumerate(vakter) for b in vakter[i + 1:] if a[2] < b[3] and b[2] < a[3]
    )
    person = _aktive(bygget_db)[0]
    kontroll = _bemanning().vurder_forslag(DATO, {s1: person, s2: person}, db_path=bygget_db)
    assert "DOBBELTBOOKET" in _grunner(kontroll, s1) | _grunner(kontroll, s2)


@VENTER_PA_08
def test_b3_for_kort_hviletid_etter_kveldsvakt_avvises(bygget_db: Path) -> None:
    for ansatt_id, dag in _sql(bygget_db, """SELECT v.ansatt_id, v.dato FROM hr_vakter v JOIN hr_ansatte a USING (ansatt_id)
                                            WHERE v.slutt >= '23:00' AND v.aar = '2026' AND a.status != 'Sluttet'
                                            ORDER BY v.dato"""):
        neste = (date.fromisoformat(dag) + timedelta(days=1)).isoformat()
        tidlige = [v for v in _vakter(bygget_db, neste) if v[2] < "10:00"]
        if tidlige:
            kontroll = _bemanning().vurder_forslag(neste, {tidlige[0][0]: ansatt_id}, db_path=bygget_db)
            assert "HVILETID" in _grunner(kontroll, tidlige[0][0])
            return
    pytest.fail("fant ingen kveldsvakt fulgt av en tidlig vakt dagen etter")


# ---------- B4 Fraværsårsak og navn går aldri til AI ----------

@VENTER_PA_09
def test_b4_ai_far_ikke_navn_eller_fravaersarsak(bygget_db: Path) -> None:
    lev = FalskLeverandor(json.dumps({"forslag": {}}))
    _bemanning().foreslaa(DATO, KONFIG, llm.Begrenser(20), apne=lev, db_path=bygget_db)
    assert len(lev.kall) == 1
    sendt = json.dumps(lev.kall[0], ensure_ascii=False)
    assert "sykemelding" not in sendt.lower() and "egenmelding" not in sendt.lower()
    navn = [r[0] for r in _sql(bygget_db, "SELECT navn FROM hr_ansatte WHERE navn IS NOT NULL")]
    lekket = [n for n in navn if n and n in sendt]
    assert not lekket, f"navn sendt til AI: {lekket[:3]}"
    for felt in ("fodselsaar", "kjonn", "epost", "telefon"):
        assert f'"{felt}"' not in sendt and f'\\"{felt}\\"' not in sendt


# ---------- B5 AI-forslaget kontrolleres og må godkjennes ----------

@VENTER_PA_09
def test_b5_ai_forslag_med_feil_person_blir_stoppet_av_kontrollen(bygget_db: Path) -> None:
    vakter = _vakter(bygget_db, DATO)
    sluttet = _sql(bygget_db, "SELECT ansatt_id FROM hr_ansatte WHERE status = 'Sluttet' LIMIT 1")[0][0]
    lev = FalskLeverandor(json.dumps({"forslag": {vakter[0][0]: sluttet}}))
    res = _bemanning().foreslaa(DATO, KONFIG, llm.Begrenser(20), apne=lev, db_path=bygget_db)
    assert res["status"] == "ok"
    assert res["ai"]["merke"] == "AI-forslag"
    assert res["ai"]["forslag"][vakter[0][0]] == sluttet
    assert res["kontroll"]["godkjent"] is False
    assert "SLUTTET" in _grunner(res["kontroll"], vakter[0][0])
    assert res["krever_godkjenning"] is True


# ---------- B6 Uten AI vises et forslag som består kontrollen ----------

@VENTER_PA_09
def test_b6_uten_ai_finnes_et_forslag_som_bestar_kontrollen(bygget_db: Path) -> None:
    res = _bemanning().foreslaa(DATO, None, None, db_path=bygget_db)
    assert res["status"] == "ai_av" and res["ai"] is None
    forslag = res["deterministisk_forslag"]
    assert set(forslag) == {v[0] for v in _vakter(bygget_db, DATO)}, "alle vaktene den dagen skal ha et forslag eller mangel"
    kontroll = _bemanning().vurder_forslag(DATO, forslag, db_path=bygget_db)
    assert kontroll["godkjent"] is True, kontroll["feil"]
    assert res["krever_godkjenning"] is True
