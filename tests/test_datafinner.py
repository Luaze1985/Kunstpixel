"""Tester for Datafinner — lokal side mellom gründerne og museum.db."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer

import pytest
from src.kunstpixel.adapters.datafinner import DatafinnerHandler, run_tool


def test_run_tool_finner_skrik() -> None:
    rows = run_tool("search_collection", {"title": "Skrik"})
    assert any(r["tittel"] == "Skrik" for r in rows)


def test_run_tool_avviser_ukjent_verktoy() -> None:
    with pytest.raises(ValueError):
        run_tool("drop_table", {})


def test_run_tool_avviser_ukjent_argument() -> None:
    with pytest.raises(ValueError):
        run_tool("search_faq", {"query": "pris", "sql": "DELETE FROM verk"})


def test_run_tool_ignorerer_tomme_argumenter() -> None:
    rows = run_tool("search_collection", {"query": "", "room_id": "SAL-D", "limit": 50})
    assert rows and all(r["sal_id"] == "SAL-D" for r in rows)


@pytest.fixture()
def server_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DatafinnerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _get(url: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url) as res:
            return res.status, res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_api_returnerer_faq(server_url: str) -> None:
    args = urllib.parse.quote(json.dumps({"query": "pris"}))
    status, body = _get(f"{server_url}/api/verktoy?navn=search_faq&args={args}")
    assert status == 200
    data = json.loads(body)
    assert data["verktoy"] == "search_faq"
    assert data["resultat"]


def test_api_avviser_ukjent_verktoy(server_url: str) -> None:
    status, _ = _get(f"{server_url}/api/verktoy?navn=execute_read_query&args=%7B%7D")
    assert status == 400


def test_side_og_stil_serveres(server_url: str) -> None:
    status, body = _get(f"{server_url}/")
    assert status == 200 and b"Datafinner" in body
    status, _ = _get(f"{server_url}/af.css")
    assert status == 200
