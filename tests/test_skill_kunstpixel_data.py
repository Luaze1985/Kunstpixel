"""Tall-vakt for skillen kunstpixel-data (oppgave 01, 02 og 04, 2026-11-17).

Hver påstand i skillen sjekkes mot museum.db. Testen feiler hvis databasen bygges på nytt og et tall i
skillen ikke lenger stemmer, eller hvis noen endrer tallet i skillen uten at dataene har endret seg.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from src.kunstpixel.core import arena

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "kunstpixel-data"
TEKST = "\n".join(p.read_text(encoding="utf-8") for p in sorted(SKILL.rglob("*.md")))

_KL = "(CAST(substr({0},1,2) AS REAL)+CAST(substr({0},4,2) AS REAL)/60)"
_HVILEBRUDD = f"""SELECT count(*) FROM (
  SELECT dato, start, lag(dato) OVER w AS fdato, lag(slutt) OVER w AS fslutt
  FROM hr_vakter WINDOW w AS (PARTITION BY ansatt_id ORDER BY dato, start))
  WHERE fdato IS NOT NULL
    AND ((julianday(dato) - julianday(fdato)) * 24 + {_KL.format('start')} - {_KL.format('fslutt')})
        < (SELECT verdi FROM arbeidstid_grenser WHERE navn = 'daglig_hvile_timer')"""


def _tall(n: int) -> str:
    return f"{n:,}".replace(",", " ")


# (tekst i skillen, SQL som gir tallet, hvordan tallet skrives i teksten)
PAASTANDER = [
    ("nåværende: {} av {}", "SELECT (SELECT count(*) FROM hr_ansatte WHERE status <> 'Sluttet'), (SELECT count(*) FROM hr_ansatte)"),
    ("`status = 'Sluttet'` og `ansatt_til` satt, {} personer", "SELECT count(*) FROM hr_ansatte WHERE status = 'Sluttet'"),
    ("{} navn deles av to ansatte", "SELECT count(*) FROM (SELECT navn FROM hr_ansatte GROUP BY navn HAVING count(*) = 2)"),
    ("Dataene går til `{}`", "SELECT max(dato) FROM dagsbesok"),
    ("{} hviletidsbrudd", _HVILEBRUDD),
    ("{} vakter over døgnmaks", "SELECT count(*) FROM hr_vakter WHERE timer > (SELECT verdi FROM arbeidstid_grenser WHERE navn = 'dognmaks_timer')"),
    ("{} dager har `er_aapent = 0` og 0 besøk", "SELECT count(*) FROM dagsbesok WHERE er_aapent = 0 AND besok_totalt = 0"),
    ("{} av {} utstillinger har ingen anmeldelser", """SELECT sum(n = 0), count(*) FROM (SELECT count(a.utstilling_id) n
        FROM utstillinger_historikk u LEFT JOIN anmeldelser a USING (utstilling_id) GROUP BY u.utstilling_id)"""),
    ("{} av {} har ingen", """SELECT sum(n = 0), count(*) FROM (SELECT count(a.utstilling_id) n
        FROM utstillinger_historikk u LEFT JOIN anmeldelser a USING (utstilling_id) GROUP BY u.utstilling_id)"""),
    # Oppgave 03: vakter der timer ikke er slutt − start − lunsj, og hvor mange av dem som er over døgnmaks.
    ("men {} vakter avviker. {} av dem er døgnmaks-vaktene", f"""SELECT count(*), sum(timer > (SELECT verdi FROM arbeidstid_grenser WHERE navn = 'dognmaks_timer'))
        FROM hr_vakter WHERE abs(timer - ({_KL.format('slutt')} - {_KL.format('start')}
        - (SELECT verdi FROM arbeidstid_grenser WHERE navn = 'lunsj_timer'))) > 0.01"""),
    ("`KP-INN-Pxx`, {} personer", "SELECT count(*) FROM hr_innleide_personer"),
    ("`KP-EXH-2026-FOKUS-2` = {} kr", "SELECT netto_resultat_nok FROM utstilling_okonomi WHERE utstilling_id = 'KP-EXH-2026-FOKUS-2'"),
    # Oppgave 01: «ansatte» er nåværende (D1), så «uten vakter» må telles på nåværende.
    ("{} nåværende ansatte har ingen vakter ({} med sluttede)", """SELECT
        (SELECT count(*) FROM hr_ansatte a WHERE status <> 'Sluttet' AND NOT EXISTS (SELECT 1 FROM hr_vakter v WHERE v.ansatt_id = a.ansatt_id)),
        (SELECT count(*) FROM hr_ansatte a WHERE NOT EXISTS (SELECT 1 FROM hr_vakter v WHERE v.ansatt_id = a.ansatt_id))"""),
]


@pytest.mark.parametrize("mal,sql", PAASTANDER, ids=[p[0][:40] for p in PAASTANDER])
def test_tallet_i_skillen_stemmer_med_databasen(db_conn: sqlite3.Connection, mal: str, sql: str) -> None:
    rad = db_conn.execute(sql).fetchone()
    forventet = mal.format(*[_tall(v) if isinstance(v, int) else v for v in rad])
    assert forventet in TEKST, f"Skillen skal si «{forventet}» (fra databasen nå)"


def test_navnelikhet_og_personalmappe(db_conn: sqlite3.Connection) -> None:
    anja = sorted(r[0] for r in db_conn.execute("SELECT ansatt_id FROM hr_ansatte WHERE navn = 'Anja Eriksen'"))
    assert anja == ["KP-ANS-047", "KP-ANS-115"] and "`KP-ANS-047`, `KP-ANS-115`" in TEKST
    uten = [r[0] for r in db_conn.execute(
        "SELECT a.ansatt_id FROM hr_ansatte a LEFT JOIN hr_personalmapper p USING (ansatt_id) WHERE p.ansatt_id IS NULL")]
    assert uten == ["KP-ANS-155"] and "`KP-ANS-155` har ingen personalmappe" in TEKST


# ---------- Oppgave 02: ekte og syntetisk som i koden (arena.datamerke) ----------

def _tabeller(db_conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in db_conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name <> 'sqlite_sequence'")]


def test_offentlige_tabeller_i_skillen_er_de_koden_merker_offentlige(db_conn: sqlite3.Connection) -> None:
    linje = next((l for l in TEKST.splitlines() if "**Offentlige data:**" in l), "")
    i_skillen = set(re.findall(r"`([a-z0-9_]+)`", linje.split("Resten")[0]))
    i_koden = {m["tabell"] for m in arena.datamerke(_tabeller(db_conn)) if m["merke"] == "offentlig"}
    assert i_skillen and i_skillen == i_koden


def test_skillen_sier_ikke_at_alle_rader_er_syntetiske() -> None:
    assert "alle rader er syntetiske" not in TEKST


def test_antall_umerkede_tabeller_stemmer(db_conn: sqlite3.Connection) -> None:
    merker = [m["merke"] for m in arena.datamerke(_tabeller(db_conn))]
    assert f"{merker.count('umerket')} tabeller har ingen `datakilde`-kolonne" in TEKST
    assert f"{merker.count('syntetisk')} tabeller har `datakilde LIKE 'syntetisk%'`" in TEKST


# ---------- Oppgave 04: «i år» uten fast årstall ----------

def test_i_aar_har_ikke_fast_aarstall(db_conn: sqlite3.Connection) -> None:
    from datetime import date

    assert "'2026-01-01'" not in TEKST, "Bruk date('now','localtime','start of year'), så SQL-en virker også neste år"
    assert "date('now','localtime','start of year')" in TEKST
    assert db_conn.execute("SELECT date('now','localtime','start of year')").fetchone()[0] == f"{date.today().year}-01-01"
