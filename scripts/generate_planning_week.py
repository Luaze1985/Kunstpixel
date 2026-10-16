"""Lag deterministiske, utelukkende fiktive øvingsdata for fire uker."""
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scenario = json.loads((ROOT / "05_data/hr_simulator/scenarios/HR-001.json").read_text(encoding="utf-8"))
start = date(2026, 10, 12)
weeks = [(start + timedelta(weeks=i)).isoformat() for i in range(4)]
persons = []
for old in scenario["persons"]:
    days = []
    for offset in range(28):
        day = start + timedelta(days=offset)
        if day.weekday() == 6:
            continue
        lo = datetime.combine(day, time(8, 0))
        hi = datetime.combine(day, time(21, 0))
        if old["id"] == "EMP-01":
            hi = datetime.combine(day, time(17, 0))
        days.append([lo.isoformat(timespec="minutes"), hi.isoformat(timespec="minutes")])
    persons.append({
        "id": old["id"], "name": old["name"], "person_type": old["person_type"],
        "position_percent": old["position_percent"],
        "email": old["email"], "phone": old["phone"], "skills": old["skills"],
        "training": {skill: True for skill in old["skills"]} if old["id"] != "POOL-01" else {},
        "availability": days, "source_ids": ["R-03"], "synthetic": True,
    })

templates = [
    (0, "Publikumsmottak", "fixed", "09:00", "16:00", {"vertskap": 1}, ["K-OLJE", "K-NOBEL"]),
    (1, "Skolebesøk", "event", "10:00", "12:00", {"formidling": 1, "vertskap": 1}, ["K-TEKNISK-PROGRAM"]),
    (3, "Utstillingsmontering", "fixed", "10:00", "14:00", {"montering": 2}, ["K-OLJE"]),
    (4, "Kveldsarrangement", "event", "17:00", "20:00", {"arrangementsledelse": 1, "vertskap": 1}, ["K-NOBEL", "K-TEKNISK-DRIFT"]),
    (5, "Helgevert", "fixed", "10:00", "16:00", {"vertskap": 1}, ["K-OLJE"]),
]
activities = []
assignments = []
agreed = {0: {"vertskap": "EMP-02"}, 1: {"formidling": "EMP-01"}, 3: {"montering": "EMP-03"}, 4: {"arrangementsledelse": "EMP-07"}}
for week_no in range(4):
    for weekday, title, kind, lo, hi, requirements, sources in templates:
        day = start + timedelta(weeks=week_no, days=weekday)
        aid = f"W{week_no + 1}-{weekday}-{kind}"
        start_at = f"{day}T{lo}"
        end_at = f"{day}T{hi}"
        prep = (datetime.fromisoformat(start_at) - timedelta(minutes=30)).isoformat(timespec="minutes")
        close = (datetime.fromisoformat(end_at) + timedelta(minutes=30)).isoformat(timespec="minutes")
        activities.append({"id": aid, "title": title, "kind": kind, "starts_at": start_at,
                           "ends_at": end_at, "work_start": prep, "work_end": close,
                           "requirements": requirements, "source_ids": sources,
                           "synthetic": True})
        for skill, person_id in agreed.get(weekday, {}).items():
            assignments.append({"activity_id": aid, "person_id": person_id, "skill": skill,
                                "agreed": True, "fact_id": f"AG-{aid}-{person_id}"})

data = {"version": "2026-10-16.1", "synthetic": True, "weeks": weeks, "persons": persons,
        "activities": activities, "assignments": assignments,
        "contacts": [{"activity_id": "W1-4-event", "person_id": "EMP-08", "status": "forespurt",
                      "recorded_at": "2026-10-12T10:00", "fact_id": "C-W1-EMP08"}],
        "source_ids": ["K-OLJE", "K-NOBEL", "K-TEKNISK-DRIFT", "K-TEKNISK-PROGRAM", "K-PLAN", "K-TID", "K-INNLEIE", "K-TARIFF"],
        "note": "Alle personer, tider, ferdigheter, opplæring og kontaktforløp er konstruerte øvingsdata."}
target = ROOT / "05_data/hr_simulator/planning_week.json"
target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(target)
