"""Aktiv database må være den validerte databasen før Claude åpnes."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import db_status_gate as gate


@pytest.mark.parametrize("innhold,forventet", [(b"samme", gate.OK), (b"annerledes", gate.FEIL)])
def test_aktiv_db_sammenlignes_med_validert_bygg(tmp_path: Path, innhold: bytes, forventet: str) -> None:
    bygd = tmp_path / "bygd.db"
    aktiv = tmp_path / "aktiv.db"
    bygd.write_bytes(b"samme")
    aktiv.write_bytes(innhold)
    gate.resultater.clear()
    gate.sjekk_aktiv_db(bygd, aktiv)
    assert gate.resultater[-1][1] == forventet


def test_manglende_aktiv_db_blokkerer(tmp_path: Path) -> None:
    bygd = tmp_path / "bygd.db"
    bygd.write_bytes(b"samme")
    gate.resultater.clear()
    gate.sjekk_aktiv_db(bygd, tmp_path / "mangler.db")
    assert gate.resultater[-1][1] == gate.FEIL


def test_kort_oppstartsvisning_beholder_feil_og_varsler(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(gate, "KORT", True)
    gate.logg("P1 bygg", gate.OK, "ok")
    gate.logg("P0 aktiv museum.db", gate.OK, "lik")
    gate.logg("P6 kjent avvik", gate.ADVARSEL, "7 kjente")
    tekst = capsys.readouterr().out
    assert "P1 bygg" not in tekst
    assert "P0 aktiv museum.db" in tekst
    assert "7 kjente" in tekst


def test_cmd_bevarer_feilkode_fra_claude_cmd(tmp_path: Path) -> None:
    (tmp_path / "claude.cmd").write_text("@echo off\r\necho MOCK_CLAUDE\r\nexit /b 7\r\n", encoding="ascii")
    env = os.environ.copy()
    env["PATH"] = str(tmp_path) + os.pathsep + env["PATH"]
    run = subprocess.run(
        f'cmd.exe /d /c call "{ROOT / "start_claude.cmd"}" --version',
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        input="\n",
        timeout=15,
    )
    assert run.returncode == 7, run.stdout + run.stderr
    assert "MOCK_CLAUDE" in run.stdout
    assert "Claude avsluttet med kode 7" in run.stdout
