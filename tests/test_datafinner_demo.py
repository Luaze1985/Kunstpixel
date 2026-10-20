"""Tester for demomodus og sikkerhetshoder i Datafinner (forberedelse til hosting).

Testgrensen er det en nettleser ser: HTTP-svar fra serveren. Demomodus testes mot en egen
serverprosess, fordi den velges ved oppstart (DATAFINNER_DEMO=1).
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from src.kunstpixel.adapters import datafinner

ROOT = Path(__file__).resolve().parents[1]


def _hent(url: str) -> tuple[int, bytes, dict[str, str]]:
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            return res.status, res.read(), dict(res.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def _ledig_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _start_prosess(demo: bool) -> tuple[subprocess.Popen, str]:
    port = _ledig_port()
    env = {**os.environ, "DATAFINNER_PORT": str(port), "PYTHONIOENCODING": "utf-8"}
    env.pop("DATAFINNER_DEMO", None)
    if demo:
        env["DATAFINNER_DEMO"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "src/kunstpixel/adapters/datafinner.py"], cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(80):
        try:
            _hent(url + "/")
            return proc, url
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(0.25)
    proc.kill()
    raise RuntimeError("Datafinner startet ikke")


@pytest.fixture(scope="module")
def demo_server() -> Iterator[str]:
    proc, url = _start_prosess(demo=True)
    yield url
    proc.kill()
    proc.wait(timeout=10)


@pytest.fixture(scope="module")
def vanlig_server() -> Iterator[str]:
    proc, url = _start_prosess(demo=False)
    yield url
    proc.kill()
    proc.wait(timeout=10)


@pytest.mark.parametrize("navn,args", [("grep_mappe", {"query": "Kunstpixel"}), ("les_fil", {"sti": "00_felles/FORMAAL.md"})])
def test_demomodus_fjerner_filverktoyene(demo_server: str, navn: str, args: dict) -> None:
    status, body, _ = _hent(f"{demo_server}/api/verktoy?navn={navn}&args={urllib.parse.quote(json.dumps(args))}")
    assert status == 400
    assert "Ukjent verktøy" in json.loads(body)["error"]


def test_demomodus_skjuler_filsoket(demo_server: str) -> None:
    assert _hent(f"{demo_server}/sok.html")[0] == 404


def test_demomodus_beholder_demoen(demo_server: str) -> None:
    assert _hent(f"{demo_server}/")[0] == 200
    status, body, _ = _hent(f"{demo_server}/api/verktoy?navn=list_roles&args=%7B%7D")
    assert status == 200 and json.loads(body)["resultat"]


def test_vanlig_modus_har_fortsatt_filverktoyene(vanlig_server: str) -> None:
    """Kontrast: uten DATAFINNER_DEMO virker filsøket som før."""
    assert _hent(f"{vanlig_server}/sok.html")[0] == 200
    args = urllib.parse.quote(json.dumps({"sti": "00_felles/FORMAAL.md"}))
    assert _hent(f"{vanlig_server}/api/verktoy?navn=les_fil&args={args}")[0] == 200


def test_sikkerhetshoder_pa_side_og_api(vanlig_server: str) -> None:
    for sti in ("/", "/af.css", "/api/verktoy?navn=list_roles&args=%7B%7D", "/finnes-ikke"):
        _, _, hoder = _hent(vanlig_server + sti)
        assert hoder["X-Content-Type-Options"] == "nosniff", sti
        assert hoder["X-Frame-Options"] == "DENY", sti
        assert "default-src 'none'" in hoder["Content-Security-Policy"], sti
        assert "frame-ancestors 'none'" in hoder["Content-Security-Policy"], sti


def test_databasefeil_lekker_ikke_detaljer(monkeypatch: pytest.MonkeyPatch) -> None:
    def feiler(navn: str, args: dict) -> None:
        raise RuntimeError(r"unable to open database file C:\Users\hemmelig\museum.db")

    monkeypatch.setattr(datafinner, "run_tool", feiler)
    server = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        status, body, _ = _hent(f"http://127.0.0.1:{server.server_address[1]}/api/verktoy?navn=list_roles&args=%7B%7D")
    finally:
        server.shutdown()
        server.server_close()
    assert status == 500
    tekst = body.decode("utf-8")
    assert "hemmelig" not in tekst and "museum.db" not in tekst and "RuntimeError" not in tekst


def test_bruk_demomodus_endrer_bare_filverktoy_og_soeketside() -> None:
    verktoy = {"grep_mappe": 1, "les_fil": 2, "list_roles": 3}
    sider = {"/": 1, "/sok.html": 2, "/af.css": 3}
    datafinner.bruk_demomodus(verktoy, sider)
    assert verktoy == {"list_roles": 3}
    assert sider == {"/": 1, "/af.css": 3}
