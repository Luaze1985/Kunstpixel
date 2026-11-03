"""Koblingskontroll mellom datalagene (A: nøklene finner hverandre, B: innholdet stemmer).

Kontrollene ligger i src/kunstpixel/data/koblinger.py. Et kjent avvik står med dagens antall som forventning:
testen feiler hvis det blir flere (regresjon) eller færre (stram inn forventningen og si fra hvorfor).
"""

import shutil
import sqlite3

import pytest

from src.kunstpixel.data import koblinger as K
from src.kunstpixel.persondata.config import MUSEUM_DB_STI
from src.kunstpixel.persondata.generer import bygg_fra_csv


@pytest.fixture(scope="module")
def pd_db(tmp_path_factory):
    sti = tmp_path_factory.mktemp("kobling") / "persondata.db"
    bygg_fra_csv(sti)  # fra de committede CSV-ene, samme som en fersk klone
    return sti


@pytest.fixture(scope="module")
def resultater(pd_db):
    return {r.kontroll.id: r for r in K.kjor(MUSEUM_DB_STI, pd_db)}


def test_kontroll_id_er_unike_og_alle_kjente_avvik_er_forklart():
    ider = [k.id for k in K.KONTROLLER]
    assert len(ider) == len(set(ider))
    assert all(k.forklaring for k in K.KONTROLLER if k.forventet > 0)


@pytest.mark.parametrize("kontroll", K.KONTROLLER, ids=lambda k: k.id)
def test_kontrollen_holder(resultater, kontroll):
    r = resultater[kontroll.id]
    assert r.status in ("OK", "KJENT AVVIK"), (
        f"{kontroll.id} {kontroll.beskrivelse}: {r.antall} brudd, forventet {kontroll.forventet}. "
        + ("Bedre enn forventet: stram inn forventet i koblinger.py." if r.status == "BEDRE" else f"Eksempel: {r.eksempel}")
    )


def test_uten_persondata_hoppes_bare_de_kontrollene_over():
    res = K.kjor(MUSEUM_DB_STI, None)
    assert {r.kontroll.id for r in res if r.status == "HOPPET OVER"} == {k.id for k in K.KONTROLLER if k.trenger_persondata}


# ---------- kontrollene er ikke tomme: en innlagt feil blir fanget ----------


def _kopier(tmp_path, pd_db):
    m, p = tmp_path / "museum.db", tmp_path / "persondata.db"
    shutil.copy(MUSEUM_DB_STI, m)
    shutil.copy(pd_db, p)
    return m, p


@pytest.mark.parametrize(
    "db, sql, fanget_av",
    [
        ("p", "UPDATE kontakter SET ansatt_id = 'KP-ANS-999' WHERE ansatt_id = 'KP-ANS-001'", "A05"),
        ("p", "UPDATE gavekort SET solgt_av_ansatt_id = 'KP-ANS-001', utstedt = '2009-06-01' WHERE gavekort_id = 1", "B11"),
        ("m", "UPDATE utstillinger_historikk SET saler = 'Sal Z' WHERE utstilling_id = 'KP-EXH-2010-001'", "A14"),
        ("m", "UPDATE h5_historikk_2010_2026 SET ansatte_arsverk = 1.0 WHERE ar = 2015", "B02"),
        ("m", "UPDATE h5_historikk_2010_2026 SET besok_totalt = besok_totalt + 1 WHERE ar = 2024", "B01"),
        ("p", "UPDATE medlemsbesok SET dato = (SELECT min(dato) FROM dagsbesok_kopi WHERE er_aapent = 0 AND dato >= '2022-01-01') WHERE besok_id = 1", "B17"),
        ("m", "UPDATE hendelser SET ansvarlig_rolle = 'vaktmester' WHERE id = 1", "A15"),
    ],
)
def test_innlagt_feil_blir_fanget(tmp_path, pd_db, db, sql, fanget_av):
    m, p = _kopier(tmp_path, pd_db)
    with sqlite3.connect(p if db == "p" else m) as c:
        if "dagsbesok_kopi" in sql:
            c.execute("ATTACH DATABASE ? AS mm", (str(m),))
            c.execute("CREATE TEMP TABLE dagsbesok_kopi AS SELECT * FROM mm.dagsbesok")
        c.execute(sql)
        assert c.total_changes > 0, "den innlagte feilen endret ingen rad, så testen beviser ingenting"
    res = {r.kontroll.id: r for r in K.kjor(m, p)}
    assert res[fanget_av].status == "FEIL", (fanget_av, res[fanget_av].antall)
