"""Bygg storskjerm-dashbordet (spec docs/specs/2026-11-19-storskjerm-dashbord.md og -chat.md).

Skriver fire filer: storskjerm.html (malen i deploy/claude-app/ med af.css lagt inn, fordi artifacts ikke
kan hente stilark fra andre steder), data.json (tallene fra core/storskjerm.py), og til KI-chatten
museum.db.gz.txt (databasen pakket med gzip og skrevet som base64, fordi artifacts ikke tar .gz) og
chat-instruks.txt (reglene Claude får før hvert spørsmål). Claude Code publiserer dem som én artifact.

Bruk:
    py -3.13 scripts/lag_storskjerm.py                 # skriver til .scratch/claude-app/
    py -3.13 scripts/lag_storskjerm.py --ut C:\\temp
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.kunstpixel.core.storskjerm import lag_storskjerm

MAL = ROOT / "deploy" / "claude-app" / "storskjerm.html"
AF_CSS = ROOT / "src" / "kunstpixel" / "adapters" / "datafinner" / "af.css"
PLASSHOLDER = "/*AF_CSS*/"
DB = ROOT / "05_data" / "museum.db"
SKILL = ROOT / "deploy" / "claude-app" / "SKILL.md"
REFERANSER = ROOT / ".claude" / "skills" / "kunstpixel-data" / "references"

# Det som bare gjelder chatten i appen. Resten av instruksen hentes fra skillen, så reglene er like.
CHAT_HODE = """Du er KI-chat i Kunstpixels app «Kunstpixel i dag». Du svarer Lars, som er museumsdirektør, på spørsmål om det fiktive kunstmuseet Kunstpixel. Svar på norsk.

I DAG er {idag}. Tallene er et bilde av databasen per denne datoen. Bruk alltid '{idag}' som «i dag» i SQL, og '{aarstart}' som start på året. Bruk ALDRI maskinens dato (now, localtime eller CURRENT_DATE).

Du har verktøyet sql, som kjører én lesende SQLite-spørring (SELECT eller WITH) mot hele museum.db og gir maks 200 rader. Alle tall skal hentes med sql. Gjett aldri et tall. Du har få runder med verktøy: send uavhengige spørringer samtidig i samme runde, og bruk tabelloversikten under i stedet for å lete.

Format i appen: ren tekst, ingen markdown (ingen ** eller #, ingen tabeller). Svaret først i 1–3 linjer, siste tekstlinje er «Kilde: <tabell>».

Diagram: når svaret sammenligner flere tall (over tid, per utstilling, per avdeling), legg til helt til slutt én linje: DIAGRAM: {{"tittel": "...", "etiketter": ["..."], "verdier": [1, 2], "enhet": "kr"}} (maks 12 verdier, gyldig JSON, tall uten mellomrom).

Valg: når du spør hvilken av flere ting Lars mener, legg til helt til slutt én linje: VALG: ["første", "andre"] (maks 5 korte valg, gyldig JSON). Lars trykker på et valg, og teksten sendes som hans svar.
"""


def _fast_dato(tekst: str, idag: str) -> str:
    """Bytt maskinens dato i SQL-eksemplene med datoen tallene gjelder (spec: «Datoregel»)."""
    tekst = tekst.replace("date('now','localtime','start of year')", f"'{idag[:4]}-01-01'")
    tekst = tekst.replace("date('now','localtime')", f"'{idag}'")
    return re.sub(r"date\('now','localtime',", f"date('{idag}',", tekst)


def chat_instruks(con: sqlite3.Connection, idag: str) -> str:
    from scripts.lag_claude_skill import (
        kjente_hull,  # samme hull-liste som skill-pakken
    )

    skill = SKILL.read_text(encoding="utf-8")
    regler = skill[skill.index("## Definisjoner"):]
    regler = regler.split("\nMerk: i Claude-appen", 1)[0]
    tabeller = []
    for (navn,) in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        kolonner = ", ".join(r[1] for r in con.execute(f'PRAGMA table_info("{navn}")'))
        tabeller.append(f"- {navn}({kolonner})")
    deler = [
        CHAT_HODE.format(idag=idag, aarstart=idag[:4] + "-01-01"),
        regler.rstrip() + "\n",
        "# Kjente hull\n" + kjente_hull(con, date.fromisoformat(idag)),
        "# metrics.md\n" + (REFERANSER / "metrics.md").read_text(encoding="utf-8"),
        "# entities.md\n" + (REFERANSER / "entities.md").read_text(encoding="utf-8"),
        "# Alle tabeller med kolonner\n" + "\n".join(tabeller) + "\n",
    ]
    return _fast_dato("\n\n".join(deler), idag)


def bygg(ut: Path, dato: str | None = None) -> tuple[Path, Path]:
    dato = dato or date.today().isoformat()
    mal = MAL.read_text(encoding="utf-8")
    if mal.count(PLASSHOLDER) != 1:
        raise SystemExit(f"STOPP: malen må ha {PLASSHOLDER} nøyaktig én gang.")
    ut.mkdir(parents=True, exist_ok=True)
    side = ut / "storskjerm.html"
    data = ut / "data.json"
    side.write_text(mal.replace(PLASSHOLDER, AF_CSS.read_text(encoding="utf-8")), encoding="utf-8")
    data.write_text(json.dumps(lag_storskjerm(dato), ensure_ascii=False, indent=1), encoding="utf-8")
    # KI-chatten: samme database som tallene over, pakket så den kan publiseres som tekst.
    raa = DB.read_bytes()
    (ut / "museum.db.gz.txt").write_text(base64.b64encode(gzip.compress(raa, mtime=0)).decode("ascii"), encoding="ascii")
    with sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True) as con:
        (ut / "chat-instruks.txt").write_text(chat_instruks(con, dato), encoding="utf-8")
    return side, data


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Bygg storskjerm-dashbordet")
    p.add_argument("--ut", type=Path, default=ROOT / ".scratch" / "claude-app", help="mappe for filene")
    a = p.parse_args(argv)
    side, data = bygg(a.ut)
    print(f"OK: {side}\n    {data}\n    {side.parent / 'museum.db.gz.txt'}\n    {side.parent / 'chat-instruks.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
