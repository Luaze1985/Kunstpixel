"""Lag en demokopi av museum.db som kan ligge på en hostet server.

Kopien har bare tabellene Datafinner bruker, og uten opplysninger som kan peke på en ekte person
eller et ekte domene: fødselsår, e-post og telefon for de ansatte tas ut. Alt annet i de tabellene
beholdes slik at tallene i Datafinner blir de samme som i museum.db.

museum.db leses bare (mode=ro) og røres aldri. Kopien skrives til en egen fil.

Kjøres med:
    py -3.13 src/kunstpixel/data/build_demo_db.py                       # 05_data/demo/museum_demo.db
    py -3.13 src/kunstpixel/data/build_demo_db.py --ut <fil>             # annen utfil
    py -3.13 src/kunstpixel/data/build_demo_db.py --navneliste <fil.md>  # liste du går gjennom for hånd
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KILDE_DB = PROJECT_ROOT / "05_data" / "museum.db"
STANDARD_UT = PROJECT_ROOT / "05_data" / "demo" / "museum_demo.db"

# Tabellene de hvitelistede verktøyene i Datafinner leser (se tests/test_build_demo_db.py),
# pluss styrk08_katalog fordi hr_ansatte peker dit med fremmednøkkel.
BEHOLD = (
    "kunstnere", "saler", "verk", "utstilling_verk", "utstillinger", "hendelser", "publikum_faq",
    "utstilling_okonomi", "utstillinger_historikk", "ssb_sykefraver_kultur", "arbeidstid_grenser",
    "hr_ansatte", "hr_vakter", "hr_fravaer", "norske_helligdager", "virke_tariff",
    "roller", "rolle_sporsmal", "rapport_regler", "styrk08_katalog",
)
# Kolonner som settes til NULL. Kolonnene beholdes, for spørringene henter dem ved navn.
TOMMES = {"hr_ansatte": ("fodselsaar", "epost", "telefon")}


def sha256(sti: Path) -> str:
    h = hashlib.sha256()
    with sti.open("rb") as f:
        for blokk in iter(lambda: f.read(1 << 20), b""):
            h.update(blokk)
    return h.hexdigest()


def bygg_demo(kilde: Path, ut: Path) -> dict:
    """Bygg demokopien. Returnerer en oppsummering. Skriver aldri til kilden."""
    if not kilde.is_file():
        raise FileNotFoundError(f"Fant ikke kilden: {kilde}")
    ut.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kunstpixel-demo-") as tmp:
        midlertidig = Path(tmp) / "museum_demo.db"
        src = sqlite3.connect(kilde.resolve().as_uri() + "?mode=ro", uri=True)
        dst = sqlite3.connect(midlertidig)
        try:
            src.backup(dst)
            alle = [r[0] for r in dst.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            ukjent = [t for t in BEHOLD if t not in alle]
            if ukjent:
                raise ValueError(f"Kilden mangler tabeller som demokopien skal beholde: {', '.join(ukjent)}")
            fjernet = [t for t in alle if t not in BEHOLD]
            dst.execute("PRAGMA foreign_keys=OFF")
            for t in fjernet:
                dst.execute(f'DROP TABLE "{t}"')
            for tabell, kolonner in TOMMES.items():
                dst.execute(f'UPDATE "{tabell}" SET ' + ", ".join(f'"{k}" = NULL' for k in kolonner))
            dst.execute("CREATE TABLE demo_info (nokkel TEXT PRIMARY KEY, verdi TEXT NOT NULL)")
            dst.executemany("INSERT INTO demo_info VALUES (?, ?)", [
                ("kilde_sha256", sha256(kilde)),
                ("tomme_kolonner", "; ".join(f"{t}.{k}" for t, ks in TOMMES.items() for k in ks)),
                ("fjernede_tabeller", ", ".join(sorted(fjernet))),
            ])
            dst.commit()
            dst.execute("VACUUM")
            dst.commit()
            tall = {t: dst.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0] for t in BEHOLD}
        finally:
            dst.close()
            src.close()
        mellom = ut.with_name(ut.name + ".bygger")
        mellom.write_bytes(midlertidig.read_bytes())
        os.replace(mellom, ut)
    return {"tabeller": tall, "fjernet": sorted(fjernet), "sha256": sha256(ut), "bytes": ut.stat().st_size}


def skriv_navneliste(db: Path, fil: Path) -> int:
    """Skriv en liste over alle navn i demokopien, til manuell kontroll mot ekte personer."""
    con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        rader = con.execute("SELECT ansatt_id, navn, avdeling FROM hr_ansatte ORDER BY navn").fetchall()
        kunstnere = con.execute("SELECT navn FROM kunstnere ORDER BY navn").fetchall()
    finally:
        con.close()
    fil.parent.mkdir(parents=True, exist_ok=True)
    linjer = [
        "# Navn i demokopien: kontroll før hosting", "",
        "Alle navn skal være oppdiktede. Strek over det som kan være en ekte person du kjenner til, og si ifra.",
        "Programmet kan ikke avgjøre om et navn tilhører en ekte person. Det må du gjøre selv.", "",
        f"## Ansatte ({len(rader)})", "", "| ID | Navn | Avdeling | Ok |", "|---|---|---|---|",
    ]
    linjer += [f"| {i} | {n} | {a} | [ ] |" for i, n, a in rader]
    linjer += ["", f"## Kunstnere ({len(kunstnere)}), ekte personer i offentlig eie", ""]
    linjer += [f"- {n}" for (n,) in kunstnere]
    fil.write_text("\n".join(linjer) + "\n", encoding="utf-8")
    return len(rader)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kilde", type=Path, default=KILDE_DB)
    ap.add_argument("--ut", type=Path, default=STANDARD_UT)
    ap.add_argument("--navneliste", type=Path, help="skriv også en navneliste til manuell kontroll")
    args = ap.parse_args()
    info = bygg_demo(args.kilde, args.ut)
    print(f"Demokopi skrevet: {args.ut} ({info['bytes'] / 1e6:.1f} MB)")
    print(f"sha256 {info['sha256']}")
    print(f"Beholdt {len(info['tabeller'])} tabeller. Fjernet {len(info['fjernet'])}: {', '.join(info['fjernet'])}")
    if args.navneliste:
        n = skriv_navneliste(args.ut, args.navneliste)
        print(f"Navneliste med {n} ansatte: {args.navneliste}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
