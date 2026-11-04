"""HR-casefinneren skal foreslå etterprøvbare oppgaver fra syntetiske data."""

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.core import db


def test_avdelingssok_teller_alle_ansatte_med_personalmappe() -> None:
    with db.get_db_connection() as con:
        forventet = con.execute(
            "SELECT COUNT(DISTINCT a.ansatt_id) FROM hr_ansatte a "
            "JOIN hr_personalmapper p ON p.ansatt_id = a.ansatt_id WHERE a.avdeling = ?",
            ("Formidling",),
        ).fetchone()[0]
    svar = datafinner.run_tool("discover_hr_cases", {"sok": "Formidling", "kategori": "personalmappe", "limit": 50})
    assert svar["antall_funnet"] == forventet


def test_avdelingssok_finner_samtaler_ogsaa_etter_de_forste_15() -> None:
    with db.get_db_connection() as con:
        forventet = con.execute(
            "SELECT COUNT(DISTINCT a.ansatt_id) FROM hr_ansatte a "
            "JOIN hr_medarbeidersamtaler m ON m.ansatt_id = a.ansatt_id WHERE a.avdeling = ?",
            ("Formidling",),
        ).fetchone()[0]
    svar = datafinner.run_tool("discover_hr_cases", {"sok": "Formidling", "kategori": "medarbeidersamtale", "limit": 50})
    assert svar["antall_funnet"] == forventet


def test_finner_tvetydig_navn_og_gir_neste_oppslag() -> None:
    """Fanger regresjon der KI velger en av to ansatte med samme navn."""
    svar = datafinner.run_tool("discover_hr_cases", {"kategori": "tvetydig_navn", "limit": 10})
    anja = next(c for c in svar["caser"] if c["navn"] == "Anja Eriksen")
    assert anja["ansatt_ider"] == ["KP-ANS-047", "KP-ANS-115"]
    assert anja["kilde"] == "hr_ansatte"
    assert anja["neste_verktoy"] == {"navn": "resolve_employee", "args": {"sok": "Anja Eriksen"}}


def test_finner_hr_oppgaver_for_en_konkret_ansatt() -> None:
    """Fanger regresjon der casefinneren dikter opp saker eller hopper over registrerte samtaler."""
    svar = datafinner.run_tool("discover_hr_cases", {"sok": "KP-ANS-153", "limit": 10})
    assert {c["kategori"] for c in svar["caser"]} >= {"medarbeidersamtale", "personalmappe"}
    for case in svar["caser"]:
        assert case["ansatt_ider"] == ["KP-ANS-153"]
        assert case["kilde"] in {"hr_medarbeidersamtaler", "hr_personalmapper"}
        assert case["neste_verktoy"]["navn"] in {"get_employee_reviews", "get_personnel_file"}


def test_ukjent_ansatt_gir_ingen_caser() -> None:
    svar = datafinner.run_tool("discover_hr_cases", {"sok": "KP-ANS-999"})
    assert svar["caser"] == []


def test_aapent_hr_spoersmaal_gir_ulike_typer_oppgaver() -> None:
    """Fanger regresjon der de første ti treffene bare er like navn og sluttede ansatte."""
    svar = datafinner.run_tool("discover_hr_cases", {"limit": 10})
    assert {c["kategori"] for c in svar["caser"]} == {
        "tvetydig_navn", "sluttet_ansatt", "medarbeidersamtale", "personalmappe"
    }


def test_llm_kan_undersoeke_funnet_samtalecase() -> None:
    """Fanger regresjon der et case får et svar uten å hente de faktiske samtalene."""
    svar = datafinner.run_tool("investigate_hr_case", {"kategori": "medarbeidersamtale", "ansatt_id": "KP-ANS-153"})
    assert svar["ansatt_id"] == "KP-ANS-153"
    assert svar["kilde"] == "hr_medarbeidersamtaler"
    assert svar["antall"] == 2
    assert all(r["ansatt_id"] == "KP-ANS-153" for r in svar["fakta"])


def test_tomt_personalmappecase_blir_ikke_funnet_pa() -> None:
    """Fanger regresjon der en tom personalmappe blir presentert som en sak."""
    svar = datafinner.run_tool("investigate_hr_case", {"kategori": "personalmappe", "ansatt_id": "KP-ANS-155"})
    assert svar == {"ansatt_id": "KP-ANS-155", "kategori": "personalmappe", "kilde": "hr_personalmapper", "antall": 0, "fakta": []}
