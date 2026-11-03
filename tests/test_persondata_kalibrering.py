"""Kalibrering mot dagsbesok (eiers beslutning 2026-11-02: dagsbesok er sannheten).

K1 arrangementer som i hendelser, K2 skoleelever som andel av dagsbesøk, K3 stabil medlemsmasse fra start,
K4 gavekort på billett følger billettprisen, K5 henvendelser vektet etter publikum_faq.hyppighet.
"""

import random
from collections import Counter, defaultdict
from datetime import date, timedelta

import pytest
from faker import Faker

from src.kunstpixel.persondata import ansattkilde as ak
from src.kunstpixel.persondata import config
from src.kunstpixel.persondata.kunder import generer_kunder

START, REF = config.KUNDER_START, config.REFERANSEDATO
MUSEUM = config.MUSEUM_DB_STI


def _lag(faktor):
    fake = Faker("no_NO")
    fake.seed_instance(2026)
    return generer_kunder(
        random.Random(2026), fake, ak.hent_ansatte(MUSEUM),
        ak.hent_dagsbesok(MUSEUM, START - timedelta(days=365), REF), ak.hent_hendelser(MUSEUM),
        faktor=faktor, billettpriser=ak.hent_billettpriser(MUSEUM, START, REF), faq_vekter=ak.hent_faq_vekter(MUSEUM),
    )


@pytest.fixture(scope="module")
def full():
    return _lag(1.0)


def test_hent_billettpriser():
    p = ak.hent_billettpriser(MUSEUM, START, REF)
    assert p[date(2024, 6, 1)] == 120 and p[date(2022, 6, 1)] == 100


def test_hent_faq_vekter():
    v = ak.hent_faq_vekter(MUSEUM)
    assert v["praktisk"] == 109 and v["utleie"] == 8


@pytest.mark.slow
def test_k1_arrangementer_per_maaned_som_hendelser(full):
    per_mnd = Counter(a["dato"][:7] for a in full["arrangementer"] if a["kilde"] == "generert")
    mnd = [f"{y}-{m:02d}" for y in range(2022, 2026) for m in range(1, 13)]
    snitt = sum(per_mnd[x] for x in mnd) / len(mnd)
    assert 10 <= snitt <= 17


@pytest.mark.slow
def test_k2_skoleelever_som_andel_av_dagsbesok(full):
    besok = defaultdict(int)
    for d, (b, _) in ak.hent_dagsbesok(MUSEUM, START, REF).items():
        besok[d.year] += b
    elever = defaultdict(int)
    for s in full["skolebestillinger"]:
        elever[int(s["dato"][:4])] += s["antall_elever"]
    for aar in range(2022, 2026):
        assert 0.12 <= elever[aar] / besok[aar] <= 0.16, (aar, elever[aar], besok[aar])


def test_k2_skoleelever_innenfor_dagens_besok(full):
    dagsbesok = ak.hent_dagsbesok(MUSEUM, START, REF)
    per_dag = defaultdict(int)
    for s in full["skolebestillinger"]:
        per_dag[date.fromisoformat(s["dato"])] += s["antall_elever"]
    for dag, n in per_dag.items():
        besok, aapen = dagsbesok[dag]
        assert aapen and n <= config.ANDELER["maks_skoleandel_av_dagsbesok"] * besok, (dag, n, besok)


@pytest.mark.slow
@pytest.mark.parametrize("dag", ["2021-12-01", "2022-07-01", "2024-07-01", "2026-07-01"])
def test_k3_stabil_medlemsmasse_fra_start(full, dag):
    aktive = [m for m in full["medlemskap"] if m["type"] != "ansatt" and m["startdato"] <= dag <= m["sluttdato"]]
    assert 650 <= len(aktive) <= 950, (dag, len(aktive))


def test_k3_ingen_aktivitet_foer_perioden(full):
    for tabell, felt in [("medlemsbesok", "dato"), ("fordel_bruk", "dato"), ("gavekort", "utstedt"), ("pameldinger", "registrert")]:
        assert all(r[felt] >= START.isoformat() for r in full[tabell]), tabell


def test_k4_gavekort_billett_folger_billettprisen(full):
    priser = ak.hent_billettpriser(MUSEUM, START, REF)
    billett = [b for b in full["gavekort_bruk"] if b["sted"] == "billett"]
    assert billett
    for b in billett:
        pris = priser[date.fromisoformat(b["dato"])]
        assert b["belop"] <= 4 * pris + 1e-9, b


@pytest.mark.slow
def test_k5_henvendelser_vektet_etter_faq(full):
    n = Counter(h["kategori"] for h in full["henvendelser"])
    assert n.most_common(1)[0][0] == "praktisk"
    assert n["praktisk"] > 5 * n["utleie"]
