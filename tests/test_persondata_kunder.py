"""Task 3: generator for medlemmer, gavekort og kunder (syntetisk, 2021-11-02 til 2026-11-02)."""

import random
import re
from collections import defaultdict
from datetime import date

import pytest
from faker import Faker

from src.kunstpixel.persondata import ansattkilde as ak
from src.kunstpixel.persondata import config
from src.kunstpixel.persondata.kunder import generer_kunder

START, REF = config.KUNDER_START, config.REFERANSEDATO

# Datofelt som beskriver når noe skjedde (fremtidige gyldighets-/sluttdatoer er unntatt).
HENDELSESDATOER = {
    "kontakter": ["opprettet", "samtykke_dato", "trukket_dato", "siste_aktivitet"],
    "medlemskap": ["startdato"],
    "medlemsbesok": ["dato"],
    "fordel_bruk": ["dato"],
    "gavekort": ["utstedt"],
    "gavekort_bruk": ["dato"],
    "arrangementer": ["dato"],
    "pameldinger": ["registrert"],
    "skolebestillinger": ["dato"],
    "utleie": ["dato"],
    "henvendelser": ["tidspunkt"],
}

ANSATTREFERANSER = [
    ("medlemskap", "solgt_av_ansatt_id", "startdato"),
    ("gavekort", "solgt_av_ansatt_id", "utstedt"),
    ("arrangementer", "ansvarlig_ansatt_id", "dato"),
    ("skolebestillinger", "ansvarlig_ansatt_id", "dato"),
    ("utleie", "ansvarlig_ansatt_id", "dato"),
    ("henvendelser", "besvart_av_ansatt_id", "tidspunkt"),
]


def _lag(faktor: float, seed: int = 2026) -> dict:
    fake = Faker("no_NO")
    fake.seed_instance(seed)
    museum = config.MUSEUM_DB_STI
    return generer_kunder(
        random.Random(seed),
        fake,
        ak.hent_ansatte(museum),
        ak.hent_dagsbesok(museum, START, REF),
        ak.hent_hendelser(museum),
        faktor=faktor,
    )


@pytest.fixture(scope="module")
def data():
    return _lag(config.SKALAER["test"])


@pytest.fixture(scope="module")
def ansatte():
    return {a.ansatt_id: a for a in ak.hent_ansatte(config.MUSEUM_DB_STI)}


def _d(verdi: str) -> date:
    return date.fromisoformat(verdi[:10])


def test_alle_tabeller_har_rader(data):
    for tabell in HENDELSESDATOER:
        assert data[tabell], tabell


def test_deterministisk(data):
    assert _lag(config.SKALAER["test"]) == data


def test_alle_har_datakilde(data):
    for tabell, rader in data.items():
        assert all(r["datakilde"] == config.DATAKILDE for r in rader), tabell


def test_alle_datoer_i_kundeperioden(data):
    for tabell, felt in HENDELSESDATOER.items():
        for r in data[tabell]:
            for f in felt:
                if r[f] is not None:
                    assert START <= _d(r[f]) <= REF, (tabell, f, r[f])


def test_ansattkontakter_matcher_hr_navn(data, ansatte):
    ansattkontakter = [k for k in data["kontakter"] if k["ansatt_id"]]
    assert ansattkontakter
    for k in ansattkontakter:
        a = ansatte[k["ansatt_id"]]
        assert f"{k['fornavn']} {k['etternavn']}" == a.navn
        assert k["epost"] == a.epost


def test_ansattreferanser_aktive_paa_dato(data, ansatte):
    for tabell, felt, datofelt in ANSATTREFERANSER:
        for r in data[tabell]:
            if r[felt] is None:
                continue
            a = ansatte[r[felt]]
            dato = _d(r[datofelt])
            assert a.ansatt_fra <= dato and (a.ansatt_til is None or a.ansatt_til >= dato), (tabell, r)


def test_kundekontakter_er_fiktive(data):
    for k in data["kontakter"]:
        if k["ansatt_id"]:
            continue
        assert k["epost"].endswith("@eksempel.invalid") and re.fullmatch(r"[a-z0-9.]+@eksempel\.invalid", k["epost"])
        assert k["telefon"] is None or re.fullmatch(r"0\d{7}", k["telefon"])


def test_medlemsfordeler_kun_for_riktig_type(data):
    typer = {m["medlemskap_id"]: m["type"] for m in data["medlemskap"]}
    for b in data["fordel_bruk"]:
        assert typer[b["medlemskap_id"]] in config.FORDELER[b["fordel"]]["typer"], b


def test_fordel_bruk_innenfor_medlemskapet(data):
    m = {x["medlemskap_id"]: x for x in data["medlemskap"]}
    for b in data["fordel_bruk"]:
        ms = m[b["medlemskap_id"]]
        assert ms["startdato"] <= b["dato"] <= ms["sluttdato"]


def test_medlemsbesok_innenfor_dagsbesok(data):
    dagsbesok = ak.hent_dagsbesok(config.MUSEUM_DB_STI, START, REF)
    per_dag = defaultdict(int)
    for b in data["medlemsbesok"]:
        per_dag[_d(b["dato"])] += 1
    for dag, antall in per_dag.items():
        besok, aapent = dagsbesok[dag]
        assert aapent, f"medlemsbesøk på stengt dag {dag}"
        assert antall <= config.ANDELER["maks_medlemsandel_av_dagsbesok"] * besok


def test_gjester_bare_for_typer_med_fordelen(data):
    typer = {m["medlemskap_id"]: m["type"] for m in data["medlemskap"]}
    for b in data["medlemsbesok"]:
        if b["antall_gjester"] > 0:
            assert typer[b["medlemskap_id"]] in config.FORDELER["medbring_gjest"]["typer"]


def test_gavekort_saldo_aldri_negativ(data):
    brukt = defaultdict(float)
    for b in data["gavekort_bruk"]:
        brukt[b["gavekort_id"]] += b["belop"]
    for g in data["gavekort"]:
        assert brukt[g["gavekort_id"]] <= g["belop"] + 1e-9


def test_gavekort_ikke_brukt_etter_utlop(data):
    g = {x["gavekort_id"]: x for x in data["gavekort"]}
    for b in data["gavekort_bruk"]:
        kort = g[b["gavekort_id"]]
        assert kort["utstedt"] <= b["dato"] <= kort["gyldig_til"]


def test_gavekortkoder_unike(data):
    koder = [g["kode"] for g in data["gavekort"]]
    assert len(koder) == len(set(koder))
    assert all(re.fullmatch(r"GK-[A-Z0-9]{4}-[A-Z0-9]{4}", k) for k in koder)


def test_pameldinger_overstiger_aldri_kapasitet(data):
    maks = {a["arrangement_id"]: a["maks_deltakere"] for a in data["arrangementer"]}
    sum_ = defaultdict(int)
    for p in data["pameldinger"]:
        sum_[p["arrangement_id"]] += p["antall_voksne"] + p["antall_barn"]
    for arr, n in sum_.items():
        assert n <= maks[arr], arr


def test_kontakt_opprettet_for_pamelding(data):
    opprettet = {k["kontakt_id"]: k["opprettet"] for k in data["kontakter"]}
    for p in data["pameldinger"]:
        assert opprettet[p["kontakt_id"]] <= p["registrert"]


def test_arrangementer_fra_museum_db_er_med(data):
    mdb = [a for a in data["arrangementer"] if a["kilde"] == "museum.db"]
    assert mdb and all(a["arrangement_id"].startswith("MDB-") and a["dato"] <= REF.isoformat() for a in mdb)


def test_samtykkerekkefolge(data):
    for k in data["kontakter"]:
        if k["nyhetsbrev_samtykke"] == 0:
            assert k["samtykke_dato"] is None and k["trukket_dato"] is None
        if k["trukket_dato"]:
            assert k["trukket_dato"] > k["samtykke_dato"]


def test_plantede_brudd_finnes(data):
    grense = "2023-11-02"
    assert any(k["trukket_dato"] and k["epost"] and k["siste_aktivitet"] < grense for k in data["kontakter"])
    senere = defaultdict(list)
    for m in data["medlemskap"]:
        senere[m["kontakt_id"]].append(m["sluttdato"])
    epost = {k["kontakt_id"]: k["epost"] for k in data["kontakter"]}
    assert any(max(s) < grense and epost[kid] for kid, s in senere.items())


def test_henvendelser_persondata_andel(data):
    h = data["henvendelser"]
    med = [x for x in h if x["inneholder_persondata"] == 1]
    assert 0.03 <= len(med) / len(h) <= 0.07
    navn = {f"{k['fornavn']} {k['etternavn']}" for k in data["kontakter"]}
    for x in med:
        assert "@eksempel.invalid" in x["fritekst"] or re.search(r"0\d{7}", x["fritekst"]) or any(
            n in x["fritekst"] for n in navn
        ), x["fritekst"]


def test_henvendelser_uten_persondata_er_rene(data):
    for x in data["henvendelser"]:
        if x["inneholder_persondata"] == 0:
            assert "@" not in x["fritekst"] and not re.search(r"0\d{7}", x["fritekst"]), x["fritekst"]


def test_henvendelser_kategorier(data):
    kategorier = {x["kategori"] for x in data["henvendelser"]}
    assert kategorier <= {
        "billett", "praktisk", "fasiliteter", "formidling", "tilgjengelighet",
        "utleie", "samling", "butikk", "medlemskap", "gavekort",
    }


@pytest.mark.slow
def test_full_skala_volum():
    d = _lag(1.0)
    assert len([k for k in d["kontakter"] if not k["ansatt_id"]]) == 5000
    assert len(d["henvendelser"]) == 3000
    ref = REF.isoformat()
    aktive = [m for m in d["medlemskap"] if m["type"] != "ansatt" and m["startdato"] <= ref <= m["sluttdato"]]
    assert 650 <= len(aktive) <= 950
