"""«I dag» og «Driften denne uka» for ledelsessiden (spec datafinner-ledelse, B3/B4/D1).

Bare lesing (mode=ro). Alt er summert per dag, stasjon eller kategori. Ingen ansatt-ID eller navn går ut
(samme regel som bunnlinje.py, CASE-008). Driftsmeldinger vises bare som antall per kategori, uten emnetekst.

D1: de syntetiske dataene går til 2026-12-31. Tall for dagen i dag og senere vises derfor aldri som faktiske:
besøk regnes til og med i går, og en dato etter i dag avvises. «I dag» viser bare det som er planlagt
(åpent eller stengt, vakter per stasjon og arrangementer).
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

from src.kunstpixel.core import db, ledelse

_DATO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_UKEDAG = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
_APNE = ("APEN", "UNDER_BEHANDLING")


def _idag() -> date:
    """Dagens dato. Egen funksjon så testene kan låse den."""
    return date.today()


def _sjekk_dato(dato: str) -> date:
    if not isinstance(dato, str) or not _DATO.match(dato):
        raise ValueError("dato må være på formen YYYY-MM-DD")
    try:
        d = date.fromisoformat(dato)
    except ValueError as exc:
        raise ValueError("dato er ikke en gyldig dato") from exc
    if d > _idag():
        raise ValueError("Datoen er i fremtiden. Tall etter i dag vises ikke.")
    return d


def _besok_serie(con: Any, fra: date, til: date) -> dict[str, dict[str, Any]]:
    """dato -> {aapent, besok} for dager fra og med `fra` til og med `til`."""
    rader = con.execute(
        "SELECT dato, er_aapent, besok_totalt FROM dagsbesok WHERE dato BETWEEN ? AND ?",
        (fra.isoformat(), til.isoformat()),
    ).fetchall()
    return {r["dato"]: {"aapent": bool(r["er_aapent"]), "besok": r["besok_totalt"]} for r in rader}


def get_today_overview(dato: str) -> dict[str, Any]:
    """Dagens drift for ledelsen: åpent/stengt, besøk siste hele dag mot normalt, vakter per stasjon,
    arrangementer, åpne driftsmeldinger og nye HMS-avvik. Ingen tall per ansatt.

    Args:
        dato: Dagens dato i ISO-format 'YYYY-MM-DD'. Kan ikke være etter i dag.
    """
    d = _sjekk_dato(dato)
    iso = d.isoformat()
    with db.get_db_connection() as con:
        plan = con.execute("SELECT er_aapent FROM dagsbesok WHERE dato = ?", (iso,)).fetchone()
        # Besøk: siste hele åpne dag før i dag, mot samme ukedag de siste åpne ukene.
        serie = _besok_serie(con, d - timedelta(days=70), d - timedelta(days=1))
        aapne = sorted(k for k, v in serie.items() if v["aapent"])
        siste = aapne[-1] if aapne else None
        if siste:
            tall = {k: (v["besok"] if v["aapent"] else None) for k, v in serie.items()}
            vurdering = ledelse.vurder(serie[siste]["besok"], ledelse.normalt_for_ukedag(tall, siste), "besok")
            s = date.fromisoformat(siste)
            sammen = [(s - timedelta(weeks=n)).isoformat() for n in range(9)]
            besok_rader = [{"dato": k, "ukedag": _UKEDAG[date.fromisoformat(k).weekday()],
                            "aapent": serie[k]["aapent"], "besok": serie[k]["besok"]} for k in sammen if k in serie]
        else:
            vurdering, besok_rader = ledelse.vurder(None, None, "besok"), []
        besok = {"navn": "Besøk", "dato": siste, **vurdering,
                 "rader": ledelse.kutt_fremtid(besok_rader, iso), "kilde": "dagsbesok"}

        vakter = [dict(r) for r in con.execute(
            "SELECT stasjon, COUNT(*) AS vakter, ROUND(SUM(timer), 1) AS timer FROM hr_vakter "
            "WHERE dato = ? GROUP BY stasjon ORDER BY stasjon", (iso,))]
        arrangementer = [dict(r) for r in con.execute(
            "SELECT tittel, type, klokkeslett_start, klokkeslett_slutt, status FROM hendelser "
            "WHERE dato = ? ORDER BY klokkeslett_start", (iso,))]

        grense = (d - timedelta(days=30)).isoformat()
        # Bare antall per kategori, ingen emnetekst (Lars 2026-11-16, persondata).
        meldinger = [dict(r) for r in con.execute(
            "SELECT e.kategori, COUNT(*) AS antall, SUM(e.hastegrad = 'KRITISK') AS kritiske "
            "FROM driftsmeldinger_epost e JOIN driftsmeldinger_tiltak t USING (melding_id) "
            f"WHERE t.status IN {_APNE} AND e.dato >= ? AND e.dato < ? GROUP BY e.kategori "
            "ORDER BY kritiske DESC, antall DESC, e.kategori",
            (grense, iso))]
        eldre = [dict(r) for r in con.execute(
            "SELECT substr(e.dato, 1, 4) AS aar, COUNT(*) AS antall "
            "FROM driftsmeldinger_epost e JOIN driftsmeldinger_tiltak t USING (melding_id) "
            f"WHERE t.status IN {_APNE} AND e.dato < ? GROUP BY aar ORDER BY aar DESC", (grense,))]
        avvik = [dict(r) for r in con.execute(
            "SELECT dato, kategori, alvorlighetsgrad, status, berort_sal_id, beskrivelse FROM avvik_hms_drift "
            "WHERE dato >= ? AND dato < ? ORDER BY dato DESC", ((d - timedelta(days=7)).isoformat(), iso))]

    return {
        "dato": iso,
        "ukedag": _UKEDAG[d.weekday()],
        "aapent_i_dag": None if plan is None else bool(plan["er_aapent"]),
        "hentet_kl": datetime.now().strftime("%H:%M"),
        "besok": besok,
        "vakter": {"navn": "Vakter i dag", "verdi": sum(r["vakter"] for r in vakter), "rader": vakter,
                   "rapport": {"sporsmal_id": "vaktplan", "args": {"dato": iso}}, "kilde": "hr_vakter"},
        "arrangementer": {"navn": "Arrangementer i dag", "verdi": len(arrangementer), "rader": arrangementer,
                          "kilde": "hendelser"},
        "driftsmeldinger": {"navn": "Åpne driftsmeldinger siste 30 dager",
                            "verdi": sum(r["antall"] for r in meldinger), "rader": meldinger,
                            "kilde": "driftsmeldinger_epost og driftsmeldinger_tiltak"},
        "driftsmeldinger_eldre": {"navn": "Eldre åpne driftsmeldinger", "verdi": sum(r["antall"] for r in eldre),
                                  "rader": eldre, "kilde": "driftsmeldinger_epost og driftsmeldinger_tiltak"},
        "hms_avvik": {"navn": "HMS-avvik siste 7 dager", "verdi": len(avvik), "rader": avvik, "kilde": "avvik_hms_drift"},
        "merknad": "Besøk gjelder siste hele åpne dag. Summert per stasjon og kategori, ingen tall per ansatt.",
        "datakilde": "dagsbesok, hr_vakter, hendelser, driftsmeldinger og avvik_hms_drift",
    }


def _horisont(con: Any, tabell: str) -> str:
    # Tabellnavnet kommer fra koden, ikke fra brukeren.
    return con.execute(f"SELECT MAX(dato) FROM {tabell}").fetchone()[0] or ""


def get_week_overview(dato: str) -> dict[str, Any]:
    """Driften i uka (mandag–søndag) som `dato` ligger i: besøk per dag mot forrige uke og samme uke i fjor,
    tilfredshet, lave anmeldelser, kafésalg per besøkende, og driftsmeldinger og HMS-avvik åpnet og lukket.
    Dager fra og med i dag tas ikke med.

    Args:
        dato: En dag i uka, ISO-format 'YYYY-MM-DD'. Kan ikke være etter i dag.
    """
    d = _sjekk_dato(dato)
    idag = _idag()
    aar, uke, ukedag = d.isocalendar()
    mandag = d - timedelta(days=ukedag - 1)
    sondag = mandag + timedelta(days=6)
    siste_ferdige = min(sondag, idag - timedelta(days=1))
    try:
        fjor_mandag: date | None = date.fromisocalendar(aar - 1, uke, 1)
    except ValueError:  # uke 53 finnes ikke i fjor
        fjor_mandag = None

    with db.get_db_connection() as con:
        denne = _besok_serie(con, mandag, sondag)
        forrige = _besok_serie(con, mandag - timedelta(days=7), sondag - timedelta(days=7))
        fjor = _besok_serie(con, fjor_mandag, fjor_mandag + timedelta(days=6)) if fjor_mandag else {}

        dager, sum_na, sum_forrige, sum_fjor, ferdige = [], 0, 0, 0, 0
        for i in range(7):
            dag = mandag + timedelta(days=i)
            k = dag.isoformat()
            rad = {"dato": k, "ukedag": _UKEDAG[i], "aapent": (denne.get(k) or {}).get("aapent")}
            if dag >= idag:
                dager.append({**rad, "besok": None, "kommer": True})
                continue
            na = (denne.get(k) or {}).get("besok")
            f = (forrige.get((dag - timedelta(days=7)).isoformat()) or {}).get("besok")
            fj = (fjor.get((fjor_mandag + timedelta(days=i)).isoformat()) or {}).get("besok") if fjor_mandag else None
            dager.append({**rad, "besok": na, "forrige_uke": f, "i_fjor": fj, "kommer": False})
            ferdige += 1
            sum_na += na or 0
            sum_forrige += f or 0
            sum_fjor += fj or 0

        fra, til = mandag.isoformat(), siste_ferdige.isoformat()
        har_dager = ferdige > 0

        def dekket(tabell: str) -> bool:
            return har_dager and _horisont(con, tabell) >= til

        tilfredshet = None
        if dekket("besok_tilfredshet"):
            r = con.execute(
                "SELECT SUM(score_totalt * antall_svar) * 1.0 / SUM(antall_svar) AS snitt, SUM(antall_svar) AS svar "
                "FROM besok_tilfredshet WHERE dato BETWEEN ? AND ?", (fra, til)).fetchone()
            tilfredshet = round(r["snitt"], 2) if r["snitt"] is not None else None
        lave = None
        if dekket("anmeldelser"):
            lave = con.execute("SELECT COUNT(*) FROM anmeldelser WHERE stjerner <= 2 AND dato BETWEEN ? AND ?",
                               (fra, til)).fetchone()[0]
        kafe = None
        if dekket("kafe_varesalg") and sum_na:
            oms = con.execute("SELECT COALESCE(SUM(omsetning_nok), 0) FROM kafe_varesalg WHERE dato BETWEEN ? AND ?",
                              (fra, til)).fetchone()[0]
            kafe = round(oms / sum_na, 2)

        aapnet = con.execute("SELECT COUNT(*) FROM driftsmeldinger_epost WHERE dato BETWEEN ? AND ?", (fra, til)).fetchone()[0]
        lukket = con.execute("SELECT COUNT(*) FROM driftsmeldinger_tiltak WHERE lost_dato BETWEEN ? AND ?",
                             (fra, til)).fetchone()[0]
        avvik = con.execute("SELECT COUNT(*) FROM avvik_hms_drift WHERE dato BETWEEN ? AND ?", (fra, til)).fetchone()[0]

    if not har_dager:
        aapnet = lukket = avvik = None
    besok = ledelse.vurder(sum_na if har_dager else None, sum_forrige if har_dager else None, "besok")
    i_fjor = sum_fjor if har_dager and fjor_mandag else None
    return {
        "aar": aar, "uke": uke, "fra": mandag.isoformat(), "til": sondag.isoformat(),
        "ferdige_dager": ferdige,
        "hentet_kl": datetime.now().strftime("%H:%M"),
        "dager": dager,
        "besok": {"navn": "Besøk i uka", **besok, "forrige_uke": sum_forrige if har_dager else None, "i_fjor": i_fjor,
                  "i_fjor_pst": round((sum_na - i_fjor) / i_fjor * 100, 1) if i_fjor else None, "kilde": "dagsbesok"},
        "tilfredshet": {"navn": "Tilfredshet (1–5)", "verdi": tilfredshet,
                        "status": "Ukjent" if tilfredshet is None else None, "kilde": "besok_tilfredshet"},
        "lave_anmeldelser": {"navn": "Anmeldelser med 1–2 stjerner", "verdi": lave,
                             "status": "Ukjent" if lave is None else None, "kilde": "anmeldelser"},
        "kafe_per_besok": {"navn": "Kafésalg per besøkende (kr)", "verdi": kafe,
                           "status": "Ukjent" if kafe is None else None, "kilde": "kafe_varesalg og dagsbesok"},
        "driftsmeldinger": {"navn": "Driftsmeldinger", "aapnet": aapnet, "lukket": lukket,
                            "kilde": "driftsmeldinger_epost og driftsmeldinger_tiltak"},
        "hms_avvik": {"navn": "HMS-avvik", "aapnet": avvik, "kilde": "avvik_hms_drift"},
        "merknad": "Besøk sammenlignes med de samme ukedagene forrige uke. Mangler data betyr at kilden ikke dekker "
                   "hele perioden ennå.",
        "datakilde": "dagsbesok, besok_tilfredshet, anmeldelser, kafe_varesalg, driftsmeldinger og avvik_hms_drift",
    }
