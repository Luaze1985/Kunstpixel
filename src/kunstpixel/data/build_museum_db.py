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
10. Intern organisasjon (colab_org_bygger) lastes fra fire CSV-er, normalisert mot hr_ansatte:
    org_ferdigheter (`mock_interne_ferdigheter.csv`), org_ansatt_kompetanse (`mock_ansatt_kompetanser.csv`),
    interne_henvendelser (`mock_interne_henvendelser.csv`) og hms_avvik_tekst (`mock_avvik_hms_tekst.csv`).
    Navn og avdeling hentes ved oppslag fra hr_ansatte, de lagres ikke på nytt.
    NB: org_ferdigheter overlapper de 7 første kodene i hr_skills (HR-demoen) med litt andre navn.
    Dette er to kilder for samme ferdigheter, og må samkjøres av Lars før de brukes sammen.
11. Indekser for vaktoppslag og interne tabeller.
12. PRAGMA user_version = SKJEMAVERSJON, VACUUM, integrity_check og foreign_key_check.

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
SKJEMAVERSJON = 5

KLOKKESLETT_CSV = DATA_DIR / "arkiv_hr_vakt_klokkeslett.csv"
GRENSER_CSV = DATA_DIR / "arbeidstid_grenser.csv"
TARIFF_TILLEGG_CSV = DATA_DIR / "virke_tariff_tillegg.csv"
FRAVAER_CSV = DATA_DIR / "arkiv_hr_fravaer.csv"
ROLLER_CSV = DATA_DIR / "roller.csv"
ROLLE_SPORSMAL_CSV = DATA_DIR / "rolle_sporsmal.csv"
RAPPORT_REGLER_CSV = DATA_DIR / "rapport_regler.csv"
VAKT_JUSTERING_CSV = DATA_DIR / "arkiv_hr_vakt_justering.csv"
HENDELSER_TILLEGG_CSV = DATA_DIR / "hendelser_tillegg_2026.csv"
ORG_FERDIGHETER_CSV = DATA_DIR / "mock_interne_ferdigheter.csv"
ORG_KOMPETANSE_CSV = DATA_DIR / "mock_ansatt_kompetanser.csv"
INTERNE_HENVENDELSER_CSV = DATA_DIR / "mock_interne_henvendelser.csv"
HMS_AVVIK_TEKST_CSV = DATA_DIR / "mock_avvik_hms_tekst.csv"

# H5 & Governance CSV-er
H5_MYNDIGHETER_CSV = DATA_DIR / "h5_myndighetskontakter.csv"
H5_TILSYNSBESOK_CSV = DATA_DIR / "h5_tilsynsbesok_rutine.csv"
H5_KALENDER_CSV = DATA_DIR / "h5_rapporteringskalender.csv"
H5_MALER_CSV = DATA_DIR / "h5_rapportmaler.csv"
H5_TIDSBRUK_CSV = DATA_DIR / "h5_arbeidsoppgaver_tidsbruk.csv"
H5_HISTORIKK_CSV = DATA_DIR / "h5_historikk_2010_2026.csv"
HR_OPPLAERING_CSV = DATA_DIR / "hr_opplaering_onboarding.csv"

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

ORG_FERDIGHETER_SQL = """
CREATE TABLE org_ferdigheter (
    skill_code TEXT PRIMARY KEY,
    navn TEXT NOT NULL,
    utloper INTEGER NOT NULL CHECK(utloper IN (0, 1)),
    kategori TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

ORG_KOMPETANSE_SQL = """
CREATE TABLE org_ansatt_kompetanse (
    ansatt_id TEXT NOT NULL REFERENCES hr_ansatte(ansatt_id),
    skill_code TEXT NOT NULL REFERENCES org_ferdigheter(skill_code),
    sertifisert_dato TEXT NOT NULL CHECK(sertifisert_dato GLOB '????-??-??'),
    gyldig_til TEXT CHECK(gyldig_til IS NULL OR gyldig_til GLOB '????-??-??'),
    status TEXT NOT NULL CHECK(status IN ('gyldig', 'utlopt')),
    datakilde TEXT NOT NULL,
    PRIMARY KEY(ansatt_id, skill_code)
)
"""

INTERNE_HENVENDELSER_SQL = """
CREATE TABLE interne_henvendelser (
    sak_id TEXT PRIMARY KEY,
    dato_tid TEXT NOT NULL CHECK(dato_tid GLOB '????-??-?? ??:??'),
    ansatt_id TEXT NOT NULL REFERENCES hr_ansatte(ansatt_id),
    kategori TEXT NOT NULL CHECK(kategori IN
        ('vaktbytte', 'permisjon', 'sykefraver', 'arbeidsmiljo', 'varsling', 'tilrettelegging')),
    tittel TEXT NOT NULL,
    fritekst TEXT NOT NULL,
    case_ref TEXT NOT NULL,
    paragraf_hjemmel TEXT NOT NULL,
    forventet_utfall TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

HMS_AVVIK_TEKST_SQL = """
CREATE TABLE hms_avvik_tekst (
    avvik_id TEXT PRIMARY KEY,
    dato TEXT NOT NULL CHECK(dato GLOB '????-??-??'),
    avdeling TEXT NOT NULL,
    stasjon TEXT NOT NULL,
    alvorlighetsgrad TEXT NOT NULL CHECK(alvorlighetsgrad IN ('LAV', 'MIDDELS', 'HØY', 'KRITISK')),
    beskrivelse TEXT NOT NULL,
    strakstiltak TEXT NOT NULL,
    ansvarlig_rolle TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('LUKKET', 'UNDER_OPPFOLGING')),
    datakilde TEXT NOT NULL
)
"""

H5_MYNDIGHETER_SQL = """
CREATE TABLE h5_myndighetskontakter (
    id TEXT PRIMARY KEY,
    myndighet TEXT NOT NULL,
    omrade TEXT NOT NULL,
    intern_eier TEXT NOT NULL,
    kontaktperson TEXT NOT NULL,
    kontakt_epost TEXT NOT NULL,
    intern_eier_navn TEXT NOT NULL,
    intern_eier_epost TEXT NOT NULL,
    hva_de_vil TEXT NOT NULL,
    utloser TEXT NOT NULL,
    dokumentasjon TEXT NOT NULL,
    merknad TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

H5_TILSYNSBESOK_SQL = """
CREATE TABLE h5_tilsynsbesok_rutine (
    steg_nr INTEGER PRIMARY KEY,
    navn TEXT NOT NULL,
    ansvarlig TEXT NOT NULL,
    handling TEXT NOT NULL,
    dokumentasjon TEXT NOT NULL,
    gult_avvik_frist TEXT NOT NULL,
    rodt_avvik_frist TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

H5_KALENDER_SQL = """
CREATE TABLE h5_rapporteringskalender (
    id TEXT PRIMARY KEY,
    rapport TEXT NOT NULL,
    mottaker TEXT NOT NULL,
    mottakertype TEXT NOT NULL CHECK(mottakertype IN ('intern', 'ekstern')),
    frekvens TEXT NOT NULL,
    antall_per_ar INTEGER NOT NULL,
    maned TEXT NOT NULL,
    eier TEXT NOT NULL,
    timer_per_gang REAL NOT NULL,
    timer_per_ar INTEGER NOT NULL,
    godkjenning TEXT NOT NULL,
    formal TEXT NOT NULL,
    kilder_json TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

H5_MALER_SQL = """
CREATE TABLE h5_rapportmaler (
    id TEXT NOT NULL,
    mal_navn TEXT NOT NULL,
    brukes_til_json TEXT NOT NULL,
    godkjenning TEXT NOT NULL,
    status_ved_opprettelse TEXT NOT NULL,
    formal TEXT NOT NULL,
    felt_rekkefolge INTEGER NOT NULL,
    felt_navn TEXT NOT NULL,
    felt_beskrivelse TEXT NOT NULL,
    felt_kilder_json TEXT NOT NULL,
    regler_json TEXT NOT NULL,
    datakilde TEXT NOT NULL,
    PRIMARY KEY(id, felt_rekkefolge)
)
"""

H5_TIDSBRUK_SQL = """
CREATE TABLE h5_arbeidsoppgaver_tidsbruk (
    id TEXT PRIMARY KEY,
    omrade TEXT NOT NULL CHECK(omrade IN ('Myndighetskontakt', 'Rapportering')),
    oppgave TEXT NOT NULL,
    myndighet TEXT,
    rapport_id TEXT REFERENCES h5_rapporteringskalender(id),
    rolle TEXT NOT NULL,
    timer_per_ar INTEGER NOT NULL,
    automatiseringspotensial TEXT NOT NULL CHECK(automatiseringspotensial IN ('Lav', 'Middels', 'Høy')),
    begrunnelse TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

H5_HISTORIKK_SQL = """
CREATE TABLE h5_historikk_2010_2026 (
    ar INTEGER PRIMARY KEY,
    status_ar TEXT NOT NULL,
    tema TEXT NOT NULL,
    besok_totalt INTEGER NOT NULL,
    betalende_andel_prosent INTEGER NOT NULL,
    betalende_besokende INTEGER NOT NULL,
    skoleelever INTEGER NOT NULL,
    arrangementer_antall INTEGER NOT NULL,
    utstillinger_antall INTEGER NOT NULL,
    ansatte_arsverk REAL NOT NULL,
    snittpris_kr INTEGER NOT NULL,
    billettinntekter_tkr INTEGER NOT NULL,
    tilskudd_tkr INTEGER NOT NULL,
    kafeinntekter_tkr INTEGER NOT NULL,
    andre_inntekter_tkr INTEGER NOT NULL,
    inntekter_totalt_tkr INTEGER NOT NULL,
    kostnader_tkr INTEGER NOT NULL,
    resultat_tkr INTEGER NOT NULL,
    tilsyn_antall INTEGER NOT NULL,
    avvik_funnet INTEGER NOT NULL,
    avvik_lukket_innen_frist INTEGER NOT NULL,
    palegg_antall INTEGER NOT NULL,
    ruh_registrert INTEGER NOT NULL,
    skader_med_fravaer INTEGER NOT NULL,
    sykefravaer_prosent REAL NOT NULL,
    ik_mat_temperaturavvik INTEGER NOT NULL,
    vernerunder_gjennomfort INTEGER NOT NULL,
    rapporter_levert INTEGER NOT NULL,
    rapporter_for_sent INTEGER NOT NULL,
    tilskuddssoknader INTEGER NOT NULL,
    tilskudd_innvilget INTEGER NOT NULL,
    timer_myndighetskontakt INTEGER NOT NULL,
    timer_rapportering INTEGER NOT NULL,
    timer_totalt INTEGER NOT NULL,
    automatiseringsgrad_prosent INTEGER NOT NULL,
    hendelse TEXT NOT NULL,
    laerdom TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

HR_OPPLAERING_SQL = """
CREATE TABLE hr_opplaering_onboarding (
    opplaering_id TEXT PRIMARY KEY,
    kategori TEXT NOT NULL CHECK(kategori IN ('kompetanse_matrise', 'onboarding_status', 'hms_opplaering')),
    rolle TEXT NOT NULL,
    tema_eller_sertifisering TEXT NOT NULL,
    fase_eller_status TEXT NOT NULL,
    aktivitet_eller_beskrivelse TEXT NOT NULL,
    ansvarlig_rolle TEXT NOT NULL,
    datakilde TEXT NOT NULL
)
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS org_kompetanse_skill_idx ON org_ansatt_kompetanse(skill_code, gyldig_til)",
    "CREATE INDEX IF NOT EXISTS interne_henvendelser_kategori_idx ON interne_henvendelser(kategori, dato_tid)",
    "CREATE INDEX IF NOT EXISTS interne_henvendelser_ansatt_idx ON interne_henvendelser(ansatt_id)",
    "CREATE INDEX IF NOT EXISTS hms_avvik_tekst_alvor_idx ON hms_avvik_tekst(alvorlighetsgrad, dato)",
    "CREATE INDEX IF NOT EXISTS hr_vakter_ansatt_dato_idx ON hr_vakter(ansatt_id, dato)",
    "CREATE INDEX IF NOT EXISTS hr_vakter_dato_idx ON hr_vakter(dato, start, slutt)",
    "CREATE INDEX IF NOT EXISTS hr_fravaer_ansatt_idx ON hr_fravaer(ansatt_id, fra, til)",
    "CREATE INDEX IF NOT EXISTS rapport_regler_sporsmal_idx ON rapport_regler(sporsmal_id)",
    "CREATE INDEX IF NOT EXISTS h5_kalender_eier_idx ON h5_rapporteringskalender(eier, maned)",
    "CREATE INDEX IF NOT EXISTS h5_tidsbruk_omrade_idx ON h5_arbeidsoppgaver_tidsbruk(omrade, rolle)",
    "CREATE INDEX IF NOT EXISTS hr_opplaering_rolle_idx ON hr_opplaering_onboarding(rolle, kategori)",
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


def bygg_org_ferdigheter(con: sqlite3.Connection) -> int:
    rader = les_csv(ORG_FERDIGHETER_CSV)
    con.execute("DROP TABLE IF EXISTS org_ferdigheter")
    con.execute(ORG_FERDIGHETER_SQL)
    con.executemany(
        "INSERT INTO org_ferdigheter VALUES (?,?,?,?,?)",
        [(r["skill_code"], r["name"], int(r["expires"]), r["kategori"], r["datakilde"]) for r in rader],
    )
    return len(rader)


def bygg_org_kompetanse(con: sqlite3.Connection) -> int:
    """Bygg org_ansatt_kompetanse. Må kjøres etter bygg_org_ferdigheter. Navn og avdeling lagres ikke."""
    rader = les_csv(ORG_KOMPETANSE_CSV)
    con.execute("DROP TABLE IF EXISTS org_ansatt_kompetanse")
    con.execute(ORG_KOMPETANSE_SQL)
    con.executemany(
        "INSERT INTO org_ansatt_kompetanse VALUES (?,?,?,?,?,?)",
        [
            (r["ansatt_id"], r["skill_code"], r["sertifisert_dato"], r["gyldig_til"] or None, r["status"], r["datakilde"])
            for r in rader
        ],
    )
    return len(rader)


def bygg_interne_henvendelser(con: sqlite3.Connection) -> int:
    rader = les_csv(INTERNE_HENVENDELSER_CSV)
    con.execute("DROP TABLE IF EXISTS interne_henvendelser")
    con.execute(INTERNE_HENVENDELSER_SQL)
    con.executemany(
        "INSERT INTO interne_henvendelser VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["sak_id"], r["dato_tid"], r["ansatt_id"], r["kategori"], r["tittel"], r["fritekst"],
                r["case_ref"], r["paragraf_hjemmel"], r["forventet_utfall"], r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_hms_avvik_tekst(con: sqlite3.Connection) -> int:
    rader = les_csv(HMS_AVVIK_TEKST_CSV)
    con.execute("DROP TABLE IF EXISTS hms_avvik_tekst")
    con.execute(HMS_AVVIK_TEKST_SQL)
    con.executemany(
        "INSERT INTO hms_avvik_tekst VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["avvik_id"], r["dato"], r["avdeling"], r["stasjon"], r["alvorlighetsgrad"], r["beskrivelse"],
                r["strakstiltak"], r["ansvarlig_rolle"], r["status"], r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_h5_myndighetskontakter(con: sqlite3.Connection) -> int:
    rader = les_csv(H5_MYNDIGHETER_CSV)
    con.execute("DROP TABLE IF EXISTS h5_myndighetskontakter")
    con.execute(H5_MYNDIGHETER_SQL)
    con.executemany(
        "INSERT INTO h5_myndighetskontakter VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["id"], r["myndighet"], r["omrade"], r["intern_eier"], r["kontaktperson"],
                r["kontakt_epost"], r["intern_eier_navn"], r["intern_eier_epost"], r["hva_de_vil"],
                r["utloser"], r["dokumentasjon"], r["merknad"], r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_h5_tilsynsbesok(con: sqlite3.Connection) -> int:
    rader = les_csv(H5_TILSYNSBESOK_CSV)
    con.execute("DROP TABLE IF EXISTS h5_tilsynsbesok_rutine")
    con.execute(H5_TILSYNSBESOK_SQL)
    con.executemany(
        "INSERT INTO h5_tilsynsbesok_rutine VALUES (?,?,?,?,?,?,?,?)",
        [
            (
                int(r["steg_nr"]), r["navn"], r["ansvarlig"], r["handling"],
                r["dokumentasjon"], r["gult_avvik_frist"], r["rodt_avvik_frist"], r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_h5_rapporteringskalender(con: sqlite3.Connection) -> int:
    rader = les_csv(H5_KALENDER_CSV)
    con.execute("DROP TABLE IF EXISTS h5_rapporteringskalender")
    con.execute(H5_KALENDER_SQL)
    con.executemany(
        "INSERT INTO h5_rapporteringskalender VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["id"], r["rapport"], r["mottaker"], r["mottakertype"], r["frekvens"],
                int(r["antall_per_ar"]), r["maned"], r["eier"], float(r["timer_per_gang"]),
                int(r["timer_per_ar"]), r["godkjenning"], r["formal"], r["kilder_json"], r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_h5_rapportmaler(con: sqlite3.Connection) -> int:
    rader = les_csv(H5_MALER_CSV)
    con.execute("DROP TABLE IF EXISTS h5_rapportmaler")
    con.execute(H5_MALER_SQL)
    con.executemany(
        "INSERT INTO h5_rapportmaler VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["id"], r["mal_navn"], r["brukes_til_json"], r["godkjenning"],
                r["status_ved_opprettelse"], r["formal"], int(r["felt_rekkefolge"]),
                r["felt_navn"], r["felt_beskrivelse"], r["felt_kilder_json"],
                r["regler_json"], r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_h5_arbeidsoppgaver_tidsbruk(con: sqlite3.Connection) -> int:
    rader = les_csv(H5_TIDSBRUK_CSV)
    con.execute("DROP TABLE IF EXISTS h5_arbeidsoppgaver_tidsbruk")
    con.execute(H5_TIDSBRUK_SQL)
    con.executemany(
        "INSERT INTO h5_arbeidsoppgaver_tidsbruk VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r["id"], r["omrade"], r["oppgave"], r["myndighet"] or None,
                r["rapport_id"] or None, r["rolle"], int(r["timer_per_ar"]),
                r["automatiseringspotensial"], r["begrunnelse"], r["datakilde"],
            )
            for r in rader
        ],
    )
    # Valider at totalsummen er nøyaktig 287 timer
    total_timer = sum(int(r["timer_per_ar"]) for r in rader)
    if total_timer != 287:
        raise ValueError(f"Total tidsbruk i H5 arbeidsoppgaver er {total_timer}, forventet 287 timer")
    return len(rader)


def bygg_h5_historikk(con: sqlite3.Connection) -> int:
    rader = les_csv(H5_HISTORIKK_CSV)
    con.execute("DROP TABLE IF EXISTS h5_historikk_2010_2026")
    con.execute(H5_HISTORIKK_SQL)
    con.executemany(
        "INSERT INTO h5_historikk_2010_2026 VALUES (" + ",".join(["?"] * 38) + ")",
        [
            (
                int(r["ar"]), r["status_ar"], r["tema"], int(r["besok_totalt"]),
                int(r["betalende_andel_prosent"]), int(r["betalende_besokende"]), int(r["skoleelever"]),
                int(r["arrangementer_antall"]), int(r["utstillinger_antall"]), float(r["ansatte_arsverk"]),
                int(r["snittpris_kr"]), int(r["billettinntekter_tkr"]), int(r["tilskudd_tkr"]),
                int(r["kafeinntekter_tkr"]), int(r["andre_inntekter_tkr"]), int(r["inntekter_totalt_tkr"]),
                int(r["kostnader_tkr"]), int(r["resultat_tkr"]), int(r["tilsyn_antall"]),
                int(r["avvik_funnet"]), int(r["avvik_lukket_innen_frist"]), int(r["palegg_antall"]),
                int(r["ruh_registrert"]), int(r["skader_med_fravaer"]), float(r["sykefravaer_prosent"]),
                int(r["ik_mat_temperaturavvik"]), int(r["vernerunder_gjennomfort"]), int(r["rapporter_levert"]),
                int(r["rapporter_for_sent"]), int(r["tilskuddssoknader"]), int(r["tilskudd_innvilget"]),
                int(r["timer_myndighetskontakt"]), int(r["timer_rapportering"]), int(r["timer_totalt"]),
                int(r["automatiseringsgrad_prosent"]), r["hendelse"], r["laerdom"], r["datakilde"],
            )
            for r in rader
        ],
    )
    return len(rader)


def bygg_hr_opplaering_onboarding(con: sqlite3.Connection) -> int:
    rader = les_csv(HR_OPPLAERING_CSV)
    con.execute("DROP TABLE IF EXISTS hr_opplaering_onboarding")
    con.execute(HR_OPPLAERING_SQL)
    con.executemany(
        "INSERT INTO hr_opplaering_onboarding VALUES (?,?,?,?,?,?,?,?)",
        [
            (
                r["opplaering_id"], r["kategori"], r["rolle"], r["tema_eller_sertifisering"],
                r["fase_eller_status"], r["aktivitet_eller_beskrivelse"], r["ansvarlig_rolle"], r["datakilde"],
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
            antall_org_ferdigheter = bygg_org_ferdigheter(con)
            antall_org_kompetanse = bygg_org_kompetanse(con)
            antall_henvendelser = bygg_interne_henvendelser(con)
            antall_hms_avvik_tekst = bygg_hms_avvik_tekst(con)
            antall_h5_myndigheter = bygg_h5_myndighetskontakter(con)
            antall_h5_tilsyn = bygg_h5_tilsynsbesok(con)
            antall_h5_kalender = bygg_h5_rapporteringskalender(con)
            antall_h5_maler = bygg_h5_rapportmaler(con)
            antall_h5_tidsbruk = bygg_h5_arbeidsoppgaver_tidsbruk(con)
            antall_h5_historikk = bygg_h5_historikk(con)
            antall_hr_opplaering = bygg_hr_opplaering_onboarding(con)
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
            "org_ferdigheter": antall_org_ferdigheter,
            "org_kompetanse": antall_org_kompetanse,
            "interne_henvendelser": antall_henvendelser,
            "hms_avvik_tekst": antall_hms_avvik_tekst,
            "h5_myndigheter": antall_h5_myndigheter,
            "h5_tilsyn": antall_h5_tilsyn,
            "h5_kalender": antall_h5_kalender,
            "h5_maler": antall_h5_maler,
            "h5_tidsbruk": antall_h5_tidsbruk,
            "h5_historikk": antall_h5_historikk,
            "hr_opplaering": antall_hr_opplaering,
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
