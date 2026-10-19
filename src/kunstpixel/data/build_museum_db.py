"""Bygg museum.db reproduserbart fra et frosset grunnlag (ADR 004).

Godkjent av Lars 2026-10-19 som det eneste sanksjonerte stedet der museum.db skrives
(jf. ADR 004: «All berikelse og mutasjon skjer via deterministiske Python-skript»).

Grunnlaget `05_data/kilde/museum_base.db` er den kuraterte kjernen og endres aldri av
dette skriptet. Hvert bygg starter fra grunnlaget og gjør de samme stegene:

1. HR-demotabellene (hr_people, hr_skills, hr_person_skill, hr_availability, hr_rules)
   lastes fra `05_data/hr_demo/seed.json`, så alt ligger i én database.
2. hr_vakter bygges om med fremmednøkkel til hr_ansatte og utledet start/slutt.
   Regelen er den samme som AML-kontrollen i db.py (ADR 009): slutt kl. 22 for
   kvelds- og vernissasjeroller, ellers kl. 17; start = slutt minus timer.
3. Indekser for vaktoppslag.
4. PRAGMA user_version = SKJEMAVERSJON, VACUUM, integrity_check og foreign_key_check.

Bygget skjer i en midlertidig fil utenfor Google Drive. Resultatet kopieres inn og
erstatter museum.db atomisk, og sha256 skrives til museum.db.sha256.

Kjøres med:
    py -3.13 src/kunstpixel/data/build_museum_db.py          # bygg og erstatt
    py -3.13 src/kunstpixel/data/build_museum_db.py --check  # bygg til temp, sammenlign hash
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.hrdemo import SEED, load_seed

DATA_DIR = PROJECT_ROOT / "05_data"
BASE_DB = DATA_DIR / "kilde" / "museum_base.db"
OUT_DB = DATA_DIR / "museum.db"
SHA_FILE = DATA_DIR / "museum.db.sha256"
SKJEMAVERSJON = 1

HR_DEMO_TABLES = ["hr_rules", "hr_availability", "hr_person_skill", "hr_skills", "hr_people"]

HR_VAKTER_SQL = """
CREATE TABLE hr_vakter_ny (
    vakt_id TEXT PRIMARY KEY,
    ansatt_id TEXT NOT NULL REFERENCES hr_ansatte(ansatt_id),
    aar TEXT,
    maaned TEXT,
    dato TEXT NOT NULL CHECK(dato GLOB '????-??-??'),
    start TEXT NOT NULL CHECK(start GLOB '??:??'),
    slutt TEXT NOT NULL CHECK(slutt GLOB '??:??'),
    stasjon TEXT,
    avdeling TEXT,
    rolle TEXT,
    timer REAL NOT NULL CHECK(timer > 0),
    utstilling_id TEXT REFERENCES utstillinger_historikk(utstilling_id),
    CHECK(start < slutt)
)
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS hr_vakter_ansatt_dato_idx ON hr_vakter(ansatt_id, dato)",
    "CREATE INDEX IF NOT EXISTS hr_vakter_dato_idx ON hr_vakter(dato, start, slutt)",
]


def slutt_for_rolle(rolle: str | None) -> float:
    r = (rolle or "").lower()
    return 22.0 if "kveld" in r or "vernissasje" in r else 17.0


def klokkeslett(timer: float) -> str:
    minutter = round(timer * 60)
    return f"{minutter // 60:02d}:{minutter % 60:02d}"


def bygg_hr_vakter(con: sqlite3.Connection) -> int:
    con.execute("DROP TABLE IF EXISTS hr_vakter_ny")
    con.execute(HR_VAKTER_SQL)
    rader = con.execute(
        "SELECT vakt_id, ansatt_id, aar, maaned, dato, stasjon, avdeling, rolle, timer, utstilling_id "
        "FROM hr_vakter ORDER BY vakt_id"
    ).fetchall()
    ut = []
    for vakt_id, ansatt_id, aar, maaned, dato, stasjon, avdeling, rolle, timer, utstilling_id in rader:
        slutt = slutt_for_rolle(rolle)
        start = slutt - float(timer)
        if start < 0:
            raise ValueError(f"Vakt {vakt_id} starter før midnatt ({timer} timer)")
        ut.append((vakt_id, ansatt_id, aar, maaned, dato, klokkeslett(start), klokkeslett(slutt),
                   stasjon, avdeling, rolle, timer, utstilling_id or None))
    con.executemany("INSERT INTO hr_vakter_ny VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", ut)
    con.execute("DROP TABLE hr_vakter")
    con.execute("ALTER TABLE hr_vakter_ny RENAME TO hr_vakter")
    return len(ut)


def bygg(til: Path) -> dict:
    if not BASE_DB.is_file():
        raise FileNotFoundError(f"Mangler grunnlag: {BASE_DB}")
    kilde = sqlite3.connect(BASE_DB.resolve().as_uri() + "?mode=ro", uri=True)
    dest = sqlite3.connect(til)
    try:
        kilde.backup(dest)
    finally:
        kilde.close()
    con = dest
    try:
        con.execute("PRAGMA foreign_keys = OFF")
        with con:
            for t in HR_DEMO_TABLES:
                con.execute(f"DROP TABLE IF EXISTS {t}")
        load_seed(con, json.loads(Path(SEED).read_text(encoding="utf-8")))
        with con:
            antall_vakter = bygg_hr_vakter(con)
            for sql in INDEXES:
                con.execute(sql)
            con.execute(f"PRAGMA user_version = {SKJEMAVERSJON}")
        con.execute("VACUUM")
        con.execute("PRAGMA foreign_keys = ON")
        integritet = con.execute("PRAGMA integrity_check").fetchone()[0]
        fk_brudd = con.execute("PRAGMA foreign_key_check").fetchall()
        if integritet != "ok" or fk_brudd:
            raise ValueError(f"Kontroll feilet: integrity={integritet}, fk_brudd={fk_brudd[:5]}")
        return {"vakter": antall_vakter, "user_version": SKJEMAVERSJON}
    finally:
        con.close()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blokk in iter(lambda: f.read(1 << 20), b""):
            h.update(blokk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="Bygg til temp og sammenlign med museum.db uten å erstatte")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="kunstpixel-bygg-") as tmp:
        temp_db = Path(tmp) / "museum.db"
        info = bygg(temp_db)
        ny_hash = sha256(temp_db)
        if args.check:
            gammel = sha256(OUT_DB) if OUT_DB.is_file() else None
            lik = gammel == ny_hash
            print(f"Bygg: {info}. sha256 ny={ny_hash} museum.db={gammel} -> {'LIK' if lik else 'ULIK'}")
            return 0 if lik else 1
        mellom = OUT_DB.with_name("museum.db.bygger")
        shutil.copyfile(temp_db, mellom)
        if sha256(mellom) != ny_hash:
            mellom.unlink()
            raise OSError("Kopien til Drive ble ikke lik bygget")
        os.replace(mellom, OUT_DB)
        SHA_FILE.write_text(f"{ny_hash}  museum.db\n", encoding="utf-8")
        print(f"museum.db bygget: {info}. sha256={ny_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
