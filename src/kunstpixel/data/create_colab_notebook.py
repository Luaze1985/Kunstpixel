"""
Genererer en interaktiv Google Colab Notebook (.ipynb) for
analyse av time-for-time historiske vaktdata og personvernrisiko.
"""

import json
import os

def create_notebook():
    notebook_path = os.path.abspath("02_deliverables/02_rapporter/personvern_time_for_time_colab.ipynb")
    os.makedirs(os.path.dirname(notebook_path), exist_ok=True)

    cells = []

    def md(text):
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in text.strip().split("\n")]
        })

    def code(code_str):
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in code_str.strip().split("\n")]
        })

    # Celle 1: Tittel & Intro
    md("""# 🏛️ Kunstpixel: Time-for-time Vaktanalyse & Personvern
### Re-identifisering, Kvasi-identifikatorer og Mosaikkteorien i Praksis

Denne notatblokken demonstrerer et sentralt paradoks i datavitenskap og personvern:
> **Jo mer nøyaktig og operativt et datasett blir i tid og rom (f.eks. time-for-time per stasjon), desto mer dramatisk faller anonymitetsgraden ($k$-anonymitet $\\to 1$).**

Vi kobler sammen:
1. **Time-for-time vaktlister** (439 952 historiske vakt-timer 2010–2026).
2. **Avviks- og hendelsesrapporter** (HMS, tekniske feil, publikumskonflikter).
3. **Ansattopplysninger** (lønnstrinn, stilling, fødselsår).
4. **Fraværslogger** (sykemeldinger og permisjoner).
""")

    # Celle 2: Laste inn data
    md("""## 1. Laste inn data (SQLite eller CSV)
I Google Colab kan du enten laste opp SQLite-databasen `colab_personvern_historikk.db` direkte, eller bruke CSV-uttrekket `vakt_time_for_time_2025_2026.csv`.
""")

    code("""import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Automatisk sjekk for SQLite-fil eller CSV
db_path = "colab_personvern_historikk.db"
csv_path = "vakt_time_for_time_2025_2026.csv"

if os.path.exists(db_path):
    print(f"✅ Kobler til SQLite-database: {db_path}")
    conn = sqlite3.connect(db_path)
    df_vakt = pd.read_sql_query("SELECT * FROM vakt_time_for_time WHERE aar >= 2024", conn)
    df_ansatte = pd.read_sql_query("SELECT * FROM hr_ansatte", conn)
    df_fravaer = pd.read_sql_query("SELECT * FROM hr_fravaer", conn)
    df_avvik = pd.read_sql_query("SELECT * FROM avvik_hms", conn)
elif os.path.exists(csv_path):
    print(f"✅ Laster fra CSV-fil: {csv_path}")
    df_vakt = pd.read_csv(csv_path)
    conn = sqlite3.connect(":memory:")
    df_vakt.to_sql("vakt_time_for_time", conn, index=False)
else:
    print("ℹ️ Laster eksempeldata direkte i minnet...")
    # Fallback syntetisk mini-sett
    df_vakt = pd.DataFrame({
        "vakt_id": ["VAKT-01", "VAKT-02", "VAKT-03"],
        "ansatt_id": ["KP-ANS-008", "KP-ANS-011", "KP-ANS-005"],
        "dato": ["2025-05-14", "2025-05-14", "2025-05-14"],
        "time_slot": ["14:00", "14:00", "14:00"],
        "stasjon": ["Resepsjon og billett", "Museumsbutikk", "Vaktrom"]
    })

print(f"Antall vakt-timer lastet inn: {len(df_vakt):,}")
df_vakt.head(5)""")

    # Celle 3: K-anonymitetsberegning
    md("""## 2. Matematisk analyse: K-anonymitetsgradient
$k$-anonymitet krever at enhver kombinasjon av kvasi-identifikatorer (her: **Dato + Klokketime + Stasjon**) skal deles av minst $k$ personer.
- Dersom $k = 1$, er personen **100 % unikt identifiserbar**.
""")

    code("""# Grupperer på dato, time og stasjon for å finne antall unike ansatte
k_scores = df_vakt.groupby(["dato", "time_slot", "stasjon"])["ansatt_id"].nunique()

k_equal_1 = (k_scores == 1).mean() * 100
print("--- K-ANONYMITETSRAPPORT ---")
print(f"Totalt antall unike tids- og stasjonskombinasjoner: {len(k_scores):,}")
print(f"Andel tidsrom der k = 1 (Fullstendig re-identifiserbar): {k_equal_1:.2f} %")
print(f"Gjennomsnittlig k-verdi: {k_scores.mean():.2f}")
print(f"Maksimal k-verdi: {k_scores.max()}")""")

    # Celle 4: Visualisering
    md("""## 3. Visualisering av tidsbemanningsmatrise
La oss se på hvordan bemanningen fordeler seg gjennom døgnet på de ulike stasjonene for en typisk uke.
""")

    code("""pivot_time = df_vakt.groupby(["stasjon", "klokketime"]).size().unstack(fill_value=0)

plt.figure(figsize=(14, 6))
plt.imshow(pivot_time, cmap="YlOrRd", aspect="auto")
plt.colorbar(label="Antall vakt-timer registrert")
plt.yticks(range(len(pivot_time.index)), pivot_time.index, fontsize=9)
plt.xticks(range(len(pivot_time.columns)), [f"{h:02d}:00" for h in pivot_time.columns], rotation=45)
plt.title("Aktivitetsprofil per stasjon og klokketime (Høy oppløsning)", fontsize=13, fontweight="bold")
plt.xlabel("Klokkeslett")
plt.ylabel("Stasjon / Sal")
plt.tight_layout()
plt.show()""")

    # Celle 5: Simulering av mosaikkangrep
    md("""## 4. Simulering av et reelt mosaikkangrep
Her simulerer vi en ekstern observasjon (f.eks. en klage eller et bilde fra et publikumsbesøk) og ser hvor raskt vi kan hente ut personens fulle profil, lønnstrinn og private fraværshistorikk.
""")

    code("""# Scenario: En hendelse observeres på en spesifikk dato, klokkeslett og stasjon
observasjon_dato = "2025-05-14"
observasjon_time = "14:00"
observasjon_stasjon = "Resepsjon og billett"

print(f"🔍 Søker etter tilstedeværelse for: {observasjon_dato} kl. {observasjon_time} på '{observasjon_stasjon}'...")

treff = df_vakt[
    (df_vakt["dato"] == observasjon_dato) &
    (df_vakt["time_slot"] == observasjon_time) &
    (df_vakt["stasjon"] == observasjon_stasjon)
]

if not treff.empty:
    ansatt_id = treff["ansatt_id"].values[0]
    vakt_id = treff["vakt_id"].values[0]
    print(f"🎯 100 % entydig treff! Ansatt-ID: {ansatt_id} (Vakt-ID: {vakt_id})")
    
    # Kobling mot ansattregister (hvis tilgjengelig)
    if 'df_ansatte' in locals() and not df_ansatte.empty:
        person = df_ansatte[df_ansatte["ansatt_id"] == ansatt_id]
        if not person.empty:
            print("\n🚨 AVSLØRT PERSONPROFIL FRA GRUNNLAGSDATA:")
            print(person[["navn", "fodselsaar", "kjonn", "stilling", "lonnstrinn_virke", "epost"]].to_dict(orient="records")[0])
            
    # Kobling mot fraværsregister
    if 'df_fravaer' in locals() and not df_fravaer.empty:
        fravaer = df_fravaer[df_fravaer["ansatt_id"] == ansatt_id]
        if not fravaer.empty:
            print(f"\n⚠️ SENSITIV FRAVÆRSHISTORIKK FUNNET (Artikkel 9): {len(fravaer)} registreringer:")
            display(fravaer.head(3))
else:
    print("Ingen vakt registrert på det eksakte tidspunktet.")""")

    # Celle 6: Avbøtende tiltak
    md("""## 5. Beskyttelse: Hvordan rette opp personvernet?
For å hindre at time-for-time data misbrukes til overvåking og re-identifisering, må vi innføre **beskyttende transformasjoner**:
1. **Tidsmessig generalisering:** Slå sammen time-slots til hele dager eller skiftkategorier (Morgen / Kveld).
2. **Romlig generalisering:** Erstatte eksakte saler med avdelinger (f.eks. 'Utstillingsfløy Vest').
3. **$k$-anonymitetsfilter:** Undertrykke rader der færre enn $k=5$ personer deler profilen.
""")

    code("""# Demonstrasjon av tidsgeneralisering
df_generalisert = df_vakt.copy()

def categorize_time(hour):
    if hour < 12:
        return "Formiddag (08-12)"
    elif hour < 16:
        return "Ettermiddag (12-16)"
    else:
        return "Kveld (16-20)"

df_generalisert["tidsblokk"] = df_generalisert["klokketime"].apply(categorize_time)

# Ny k-beregning med generaliserte tidsblokker og avdeling i stedet for stasjon
k_beskyttet = df_generalisert.groupby(["dato", "tidsblokk", "avdeling"])["ansatt_id"].nunique()

print(f"Gjennomsnittlig k etter tidsblokk-generalisering: {k_beskyttet.mean():.2f}")
print(f"Andel unike treff (k=1) redusert fra {k_equal_1:.1f}% til {(k_beskyttet == 1).mean()*100:.1f}%!")""")

    notebook_data = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.13"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(notebook_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Skrevet ferdig Colab-notebook til: {notebook_path}")

if __name__ == "__main__":
    create_notebook()
