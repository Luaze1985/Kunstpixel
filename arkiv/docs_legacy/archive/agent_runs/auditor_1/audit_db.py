import sqlite3
import json

db_path = "g:/Min disk/Fellesprosjekt KI/data/museum.db"
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("PRAGMA integrity_check;")
print("PRAGMA integrity_check:", c.fetchall()[0][0])

c.execute("PRAGMA foreign_key_check;")
fk_violations = c.fetchall()
print("PRAGMA foreign_key_check:", fk_violations)

c.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = c.fetchall()

total_rows = 0
table_counts = {}
for t in tables:
    name = t["name"]
    c.execute(f"SELECT count(*) as cnt FROM [{name}];")
    cnt = c.fetchone()["cnt"]
    table_counts[name] = cnt
    total_rows += cnt
    print(f"Table {name}: {cnt} rows")

print(f"Total tables: {len(tables)}, Total rows: {total_rows}")

print("\n--- SAMPLE ROWS ---")
for t in tables:
    name = t["name"]
    c.execute(f"SELECT * FROM [{name}] LIMIT 2;")
    rows = [dict(r) for r in c.fetchall()]
    print(f"\nSample from {name}:")
    for r in rows:
        # truncate wall text if long
        if "veggtekst" in r and r["veggtekst"] and len(r["veggtekst"]) > 60:
            r["veggtekst"] = r["veggtekst"][:60] + "..."
        print(" ", r)

