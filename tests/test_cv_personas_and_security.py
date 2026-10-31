"""Tester for komplett CV-dekning, aktive innleide og sikkerhetslås for personalmapper (CASE-016).

Sikrer at:
1. Alle 168 ansatte og 74 aktive har fullstendig syntetisk CV/persona.
2. Aktive innleide konsulenter og vektere i 2026 kan søkes opp med profil og timepris.
3. Fortrolige personalmapper er strengt beskyttet (RBAC) mot uautorisert innsyn (CASE-016).
4. Alle nye data er 100 % syntetisk merket.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.kunstpixel.core import db
from src.kunstpixel.core.mcp_server import get_employee_cv, search_active_contractors, get_personnel_dossier

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "05_data"


# =====================================================================
# 1. Tester for fullstendig CV-dekning (alle 168 ansatte)
# =====================================================================

def test_alle_168_ansatte_har_cv_og_persona() -> None:
    """Samtlige ansatte i arkivet skal ha en tilgjengelig CV/persona."""
    emp_file = DATA_DIR / "arkiv_hr_ansatte.csv"
    with emp_file.open(encoding="utf-8") as f:
        employees = list(csv.DictReader(f))
    
    assert len(employees) == 168, "Forventet 168 ansatte i registeret"
    
    for emp in employees:
        res = db.query_employee_cv(emp["ansatt_id"])
        assert res is not None, f"Mangler CV for ansatt {emp['ansatt_id']} ({emp['navn']})"
        assert res["navn"] == emp["navn"]
        assert "cv_detaljer" in res or "cv_json" in res
        
        cv = res.get("cv_detaljer", {})
        assert "utdanning" in cv, f"Mangler utdanning for {emp['ansatt_id']}"
        assert len(cv["utdanning"]) >= 1, f"Tom utdanningshistorikk for {emp['ansatt_id']}"


def test_aktive_ansatte_har_relevante_utdanningslop() -> None:
    """Verifiser at f.eks. museumsverter og vektere har relevante kurs/fagutdanning."""
    vert_cv = db.query_employee_cv("KP-ANS-153")  # Sindre Lindqvist, Museumsvert
    assert vert_cv is not None
    assert vert_cv["stilling"] == "Museumsvert og omviser (Deltid)"
    
    utdanning = vert_cv["cv_detaljer"]["utdanning"]
    grader = [u["grad"] for u in utdanning]
    assert any("formidling" in g.lower() or "vekter" in g.lower() or "førstehjelp" in g.lower() or "kultur" in g.lower() for g in grader)


def test_originale_28_personas_er_intakte() -> None:
    """De opprinnelige 28 nøkkelpersonene må forbli uendret."""
    direktor = db.query_employee_cv("KP-ANS-001")
    assert direktor is not None
    assert direktor["navn"] == "Henrik Faye-Lund"
    assert direktor["stilling"] == "Museumsdirektør"
    assert any("Dr.philos" in u.get("grad", "") for u in direktor["cv_detaljer"]["utdanning"])


# =====================================================================
# 2. Tester for aktive innleide konsulenter og fagpersoner (2026)
# =====================================================================

def test_aktive_innleide_finnes_og_kan_sokes() -> None:
    """Aktive innleide i 2026 skal returneres med rammeavtale-info og timepris."""
    contractors = db.query_active_contractors()
    assert len(contractors) >= 6, "Forventet minst 6 aktive innleide konsulenter/vektere"
    
    # Sjekk obligatoriske felter
    first = contractors[0]
    for key in ["innleid_id", "navn", "firma", "stilling", "timepris_nok", "avtale_fra", "avtale_til", "status", "datakilde"]:
        assert key in first, f"Mangler nøkkel {key} i innleid kontraktør"
        
    assert first["status"] == "Aktiv"
    assert first["datakilde"].startswith("syntetisk")


def test_innleid_konservator_oppslag_med_cv() -> None:
    """Konservator fra Atelier Konservering skal kunne finnes både via navn og ID."""
    cv_by_id = db.query_employee_cv("KP-INN-P01")
    assert cv_by_id is not None
    assert cv_by_id["navn"] == "Kirsti Holte"
    assert "Atelier Konservering" in cv_by_id["avdeling"]
    assert cv_by_id["cv_detaljer"]["timepris_nok"] == 1400.0

    cv_by_name = db.query_employee_cv("Kirsti Holte")
    assert cv_by_name is not None
    assert cv_by_name["id"] == "KP-INN-P01"


def test_mcp_search_active_contractors_filtrering() -> None:
    """MCP-verktøyet for aktive innleide skal støtte kategori- og fritekstfiltrering."""
    # Kategori: Eksternt vakthold
    vektere = search_active_contractors(kategori="vakthold")
    assert len(vektere) >= 2
    assert all("Securitas" in v["firma"] or "Avarn" in v["firma"] for v in vektere)

    # Fritekst: "lysteknikk" eller "scenoteknikk"
    av_treff = search_active_contractors(query="Lys & Rom")
    assert len(av_treff) == 1
    assert av_treff[0]["navn"] == "Torstein Solberg"


# =====================================================================
# 3. Tester for sikkerhetslås og hemmelige personalmapper (CASE-016)
# =====================================================================

def test_uautorisert_rolle_avvises_for_personalmappe() -> None:
    """En publikumsvert eller uautorisert rolle skal nektes tilgang til personalmapper (CASE-016)."""
    # Test med museumsvert
    res_vert = db.query_personnel_file(ansatt_id="KP-ANS-006", requester_role="museumsvert")
    assert res_vert.get("status") == 403
    assert res_vert.get("code") == "ACCESS_DENIED"
    assert "FORBIDDEN" in res_vert.get("error", "")
    assert len(res_vert.get("saker", [])) == 0

    # Test med tom/ukjent rolle
    res_ukjent = db.query_personnel_file(ansatt_id="KP-ANS-006", requester_role="")
    assert res_ukjent.get("status") == 403

    # Test via FastMCP verktøy
    mcp_res = get_personnel_dossier(ansatt_id="KP-ANS-006", requester_role="kafeansvarlig")
    assert mcp_res.get("code") == "ACCESS_DENIED"


def test_autorisert_leder_far_tilgang_til_personalmappe() -> None:
    """Museumsdirektør, driftsansvarlig og kvalitetsvokter skal ha tilgang til saksjournal."""
    # Driftsansvarlig ber om Jonas Berg sin mappe (sykeoppfølging)
    res_leder = db.query_personnel_file(ansatt_id="KP-ANS-006", requester_role="driftsansvarlig")
    assert "error" not in res_leder
    assert res_leder["antall_saker"] == 1
    assert res_leder["gradering"] == "LEDER_FORTROLIG"
    
    sak = res_leder["saker"][0]
    assert sak["kategori"] == "sykeoppfolging"
    assert "Oppfølgingsplan" in sak["tittel"]
    assert "BHT" in sak["innhold_fortrolig"]
    assert sak["datakilde"].startswith("syntetisk")


def test_direktor_far_innsyn_i_varslingssak_og_advarsel() -> None:
    """Verifiser innsyn i skriftlig advarsel og varslingssak for museumsdirektør."""
    # Skriftlig advarsel
    res_advarsel = db.query_personnel_file(ansatt_id="KP-ANS-153", requester_role="museumsdirektor")
    assert res_advarsel["antall_saker"] == 1
    assert res_advarsel["saker"][0]["kategori"] == "skriftlig_advarsel"

    # Varslingssak for driftssjef
    res_varsling = db.query_personnel_file(ansatt_id="KP-ANS-005", requester_role="kvalitetsvokter")
    assert res_varsling["antall_saker"] == 1
    assert res_varsling["saker"][0]["kategori"] == "varslingssak"


# =====================================================================
# 4. Data- og personverngarantier (100 % syntetisk)
# =====================================================================

def test_alle_nye_data_er_merket_syntetisk() -> None:
    """Garanter at ingen reelle personopplysninger eller hemmeligheter forekommer."""
    # Innleide
    with (DATA_DIR / "arkiv_hr_innleide_personer.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            assert row["datakilde"].startswith("syntetisk"), f"Umerket rad i innleide: {row}"
            
    # Personalmapper
    with (DATA_DIR / "arkiv_hr_personalmapper.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            assert row["datakilde"].startswith("syntetisk"), f"Umerket rad i personalmapper: {row}"
            assert row["gradering"] == "LEDER_FORTROLIG"


# =====================================================================
# 5. REST API tester (hrdemo_api.py)
# =====================================================================

def test_hrdemo_api_nye_endepunkter() -> None:
    """Tester de nye API-endepunktene for innleide, CV og sikkerhetslås for personalmapper."""
    import io
    from src.kunstpixel.core.hrdemo_api import Handler

    class FakeServerHandler(Handler):
        def __init__(self, path: str, headers: dict | None = None):
            self.path = path
            self.requestline = f"GET {path} HTTP/1.1"
            self.command = "GET"
            self.request_version = "HTTP/1.1"
            self.client_address = ("127.0.0.1", 8765)
            self.headers = headers or {}
            self.wfile = io.BytesIO()
            self.do_GET()

        def log_message(self, *args):
            pass

    # 1. Aktive innleide
    h_inn = FakeServerHandler("/api/v1/hr/contractors/active")
    raw_inn = h_inn.wfile.getvalue().decode("utf-8")
    assert "KP-INN-P01" in raw_inn
    assert "Atelier Konservering" in raw_inn

    # 2. CV-oppslag på museumsvert
    h_cv = FakeServerHandler("/api/v1/hr/cv?id=KP-ANS-153")
    raw_cv = h_cv.wfile.getvalue().decode("utf-8")
    assert "Sindre Lindqvist" in raw_cv
    assert "Museumsvert" in raw_cv

    # 3. Personalmappe uten autorisert rolle -> 403 Forbidden
    h_forbid = FakeServerHandler("/api/v1/hr/personalmapper?id=KP-ANS-006", headers={"Role": "museumsvert"})
    raw_forbid = h_forbid.wfile.getvalue().decode("utf-8")
    assert "403" in raw_forbid or "ACCESS_DENIED" in raw_forbid or "FORBIDDEN" in raw_forbid

    # 4. Personalmappe med autorisert rolle -> 200 OK
    h_ok = FakeServerHandler("/api/v1/hr/personalmapper?id=KP-ANS-006", headers={"Role": "museumsdirektor"})
    raw_ok = h_ok.wfile.getvalue().decode("utf-8")
    assert "Jonas Berg" in raw_ok
    assert "LEDER_FORTROLIG" in raw_ok
    assert "sykeoppfolging" in raw_ok

