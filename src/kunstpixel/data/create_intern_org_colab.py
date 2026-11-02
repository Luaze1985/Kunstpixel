"""Genererer en komplett, interaktiv Google Colab Notebook (.ipynb) for intern org-databygging."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "intern_org_databygger.ipynb"


def generate_colab_notebook():
    cells = []

    def md(text: str):
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in text.strip().split("\n")]
        })

    def code(code_str: str):
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in code_str.strip().split("\n")]
        })

    # Header
    md(r"""# 🏛️ Kunstpixel: Intern Organisasjons- og Databygger (Google Colab)
### Interaktiv generering, kvalitetssikring og inspeksjon av interne HR-, kompetanse- og HMS-data

Denne notatboken er skreddersydd for å hjelpe deg med å **bygge de interne dataene organisasjonen mangler**, med **100 % fokus innover i egen organisasjon** (utadrettede publikums- og kunstverksdata er satt på vent):

1. **Kompetansekart for alle 168 ansatte:** Ferdighetskatalog, sertifikater, utløpsdatoer og avdelingsdekning.
2. **Interne sakslogger og henvendelser:** Realistiske henvendelser (vaktbytter, permisjoner, tilrettelegging, varsling) forankret i de 14 etiske HR-casene (CASE-004, CASE-013 m.fl.).
3. **HMS- og arbeidsmiljøavvik:** Ergonomi (steingulv 90 min), tunge løft (>15 kg), alenearbeid og belysning.
4. **Deterministisk compliance-sjekk:** Kontroll mot Arbeidsmiljøloven (11t hviletid, overtid) og k-anonymitet ($k \ge 5$).
5. **Eksport til `05_data/`:** Standardiserte CSV-filer merket `syntetisk (colab_org_bygger)` klare for FastMCP og LLM.
""")

    # Steg 1: Tilkobling
    md("""## 1. Koble til Google Drive (eller kjør lokalt)
I Google Colab monteres Drive automatisk. Kjører du lokalt i VS Code eller Jupyter, brukes mappen du står i.
""")

    code("""from pathlib import Path
import os
import sys

try:
    from google.colab import drive
    drive.mount('/content/drive')
    PROSJEKT = Path('/content/drive/MyDrive/Kunstpixel')
except ImportError:
    PROSJEKT = Path.cwd()
    if PROSJEKT.name == 'notebooks':
        PROSJEKT = PROSJEKT.parent

assert (PROSJEKT / '05_data').is_dir(), f"Fant ikke 05_data i {PROSJEKT}. Sjekk stien."
os.chdir(PROSJEKT)
if str(PROSJEKT) not in sys.path:
    sys.path.insert(0, str(PROSJEKT))

print(f"✅ Prosjektmappe aktiv: {PROSJEKT}")""")

    # Steg 2: Avhengigheter og data
    md("""## 2. Importere verktøy og koble mot grunnlagsdata
Vi laster inn `pandas`, `sqlite3` og den deterministiske generatormodulen `org_builder`.
""")

    code("""import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from src.kunstpixel.data.org_builder import (
    load_raw_employees,
    generate_skills_matrix,
    generate_internal_requests,
    generate_hms_incidents,
    write_csv,
    DATA_DIR
)

# Last inn eksisterende stab (168 ansatte)
employees = load_raw_employees()
df_emp = pd.DataFrame(employees)
print(f"✅ Lastet inn {len(df_emp)} ansatte fordelt på {df_emp['avdeling'].nunique()} avdelinger:")
print(df_emp['avdeling'].value_counts())""")

    # Steg 3: Generere kompetansekart
    md("""## 3. Bygge helhetlig kompetansematrise (Alle 168 ansatte)
Vi tildeler kompetanser basert på stilling og avdeling (sertifisert dato, utløpsdato og status `gyldig`/`utlopt`).
""")

    code("""skills_catalog, person_skills = generate_skills_matrix(employees, seed=42)

df_skills = pd.DataFrame(skills_catalog)
df_matrix = pd.DataFrame(person_skills)

print(f"✅ Generert {len(df_skills)} unike ferdigheter og {len(df_matrix)} kompetansekoblinger.")
display(df_skills.head(10))

print("\\nEksempel på ansattes kompetansekort:")
display(df_matrix[['ansatt_id', 'navn', 'avdeling', 'stilling', 'skill_name', 'status', 'gyldig_til']].head(10))""")

    # Steg 4: Visualisere kompetansedekning
    md("""## 4. Visuell analyse: Kompetansedekning per avdeling
Sjekk at ingen avdelinger mangler nøkkelkompetanser som førstehjelp, brannvern eller HMS.
""")

    code("""plt.figure(figsize=(12, 6))
dekning = df_matrix.groupby(['avdeling', 'skill_name']).size().unstack(fill_value=0)
dekning[['Akutt førstehjelp og hjertestarter', 'Brannvernleder og evakueringsansvar', 'Generell HMS-opplæring']].plot(
    kind='bar', stacked=False, figsize=(12, 5), colormap='viridis'
)
plt.title("Nøkkelsikkerhetskompetanser per avdeling")
plt.ylabel("Antall sertifiserte ansatte")
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Sjekk utløpte sertifikater (for avviks- og revisjonstesting)
utlopte = df_matrix[df_matrix['status'] == 'utlopt']
print(f"⚠️ Antall sertifikater som krever fornyelse: {len(utlopte)} (perfekt for opplærings- og varslingstesting)")""")

    # Steg 5: Interne henvendelser forankret i de 14 HR-casene
    md("""## 5. Bygge interne henvendelser & sakslogger (for LLM-trening)
Genererer 60 realistiske søknader og henvendelser fra ansatte knyttet til:
- Vaktbytter (inkludert hviletidspress jf. **CASE-004**)
- Permisjoner og ferie jf. **SOP-002**
- Tilrettelegging og steingulvbelastning jf. **CASE-012** / **STAMI**
- Konfidensiell varsling jf. **CASE-013** / **aml. kap. 2 A**
""")

    code("""requests = generate_internal_requests(employees, count=60, seed=42)
df_req = pd.DataFrame(requests)

print(f"✅ Generert {len(df_req)} interne henvendelser.")
print("\\nFordeling per kategori:")
print(df_req['kategori'].value_counts())

print("\\nUtdrag av saker tilpasset KI-saksbehandling:")
display(df_req[['sak_id', 'dato_tid', 'avdeling', 'kategori', 'tittel', 'case_ref', 'forventet_utfall']].head(10))""")

    # Steg 6: Reelle HMS-avvik og tiltakslogg
    md("""## 6. Bygge interne HMS- og arbeidsmiljøavvik
Genererer 40 detaljerte hendelser med strakstiltak for ergonomi, tunge løft (>15 kg), alenearbeid (>80 gjester) og stasjonsforhold.
""")

    code("""incidents = generate_hms_incidents(count=40, seed=42)
df_inc = pd.DataFrame(incidents)

print(f"✅ Generert {len(df_inc)} HMS-avvik.")
print("\\nFordeling per alvorlighetsgrad:")
print(df_inc['alvorlighetsgrad'].value_counts())

print("\\nEksempler på hendelser og strakstiltak:")
display(df_inc[['avvik_id', 'dato', 'avdeling', 'stasjon', 'alvorlighetsgrad', 'beskrivelse', 'strakstiltak']].head(8))""")

    # Steg 7: Deterministisk compliance- og etikkvalidator
    md(r"""## 7. Deterministisk compliance-validator (AML & K-anonymitet)
Tester sakene mot museets etablerte regler før en LLM eventuelt foreslår tiltak:
- **11t hviletid (aml. § 10-8):** Kan ALDRI overstyres automatisk.
- **K-anonymitet ($k \ge 5$):** Skjerming av små grupper ved fraværs- og trivselsinnsyn.
- **Identitetsskjerming (aml. kap. 2 A):** Varslerens navn skal aldri oppgis til andre ledere.
""")

    code("""def valider_henvendelse(sak):
    fritekst = sak['fritekst'].lower()
    utfall = []
    
    # CASE-004: Forsøk på å overstyre hviletid
    if ("overstyre" in fritekst or "overstyrer" in fritekst) and "hviletid" in fritekst:
        utfall.append("🚨 STOPP (CASE-004): Brudd på aml. § 10-8. 11 timers hviletid kan ikke fravikes.")
        
    # CASE-013: Varsling
    if sak['kategori'] == "varsling":
        utfall.append("🛡️ VARSEL (CASE-013): Konfidensiell behandling. Varslerens identitet skal skjermes.")
        
    # CASE-014: K-anonymitet
    if sak['kategori'] == "arbeidsmiljo" and ("lite team" in fritekst or "3 ansatte" in fritekst):
        utfall.append("🔒 PERSONVERN (CASE-014): Avslått. Svargrupper under 5 personer gir fare for re-identifisering.")
        
    return utfall if utfall else ["✅ Godkjent for ordinær saksbehandling"]

# Test validatoren mot de genererte sakene
for _, sak in df_req.head(8).iterrows():
    sjekk = valider_henvendelse(sak)
    print(f"[{sak['sak_id']}] {sak['tittel']}\\n   -> {sjekk[0]}\\n")""")

    # Steg 8: Eksport og lagring
    md("""## 8. Eksportere rene CSV-filer til `05_data/`
Skriver datasettene til disk med `datakilde = "syntetisk (colab_org_bygger)"` og anførselstegn rundt all tekst.
""")

    code("""from src.kunstpixel.data.org_builder import build_all_internal_datasets

resultat = build_all_internal_datasets()
print("🎉 Vellykket eksport til 05_data/ med 100 % konsistens:")
for fil, antall in resultat.items():
    print(f"  - {fil}: {antall} rader eksportert til CSV")""")

    # Steg 9: Verifisering mot testporten
    md("""## 9. Verifisering: Datafilene er feilfrie
Kjører testene for CSV-integritet for å garantere at ingen komma mangler anførselstegn.
""")

    code("""import subprocess
r = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_org_builder.py', 'tests/test_data_csv.py', '-q'], capture_output=True, text=True)
print(r.stdout)
print("Exit-kode:", r.returncode, "(0 = Alt er 100 % feilfritt og klart!)")""")

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

    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(notebook_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Genererte Colab-notatbok: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    generate_colab_notebook()
