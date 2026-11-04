"""Bemanning: hvilke kurs en stasjon krever, og (oppgave 08–09) hvem som er egnet.

Alt leses fra museum.db med mode=ro. Dataene er syntetiske.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from src.kunstpixel.core import db, llm


def krav(stasjon: str, db_path: Path | str | None = None) -> list[str]:
    """skill_code-ene stasjonen krever, sortert. Tom liste hvis stasjonen er ukjent."""
    with db.get_db_connection(db_path) as con:
        rader = con.execute(
            "SELECT skill_code FROM stasjon_krav WHERE stasjon = ? ORDER BY skill_code", (stasjon,)
        ).fetchall()
    return [r[0] for r in rader]


def _time_to_minutes(t_str: str) -> int:
    h, m = t_str.strip().split(":")[:2]
    return int(h) * 60 + int(m)


def vurder_ansatt(
    ansatt_id: str,
    dato: str,
    stasjon: str,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Vurderer en ansatts egnethet for en stasjon på en gitt dato ut fra dokumenterte fakta."""
    mangler: list[str] = []

    with db.get_db_connection(db_path) as con:
        ansatt = con.execute(
            "SELECT status FROM hr_ansatte WHERE ansatt_id = ?", (ansatt_id,)
        ).fetchone()
        if not ansatt:
            return {"ansatt_id": ansatt_id, "egnet": False, "mangler": ["UKJENT_PERSON"]}

        status = ansatt[0]
        if status == "Sluttet":
            mangler.append("SLUTTET")

        fravaer = con.execute(
            "SELECT 1 FROM hr_fravaer WHERE ansatt_id = ? AND ? BETWEEN fra AND til",
            (ansatt_id, dato),
        ).fetchone()
        if fravaer:
            mangler.append("FRAVAER")

        stasjon_krav = krav(stasjon, db_path=db_path)
        for skill_code in stasjon_krav:
            komp = con.execute(
                """SELECT 1 FROM org_ansatt_kompetanse 
                   WHERE ansatt_id = ? AND skill_code = ? 
                   AND status = 'gyldig' 
                   AND (gyldig_til IS NULL OR gyldig_til >= ?)""",
                (ansatt_id, skill_code, dato),
            ).fetchone()
            if not komp:
                mangler.append("MANGLER_KURS")
                break

    return {
        "ansatt_id": ansatt_id,
        "egnet": len(mangler) == 0,
        "mangler": mangler,
    }


def kandidater(
    dato: str,
    stasjon: str,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Henter alle kandidater og deres egnethet for en stasjon på en gitt dato."""
    krav_liste = krav(stasjon, db_path=db_path)

    with db.get_db_connection(db_path) as con:
        vakt = con.execute(
            "SELECT start, slutt FROM hr_vakter WHERE dato = ? AND stasjon = ? ORDER BY start LIMIT 1",
            (dato, stasjon),
        ).fetchone()
        start = vakt[0] if vakt else None
        slutt = vakt[1] if vakt else None

        ansatte = con.execute(
            "SELECT ansatt_id, stilling FROM hr_ansatte ORDER BY ansatt_id"
        ).fetchall()

    personer = []
    for aid, stilling in ansatte:
        v = vurder_ansatt(aid, dato, stasjon, db_path=db_path)
        personer.append({
            "ansatt_id": aid,
            "stilling": stilling,
            "egnet": v["egnet"],
            "mangler": v["mangler"],
        })

    return {
        "dato": dato,
        "stasjon": stasjon,
        "start": start,
        "slutt": slutt,
        "krav": krav_liste,
        "personer": personer,
    }


def vurder_forslag(
    dato: str,
    forslag: dict[str, str | None],
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Kontrollerer et bemanningsforslag for gitte stasjoner på en dato."""
    feil: list[dict[str, str]] = []
    mangel: list[str] = []

    with db.get_db_connection(db_path) as con:
        vakter_paa_dato = con.execute(
            "SELECT stasjon, start, slutt FROM hr_vakter WHERE dato = ?", (dato,)
        ).fetchall()
        stasjon_tid: dict[str, tuple[str, str]] = {r[0]: (r[1], r[2]) for r in vakter_paa_dato}

        alle_stasjoner = {r[0] for r in con.execute("SELECT DISTINCT stasjon FROM stasjon_krav").fetchall()}
        alle_stasjoner |= set(stasjon_tid.keys())

        hvile_grense_rad = con.execute(
            "SELECT verdi FROM arbeidstid_grenser WHERE navn = 'daglig_hvile_timer'"
        ).fetchone()
        min_hvile_timer = float(hvile_grense_rad[0]) if hvile_grense_rad else 11.0

        for stasjon, ansatt_id in forslag.items():
            if ansatt_id is None:
                mangel.append(stasjon)
                continue

            if stasjon not in alle_stasjoner and stasjon not in stasjon_tid:
                feil.append({"stasjon": stasjon, "ansatt_id": ansatt_id, "grunn": "UKJENT_STASJON"})
                continue

            ansatt = con.execute(
                "SELECT status FROM hr_ansatte WHERE ansatt_id = ?", (ansatt_id,)
            ).fetchone()
            if not ansatt:
                feil.append({"stasjon": stasjon, "ansatt_id": ansatt_id, "grunn": "UKJENT_PERSON"})
                continue

            if ansatt[0] == "Sluttet":
                feil.append({"stasjon": stasjon, "ansatt_id": ansatt_id, "grunn": "SLUTTET"})

            fravaer = con.execute(
                "SELECT 1 FROM hr_fravaer WHERE ansatt_id = ? AND ? BETWEEN fra AND til",
                (ansatt_id, dato),
            ).fetchone()
            if fravaer:
                feil.append({"stasjon": stasjon, "ansatt_id": ansatt_id, "grunn": "FRAVAER"})

            stasjon_krav = krav(stasjon, db_path=db_path)
            har_alle_kurs = True
            for skill_code in stasjon_krav:
                komp = con.execute(
                    """SELECT 1 FROM org_ansatt_kompetanse 
                       WHERE ansatt_id = ? AND skill_code = ? 
                       AND status = 'gyldig' 
                       AND (gyldig_til IS NULL OR gyldig_til >= ?)""",
                    (ansatt_id, skill_code, dato),
                ).fetchone()
                if not komp:
                    har_alle_kurs = False
                    break
            if not har_alle_kurs:
                feil.append({"stasjon": stasjon, "ansatt_id": ansatt_id, "grunn": "MANGLER_KURS"})

            # Sjekk dobbeltbooking mot annen vakt i samme forslag
            if stasjon in stasjon_tid:
                start1, slutt1 = stasjon_tid[stasjon]
                m_start1, m_slutt1 = _time_to_minutes(start1), _time_to_minutes(slutt1)
                for annen_stasjon, annen_ansatt in forslag.items():
                    if annen_stasjon != stasjon and annen_ansatt == ansatt_id and annen_stasjon in stasjon_tid:
                        start2, slutt2 = stasjon_tid[annen_stasjon]
                        m_start2, m_slutt2 = _time_to_minutes(start2), _time_to_minutes(slutt2)
                        if m_start1 < m_slutt2 and m_start2 < m_slutt1:
                            feil.append({"stasjon": stasjon, "ansatt_id": ansatt_id, "grunn": "DOBBELTBOOKET"})
                            break

            # Sjekk hviletid mot vakt kvelden før
            if stasjon in stasjon_tid:
                start_idag = stasjon_tid[stasjon][0]
                m_start_idag = _time_to_minutes(start_idag)
                gaarsdag = (date.fromisoformat(dato) - timedelta(days=1)).isoformat()
                forrige_vakter = con.execute(
                    "SELECT slutt FROM hr_vakter WHERE ansatt_id = ? AND dato = ?",
                    (ansatt_id, gaarsdag),
                ).fetchall()
                for (slutt_i_gaar,) in forrige_vakter:
                    m_slutt_i_gaar = _time_to_minutes(slutt_i_gaar)
                    hvile_timer = (m_start_idag + 24 * 60 - m_slutt_i_gaar) / 60.0
                    if hvile_timer < min_hvile_timer:
                        feil.append({"stasjon": stasjon, "ansatt_id": ansatt_id, "grunn": "HVILETID"})
                        break

    return {
        "godkjent": len(feil) == 0,
        "feil": feil,
        "mangel": mangel,
    }


SYSTEM_BEMANNING = (
    "Du foreslår bemanning for vaktene på en gitt dato ut fra anonymiserte ansatt-ID-er og kompetansekrav.\n"
    "Svar KUN med et gyldig JSON-objekt med nøkkelen \"forslag\" (et objekt fra stasjon til ansatt_id eller null)."
)


def _deterministisk_forslag(dato: str, db_path: Path | str | None = None) -> dict[str, str | None]:
    """Velger én gyldig ansatt per stasjon på gitt dato som består vurder_forslag."""
    with db.get_db_connection(db_path) as con:
        stasjoner = [
            r[0]
            for r in con.execute(
                "SELECT DISTINCT stasjon FROM hr_vakter WHERE dato = ? ORDER BY start, stasjon",
                (dato,),
            ).fetchall()
        ]
    forslag: dict[str, str | None] = {}
    brukt: set[str] = set()
    for stasjon in stasjoner:
        kand = kandidater(dato, stasjon, db_path=db_path)
        valgt: str | None = None
        for p in kand["personer"]:
            aid = p["ansatt_id"]
            if not p["egnet"] or aid in brukt:
                continue
            prøve = {**forslag, stasjon: aid}
            if vurder_forslag(dato, prøve, db_path=db_path)["godkjent"]:
                valgt = aid
                brukt.add(aid)
                break
        forslag[stasjon] = valgt
    return forslag


def foreslaa(
    dato: str,
    konfig: llm.LlmKonfig | None,
    begrenser: llm.Begrenser | None,
    apne: Any = urllib.request.urlopen,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Lager et deterministisk forslag og (hvis KI er på) et anonymisert AI-forslag som kontrolleres."""
    det_forslag = _deterministisk_forslag(dato, db_path=db_path)
    if konfig is None:
        return {
            "status": "ai_av",
            "deterministisk_forslag": det_forslag,
            "ai": None,
            "kontroll": vurder_forslag(dato, det_forslag, db_path=db_path),
            "krever_godkjenning": True,
        }
    if begrenser is not None and not begrenser.tillat():
        return {
            "status": "grense_naadd",
            "deterministisk_forslag": det_forslag,
            "ai": None,
            "kontroll": vurder_forslag(dato, det_forslag, db_path=db_path),
            "krever_godkjenning": True,
        }

    # Anonymisert grunnlag: kun stasjon, tider, krav og ansatt_id for egnede kandidater (aldri navn/fraværsårsak)
    grunnlag_stasjoner = []
    for stasjon in det_forslag:
        kand = kandidater(dato, stasjon, db_path=db_path)
        grunnlag_stasjoner.append({
            "stasjon": stasjon,
            "start": kand["start"],
            "slutt": kand["slutt"],
            "krav": kand["krav"],
            "egnede_ansatt_id": [p["ansatt_id"] for p in kand["personer"] if p["egnet"]],
        })
    bruker_tekst = json.dumps({"dato": dato, "stasjoner": grunnlag_stasjoner}, ensure_ascii=False)
    try:
        adresse, hoder, kropp = llm.bygg_foresporsel(konfig, bruker_tekst, SYSTEM_BEMANNING)
        data = llm._post_json(konfig, adresse, hoder, kropp, apne=apne)
        tekst = llm.les_svar(konfig.leverandor, data)
        parsed = json.loads(tekst)
        ai_forslag = parsed.get("forslag") if isinstance(parsed, dict) else None
        if not isinstance(ai_forslag, dict):
            raise llm.LlmFeil("leverandorfeil", "AI-svaret mangler 'forslag'-objekt")
    except (llm.LlmFeil, json.JSONDecodeError) as exc:
        return {
            "status": "ai_feil",
            "deterministisk_forslag": det_forslag,
            "ai": None,
            "kontroll": vurder_forslag(dato, det_forslag, db_path=db_path),
            "krever_godkjenning": True,
            "feil": str(exc),
        }

    kontroll = vurder_forslag(dato, ai_forslag, db_path=db_path)
    return {
        "status": "ok",
        "deterministisk_forslag": det_forslag,
        "ai": {"merke": "AI-forslag", "forslag": ai_forslag, "tekst": tekst},
        "kontroll": kontroll,
        "krever_godkjenning": True,
    }
