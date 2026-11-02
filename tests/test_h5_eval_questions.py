"""Deterministisk gull-testsuite for de 20 prøvespørsmålene i H5-spesifikasjonen (0 tokens).

Kilde: 01_inbox/h5_forslag_syntetisk_fyll.md (spørsmål 1–20).
- Spørsmål 1–14: Skal dekkes med eksakte tall, roller, kilder og rutiner fra H5-dataene.
- Spørsmål 15–20: Ikke dekket av databasen — verifiserer at systemet ikke inneholder eller lekker
  oppdiktede telefonnumre, tilsynsrapporter, personlig tidsbruk eller fremtidige tilskuddstall,
  samt at tilgangsgrenser håndheves i åpne kall (Datafinner).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import db, mcp_server

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOV_DIR = PROJECT_ROOT / "05_data" / "governance"


# -----------------------------------------------------------------------------
# DEL 1: DE 14 DEKKEDE SPØRSMÅLENE (EKSKLUSIV FASIT FRA H5-DATAENE)
# -----------------------------------------------------------------------------

def test_spm_01_hvem_har_kontakten_med_mattilsynet() -> None:
    """1. Hvem har kontakten med Mattilsynet?"""
    res = mcp_server.search_myndighet(query="Mattilsynet")
    assert res["antall"] == 1
    rad = res["myndigheter"][0]
    assert rad["id"] == "MK-02"
    assert rad["myndighet"] == "Mattilsynet"
    assert rad["intern_eier"] == "Kafeansvarlig"
    assert rad["kontaktperson"] == "[SKJERMET]"  # Standard er skjermet


def test_spm_02_hva_gjor_vi_forste_dagen_etter_varsel_om_tilsyn() -> None:
    """2. Hva gjør vi første dagen etter varsel om tilsyn?"""
    res = mcp_server.get_inspection_routine()
    steg1 = next(s for s in res["steg"] if s["steg_nr"] == 1)
    assert steg1["navn"] == "Varsel kommer"
    assert steg1["ansvarlig"] == "Driftsansvarlig"
    assert "kvalitetssystemet" in steg1["handling"]
    assert "saksmappe" in steg1["dokumentasjon"]


def test_spm_03_hva_trenger_arbeidstilsynet_av_dokumentasjon() -> None:
    """3. Hva trenger Arbeidstilsynet av dokumentasjon?"""
    res = mcp_server.search_myndighet(query="Arbeidstilsynet")
    assert res["antall"] == 1
    rad = res["myndigheter"][0]
    assert rad["id"] == "MK-01"
    assert "risikovurdering" in rad["dokumentasjon"].lower()
    assert "avvikslogger" in rad["dokumentasjon"].lower()
    assert "arbeidsmiljøutvalget" in rad["dokumentasjon"].lower()


def test_spm_04_hvem_er_kontaktpunkt_mot_kulturdirektoratet() -> None:
    """4. Hvem er kontaktpunkt mot Kulturdirektoratet?"""
    res = mcp_server.search_myndighet(query="Kulturdirektoratet")
    assert res["antall"] == 1
    rad = res["myndigheter"][0]
    assert rad["id"] == "MK-06"
    assert rad["intern_eier"] == "Museumsdirektør"


def test_spm_05_hvilken_rapport_skal_leveres_i_mars() -> None:
    """5. Hvilken rapport skal leveres i mars?"""
    res = mcp_server.search_rapportering(maned="Mars")
    ids = {r["id"] for r in res["rapporter"]}
    navn = {r["rapport"] for r in res["rapporter"]}
    assert {"RP-02", "RP-03", "RP-10"} <= ids
    assert "Besøkstall og statistikk" in navn
    assert "Tilskuddsrapport" in navn
    assert "Brannøvelsesrapport" in navn


def test_spm_06_hvem_godkjenner_rapporter_for_de_sendes_ut() -> None:
    """6. Hvem godkjenner rapporter før de sendes ut?"""
    res = mcp_server.search_rapportering(mottakertype="ekstern")
    assert res["antall"] == 3
    for r in res["rapporter"]:
        assert r["godkjenning"] == "eier"


def test_spm_07_hvilke_datakilder_bruker_driftsrapporten() -> None:
    """7. Hvilke datakilder bruker driftsrapporten?"""
    kal = mcp_server.search_rapportering()
    rp01 = next(r for r in kal["rapporter"] if r["id"] == "RP-01")
    assert set(rp01["kilder"]) == {"driftslogg", "avviksregister"}

    mal = mcp_server.search_rapportering(mal_id="ML-01")
    ml01 = mal["maler"][0]
    assert ml01["mal_navn"] == "Driftsrapport"
    alle_kilder = {k for felt in ml01["felt"] for k in felt["kilde"]}
    assert alle_kilder == {"driftslogg", "avviksregister", "hendelser"}


def test_spm_08_hva_skal_sta_i_en_avviksrapport() -> None:
    """8. Hva skal stå i en avviksrapport?"""
    mal = mcp_server.search_rapportering(mal_id="ML-02")
    assert mal["antall"] == 1
    ml02 = mal["maler"][0]
    assert ml02["mal_navn"] == "Avviksrapport"
    feltnavn = [f["felt_navn"] for f in ml02["felt"]]
    assert feltnavn == [
        "Hva skjedde",
        "Når og hvor",
        "Alvorlighetsgrad",
        "Umiddelbart tiltak",
        "Varig tiltak",
        "Frist for lukking",
    ]


def test_spm_09_hvem_skriver_styrerapporten() -> None:
    """9. Hvem skriver styrerapporten?"""
    kal = mcp_server.search_rapportering()
    rp12 = next(r for r in kal["rapporter"] if r["id"] == "RP-12")
    assert rp12["rapport"] == "Styrerapport"
    assert rp12["mottaker"] == "Styret"
    assert rp12["eier"] == "Museumsdirektør"


def test_spm_10_hvilke_rapporter_gar_til_eksterne_mottakere() -> None:
    """10. Hvilke rapporter går til eksterne mottakere?"""
    res = mcp_server.search_rapportering(mottakertype="ekstern")
    assert res["antall"] == 3
    mottakere = {r["id"]: (r["rapport"], r["mottaker"]) for r in res["rapporter"]}
    assert mottakere == {
        "RP-02": ("Besøkstall og statistikk", "Kulturdirektoratet"),
        "RP-03": ("Tilskuddsrapport", "Kulturdirektoratet"),
        "RP-04": ("Årsregnskap og årsberetning", "Stiftelsestilsynet"),
    }


def test_spm_11_hvor_mange_timer_bruker_vi_pa_tilskuddsrapportering_ledelse() -> None:
    """11. Hvor mange timer bruker vi på tilskuddsrapportering? (ledelse)"""
    res = mcp_server.search_arbeidsoppgaver(omrade="Rapportering")
    oppg = next(o for o in res["oppgaver"] if o["rapport_id"] == "RP-03")
    assert oppg["id"] == "AO-10"
    assert oppg["oppgave"] == "Tilskuddsrapport"
    assert oppg["timer_per_ar"] == 36
    assert oppg["rolle"] == "Museumsdirektør"


def test_spm_12_hva_bruker_vi_mest_tid_pa_innen_myndighetskontakt_ledelse() -> None:
    """12. Hva bruker vi mest tid på innen myndighetskontakt? (ledelse)"""
    res = mcp_server.search_arbeidsoppgaver(omrade="Myndighetskontakt")
    assert res["total_timer"] == 112
    sortert = sorted(res["oppgaver"], key=lambda o: o["timer_per_ar"], reverse=True)
    topp = sortert[0]
    assert topp["id"] == "AO-01"
    assert topp["oppgave"] == "Tilskuddssøknad"
    assert topp["myndighet"] == "Kulturdirektoratet"
    assert topp["timer_per_ar"] == 40


def test_spm_13_hvilke_oppgaver_bor_automatiseres_forst_ledelse() -> None:
    """13. Hvilke oppgaver bør automatiseres først? (ledelse)"""
    res = mcp_server.search_arbeidsoppgaver(automatiseringspotensial="Høy")
    hoy_ids = {o["id"] for o in res["oppgaver"]}
    assert {
        "AO-03", "AO-04", "AO-05", "AO-08", "AO-09",
        "AO-12", "AO-13", "AO-14", "AO-17", "AO-18",
    } == hoy_ids
    for o in res["oppgaver"]:
        assert o["automatiseringspotensial"] == "Høy"
        assert len(o["begrunnelse"]) > 20


def test_spm_14_hvor_lenge_har_vi_pa_a_lukke_et_gult_avvik_etter_tilsyn() -> None:
    """14. Hvor lenge har vi på å lukke et gult avvik etter tilsyn?"""
    res = mcp_server.get_inspection_routine()
    assert res["avvik_frister"]["gult_avvik_lukkes_innen"] == "14 dager"
    assert res["avvik_frister"]["rodt_avvik_lukkes_innen"] == "24 timer"


# -----------------------------------------------------------------------------
# DEL 2: DE 6 FELLESPØRSMÅLENE (SKAL IKKE FINNES / SKAL GI AVSLAG ELLER SKJERMING)
# -----------------------------------------------------------------------------

def test_spm_15_ingen_telefonnummer_til_mattilsynet_i_h5() -> None:
    """15. Hva er telefonnummeret til Mattilsynet? -> Finnes ikke i H5-dataene."""
    res = db.query_myndighetskontakter(query="Mattilsynet", include_contacts=True)
    rad = res["myndigheter"][0]
    assert "telefon" not in rad
    tekst = " ".join(str(v) for v in rad.values())
    assert not re.search(r"\b\d{8}\b", tekst), "Skal ikke inneholde 8-sifret telefonnummer"


def test_spm_16_ingen_konkret_tilsynsrapport_fra_forrige_tilsyn() -> None:
    """16. Hva stod i rapporten fra forrige tilsyn? -> Kun generell rutine, ingen historisk tilsynsrapport."""
    rutine = mcp_server.get_inspection_routine()
    for s in rutine["steg"]:
        # Friteksten i rutinen har ingen årstall eller konkrete funn fra tidligere tilsyn
        assert not re.search(r"\d", s["handling"])
        assert not re.search(r"\d", s["dokumentasjon"])


def test_spm_17_tilskudd_og_historikk_er_kun_for_ledelse_ikke_aapen_datafinner() -> None:
    """17. Hvor mye fikk vi i tilskudd i fjor? -> Skjermet i åpne kall (Datafinner), kun i ledelsesverktøyet."""
    with pytest.raises(ValueError, match="Ukjent verktøy"):
        datafinner.run_tool("search_governance_history", {"ar_fra": 2025, "ar_til": 2025})

    # For ledelse via MCP finnes 2025-tallene deterministisk:
    hist = mcp_server.search_governance_history(ar_fra=2025, ar_til=2025)
    assert hist["antall"] == 1
    assert hist["historikk"][0]["tilskudd_tkr"] > 0


def test_spm_18_ingen_lovtolkning_om_oppbevaringstid_for_temperaturlogger() -> None:
    """18. Hva sier loven om oppbevaring av temperaturlogger? -> H5 har ingen lovparagrafer eller oppbevaringstider."""
    res = mcp_server.search_myndighet(query="Mattilsynet")
    rad = res["myndigheter"][0]
    for felt in ("hva_de_vil", "utloser", "dokumentasjon"):
        assert "§" not in rad[felt]
        assert not re.search(r"\d", rad[felt])


def test_spm_19_ingen_navn_pa_inspektorer_for_neste_tilsyn_i_aapne_kall() -> None:
    """19. Hvem kommer fra tilsynet neste gang? -> Kontaktpersoner er skjermet som standard og i Datafinner."""
    res_mcp_default = mcp_server.search_myndighet()
    for m in res_mcp_default["myndigheter"]:
        assert m["kontaktperson"] == "[SKJERMET]"
        assert m["kontakt_epost"] == "[SKJERMET]"

    res_df = datafinner.run_tool("search_myndighet", {})
    for m in res_df["myndigheter"]:
        assert m["kontaktperson"] == "[SKJERMET]"


def test_spm_20_ingen_personlig_tidsbruk_per_enkeltperson_kun_roller() -> None:
    """20. Hvor mange timer bruker jeg personlig på rapporter? -> Fil E har kun roller, aldri personnavn/ansatt_id, og er stengt i Datafinner."""
    with pytest.raises(ValueError, match="Ukjent verktøy"):
        datafinner.run_tool("search_arbeidsoppgaver", {})

    oppgaver = mcp_server.search_arbeidsoppgaver()["oppgaver"]
    for o in oppgaver:
        assert "ansatt_id" not in o
        assert "navn" not in o
        assert o["rolle"] in {"Museumsdirektør", "Driftsansvarlig", "Kafeansvarlig", "Samlingsforvalter"}
