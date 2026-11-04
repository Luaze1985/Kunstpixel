"""HR- og HMS-pakken: hele pakken er syntetisk, deterministisk og henger sammen med historikken 2010 til 2026."""

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from datetime import date

import pytest

from src.kunstpixel.core.intern import hr_hms_pakke as P
from src.kunstpixel.core.intern import leveranse as L

H, AAR = L._H, L.HISTORIKK_AAR


@pytest.fixture(scope="module")
def tab():
    return P.tabeller()


def per_ar(rader, felt="dato"):
    return Counter(int(r[felt][:4]) for r in rader)


def test_package_is_byte_identical_every_time():
    assert P.zip_bytes() == P.zip_bytes()
    assert hashlib.sha256(P.zip_bytes()).hexdigest() == hashlib.sha256(P.zip_bytes()).hexdigest()


def test_zip_contains_all_tables_readme_and_a_manifest_that_matches(tab):
    with zipfile.ZipFile(io.BytesIO(P.zip_bytes())) as z:
        navn = set(z.namelist())
        assert navn == set(tab) | {"README.md", "MANIFEST.json"}
        m = json.loads(z.read("MANIFEST.json"))
        for fil, info in m["filer"].items():
            assert hashlib.sha256(z.read(fil)).hexdigest() == info["sha256"] and info["rader"] == len(tab[fil])
        assert m["klassifisering"] == "syntetisk"


def test_every_row_is_marked_synthetic_and_files_open_in_norwegian_excel():
    for navn, data in P.pakke().items():
        if not navn.endswith(".csv"):
            continue
        assert data.startswith(b"\xef\xbb\xbf")
        rader = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig")), delimiter=";"))
        assert rader and all(r["klassifisering"] == "syntetisk" for r in rader), navn


def test_year_end_fte_matches_the_history_series_exactly(tab):
    for i, ar in enumerate(AAR):
        assert P.aarsverk_ved_aarsslutt(tab["ansatte.csv"], ar) == H["ansatte_arsverk"][i], ar


def test_staff_register_is_consistent(tab):
    reg = tab["ansatte.csv"]
    assert len({a["ansatt_id"] for a in reg}) == len(reg) and len({a["navn"] for a in reg}) == len(reg)
    assert all(a["epost"].endswith("@kunstpixel.example.test") and re.fullmatch(r"[a-z0-9.@-]+", a["epost"]) for a in reg)
    for a in reg:
        assert not a["ansatt_til"] or a["ansatt_fra"] < a["ansatt_til"]
        assert a["rolle"] in L.ROLLER_TILLATT
    nu = {a["stillingstittel"]: a["navn"] for a in reg if not a["ansatt_til"]}
    for tittel in ("Museumsdirektør", "Driftsansvarlig", "Kafeansvarlig"):
        assert nu[tittel] == L.INTERNE_PERSONER[tittel][0]
    assert not {a["navn"] for a in reg} & {n for n, _ in L.KONTAKTPERSONER.values()}  # myndighetenes folk er ikke ansatte


def test_ruh_counts_injuries_and_deadlines_follow_the_history(tab):
    ruh = tab["ruh_avviksmeldinger.csv"]
    assert per_ar(ruh) == Counter(dict(zip(AAR, H["ruh_registrert"])))
    skader = Counter(int(r["dato"][:4]) for r in ruh if r["kategori"] == "personskade")
    assert all(skader.get(ar, 0) == H["skader_med_fravaer"][i] for i, ar in enumerate(AAR))
    assert len({r["ruh_id"] for r in ruh}) == len(ruh)
    for r in ruh:
        assert r["dato"] <= P.IDAG.isoformat()
        if r["status"] == "lukket":
            assert r["lukket_dato"] >= r["dato"] and r["lukket_innen_frist"] in ("ja", "nei")
        assert (r["kategori"] == "personskade") == (int(r["fravaersdager"]) > 0)
    aktive = {a["ansatt_id"]: a for a in tab["ansatte.csv"]}
    for r in ruh:  # melderen var ansatt den dagen
        a = aktive[r["melder_id"]]
        assert a["ansatt_fra"] <= r["dato"] and (not a["ansatt_til"] or r["dato"] <= a["ansatt_til"])


def test_inspections_sum_to_the_history(tab):
    t = tab["tilsyn.csv"]
    for felt, serie in (("avvik_funnet", "avvik_funnet"), ("avvik_lukket_innen_frist", "avvik_lukket_innen_frist"), ("palegg", "palegg_antall")):
        s = Counter()
        for r in t:
            s[int(r["dato"][:4])] += r[felt]
        assert s == Counter({ar: v for ar, v in zip(AAR, H[serie]) if v}), felt
    assert per_ar(t) == Counter(dict(zip(AAR, H["tilsyn_antall"])))
    assert all(r["avvik_lukket_innen_frist"] <= r["avvik_funnet"] and r["dato"] <= P.IDAG.isoformat() for r in t)
    for r in t:
        if r["resultat"] == "uten avvik":
            assert r["avvik_funnet"] == 0 and r["palegg"] == 0
        elif r["resultat"] == "avvik, alle lukket innen frist":
            assert r["avvik_funnet"] == r["avvik_lukket_innen_frist"] and r["palegg"] == 0
        elif r["resultat"] == "avvik, noen lukket etter frist":
            assert r["avvik_lukket_innen_frist"] < r["avvik_funnet"] and r["palegg"] == 0
        else:
            assert r["resultat"] == "avvik og pålegg" and r["palegg"] == 1
    ids = {n: i for i, n, _, _ in L.MYNDIGHETER}
    assert all(r["myndighet_id"] == ids[r["myndighet"]] and r["kontaktperson"] == L.KONTAKTPERSONER[r["myndighet_id"]][0] for r in t)


def test_other_counts_follow_the_history(tab):
    assert per_ar(tab["vernerunder.csv"]) == Counter(dict(zip(AAR, H["vernerunder_gjennomfort"])))
    assert per_ar(tab["temperaturavvik_kafe.csv"]) == Counter({ar: v for ar, v in zip(AAR, H["ik_mat_temperaturavvik"]) if v})
    assert all(r["funn_lukket"] <= r["funn_antall"] and r["dato"] <= P.IDAG.isoformat() for r in tab["vernerunder.csv"])
    n = {r["ar"]: r for r in tab["hr_nokkeltall_per_ar.csv"]}
    assert n[2010]["nyansatte"] == 0  # staben ved oppstart er ikke nyansatte
    for ar in AAR[1:]:  # hoder ved årsslutt = hoder ved årsstart + nyansatte - avganger
        assert n[ar]["hoder_31_12"] == n[ar]["hoder_1_1"] + n[ar]["nyansatte"] - n[ar]["avganger"], ar
    for i, ar in enumerate(AAR):
        assert n[ar]["sykefravaer_prosent"] == H["sykefravaer_prosent"][i] and n[ar]["ansatte_arsverk"] == H["ansatte_arsverk"][i]


def test_monthly_sick_leave_averages_back_to_the_annual_figure_and_stops_in_september_2026(tab):
    mnd = tab["sykefravaer_per_maned.csv"]
    for i, ar in enumerate(AAR):
        v = [r["sykefravaer_prosent"] for r in mnd if r["ar"] == ar]
        assert len(v) == (9 if ar == 2026 else 12)
        assert abs(sum(v) / len(v) - H["sykefravaer_prosent"][i]) < 0.12, ar
    pand = {r["maned"]: r["sykefravaer_prosent"] for r in mnd if r["ar"] == 2020}
    assert pand[3] > 1.2 * pand[7]  # pandemitopp i mars, lavt om sommeren


def test_temperature_deviations_are_actual_breaches_of_the_ik_mat_limits(tab):
    for r in tab["temperaturavvik_kafe.csv"]:
        m = r["malt_celsius"]
        if r["utstyr"] == "kjøleskap":
            assert m > 4
        elif r["utstyr"] == "fryser":
            assert m > -18
        else:
            assert m < 60


def test_training_and_fire_drills_are_plausible(tab):
    kurs = {(r["ar"], r["kurs"]): r for r in tab["opplaering.csv"]}
    assert kurs[(2020, "HLR og førstehjelp")]["gjennomfort"] == "nei"  # pandemi
    assert kurs[(2022, "HLR og førstehjelp")]["gjennomfort"] == "ja" and kurs[(2023, "HLR og førstehjelp")]["gjennomfort"] == "nei"
    assert all(0 <= r["dekning_prosent"] <= 100 and r["deltakere"] <= r["malgruppe_antall"] for r in kurs.values())
    brann = tab["brannovelser.csv"]
    assert per_ar(brann)[2020] == 1 and per_ar(brann)[2024] == 2
    tid = {r["ovelse_id"]: r["evakueringstid_sekunder"] for r in brann}
    assert tid["BO-2010-1"] > tid["BO-2026-1"]  # evakueringen går raskere over tid


def test_nothing_that_looks_like_real_contact_data_or_dates_in_the_future():
    for navn, data in P.pakke().items():
        tekst = data.decode("utf-8-sig")
        assert not re.search(r"https?://|\+47|\+\d{8}|\b\d{2}[ -]\d{2}[ -]\d{2}[ -]\d{2}\b", tekst), navn  # «+60 °C» er en temperatur, ikke et telefonnummer
        for e in re.findall(r"[\w.+-]+@[\w.-]+", tekst):
            assert e.endswith(".example.test"), (navn, e)
        for d in re.findall(r"\b(20\d\d)-(\d\d)-(\d\d)\b", tekst):
            assert date(*map(int, d)) <= P.IDAG, (navn, d)  # ingen datoer etter siste dato i dataene


def test_cli_writes_the_zip(tmp_path):
    from tests import lag_hr_hms_pakke as cli

    ut = tmp_path / "pakke.zip"
    assert cli.main(["--til", str(ut)]) == 0
    assert ut.read_bytes() == P.zip_bytes()
