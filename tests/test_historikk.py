"""H5: historikk 2010 til 2026. Tallene lages av koden og skal henge sammen, og de skal ikke kunne endres av en modell."""

import copy
import hashlib
import sqlite3
from pathlib import Path

import pytest
import yaml

from src.kunstpixel.core.intern import leveranse as L
from src.kunstpixel.core.intern.data import DEFAULT_SOURCES, InternData, SourceSpec
from tests import kontroller_leveranse as cli
from tests.test_leveranse import Teller, dump, fyll

ROOT = Path(__file__).resolve().parent.parent

# Fingeravtrykk av tallfilen. Endres tallene med vilje, oppdater disse to linjene og si fra hvorfor.
FINGERAVTRYKK_TALL = "0a1938c5f4059bf7ad4064203122e519f326b6db97067b5b79a36bb8fa05eee7"
FINGERAVTRYKK_TEKST_SKJELETT = "78825771a3a0566349b1f4ab06b33e833a40b7edacf0f506750876e9a65caa7f"


@pytest.fixture(scope="module")
def rader():
    return L.historikk_rader()


def koder(funn):
    return {f.kode for f in funn if f.alvor == "FEIL"}


# ---------- Omfang ----------


def test_one_row_per_year_2010_to_2026_with_35_parameters(rader):
    assert [r["ar"] for r in rader] == list(range(2010, 2027))
    assert all(len(r) == 35 for r in rader)
    assert len({tuple(r) for r in rader}) == 1  # alle rader har de samme feltene i samme rekkefølge
    assert len(rader) * len(rader[0]) == 595


def test_only_the_current_year_is_preliminary(rader):
    assert [r["ar"] for r in rader if r["status_ar"] == "foreløpig"] == [2026]
    assert {r["status_ar"] for r in rader if r["ar"] < 2026} == {"endelig"}


def test_every_year_has_a_theme_and_themes_are_plain_text_without_digits(rader):
    for r in rader:
        assert r["tema"] and not any(c.isdigit() for c in r["tema"])


# ---------- Regnskapet går opp ----------


def test_derived_numbers_are_computed_exactly(rader):
    for r in rader:
        assert r["betalende_besokende"] == r["besok_totalt"] * r["betalende_andel_prosent"] // 100
        assert r["billettinntekter_tkr"] == r["betalende_besokende"] * r["snittpris_kr"] // 1000
        assert r["inntekter_totalt_tkr"] == r["billettinntekter_tkr"] + r["tilskudd_tkr"] + r["kafeinntekter_tkr"] + r["andre_inntekter_tkr"]
        assert r["resultat_tkr"] == r["inntekter_totalt_tkr"] - r["kostnader_tkr"]
        assert r["timer_totalt"] == r["timer_myndighetskontakt"] + r["timer_rapportering"]


def test_logical_limits_hold_every_year(rader):
    for r in rader:
        assert 0 <= r["avvik_lukket_innen_frist"] <= r["avvik_funnet"], r["ar"]
        assert 0 <= r["tilskudd_innvilget"] <= r["tilskuddssoknader"], r["ar"]
        assert 0 <= r["rapporter_for_sent"] <= r["rapporter_levert"] <= len(L.RAPPORTER), r["ar"]
        assert 0 <= r["betalende_besokende"] <= r["besok_totalt"] and 0 <= r["skoleelever"] <= r["besok_totalt"], r["ar"]
        assert 0 <= r["betalende_andel_prosent"] <= 100 and 0 <= r["sykefravaer_prosent"] <= 100 and 0 <= r["automatiseringsgrad_prosent"] <= 100
        assert r["vernerunder_gjennomfort"] <= 4 and r["inntekter_totalt_tkr"] > 0 and r["kostnader_tkr"] > 0
        for k, v in r.items():
            if k not in ("resultat_tkr", "tema", "status_ar") and isinstance(v, (int, float)):
                assert v >= 0, (r["ar"], k)


def test_all_numbers_are_whole_except_the_two_decimal_series(rader):
    desimal = {"ansatte_arsverk", "sykefravaer_prosent"}
    for r in rader:
        for k, v in r.items():
            if isinstance(v, float):
                assert k in desimal, (r["ar"], k)
            elif isinstance(v, int) and not isinstance(v, bool):
                assert k not in desimal or True


# ---------- Historien er troverdig ----------


def by(rader, ar):
    return next(r for r in rader if r["ar"] == ar)


def test_pandemic_years_show_the_dip_and_the_recovery(rader):
    assert by(rader, 2020)["besok_totalt"] < 0.4 * by(rader, 2019)["besok_totalt"]
    assert by(rader, 2020)["arrangementer_antall"] < by(rader, 2019)["arrangementer_antall"] / 2
    assert by(rader, 2020)["resultat_tkr"] < 0 and by(rader, 2021)["resultat_tkr"] < 0
    assert all(by(rader, a)["resultat_tkr"] > 0 for a in range(2022, 2027))
    assert "pandemi" in by(rader, 2020)["tema"] and "pandemi" in by(rader, 2021)["tema"]
    assert by(rader, 2022)["besok_totalt"] > 2 * by(rader, 2021)["besok_totalt"] * 0.9


def test_2019_is_the_record_year_before_the_pandemic(rader):
    assert by(rader, 2019)["tema"] == "rekordår"
    assert by(rader, 2019)["besok_totalt"] == max(r["besok_totalt"] for r in rader if r["ar"] < 2020)


def test_automation_starts_late_and_only_goes_up(rader):
    a = [r["automatiseringsgrad_prosent"] for r in rader]
    assert a[:13] == [0] * 13  # 2010 til 2022
    assert a[13:] == sorted(a[13:]) and len(set(a[13:])) == 4
    assert by(rader, 2025)["tema"] == "første automatisering" and by(rader, 2026)["tema"] == "KI-pilot"


def test_ticket_price_never_falls_and_staff_grows_over_the_period(rader):
    priser = [r["snittpris_kr"] for r in rader]
    assert priser == sorted(priser)
    assert by(rader, 2026)["ansatte_arsverk"] > by(rader, 2010)["ansatte_arsverk"]


# ---------- Henger sammen med resten av dataene ----------


def test_2026_matches_the_time_use_file_exactly(rader):
    s = L.summer()
    r = by(rader, 2026)
    assert (r["timer_myndighetskontakt"], r["timer_rapportering"], r["timer_totalt"]) == (s["myndighetskontakt"], s["rapportering"], s["totalt"]) == (112, 175, 287)


def test_2026_matches_the_report_calendar_and_the_database(rader):
    r = by(rader, 2026)
    assert r["rapporter_levert"] == len(L.RAPPORTER)
    assert r["vernerunder_gjennomfort"] == next(x[5] for x in L.RAPPORTER if x[1] == "Vernerundeprotokoll")  # kvartalsvis
    c = sqlite3.connect(f"file:{(ROOT / '05_data' / 'museum.db').as_posix()}?mode=ro", uri=True)
    aktive = c.execute("SELECT COUNT(*) FROM utstillinger WHERE status = 'aktiv'").fetchone()[0]
    c.close()
    assert r["utstillinger_antall"] == aktive == 2


def test_the_numbers_have_a_pinned_fingerprint():
    assert hashlib.sha256(L.skjelett_tekst("T").encode("utf-8")).hexdigest() == FINGERAVTRYKK_TALL
    assert hashlib.sha256(L.skjelett_tekst("F").encode("utf-8")).hexdigest() == FINGERAVTRYKK_TEKST_SKJELETT


def test_generation_is_deterministic_and_has_no_hidden_state():
    assert L.skjelett_tekst("T") == L.skjelett_tekst("T")
    assert L.historikk_rader() == L.historikk_rader()
    a = L.historikk_rader()
    a[0]["besok_totalt"] = 1  # å endre en kopi skal ikke påvirke neste generering
    assert L.historikk_rader()[0]["besok_totalt"] == 21400


# ---------- Tallfilen (T) lages av koden og kan ikke endres ----------


def test_number_file_passes_its_own_check_with_no_warnings(tmp_path):
    p = L.skriv_historikk_tall(tmp_path)
    assert p.name == "historikk_tall.yaml"
    assert L.kontroller_tekst("T", p.read_text(encoding="utf-8")) == []
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert data["klassifisering"] == "syntetisk" and data["syntetisk"] is True and len(data["aar"]) == 17


TALL_MUT = [
    ("besøk endret", lambda d: d["aar"][5].update(besok_totalt=30501), "FAST_FELT_ENDRET"),
    ("resultat endret", lambda d: d["aar"][10].update(resultat_tkr=-419), "FAST_FELT_ENDRET"),
    ("timer 2026 endret", lambda d: d["aar"][16].update(timer_totalt=288), "FAST_FELT_ENDRET"),
    ("tema endret", lambda d: d["aar"][10].update(tema="vekst"), "FAST_FELT_ENDRET"),
    ("status endret", lambda d: d["aar"][16].update(status_ar="endelig"), "FAST_FELT_ENDRET"),
    ("årstall endret", lambda d: d["aar"][3].update(ar=2014), "FAST_FELT_ENDRET"),
    ("desimal blir heltall", lambda d: d["aar"][0].update(ansatte_arsverk=6), "FAST_FELT_ENDRET"),
    ("heltall blir tekst", lambda d: d["aar"][2].update(skoleelever="3600"), "FAST_FELT_ENDRET"),
    ("år fjernet", lambda d: d["aar"].pop(), "ANTALL"),
    ("år lagt til", lambda d: d["aar"].append(copy.deepcopy(d["aar"][0])), "ANTALL"),
    ("rekkefølge byttet", lambda d: d["aar"].reverse(), "FAST_FELT_ENDRET"),
    ("ukjent felt", lambda d: d["aar"][0].update(ekstra=1), "UKJENT_FELT"),
    ("felt mangler", lambda d: d["aar"][0].pop("besok_totalt"), "MANGLER"),
    ("header endret", lambda d: d.update(syntetisk=False), "FAST_FELT_ENDRET"),
    ("forklaring endret", lambda d: d["forklaring"].update(tkr="millioner kroner"), "FAST_FELT_ENDRET"),
]


@pytest.mark.parametrize("navn,endring,forventet", TALL_MUT, ids=[m[0] for m in TALL_MUT])
def test_any_change_to_the_number_file_is_caught(navn, endring, forventet):
    d = yaml.safe_load(L.skjelett_tekst("T"))
    endring(d)
    assert forventet in koder(L.kontroller_tekst("T", dump(d))), navn


def test_every_single_number_is_protected(rader):
    """Endrer hvert av de 595 tallene for seg. Kontrollen skal fange alle."""
    skel = L.skjelett("T")
    for i in range(len(rader)):
        for k, v in rader[i].items():
            d = copy.deepcopy(skel)
            d["aar"][i][k] = (v + 1) if isinstance(v, (int, float)) and not isinstance(v, bool) else f"{v}x"
            funn: list = []
            L._sammenlign(skel, d, "historikk_tall.yaml", "", funn, [])  # samme sammenligning som kontrollen bruker, uten YAML-runde
            assert [f.kode for f in funn] == ["FAST_FELT_ENDRET"], (rader[i]["ar"], k)


# ---------- Tekstfilen (F) ----------


def test_text_skeleton_has_one_entry_per_year_with_fixed_key_figures(rader):
    s = L.skjelett("F")["historikk"]
    assert [e["ar"] for e in s] == list(range(2010, 2027))
    for e, r in zip(s, rader):
        assert e["tema"] == r["tema"] and e["status_ar"] == r["status_ar"]
        assert e["nokkeltall"] == {k: r[k] for k in L.HISTORIKK_NOKKELTALL}
    assert L.skjelett_tekst("F").count(L.PLASSHOLDER) == 34


def test_raw_text_skeleton_is_rejected():
    assert "PLASSHOLDER" in koder(L.kontroller_tekst("F", L.skjelett_tekst("F")))


def test_reference_text_passes_and_changes_to_fixed_fields_are_caught():
    ref = fyll(L.skjelett("F"), Teller())
    assert koder(L.kontroller_tekst("F", dump(ref))) == set()
    for navn, endring, forventet in [
        ("nøkkeltall endret", lambda d: d["historikk"][4]["nokkeltall"].update(besok_totalt=1), "FAST_FELT_ENDRET"),
        ("tema endret", lambda d: d["historikk"][10].update(tema="rekordår"), "FAST_FELT_ENDRET"),
        ("år fjernet", lambda d: d["historikk"].pop(), "ANTALL"),
        ("årstall i tekst", lambda d: d["historikk"][9].update(hendelse="Året 2019 ble det største besøket noensinne for museet."), "TALL_I_TEKST"),
        ("samme tekst to år", lambda d: d["historikk"][3].update(hendelse=d["historikk"][2]["hendelse"]), "KOPIERT_TEKST"),
        ("laerdom mangler", lambda d: d["historikk"][0].pop("laerdom"), "MANGLER"),
        ("plassholder igjen", lambda d: d["historikk"][0].update(hendelse="TODO_FYLL (1 setning): noe"), "PLASSHOLDER"),
    ]:
        d = copy.deepcopy(ref)
        endring(d)
        assert forventet in koder(L.kontroller_tekst("F", dump(d))), navn


def test_text_file_never_contains_the_numbers_so_a_model_cannot_copy_them_wrongly():
    ref = fyll(L.skjelett("F"), Teller())
    for e in ref["historikk"]:
        assert not any(c.isdigit() for c in e["hendelse"] + e["laerdom"])


# ---------- Mappekontroll og installering ----------


def test_number_file_is_optional_in_a_delivery_but_must_be_exact_when_present(tmp_path):
    for k, f in L.FILER.items():
        (tmp_path / f).write_text(dump(fyll(L.skjelett(k), Teller())), encoding="utf-8")
    assert L.kontroller_mappe(tmp_path).ok and "T" not in L.kontroller_mappe(tmp_path).filer
    L.skriv_historikk_tall(tmp_path)
    assert L.kontroller_mappe(tmp_path).ok and L.kontroller_mappe(tmp_path).filer["T"] is True
    p = tmp_path / L.GENERERT_FIL["T"]
    p.write_text(p.read_text(encoding="utf-8").replace("besok_totalt: 21400", "besok_totalt: 21401"), encoding="utf-8")
    r = L.kontroller_mappe(tmp_path)
    assert not r.ok and r.filer["T"] is False


def test_install_of_the_number_file_works_without_a_delivery_but_refuses_an_altered_one(tmp_path):
    lev, mal = tmp_path / "lev", tmp_path / "data"
    lev.mkdir()
    ok, avvist = L.installer(lev, ["T"], mal)
    assert ok == ["T"] and avvist == [] and (mal / "historikk_tall.yaml").read_text(encoding="utf-8").strip() == L.skjelett_tekst("T").strip()
    ok2, avvist2 = L.installer(lev, ["T"], mal)  # finnes fra før
    assert ok2 == [] and "finnes allerede" in avvist2[0]
    L.skriv_historikk_tall(lev)
    f = lev / "historikk_tall.yaml"
    f.write_text(f.read_text(encoding="utf-8").replace("skoleelever: 3100", "skoleelever: 9999"), encoding="utf-8")
    ok3, avvist3 = L.installer(lev, ["T"], tmp_path / "data2")
    assert ok3 == [] and "består ikke kontrollen" in avvist3[0] and not (tmp_path / "data2").exists()


def test_cli_writes_the_number_file_and_installs_it(tmp_path, capsys):
    assert cli.main(["--lag-historikk-tall", "--til", str(tmp_path / "lev")]) == 0
    assert (tmp_path / "lev" / "historikk_tall.yaml").is_file() and "laget av koden" in capsys.readouterr().out
    assert cli.main([str(tmp_path / "lev"), "--installer", "T", "--mal", str(tmp_path / "data"), "--yes"]) == 0
    assert (tmp_path / "data" / "historikk_tall.yaml").is_file() and "Installert T: historikk_tall.yaml" in capsys.readouterr().out


# ---------- Datalaget kan lese filene uten kodeendring ----------


def test_data_layer_reads_the_history_with_the_year_in_the_path_and_keeps_it_for_leadership_only(tmp_path):
    base = tmp_path / "base"
    for spec in DEFAULT_SOURCES:
        (base / spec.path).parent.mkdir(parents=True, exist_ok=True)
        (base / spec.path).write_bytes((ROOT / spec.path).read_bytes())
    L.installer(tmp_path, ["T"], base / "05_data" / "governance")
    ledelse = frozenset({"museumsdirektor", "driftsansvarlig", "kvalitetsvokter"})
    ny = SourceSpec("05_data/governance/historikk_tall.yaml", "historikk", "syntetisk", ledelse, "yaml")
    uten_ny = tuple(s for s in DEFAULT_SOURCES if s.path != ny.path)
    d = InternData(base=base, sources=uten_ny + (ny,))
    aar = [f for f in d.findings if f.tema == "historikk" and f.sti.startswith("aar")]
    assert [f.sti for f in aar] == [f"aar › {y}" for y in range(2010, 2027)]
    assert "tema: pandemi og stengt" in next(f for f in aar if f.sti.endswith("2020")).tekst
    assert d.search("pandemi stengt besøk", "museumsvert", ("historikk",), bred=True) == []
    treff = d.search("pandemi stengt besøk", "museumsdirektor", ("historikk",), bred=True)
    assert treff and "2020" in treff[0][1].sti or any("2020" in f.sti for _, f in treff)
