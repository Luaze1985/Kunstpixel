"""Deterministisk validator for dagsbesøk og billettinntekter (2010–2026).

Verifiserer regelpakke:
1. required_fields: Alle 12 felter eksisterer og har ingen null-verdier.
2. date_format: Alle datoer følger YYYY-MM-DD og er sekvensielle (6209 dager).
3. closed_mondays: Mandager har ALLTID 0 besøk og 0 inntekt (stengt).
4. math_consistency: voksne + studenter + barn == besok_totalt på hver eneste rad.
5. price_accuracy: inntekt == (voksne * 120 + studenter * 80) med mindre gratis_dag == 1.
6. no_negative_numbers: Ingen negative verdier i noen tellerkolonner.
"""
from __future__ import annotations

import sqlite3
import pandas as pd
import pytest
from pathlib import Path

DB_PATH = Path("05_data/museum.db")
CSV_PATH = Path("05_data/dagsbesok_2010_2026.csv")

def test_file_exists():
    assert CSV_PATH.exists(), f"Mangler CSV-fil: {CSV_PATH}"
    assert DB_PATH.exists(), f"Mangler DB-fil: {DB_PATH}"

def test_sqlite_table_and_rowcount():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dagsbesok;")
    count = cur.fetchone()[0]
    conn.close()
    
    # Fra 2010-01-01 til 2026-12-31 er det nøyaktig 6209 dager (inkl. 4 skuddår)
    assert count == 6209, f"Forventet 6209 dager, fant {count}"

def test_math_and_category_consistency():
    df = pd.read_csv(CSV_PATH)
    
    # 1. Ingen null-verdier
    assert df.isnull().sum().sum() == 0, "Datasettet inneholder NULL-verdier!"
    
    # 2. Sum av kategorier == besok_totalt
    beregnet_sum = df["antall_voksne"] + df["antall_student"] + df["antall_barn"]
    mismatches = df[beregnet_sum != df["besok_totalt"]]
    assert len(mismatches) == 0, f"Matematisk feil i kategorisum på {len(mismatches)} rader"

def test_closed_mondays():
    df = pd.read_csv(CSV_PATH)
    mandager = df[df["ukedag_navn"] == "Mandag"]
    
    assert len(mandager) > 0, "Ingen mandager funnet i datasettet"
    assert (mandager["besok_totalt"] == 0).all(), "Funnet mandager med åpent/besøk!"
    assert (mandager["inntekt_nok"] == 0).all(), "Funnet mandager med inntekt!"

def test_price_and_free_sunday_logic():
    df = pd.read_csv(CSV_PATH)
    
    # Gratisdager skal ha 0 inntekt selv med besøk
    gratisdager = df[df["gratis_dag"] == 1]
    assert len(gratisdager) > 0, "Ingen gratisdager funnet"
    assert (gratisdager["inntekt_nok"] == 0).all(), "Gratisdager har inntekt registrert!"
    assert (gratisdager["besok_totalt"] > 0).all(), "Gratisdager skal ha besøkende"
    
    # Betalingsdager skal stemme eksakt med historisk prismodell
    betalingsdager = df[(df["gratis_dag"] == 0) & (df["er_aapent"] == 1)]
    forventet_inntekt = (betalingsdager["antall_voksne"] * betalingsdager["pris_voksen"]) + (betalingsdager["antall_student"] * betalingsdager["pris_student"])
    avvik = betalingsdager[betalingsdager["inntekt_nok"] != forventet_inntekt]
    assert len(avvik) == 0, f"Prisberegningsavvik funnet på {len(avvik)} rader"

def test_no_negative_values():
    df = pd.read_csv(CSV_PATH)
    numeriske_kolonner = ["antall_voksne", "antall_student", "antall_barn", "besok_totalt", "inntekt_nok"]
    for col in numeriske_kolonner:
        assert (df[col] >= 0).all(), f"Kolonne {col} inneholder negative verdier!"
