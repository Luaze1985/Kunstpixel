"""Etappe 2 i spec datafinner-ledelse: «I dag» og «Driften denne uka».

B1/B2: rene funksjoner i core/ledelse.py (ingen database, fast idag).
B3/B4: verktøyene i core/driftsoversikt.py mot den ekte museum.db, med idag låst til 2026-11-16 (en stengt mandag).
D1: tall for dagen i dag og senere vises aldri som faktiske, selv om de syntetiske dataene går til 2026-12-31.
Sikkerhet: svarene har bare summer per stasjon/kategori, aldri ansatt-ID eller navn, og persondata i emnefelt skjules.
"""

from __future__ import annotations

import json
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from http.server import ThreadingHTTPServer

import pytest

from src.kunstpixel.core import driftsoversikt, ledelse

# ---------- B1/B2: rene funksjoner ----------


def test_normalt_er_snitt_av_samme_ukedag_de_siste_fire_aapne_ukene() -> None:
    serie = {"2026-11-08": 400, "2026-11-01": 420, "2026-10-25": 380, "2026-10-18": 440, "2026-10-11": 999}
    assert ledelse.normalt_for_ukedag(serie, "2026-11-15") == 410.0


def test_normalt_hopper_over_stengte_dager_og_ser_lenger_tilbake() -> None:
    serie = {"2026-11-08": None, "2026-11-01": 420, "2026-10-25": None, "2026-10-18": 440, "2026-10-11": 380, "2026-10-04": 400}
    assert ledelse.normalt_for_ukedag(serie, "2026-11-15") == 410.0


def test_normalt_er_ukjent_med_faerre_enn_to_sammenligningsdager() -> None:
    assert ledelse.normalt_for_ukedag({"2026-11-08": 400}, "2026-11-15") is None
    assert ledelse.normalt_for_ukedag({}, "2026-11-15") is None


@pytest.mark.parametrize("verdi,status", [
    (400, "Normal"),          # -2,4 %
    (360, "Normal"),          # -12,2 %
    (348.5, "Følg med"),      # -15 % (grensen er med)
    (300, "Følg med"),        # -26,8 %
    (287, "Over terskel"),    # -30 %
    (100, "Over terskel"),
    (600, "Normal"),          # flere besøk er bra for besøk
])
def test_status_for_besok_folger_tersklene(verdi: float, status: str) -> None:
    assert ledelse.vurder(verdi, 410.0, "besok")["status"] == status


def test_status_snur_naar_lavere_er_bra() -> None:
    assert ledelse.vurder(13, 10, "apne_driftsmeldinger")["status"] == "Over terskel"
    assert ledelse.vurder(5, 10, "apne_driftsmeldinger")["status"] == "Normal"


def test_ukjent_og_stengt_er_egne_statuser_aldri_normal() -> None:
    assert ledelse.vurder(None, 410.0, "besok")["status"] == "Ukjent"
    assert ledelse.vurder(400, None, "besok")["status"] == "Ukjent"
    assert ledelse.vurder(0, 410.0, "besok", aapent=False)["status"] == "Stengt"


def test_vurder_gir_endring_og_prosent() -> None:
    v = ledelse.vurder(391, 412.0, "besok")
    assert v == {"verdi": 391, "normalt": 412.0, "endring": -21.0, "endring_pst": -5.1, "status": "Normal"}


def test_tersklene_ligger_ett_sted() -> None:
    besok = ledelse.TERSKLER["besok"]
    assert besok == {"lavere_er_bra": False, "folg_med": 0.15, "over_terskel": 0.30}


def test_kutt_fremtid_tar_bort_i_dag_og_senere() -> None:
    rader = [{"dato": "2026-11-15"}, {"dato": "2026-11-16"}, {"dato": "2026-12-31"}]
    assert ledelse.kutt_fremtid(rader, "2026-11-16") == [{"dato": "2026-11-15"}]


def test_fyll_dager_setter_inn_dager_uten_rader() -> None:
    ut = ledelse.fyll_dager([{"dato": "2026-11-10", "besok": 5}], "2026-11-09", "2026-11-11")
    assert ut == [{"dato": "2026-11-09", "mangler": True}, {"dato": "2026-11-10", "besok": 5},
                  {"dato": "2026-11-11", "mangler": True}]


# ---------- B3: get_today_overview ----------

IDAG = date(2026, 11, 16)  # mandag, museet er stengt
STATUSER = {"Normal", "Følg med", "Over terskel", "Ukjent", "Stengt"}


@pytest.fixture()
def idag(monkeypatch: pytest.MonkeyPatch) -> date:
    monkeypatch.setattr(driftsoversikt, "_idag", lambda: IDAG)
    return IDAG


def test_i_dag_paa_stengt_mandag_viser_stengt_og_sist_hele_dag(idag: date) -> None:
    d = driftsoversikt.get_today_overview("2026-11-16")
    assert d["dato"] == "2026-11-16"
    assert d["aapent_i_dag"] is False
    besok = d["besok"]
    assert besok["dato"] == "2026-11-15"  # søndag, siste hele åpne dag
    assert besok["verdi"] == 391
    assert besok["status"] in STATUSER - {"Stengt"}
    assert besok["normalt"] is not None
    assert re.fullmatch(r"\d{2}:\d{2}", d["hentet_kl"])


def test_i_dag_viser_aldri_besok_for_i_dag_eller_senere(idag: date) -> None:
    d = driftsoversikt.get_today_overview("2026-11-16")
    assert all(r["dato"] < "2026-11-16" for r in d["besok"]["rader"])


def test_i_dag_har_vakter_per_stasjon_og_arrangementer(idag: date) -> None:
    d = driftsoversikt.get_today_overview("2026-11-14")
    assert d["aapent_i_dag"] is True
    stasjoner = {r["stasjon"] for r in d["vakter"]["rader"]}
    assert "Museumskafé" in stasjoner
    assert d["vakter"]["verdi"] == sum(r["vakter"] for r in d["vakter"]["rader"])
    assert d["vakter"]["rapport"] == {"sporsmal_id": "vaktplan", "args": {"dato": "2026-11-14"}}
    assert [r["tittel"] for r in d["arrangementer"]["rader"]] == ["Helgeverksted: Farger og form"]


def test_i_dag_skiller_nye_og_gamle_aapne_driftsmeldinger(idag: date) -> None:
    d = driftsoversikt.get_today_overview("2026-11-16")
    nye, eldre = d["driftsmeldinger"], d["driftsmeldinger_eldre"]
    assert nye["verdi"] == 15  # åpne fra 2026-10-17 til og med 2026-11-15
    assert nye["verdi"] == sum(r["antall"] for r in nye["rader"])
    assert eldre["verdi"] > 100  # gamle saker som aldri ble lukket, vises for seg


def test_i_dag_driftsmeldinger_er_bare_antall_per_kategori(idag: date) -> None:
    """Lars 2026-11-16: Hjem viser ikke emnetekst, bare antall per kategori (og hvor mange som er kritiske)."""
    rader = driftsoversikt.get_today_overview("2026-11-16")["driftsmeldinger"]["rader"]
    assert rader and all(set(r) == {"kategori", "antall", "kritiske"} for r in rader)
    assert len({r["kategori"] for r in rader}) == len(rader)


def test_i_dag_har_hms_avvik_siste_sju_dager(idag: date) -> None:
    d = driftsoversikt.get_today_overview("2026-11-16")
    assert d["hms_avvik"]["verdi"] == 1  # 2026-11-10, SIKKERHET
    assert d["hms_avvik"]["rader"][0]["dato"] == "2026-11-10"


def test_i_dag_lekker_ikke_ansatte_eller_persondata(idag: date) -> None:
    for dato in ("2026-11-14", "2026-11-16"):
        tekst = json.dumps(driftsoversikt.get_today_overview(dato), ensure_ascii=False)
        assert "KP-ANS" not in tekst and "KP-INN" not in tekst and "ansatt_id" not in tekst
        assert '"emne"' not in tekst and "meldingstekst" not in tekst and "inneholder_persondata" not in tekst


@pytest.mark.parametrize("dato", ["2026-11-17", "2027-01-01"])
def test_i_dag_avviser_datoer_i_fremtiden(idag: date, dato: str) -> None:
    with pytest.raises(ValueError, match="fremtiden"):
        driftsoversikt.get_today_overview(dato)


@pytest.mark.parametrize("dato", ["", "16.11.2026", "2026-13-01", "x' OR 1=1 --"])
def test_i_dag_avviser_ugyldig_dato(idag: date, dato: str) -> None:
    with pytest.raises(ValueError):
        driftsoversikt.get_today_overview(dato)


# ---------- B4: get_week_overview ----------


def test_uka_har_sju_dager_mot_forrige_uke_og_i_fjor(idag: date) -> None:
    d = driftsoversikt.get_week_overview("2026-11-14")
    assert d["uke"] == 46 and d["fra"] == "2026-11-09" and d["til"] == "2026-11-15"
    assert [x["dato"] for x in d["dager"]] == [f"2026-11-{n:02d}" for n in range(9, 16)]
    mandag = d["dager"][0]
    assert mandag["aapent"] is False and mandag["besok"] == 0
    assert d["besok"]["verdi"] == 210 + 194 + 234 + 285 + 436 + 391
    assert d["besok"]["forrige_uke"] is not None and d["besok"]["i_fjor"] is not None
    assert d["besok"]["status"] in STATUSER


def test_uka_viser_ikke_dager_fra_i_dag_og_utover(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(driftsoversikt, "_idag", lambda: date(2026, 11, 12))
    d = driftsoversikt.get_week_overview("2026-11-11")
    kommende = [x for x in d["dager"] if x["dato"] >= "2026-11-12"]
    assert kommende and all(x["besok"] is None and x["kommer"] for x in kommende)
    assert d["besok"]["verdi"] == 210 + 194


def test_uka_uten_hele_dager_viser_forrige_uke(idag: date) -> None:
    """Mandag 2026-11-16: uke 47 har ingen hele dager ennå. Da vises uke 46, med merknad."""
    d = driftsoversikt.get_week_overview("2026-11-16")
    assert d["uke"] == 46 and d["viser_forrige_uke"] is True
    assert "forrige uke" in d["merknad"].lower()
    assert d["besok"]["verdi"] == 1750
    assert driftsoversikt.get_week_overview("2026-11-14")["viser_forrige_uke"] is False


def test_uka_sier_mangler_data_der_kildene_stopper(idag: date) -> None:
    d = driftsoversikt.get_week_overview("2026-11-14")  # tilfredshet, anmeldelser og kafé stopper 2026-10-29
    assert d["tilfredshet"]["verdi"] is None and d["tilfredshet"]["status"] == "Ukjent"
    assert d["lave_anmeldelser"]["verdi"] is None
    assert d["kafe_per_besok"]["verdi"] is None


def test_uka_har_tall_der_kildene_dekker_perioden(idag: date) -> None:
    d = driftsoversikt.get_week_overview("2026-10-21")  # uke 43, før datahullet
    assert d["tilfredshet"]["verdi"] is not None
    assert d["lave_anmeldelser"]["verdi"] is not None
    assert d["kafe_per_besok"]["verdi"] is not None and d["kafe_per_besok"]["verdi"] > 0


def test_uka_teller_driftsmeldinger_aapnet_og_lukket(idag: date) -> None:
    d = driftsoversikt.get_week_overview("2026-11-14")
    assert d["driftsmeldinger"]["aapnet"] == 9  # 2026-11-13 (1) og 2026-11-14 (8)
    assert isinstance(d["driftsmeldinger"]["lukket"], int)
    assert d["hms_avvik"]["aapnet"] == 1


def test_uka_lekker_ikke_ansatte(idag: date) -> None:
    tekst = json.dumps(driftsoversikt.get_week_overview("2026-11-14"), ensure_ascii=False)
    assert "KP-ANS" not in tekst and "ansatt_id" not in tekst


def test_uka_avviser_fremtid(idag: date) -> None:
    with pytest.raises(ValueError, match="fremtiden"):
        driftsoversikt.get_week_overview("2026-11-20")


# ---------- Hvitelisten og API ----------


def test_verktoyene_er_hvitelistet_med_bare_dato() -> None:
    from src.kunstpixel.adapters.datafinner import VERKTOY

    assert VERKTOY["get_today_overview"][1] == {"dato"}
    assert VERKTOY["get_week_overview"][1] == {"dato"}


@pytest.fixture()
def server_url():
    from src.kunstpixel.adapters.datafinner import DatafinnerHandler

    server = ThreadingHTTPServer(("127.0.0.1", 0), DatafinnerHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _kall(base: str, navn: str, args: dict) -> tuple[int, dict]:
    url = f"{base}/api/verktoy?navn={navn}&args={urllib.parse.quote(json.dumps(args))}"
    try:
        with urllib.request.urlopen(url) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_api_gir_400_for_ugyldig_og_fremtidig_dato(server_url: str) -> None:
    assert _kall(server_url, "get_today_overview", {"dato": "x' OR 1=1"})[0] == 400
    assert _kall(server_url, "get_week_overview", {"dato": "2999-01-01"})[0] == 400
    assert _kall(server_url, "get_today_overview", {"dato": "2026-11-14", "ansatt_id": "KP-ANS-001"})[0] == 400


def test_api_svarer_for_en_dag_i_fortiden(server_url: str) -> None:
    status, d = _kall(server_url, "get_today_overview", {"dato": "2026-11-14"})
    assert status == 200 and d["resultat"]["dato"] == "2026-11-14"
