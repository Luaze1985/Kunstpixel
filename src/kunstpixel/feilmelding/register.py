"""Registeret over feilmeldinger: én CSV-fil i repoet som kan åpnes i Excel.

En ansatt som er i jobb, velger et objekt, ser originalen og melder fra til
systemansvarlig. Et øyeblikksbilde av originalen lagres sammen med meldingen,
så feilen kan kontrolleres senere selv om dataene er endret i mellomtiden.
"""

from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path

from src.kunstpixel.feilmelding import objekter
from src.kunstpixel.persondata.config import PROJECT_ROOT

REGISTER_STI = PROJECT_ROOT / "05_data" / "feilmeldinger" / "feilmeldinger.csv"
MOTTAKER = "Systemansvarlig (byggeteamet)"
STATUSER = ("ny", "under arbeid", "rettet", "avvist")
KOLONNER = [
    "melding_id", "meldt", "melder_ansatt_id", "melder_navn", "oppgave", "objekttype", "objekt_id",
    "objekt_visning", "felt", "verdi_da", "beskrivelse", "forslag", "kilde", "original", "mottaker",
    "status", "status_dato", "kommentar",
]


def _naa() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


def liste(status: str | None = None) -> list[dict]:
    if not REGISTER_STI.is_file():
        return []
    with open(REGISTER_STI, encoding="utf-8-sig", newline="") as f:
        rader = list(csv.DictReader(f, delimiter=";"))
    return [r for r in rader if status is None or r["status"] == status]


def _skriv(rader: list[dict]) -> None:
    REGISTER_STI.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTER_STI.with_name(REGISTER_STI.name + ".tmp")
    with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KOLONNER, delimiter=";")
        w.writeheader()
        w.writerows(rader)
    tmp.replace(REGISTER_STI)


def registrer(melding: dict, naa: str | None = None) -> str:
    """Valider og lagre en feilmelding. Gir melding_id (FM-0001, FM-0002, ...)."""
    naa = naa or _naa()
    dag = date.fromisoformat(naa[:10])
    melder = next((a for a in objekter.aktive_ansatte(dag) if a["ansatt_id"] == melding.get("melder_ansatt_id")), None)
    if melder is None:
        raise ValueError("Den som melder, må være en ansatt som er i jobb i dag.")
    obj = objekter.hent_objekt(melding.get("objekttype", ""), str(melding.get("objekt_id", "")))
    if obj is None:
        raise ValueError("Fant ikke objektet. Velg det fra listen.")
    felt = melding.get("felt", "")
    if felt not in obj["felt"]:
        raise ValueError(f"Feltet '{felt}' finnes ikke på dette objektet.")
    beskrivelse = (melding.get("beskrivelse") or "").strip()
    if not beskrivelse:
        raise ValueError("Skriv kort hva som er feil.")
    rader = liste()
    nr = max((int(r["melding_id"].split("-")[1]) for r in rader), default=0) + 1
    rad = {
        "melding_id": f"FM-{nr:04d}", "meldt": naa, "melder_ansatt_id": melder["ansatt_id"], "melder_navn": melder["navn"],
        "oppgave": (melding.get("oppgave") or "").strip(), "objekttype": obj["type"], "objekt_id": obj["id"],
        "objekt_visning": obj["visning"], "felt": felt, "verdi_da": "" if obj["felt"][felt] is None else str(obj["felt"][felt]),
        "beskrivelse": beskrivelse, "forslag": (melding.get("forslag") or "").strip(), "kilde": obj["kilde"],
        "original": json.dumps(obj["felt"], ensure_ascii=False, default=str), "mottaker": MOTTAKER,
        "status": "ny", "status_dato": naa, "kommentar": "",
    }
    _skriv(rader + [rad])
    return rad["melding_id"]


def oppdater_status(melding_id: str, status: str, kommentar: str, naa: str | None = None) -> None:
    if status not in STATUSER:
        raise ValueError(f"Status må være en av: {', '.join(STATUSER)}")
    rader = liste()
    for r in rader:
        if r["melding_id"] == melding_id:
            r.update(status=status, kommentar=kommentar, status_dato=naa or _naa())
            _skriv(rader)
            return
    raise ValueError(f"Fant ikke {melding_id}")
