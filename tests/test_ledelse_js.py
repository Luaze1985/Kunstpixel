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


@pytest.mark.parametrize("dager,tekst", [(-260, "260 dager over fristen"), (-1, "1 dag over fristen"),
                                          (0, "I dag"), (1, "Om 1 dag"), (14, "Om 14 dager")])
def test_frist_tekst(dager: int, tekst: str) -> None:
    assert js(f"L.fristTekst({dager})") == tekst
