"""Tester for scripts/db_kvalitet.py (databasekvalitet i klartekst)."""

from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import db_kvalitet as kvalitet
import db_status_gate as port


@pytest.fixture(scope="module")
def bygget_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from src.kunstpixel.data.build_museum_db import bygg

    db = tmp_path_factory.mktemp("kvalitet") / "museum.db"
    bygg(db)
    return db


def test_alle_regler_har_forklaring_pa_norsk() -> None:
    mangler = [navn for navn, _, _ in port.REGLER if navn not in kvalitet.FORKLARING]
    assert not mangler, f"regler uten forklaring: {mangler}"
    for navn, (betyr, gjor) in kvalitet.FORKLARING.items():
        assert betyr.strip() and gjor.strip(), navn


def test_ren_database_gir_ingen_feil(bygget_db: Path) -> None:
    resultat = kvalitet.kjor(bygget_db, med_bygg=False)
    assert [r for r in resultat if r[1] == kvalitet.FEIL] == []
    assert {r[0] for r in resultat} >= {"Databasen er hel", "Riktig skjemaversjon", "Alt er merket syntetisk"}


def test_ny_feil_i_data_gir_feil_med_forklaring(bygget_db: Path, tmp_path: Path) -> None:
    kopi = tmp_path / "museum.db"
    shutil.copyfile(bygget_db, kopi)
    con = sqlite3.connect(kopi)
    con.execute("INSERT INTO hr_fravaer (fravaer_id, ansatt_id, fra, til, type, datakilde) "
                "SELECT 'TEST-1', ansatt_id, dato, dato, 'egenmelding', 'syntetisk (test)' FROM hr_vakter LIMIT 1")
    con.commit()
    con.close()
    feil = [r for r in kvalitet.kjor(kopi, med_bygg=False) if r[1] == kvalitet.FEIL]
    assert [r[0] for r in feil] == ["vakt på dag med eget fravær"]
    navn, _, hva, tiltak = feil[0]
    assert "sykmeldt" in hva and "bygg" in tiltak.lower()


def test_gammel_skjemaversjon_meldes_med_tiltak(bygget_db: Path, tmp_path: Path) -> None:
    kopi = tmp_path / "museum.db"
    shutil.copyfile(bygget_db, kopi)
    con = sqlite3.connect(kopi)
    con.execute("PRAGMA user_version = 3")
    con.commit()
    con.close()
    niva, hva, tiltak = kvalitet.sjekk_skjemaversjon(kvalitet._ro(kopi))
    assert niva == kvalitet.FEIL and "versjon 3" in hva and "build_museum_db.py" in tiltak


def test_endret_fil_oppdages_via_sha(bygget_db: Path, tmp_path: Path) -> None:
    kopi = tmp_path / "museum.db"
    shutil.copyfile(bygget_db, kopi)
    (tmp_path / "museum.db.sha256").write_text("0" * 64 + "  museum.db\n", encoding="utf-8")
    assert kvalitet.sjekk_sha(kopi)[0] == kvalitet.FEIL


def test_manglende_database_gir_exit_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["db_kvalitet.py", "--db", str(tmp_path / "finnes_ikke.db")])
    assert kvalitet.main() == 1


def test_alle_funn_peker_pa_en_fil_som_finnes() -> None:
    from src.kunstpixel.data.build_museum_db import SKJEMAVERSJON  # noqa: F401 (sikrer at bygget importeres)

    manglende = [f"{navn}: {fil}" for navn, fil in kvalitet.FIL_FOR_FUNN.items() if not (ROOT / fil).is_file()]
    assert not manglende, manglende
    regler = {navn for navn, _, _ in port.REGLER}
    assert regler <= set(kvalitet.FIL_FOR_FUNN), "en regel mangler fil i FIL_FOR_FUNN"


def test_problemlinjer_passer_med_matcheren_i_tasks_json() -> None:
    import json
    import re

    oppgaver = json.loads((ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8"))["tasks"]
    oppgave = next(o for o in oppgaver if o["label"].startswith("Databasekvalitet"))
    assert "--problems" in oppgave["command"]
    mønster = re.compile(oppgave["problemMatcher"]["pattern"]["regexp"])

    resultat = [
        ("Riktig skjemaversjon", kvalitet.FEIL, "Databasen har versjon 3.", "Bygg på nytt."),
        ("for kort hviletid mellom vakter", kvalitet.ADVARSEL, "7 kjente brudd.", "Rett vaktene."),
        ("Databasen er hel", kvalitet.OK, "Fint.", ""),
    ]
    linjer = kvalitet.problemlinjer(resultat)
    assert len(linjer) == 2, "OK-funn skal ikke bli til problemer"
    treff = [mønster.match(l) for l in linjer]
    assert all(treff), linjer
    assert [t.group(1) for t in treff] == ["error", "warning"]
    assert treff[0].group(2) == kvalitet.BYGGESKRIPT and treff[0].group(3) == "1"
    assert "Databasen har versjon 3" in treff[0].group(4) and "Bygg på nytt" in treff[0].group(4)


def _les_innstillinger() -> dict:
    import json
    import re

    tekst = (ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8")
    return json.loads(re.sub(r"^\s*//.*$", "", tekst, flags=re.M))  # settings.json tillater kommentarer


def test_run_on_save_treffer_csv_i_05_data_og_ingenting_annet() -> None:
    import re

    kommando = _les_innstillinger()["emeraldwalk.runonsave"]["commands"][0]
    regel = re.compile(kommando["match"])
    assert regel.search(r"G:\Min disk\Kunstpixel\05_data\arkiv_hr_fravaer.csv")
    assert regel.search("G:/Min disk/Kunstpixel/05_data/roller.csv")
    assert not regel.search(r"G:\Min disk\Kunstpixel\src\kunstpixel\core\db.py")
    assert not regel.search(r"G:\Min disk\Kunstpixel\docs\ekstern.csv")
    assert "--fra-data" in kommando["cmd"] and "db_kvalitet.py" in kommando["cmd"]


def test_fra_data_bygger_midlertidig_og_rorer_ikke_museum_db(monkeypatch: pytest.MonkeyPatch,
                                                              capsys: pytest.CaptureFixture[str]) -> None:
    fil = kvalitet.bygger.OUT_DB
    for_ = (fil.stat().st_mtime_ns, fil.stat().st_size) if fil.is_file() else None
    monkeypatch.setattr(sys, "argv", ["db_kvalitet.py", "--fra-data"])
    assert kvalitet.main() == 0
    ut = capsys.readouterr().out
    assert "bygget nå fra datafilene" in ut and "RESULTAT:" in ut
    etter = (fil.stat().st_mtime_ns, fil.stat().st_size) if fil.is_file() else None
    assert etter == for_, "museum.db skal ikke endres av --fra-data"
