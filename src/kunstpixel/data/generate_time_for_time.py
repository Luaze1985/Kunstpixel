"""
Genererer time-for-time historiske vaktdata og eksporterer til en ren
Colab-klar SQLite-database (05_data/colab_personvern_historikk.db)
samt en representativ CSV-fil for testing.
"""

import os
import csv
import sqlite3
from datetime import datetime

def generate_hourly_records():
    data_dir = os.path.abspath("05_data")
    vakt_hist_csv = os.path.join(data_dir, "arkiv_hr_vakt_historikk.csv")
    vakt_klokke_csv = os.path.join(data_dir, "arkiv_hr_vakt_klokkeslett.csv")
    ansatte_csv = os.path.join(data_dir, "arkiv_hr_ansatte.csv")
    fravaer_csv = os.path.join(data_dir, "arkiv_hr_fravaer.csv")
    db_out = os.path.join(data_dir, "colab_personvern_historikk.db")
    sample_csv_out = os.path.join(data_dir, "vakt_time_for_time_2025_2026.csv")

    print("[1/5] Laster inn klokkeslett for vakter...")
    times = {}
    with open(vakt_klokke_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times[row["vakt_id"]] = (row["start"], row["slutt"])

    print(f"       Fant {len(times)} vakt-klokkeslett.")

    # Klargjør database
    if os.path.exists(db_out):
        os.remove(db_out)

    conn = sqlite3.connect(db_out)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE vakt_time_for_time (
        vakt_id TEXT,
        ansatt_id TEXT,
        dato TEXT,
        aar INTEGER,
        maaned INTEGER,
        time_slot TEXT,
        klokketime INTEGER,
        stasjon TEXT,
        avdeling TEXT,
        rolle TEXT,
        utstilling_id TEXT
    )
    """)

    print("[2/5] Ekspanderer vakter til time-for-time rader...")
    batch = []
    sample_rows = []
    total_hourly_rows = 0

    with open(vakt_hist_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid = row["vakt_id"]
            if vid not in times:
                continue
            start_str, slutt_str = times[vid]
            start_h = int(start_str.split(":")[0])
            slutt_h = int(slutt_str.split(":")[0])
            if slutt_h < start_h:
                # Nattskift eller kveld
                slutt_h += 24

            aar = int(row["aar"])
            maaned = int(row["maaned"])
            dato = row["dato"]
            aid = row["ansatt_id"]
            stasjon = row["stasjon"]
            avdeling = row["avdeling"]
            rolle = row["rolle"]
            utstilling = row["utstilling_id"]

            for h in range(start_h, slutt_h):
                actual_h = h % 24
                slot_str = f"{actual_h:02d}:00"
                rec = (
                    vid, aid, dato, aar, maaned, slot_str, actual_h,
                    stasjon, avdeling, rolle, utstilling
                )
                batch.append(rec)
                if aar in (2025, 2026):
                    sample_rows.append(rec)

                if len(batch) >= 50000:
                    cur.executemany("INSERT INTO vakt_time_for_time VALUES (?,?,?,?,?,?,?,?,?,?,?)", batch)
                    total_hourly_rows += len(batch)
                    batch = []

    if batch:
        cur.executemany("INSERT INTO vakt_time_for_time VALUES (?,?,?,?,?,?,?,?,?,?,?)", batch)
        total_hourly_rows += len(batch)

    print(f"       Totalt generert: {total_hourly_rows} time-for-time rader!")

    print("[3/5] Bygger indekser for lynraske spørringer...")
    cur.execute("CREATE INDEX idx_vakt_tid_stasjon ON vakt_time_for_time (dato, time_slot, stasjon)")
    cur.execute("CREATE INDEX idx_vakt_ansatt ON vakt_time_for_time (ansatt_id, dato)")
    cur.execute("CREATE INDEX idx_vakt_aar ON vakt_time_for_time (aar)")

    print("[4/5] Kopierer ansatte, fravær og avvik til Colab-databasen...")
    # Ansatte
    cur.execute("""
    CREATE TABLE hr_ansatte (
        ansatt_id TEXT PRIMARY KEY,
        navn TEXT,
        kjonn TEXT,
        fodselsaar INTEGER,
        avdeling TEXT,
        stilling TEXT,
        lonnstrinn_virke INTEGER,
        epost TEXT,
        styrk08_kode TEXT
    )
    """)
    if os.path.exists(ansatte_csv):
        with open(ansatte_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ansatt_batch = [
                (
                    r["ansatt_id"], r["navn"], r.get("kjonn", ""),
                    int(r.get("fodselsaar", 1980) or 1980), r["avdeling"],
                    r["stilling"], int(r.get("lonnstrinn_virke", 30) or 30),
                    r.get("epost", ""), r.get("styrk08_kode", "")
                )
                for r in reader
            ]
            cur.executemany("INSERT INTO hr_ansatte VALUES (?,?,?,?,?,?,?,?,?)", ansatt_batch)

    # Fravær
    cur.execute("""
    CREATE TABLE hr_fravaer (
        fravaer_id TEXT,
        ansatt_id TEXT,
        fra TEXT,
        til TEXT,
        type TEXT
    )
    """)
    if os.path.exists(fravaer_csv):
        with open(fravaer_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fravaer_batch = [
                (r.get("fravaer_id", ""), r["ansatt_id"], r["fra"], r["til"], r["type"])
                for r in reader
            ]
            cur.executemany("INSERT INTO hr_fravaer VALUES (?,?,?,?,?)", fravaer_batch)

    # Avvik fra museum.db (read-only)
    cur.execute("""
    CREATE TABLE avvik_hms (
        avvik_id TEXT,
        dato TEXT,
        kategori TEXT,
        alvorlighetsgrad TEXT,
        berort_sal_id TEXT,
        beskrivelse TEXT
    )
    """)
    src_db = os.path.join(data_dir, "museum.db")
    if os.path.exists(src_db):
        ro_conn = sqlite3.connect(f"file:{src_db}?mode=ro", uri=True)
        ro_cur = ro_conn.cursor()
        avvik_rows = ro_cur.execute(
            "SELECT avvik_id, dato, kategori, alvorlighetsgrad, berort_sal_id, beskrivelse FROM avvik_hms_drift"
        ).fetchall()
        cur.executemany("INSERT INTO avvik_hms VALUES (?,?,?,?,?,?)", avvik_rows)
        ro_conn.close()

    conn.commit()
    conn.close()
    print(f"       Fullført eksport til SQLite: {db_out} ({os.path.getsize(db_out) / (1024*1024):.1f} MB)")

    print("[5/5] Skriver representativ sample-CSV for 2025–2026...")
    with open(sample_csv_out, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vakt_id", "ansatt_id", "dato", "aar", "maaned", "time_slot", "klokketime", "stasjon", "avdeling", "rolle", "utstilling_id"])
        writer.writerows(sample_rows)
    print(f"       Skrevet {len(sample_rows)} rader til: {sample_csv_out} ({os.path.getsize(sample_csv_out) / (1024*1024):.1f} MB)")

if __name__ == "__main__":
    generate_hourly_records()
