"""KI-en må avklare person før oppslag i HR-data."""

from src.kunstpixel.adapters import datafinner


def test_likt_fullt_navn_gir_tvetydig_resultat_med_begge_ider() -> None:
    svar = datafinner.run_tool("resolve_employee", {"sok": "Anja Eriksen"})
    assert svar["status"] == "tvetydig"
    assert svar["antall"] == 2
    assert {r["ansatt_id"] for r in svar["kandidater"]} == {"KP-ANS-047", "KP-ANS-115"}
    assert svar["kilde"] == "hr_ansatte"


def test_eksakt_id_gir_en_person_selv_om_navn_er_likt() -> None:
    svar = datafinner.run_tool("resolve_employee", {"sok": "KP-ANS-047"})
    assert svar["status"] == "entydig"
    assert [r["ansatt_id"] for r in svar["kandidater"]] == ["KP-ANS-047"]


def test_ukjent_id_gir_ingen_uten_oppdiktet_kandidat() -> None:
    svar = datafinner.run_tool("resolve_employee", {"sok": "KP-ANS-999"})
    assert svar == {"status": "ingen", "antall": 0, "kandidater": [], "kilde": "hr_ansatte"}
