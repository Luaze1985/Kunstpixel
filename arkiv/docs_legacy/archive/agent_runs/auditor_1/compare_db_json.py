import json
import sqlite3

with open("data/samling.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

conn = sqlite3.connect("file:data/museum.db?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id, tittel, sal_id, status FROM verk ORDER BY id")
db_works = [dict(r) for r in c.fetchall()]

print(f"JSON works count: {len(json_data)}")
print(f"DB works count: {len(db_works)}")

json_ids = {w["id"] for w in json_data}
db_ids = {w["id"] for w in db_works}

print("All JSON works exist in DB:", json_ids.issubset(db_ids))
print("Extra in DB:", db_ids - json_ids)

tables = ["kunstnere", "saler", "verk", "utstillinger", "utstilling_verk", "hendelser", "publikum_faq"]
total = 0
for t in tables:
    c.execute(f"SELECT count(*) FROM {t}")
    cnt = c.fetchone()[0]
    total += cnt
    print(f"Table {t}: {cnt}")
print(f"Total rows in 7 business tables: {total}")
