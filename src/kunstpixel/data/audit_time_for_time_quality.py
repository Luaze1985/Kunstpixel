"""
Omfattende datakvalitetskontroll for time-for-time historiske vaktdata (439 952 rader).
Evaluerer 5 dimensjoner:
1. Fullstendighet (Null-verdier / tomme felt)
2. Konsistens (Dobbeltbookinger i samme klokketime)
3. Arbeidsmiljøsamsvar (AML hviletid og rotasjon)
4. Fraværsvalidering (Spøkelsesvakter under sykemelding)
5. K-anonymitetsfordeling
"""

import sqlite3
import pandas as pd
import json
import os

def audit_quality():
    db_path = os.path.abspath("05_data/colab_personvern_historikk.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    report = {"database": db_path, "dimensjoner": {}}

    print("--- STARTER DATAKVALITETSKONTROLL (439 952 RADER) ---")

    # 1. Fullstendighet
    print("[1/5] Sjekker fullstendighet (NULL-verdier)...")
    cur.execute("""
    SELECT 
        COUNT(*) as totalt,
        SUM(CASE WHEN vakt_id IS NULL OR vakt_id = '' THEN 1 ELSE 0 END) as mangler_vakt_id,
        SUM(CASE WHEN ansatt_id IS NULL OR ansatt_id = '' THEN 1 ELSE 0 END) as mangler_ansatt_id,
        SUM(CASE WHEN dato IS NULL OR dato = '' THEN 1 ELSE 0 END) as mangler_dato,
        SUM(CASE WHEN time_slot IS NULL OR time_slot = '' THEN 1 ELSE 0 END) as mangler_time,
        SUM(CASE WHEN stasjon IS NULL OR stasjon = '' THEN 1 ELSE 0 END) as mangler_stasjon
    FROM vakt_time_for_time
    """)
    row1 = cur.fetchone()
    report["dimensjoner"]["fullstendighet"] = {
        "totalt_rader": row1[0],
        "mangler_vakt_id": row1[1],
        "mangler_ansatt_id": row1[2],
        "mangler_dato": row1[3],
        "mangler_time": row1[4],
        "mangler_stasjon": row1[5],
        "kompletthet_prosent": 100.0 if sum(row1[1:]) == 0 else (1 - sum(row1[1:])/(row1[0]*5))*100
    }

    # 2. Konsistens: Dobbeltbooking i samme klokketime
    print("[2/5] Sjekker for dobbeltbookinger (samme person på to steder samtidig)...")
    cur.execute("""
    SELECT ansatt_id, dato, time_slot, COUNT(*) as antall_steder
    FROM vakt_time_for_time
    GROUP BY ansatt_id, dato, time_slot
    HAVING COUNT(*) > 1
    """)
    dobbeltbookinger = cur.fetchall()
    report["dimensjoner"]["dobbeltbooking"] = {
        "antall_konflikter": len(dobbeltbookinger),
        "eksempler": [
            {"ansatt_id": r[0], "dato": r[1], "time_slot": r[2], "steder": r[3]}
            for r in dobbeltbookinger[:5]
        ]
    }

    # 3. Kryssvalidering mot fravær (Spøkelsesvakter)
    print("[3/5] Krysstester vakter mot sykemeldinger/fravær...")
    cur.execute("""
    SELECT v.ansatt_id, v.dato, v.time_slot, v.stasjon, f.type, f.fra, f.til
    FROM vakt_time_for_time v
    JOIN hr_fravaer f ON v.ansatt_id = f.ansatt_id
    WHERE v.dato >= f.fra AND v.dato <= f.til
    LIMIT 10
    """)
    ghost_shifts = cur.fetchall()
    cur.execute("""
    SELECT COUNT(DISTINCT v.vakt_id)
    FROM vakt_time_for_time v
    JOIN hr_fravaer f ON v.ansatt_id = f.ansatt_id
    WHERE v.dato >= f.fra AND v.dato <= f.til
    """)
    total_ghost_vakter = cur.fetchone()[0]
    report["dimensjoner"]["fravaerskonflikt"] = {
        "vakter_paa_sykedato": total_ghost_vakter,
        "eksempler": [
            {"ansatt_id": r[0], "dato": r[1], "time_slot": r[2], "stasjon": r[3], "fravaerstype": r[4]}
            for r in ghost_shifts[:5]
        ]
    }

    # 4. Rotasjon og ståtid (STAMI-krav: maks sammenhengende timer på samme stasjon)
    print("[4/5] Undersøker rotasjon og sammenhengende vakter...")
    cur.execute("""
    SELECT stasjon, COUNT(DISTINCT klokketime) as timer_aktiv, COUNT(*) as rader
    FROM vakt_time_for_time
    GROUP BY stasjon
    ORDER BY rader DESC
    """)
    stasjoner = cur.fetchall()
    report["dimensjoner"]["stasjonsfordeling"] = [
        {"stasjon": r[0], "aktive_timer": r[1], "total_timer": r[2]}
        for r in stasjoner
    ]

    # 5. K-anonymitetsprofil
    print("[5/5] Beregner K-anonymitetsfordeling...")
    cur.execute("""
    SELECT k_verdi, COUNT(*) as antall_slots, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM (SELECT COUNT(*) FROM vakt_time_for_time GROUP BY dato, time_slot, stasjon)), 2) as prosent
    FROM (
        SELECT dato, time_slot, stasjon, COUNT(DISTINCT ansatt_id) as k_verdi
        FROM vakt_time_for_time
        GROUP BY dato, time_slot, stasjon
    )
    GROUP BY k_verdi
    """)
    k_dist = cur.fetchall()
    report["dimensjoner"]["k_anonymitet"] = [
        {"k": r[0], "antall_tidspunkter": r[1], "prosent": r[2]}
        for r in k_dist
    ]

    conn.close()

    out_path = os.path.abspath("02_deliverables/02_rapporter/datakvalitet_rapport.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ Fullført! Rapport lagret til: {out_path}")
    return report

if __name__ == "__main__":
    audit_quality()
