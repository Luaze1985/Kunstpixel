"""Finn etterprøvbare HR-øvelser i den skrivebeskyttede museumsdatabasen."""

from __future__ import annotations

from datetime import date
from typing import Any

from src.kunstpixel.core import db, vaktrom


def resolve_employee(sok: str) -> dict[str, Any]:
    """Avklar om navn eller ansatt-ID peker på én person før personoppslag.

    Args:
        sok: Eksakt navn eller ansatt-ID. Et delvis navn gir kandidater, aldri automatisk valg.
    """
    tekst = str(sok or "").strip()
    if not tekst:
        raise ValueError("Oppgi navn eller ansatt-ID.")
    with db.get_db_connection() as con:
        rader = [dict(r) for r in con.execute(
            "SELECT ansatt_id, navn, stilling, avdeling, ansatt_til FROM hr_ansatte ORDER BY navn, ansatt_id"
        )]
    ident = tekst.upper()
    eksakt_id = [r for r in rader if r["ansatt_id"] == ident]
    eksakt_navn = [r for r in rader if r["navn"].casefold() == tekst.casefold()]
    kandidater = eksakt_id or eksakt_navn
    if not kandidater and not ident.startswith("KP-ANS-"):
        kandidater = [r for r in rader if tekst.casefold() in r["navn"].casefold()]
    kandidater = [{"ansatt_id": r["ansatt_id"], "navn": r["navn"],
                   "stilling": r["stilling"], "avdeling": r["avdeling"],
                   "aktiv": not r["ansatt_til"] or r["ansatt_til"] >= date.today().isoformat()}
                  for r in kandidater]
    antall = len(kandidater)
    return {"status": "ingen" if antall == 0 else "entydig" if antall == 1 else "tvetydig",
            "antall": antall, "kandidater": kandidater, "kilde": "hr_ansatte"}


def discover_hr_cases(sok: str | None = None, kategori: str | None = None, limit: int = 10) -> dict[str, Any]:
    """Foreslå HR-caser med kilde og neste lesende verktøykall.

    Args:
        sok: Valgfritt navn eller ansatt-ID; ingen person velges automatisk av rollevalget.
        kategori: tvetydig_navn, sluttet_ansatt, medarbeidersamtale eller personalmappe.
        limit: Maks antall caser, fra 1 til 50.
    """
    gyldige = {"tvetydig_navn", "sluttet_ansatt", "medarbeidersamtale", "personalmappe"}
    if kategori and kategori not in gyldige:
        raise ValueError("Ukjent HR-casekategori")
    maks = max(1, min(int(limit), 50))
    with db.get_db_connection() as con:
        alle = [dict(r) for r in con.execute(
            "SELECT ansatt_id, navn, ansatt_til FROM hr_ansatte ORDER BY navn, ansatt_id"
        )]
        samtaler = dict(con.execute(
            "SELECT ansatt_id, COUNT(*) FROM hr_medarbeidersamtaler GROUP BY ansatt_id"
        ).fetchall())
        mapper = dict(con.execute(
            "SELECT ansatt_id, COUNT(*) FROM hr_personalmapper GROUP BY ansatt_id"
        ).fetchall())
    if sok:
        valgt = {r["ansatt_id"] for r in vaktrom.find_employee(sok, maks_treff=None)}
        ansatte = [r for r in alle if r["ansatt_id"] in valgt]
    else:
        ansatte = alle
    grupper: dict[str, list[str]] = {}
    for r in ansatte:
        grupper.setdefault(r["navn"], []).append(r["ansatt_id"])
    caser: list[dict[str, Any]] = []
    if not kategori or kategori == "tvetydig_navn":
        for navn, ids in sorted(grupper.items()):
            if len(ids) > 1:
                caser.append({"kategori": "tvetydig_navn", "navn": navn, "ansatt_ider": ids,
                              "funn": f"{len(ids)} ansatte har samme navn. Avklar ansatt-ID før personoppslag.",
                              "kilde": "hr_ansatte", "neste_verktoy": {"navn": "resolve_employee", "args": {"sok": navn}}})
    for r in ansatte:
        ident, navn = r["ansatt_id"], r["navn"]
        base = {"navn": navn, "ansatt_ider": [ident]}
        if (not kategori or kategori == "sluttet_ansatt") and r["ansatt_til"] and r["ansatt_til"] < date.today().isoformat():
            caser.append({**base, "kategori": "sluttet_ansatt", "funn": "Ansettelsen er avsluttet.",
                          "kilde": "hr_ansatte", "neste_verktoy": {"navn": "find_employee", "args": {"sok": ident}}})
        if (not kategori or kategori == "medarbeidersamtale") and samtaler.get(ident, 0):
            caser.append({**base, "kategori": "medarbeidersamtale", "funn": f"{samtaler[ident]} registrerte samtaler.",
                          "kilde": "hr_medarbeidersamtaler", "neste_verktoy": {"navn": "get_employee_reviews", "args": {"ansatt_id": ident}}})
        if (not kategori or kategori == "personalmappe") and mapper.get(ident, 0):
            caser.append({**base, "kategori": "personalmappe", "funn": f"{mapper[ident]} registrerte saker.",
                          "kilde": "hr_personalmapper", "neste_verktoy": {"navn": "get_personnel_file", "args": {"ansatt_id": ident}}})
    if not sok and not kategori:
        grupperte = {k: [c for c in caser if c["kategori"] == k] for k in (
            "tvetydig_navn", "sluttet_ansatt", "medarbeidersamtale", "personalmappe"
        )}
        caser = [c for i in range(max(map(len, grupperte.values()))) for gruppe in grupperte.values()
                 for c in gruppe[i:i + 1]]
    return {"caser": caser[:maks], "antall_funnet": len(caser)}


def investigate_hr_case(kategori: str, ansatt_id: str) -> dict[str, Any]:
    """Hent faktagrunnlaget for én eksplisitt valgt HR-øvelse.

    Args:
        kategori: medarbeidersamtale eller personalmappe.
        ansatt_id: Eksakt ansatt-ID valgt etter casefunn; aldri utledet fra rollen.
    """
    ident = (ansatt_id or "").strip().upper()
    if not ident.startswith("KP-ANS-") or not vaktrom.find_employee(ident):
        raise ValueError("Velg en gyldig ansatt-ID")
    if kategori == "medarbeidersamtale":
        r = vaktrom.get_employee_reviews(ident)
        return {"ansatt_id": ident, "kategori": kategori, "kilde": "hr_medarbeidersamtaler",
                "antall": r["antall"], "fakta": r["samtaler"]}
    if kategori == "personalmappe":
        r = vaktrom.get_personnel_file(ident)
        return {"ansatt_id": ident, "kategori": kategori, "kilde": "hr_personalmapper",
                "antall": r["antall_saker"], "fakta": r["saker"]}
    raise ValueError("Ukjent HR-casekategori")
