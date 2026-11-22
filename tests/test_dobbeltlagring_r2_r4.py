"""R2–R4: dobbeltlagring fjernet i bygget av museum.db.

R2: hr_skills er borte. hr_person_skill.skill_code peker på org_ferdigheter, og kortnavnene fra
    HR-demoen ligger i org_ferdigheter.kortnavn.
R3: personas lagrer ikke navn, avdeling og stilling. De hentes fra hr_ansatte med JOIN.
R4: driftsmeldinger_epost, driftsmeldinger_tiltak, anmeldelser og hendelser har rolle_kode med
    fremmednøkkel til roller(kode). De gamle rollekolonnene er urørt.

Alt testes mot et midlertidig bygg. 05_data/museum.db røres ikke.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "05_data"
SEED = DATA / "hr_demo" / "seed.json"
ROLLE_TABELLER = {
    "driftsmeldinger_epost": "mottaker_rolle",
    "driftsmeldinger_tiltak": "ansvarlig_rolle",
    "anmeldelser": "ansvarlig_rolle",
    "hendelser": "ansvarlig_rolle",
}


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("dobbeltlagring") / "museum.db"
    bygg(db)
    return db


@pytest.fixture
def con(bygget_db: Path):
    c = sqlite3.connect(bygget_db.resolve().as_uri() + "?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    try:
        yield c
    finally:
        c.close()


def _les_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _kolonner(con: sqlite3.Connection, tabell: str) -> dict[str, sqlite3.Row]:
    return {r["name"]: r for r in con.execute(f"PRAGMA table_info('{tabell}')")}


def _fk(con: sqlite3.Connection, tabell: str) -> set[tuple[str, str, str]]:
    return {(r["from"], r["table"], r["to"]) for r in con.execute(f"PRAGMA foreign_key_list('{tabell}')")}


# --- R2 -----------------------------------------------------------------------------------------


def test_r2_hr_skills_finnes_ikke(con) -> None:
    assert con.execute("SELECT 1 FROM sqlite_master WHERE name = 'hr_skills'").fetchone() is None


def test_r2_hr_person_skill_peker_paa_org_ferdigheter(con) -> None:
    assert ("skill_code", "org_ferdigheter", "skill_code") in _fk(con, "hr_person_skill")
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []


def test_r2_kortnavn_og_utlop_fra_hr_demoen_er_bevart(con) -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    rader = {r["skill_code"]: r for r in con.execute("SELECT skill_code, kortnavn, utloper FROM org_ferdigheter")}
    for s in seed["skills"]:
        assert rader[s["code"]]["kortnavn"] == s["name"], s["code"]
        assert rader[s["code"]]["utloper"] == s["expires"], s["code"]


def test_r2_katalogen_har_samme_felt_og_alle_14_koder(bygget_db: Path) -> None:
    from src.kunstpixel.core.hrdemo import list_skills

    seed = {s["code"]: s for s in json.loads(SEED.read_text(encoding="utf-8"))["skills"]}
    katalog = list_skills(bygget_db)
    assert len(katalog) == 14
    assert all(set(k) == {"code", "name", "expires"} for k in katalog)
    for k in katalog:
        if k["code"] in seed:
            assert (k["name"], k["expires"]) == (seed[k["code"]]["name"], seed[k["code"]]["expires"])


def test_r2_telling_og_person_har_samme_felt(bygget_db: Path) -> None:
    from src.kunstpixel.core.hrdemo import count_skill, get_person

    svar = count_skill("kasse", "2026-11-07", bygget_db)
    assert set(svar) == {"code", "as_of", "count", "people"} and svar["count"] == 7
    assert count_skill("finnes_ikke", "2026-11-07", bygget_db)["error"] == "UNKNOWN_SKILL"
    person = get_person("E101", db_path=bygget_db)
    assert person["skills"]
    assert all(set(s) == {"skill_code", "skill_name", "expires", "verified", "evidence", "acquired",
                          "valid_to", "is_current"} for s in person["skills"])
    assert {s["skill_code"]: s["skill_name"] for s in person["skills"]}["kasse"] == "Kassasystem"


def test_r2_load_seed_avviser_kompetanse_som_ikke_stemmer_med_org_ferdigheter(con) -> None:
    from src.kunstpixel.core.hrdemo import load_seed

    mal = sqlite3.connect(":memory:")
    try:
        con.backup(mal)
        for t in ("hr_rules", "hr_availability", "hr_person_skill", "hr_people"):
            mal.execute(f"DROP TABLE {t}")
        feil_navn = json.loads(SEED.read_text(encoding="utf-8"))
        feil_navn["skills"][0]["name"] = "Annet navn"
        ukjent = json.loads(SEED.read_text(encoding="utf-8"))
        ukjent["skills"].append({"code": "ukjent_kurs", "name": "Ukjent", "expires": 0})
        for seed in (feil_navn, ukjent):
            with pytest.raises(ValueError, match="org_ferdigheter"):
                load_seed(mal, seed)
    finally:
        mal.close()


# --- R3 -----------------------------------------------------------------------------------------


def test_r3_personas_lagrer_ikke_navn_avdeling_stilling(con) -> None:
    kolonner = set(_kolonner(con, "personas"))
    assert not kolonner & {"navn", "avdeling", "stilling"}
    assert ("id", "hr_ansatte", "ansatt_id") in _fk(con, "personas")


def test_r3_cv_har_samme_felt_og_verdier_som_kilden(bygget_db: Path) -> None:
    from src.kunstpixel.core.db import query_employee_cv

    kilde = {p["id"]: p for p in json.loads((DATA / "arkiv_cv_personas.json").read_text(encoding="utf-8"))}
    for ident in ("KP-ANS-001", "KP-ANS-153"):
        cv = query_employee_cv(ident, db_path=bygget_db)
        assert set(cv) == {"id", "navn", "avdeling", "stilling", "icor_rolle", "cv_json", "cv_detaljer"}
        p = kilde[ident]
        assert (cv["id"], cv["navn"], cv["avdeling"], cv["stilling"], cv["icor_rolle"]) == (
            p["id"], p["navn"], p.get("avdeling"), p.get("stilling"), p.get("icor_rolle"))
        assert cv["cv_detaljer"] == p
    assert query_employee_cv("Henrik Faye-Lund", db_path=bygget_db)["id"] == "KP-ANS-001"


# --- R4 -----------------------------------------------------------------------------------------


def test_r4_normalisering_av_rollenavn() -> None:
    from src.kunstpixel.data.build_museum_db import normaliser_rollenavn

    assert normaliser_rollenavn("Museumsdirektør") == "museumsdirektor"
    assert normaliser_rollenavn("Økonomi og innkjøp") == "okonomi_og_innkjop"
    assert normaliser_rollenavn("HR og bemanning") == "hr_og_bemanning"
    assert normaliser_rollenavn("Kafeansvarlig") == "kafeansvarlig"
    assert normaliser_rollenavn("Ærlig Åpen") == "aerlig_apen"


def test_r4_oppslagsfila_er_lik_det_generatoren_lager() -> None:
    from src.kunstpixel.data.build_museum_db import (
        ROLLE_KODE_OPPSLAG_CSV,
        lag_rolle_kode_oppslag,
    )

    forventet = lag_rolle_kode_oppslag(_les_csv(DATA / "roller.csv"))
    assert _les_csv(ROLLE_KODE_OPPSLAG_CSV) == forventet
    assert b"\r\n" not in ROLLE_KODE_OPPSLAG_CSV.read_bytes()


def test_r4_like_normaliserte_navn_stopper() -> None:
    from src.kunstpixel.data.build_museum_db import lag_rolle_kode_oppslag

    with pytest.raises(ValueError, match="samme"):
        lag_rolle_kode_oppslag([{"kode": "X", "navn": "HR og bemanning"}, {"kode": "Y", "navn": "hr og Bemanning"}])


def test_r4_ukjent_rolle_stopper_med_tabell_og_verdi() -> None:
    from src.kunstpixel.data.build_museum_db import rolle_kode_for

    with pytest.raises(ValueError, match=r"anmeldelser.*sjefsrolle"):
        rolle_kode_for("sjefsrolle", {"kurator": "C"}, "anmeldelser")


@pytest.mark.parametrize("tabell", sorted(ROLLE_TABELLER))
def test_r4_rolle_kode_er_utfylt_med_fremmednokkel(con, tabell: str) -> None:
    kol = _kolonner(con, tabell)
    assert "rolle_kode" in kol and kol["rolle_kode"]["notnull"] == 1
    assert ("rolle_kode", "roller", "kode") in _fk(con, tabell)
    gammel = ROLLE_TABELLER[tabell]
    oppslag = {r["rolle_tekst"]: r["rolle_kode"] for r in _les_csv(DATA / "rolle_kode_oppslag.csv")}
    rader = con.execute(f"SELECT {gammel} AS g, rolle_kode FROM {tabell}").fetchall()
    assert rader and all(r["rolle_kode"] == oppslag[r["g"]] for r in rader)
    assert con.execute(f"SELECT count(*) FROM {tabell} t LEFT JOIN roller r ON r.kode = t.rolle_kode "
                       "WHERE r.kode IS NULL").fetchone()[0] == 0


def test_r4_gamle_rollekolonner_er_like_kilden(con) -> None:
    from src.kunstpixel.data import build_museum_db as b

    for tabell, csvfil, nokkel, kol in (
        ("driftsmeldinger_epost", b.DRIFTSMELDINGER_EPOST_CSV, "melding_id", "mottaker_rolle"),
        ("driftsmeldinger_tiltak", b.DRIFTSMELDINGER_TILTAK_CSV, "tiltak_id", "ansvarlig_rolle"),
        ("anmeldelser", b.ANMELDELSER_CSV, "anmeldelse_id", "ansvarlig_rolle"),
    ):
        kilde = {r[nokkel]: r[kol] for r in _les_csv(csvfil)}
        bygget = {r[0]: r[1] for r in con.execute(f"SELECT {nokkel}, {kol} FROM {tabell}")}
        assert bygget == kilde, tabell

    base = sqlite3.connect(b.BASE_DB.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        forventet = [r[0] for r in base.execute("SELECT ansvarlig_rolle FROM hendelser ORDER BY id")]
    finally:
        base.close()
    forventet += [r["ansvarlig_rolle"] for r in _les_csv(b.HENDELSER_TILLEGG_CSV)]
    assert [r[0] for r in con.execute("SELECT ansvarlig_rolle FROM hendelser ORDER BY id")] == forventet


def test_r4_bygget_stopper_paa_rolle_uten_kobling(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.kunstpixel.data import build_museum_db as b

    tekst = b.ANMELDELSER_CSV.read_text(encoding="utf-8").replace(",kommunikasjon,", ",sjefsrolle,", 1)
    assert ",sjefsrolle," in tekst
    odelagt = tmp_path / "anmeldelser.csv"
    odelagt.write_text(tekst, encoding="utf-8")
    monkeypatch.setattr(b, "ANMELDELSER_CSV", odelagt)
    with pytest.raises(ValueError, match="sjefsrolle"):
        b.bygg(tmp_path / "x.db")
