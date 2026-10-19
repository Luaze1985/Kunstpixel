"""Deterministisk omforming av syntetisk HR-arkiv til planleggingspersoner."""
from __future__ import annotations

import csv
from datetime import date, datetime, time, timedelta
from pathlib import Path


ROLE_SKILLS = {
    "Formidlingsleder": ("formidling", "arrangementsledelse"),
    "Museumspedagog": ("formidling",),
    "Senior museumspedagog": ("formidling",),
    "DKS-koordinator (Skolesekken)": ("formidling",),
    "Museumsvert og omviser (Deltid)": ("vertskap", "formidling"),
    "Seniorvert / Skrankeleder": ("vertskap",),
    "Bygningstekniker / Montør": ("montering",),
    "AV- og utstillingslystekniker": ("montering",),
    "Drifts- og eiendomssjef": ("arrangementsledelse",),
    "Kommunikasjons- og markedssjef": ("arrangementsledelse",),
}
SKILLS = {"formidling", "vertskap", "montering", "arrangementsledelse"}
PROFILES = {"weekday", "host", "technical", "none"}
SOURCE_FIELDS = ("ansatt_id", "navn", "avdeling", "stilling", "ansatt_fra", "ansatt_til", "status", "stillingsprosent")
DRAFT_FIELDS = (*SOURCE_FIELDS, "skills", "training", "availability_profile")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DRAFT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def default_draft(source: list[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    for row in source:
        skills = ROLE_SKILLS.get(row["stilling"], ())
        profile = "host" if "vertskap" in skills else "technical" if "montering" in skills else "weekday" if skills else "none"
        # Tverrkompetanse er ukjent inntil den uttrykkelig settes i arbeidskopien.
        training = skills[:1]
        result.append({**{key: row[key] for key in SOURCE_FIELDS},
                       "skills": ";".join(skills), "training": ";".join(training),
                       "availability_profile": profile})
    return result


def validate_draft(rows: list[dict[str, str]], source: list[dict[str, str]]) -> list[str]:
    errors = []
    original = {row["ansatt_id"]: row for row in source}
    ids = [row.get("ansatt_id", "") for row in rows]
    if len(rows) != len(source) or set(ids) != set(original) or len(ids) != len(set(ids)):
        errors.append("Arbeidskopien må inneholde nøyaktig de 168 unike arkiv-ID-ene")
    for number, row in enumerate(rows, 2):
        pid = row.get("ansatt_id", "")
        if pid not in original:
            continue
        for key in SOURCE_FIELDS:
            if row.get(key) != original[pid].get(key):
                errors.append(f"Rad {number}: kildefeltet {key} kan ikke endres")
        skills = set(filter(None, row.get("skills", "").split(";")))
        training = set(filter(None, row.get("training", "").split(";")))
        if not skills <= SKILLS or not training <= skills:
            errors.append(f"Rad {number}: ukjent kompetanse eller opplæring uten kompetanse")
        if row.get("availability_profile") not in PROFILES:
            errors.append(f"Rad {number}: ukjent tilgjengelighetsprofil")
        try:
            start = date.fromisoformat(row["ansatt_fra"])
            end = date.fromisoformat(row["ansatt_til"]) if row["ansatt_til"] else None
            if end and end < start:
                errors.append(f"Rad {number}: sluttdato før startdato")
            percent = float(row["stillingsprosent"])
            if not 0 <= percent <= 1:
                errors.append(f"Rad {number}: stillingsprosent utenfor 0–1")
        except (ValueError, KeyError):
            errors.append(f"Rad {number}: ugyldig dato eller stillingsprosent")
    return errors


def availability(week_starts: list[date], profile: str) -> list[list[str]]:
    windows = []
    for week in week_starts:
        for offset in range(7):
            day = week + timedelta(days=offset)
            if profile == "none" or day.weekday() == 6:
                continue
            if day.weekday() == 5 and profile != "host":
                continue
            begin, end = ((8, 21) if profile == "host" else
                          (8, 18) if profile == "technical" else (8, 21))
            windows.append([datetime.combine(day, time(begin)).isoformat(timespec="minutes"),
                            datetime.combine(day, time(end)).isoformat(timespec="minutes")])
    return windows


def compile_people(rows: list[dict[str, str]], week_starts: list[date]) -> list[dict]:
    people = []
    for row in rows:
        pid = row["ansatt_id"]
        baseline = default_draft([row])[0]
        skills = list(filter(None, row["skills"].split(";")))
        training = set(filter(None, row["training"].split(";")))
        people.append({
            "id": pid, "name": row["navn"], "person_type": "employee",
            "position_percent": round(float(row["stillingsprosent"]) * 100),
            "email": f"{pid.lower()}@example.invalid", "phone": f"000{pid[-3:]}",
            "skills": skills, "training": {skill: True for skill in skills if skill in training},
            "availability": availability(week_starts, row["availability_profile"]),
            "employment_start": row["ansatt_fra"], "employment_end": row["ansatt_til"] or None,
            "department": row["avdeling"], "title": row["stilling"],
            "field_sources": {"employment": f"syntetisk arkiv:{pid}",
                              "skills": "fiktiv stillingsmapping:v1" if row["skills"] == baseline["skills"] else "redigert fiktiv arbeidskopi",
                              "training": "fiktiv øvingsregel:v1" if row["training"] == baseline["training"] else "redigert fiktiv arbeidskopi",
                              "availability": "fiktiv tilgjengelighetsprofil:v1" if row["availability_profile"] == baseline["availability_profile"] else "redigert fiktiv arbeidskopi"},
            "source_ids": ["R-03"], "synthetic": True,
        })
    return people
