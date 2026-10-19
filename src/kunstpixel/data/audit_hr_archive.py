"""Lokal, skrivebeskyttet kvalitetskontroll av det syntetiske HR-arkivet.

Kjør fra prosjektroten: py -3.13 src/kunstpixel/data/audit_hr_archive.py
Originalfilene leses bare. Resultatene skrives til 05_data/kvalitetskontroll_hr/.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "05_data"
OUTPUT = DATA / "kvalitetskontroll_hr"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def audit(
    data_dir: Path, as_of: date, shifts_path: Path | None = None
) -> tuple[dict[str, int], list[dict[str, object]]]:
    employees = read_csv(data_dir / "arkiv_hr_ansatte.csv")
    shifts = read_csv(shifts_path or (data_dir / "arkiv_hr_vakt_historikk.csv"))
    hires = read_csv(data_dir / "arkiv_hr_innleie.csv")
    exhibitions = read_csv(data_dir / "arkiv_utstillinger_2010_2026.csv")
    exhibition_key = "utstilling_id"

    counts = {
        "ansatte": len(employees),
        "vakter": len(shifts),
        "innleie": len(hires),
        "utstillinger": len(exhibitions),
    }
    findings: list[dict[str, object]] = []

    def add(kind: str, severity: str, entity: str, entity_id: str, detail: str) -> None:
        findings.append({
            "type": kind,
            "grad": severity,
            "entitet": entity,
            "id": entity_id,
            "detalj": detail,
        })

    employee_ids = {row["ansatt_id"] for row in employees}
    exhibition_ids = {row[exhibition_key] for row in exhibitions}
    for label, rows, key in (
        ("ansatt", employees, "ansatt_id"),
        ("vakt", shifts, "vakt_id"),
        ("innleie", hires, "innleie_id"),
        ("utstilling", exhibitions, exhibition_key),
    ):
        for entity_id, amount in Counter(row[key] for row in rows).items():
            if not entity_id:
                add("tom_id", "feil", label, "", f"{amount} rader uten ID")
            elif amount > 1:
                add("duplikat_id", "feil", label, entity_id, f"{amount} rader")

    daily_hours: dict[tuple[str, str], float] = defaultdict(float)
    daily_count: Counter[tuple[str, str]] = Counter()
    for row in shifts:
        shift_id = row["vakt_id"]
        person_id = row["ansatt_id"]
        if person_id not in employee_ids:
            add("ukjent_ansatt", "feil", "vakt", shift_id, person_id)
        if row["utstilling_id"] and row["utstilling_id"] not in exhibition_ids:
            add("ukjent_utstilling", "feil", "vakt", shift_id, row["utstilling_id"])
        try:
            shift_date = date.fromisoformat(row["dato"])
            hours = float(row["timer"])
            if not 0 < hours <= 24:
                add("ugyldig_timetall", "feil", "vakt", shift_id, row["timer"])
            else:
                key = (person_id, row["dato"])
                daily_hours[key] += hours
                daily_count[key] += 1
            if shift_date > as_of:
                add("fremtidig_vakt", "info", "vakt", shift_id, row["dato"])
            if str(shift_date.year) != row["aar"] or str(shift_date.month) != row["maaned"]:
                add("datoavvik", "feil", "vakt", shift_id, row["dato"])
        except (ValueError, TypeError):
            add("ugyldig_dato_eller_timer", "feil", "vakt", shift_id, f"{row['dato']} / {row['timer']}")

    for (person_id, day), hours in sorted(daily_hours.items()):
        if hours > 24:
            add("over_24_timer_per_dag", "feil", "persondag", f"{person_id}:{day}",
                f"{hours:g} timer fordelt på {daily_count[(person_id, day)]} vaktposter")
        elif hours > 13:
            add("over_13_timer_per_dag", "kontroll", "persondag", f"{person_id}:{day}",
                f"{hours:g} timer fordelt på {daily_count[(person_id, day)]} vaktposter")

    for row in hires:
        hire_id = row["innleie_id"]
        if row["godkjent_av_ansatt_id"] not in employee_ids:
            add("ukjent_godkjenner", "feil", "innleie", hire_id, row["godkjent_av_ansatt_id"])
        if row["knyttet_utstilling_id"] and row["knyttet_utstilling_id"] not in exhibition_ids:
            add("ukjent_utstilling", "feil", "innleie", hire_id, row["knyttet_utstilling_id"])
        try:
            if date.fromisoformat(row["periode_fra"]) > date.fromisoformat(row["periode_til"]):
                add("omvendt_periode", "feil", "innleie", hire_id,
                    f"{row['periode_fra']}–{row['periode_til']}")
            expected = float(row["fakturerte_timer"]) * float(row["timepris_nok"])
            actual = float(row["totalbelop_nok"])
            if abs(expected - actual) > 0.01:
                add("belopsavvik", "feil", "innleie", hire_id,
                    f"forventet {expected:g}, registrert {actual:g}")
        except (ValueError, TypeError):
            add("ugyldig_innleie_felt", "feil", "innleie", hire_id, "periode eller beløp")

    return counts, findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Referansedato YYYY-MM-DD")
    args = parser.parse_args()
    as_of = date.fromisoformat(args.as_of)
    counts, findings = audit(DATA, as_of)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fields = ["type", "grad", "entitet", "id", "detalj"]
    write_csv(OUTPUT / "avvik.csv", findings, fields)
    # Arbeidskopi: behold alle vakter, men gjør det mulig å filtrere bort
    # usikre persondager uten å endre eller gjette på kildedata.
    blocked_days = {str(row["id"]) for row in findings if row["type"] == "over_24_timer_per_dag"}
    review_days = {str(row["id"]) for row in findings if row["type"] == "over_13_timer_per_dag"}
    invalid_shifts = {
        str(row["id"]) for row in findings
        if row["entitet"] == "vakt" and row["grad"] == "feil"
    }
    future_shifts = {str(row["id"]) for row in findings if row["type"] == "fremtidig_vakt"}
    source_shifts = read_csv(DATA / "arkiv_hr_vakt_historikk.csv")
    checked_shifts: list[dict[str, object]] = []
    for shift in source_shifts:
        day_id = f"{shift['ansatt_id']}:{shift['dato']}"
        reasons = []
        if shift["vakt_id"] in invalid_shifts or day_id in blocked_days:
            status = "sperret"
            reasons.append("feil i rad eller over 24 timer på persondag")
        elif day_id in review_days:
            status = "manuell_kontroll"
            reasons.append("over 13 timer på persondag")
        elif shift["vakt_id"] in future_shifts:
            status = "planlagt_fremtidig"
            reasons.append("fremtidig syntetisk vakt")
        else:
            status = "ingen_funn_i_disse_reglene"
        if shift["vakt_id"] in future_shifts and status != "planlagt_fremtidig":
            reasons.append("fremtidig syntetisk vakt")
        checked_shifts.append({
            **shift,
            "kontrollstatus": status,
            "kontrollmerknad": "; ".join(reasons),
        })
    write_csv(
        OUTPUT / "vakter_arbeidskopi.csv",
        checked_shifts,
        list(source_shifts[0]) + ["kontrollstatus", "kontrollmerknad"],
    )
    status_counts = Counter(str(row["kontrollstatus"]) for row in checked_shifts)
    by_type = Counter(row["type"] for row in findings)
    lines = [
        "# Lokal kvalitetskontroll av syntetisk HR-arkiv",
        "",
        f"Referansedato: {as_of.isoformat()}. Kilder: CSV-filene i `05_data/`.",
        "Originalfilene er ikke endret. Ingen rader er automatisk rettet eller slettet.",
        "",
        "## Omfang",
        "",
        *(f"- {label}: {amount}" for label, amount in counts.items()),
        "",
        "## Funn",
        "",
        *(f"- {label}: {amount}" for label, amount in sorted(by_type.items())),
        "",
        "## Vakter i arbeidskopien",
        "",
        *(f"- {label}: {amount}" for label, amount in sorted(status_counts.items())),
        "",
        "Detaljene med ID-er ligger i `avvik.csv`. Persondager over 24 timer er umulige",
        "som faktisk arbeid. Persondager over 13 timer trenger kontroll, men er ikke alene",
        "bevis for regelbrudd. Flere poster samme dag er ikke nødvendigvis overlapp,",
        "fordi materialet mangler klokkeslett. Fremtidige vakter er merket som informasjon",
        "fordi arkivet er syntetisk. Ingen avvik gir grunnlag for å gjette nye tider.",
        "",
        "`vakter_arbeidskopi.csv` inneholder alle originalradene med kontrollstatus.",
        "`sperret` betyr dokumentert datakonflikt, `manuell_kontroll` betyr høy",
        "dagsum, og `ingen_funn_i_disse_reglene` betyr bare at disse kontrollene",
        "ikke fant avvik. Kopien beviser ikke klokkeslett, hvile eller lovlighet.",
        "",
        "## Neste bruk",
        "",
        "Retting bør skje i datageneratoren eller i en egen, gjennomgått arbeidskopi.",
        "Dette arkivet er fortsatt ikke koblet til ukeplan-demoens personer og kandidater.",
    ]
    (OUTPUT / "SAMMENDRAG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Kontroll ferdig: {len(findings)} avvik/merknader. Se {OUTPUT / 'SAMMENDRAG.md'}")


if __name__ == "__main__":
    main()
