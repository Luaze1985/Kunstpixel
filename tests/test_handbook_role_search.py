"""Arbeidsroller må treffe håndbokens målgrupper, ikke tilfeldige ord i innholdet."""

from src.kunstpixel.core.db import query_handbook


def test_montor_drift_finner_brannrutine_for_montorer_og_drift() -> None:
    treff = query_handbook(query="brann", role="Montør/drift", limit=20)
    assert "HMS_SIKKERHET-7.1" in {r["punkt_id"] for r in treff}


def test_samling_kurator_faar_fellesregler_for_egenmelding() -> None:
    treff = query_handbook(query="egenmelding", role="Samling/kurator", limit=20)
    assert "PERSONAL-5.2" in {r["punkt_id"] for r in treff}


def test_kafe_rolle_faar_ikke_treff_bare_fordi_innholdet_nevner_kafe() -> None:
    treff = query_handbook(query="brann", role="Kafé", limit=20)
    assert all("alle ansatte" in r["malgruppe"].lower() or "kafé" in r["malgruppe"].lower() for r in treff)


def test_tegn_uten_sokeord_gir_ikke_tilfeldige_handbokpunkter() -> None:
    assert query_handbook(query="???") == []
