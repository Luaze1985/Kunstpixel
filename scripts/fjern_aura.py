"""Bytt det gamle navnet «Aura» med «Kunstpixel» / «KP-» (DECISIONS 2026-11-09, punkt 10).

Deterministisk: faste regler i fast rekkefølge, lengste mønster først. Ingen fallback-regel,
så alt som ikke dekkes, skrives ut som rest og må vurderes for hånd.

    py -3.13 scripts/fjern_aura.py --tekst          # sporede tekstfiler + filnavn (git mv)
    py -3.13 scripts/fjern_aura.py --db STI.db      # tekstceller i en SQLite-database
    py -3.13 scripts/fjern_aura.py --rest           # skriv ut det som fortsatt treffer

Tekstfiler leses og skrives som bytes, så linjeskift og koding beholdes.
museum.db skal ikke endres her: den bygges av build_museum_db.py fra kilde/museum_base.db.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"docs/DECISIONS.md", "scripts/fjern_aura.py", "tests/test_ingen_aura.py"}
GUARD = re.compile(r"(?<![A-Za-zÆØÅæøå])aura(?![A-Za-zÆØÅæøå])", re.IGNORECASE)


def _id_prefiks(m: re.Match[str]) -> str:
    """AURA- → KP-, aura- → kp-, blandet (AuRa-) → Kp-. Bevarer skrivemåten i case-tester."""
    ord_ = m.group(1)
    if ord_.isupper():
        return "KP-"
    if ord_.islower():
        return "kp-"
    return "Kp-"


# (mønster, erstatning). Rekkefølgen betyr noe: lengste og mest spesifikke først.
REGLER: list[tuple[re.Pattern[str], object]] = [
    (re.compile(r"Aura Kunstmuseum \(Kunstpixel\)"), "Kunstpixel"),
    (re.compile(r"Aura Kunstmuseums\b"), "Kunstpixels"),
    (re.compile(r"Aura Kunstmuseum\b"), "Kunstpixel"),
    (re.compile(r"Aura Museum\b"), "Kunstpixel"),
    (re.compile(r"Aura Museumsvert\b"), "Kunstpixel Museumsvert"),
    (re.compile(r"Aura Bokhandel\b"), "Kunstpixel Bokhandel"),
    (re.compile(r"Aura MCP Server\b"), "Kunstpixel MCP Server"),
    (re.compile(r"Aura-(prosjektet|agentene)\b"), r"Kunstpixel-\1"),
    (re.compile(r"FastMCP\('Aura'\)"), "FastMCP('Kunstpixel')"),
    (re.compile(r"\bAuras\b"), "Kunstpixels"),
    (re.compile(r"\bAURA KUNSTMUSEUMS\b"), "KUNSTPIXELS"),
    (re.compile(r"\bAURA MUSEUM\b"), "KUNSTPIXEL"),
    # Inventarnumre og mal for dem. Store bokstaver: alltid. Små/blandet: bare foran sifre.
    (re.compile(r"\bAURA-"), "KP-"),
    (re.compile(r"\b(aura)-(?=\d{4}-\d{3}|YYYY-NNN)", re.IGNORECASE), _id_prefiks),
    # Kodenavn
    (re.compile(r"\bAURA_DB_PATH\b"), "KUNSTPIXEL_DB_PATH"),
    (re.compile(r"\bAURA_TODAY\b"), "KUNSTPIXEL_TODAY"),
    (re.compile(r"\bAURA_ID_RE\b"), "KP_ID_RE"),
    (re.compile(r"\baura_id\b"), "kp_id"),
    # Filer, mapper og konfignavn
    (re.compile(r"src/aura_museum/"), "arkiv/kunstpixel_legacy/"),
    (re.compile(r"\baura_museum_komplett\b"), "kunstpixel_komplett"),
    (re.compile(r"\baura_museum_legacy\b"), "kunstpixel_legacy"),
    (re.compile(r"\baura-kunstmuseum\b"), "kunstpixel"),
    (re.compile(r"\baura-museum\b"), "kunstpixel"),
    (re.compile(r"\baura\.db\b"), "kunstpixel.db"),
]


def bytt(tekst: str) -> str:
    for monster, erstatning in REGLER:
        tekst = monster.sub(erstatning, tekst)  # type: ignore[arg-type]
    return tekst


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=True
    ).stdout.decode("utf-8")


def _sporede() -> list[str]:
    return [p for p in _git("ls-files", "-z").split("\0") if p]


def kjor_tekst() -> None:
    endret = 0
    for rel in _sporede():
        if rel in SKIP:
            continue
        sti = ROOT / rel
        if not sti.is_file():
            continue
        data = sti.read_bytes()
        if b"\0" in data[:8192] or not GUARD.search(data.decode("utf-8", "replace")):
            continue
        try:
            tekst = data.decode("utf-8")
        except UnicodeDecodeError:
            print(f"HOPPET OVER (ikke UTF-8): {rel}")
            continue
        ny = bytt(tekst)
        if ny != tekst:
            sti.write_bytes(ny.encode("utf-8"))
            endret += 1
    print(f"Tekstfiler endret: {endret}")

    flyttet = 0
    for rel in _sporede():
        ny_rel = bytt(rel)
        if ny_rel != rel:
            (ROOT / ny_rel).parent.mkdir(parents=True, exist_ok=True)
            _git("mv", rel, ny_rel)
            flyttet += 1
    print(f"Filer flyttet (git mv): {flyttet}")


def kjor_db(sti: Path) -> None:
    con = sqlite3.connect(sti)
    con.execute("PRAGMA foreign_keys=OFF")  # verk.id er primærnøkkel med referanser
    endret = 0
    try:
        con.execute("BEGIN")
        tabeller = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
        for t in tabeller:
            kolonner = [r[1] for r in con.execute(f"pragma table_info([{t}])")]
            for k in kolonner:
                rader = con.execute(
                    f"select rowid, [{k}] from [{t}] where cast([{k}] as text) like '%aura%'"
                ).fetchall()
                for rowid, verdi in rader:
                    if not isinstance(verdi, str):
                        continue
                    ny = bytt(verdi)
                    if ny != verdi:
                        con.execute(f"update [{t}] set [{k}] = ? where rowid = ?", (ny, rowid))
                        endret += 1
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        if fk:
            raise RuntimeError(f"Fremmednøkkelbrudd etter bytte: {fk[:5]}")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    ok = con.execute("PRAGMA integrity_check").fetchone()[0]
    con.close()
    if ok != "ok":
        raise RuntimeError(f"integrity_check: {ok}")
    print(f"{sti.name}: {endret} celler endret, fremmednøkler og integritet ok")


def vis_rest() -> int:
    rest = 0
    for rel in _sporede():
        if GUARD.search(rel):
            print(f"FILNAVN  {rel}")
            rest += 1
        if rel in SKIP:
            continue
        sti = ROOT / rel
        if not sti.is_file():
            continue
        data = sti.read_bytes()
        if b"\0" in data[:8192]:
            continue
        for nr, linje in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            if GUARD.search(linje):
                print(f"{rel}:{nr}: {linje.strip()[:140]}")
                rest += 1
    print(f"Rest: {rest}")
    return rest


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tekst", action="store_true")
    g.add_argument("--db", type=Path)
    g.add_argument("--rest", action="store_true")
    a = p.parse_args()
    if a.tekst:
        kjor_tekst()
    elif a.db:
        if a.db.name == "museum.db":
            print("museum.db bygges av build_museum_db.py, ikke her.", file=sys.stderr)
            return 2
        kjor_db(a.db)
    else:
        return 1 if vis_rest() else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
