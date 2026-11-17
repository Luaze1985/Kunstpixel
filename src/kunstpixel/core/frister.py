"""«Mine frister» for ledelsessiden (spec datafinner-ledelse, B8). Reglene står i ledelse.py (B6/B7).

Bare lesing (mode=ro). Hver rolle ser sine frister:
- sykefravær uke 4/7: HR og bemanning og Avdelingsleder (navn, aldri fraværstype eller årsak)
- driftsmeldinger åpne over 14 dager: rollen som er mottaker (kategori og ID, aldri emnetekst)
- HMS-avvik åpne over 14 dager: Driftsansvarlig og Museumsdirektør
- rapportfrister: rollen som er eier i rapporteringskalenderen
- tilstandskontroll og retur av innlån: Samlingsforvalter og Kurator
Fristene regnes ut ved hvert kall og lagres aldri. Ingenting sendes.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

from src.kunstpixel.core import db, epostmaler, ledelse

_DATO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_APNE = ("APEN", "UNDER_BEHANDLING")
SYKEFRAVAER_ROLLER = {"HR og bemanning", "Avdelingsleder"}
AVVIK_ROLLER = {"Driftsansvarlig", "Museumsdirektør"}
SAMLING_ROLLER = {"Samlingsforvalter", "Kurator"}
# Direktøren ser også retur av innlån: Samlingsforvalter og Kurator har ingen rapporter og kan ikke velges i «Jeg er».
INNLAN_ROLLER = SAMLING_ROLLER | {"Museumsdirektør"}
_TITTEL_SYKE = {"sykefravaer_uke4": "Oppfølgingsplan (uke 4)", "sykefravaer_uke7": "Dialogmøte (uke 7)"}


def _idag() -> date:
    """Dagens dato. Egen funksjon så testene kan låse den."""
    return date.today()


def _mottaker_kode(rolle: str) -> str:
    """«Museumsdirektør» -> «museumsdirektor», «HR og bemanning» -> «hr_og_bemanning» (som i driftsmeldingene)."""
    t = rolle.lower().replace("ø", "o").replace("å", "a").replace("æ", "ae").replace("é", "e")
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def _pagaende_sykefravaer(con: Any, idag: date) -> list[dict[str, Any]]:
    """Sykemeldinger som pågår i dag. Typen hentes bare for å filtrere og går aldri videre."""
    return [dict(r) for r in con.execute(
        "SELECT f.ansatt_id, a.navn, f.fra, f.til FROM hr_fravaer f JOIN hr_ansatte a USING (ansatt_id) "
        "WHERE f.type = 'sykemelding' AND f.fra <= ? AND (f.til IS NULL OR f.til >= ?)",
        (idag.isoformat(), idag.isoformat()))]


def _pluss_maaneder(d: date, n: int) -> date:
    m = d.month - 1 + n
    aar, maaned = d.year + m // 12, m % 12 + 1
    dag = min(d.day, (date(aar + (maaned == 12), maaned % 12 + 1, 1) - timedelta(days=1)).day)
    return date(aar, maaned, dag)


def get_my_deadlines(rolle: str, dato: str) -> dict[str, Any]:
    """Fristene for en rolle, gruppert som Forfalt, I dag, Denne uka og Senere (innen 60 dager).

    Args:
        rolle: Rollenavnet, f.eks. 'Driftsansvarlig' eller 'HR og bemanning'.
        dato: Dagens dato i ISO-format 'YYYY-MM-DD'. Kan ikke være etter i dag.
    """
    if not isinstance(dato, str) or not _DATO.match(dato):
        raise ValueError("dato må være på formen YYYY-MM-DD")
    try:
        idag = date.fromisoformat(dato)
    except ValueError as exc:
        raise ValueError("dato er ikke en gyldig dato") from exc
    if idag > _idag():
        raise ValueError("Datoen er i fremtiden. Frister regnes fra i dag.")
    regler = ledelse.FRISTREGLER
    sak_grense = (idag - timedelta(days=regler["aapen_sak_dager"])).isoformat()
    sak_eldst = (idag - timedelta(days=regler["aapen_sak_maks_alder_dager"])).isoformat()
    kandidater: list[dict[str, Any]] = []

    with db.get_db_connection() as con:
        roller = {r[0] for r in con.execute("SELECT navn FROM roller")}
        if rolle not in roller:
            raise ValueError("Ukjent rolle. Bruk et rollenavn fra list_roles.")

        if rolle in SYKEFRAVAER_ROLLER:
            for r in _pagaende_sykefravaer(con, idag):
                for typ, frist in ledelse.sykefravaer_frister(r["fra"], r["til"], idag):
                    kandidater.append({"type": typ, "ref": r["ansatt_id"], "tittel": f"{_TITTEL_SYKE[typ]}: {r['navn']}",
                                       "frist_dato": frist.isoformat(), "kilde": "hr_fravaer og hr_ansatte"})

        kode = _mottaker_kode(rolle)
        for r in con.execute(
                "SELECT e.melding_id, e.dato, e.kategori FROM driftsmeldinger_epost e "
                "JOIN driftsmeldinger_tiltak t USING (melding_id) "
                f"WHERE t.status IN {_APNE} AND e.mottaker_rolle = ? AND e.dato <= ? AND e.dato >= ?",
                (kode, sak_grense, sak_eldst)):
            frist = date.fromisoformat(r["dato"]) + timedelta(days=regler["aapen_sak_dager"])
            kategori = r["kategori"].replace("_", " ")
            kandidater.append({"type": "driftsmelding", "ref": r["melding_id"],
                               "tittel": f"Driftsmelding åpen over {regler['aapen_sak_dager']} dager: {kategori}",
                               "frist_dato": frist.isoformat(), "kilde": "driftsmeldinger_epost og driftsmeldinger_tiltak"})
        eldre = con.execute(
            "SELECT COUNT(*) FROM driftsmeldinger_epost e JOIN driftsmeldinger_tiltak t USING (melding_id) "
            f"WHERE t.status IN {_APNE} AND e.mottaker_rolle = ? AND e.dato < ?", (kode, sak_eldst)).fetchone()[0]

        if rolle in AVVIK_ROLLER:
            for r in con.execute(
                    "SELECT avvik_id, dato, kategori FROM avvik_hms_drift WHERE status != 'LUKKET' AND dato <= ? AND dato >= ?",
                    (sak_grense, sak_eldst)):
                frist = date.fromisoformat(r["dato"]) + timedelta(days=regler["aapen_sak_dager"])
                kandidater.append({"type": "hms_avvik", "ref": r["avvik_id"],
                                   "tittel": f"HMS-avvik åpent over {regler['aapen_sak_dager']} dager: {r['kategori'].lower()}",
                                   "frist_dato": frist.isoformat(), "kilde": "avvik_hms_drift"})

        for r in con.execute("SELECT id, rapport, mottaker, maned FROM h5_rapporteringskalender WHERE eier = ?", (rolle,)):
            frist = ledelse.rapport_frist(r["maned"], idag)
            if frist:
                kandidater.append({"type": "rapport", "ref": r["id"], "tittel": f"{r['rapport']} til {r['mottaker']}",
                                   "frist_dato": frist.isoformat(), "kilde": "h5_rapporteringskalender"})

        if rolle in SAMLING_ROLLER:
            for r in con.execute("SELECT verk_id, MAX(inspeksjonsdato) AS sist, MAX(rapport_id) AS rapport_id "
                                 "FROM tilstandsrapporter GROUP BY verk_id"):
                frist = _pluss_maaneder(date.fromisoformat(r["sist"]), regler["tilstand_maaneder"])
                kandidater.append({"type": "tilstandskontroll", "ref": r["verk_id"],
                                   "tittel": f"Tilstandskontroll: {r['verk_id']}",
                                   "frist_dato": frist.isoformat(), "kilde": "tilstandsrapporter"})
        if rolle in INNLAN_ROLLER:
            for r in con.execute(
                    "SELECT i.innlan_id, i.tittel, i.eierinstitusjon, h.periode_slutt FROM utstillingsinnlan i "
                    "JOIN utstillinger_historikk h USING (utstilling_id) "
                    "WHERE i.status != 'Returnert' AND h.periode_slutt IS NOT NULL"):
                kandidater.append({"type": "innlan", "ref": r["innlan_id"],
                                   "tittel": f"Retur av innlån: {r['tittel']} ({r['eierinstitusjon']})",
                                   "frist_dato": r["periode_slutt"], "kilde": "utstillingsinnlan og utstillinger_historikk"})

    liste = ledelse.beregn_frister(kandidater, idag)
    for f in liste:
        f["epost"] = epostmaler.utkast_for_frist(f)  # B9: fast mal, fakta fra databasen. Ingenting sendes.
    antall = {g: sum(1 for f in liste if f["gruppe"] == g) for g in ("Forfalt", "I dag", "Denne uka", "Senere")}
    return {
        "dato": idag.isoformat(), "rolle": rolle, "hentet_kl": datetime.now().strftime("%H:%M"),
        "frister": liste, "antall": antall, "eldre_saker": eldre,
        "merknad": (f"Åpne saker eldre enn {regler['aapen_sak_maks_alder_dager']} dager står ikke i lista, "
                    "men telles i eldre_saker. Fristene regnes ut nå og lagres ikke."),
        "datakilde": "hr_fravaer, driftsmeldinger, avvik_hms_drift, h5_rapporteringskalender, tilstandsrapporter, "
                     "utstillingsinnlan",
    }
