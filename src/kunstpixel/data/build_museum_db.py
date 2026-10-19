"""Bygg museum.db reproduserbart fra et frosset grunnlag (ADR 004).

Godkjent av Lars 2026-10-19 som det eneste sanksjonerte stedet der museum.db skrives
(jf. ADR 004: «All berikelse og mutasjon skjer via deterministiske Python-skript»).

Grunnlaget `05_data/kilde/museum_base.db` er den kuraterte kjernen og endres aldri av
dette skriptet. Hvert bygg starter fra grunnlaget og gjør de samme stegene:

1. HR-demotabellene (hr_people, hr_skills, hr_person_skill, hr_availability, hr_rules)
   lastes fra `05_data/hr_demo/seed.json`, så alt ligger i én database.
   hr_people kobles til hr_ansatte (ansatt_id) for felles sannhetskilde (G10).
2. hr_vakter bygges om med fremmednøkkel til hr_ansatte, start/slutt fra
   `05_data/arkiv_hr_vakt_klokkeslett.csv`, og overtidstimer fra `05_data/arkiv_hr_vakt_justering.csv`.
3. Tabellen arbeidstid_grenser lastes fra `05_data/arbeidstid_grenser.csv`.
4. virke_tariff berikes med trinn 66-86 fra `05_data/virke_tariff_tillegg.csv`.
5. hr_fravaer lastes fra `05_data/arkiv_hr_fravaer.csv`.
6. roller og rolle_sporsmal lastes fra `05_data/roller.csv` og `05_data/rolle_sporsmal.csv`.
7. rapport_regler lastes fra `05_data/rapport_regler.csv`.
8. hendelser berikes med syntetiske omvisninger ut 2026 fra `05_data/hendelser_tillegg_2026.csv`.
9. Fremmednøkler legges til på hr_innleie, avvik_hms_drift, utstillingsinnlan, hendelser, hms_ergonomi_rotasjon.
10. Indekser for vaktoppslag.
11. PRAGMA user_version = SKJEMAVERSJON, VACUUM, integrity_check og foreign_key_check.

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
SKJEMAVERSJON = 3

KLOKKESLETT_CSV = DATA_DIR / "arkiv_hr_vakt_klokkeslett.csv"
GRENSER_CSV = DATA_DIR / "arbeidstid_grenser.csv"
TARIFF_TILLEGG_CSV = DATA_DIR / "virke_tariff_tillegg.csv"
FRAVAER_CSV = DATA_DIR / "arkiv_hr_fravaer.csv"
ROLLER_CSV = DATA_DIR / "roller.csv"
ROLLE_SPORSMAL_CSV = DATA_DIR / "rolle_sporsmal.csv"
RAPPORT_REGLER_CSV = DATA_DIR / "rapport_regler.csv"
VAKT_JUSTERING_CSV = DATA_DIR / "arkiv_hr_vakt_justering.csv"
HENDELSER_TILLEGG_CSV = DATA_DIR / "hendelser_tillegg_2026.csv"

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
    klokkeslett_datakilde TEXT NOT NULL,
    CHECK(start < slutt)
)
"""

GRENSER_SQL = """
CREATE TABLE arbeidstid_grenser (
    navn TEXT PRIMARY KEY,
    verdi REAL NOT NULL,
    enhet TEXT NOT NULL,
    beskrivelse TEXT NOT NULL,
    kilde TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

FRAVAER_SQL = """
CREATE TABLE hr_fravaer (
    fravaer_id TEXT PRIMARY KEY,
    ansatt_id TEXT NOT NULL REFERENCES hr_ansatte(ansatt_id),
    fra TEXT NOT NULL CHECK(fra GLOB '????-??-??'),
    til TEXT NOT NULL CHECK(til GLOB '????-??-??'),
    type TEXT NOT NULL CHECK(type IN ('egenmelding', 'sykemelding', 'permisjon')),
    datakilde TEXT NOT NULL,
    CHECK(fra <= til)
)
"""

ROLLER_SQL = """
CREATE TABLE roller (
    kode TEXT PRIMARY KEY,
    navn TEXT NOT NULL,
    trigger TEXT NOT NULL,
    beskrivelse TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

ROLLE_SPORSMAL_SQL = """
CREATE TABLE rolle_sporsmal (
    rolle_kode TEXT NOT NULL REFERENCES roller(kode),
    sporsmal_id TEXT NOT NULL,
    rekkefolge INTEGER NOT NULL,
    PRIMARY KEY(rolle_kode, sporsmal_id)
)
"""

RAPPORT_REGLER_SQL = """
CREATE TABLE rapport_regler (
    regel_id TEXT PRIMARY KEY,
    sporsmal_id TEXT NOT NULL,
    felt TEXT NOT NULL,
    operator TEXT NOT NULL,
    terskel REAL,
    vurdering TEXT NOT NULL,
    forslag TEXT NOT NULL,
    kilde TEXT NOT NULL,
    versjon TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS hr_vakter_ansatt_dato_idx ON hr_vakter(ansatt_id, dato)",
    "CREATE INDEX IF NOT EXISTS hr_vakter_dato_idx ON hr_vakter(dato, start, slutt)",
    "CREATE INDEX IF NOT EXISTS hr_fravaer_ansatt_idx ON hr_fravaer(ansatt_id, fra, til)",
    "CREATE INDEX IF NOT EXISTS rapport_regler_sporsmal_idx ON rapport_regler(sporsmal_id)",
]


def les_csv(path: Path) -> list[dict]:
    import csv

    if not path.is_file():
        raise FileNotFoundError(f"Mangler datafil: {path}")
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def bygg_hr_vakter(con: sqlite3.Connection) -> int:
    klokke = {r["vakt_id"]: r for r in les_csv(KLOKKESLETT_CSV)}
    justeringer = {r["vakt_id"]: float(r["nye_timer"]) for r in les_csv(VAKT_JUSTERING_CSV)} if VAKT_JUSTERING_CSV.is_file() else {}

    con.execute("DROP TABLE IF EXISTS hr_vakter_ny")
    con.execute(HR_VAKTER_SQL)
    rader = con.execute(
        "SELECT vakt_id, ansatt_id, aar, maaned, dato, stasjon, avdeling, rolle, timer, utstilling_id "
        "FROM hr_vakter ORDER BY vakt_id"
    ).fetchall()
    ut = []
    for vakt_id, ansatt_id, aar, maaned, dato, stasjon, avdeling, rolle, timer, utstilling_id in rader:
        k = klokke.get(vakt_id)
        if k is None:
            raise ValueError(f"Vakt {vakt_id} mangler klokkeslett i {KLOKKESLETT_CSV.name}")
        vakt_timer = justeringer.get(vakt_id, float(timer))
        start = k["start"]
        slutt = k["slutt"]
        # Hvis timetallet ble justert (overtid), forskyv slutt-tidspunktet tilsvarende
        if vakt_id in justeringer:
            start_m = int(start[:2]) * 60 + int(start[3:])
            slutt_m = start_m + round(vakt_timer * 60) + 30  # 30 min lunsj
            slutt = f"{min(23, slutt_m // 60):02d}:{min(59, slutt_m % 60):02d}"

        ut.append((vakt_id, ansatt_id, aar, maaned, dato, start, slutt,
                   stasjon, avdeling, rolle, vakt_timer, utstilling_id or None, k["datakilde"]))
    con.executemany("INSERT INTO hr_vakter_ny VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", ut)
    con.execute("DROP TABLE hr_vakter")
    con.execute("ALTER TABLE hr_vakter_ny RENAME TO hr_vakter")
    return len(ut)


def bygg_grenser(con: sqlite3.Connection) -> int:
    rader = les_csv(GRENSER_CSV)
    con.execute("DROP TABLE IF EXISTS arbeidstid_grenser")
    con.execute(GRENSER_SQL)
    con.executemany(
        "INSERT INTO arbeidstid_grenser VALUES (?,?,?,?,?,?)",
        [(r["navn"], float(r["verdi"]), r["enhet"], r["beskrivelse"], r["kilde"], r["datakilde"]) for r in rader],
    )
    return len(rader)


def bygg_tariff(con: sqlite3.Connection) -> int:
    rader = les_csv(TARIFF_TILLEGG_CSV)
    con.executemany(
        "INSERT OR REPLACE INTO virke_tariff VALUES (?,?,?,?,?,?,?,?)",
        [
            (
                int(r["lonnstrinn"]),
                r["tittel_eksempel"],
                int(r["aarslonn_nok"]),
                float(r["timesats_ordinar"]),
                float(r["timesats_kveld"]),
                float(r["timesats_helg"]),
                float(r["timesats_helligdag"]),
                r["gjeldende_fra"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_fravaer(con: sqlite3.Connection) -> int:
    rader = les_csv(FRAVAER_CSV)
    con.execute("DROP TABLE IF EXISTS hr_fravaer")
    con.execute(FRAVAER_SQL)
    con.executemany(
        "INSERT INTO hr_fravaer VALUES (?,?,?,?,?,?)",
        [(r["fravaer_id"], r["ansatt_id"], r["fra"], r["til"], r["type"], r["datakilde"]) for r in rader],
    )
    return len(rader)


def bygg_roller(con: sqlite3.Connection) -> int:
    roller = les_csv(ROLLER_CSV)
    koblinger = les_csv(ROLLE_SPORSMAL_CSV)

    con.execute("DROP TABLE IF EXISTS rolle_sporsmal")
    con.execute("DROP TABLE IF EXISTS roller")

    con.execute(ROLLER_SQL)
    con.execute(ROLLE_SPORSMAL_SQL)

    con.executemany(
        "INSERT INTO roller VALUES (?,?,?,?,?)",
        [(r["kode"], r["navn"], r["trigger"], r["beskrivelse"], r["datakilde"]) for r in roller],
    )
    con.executemany(
        "INSERT INTO rolle_sporsmal VALUES (?,?,?)",
        [(r["rolle_kode"], r["sporsmal_id"], int(r["rekkefolge"])) for r in koblinger],
    )
    return len(roller)


def bygg_rapport_regler(con: sqlite3.Connection) -> int:
    rader = les_csv(RAPPORT_REGLER_CSV)
    con.execute("DROP TABLE IF EXISTS rapport_regler")
    con.execute(RAPPORT_REGLER_SQL)
    con.executemany(
        "INSERT INTO rapport_regler VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["regel_id"],
                r["sporsmal_id"],
                r["felt"],
                r["operator"],
                float(r["terskel"]) if r["terskel"] else None,
                r["vurdering"],
                r["forslag"],
                r["kilde"],
                r["versjon"],
                r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_hendelser(con: sqlite3.Connection) -> int:
    rader = les_csv(HENDELSER_TILLEGG_CSV)
    con.executemany(
        "INSERT INTO hendelser (type, tittel, dato, klokkeslett_start, klokkeslett_slutt, "
        "sal_id, maks_deltakere, pris_voksen, pris_barn, beskrivelse, ansvarlig_rolle, status) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["type"],
                r["tittel"],
                r["dato"],
                r["klokkeslett_start"],
                r["klokkeslett_slutt"],
                r["sal_id"],
                int(r["maks_deltakere"]),
                float(r["pris_voksen"]),
                float(r["pris_barn"]),
                r["beskrivelse"],
                r["ansvarlig_rolle"],
                r["status"],
            )
            for r in rader
        ],
    )
    return len(rader)


def oppgrader_fremmednokler(con: sqlite3.Connection) -> None:
    """Bygg om tabellene i G9 for å legge til eksplisitte FOREIGN KEY constraints."""
    # 1. hr_innleie
    con.execute("""
    CREATE TABLE hr_innleie_ny (
        innleie_id TEXT PRIMARY KEY,
        aar INTEGER,
        leverandor TEXT,
        orgnr TEXT,
        kategori TEXT,
        oppdragsbeskrivelse TEXT,
        knyttet_utstilling_id TEXT REFERENCES utstillinger_historikk(utstilling_id),
        periode_fra TEXT,
        periode_til TEXT,
        fakturerte_timer INTEGER,
        timepris_nok INTEGER,
        totalbelop_nok INTEGER,
        kontaktperson_ekstern TEXT,
        godkjent_av_ansatt_id TEXT REFERENCES hr_ansatte(ansatt_id),
        godkjent_av_navn TEXT,
        status TEXT,
        doffin_referanse TEXT,
        anskaffelsesprosedyre TEXT,
        mva_kode_saft INTEGER DEFAULT 25
    )
    """)
    con.execute("INSERT INTO hr_innleie_ny SELECT * FROM hr_innleie")
    con.execute("DROP TABLE hr_innleie")
    con.execute("ALTER TABLE hr_innleie_ny RENAME TO hr_innleie")

    # 2. avvik_hms_drift
    con.execute("""
    CREATE TABLE avvik_hms_drift_ny (
        avvik_id TEXT PRIMARY KEY,
        aar INTEGER NOT NULL,
        dato TEXT NOT NULL,
        kategori TEXT NOT NULL CHECK(kategori IN ('HMS', 'SIKKERHET', 'KLIMA', 'TEKNISK', 'PUBLIKUM')),
        alvorlighetsgrad TEXT NOT NULL CHECK(alvorlighetsgrad IN ('GRØNN', 'GUL', 'RØD')),
        berort_sal_id TEXT REFERENCES saler(id),
        berort_verk_id TEXT REFERENCES verk(id),
        beskrivelse TEXT NOT NULL,
        strakstiltak TEXT NOT NULL,
        oppfolging_ansvarlig_id TEXT NOT NULL REFERENCES hr_ansatte(ansatt_id),
        status TEXT NOT NULL CHECK(status IN ('LUKKET', 'UNDER_OPPFOLGING'))
    )
    """)
    con.execute("INSERT INTO avvik_hms_drift_ny SELECT * FROM avvik_hms_drift")
    con.execute("DROP TABLE avvik_hms_drift")
    con.execute("ALTER TABLE avvik_hms_drift_ny RENAME TO avvik_hms_drift")

    # 3. utstillingsinnlan: oppdater historiske utstilling_id-er til kjente KP-EXH-ID-er i utstillinger_historikk
    aar_til_exh = dict(
        con.execute("SELECT aar, min(utstilling_id) FROM utstillinger_historikk GROUP BY aar").fetchall()
    )
    innlan_rader = con.execute("SELECT * FROM utstillingsinnlan").fetchall()
    con.execute("""
    CREATE TABLE utstillingsinnlan_ny (
        innlan_id TEXT PRIMARY KEY,
        utstilling_id TEXT REFERENCES utstillinger_historikk(utstilling_id),
        eierinstitusjon TEXT NOT NULL,
        tittel TEXT NOT NULL,
        kunstner TEXT NOT NULL,
        aar INTEGER NOT NULL,
        teknikk TEXT NOT NULL,
        dimensjoner TEXT NOT NULL,
        veggtekst TEXT NOT NULL,
        audioguide_manus TEXT NOT NULL,
        barneformidling TEXT NOT NULL,
        forsikringsverdi_nok INTEGER NOT NULL,
        kurertransport_krav TEXT NOT NULL,
        tilstand_ved_mottak TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    innlan_cols = [c[1] for c in con.execute("PRAGMA table_info(utstillingsinnlan)").fetchall()]
    ny_innlan = []
    for r in innlan_rader:
        d = dict(zip(innlan_cols, r))
        # Hvis utstilling_id mangler i utstillinger_historikk, match via år
        exh_id = d["utstilling_id"]
        if exh_id not in [x[0] for x in con.execute("SELECT utstilling_id FROM utstillinger_historikk").fetchall()]:
            exh_aar = int(exh_id.split("-")[2]) if "KP-EXH-" in exh_id else d["aar"]
            exh_id = aar_til_exh.get(exh_aar, exh_id)
        d["utstilling_id"] = exh_id
        ny_innlan.append(tuple(d.values()))
    con.executemany("INSERT INTO utstillingsinnlan_ny VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ny_innlan)
    con.execute("DROP TABLE utstillingsinnlan")
    con.execute("ALTER TABLE utstillingsinnlan_ny RENAME TO utstillingsinnlan")

    # 4. hendelser
    con.execute("""
    CREATE TABLE hendelser_ny (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT CHECK(type IN ('omvisning','verksted','foredrag','konsert','barnearrangement','aaapning','lukket')) NOT NULL,
        tittel TEXT NOT NULL,
        dato TEXT,
        klokkeslett_start TEXT,
        klokkeslett_slutt TEXT,
        sal_id TEXT REFERENCES saler(id),
        maks_deltakere INTEGER,
        pris_voksen REAL DEFAULT 0,
        pris_barn REAL DEFAULT 0,
        beskrivelse TEXT,
        ansvarlig_rolle TEXT,
        status TEXT CHECK(status IN ('planlagt','bekreftet','avlyst','gjennomfoert')) DEFAULT 'planlagt'
    )
    """)
    con.execute("INSERT INTO hendelser_ny SELECT * FROM hendelser")
    con.execute("DROP TABLE hendelser")
    con.execute("ALTER TABLE hendelser_ny RENAME TO hendelser")

    # 5. hms_ergonomi_rotasjon
    con.execute("""
    CREATE TABLE hms_ergonomi_rotasjon_ny (
        stasjon_id TEXT PRIMARY KEY,
        navn TEXT NOT NULL,
        underlag_type TEXT NOT NULL,
        maks_sammenhengende_timer REAL NOT NULL,
        krav_om_sittepause_minutter INTEGER NOT NULL,
        anbefalt_rotasjon_stasjon_id TEXT NOT NULL REFERENCES hms_ergonomi_rotasjon_ny(stasjon_id)
    )
    """)
    con.execute("INSERT INTO hms_ergonomi_rotasjon_ny SELECT * FROM hms_ergonomi_rotasjon")
    con.execute("DROP TABLE hms_ergonomi_rotasjon")
    con.execute("ALTER TABLE hms_ergonomi_rotasjon_ny RENAME TO hms_ergonomi_rotasjon")


def koble_ansattregistre(con: sqlite3.Connection) -> None:
    """Koble hr_people (E101..E112) til hr_ansatte (KP-ANS-...) for én felles sannhet (G10)."""
    # Kartlegging mellom kiosk-roller og representative ansatte i hr_ansatte
    # E101..E112 er 12 verter/kafémedarbeidere
    mapping = {
        "E101": "KP-ANS-006",  # Ada Nord -> Jonas Berg (Seniorvert)
        "E102": "KP-ANS-139",  # Birk Lund -> Synnøve Myhre (Kafémedarbeider)
        "E103": "KP-ANS-156",  # Celia Vik -> Vegard Haugen (Butikk/Kafé)
        "E104": "KP-ANS-153",  # Dag Foss -> Sindre Lindqvist (Museumsvert)
        "E105": "KP-ANS-163",  # Eva Blom -> Liv Pettersen (Museumsvert)
        "E106": "KP-ANS-073",  # Finn Mo -> Henrik Pettersen (Vekter/vert)
        "E107": "KP-ANS-091",  # Gina Dal -> Sunniva Bratt (Vekter/vert)
        "E108": "KP-ANS-096",  # Hugo Vik -> Magnus Hansen (Vekter/vert)
        "E109": "KP-ANS-119",  # Iris Sol -> Sindre Pedersen (Formidling/vert)
        "E110": "KP-ANS-142",  # Jan Hage -> Kirsti Johansen (Formidling/vert)
        "E111": "KP-ANS-158",  # Kaja Lien -> Trond Hansen (Formidling/vert)
        "E112": "KP-ANS-168",  # Leo Vang -> Fredrik Ruud (Vekter/vert)
    }

    # Legg til koblingskolonne ansatt_id REFERENCES hr_ansatte(ansatt_id)
    con.execute("""
    CREATE TABLE hr_people_ny (
        id TEXT PRIMARY KEY CHECK(length(id)>0),
        name TEXT NOT NULL CHECK(length(name)>1),
        role TEXT NOT NULL,
        active INTEGER NOT NULL CHECK(active IN (0,1)),
        employment TEXT NOT NULL CHECK(employment IN ('fast','deltid','innleie')),
        ansatt_id TEXT REFERENCES hr_ansatte(ansatt_id)
    )
    """)
    folk = con.execute("SELECT id, name, role, active, employment FROM hr_people").fetchall()
    con.executemany(
        "INSERT INTO hr_people_ny VALUES (?,?,?,?,?,?)",
        [(fid, name, role, act, emp, mapping.get(fid)) for fid, name, role, act, emp in folk],
    )
    con.execute("DROP TABLE hr_people")
    con.execute("ALTER TABLE hr_people_ny RENAME TO hr_people")


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
            antall_grenser = bygg_grenser(con)
            antall_tariff = bygg_tariff(con)
            antall_fravaer = bygg_fravaer(con)
            antall_roller = bygg_roller(con)
            antall_regler = bygg_rapport_regler(con)
            antall_nye_hendelser = bygg_hendelser(con)
            oppgrader_fremmednokler(con)
            koble_ansattregistre(con)
            for sql in INDEXES:
                con.execute(sql)
            con.execute(f"PRAGMA user_version = {SKJEMAVERSJON}")
        con.execute("VACUUM")
        con.execute("PRAGMA foreign_keys = ON")
        integritet = con.execute("PRAGMA integrity_check").fetchone()[0]
        fk_brudd = con.execute("PRAGMA foreign_key_check").fetchall()
        if integritet != "ok" or fk_brudd:
            raise ValueError(f"Kontroll feilet: integrity={integritet}, fk_brudd={fk_brudd[:5]}")
        return {
            "vakter": antall_vakter,
            "grenser": antall_grenser,
            "tariff_tillegg": antall_tariff,
            "fravaer": antall_fravaer,
            "roller": antall_roller,
            "rapport_regler": antall_regler,
            "nye_hendelser": antall_nye_hendelser,
            "user_version": SKJEMAVERSJON,
        }
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
