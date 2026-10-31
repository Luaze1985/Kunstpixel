"""Drift og bunnlinje: besøk mot vakter, resultat per måned og utstillingenes økonomi.

Bare lesing (mode=ro). Alt er summert per dag, måned, avdeling eller utstilling. Ingen funksjon her
gir tall per ansatt, så ingen kan brukes til å måle enkeltpersoner (CASE-008).
"""

from __future__ import annotations

import re
from typing import Any

from src.kunstpixel.core import db

_DATO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MAANED = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _per_vakttime(besok: int, timer: float) -> float | None:
    return round(besok / timer, 2) if timer else None


def get_day_overview(dato: str) -> dict[str, Any]:
    """Besøk, billettinntekt og vakter for én dag, med besøkende per vakttime per avdeling.

    Args:
        dato: Dato i ISO-format 'YYYY-MM-DD'.
    """
    if not _DATO.match(dato or ""):
        raise ValueError("dato må være på formen YYYY-MM-DD")
    with db.get_db_connection() as con:
        dag = con.execute(
            "SELECT er_aapent, besok_totalt, inntekt_nok FROM dagsbesok WHERE dato = ?", (dato,)
        ).fetchone()
        if dag is None:
            return {"dato": dato, "funnet": False, "datakilde": "dagsbesok"}
        rader = con.execute(
            "SELECT avdeling, COUNT(*) AS vakter, ROUND(SUM(timer), 2) AS timer FROM hr_vakter "
            "WHERE dato = ? GROUP BY avdeling ORDER BY timer DESC",
            (dato,),
        ).fetchall()
    avdelinger = [
        {"avdeling": r["avdeling"], "vakter": r["vakter"], "timer": r["timer"],
         "besok_per_vakttime": _per_vakttime(dag["besok_totalt"], r["timer"])}
        for r in rader
    ]
    timer = round(sum(a["timer"] for a in avdelinger), 2)
    return {
        "dato": dato, "funnet": True, "er_aapent": bool(dag["er_aapent"]),
        "besok_totalt": dag["besok_totalt"], "billettinntekt_nok": dag["inntekt_nok"],
        "vakter": sum(a["vakter"] for a in avdelinger), "vakttimer": timer,
        "besok_per_vakttime": _per_vakttime(dag["besok_totalt"], timer),
        "avdelinger": avdelinger,
        "merknad": "Summert per avdeling. Ingen tall per ansatt.",
        "datakilde": "dagsbesok og hr_vakter",
    }


def get_period_result(maaned: str) -> dict[str, Any]:
    """Billettinntekt mot vaktkostnad for en måned. Resultatet er ikke et regnskap.

    Args:
        maaned: Måned i formatet 'YYYY-MM'.
    """
    if not _MAANED.match(maaned or ""):
        raise ValueError("maaned må være på formen YYYY-MM")
    aar, mnd = int(maaned[:4]), int(maaned[5:])
    with db.get_db_connection() as con:
        r = con.execute(
            "SELECT COALESCE(SUM(besok_totalt), 0) AS besok, COALESCE(SUM(inntekt_nok), 0) AS inntekt, "
            "SUM(er_aapent) AS dager FROM dagsbesok WHERE aar = ? AND maaned = ?",
            (aar, mnd),
        ).fetchone()
    kostnad = db.query_shift_cost(maaned)["kostnad_nok_totalt"]
    inntekt = r["inntekt"]
    return {
        "maaned": maaned, "dager_aapent": r["dager"], "besok_totalt": r["besok"],
        "billettinntekt_nok": inntekt, "vaktkostnad_nok": kostnad,
        "differanse_nok": round(inntekt - kostnad, 2),
        "i_pluss": inntekt - kostnad > 0,
        "merknad": "Bare billettinntekt minus vaktkostnad. Leie, innkjøp, tilskudd og kafé er ikke med, "
                   "så dette er ikke driftsresultatet.",
        "datakilde": "dagsbesok, hr_vakter og virke_tariff",
    }


def get_team_efficiency(maaned: str) -> dict[str, Any]:
    """Besøkende per vakttime per avdeling (team) for en måned. Aldri per person.

    Args:
        maaned: Måned i formatet 'YYYY-MM'.
    """
    if not _MAANED.match(maaned or ""):
        raise ValueError("maaned må være på formen YYYY-MM")
    aar, mnd = int(maaned[:4]), int(maaned[5:])
    with db.get_db_connection() as con:
        besok = con.execute(
            "SELECT COALESCE(SUM(besok_totalt), 0) FROM dagsbesok WHERE aar = ? AND maaned = ?", (aar, mnd)
        ).fetchone()[0]
        rader = con.execute(
            "SELECT avdeling, COUNT(*) AS vakter, ROUND(SUM(timer), 2) AS timer FROM hr_vakter "
            "WHERE substr(dato, 1, 7) = ? GROUP BY avdeling ORDER BY timer DESC",
            (maaned,),
        ).fetchall()
    return {
        "maaned": maaned, "besok_totalt": besok,
        "team": [{"avdeling": x["avdeling"], "vakter": x["vakter"], "timer": x["timer"],
                  "besok_per_vakttime": _per_vakttime(besok, x["timer"])} for x in rader],
        "merknad": "Per avdeling. Tallet sier noe om bemanningsbehov, ikke om hvor flinke folk er.",
        "datakilde": "dagsbesok og hr_vakter",
    }


def get_exhibition_ranking(aar: int, limit: int = 3) -> dict[str, Any]:
    """Utstillingene med best og dårligst netto resultat i et år.

    Args:
        aar: Året utstillingene åpnet.
        limit: Hvor mange som vises i hver ende (1-10).
    """
    limit = max(1, min(int(limit), 10))
    with db.get_db_connection() as con:
        rader = con.execute(
            "SELECT h.utstilling_id, h.tittel, o.billettinntekter_nok, o.faktisk_totalkostnad_nok, "
            "o.netto_resultat_nok FROM utstillinger_historikk h JOIN utstilling_okonomi o USING (utstilling_id) "
            "WHERE h.aar = ? ORDER BY o.netto_resultat_nok DESC",
            (int(aar),),
        ).fetchall()
    alle = [dict(r) for r in rader]
    return {
        "aar": int(aar), "antall": len(alle),
        "best": alle[:limit], "svakest": list(reversed(alle[-limit:])) if alle else [],
        "datakilde": "utstillinger_historikk og utstilling_okonomi",
    }
