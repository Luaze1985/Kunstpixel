"""Vakttest: det gamle navnet «Aura» skal ikke dukke opp igjen (DECISIONS 2026-11-09, punkt 10).

Sjekker alle sporede tekstfiler, alle filnavn og tekstcellene i museum.db og kilde/museum_base.db.
Ordgrense holder «Laura» og «restaurant» utenfor.
"""

from __future__ import annotations

import re
import sqlite3
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Ordet bygges opp, så denne filen ikke treffer seg selv.
ORD = "au" + "ra"
MONSTER = re.compile(rf"(?<![A-Za-zÆØÅæøå]){ORD}(?![A-Za-zÆØÅæøå])", re.IGNORECASE)

# Filer som må nevne navnet: beslutningsloggen, byttemanuset og denne testen.
TILLATT = {
    "docs/DECISIONS.md",
    "scripts/fjern_" + ORD + ".py",
    "tests/test_ingen_" + ORD + ".py",
}


def _sporede_filer() -> list[str]:
    ut = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    return [p for p in ut.decode("utf-8").split("\0") if p]


def test_ingen_filnavn_med_gammelt_navn() -> None:
    treff = [p for p in _sporede_filer() if MONSTER.search(p) and p not in TILLATT]
    assert treff == [], f"Filnavn med gammelt navn: {treff[:20]}"


def test_ingen_tekstfiler_med_gammelt_navn() -> None:
    treff = []
    for rel in _sporede_filer():
        if rel in TILLATT:
            continue
        sti = ROOT / rel
        if not sti.is_file():
            continue
        data = sti.read_bytes()
        if b"\0" in data[:8192]:
            continue  # binærfil, databasene sjekkes for seg
        tekst = data.decode("utf-8", errors="replace")
        for linje_nr, linje in enumerate(tekst.splitlines(), 1):
            if MONSTER.search(linje):
                treff.append(f"{rel}:{linje_nr}: {linje.strip()[:100]}")
    assert treff == [], f"{len(treff)} treff, de første:\n" + "\n".join(treff[:30])


@pytest.mark.parametrize("db", ["05_data/museum.db", "05_data/kilde/museum_base.db"])
def test_ingen_databaseceller_med_gammelt_navn(db: str) -> None:
    con = sqlite3.connect(f"file:{ROOT / db}?mode=ro", uri=True)
    try:
        treff = []
        tabeller = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
        for t in tabeller:
            if MONSTER.search(t):
                treff.append(f"tabellnavn {t}")
            kolonner = [r[1] for r in con.execute(f"pragma table_info([{t}])")]
            for k in kolonner:
                if MONSTER.search(k):
                    treff.append(f"kolonnenavn {t}.{k}")
                for (verdi,) in con.execute(
                    f"select [{k}] from [{t}] where cast([{k}] as text) like ?", (f"%{ORD}%",)
                ):
                    if isinstance(verdi, str) and MONSTER.search(verdi):
                        treff.append(f"{t}.{k}: {verdi[:80]}")
    finally:
        con.close()
    assert treff == [], f"{len(treff)} treff i {db}, de første:\n" + "\n".join(treff[:20])
