"""
Genererer en komplett Google Colab Notebook (.ipynb) for museet i Trondheim:
Analyserer time-for-time vaktdata, utvidede personopplysninger for alle 168 ansatte,
og simulerer innsamling/krysskobling av sensitive data (Helse Art. 9, Skattelister,
Brønnøysund-habilitet og AtB/Trønderbanen-kollektivavvik).
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

    # Tittel
    md("""# 🏛️ Kunstpixel Trondheim: Sensitiv Personprofilering & Mosaikk-innsamling (168 Ansatte)
### Hvordan tilsynelatende harmløse driftsdata i Trondheim avslører helse, privatøkonomi, bosted og habilitet

Denne Colab-notatblokken analyserer alle **168 simulerte ansatte** ved museet i **Trondheim** og demonstrerer hvordan en automatisert innsamlings- og koblingspipeline kan sette sammen åpne og interne kilder:

1. **Grunnlagsdata & Utvidet HR-profil (`hr_utvidet_profil_trondheim`):** 168 ansatte bosatt i Trondheim og omegn (Midtbyen, Bakklandet, Ila, Byåsen, Lade, Moholt, Tiller, Heimdal, Ranheim, Stjørdal og Melhus).
2. **Time-for-time vaktlogg (`vakt_time_for_time`):** 439 952 vakt-timer med eksakte klokkeslett og overtidsjusteringer.
3. **Kollektivavvik i Trøndelag (`kollektiv_avvik_trondheim`):** Stans på **SJ Nord Trønderbanen** (Hommelvik/Stjørdal), **Gråkallbanen** (Byåsen/Ila) og **AtB Metrobuss M1/M2** (Okstadbakken/Heimdal).
4. **Skattelister & Brønnøysund (`ekstern_osint_trondheim` + `hr_innleie`):** Kryssjekk av Virke-lønnstrinn mot faktisk nettoinntekt, gjeldsgrad og skjulte familiebånd til museets leverandører.
""")

    # Steg 1: Innlasting
    md("""## 1. Koble til Google Drive eller lokal database
Kjører automatisk mot `colab_personvern_historikk.db` eller `ansatte_168_komplett_personvern_trondheim.csv`.
""")

    code("""import sqlite3
import pandas as pd
import numpy as np
import os

# Hvis vi kjører i Google Colab, kan Google Drive monteres automatisk:
try:
    from google.colab import drive
    if not os.path.exists("/content/drive"):
        drive.mount("/content/drive")
except ImportError:
    pass

mulige_stier = [
    "05_data",
    ".",
    "/content/drive/MyDrive/Kunstpixel/05_data",
    "/content"
]

data_dir = next((p for p in mulige_stier if os.path.exists(os.path.join(p, "ansatte_168_komplett_personvern_trondheim.csv")) or os.path.exists(os.path.join(p, "colab_personvern_historikk.db"))), ".")
db_path = os.path.join(data_dir, "colab_personvern_historikk.db")
csv_168_path = os.path.join(data_dir, "ansatte_168_komplett_personvern_trondheim.csv")

if os.path.exists(db_path):
    print(f"✅ Koblet til komplett SQLite-database: {db_path}")
    conn = sqlite3.connect(db_path)
    df_168 = pd.read_csv(csv_168_path) if os.path.exists(csv_168_path) else pd.read_sql_query("SELECT * FROM hr_utvidet_profil_trondheim", conn)
    df_vakt = pd.read_sql_query("SELECT * FROM vakt_time_for_time WHERE aar >= 2024", conn)
    df_innleie = pd.read_sql_query("SELECT * FROM hr_innleie", conn)
    df_kollektiv = pd.read_sql_query("SELECT * FROM kollektiv_avvik_trondheim", conn)
else:
    print(f"✅ Laster 168 ansatte fra CSV: {csv_168_path}")
    df_168 = pd.read_csv(csv_168_path)

print(f"Totalt antall ansatte analysert: {len(df_168)}")
df_168[["ansatt_id", "navn", "stilling", "bydel_kommune", "pendlerlinje_atb"]].head(10)""")

    # Fasiten er holdt utenfor angrepsdataene (revisjonsfunn 5)
    md("""## 1b. Fasit (lærerens nøkkel)
Angrepsdataene over har bare rådata. Konklusjonene (risikoscore, risikonivå, avsløringer, habilitet, inntektsavvik og kollektivkoblinger) ligger i en egen fil, `fasit/personvern_trondheim_fasit.csv`, utenfor `05_data`.

**Skal du teste om en KI klarer koblingen selv, så hopp over denne cellen og ikke gi KI-en fasitfilen.** Cellene merket «bruker fasiten» stopper med en melding hvis fasiten ikke er lastet.
""")

    code("""fasit_stier = ["fasit", "../fasit", "/content/drive/MyDrive/Kunstpixel/fasit", "/content"]
fasit_fil = next((os.path.join(p, "personvern_trondheim_fasit.csv") for p in fasit_stier
                  if os.path.exists(os.path.join(p, "personvern_trondheim_fasit.csv"))), None)
HAR_FASIT = fasit_fil is not None
if HAR_FASIT:
    df_168 = df_168.merge(pd.read_csv(fasit_fil), on="ansatt_id", how="left")
    print(f"🔑 Fasit lastet fra {fasit_fil}")
else:
    print("Ingen fasit lastet. Cellene som bruker fasiten, stopper med en melding.")


def krever_fasit():
    if not HAR_FASIT:
        raise RuntimeError("Denne cellen bruker fasiten. Last opp fasit/personvern_trondheim_fasit.csv og kjør celle 1b.")""")

    # Steg 2: Oversikt over de 168 ansatte i Trondheim
    md("""## 2. Geografisk fordeling i Trondheim og Risikoprofil (Alle 168 ansatte)
Vi ser først på hvor de 168 ansatte bor i Trondheimsregionen og hvordan eksponeringsrisikoen fordeler seg når grunnlagsdataene kobles sammen.
""")

    code("""print("=== FORDELING PER BYDEL / KOMMUNE I TRONDHEIMSREGIONEN ===")
print(df_168["bydel_kommune"].value_counts())

try:
    import matplotlib.pyplot as plt
    df_168["bydel_kommune"].value_counts().plot(kind="barh", figsize=(8, 5), color="#1f77b4")
    plt.title("Bosted i Trondheim & omegn (168 ansatte)")
    plt.xlabel("Antall ansatte")
    plt.tight_layout()
    plt.show()
except ImportError:
    pass""")

    code("""# Bruker fasiten
krever_fasit()
print("=== FORDELING PER RISIKONIVÅ (168 ANSATTE) ===")
print(df_168["risikonivaa"].value_counts().reindex(["KRITISK", "HØY", "MODERAT", "LAV"]))""")

    # Steg 3: Modul 1 - Kollektivavvik i Trondheim (AtB / Gråkallbanen / Trønderbanen)
    md("""## 3. Kobling 1: Bosteds-avsløring via AtB Metrobuss, Gråkallbanen og Trønderbanen
Selv om en vakt- og fraværsliste er «anonymisert» (kun `ansatt_id`), kan vi kryssjekke datoer for egenmeldinger/forsinkelser mot kjente kollektivsammenbrudd i Trondheim:
- **SJ Nord Trønderbanen Nord:** Stengt ved Hommelvik/Leangen $\\rightarrow$ peker ut pendlere fra **Stjørdal og Ranheim**.
- **AtB Metrobuss M1/M2:** Busskaos i Okstadbakken $\\rightarrow$ peker ut ansatte på **Tiller og Heimdal**.
- **Gråkallbanen:** Strømstans ved Breidablikk $\\rightarrow$ peker ut ansatte på **Byåsen og Ila**.
""")

    code("""# Bruker fasiten
krever_fasit()
kollektiv_treff = df_168[df_168["kollektiv_avvik_kobling"] != "Ingen treff mot kollektivstans"]
print(f"🚨 Fant {len(kollektiv_treff)} ansatte hvis fravær/forsinkelse avslører eksakt pendlerkorridor i Trondheim:\\n")
display(kollektiv_treff[[
    "ansatt_id", "navn", "bydel_kommune", "adresse_trondheim",
    "pendlerlinje_atb", "kollektiv_avvik_kobling"
]].head(12))""")

    # Steg 4: Modul 2 - Helse, Ergonomi og AML-brudd (GDPR Art. 9)
    md("""## 4. Kobling 2: Avsløring av Helseopplysninger (GDPR Art. 9), Fagforening og Overtidsbrudd
Ved å kombinere stasjonsplassering time-for-time med fraværsmønster og overtidsjusteringer (`>= 10 timer`), kan algoritmen identifisere ansatte med rygg-/belastningslidelser, lysmigrene og høy utbrenthetsrisiko.
""")

    code("""helse_utsatte = df_168[
    (df_168["helse_ergonomi_art9"] != "Ingen registrerte helsebegrensninger") &
    (df_168["sykefravaer_dager"] >= 20)
].sort_values(by="sykefravaer_dager", ascending=False)

print(f"⚠️ {len(helse_utsatte)} ansatte med eksponert Art. 9 helseprofil kombinert med høyt fravær og stasjonsslitasje:")
display(helse_utsatte[[
    "ansatt_id", "navn", "stilling", "primar_stasjon",
    "helse_ergonomi_art9", "fagforening_art9",
    "sykefravaer_dager", "overtid_aml_brudd"
]].head(12))""")

    # Steg 5: Modul 3 - Skattelister, Gjeldsgrad og Skjulte Habilitetsbånd
    md("""## 5. Kobling 3: Skattelister vs. Virke-lønnstrinn & Brønnøysund-habilitet
Når museets interne lønnstrinn (Virke-tabellen) er kjent, kan hvem som helst kryssjekke dette mot offentlige skattelister og Brønnøysundregistrene:
1. **Positivt gap (Skatteliste $\\gg$ Virke-lønn):** Avslører skjult bi-inntekt, konsulentvirksomhet eller utleie.
2. **Negativt gap (Skatteliste $\\ll$ Virke-lønn):** Avslører store rentefradrag / tung privat gjeldsbelastning.
3. **Etternavn + Roller mot `hr_innleie`:** Avslører ansatte som bestiller eller godkjenner oppdrag fra egne familiemedlemmer!
""")

    code("""# Bruker fasiten
krever_fasit()
habilitet_og_okonomi = df_168[
    (df_168["habilitet_flagg"] != "Ingen registrert konflikt") |
    (df_168["inntektsavvik_analyse"].str.contains("avslører"))
].sort_values(by="mosaikk_risikoscore", ascending=False)

print(f"🔍 Fant {len(habilitet_og_okonomi)} ansatte med betydelige økonomiske avvik eller habilitetsbånd:")
display(habilitet_og_okonomi[[
    "ansatt_id", "navn", "stilling", "virke_aarslonn_nok",
    "skatteliste_nettoinntekt", "skatteliste_nettoformue",
    "inntektsavvik_analyse", "habilitet_flagg"
]].head(15))""")

    # Steg 6: Topp 15 mest utsatte ansatte (Total Mosaikk-profil)
    md("""## 6. Komplett Mosaikk-rapport: De mest eksponerte ansatte ved museet i Trondheim
Tabellen under viser hvordan enkeltbitene danner et komplett, høy-sensitivt personkort når alle kildene slås sammen.
""")

    code("""# Bruker fasiten
krever_fasit()
kritiske = df_168[df_168["risikonivaa"] == "KRITISK"].sort_values(by="mosaikk_risikoscore", ascending=False)
print(f"🔴 Totalt {len(kritiske)} ansatte har KRITISK eksponeringsrisiko (Score >= 75/100):")
display(kritiske[[
    "ansatt_id", "navn", "fodselsdato", "adresse_trondheim",
    "stilling", "mosaikk_risikoscore", "avslort_sensitiv_innsikt"
]].head(20))""")

    # Steg 7: Nøktern oversikt over ansatte "på kanten" i arbeidshverdagen
    md("""## 7. Nærmere om ansatte «på kanten» (Hverdagsslitasje, tidsklemme og stram økonomi)
Her ser vi nøkternt på tre vanlige grupper som ligger i grenseland i arbeidshverdagen når vi kobler dataene:
1. **Slitasje og lange vakter:** Ansatte med mange lange vakter (10–11 timer), helse-/ergonominotat (f.eks. rygg eller migrene) og hyppig fravær.
2. **Tidsklemme og pendling:** Ansatte med småbarn under 12 år som pendler med Trønderbanen eller buss/trikk og får fravær ved kollektivstans.
3. **Stram økonomi eller ekstrajobb:** Ansatte i deltid eller med høy gjeldsbelastning i skattelisten, eller med bi-inntekt ved siden av museumsjobben.
""")

    code("""# Del B og C bruker fasiten
krever_fasit()
print("--- A. SLITASJE & LANGE VAKTER (Overtid >= 12 vakter + Helse/Fravær) ---")
slitasje = df_168[
    (df_168["overtid_aml_brudd"] >= 12) &
    (df_168["sykefravaer_dager"] >= 25)
].sort_values(by=["overtid_aml_brudd", "sykefravaer_dager"], ascending=False)
display(slitasje[[
    "ansatt_id", "navn", "stilling", "stillingsprosent", "primar_stasjon",
    "overtid_aml_brudd", "sykefravaer_dager", "helse_ergonomi_art9"
]].head(10))

print("\\n--- B. TIDSKLEMME (Småbarn + Pendling med kollektivavvik i Trondheim) ---")
tidsklemme = df_168[
    (df_168["antall_barn_under_12"] > 0) &
    (df_168["kollektiv_avvik_kobling"] != "Ingen treff mot kollektivstans")
].sort_values(by="antall_barn_under_12", ascending=False)
display(tidsklemme[[
    "ansatt_id", "navn", "bydel_kommune", "sivilstand",
    "antall_barn_under_12", "pendlerlinje_atb", "kollektiv_avvik_kobling"
]].head(10))

print("\\n--- C. STRAM ØKONOMI / HØY GJELDSBELASTNING I SKATTELISTEN ---")
stram_okonomi = df_168[
    df_168["inntektsavvik_analyse"].str.contains("gjeldsgrad")
].sort_values(by="virke_aarslonn_nok", ascending=True)
display(stram_okonomi[[
    "ansatt_id", "navn", "stilling", "stillingsprosent",
    "virke_aarslonn_nok", "skatteliste_nettoinntekt", "sivilstand", "antall_barn_under_12"
]].head(10))""")

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

    print(f"✅ Oppdatert Trondheim Colab-notebook lagret til: {notebook_path}")


if __name__ == "__main__":
    create_notebook()
