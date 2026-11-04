"""H2: de seks interne verktøyene. Kilde, sti, rollestyring og tåleevne for rare inndata."""

import pytest

from src.kunstpixel.core.intern.data import LEDELSE, ROLLER
from src.kunstpixel.core.intern.tools import TOOL_NAMES, TOOL_TEMA, InternTools
from tests.intern_questions import (
    ARBEIDSOPPGAVER,
    BRANN,
    HISTORIKK_TALL,
    HISTORIKK_TEKST,
    HMS,
    IK,
    MYNDIGHET,
    RAPPORTERING,
    RAPPORTMALER,
    ROSTER,
    TILSYN,
    TILSYNSBESOK,
    TILTAK,
)

SOURCE_OF = {
    "search_hms": {HMS},
    "search_ik_mat": {IK},
    "search_brann_sikring": {BRANN},
    "get_tilsyn": {TILSYN},
    "get_rolle": {ROSTER, "04_knowledge/04_domain/operations/tool_access.md"},
    "search_tiltak": {TILTAK},
    "search_myndighet": {MYNDIGHET, TILSYNSBESOK},
    "search_rapportering": {RAPPORTERING, RAPPORTMALER},
    "search_arbeidsoppgaver": {ARBEIDSOPPGAVER, HISTORIKK_TALL, HISTORIKK_TEKST},
}
QUERY_TOOLS = [
    "search_hms",
    "search_ik_mat",
    "search_brann_sikring",
    "search_myndighet",
    "search_rapportering",
    "search_tiltak",
    "search_arbeidsoppgaver",
]


@pytest.fixture(scope="module")
def tools():
    return InternTools()


def test_tool_registry_is_the_six_read_only_tools():
    assert set(TOOL_NAMES) == set(SOURCE_OF) == set(TOOL_TEMA)


def test_unknown_tool_name_is_rejected(tools):
    with pytest.raises(ValueError):
        tools.call("write_query", "museumsvert", query="x")
    with pytest.raises(ValueError):
        tools.call("search_hms; DROP TABLE", "museumsvert", query="x")


def test_findings_have_source_path_classification_and_score(tools):
    out = tools.search_hms("løft vekt person", "museumsvert")
    assert out["antall"] == len(out["funn"]) >= 1
    for f in out["funn"]:
        assert {"kilde", "sti", "tekst", "tema", "klassifisering", "score"} <= set(f)
        assert 0 < f["score"] <= 1


@pytest.mark.parametrize("tool", QUERY_TOOLS)
@pytest.mark.parametrize("query", ["", "   ", "\n\t", None, 123, ["løft"], {"q": 1}])
def test_empty_or_non_string_query_is_rejected(tools, tool, query):
    out = tools.call(tool, "driftsansvarlig", query=query)
    assert out["code"] == "EMPTY_QUERY" and out["funn"] == []


@pytest.mark.parametrize("tool", TOOL_NAMES)
@pytest.mark.parametrize("bad_role", [None, "", "admin", "gjest", "museumsvert'; DROP TABLE x;--", 42, ["museumsvert"]])
def test_unknown_role_is_refused_by_every_tool(tools, tool, bad_role):
    kwargs = {"maaned": "Mars"} if tool == "get_tilsyn" else {"rolle": "kurator"} if tool == "get_rolle" else {"query": "løft"}
    out = tools.call(tool, bad_role, **kwargs)
    assert out["code"] == "UNKNOWN_ROLE" and out["funn"] == []


@pytest.mark.parametrize("role", ROLLER)
def test_tiltak_access_follows_leadership_rule(tools, role):
    out = tools.search_tiltak("digital formidling ambisjon", role)
    if role in LEDELSE:
        assert out["antall"] >= 1 and out["funn"][0]["kilde"] == TILTAK
    else:
        assert out["code"] == "FORBIDDEN" and out["funn"] == []


@pytest.mark.parametrize("role", ROLLER)
def test_arbeidsoppgaver_access_follows_leadership_rule(tools, role):
    out = tools.search_arbeidsoppgaver("timer tilskuddsrapportering", role)
    if role in LEDELSE:
        assert out["antall"] >= 1 and out["funn"][0]["kilde"] in SOURCE_OF["search_arbeidsoppgaver"]
    else:
        assert out["code"] == "FORBIDDEN" and out["funn"] == []


@pytest.mark.parametrize("tool", QUERY_TOOLS[:-2])
@pytest.mark.parametrize("query", ["brann kapasitet", "løft hansker", "temperatur kjøleskap", "ansvar rolle tilsyn"])
def test_each_tool_only_returns_its_own_sources(tools, tool, query):
    for f in tools.call(tool, "museumsvert", query=query)["funn"]:
        assert f["kilde"] in SOURCE_OF[tool]


@pytest.mark.parametrize("limit,expected_max", [(1, 1), (0, 1), (-5, 1), (2, 2), (1000, 20)])
def test_limit_is_clamped(tools, limit, expected_max):
    out = tools.search_brann_sikring("personer maks", "museumsvert", limit=limit)
    assert 1 <= out["antall"] <= expected_max


def test_get_tilsyn_by_month_is_case_and_spelling_insensitive(tools):
    for m in ("Mars", "mars", "MARS", " mars "):
        out = tools.get_tilsyn("kurator", maaned=m)
        assert out["antall"] == 1 and out["funn"][0]["sti"].endswith("Mars")
    assert tools.get_tilsyn("kurator", maaned="Smarch")["antall"] == 0


def test_get_tilsyn_requires_month_or_query(tools):
    assert tools.get_tilsyn("kurator")["code"] == "EMPTY_QUERY"
    assert tools.get_tilsyn("kurator", query="  ")["code"] == "EMPTY_QUERY"


def test_get_tilsyn_free_text(tools):
    out = tools.get_tilsyn("kurator", query="Mattilsynet hygiene")
    assert out["antall"] >= 1 and "Mattilsynet" in out["funn"][0]["tekst"]


def test_get_rolle_by_name_returns_only_that_role(tools):
    out = tools.get_rolle("museumsvert", rolle="Kvalitetsvokter")
    assert out["antall"] >= 4
    assert all(f["rolle"] == "kvalitetsvokter" for f in out["funn"])


def test_get_rolle_unknown_role_name_is_empty_not_error(tools):
    assert tools.get_rolle("museumsvert", rolle="Sjef")["antall"] == 0


def test_get_rolle_needs_role_or_query(tools):
    assert tools.get_rolle("museumsvert")["code"] == "EMPTY_QUERY"


@pytest.mark.parametrize("tool", QUERY_TOOLS)
@pytest.mark.parametrize(
    "hostile",
    ["'; DROP TABLE verk; --", "../../etc/passwd", "05_data/museum.db", "{{7*7}}", "<script>alert(1)</script>", "A" * 20000, "\x00\x01\x02", "💥" * 50],
    ids=["sql", "sti", "db-fil", "mal", "script", "veldig-lang", "kontrolltegn", "emoji"],
)
def test_hostile_queries_never_crash_or_leak(tools, tool, hostile):
    out = tools.call(tool, "driftsansvarlig", query=hostile)
    assert "funn" in out
    assert all(f["kilde"] in SOURCE_OF[tool] for f in out["funn"])


def test_tools_do_not_mutate_state(tools):
    a = tools.search_hms("løft", "museumsvert")
    n = len(tools.data.findings)
    b = tools.search_hms("løft", "museumsvert")
    assert a == b and len(tools.data.findings) == n


def test_tool_result_is_plain_json_serialisable(tools):
    import json

    for name in TOOL_NAMES:
        kwargs = {"maaned": "Mars"} if name == "get_tilsyn" else {"rolle": "kurator"} if name == "get_rolle" else {"query": "løft"}
        json.dumps(tools.call(name, "museumsdirektor", **kwargs), ensure_ascii=False)
