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


def test_grep_mappe_finner_tekst_i_knowledge() -> None:
    hits = run_tool("grep_mappe", {"query": "Kunstpixel", "mappe": "04_knowledge"})
    assert hits and all(h["sti"].startswith("04_knowledge/") for h in hits)


def test_grep_mappe_avviser_ukjent_mappe() -> None:
    with pytest.raises(ValueError):
        run_tool("grep_mappe", {"query": "x", "mappe": "src"})


def test_les_fil_leser_formaal() -> None:
    data = run_tool("les_fil", {"sti": "00_felles/FORMAAL.md"})
    assert data["tekst"]


@pytest.mark.parametrize("sti", ["../AGENTS.md", "AGENTS.md", "05_data/museum.db", "00_felles/../src/mcp_server.py"])
def test_les_fil_avviser_stier_utenfor_mappene(sti: str) -> None:
    with pytest.raises(ValueError):
        run_tool("les_fil", {"sti": sti})


@pytest.mark.parametrize(
    "navn,args",
    [
        ("get_staff_on_shift", {"dato": "2026-10-19"}),
        ("get_shifts_for_date", {"dato": "2026-10-20"}),
        ("get_working_hours_report", {"maaned": "2026-09"}),
        ("get_sickness_absence_statistics", {"year": 2025, "quarter": 2}),
        ("get_exhibition_economy", {"exhibition_id": "KP-EXH-2026-065"}),
        ("get_shift_cost_for_period", {"maaned": "2026-09"}),
        ("list_exhibitions_with_economy", {}),
        ("get_absence_report", {"aar": 2025, "kvartal": 2}),
        ("list_roles", {}),
        ("get_report_assessment", {"sporsmal_id": "vakt-i-dag", "verdier": {"antall_med_vakt": 9}}),
    ],
)
def test_api_svarer_paa_hr_og_okonomi(server_url: str, navn: str, args: dict) -> None:
    q = urllib.parse.quote(json.dumps(args))
    status, body = _get(f"{server_url}/api/verktoy?navn={navn}&args={q}")
    assert status == 200, body
    assert json.loads(body)["resultat"]


def test_utstillingsliste_dekker_alle_med_okonomi() -> None:
    assert len(run_tool("list_exhibitions_with_economy", {})) == 102
