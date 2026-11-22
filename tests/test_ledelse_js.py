"""ledelse.js (F2/F4): rene visningsfunksjoner uten DOM, testet i Node. Hoppes over hvis Node mangler."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDELSE_JS = ROOT / "src" / "kunstpixel" / "adapters" / "datafinner" / "ledelse.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")


def js(uttrykk: str):
    """Kjør ett uttrykk mot ledelse.js og returner svaret som JSON."""
    kode = f"const L=require({json.dumps(str(LEDELSE_JS))});process.stdout.write(JSON.stringify({uttrykk}));"
    ut = subprocess.run([NODE, "-e", kode], capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(ut.stdout)


@pytest.mark.parametrize("status,tekst,klasse", [
    ("Normal", "Normal", "go"),
    ("Følg med", "Følg med", "check"),
    ("Over terskel", "Over terskel", "stop"),
    ("Ukjent", "Mangler data", ""),
    ("Stengt", "Stengt", ""),
    (None, "Mangler data", ""),
    ("noe rart", "Mangler data", ""),
])
def test_status_gir_ord_og_form(status, tekst: str, klasse: str) -> None:
    assert js(f"L.statusVisning({json.dumps(status)})") == {"tekst": tekst, "klasse": klasse}


def test_ukjent_er_aldri_gronn() -> None:
    assert js('L.statusVisning("Ukjent").klasse') != "go"


@pytest.mark.parametrize("normalt,pst,forventet", [
    (412.3, -5.1, "Normalt 412 · −5,1 %"),
    (410, 6, "Normalt 410 · +6 %"),
    (410, 0, "Normalt 410 · 0 %"),
    (None, None, "Ingen sammenligning"),
])
def test_normalt_tekst(normalt, pst, forventet: str) -> None:
    assert js(f"L.normaltTekst({json.dumps(normalt)}, {json.dumps(pst)})") == forventet


def test_tall_per() -> None:
    assert js('L.tallPer("09:14")') == "Tall per kl. 09:14"
    assert js("L.tallPer(null)") == ""


def test_dato_kort() -> None:
    assert js('L.datoKort("2026-11-15")') == "søndag 15.11."
    assert js('L.datoKort("2026-11-16")') == "mandag 16.11."


@pytest.mark.parametrize("felt,etikett", [
    ("maaned", "Måned"), ("maned", "Måned"), ("formal", "Formål"), ("aar", "År"), ("ar", "År"),
    ("besok_totalt", "Besøk totalt"), ("ukedag_navn", "Ukedag"), ("kategori", "Kategori"),
    ("hastegrad", "Hastegrad"), ("mottaker_rolle", "Mottaker"), ("er_aapent", "Åpent"),
])
def test_etiketter_med_aeoeaa(felt: str, etikett: str) -> None:
    assert js(f"L.etikett({json.dumps(felt)})") == etikett


@pytest.mark.parametrize("felt,etikett", [
    ("besok_uka", "Besøk i uka"),
    ("endring_forrige_uke_pst", "Endring mot forrige uke (%)"),
    ("endring_i_fjor_pst", "Endring mot i fjor (%)"),
    ("driftsmeldinger_aapnet", "Driftsmeldinger åpnet"),
])
def test_etiketter_for_ukerapporten(felt: str, etikett: str) -> None:
    assert js(f"L.etikett({json.dumps(felt)})") == etikett


@pytest.mark.parametrize("verdi,tekst", [
    ("klima_og_samling", "Klima og samling"),
    ("kafe_og_allergen", "Kafé og allergen"),
    ("hms_og_sikkerhet", "HMS og sikkerhet"),
    ("SIKKERHET", "SIKKERHET"),
])
def test_kategorinavn_uten_understrek(verdi: str, tekst: str) -> None:
    assert js(f"L.kategoriTekst({json.dumps(verdi)})") == tekst


def test_ja_nei() -> None:
    assert js("[L.jaNei(true), L.jaNei(false)]") == ["Ja", "Nei"]


# ---------- F6: «Fulgt opp» i nettleseren (falsk lagring) ----------

FALSK = "(function(){var d={};return {getItem:function(k){return k in d?d[k]:null},setItem:function(k,v){d[k]=String(v)}}})()"
KAPUTT = "{getItem:function(){throw new Error('blokkert')},setItem:function(){throw new Error('blokkert')}}"


def test_tom_lagring_gir_ingen_oppfolging() -> None:
    assert js(f"L.lesOppfolging({FALSK})") == {}


def test_merk_og_angre_fulgt_opp() -> None:
    ut = js(f"(function(){{var s={FALSK};L.merkFulgtOpp(s,'innlan:LAN-1:2026-03-01','2026-11-16T10:00');"
            f"var a=L.erFulgtOpp(L.lesOppfolging(s),'innlan:LAN-1:2026-03-01');L.angreFulgtOpp(s,'innlan:LAN-1:2026-03-01');"
            f"return [a,L.erFulgtOpp(L.lesOppfolging(s),'innlan:LAN-1:2026-03-01'),JSON.parse(s.getItem('kunstpixel.oppfolging.v1'))]}})()")
    assert ut == [True, False, {}]


def test_blokkert_lagring_velter_ikke_siden() -> None:
    assert js(f"(function(){{var s={KAPUTT};L.merkFulgtOpp(s,'x','t');return L.lesOppfolging(s)}})()") == {}


def test_grupper_flytter_fulgt_opp_til_egen_gruppe() -> None:
    frister = [{"id": "a", "gruppe": "Forfalt"}, {"id": "b", "gruppe": "Senere"}, {"id": "c", "gruppe": "I dag"}]
    ut = js(f"L.grupper({json.dumps(frister)}, {{b: {{tid: 't'}}}})")
    assert [x["id"] for x in ut["Forfalt"]] == ["a"]
    assert ut["Senere"] == [] and [x["id"] for x in ut["Fulgt opp"]] == ["b"]
    assert list(ut) == ["Forfalt", "I dag", "Denne uka", "Senere", "Fulgt opp"]



# ---------- Hjem → Oversikt (Lars 2026-11-17: «pass på støyen»): vis det som krever oppmerksomhet, resten bak ett klikk ----------

def test_del_avvik_viser_bare_det_som_krever_oppmerksomhet() -> None:
    d = {
        "besok": {"status": "Normal", "verdi": 391},
        "vakter": {"verdi": 10},
        "arrangementer": {"verdi": 0},
        "driftsmeldinger": {"verdi": 15},
        "hms_avvik": {"verdi": 1},
        "driftsmeldinger_eldre": {"verdi": 198},
    }
    nokler = ["besok", "vakter", "arrangementer", "driftsmeldinger", "hms_avvik", "driftsmeldinger_eldre"]
    ut = js(f"L.delAvvik({json.dumps(d)}, {json.dumps(nokler)})")
    assert ut == {"avvik": ["driftsmeldinger", "hms_avvik"], "resten": ["besok", "vakter", "arrangementer", "driftsmeldinger_eldre"]}


@pytest.mark.parametrize("status", ["Følg med", "Over terskel", "Ukjent"])
def test_del_avvik_loefter_status_som_ikke_er_normal(status: str) -> None:
    ut = js(f"L.delAvvik({{besok: {{status: {json.dumps(status)}, verdi: null}}}}, ['besok'])")
    assert ut == {"avvik": ["besok"], "resten": []}


def test_del_avvik_null_hms_avvik_er_ikke_avvik_og_manglende_hoppes_over() -> None:
    ut = js("L.delAvvik({hms_avvik: {verdi: 0}}, ['hms_avvik', 'vakter'])")
    assert ut == {"avvik": [], "resten": ["hms_avvik"]}


# ---------- 3b: e-postutkast (F7), «Mine oppfølginger» (F9) og «Godta» (F8). Bare i nettleseren. ----------

def test_mailto_koder_emne_og_tekst() -> None:
    ut = js('L.mailto({overskrift: "Oppfølging: A & B", tekst: "Hei\\nLinje 2"})')
    assert ut == "mailto:?subject=Oppf%C3%B8lging%3A%20A%20%26%20B&body=Hei%0D%0ALinje%202"


def test_mailto_uten_utkast_gir_null() -> None:
    assert js("L.mailto(null)") is None


def _med_lager(kropp: str) -> str:
    return f"(function(){{var s={FALSK};{kropp}}})()"


def test_legg_til_og_les_oppfolging() -> None:
    ut = js(_med_lager("var o=L.leggTilOppfolging(s,{tittel:'Vaktplan',type:'avvik',adresse:'rolle:X/vaktplan',kilde:'get_staff_on_shift'},'2026-11-17T10:00');"
                       "return [o.id.length>0, L.lesOppfolginger(s)]"))
    assert ut[0] is True
    o = ut[1][0]
    assert {k: o[k] for k in ("tittel", "type", "adresse", "kilde", "opprettet", "lukket")} == {
        "tittel": "Vaktplan", "type": "avvik", "adresse": "rolle:X/vaktplan", "kilde": "get_staff_on_shift",
        "opprettet": "2026-11-17T10:00", "lukket": None}


def test_samme_aapne_oppfolging_legges_ikke_inn_to_ganger() -> None:
    ut = js(_med_lager("var a={tittel:'T',type:'oppfolging',adresse:'x'};L.leggTilOppfolging(s,a,'t1');L.leggTilOppfolging(s,a,'t2');"
                       "return L.lesOppfolginger(s).length"))
    assert ut == 1


def test_lukk_og_gjenaapne_oppfolging() -> None:
    ut = js(_med_lager("var o=L.leggTilOppfolging(s,{tittel:'T',type:'oppfolging',adresse:'x'},'t1');L.lukkOppfolging(s,o.id,'t2');"
                       "var a=L.lesOppfolginger(s)[0].lukket;L.gjenaapneOppfolging(s,o.id);return [a,L.lesOppfolginger(s)[0].lukket]"))
    assert ut == ["t2", None]


def test_ugyldig_type_og_lang_tittel_vaskes() -> None:
    ut = js(_med_lager("L.leggTilOppfolging(s,{tittel:'x'.repeat(500),type:'<script>',adresse:'x'},'t');var o=L.lesOppfolginger(s)[0];"
                       "return [o.tittel.length,o.type]"))
    assert ut == [200, "oppfolging"]


def test_odelagt_lagring_gir_tom_liste() -> None:
    assert js("L.lesOppfolginger({getItem:function(){return '{ikke json'}})") == []
    assert js("L.lesOppfolginger({getItem:function(){return '{\"a\":1}'}})") == []
    assert js(f"(function(){{var s={KAPUTT};L.leggTilOppfolging(s,{{tittel:'T',type:'avvik',adresse:'x'}},'t');return L.lesOppfolginger(s)}})()") == []


def test_godta_huskes_per_adresse_og_kan_angres() -> None:
    ut = js(_med_lager("L.godta(s,'rolle:X/vaktplan?dato=2026-11-14','Vaktplan','t');var a=L.erGodkjent(L.lesOppfolginger(s),'rolle:X/vaktplan?dato=2026-11-14');"
                       "var b=L.erGodkjent(L.lesOppfolginger(s),'rolle:X/vaktplan?dato=2026-11-13');L.angreGodta(s,'rolle:X/vaktplan?dato=2026-11-14');"
                       "return [a,b,L.erGodkjent(L.lesOppfolginger(s),'rolle:X/vaktplan?dato=2026-11-14')]"))
    assert ut == [True, False, False]


def test_godkjent_er_ikke_en_aapen_oppfolging() -> None:
    ut = js(_med_lager("L.godta(s,'a','Rapport A','t1');L.leggTilOppfolging(s,{tittel:'B',type:'avvik',adresse:'b'},'t2');"
                       "L.leggTilOppfolging(s,{tittel:'C',type:'oppfolging',adresse:'c'},'t3');"
                       "return L.nyesteAapne(L.lesOppfolginger(s),5).map(function(o){return o.tittel})"))
    assert ut == ["C", "B"]


def test_csv_har_overskrift_semikolon_og_sitater() -> None:
    liste = [{"tittel": 'Si "hei"; nå', "type": "avvik", "adresse": "x", "kilde": "db", "opprettet": "t1", "lukket": None}]
    ut = js(f"L.oppfolgingCsv({json.dumps(liste)})")
    linjer = ut.lstrip("﻿").split("\r\n")
    assert linjer[0] == '"Tittel";"Type";"Status";"Opprettet";"Lukket";"Kilde";"Adresse"'
    assert linjer[1] == '"Si ""hei""; nå";"Avvik";"Åpen";"t1";"";"db";"x"'


@pytest.mark.parametrize("farlig", ["=HYPERLINK(\"x\")", "+1", "-1", "@SUM(A1)"])
def test_csv_noeytraliserer_formler(farlig: str) -> None:
    """CSV-injeksjon: en celle som starter med = + - @ skal ikke bli en formel i Excel."""
    liste = [{"tittel": farlig, "type": "oppfolging", "adresse": "x", "kilde": "", "opprettet": "t", "lukket": "t2"}]
    celle = js(f"L.oppfolgingCsv({json.dumps(liste)})").split("\r\n")[1].split(";")[0]
    assert celle.startswith("\"'")


@pytest.mark.parametrize("dager,tekst", [(-260, "260 dager over fristen"), (-1, "1 dag over fristen"),
                                          (0, "I dag"), (1, "Om 1 dag"), (14, "Om 14 dager")])
def test_frist_tekst(dager: int, tekst: str) -> None:
    assert js(f"L.fristTekst({dager})") == tekst


# ---------- Brukervennlighet (Lars 2026-11-18): lesbar Fasit, hjelpetekst, uketabell, tabellsøk og skjulte innlånsfrister ----------

def test_verktoy_tekst_uten_json() -> None:
    assert js('L.verktoyTekst("get_week_overview", {"dato": "2026-11-18"})') == "get_week_overview(dato 2026-11-18)"
    assert js('L.verktoyTekst("get_absence_report", {"aar": 2025, "kvartal": 2})') == "get_absence_report(år 2025, kvartal 2)"
    assert js('L.verktoyTekst("list_roles", null)') == "list_roles()"
    assert js('L.verktoyTekst(null, null)') == "Ingen ennå"


def test_regel_tekst_med_etikett_og_tegn() -> None:
    assert js('L.regelTekst("R-UKE-01", "endring_forrige_uke_pst", ">=", -15)') == "R-UKE-01: Endring mot forrige uke (%) ≥ −15"
    assert js('L.regelTekst("R-FRAV-01", "egen_prosent", "<=", 7)') == "R-FRAV-01: Egen prosent ≤ 7"
    assert js('L.regelTekst("R-X", "antall", ">", 3)') == "R-X: Antall > 3"
    assert js('L.regelTekst(null, "antall", ">", 3)') is None


@pytest.mark.parametrize("hjelp,type_,forventet", [
    ("En dag i uka, ISO-format 'YYYY-MM-DD'. Kan ikke være etter i dag.", "date", "En dag i uka. Kan ikke være etter i dag."),
    ("Dato i ISO-format 'YYYY-MM-DD'. Standard er i dag.", "date", "Standard er i dag."),
    ("Dagens dato i ISO-format 'YYYY-MM-DD'. Kan ikke være etter i dag.", "date", "Kan ikke være etter i dag."),
    ("Fra og med dato (ISO-format YYYY-MM-DD). Standard er dagens dato.", "date", "Fra og med dato. Standard er dagens dato."),
    ("Måned på formen YYYY-MM.", "month", ""),
    ("Måned i formatet 'YYYY-MM'.", "month", ""),  # ekte tekst fra verktøyskjemaet
    ("Eksakt dato (YYYY-MM-DD).", "date", ""),
    ("Dato i ISO-format 'YYYY-MM-DD'.", "text", "Dato i ISO-format 'YYYY-MM-DD'."),  # tekstfelt trenger formatet
    ("Søkeord i tittel.", "text", "Søkeord i tittel."),
])
def test_hjelp_tekst_uten_iso_for_datovelger(hjelp: str, type_: str, forventet: str) -> None:
    assert js(f"L.hjelpTekst({json.dumps(hjelp)}, {json.dumps(type_)})") == forventet


def test_uke_rader_uten_dager_som_kommer_og_stengt_som_ord() -> None:
    rader = [
        {"dato": "2026-11-16", "ukedag": "mandag", "besok": 0, "forrige_uke": 0, "i_fjor": 0, "aapent": False, "kommer": False},
        {"dato": "2026-11-17", "ukedag": "tirsdag", "besok": 204, "forrige_uke": 210, "i_fjor": 218, "aapent": True, "kommer": False},
        {"dato": "2026-11-18", "ukedag": "onsdag", "besok": None, "forrige_uke": None, "i_fjor": None, "aapent": True, "kommer": True},
    ]
    ut = js(f"L.ukeRader({json.dumps(rader)})")
    assert [r["dato"] for r in ut] == ["2026-11-16", "2026-11-17"]
    assert ut[0]["besok"] == "Stengt" and ut[1]["besok"] == 204
    assert rader[0]["besok"] == 0  # originalen er urørt


def test_uke_rader_lar_andre_lister_vaere() -> None:
    rader = [{"navn": "Anja", "besok": 0, "aapent": False}]
    assert js(f"L.ukeRader({json.dumps(rader)})") == rader


def test_innlansfrister_vises() -> None:
    # Lars 2026-11-22: regelen «retur når utstillingen slutter» er godkjent. U6 er opphevet, ingen frister skjules.
    frister = [{"type": "innlan", "id": "a"}, {"type": "driftsmelding", "id": "b"}, {"type": "rapport", "id": "c"}]
    ut = js(f"L.skjulFrister({json.dumps(frister)})")
    assert [f["id"] for f in ut["frister"]] == ["a", "b", "c"]
    assert ut["skjult"] == 0
    assert js("L.skjulFrister(null)") == {"frister": [], "skjult": 0}


def test_filtrer_tabeller_paa_navn_og_kolonne() -> None:
    tabeller = [{"navn": "dagsbesok", "kolonner": ["dato", "besok_totalt"]},
                {"navn": "hr_ansatte", "kolonner": ["navn", "stilling"]},
                {"navn": "besok_tilfredshet", "kolonner": ["dato", "score_totalt"]}]
    navn = lambda sok: [t["navn"] for t in js(f"L.filtrerTabeller({json.dumps(tabeller)}, {json.dumps(sok)})")]
    assert navn("besok") == ["dagsbesok", "besok_tilfredshet"]
    assert navn("BESØK") == ["dagsbesok", "besok_tilfredshet"]  # ø = o, store bokstaver
    assert navn("hr ansatte") == ["hr_ansatte"]  # mellomrom = understrek
    assert navn("stilling") == ["hr_ansatte"]  # treff i kolonnenavn
    assert navn("") == ["dagsbesok", "hr_ansatte", "besok_tilfredshet"]
    assert navn("finnes_ikke") == []
