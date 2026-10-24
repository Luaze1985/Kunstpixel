"""Tester for den samlede kvalitetsrapporten og at sjekkene er stille."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import kvalitetsrapport as rapport  # noqa: E402


def test_hver_sjekk_erstatter_bare_sin_egen_seksjon(tmp_path: Path) -> None:
    sti = tmp_path / "RAPPORT.md"
    rapport.oppdater("apning", "OBS", "to ting å se på", sti, datetime(2026, 10, 24, 9, 0))
    rapport.oppdater("commit", "OK", "KLAR for sammenslåing", sti, datetime(2026, 10, 24, 9, 5))
    rapport.oppdater("apning", "OK", "alt i orden", sti, datetime(2026, 10, 24, 10, 0))

    data = rapport.les(sti)
    assert data["apning"] == ("OK", "2026-10-24 10:00", "alt i orden")
    assert data["commit"] == ("OK", "2026-10-24 09:05", "KLAR for sammenslåing")
    assert "lagring" not in data
    tekst = sti.read_text(encoding="utf-8")
    assert "| Når en datafil i 05_data lagres (bygget fra datafilene) | ikke kjørt ennå | **-** |" in tekst
    assert tekst.count("<!-- seksjon:apning") == 1


def test_ukjent_seksjon_eller_status_avvises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        rapport.oppdater("tull", "OK", "x", tmp_path / "R.md")
    with pytest.raises(ValueError):
        rapport.oppdater("apning", "GRONN", "x", tmp_path / "R.md")


def test_kodeblokk_i_innhold_odelegger_ikke_rapporten(tmp_path: Path) -> None:
    sti = tmp_path / "RAPPORT.md"
    rapport.oppdater("lagring", "FEIL", "noe ```rart``` her", sti)
    rapport.oppdater("apning", "OK", "fint", sti)
    assert set(rapport.les(sti)) == {"lagring", "apning"}


def test_db_kvalitet_skriver_stille_til_rapporten(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                  capsys: pytest.CaptureFixture[str]) -> None:
    import db_kvalitet

    sti = tmp_path / "RAPPORT.md"
    monkeypatch.setattr(rapport, "RAPPORT", sti)
    monkeypatch.setattr(rapport.oppdater, "__defaults__", (sti, None))
    monkeypatch.setattr(sys, "argv", ["db_kvalitet.py", "--fra-data", "--stille", "--rapport", "lagring"])
    assert db_kvalitet.main() == 0
    assert capsys.readouterr().out == "", "--stille skal ikke vise noe"
    status, _, tekst = rapport.les(sti)["lagring"]
    assert status in ("OK", "OBS") and "RESULTAT:" in tekst


def _uten_kommentarer(sti: Path) -> dict:
    return json.loads(re.sub(r"^\s*//.*$", "", sti.read_text(encoding="utf-8"), flags=re.M))


def test_vscode_sjekkene_er_stille_og_skriver_rapport() -> None:
    oppgave = next(o for o in _uten_kommentarer(ROOT / ".vscode" / "tasks.json")["tasks"]
                   if o.get("runOptions", {}).get("runOn") == "folderOpen")
    assert oppgave["presentation"]["reveal"] == "never"
    assert "--stille" in oppgave["command"] and "--rapport apning" in oppgave["command"]

    lagring = _uten_kommentarer(ROOT / ".vscode" / "settings.json")["emeraldwalk.runonsave"]["commands"][0]
    assert lagring["autoShowOutputPanel"] == "never"
    assert "--stille" in lagring["cmd"] and "--rapport lagring" in lagring["cmd"]


def test_commit_kontrollen_skriver_rapport_og_er_stille_ved_suksess() -> None:
    krok = (ROOT / "scripts" / "githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "kvalitetsrapport.py commit" in krok
    forut, stopp = krok.rsplit("if [ $kode -ne 0 ]; then", 1)
    kode_for = "\n".join(linje for linje in forut.splitlines() if not linje.lstrip().startswith("#"))
    assert "echo" not in kode_for and ">&2" not in kode_for, "meldinger skal bare vises når commiten stoppes"
    assert ">&2" in stopp and "exit 1" in stopp
