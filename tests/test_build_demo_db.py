"""Tester for demokopien av museum.db (forberedelse til hosting).

Testgrensen: det som blir igjen i kopien, og at Datafinners hvitelistede verktøy gir de samme
svarene mot kopien som mot museum.db. Hver ny tabell eller hvert nytt verktøy som ikke er dekket,
får testen til å feile.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from src.kunstpixel.adapters import datafinner
from src.kunstpixel.data import build_demo_db as demo


@pytest.fixture(scope="module")
def demo_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    ut = tmp_path_factory.mktemp("demo") / "museum_demo.db"
    demo.bygg_demo(demo.KILDE_DB, ut)
    return ut


def _tilkobling(db: Path) -> sqlite3.Connection:
    return sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)


def test_demokopien_har_bare_de_tillatte_tabellene(demo_db: Path) -> None:
    con = _tilkobling(demo_db)
    try:
        tabeller = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    finally:
        con.close()
    assert tabeller == set(demo.BEHOLD) | {"demo_info"}


def test_personopplysninger_er_tatt_ut(demo_db: Path) -> None:
    con = _tilkobling(demo_db)
    try:
        antall = con.execute("SELECT count(*) FROM hr_ansatte").fetchone()[0]
        igjen = con.execute(
            "SELECT count(*) FROM hr_ansatte WHERE fodselsaar IS NOT NULL OR epost IS NOT NULL OR telefon IS NOT NULL"
        ).fetchone()[0]
    finally:
        con.close()
    assert antall == 168 and igjen == 0


def test_ingen_epost_eller_telefon_i_noen_tekstkolonne(demo_db: Path) -> None:
    """Skanner alle tekstkolonner i alle tabeller, ikke bare de vi vet om."""
    # Telefon: +47 foran siffer, eller et frittstående 8-sifret nummer som starter på 4 eller 9 (ikke ID-er som VAKT-0012345).
    epost, telefon = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), re.compile(r"\+47\s?\d|(?<![\w.-])[49]\d{7}(?![\w-])")
    con = _tilkobling(demo_db)
    funn = []
    try:
        for (tabell,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
            kolonner = [r[1] for r in con.execute(f'PRAGMA table_info("{tabell}")') if (r[2] or "").upper() in ("TEXT", "")]
            for kol in kolonner:
                for (verdi,) in con.execute(f'SELECT "{kol}" FROM "{tabell}" WHERE "{kol}" IS NOT NULL'):
                    if isinstance(verdi, str) and (epost.search(verdi) or telefon.search(verdi)):
                        funn.append(f"{tabell}.{kol}: {verdi[:40]}")
    finally:
        con.close()
    assert not funn, funn[:5]


def test_kopien_er_hel_og_ren(demo_db: Path) -> None:
    con = _tilkobling(demo_db)
    try:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
        info = dict(con.execute("SELECT nokkel, verdi FROM demo_info").fetchall())
    finally:
        con.close()
    assert info["kilde_sha256"] == demo.sha256(demo.KILDE_DB)
    assert "hr_ansatte.epost" in info["tomme_kolonner"]


def test_bygget_er_deterministisk(tmp_path: Path) -> None:
    a, b = tmp_path / "a.db", tmp_path / "b.db"
    assert demo.bygg_demo(demo.KILDE_DB, a)["sha256"] == demo.bygg_demo(demo.KILDE_DB, b)["sha256"]


def test_bygget_rorer_ikke_kilden() -> None:
    for_hash = demo.sha256(demo.KILDE_DB)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        demo.bygg_demo(demo.KILDE_DB, Path(tmp) / "x.db")
    assert demo.sha256(demo.KILDE_DB) == for_hash


def test_bygget_feiler_tydelig_uten_kilde(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        demo.bygg_demo(tmp_path / "finnes-ikke.db", tmp_path / "ut.db")


# Eksempelargumenter for hvert hvitelistet databaseverktøy. Et nytt verktøy uten eksempel feiler testen under.
EKSEMPLER = {
    "search_collection": {"title": "Skrik"},
    "get_artwork_details": {"artwork_id": None},  # fylles inn fra databasen
    "get_room_artworks": {"room_id": "SAL-D"},
    "search_events": {},
    "search_faq": {"query": "pris"},
    "get_staff_on_shift": {"dato": "2026-10-19", "klokkeslett": "12:00"},
    "get_working_time_limits": {},
    "get_shifts_for_date": {"dato": "2026-10-20"},
    "get_working_hours_report": {"maaned": "2026-09"},
    "get_sickness_absence_statistics": {"year": 2025, "quarter": 2},
    "get_absence_report": {"aar": 2025, "kvartal": 2},
    "list_roles": {},
    "get_report_rules": {"sporsmal_id": "vakt-i-dag"},
    "get_report_assessment": {"sporsmal_id": "vakt-i-dag", "verdier": {"antall_med_vakt": 9}},
    "get_exhibition_economy": {"exhibition_id": None},  # fylles inn fra databasen
    "get_shift_cost_for_period": {"maaned": "2026-09"},
    "list_exhibitions_with_economy": {},
}


def _kjor_alle(db: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.setenv("KUNSTPIXEL_DB_PATH", str(db))
    liste = datafinner.run_tool("list_exhibitions_with_economy", {})
    eks = {k: dict(v) for k, v in EKSEMPLER.items()}
    eks["get_exhibition_economy"]["exhibition_id"] = liste[0]["utstilling_id"]
    eks["get_artwork_details"]["artwork_id"] = datafinner.run_tool("search_collection", {"limit": 1})[0]["id"]
    return {navn: datafinner.run_tool(navn, args) for navn, args in eks.items()}


def test_alle_databaseverktoy_har_eksempel() -> None:
    verktoy = set(datafinner.VERKTOY) - set(datafinner.FILVERKTOY)
    assert verktoy == set(EKSEMPLER), "Legg til eksempelargumenter for nye verktøy i EKSEMPLER"


def test_alle_verktoy_virker_mot_demokopien_og_gir_samme_tall(demo_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ekte = _kjor_alle(demo.KILDE_DB, monkeypatch)
    kopi = _kjor_alle(demo_db, monkeypatch)
    assert kopi.keys() == ekte.keys()
    # Tallene skal være identiske. Vaktlistene har telefon og e-post (tatt ut), så de sammenlignes uten dem.
    for navn in ("get_working_hours_report", "get_shift_cost_for_period", "get_absence_report", "get_exhibition_economy",
                 "get_report_assessment", "list_roles", "get_working_time_limits", "get_sickness_absence_statistics"):
        assert kopi[navn] == ekte[navn], navn
    antall_ekte = {v["vakt_id"] for v in ekte["get_shifts_for_date"]}
    assert {v["vakt_id"] for v in kopi["get_shifts_for_date"]} == antall_ekte and antall_ekte
    for v in kopi["get_shifts_for_date"]:
        assert not v.get("epost") and not v.get("telefon")


def test_navneliste_skrives(demo_db: Path, tmp_path: Path) -> None:
    fil = tmp_path / "navn.md"
    assert demo.skriv_navneliste(demo_db, fil) == 168
    tekst = fil.read_text(encoding="utf-8")
    assert "KP-ANS-001" in tekst and "[ ]" in tekst
