"""Helsesjekken skal måle hva demo-Claude faktisk når via MCP, ikke bare om et tabellnavn står i src/."""

import importlib.util
import textwrap
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("sjekk_kunnskapsgraf", ROT / "scripts" / "sjekk_kunnskapsgraf.py")
skg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(skg)


def _skriv(mappe: Path, navn: str, kode: str) -> Path:
    p = mappe / navn
    p.write_text(textwrap.dedent(kode), encoding="utf-8")
    return p


def test_bare_tabeller_som_et_verktoy_leser_telles(tmp_path):
    db = _skriv(tmp_path, "db.py", """
        SQL_C = "SELECT * FROM tabell_c"

        def les_a():
            return hjelper()

        def hjelper():
            return "SELECT * FROM tabell_a"

        def les_b():
            return "SELECT * FROM tabell_b"

        def les_c():
            return SQL_C
    """)
    mcp = _skriv(tmp_path, "mcp_server.py", """
        from db import les_a, les_b, les_c

        @mcp.tool()
        def verktoy_a():
            return les_a()

        @mcp.tool()
        def verktoy_c():
            return les_c()

        def ikke_verktoy():
            return les_b()
    """)
    tabeller = ["tabell_a", "tabell_b", "tabell_c", "tabell_d"]
    assert skg.tabeller_via_mcp(tabeller, mcp, [db, mcp]) == {"tabell_a", "tabell_c"}


def test_ekte_mcp_server_naar_kjente_tabeller():
    tabeller = ["hr_vakter", "driftsmeldinger_epost", "verk", "finnes_ikke_tabell"]
    funnet = skg.tabeller_via_mcp(tabeller, skg.MCP_PATH, skg.kodefiler_for_mcp())
    assert {"hr_vakter", "driftsmeldinger_epost", "verk"} <= funnet
    assert "finnes_ikke_tabell" not in funnet


def test_analysen_skiller_mcp_fra_resten_av_src():
    import sqlite3

    con = sqlite3.connect(skg.DB_PATH.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        analyse = skg.analyser_database(con)
    finally:
        con.close()
    blinde_mcp = {t for t, _ in analyse["usynlige_for_mcp"]}
    blinde_src = {t for t, _ in analyse["usynlige_for_llm"]}
    assert blinde_src <= blinde_mcp
    alle = {t["tabell"] for t in analyse["tabeller"]}
    via_mcp = {t["tabell"] for t in analyse["tabeller"] if t["via_mcp"]}
    assert via_mcp | blinde_mcp == alle
