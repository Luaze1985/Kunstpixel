"""B9: e-postmaler som data. Utkastet lages på serveren fra fakta i databasen. Ingenting sendes."""

from __future__ import annotations

import re
from datetime import date

import pytest

from src.kunstpixel.core import epostmaler, frister
from src.kunstpixel.core.epostmaler import (
    MALER,
    PLASSHOLDERE,
    fyll_mal,
    utkast_for_frist,
)


def test_fyll_mal_setter_inn_verdiene() -> None:
    assert fyll_mal("Frist {frist_dato}: {tittel}", {"tittel": "Retur av innlån", "frist_dato": "2026-03-01"}) == \
        "Frist 2026-03-01: Retur av innlån"


def test_fyll_mal_feiler_naar_en_plassholder_mangler() -> None:
    with pytest.raises(ValueError, match="frist_dato"):
        fyll_mal("Frist {frist_dato}: {tittel}", {"tittel": "x"})


def test_fyll_mal_ignorerer_ekstra_verdier() -> None:
    assert fyll_mal("{tittel}", {"tittel": "a", "annet": "b"}) == "a"


def test_verdier_kan_ikke_lage_nye_plassholdere() -> None:
    """En verdi som ser ut som en plassholder settes inn som tekst og fylles ikke ut på nytt."""
    assert fyll_mal("{tittel} / {kilde}", {"tittel": "{kilde}", "kilde": "db"}) == "{kilde} / db"


def test_linjeskift_i_verdier_fjernes() -> None:
    """Hindrer at en verdi lager nye linjer i emnet (e-posthode-injeksjon)."""
    assert fyll_mal("Emne: {tittel}", {"tittel": "a\r\nBcc: x@y.no"}) == "Emne: a Bcc: x@y.no"


def test_for_lange_verdier_kuttes() -> None:
    assert len(fyll_mal("{tittel}", {"tittel": "x" * 2000})) <= 300


@pytest.mark.parametrize("mal_id", sorted(MALER))
def test_malene_bruker_bare_tillatte_plassholdere(mal_id: str) -> None:
    for del_ in ("overskrift", "tekst"):
        felt = set(re.findall(r"\{([^{}]*)\}", MALER[mal_id][del_]))
        assert felt <= PLASSHOLDERE, f"{mal_id}.{del_}: {felt - PLASSHOLDERE}"


@pytest.mark.parametrize("mal_id", sorted(MALER))
def test_malene_spor_aldri_om_diagnose_eller_aarsak(mal_id: str) -> None:
    tekst = (MALER[mal_id]["overskrift"] + " " + MALER[mal_id]["tekst"]).lower()
    for ord_ in ("diagnose", "årsak", "sykdom", "grunnen til"):
        assert ord_ not in tekst


def test_malene_viser_kilden() -> None:
    for mal in MALER.values():
        assert "{kilde}" in mal["tekst"]  # fakta skal kunne spores tilbake


@pytest.mark.parametrize("typ", ["sykefravaer_uke4", "sykefravaer_uke7", "driftsmelding", "hms_avvik", "rapport",
                                 "tilstandskontroll", "innlan"])
def test_hver_fristtype_har_et_utkast(typ: str) -> None:
    f = {"type": typ, "tittel": "Testsak", "frist_dato": "2026-03-01", "dager_til": -5, "kilde": "tabell"}
    ut = utkast_for_frist(f)
    assert set(ut) == {"overskrift", "tekst"}
    assert "Testsak" in ut["overskrift"] and "tabell" in ut["tekst"] and "5 dager over fristen" in ut["tekst"]


def test_ukjent_fristtype_gir_ingen_utkast() -> None:
    assert utkast_for_frist({"type": "noe_nytt", "tittel": "x", "frist_dato": "2026-01-01", "dager_til": 0, "kilde": "y"}) is None


def test_mine_frister_har_epostutkast_fra_databasen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(frister, "_idag", lambda: date(2026, 11, 16))
    svar = frister.get_my_deadlines("Museumsdirektør", "2026-11-16")
    # Innlånene er returnert i bygget (Lars 2026-11-22), så testen bruker fristene som finnes, ikke innlån.
    assert svar["frister"], "testdataene har frister for direktøren"
    for f in svar["frister"]:
        assert f["epost"]["overskrift"] == f"Oppfølging: {f['tittel']}"
    assert "kilde" not in epostmaler.MALER["innlan"]["overskrift"]
