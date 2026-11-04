"""CLI inspector for Kunstpixel HR, Innleie & Exhibition Archive (Kunstsilo Scale)."""

import json
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "05_data"


def inspect():
    print("=" * 65)
    print(" KUNSTPIXEL ARKIVINSPEKSJON (2010–2026) — KUNSTSILO-SKALA")
    print("=" * 65)

    # 1. HR-ansatte
    emp_file = DATA_DIR / "arkiv_hr_ansatte.csv"
    if emp_file.exists():
        df_emp = pd.read_csv(emp_file)
        print(f"\n[+] HR-historikk: {len(df_emp):,} ansatte registrert (2010–2026).")
        print("\nFordeling per avdeling:")
        print(df_emp["avdeling"].value_counts().to_string())
        print("\nStatus:")
        print(df_emp["status"].value_counts().to_string())

    # 2. Innleieliste (Ny modul)
    inn_file = DATA_DIR / "arkiv_hr_innleie.csv"
    if inn_file.exists():
        df_inn = pd.read_csv(inn_file)
        print(f"\n[+] Innleie og eksterne oppdrag: {len(df_inn):,} kontrakter registrert.")
        print(f"Totalt innleiebeløp: {df_inn['totalbelop_nok'].sum():,} NOK ({df_inn['fakturerte_timer'].sum():,} fakturerte timer).")
        print("\nFordeling per leverandørkategori:")
        summary_kat = df_inn.groupby("kategori").agg(
            oppdrag=("innleie_id", "count"),
            timer=("fakturerte_timer", "sum"),
            totalt_nok=("totalbelop_nok", "sum")
        )
        print(summary_kat.to_string())

        print("\nEksempel på innleieoppdrag:")
        sample_cols = ["aar", "kategori", "leverandor", "fakturerte_timer", "totalbelop_nok", "oppdragsbeskrivelse"]
        print(df_inn.sample(3, random_state=42)[sample_cols].to_string(index=False))

    # 3. Utstillinger
    exh_file = DATA_DIR / "arkiv_utstillinger_2010_2026.csv"
    if exh_file.exists():
        df_exh = pd.read_csv(exh_file)
        print(f"\n[+] Utstillingsarkiv: {len(df_exh):,} utstillinger katalogisert (2010–2026).")
        print(f"Totalt akkumulert publikumsbesøk: {df_exh['besokstall_total'].sum():,} besøkende.")

    # 4. Personas / CV
    cv_file = DATA_DIR / "arkiv_cv_personas.json"
    if cv_file.exists():
        with open(cv_file, "r", encoding="utf-8") as f:
            personas = json.load(f)
        print(f"\n[+] Personas & CV-base: {len(personas):,} detaljerte faglige CV-er for faste nøkkelroller.")

    # 5. Vakthistorikk
    shifts_file = DATA_DIR / "arkiv_hr_vakt_historikk.parquet"
    if shifts_file.exists():
        import duckdb
        count = duckdb.query(f"SELECT COUNT(*) FROM '{shifts_file}'").fetchone()[0]
        print(f"\n[+] Vakthistorikk (Parquet): {count:,} vaktlinjer logget.")


if __name__ == "__main__":
    inspect()
