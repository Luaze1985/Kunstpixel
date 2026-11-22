"""Tallene til storskjerm-dashbordet (spec docs/specs/2026-11-19-storskjerm-dashbord.md, DECISIONS D1–D8).

Bare lesing. Setter sammen Datafinners egne beregninger («I dag», «Driften denne uka», «Mine frister» for
Museumsdirektør), så dashbordet og Datafinner viser de samme tallene. Ingen navn, fraværsårsak eller
e-postutkast går ut, fordi skjermen vises for andre. Innlånsfrister vises (U6 opphevet 2026-11-22).
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any

from src.kunstpixel.core import db, driftsoversikt, frister

ROLLE = "Museumsdirektør"
GRUPPER = ("Forfalt", "I dag", "Denne uka", "Senere")
SKJULTE_FRISTER: set[str] = set()  # Tom: Lars godkjente regelen for retur av innlån 2026-11-22 (U6 opphevet)
FELT_I_FRIST = ("type", "ref", "tittel", "frist_dato", "gruppe", "kilde")
UKER = 8

# Tidsserier og datokolonnen deres. Slutter en før i går, står den i «Dette vet vi ikke».
TIDSSERIER = [
    ("dagsbesok", "dato"), ("besok_tilfredshet", "dato"), ("anmeldelser", "dato"), ("kafe_varesalg", "dato"),
    ("driftsmeldinger_epost", "dato"), ("avvik_hms_drift", "dato"), ("hr_vakter", "dato"), ("hr_fravaer", "fra"),
]


def _idag() -> date:
    """Dagens dato. Egen funksjon så testene kan låse den."""
    return date.today()


def _tall(v: float | None) -> str:
    """Heltall med mellomrom som tusenskille (1 750), ellers én desimal med komma."""
    if v is None:
        return "–"
    if float(v).is_integer():
        return f"{int(v):,}".replace(",", " ")
    return f"{v:,.1f}".replace(",", " ").replace(".", ",")


def _flater(i_dag: dict[str, Any], uke: dict[str, Any], igaar: str) -> list[dict[str, Any]]:
    b = i_dag["besok"]
    ub = uke["besok"]
    hvilken = "forrige uke" if uke["viser_forrige_uke"] else "denne uka"
    saker = i_dag["driftsmeldinger"]["verdi"] + i_dag["hms_avvik"]["verdi"]
    tilfreds = uke["tilfredshet"]["verdi"]
    periode = f"{uke['fra']}–{min(uke['til'], igaar)}"
    return [
        {"id": "besok", "navn": "Besøk", "verdi": b["verdi"], "enhet": "besøk", "normalt": b["normalt"],
         "sammenligning": f"normalt for dagen: {_tall(b['normalt'])}" if b["normalt"] is not None else "ingen sammenligning",
         "status": b["status"], "gjelder": b["dato"], "kilde": b["kilde"]},
        {"id": "besok_uke", "navn": f"Besøk {hvilken}", "verdi": ub["verdi"], "enhet": "besøk", "normalt": ub["normalt"],
         "sammenligning": f"samme dager uka før: {_tall(ub['normalt'])}" if ub["normalt"] is not None else "ingen sammenligning",
         "status": ub["status"], "gjelder": periode, "kilde": ub["kilde"]},
        {"id": "saker", "navn": "Åpne saker", "verdi": saker, "enhet": "saker", "normalt": None,
         "sammenligning": (f"{i_dag['driftsmeldinger']['verdi']} meldinger (30 d) · "
                           f"{i_dag['hms_avvik']['verdi']} HMS-avvik (7 d) · "
                           f"{i_dag['driftsmeldinger_eldre']['verdi']} eldre"),
         "status": None, "gjelder": i_dag["dato"],
         "kilde": "driftsmeldinger_epost, driftsmeldinger_tiltak og avvik_hms_drift"},
        {"id": "tilfredshet", "navn": f"Tilfredshet {hvilken}", "verdi": tilfreds, "enhet": "av 5", "normalt": None,
         "sammenligning": "kilden dekker ikke perioden" if tilfreds is None else "snitt vektet etter antall svar",
         "status": "Ukjent" if tilfreds is None else None, "gjelder": periode,
         "kilde": uke["tilfredshet"]["kilde"]},
    ]


def _frister(dato: str) -> dict[str, Any]:
    alle = frister.get_my_deadlines(ROLLE, dato)["frister"]
    rader = [{k: f[k] for k in FELT_I_FRIST} for f in alle if f["type"] not in SKJULTE_FRISTER]
    return {"antall": {g: sum(r["gruppe"] == g for r in rader) for g in GRUPPER}, "rader": rader,
            "skjult": sum(f["type"] in SKJULTE_FRISTER for f in alle)}


def _besok_uker(con: Any, igaar: date) -> list[dict[str, Any]]:
    """De siste hele ukene (mandag–søndag) til og med i går. Uka som pågår står i flaten «Besøk denne uka»."""
    siste_sondag = igaar - timedelta(days=(igaar.weekday() + 1) % 7)
    siste_mandag = siste_sondag - timedelta(days=6)
    ut = []
    for n in range(UKER - 1, -1, -1):
        fra = siste_mandag - timedelta(weeks=n)
        til = fra + timedelta(days=6)
        aar, uke, _ = fra.isocalendar()
        sql = "SELECT sum(besok_totalt) FROM dagsbesok WHERE dato BETWEEN ? AND ?"
        i_aar = con.execute(sql, (fra.isoformat(), til.isoformat())).fetchone()[0]
        try:
            fjor_fra = date.fromisocalendar(aar - 1, uke, 1)
            i_fjor = con.execute(sql, (fjor_fra.isoformat(), (fjor_fra + (til - fra)).isoformat())).fetchone()[0]
        except ValueError:  # uke 53 finnes ikke i fjor
            i_fjor = None
        ut.append({"uke": uke, "fra": fra.isoformat(), "til": til.isoformat(), "i_aar": i_aar, "i_fjor": i_fjor})
    return ut


def _utstillinger(con: Any, aar: int) -> list[dict[str, Any]]:
    return [dict(r) for r in con.execute(
        "SELECT h.utstilling_id, h.tittel, h.sesong, o.netto_resultat_nok FROM utstillinger_historikk h "
        "JOIN utstilling_okonomi o USING (utstilling_id) WHERE h.aar = ? ORDER BY o.netto_resultat_nok DESC", (aar,))]


def _hull(con: Any, d: date) -> list[dict[str, Any]]:
    igaar = (d - timedelta(days=1)).isoformat()
    ut = []
    for tabell, kol in TIDSSERIER:
        slutt = con.execute(f"SELECT max({kol}) FROM {tabell}").fetchone()[0]
        if slutt and slutt < igaar:
            ut.append({"type": "slutter", "tabell": tabell, "slutter": slutt, "tekst": f"{tabell} slutter {slutt}.",
                       "kilde": tabell})
    iso = d.isoformat()
    aktive = sorted(r[0] for r in con.execute("SELECT tittel FROM utstillinger WHERE status = 'aktiv'"))
    historikk = sorted({r[0] for r in con.execute(
        "SELECT tittel FROM utstillinger_historikk WHERE periode_start <= ? AND periode_slutt >= ?", (iso, iso))})
    if aktive and historikk and not set(aktive) & set(historikk):
        kort = sorted({re.sub(r"\s*\(\d{4}\)$", "", h).split(":")[0] for h in historikk})
        ut.append({"type": "uenige", "tekst": (f"To tabeller er uenige om hva som vises nå. utstillinger: "
                                                f"{', '.join(aktive)}. utstillinger_historikk: {', '.join(kort)}."),
                   "kilde": "utstillinger og utstillinger_historikk"})
    return ut


def lag_storskjerm(dato: str) -> dict[str, Any]:
    """Alt dashbordet viser for `dato` (ISO 'YYYY-MM-DD', ikke etter i dag)."""
    d = date.fromisoformat(dato)
    if d > _idag():
        raise ValueError("Datoen er i fremtiden. Tall etter i dag vises ikke.")
    i_dag = driftsoversikt.get_today_overview(dato)
    uke = driftsoversikt.get_week_overview(dato)
    flater = _flater(i_dag, uke, (d - timedelta(days=1)).isoformat())
    fristdata = _frister(dato)
    with db.get_db_connection() as con:
        besok_uker = _besok_uker(con, d - timedelta(days=1))
        utstillinger = _utstillinger(con, d.year)
        hull = _hull(con, d)
    oppmerksomhet = sum(f["status"] in ("Følg med", "Over terskel") for f in flater) + fristdata["antall"]["Forfalt"]
    return {
        "dato": dato, "ukedag": i_dag["ukedag"], "hentet_kl": i_dag["hentet_kl"],
        "aapent_i_dag": i_dag["aapent_i_dag"], "oppmerksomhet": oppmerksomhet, "flater": flater,
        "besok_uker": besok_uker, "frister": fristdata, "utstillinger": utstillinger, "hull": hull,
    }
