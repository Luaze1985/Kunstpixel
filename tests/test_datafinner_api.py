"""Tester for det åpne API-et: verktøyskjema og deterministiske rapporter (ingen KI)."""

from __future__ import annotations

import json
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from src.kunstpixel.adapters import datafinner, datafinner_api

ROOT = Path(__file__).resolve().parents[1]

EKSEMPEL_ARGS = {
    "vakt-i-dag": {},
    "vaktplan": {"dato": "2026-10-20"},
    "arbeidstid": {"maaned": "2026-09"},
    "sykefravaer": {"aar": 2025, "kvartal": 2},
    "utstilling": {"exhibition_id": "KP-EXH-2026-FOKUS-2"},
    "vaktkostnad": {"maaned": "2026-09"},
}


@pytest.fixture()
def server() -> Iterator[str]:
    s = ThreadingHTTPServer(("127.0.0.1", 0), datafinner.DatafinnerHandler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_address[1]}"
    s.shutdown()
    s.server_close()


def _get(url: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(url, timeout=20) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _rapport_url(server: str, sporsmal: str, args: dict) -> str:
    return f"{server}/api/rapport?sporsmal={sporsmal}&args={urllib.parse.quote(json.dumps(args))}"


# ---------- verktøyskjema ----------

def test_skjemaet_dekker_alle_hvitelistede_verktoy(server: str) -> None:
    status, data = _get(f"{server}/api/verktoyskjema")
    assert status == 200
    navn = {v["navn"] for v in data["verktoy"]}
    assert navn == set(datafinner.VERKTOY)


def test_skjemaet_er_gyldig_json_schema_pa_parametrene() -> None:
    skjema = {v["navn"]: v for v in datafinner_api.verktoyskjema(datafinner.VERKTOY)}
    absence = skjema["get_absence_report"]["parametre"]
    assert absence["type"] == "object" and absence["additionalProperties"] is False
    assert absence["properties"]["aar"]["type"] == "integer"
    assert set(absence["required"]) == {"aar", "kvartal"}
    assert "Årstall" in absence["properties"]["aar"]["description"]
    assert skjema["get_absence_report"]["beskrivelse"]
    # Valgfrie parametere (har standardverdi) er ikke påkrevd.
    assert "dato" not in skjema["get_staff_on_shift"]["parametre"]["required"]
    for v in skjema.values():
        for egenskap in v["parametre"]["properties"].values():
            assert egenskap["type"] in {"string", "integer", "number", "boolean", "object", "array"}


# ---------- deterministiske rapporter ----------

@pytest.mark.parametrize("sporsmal", sorted(EKSEMPEL_ARGS))
def test_rapporten_er_deterministisk_og_har_regel_og_merker(server: str, sporsmal: str) -> None:
    url = _rapport_url(server, sporsmal, EKSEMPEL_ARGS[sporsmal])
    (s1, a), (s2, b) = _get(url), _get(url)
    assert s1 == s2 == 200
    assert a == b, "Samme input skal gi nøyaktig samme rapport"
    assert a["vurdering"]["regel_id"] and a["vurdering"]["vurdering"] and a["vurdering"]["forslag"]
    assert a["merker"] == {"fakta": "Bør verifiseres", "vurdering": "Systemforslag", "forslag": "Systemforslag"}
    assert a["status"] == "Utkast"
    assert a["fakta"]


def test_vaktplanen_telles_for_regelen(server: str) -> None:
    _, r = _get(_rapport_url(server, "vaktplan", EKSEMPEL_ARGS["vaktplan"]))
    assert r["regelverdier"] == {"antall_vakter": len(r["fakta"])}


def test_ukjent_sporsmal_og_ukjent_argument_gir_400(server: str) -> None:
    status, data = _get(_rapport_url(server, "finnes-ikke", {}))
    assert status == 400 and "Gyldige" in data["error"]
    status, data = _get(_rapport_url(server, "vaktplan", {"dato": "2026-10-20", "sql": "DROP TABLE x"}))
    assert status == 400 and "sql" in data["error"]


def test_status_sier_at_kilaget_er_av(server: str) -> None:
    status, data = _get(f"{server}/api/status")
    assert status == 200 and data["llm"] is False and data["llm_modell"] is None


def test_forklar_gir_503_nar_kilaget_er_av(server: str) -> None:
    req = urllib.request.Request(f"{server}/api/forklar", data=b'{"sporsmal":"vaktplan"}', headers={"Content-Type": "application/json"}, method="POST")
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req, timeout=10)
    assert e.value.code == 503


# ---------- vokter mot at listene glir fra hverandre ----------

def test_sporsmalene_i_api_hjemmesiden_og_databasen_er_de_samme() -> None:
    import sqlite3
    html = (ROOT / "src/kunstpixel/adapters/datafinner/index.html").read_text(encoding="utf-8")
    i_html = set(re.findall(r'\{ id: "([a-z-]+)", tekst:', html))
    con = sqlite3.connect((ROOT / "05_data/museum.db").resolve().as_uri() + "?mode=ro", uri=True)
    try:
        i_db = {r[0] for r in con.execute("SELECT sporsmal_id FROM rolle_sporsmal")}
        i_regler = {r[0] for r in con.execute("SELECT DISTINCT sporsmal_id FROM rapport_regler")}
    finally:
        con.close()
    assert set(datafinner_api.SPORSMAL) == i_html == i_db == i_regler


def test_hvert_sporsmal_peker_pa_et_hvitelistet_verktoy() -> None:
    for spec in datafinner_api.SPORSMAL.values():
        assert spec["verktoy"] in datafinner.VERKTOY
