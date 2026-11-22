"""Rollevisningene på storskjermen (DECISIONS SC14–SC20).

Seks lederroller får hver sine fire tall og sine flater. Alt regnes her i Python fra museum.db, så skjermen og
testene bruker samme tall. Bare lesing. Ingen navn går ut: sykefraværsfrister vises med ansatt-ID (D7).

Hvert tall har en sammenligning (samme periode i fjor, eller for 7 dager siden for beholdninger), en retning og
et statusord. Mangler kilden tall for perioden, er verdien None og statusen «Ukjent», aldri 0.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

from src.kunstpixel.core import db, frister

UKER = 8
MND = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
SYKE = "type IN ('egenmelding', 'sykemelding')"
GRUPPER = ("Forfalt", "I dag", "Denne uka", "Senere")

# Tabellnavn i vanlige ord, til «Vet ikke».
KILDENAVN = {
    "dagsbesok": "Besøk per dag", "besok_tilfredshet": "Tilfredshet", "anmeldelser": "Anmeldelser",
    "kafe_varesalg": "Kafésalg", "driftsmeldinger_epost": "Driftsmeldinger", "avvik_hms_drift": "HMS-avvik",
    "hr_vakter": "Vakter", "hr_fravaer": "Fravær", "hr_innleie": "Innleie", "driftsregnskap": "Driftsregnskapet",
}
FRISTKILDE = {"driftsmelding": "driftsmeldinger", "rapport": "h5_rapporteringskalender", "sykefravaer": "hr_fravaer",
              "innlan": "utstillingsinnlan", "tilstandskontroll": "tilstandsrapporter", "hms": "avvik_hms_drift"}
DATOKOLONNE = {"hr_fravaer": "fra", "hr_innleie": "periode_fra", "driftsregnskap": "maaned"}


def _idag() -> date:
    """Dagens dato. Egen funksjon så testene kan låse den."""
    return date.today()


# --- Felles regler ---

def _vurder(verdi: float | None, mot: float | None, bra: int, min_endring: float = 0) -> dict[str, Any]:
    """Retning og status. `bra` er +1 når mer er bra (besøk), -1 når mindre er bra (fravær), 0 når nøytralt.
    Normal: høyst 10 % verre. Følg med: 10–25 % verre. Over terskel: mer enn 25 % verre (agentens valg, SC16).
    `min_endring`: små tall (3 mot 2 timer) gir ikke alarm før forskjellen er minst så stor."""
    if verdi is not None and mot is not None and abs(verdi - mot) < min_endring:
        return {"status": "Normal", "endring_pst": round((verdi - mot) / abs(mot) * 100, 1) if mot else None,
                "retning": 0 if verdi == mot else (1 if verdi > mot else -1)}
    if verdi is None:
        return {"status": "Ukjent", "endring_pst": None, "retning": 0}
    if mot is None:
        return {"status": "Normal", "endring_pst": None, "retning": 0}
    if mot == 0:
        pst = None
        verre = 0.0 if verdi == 0 else (1.0 if bra < 0 else 0.0)
        retning = 0 if verdi == 0 else 1
    else:
        pst = round((verdi - mot) / abs(mot) * 100, 1)
        verre = max(0.0, -pst / 100 * bra) if bra else 0.0
        retning = 0 if abs(pst) < 1 else (1 if pst > 0 else -1)
    status = "Over terskel" if verre > 0.25 else "Følg med" if verre > 0.10 else "Normal"
    return {"status": status, "endring_pst": pst, "retning": retning}


def _tall(v: float | None, des: int = 0) -> str:
    if v is None:
        return "–"
    s = f"{v:,.{des}f}".replace(",", " ").replace(".", ",")
    return s


def _flis(fid: str, navn: str, verdi: float | None, enhet: str, mot: float | None, mot_tekst: str, bra: int,
          kilde: str, serie: list | None = None, etiketter: list | None = None, des: int = 0,
          min_endring: float = 0) -> dict[str, Any]:
    v = _vurder(verdi, mot, bra, min_endring)
    if verdi is None:
        sammenligning = "kilden dekker ikke perioden"
    elif mot is None:
        sammenligning = ""
    else:
        kort = _tall(mot / 1e6, 1) + " mill." if abs(mot) >= 1e6 else _tall(mot, des)
        sammenligning = f"{mot_tekst} {kort}"
    return {"id": fid, "navn": navn, "verdi": verdi, "enhet": enhet, "des": des, "sammenligning": sammenligning,
            "bra": bra, **v, "serie": serie, "serie_etiketter": etiketter, "kilde": kilde}


def _uker(d: date) -> list[tuple[date, date]]:
    """De siste hele ukene (mandag–søndag) før uka `d` ligger i, eldste først."""
    igaar = d - timedelta(days=1)
    sondag = igaar - timedelta(days=(igaar.weekday() + 1) % 7)
    return [(sondag - timedelta(days=6 + 7 * n), sondag - timedelta(days=7 * n)) for n in range(UKER - 1, -1, -1)]


def _fjor(fra: date, til: date) -> tuple[date, date] | None:
    aar, uke, _ = fra.isocalendar()
    try:
        f = date.fromisocalendar(aar - 1, uke, 1)
    except ValueError:
        return None
    return f, f + (til - fra)


def _horisont(con: Any, tabell: str) -> str:
    return con.execute(f"SELECT max({DATOKOLONNE.get(tabell, 'dato')}) FROM {tabell}").fetchone()[0] or ""


def _ukeserie(con: Any, d: date, tabell: str, f: Callable[[date, date], float | None]) -> dict[str, Any]:
    """Tallet per uke for de siste hele ukene, og samme uker i fjor. Uker etter kildens siste dato er None."""
    slutt = _horisont(con, tabell)
    uker = _uker(d)
    i_aar = [f(a, b) if b.isoformat() <= slutt else None for a, b in uker]
    fjor = []
    for a, b in uker:
        p = _fjor(a, b)
        fjor.append(f(*p) if p else None)
    return {"etiketter": [f"uke {a.isocalendar()[1]}" for a, _ in uker], "i_aar": i_aar, "i_fjor": fjor,
            "uker": uker}


def _sum(con: Any, sql: str, *args: Any) -> float:
    return con.execute(sql, args).fetchone()[0] or 0


def _maaneder(d: date) -> list[str]:
    """Hele måneder i år før måneden `d` ligger i ('2026-01' … '2026-10')."""
    return [f"{d.year}-{m:02d}" for m in range(1, d.month)]


def _resultat(con: Any, maaneder: list[str]) -> dict[str, float]:
    if not maaneder:
        return {"inn": 0, "ut": 0, "res": 0}
    plass = ",".join("?" * len(maaneder))
    inn = _sum(con, f"SELECT sum(belop_nok) FROM driftsregnskap WHERE konto < '4000' AND maaned IN ({plass})", *maaneder)
    ut = _sum(con, f"SELECT sum(belop_nok) FROM driftsregnskap WHERE konto >= '4000' AND maaned IN ({plass})", *maaneder)
    return {"inn": inn, "ut": ut, "res": inn - ut}


def _fjoraar(maaneder: list[str]) -> list[str]:
    return [f"{int(m[:4]) - 1}{m[4:]}" for m in maaneder]


# --- Byggeklosser for flatene ---

def _linje(pid: str, tittel: str, kilde: str, etiketter: list[str], serier: list[dict[str, Any]], enhet: str,
           des: int = 0, forklaring: str = "") -> dict[str, Any]:
    kolonner = ["Periode"] + [s["navn"] for s in serier]
    rader = [[e] + [_tall(s["verdier"][i], des) for s in serier] for i, e in enumerate(etiketter)]
    return {"id": pid, "type": "linje", "tittel": tittel, "kilde": kilde, "forklaring": forklaring,
            "data": {"etiketter": etiketter, "serier": serier, "enhet": enhet, "des": des},
            "underlag": {"kolonner": kolonner, "rader": rader, "tall": list(range(1, len(kolonner)))}}


def _stolper(pid: str, tittel: str, kilde: str, rader: list[tuple[str, float | None]], enhet: str, des: int = 0,
             ekstra: dict[str, Any] | None = None) -> dict[str, Any]:
    ekstra = ekstra or {"kolonner": [], "rader": [[] for _ in rader]}
    return {"id": pid, "type": "stolper", "tittel": tittel, "kilde": kilde, "forklaring": "",
            "data": {"rader": [{"navn": n, "verdi": v} for n, v in rader], "enhet": enhet, "des": des},
            "underlag": {"kolonner": ["Navn", tittel.split(":")[0]] + ekstra["kolonner"],
                         "rader": [[n, _tall(v, des) + (" " + enhet if enhet and v is not None else "")] + e
                                   for (n, v), e in zip(rader, ekstra["rader"])], "tall": [1]}}


def _anonym(r: dict[str, Any]) -> dict[str, Any]:
    """Sykefraværsfrister har navnet i tittelen. Skjermen viser bare hva og ansatt-ID (D7)."""
    tittel = r["tittel"]
    if r["type"].startswith("sykefravaer"):
        tittel = tittel.split(":")[0].replace("(uke", "sykefravær (uke")
    return {"type": r["type"], "ref": r["ref"], "tittel": tittel, "frist_dato": r["frist_dato"], "gruppe": r["gruppe"],
            "rolle": r.get("rolle", "")}


def _fristdata(roller: list[str], dato: str) -> dict[str, Any]:
    sett, rader = set(), []
    for rolle in roller:
        for f in frister.get_my_deadlines(rolle, dato)["frister"]:
            if f["ref"] + f["type"] in sett:
                continue
            sett.add(f["ref"] + f["type"])
            rader.append(_anonym({**f, "rolle": rolle}))
    rader.sort(key=lambda r: (GRUPPER.index(r["gruppe"]), r["frist_dato"]))
    return {"antall": {g: sum(r["gruppe"] == g for r in rader) for g in GRUPPER}, "rader": rader}


def _frister_flate(pid: str, roller: list[str], dato: str, d: date) -> dict[str, Any]:
    data = _fristdata(roller, dato)
    vis_rolle = len(roller) > 1
    kolonner = ["Frist", "Status", "Sak", "Referanse"] + (["Rolle"] if vis_rolle else [])
    rader = []
    for r in data["rader"]:
        om = (date.fromisoformat(r["frist_dato"]) - d).days
        st = f"{-om} dager over" if om < 0 else "i dag" if om == 0 else f"om {om} dager"
        rader.append([r["frist_dato"][8:10] + "." + r["frist_dato"][5:7], st, r["tittel"], r["ref"]]
                     + ([r["rolle"]] if vis_rolle else []))
    typer = sorted({FRISTKILDE.get(r["type"].split("_")[0], r["type"]) for r in data["rader"]})
    return {"id": pid, "type": "frister", "tittel": "Frister", "kilde": ", ".join(typer) or "fristene for rollen",
            "forklaring": "",
            "data": data, "underlag": {"kolonner": kolonner, "rader": rader, "tall": []}}


def _vet_ikke(con: Any, d: date, tabeller: list[str], ekstra: list[str] | None = None) -> dict[str, Any]:
    igaar = (d - timedelta(days=1)).isoformat()
    linjer, underlag = [], []
    for t in tabeller:
        slutt = _horisont(con, t)
        if t == "driftsregnskap":
            continue
        if slutt and slutt < igaar:
            dager = (d - date.fromisoformat(slutt[:10])).days
            linjer.append(f"{KILDENAVN[t]}: tall slutter {slutt[8:10]}.{slutt[5:7]}, {dager} dager uten tall")
            underlag.append([KILDENAVN[t], slutt[8:10] + "." + slutt[5:7], str(dager)])
    linjer += ekstra or []
    if not linjer:
        linjer = ["Alle kildene for denne rollen har tall til og med i går."]
    return {"id": "vet_ikke", "type": "liste", "tittel": "Dette vet vi ikke", "kilde": "kildene for rollen",
            "forklaring": "Mangler en kilde tall, står tallet som Ukjent, ikke 0.",
            "data": {"rader": linjer}, "underlag": {"kolonner": ["Kilde", "Siste dato", "Dager uten tall"],
                                                    "rader": underlag, "tall": [2]}}


# --- Tall som brukes av flere roller ---

def _besok(con: Any, d: date) -> dict[str, Any]:
    return _ukeserie(con, d, "dagsbesok", lambda a, b: _sum(
        con, "SELECT sum(besok_totalt) FROM dagsbesok WHERE dato BETWEEN ? AND ?", a.isoformat(), b.isoformat()))


def _fravaer(con: Any, d: date) -> dict[str, Any]:
    def f(a: date, b: date) -> float:
        return round(_sum(con, f"""SELECT sum(julianday(min(til, ?)) - julianday(max(fra, ?)) + 1) FROM hr_fravaer
                                   WHERE {SYKE} AND fra <= ? AND til >= ?""",
                          b.isoformat(), a.isoformat(), b.isoformat(), a.isoformat()))
    return _ukeserie(con, d, "hr_fravaer", f)


def _forfalte(roller: list[str], dato: str) -> int:
    return _fristdata(roller, dato)["antall"]["Forfalt"]


LEDERROLLER = ["Museumsdirektør", "Driftsansvarlig", "HR og bemanning", "Økonomi og innkjøp", "Kafeansvarlig",
               "Kommunikasjon", "Samlingsforvalter", "Kurator"]


def _beholdning(con: Any, d: date, fid: str, navn: str, f: Callable[[date], float], kilde: str) -> dict[str, Any]:
    """Et tall som teller det som står åpent på en dag (meldinger uten løst tiltak). Slutter kilden før i går,
    gjelder tallet kildens siste dag, og navnet sier det. Ellers ser et hull ut som «ingen endring» (spec-anti-mål)."""
    slutt = _horisont(con, "driftsmeldinger_epost")
    igaar = d - timedelta(days=1)
    paa = min(igaar, date.fromisoformat(slutt)) if slutt else igaar
    tekst = navn if paa >= igaar else f"{navn} per {paa.strftime('%d.%m')}"
    uker = _uker(d)
    serie = [f(b) if b <= paa else None for _, b in uker]
    return _flis(fid, tekst, f(paa), "", f(paa - timedelta(days=7)), "uka før", -1, kilde, serie,
                 [f"uke {a.isocalendar()[1]}" for a, _ in uker])


def _uke_flis(fid: str, navn: str, s: dict[str, Any], enhet: str, bra: int, kilde: str, des: int = 0,
              min_endring: float = 0) -> dict[str, Any]:
    """Siste hele uke med tall. Slutter kilden før siste uke, vises uka før, og navnet sier hvilken uke det er."""
    i = max((n for n, v in enumerate(s["i_aar"]) if v is not None), default=len(s["i_aar"]) - 1)
    return _flis(fid, f"{navn} {s['etiketter'][i]}", s["i_aar"][i], enhet, s["i_fjor"][i], "i fjor", bra,
                 kilde, s["i_aar"], s["etiketter"], des, min_endring)


def _maaned_serie(con: Any, d: date, felt: str) -> tuple[list[str], list[float], list[float]]:
    mnd = _maaneder(d)
    et = [MND[int(m[5:]) - 1] for m in mnd]
    i_aar = [_resultat(con, [m])[felt] for m in mnd]
    fjor = [_resultat(con, [m])[felt] for m in _fjoraar(mnd)]
    return et, i_aar, fjor


# --- Rollene ---

def _direktor(con: Any, d: date, dato: str) -> dict[str, Any]:
    b = _besok(con, d)
    fr = _fravaer(con, d)
    mnd = _maaneder(d)
    r, rf = _resultat(con, mnd), _resultat(con, _fjoraar(mnd))
    et, res, res_f = _maaned_serie(con, d, "res")
    forfalt, forfalt_7 = _forfalte(LEDERROLLER, dato), _forfalte(LEDERROLLER, (d - timedelta(days=7)).isoformat())
    hittil = f"hittil i år (jan–{MND[d.month - 2]})" if mnd else "hittil i år"
    utst = _utstillinger(con, d.year)
    return {
        "id": "direktor", "navn": "Direktør", "kort": "Direktør",
        "fliser": [
            _uke_flis("besok_uke", "Besøk", b, "besøk", +1, "dagsbesok"),
            _flis("resultat", f"Resultat {hittil}", round(r["res"]), "kr", round(rf["res"]), "i fjor", +1,
                  "driftsregnskap", res[-UKER:], et[-UKER:]),
            _uke_flis("fravaer_uke", "Sykefraværsdager", fr, "dager", -1, "hr_fravaer"),
            _flis("forfalt", "Forfalte frister, alle ledere", forfalt, "", forfalt_7, "for en uke siden", -1,
                  "frister for alle lederroller"),
        ],
        "flater": [
            _linje("besok", "Besøk per uke", "dagsbesok", b["etiketter"],
                   [{"navn": "I år", "verdier": b["i_aar"], "hoved": True},
                    {"navn": "I fjor", "verdier": b["i_fjor"]}], "besøk", forklaring="Hele uker, uten uka som pågår."),
            _linje("resultat_maaned", "Resultat per måned", "driftsregnskap", et,
                   [{"navn": "I år", "verdier": res, "hoved": True}, {"navn": "I fjor", "verdier": res_f}], "kr",
                   forklaring="Inntekter minus kostnader. Bare hele måneder."),
            _frister_flate("frister", LEDERROLLER, dato, d),
            utst,
            _vet_ikke(con, d, ["dagsbesok", "hr_fravaer", "driftsmeldinger_epost", "avvik_hms_drift"],
                      _uenige_utstillinger(con, d)),
        ],
        "forslag": ["Hva krever oppmerksomhet i dag?", "Hvordan går økonomien i år mot i fjor?",
                    "Hvilke frister er forfalt, og hvem eier dem?", "Hvordan gikk utstillingene i år?"],
    }


def _drift(con: Any, d: date, dato: str) -> dict[str, Any]:
    def aapne(paa: date) -> float:
        return _sum(con, """SELECT count(*) FROM driftsmeldinger_epost e LEFT JOIN driftsmeldinger_tiltak t USING (melding_id)
                            WHERE e.dato <= ? AND (t.lost_dato IS NULL OR t.lost_dato > ?)""",
                    paa.isoformat(), paa.isoformat())
    nye = _ukeserie(con, d, "driftsmeldinger_epost", lambda a, b: _sum(
        con, "SELECT count(*) FROM driftsmeldinger_epost WHERE dato BETWEEN ? AND ?", a.isoformat(), b.isoformat()))
    lost = _ukeserie(con, d, "driftsmeldinger_epost", lambda a, b: _sum(
        con, "SELECT count(*) FROM driftsmeldinger_tiltak WHERE lost_dato BETWEEN ? AND ?", a.isoformat(), b.isoformat()))
    hms = _ukeserie(con, d, "avvik_hms_drift", lambda a, b: _sum(
        con, "SELECT count(*) FROM avvik_hms_drift WHERE dato BETWEEN ? AND ?", a.isoformat(), b.isoformat()))
    svartid = _ukeserie(con, d, "driftsmeldinger_epost", lambda a, b: con.execute(
        "SELECT round(avg(svartid_timer), 1) FROM driftsmeldinger_tiltak WHERE lost_dato BETWEEN ? AND ?",
        (a.isoformat(), b.isoformat())).fetchone()[0])
    per_kat = con.execute("""SELECT e.kategori, count(*) FROM driftsmeldinger_epost e
                             LEFT JOIN driftsmeldinger_tiltak t USING (melding_id)
                             WHERE e.dato <= ? AND (t.lost_dato IS NULL OR t.lost_dato > ?)
                             GROUP BY 1 ORDER BY 2 DESC""", (dato, dato)).fetchall()
    return {
        "id": "drift", "navn": "Drift og HMS", "kort": "Drift",
        "fliser": [
            _beholdning(con, d, "aapne", "Åpne driftsmeldinger", aapne, "driftsmeldinger_epost og driftsmeldinger_tiltak"),
            _uke_flis("nye_uke", "Nye meldinger", nye, "", -1, "driftsmeldinger_epost", min_endring=3),
            _uke_flis("hms_uke", "HMS-avvik", hms, "", -1, "avvik_hms_drift", min_endring=2),
            _uke_flis("svartid_uke", "Svartid", svartid, "timer", -1,
                      "driftsmeldinger_tiltak", des=1),
        ],
        "flater": [
            _frister_flate("frister", ["Driftsansvarlig"], dato, d),
            _stolper("kategorier", "Åpne meldinger per kategori", "driftsmeldinger_epost og driftsmeldinger_tiltak",
                     [(k.replace("_og_", " og ").replace("_", " ").capitalize(), n) for k, n in per_kat], ""),
            _linje("meldinger_uke", "Meldinger per uke", "driftsmeldinger_epost og driftsmeldinger_tiltak",
                   nye["etiketter"], [{"navn": "Nye", "verdier": nye["i_aar"], "hoved": True},
                                      {"navn": "Løst", "verdier": lost["i_aar"]}], "meldinger"),
            _vet_ikke(con, d, ["driftsmeldinger_epost", "avvik_hms_drift"]),
        ],
        "forslag": ["Hvilke driftsmeldinger har vært åpne lengst?", "Hvor kommer HMS-avvikene fra i år?",
                    "Hvilken kategori har lengst svartid?", "Hvordan var driften forrige uke?"],
    }


def _hr(con: Any, d: date, dato: str) -> dict[str, Any]:
    fr = _fravaer(con, d)
    timer = _ukeserie(con, d, "hr_vakter", lambda a, b: round(_sum(
        con, "SELECT sum(timer) FROM hr_vakter WHERE dato BETWEEN ? AND ?", a.isoformat(), b.isoformat())))
    over = _ukeserie(con, d, "hr_vakter", lambda a, b: round(_sum(
        con, "SELECT sum(overtid_timer) FROM hr_vakter WHERE dato BETWEEN ? AND ?", a.isoformat(), b.isoformat()), 1))
    start, igaar = f"{d.year}-01-01", (d - timedelta(days=1)).isoformat()
    fstart, figaar = f"{d.year - 1}-01-01", f"{d.year - 1}{igaar[4:]}"
    innleie = round(_sum(con, "SELECT sum(totalbelop_nok) FROM hr_innleie WHERE periode_fra BETWEEN ? AND ?", start, igaar))
    innleie_f = round(_sum(con, "SELECT sum(totalbelop_nok) FROM hr_innleie WHERE periode_fra BETWEEN ? AND ?",
                           fstart, figaar))
    avd = con.execute(f"""WITH n AS (SELECT avdeling, count(*) AS ansatte FROM hr_ansatte WHERE status <> 'Sluttet' GROUP BY 1),
        f AS (SELECT a.avdeling, sum(julianday(min(f.til, ?)) - julianday(max(f.fra, ?)) + 1) AS dager
              FROM hr_fravaer f JOIN hr_ansatte a USING (ansatt_id)
              WHERE a.status <> 'Sluttet' AND f.{SYKE.replace('type', 'type', 1)} AND f.fra <= ? AND f.til >= ? GROUP BY 1)
        SELECT n.avdeling, n.ansatte, round(coalesce(f.dager, 0)), round(coalesce(f.dager, 0) * 1.0 / n.ansatte, 1)
        FROM n LEFT JOIN f USING (avdeling) ORDER BY 4 DESC""", (igaar, start, igaar, start)).fetchall()
    ot = con.execute("""SELECT avdeling, round(sum(overtid_timer)), round(sum(timer)) FROM hr_vakter
                        WHERE dato BETWEEN ? AND ? GROUP BY 1 ORDER BY 2 DESC""", (start, igaar)).fetchall()
    kat = con.execute("""SELECT kategori, round(sum(totalbelop_nok)), count(*) FROM hr_innleie
                         WHERE periode_fra BETWEEN ? AND ? GROUP BY 1 ORDER BY 2 DESC""", (start, igaar)).fetchall()
    return {
        "id": "hr", "navn": "HR og bemanning", "kort": "HR",
        "fliser": [
            _uke_flis("fravaer_uke", "Sykefraværsdager", fr, "dager", -1, "hr_fravaer"),
            _uke_flis("overtid_uke", "Overtid", over, "timer", -1, "hr_vakter", des=1, min_endring=5),
            _uke_flis("vakttimer_uke", "Vakttimer", timer, "timer", 0, "hr_vakter"),
            _flis("innleie", "Innleie hittil i år", innleie, "kr", innleie_f, "i fjor", -1, "hr_innleie"),
        ],
        "flater": [
            _frister_flate("frister", ["HR og bemanning", "Avdelingsleder"], dato, d),
            _linje("fravaer", "Sykefravær per uke", "hr_fravaer", fr["etiketter"],
                   [{"navn": "I år", "verdier": fr["i_aar"], "hoved": True}, {"navn": "I fjor", "verdier": fr["i_fjor"]}],
                   "dager", forklaring="Egenmelding og sykemelding, kalenderdager. Ingen fraværsårsaker."),
            _stolper("fravaer_avd", "Fravær per ansatt i år", "hr_fravaer og hr_ansatte",
                     [(a, per) for a, _, _, per in avd], "dager", 1,
                     {"kolonner": ["Ansatte", "Fraværsdager"], "rader": [[str(n), _tall(dg)] for _, n, dg, _ in avd]}),
            _stolper("overtid_avd", "Overtid per avdeling i år", "hr_vakter",
                     [(a, o) for a, o, _ in ot], "timer", 0,
                     {"kolonner": ["Vakttimer"], "rader": [[_tall(t)] for _, _, t in ot]}),
            _stolper("innleie_kat", "Innleie per kategori i år", "hr_innleie", [(k, b) for k, b, _ in kat], "kr", 0,
                     {"kolonner": ["Oppdrag"], "rader": [[str(n)] for _, _, n in kat]}),
        ],
        "forslag": ["Hvilke avdelinger har mest sykefravær i år?", "Hvor mye overtid har vi hatt i høst?",
                    "Hvor bruker vi mest på innleie?", "Henger overtid og fravær sammen per avdeling?"],
    }


def _okonomi(con: Any, d: date, dato: str) -> dict[str, Any]:
    mnd = _maaneder(d)
    r, rf = _resultat(con, mnd), _resultat(con, _fjoraar(mnd))
    et, res, res_f = _maaned_serie(con, d, "res")
    _, inn, _ = _maaned_serie(con, d, "inn")
    _, ut, _ = _maaned_serie(con, d, "ut")
    hittil = f"hittil i år (jan–{MND[d.month - 2]})" if mnd else "hittil i år"
    plass = ",".join("?" * len(mnd)) or "''"
    billett = _sum(con, f"SELECT sum(belop_nok) FROM driftsregnskap WHERE konto = '3000' AND maaned IN ({plass})", *mnd)
    billett_f = _sum(con, f"SELECT sum(belop_nok) FROM driftsregnskap WHERE konto = '3000' AND maaned IN ({plass})",
                     *_fjoraar(mnd))
    siste = f"{d.year}-{d.month - 1:02d}-31" if mnd else f"{d.year}-01-01"
    besok = _sum(con, "SELECT sum(besok_totalt) FROM dagsbesok WHERE dato BETWEEN ? AND ?", f"{d.year}-01-01",
                 min(siste, (d - timedelta(days=1)).isoformat()))
    besok_f = _sum(con, "SELECT sum(besok_totalt) FROM dagsbesok WHERE dato BETWEEN ? AND ?", f"{d.year - 1}-01-01",
                   f"{d.year - 1}{min(siste, (d - timedelta(days=1)).isoformat())[4:]}")
    konto = con.execute(f"""SELECT kontonavn, round(sum(belop_nok)) FROM driftsregnskap
                            WHERE konto >= '4000' AND maaned IN ({plass}) GROUP BY konto ORDER BY 2 DESC""",
                        mnd).fetchall()
    return {
        "id": "okonomi", "navn": "Økonomi", "kort": "Økonomi",
        "fliser": [
            _flis("inntekter", f"Inntekter {hittil}", round(r["inn"]), "kr", round(rf["inn"]), "i fjor", +1,
                  "driftsregnskap", inn[-UKER:], et[-UKER:]),
            _flis("kostnader", f"Kostnader {hittil}", round(r["ut"]), "kr", round(rf["ut"]), "i fjor", -1,
                  "driftsregnskap", ut[-UKER:], et[-UKER:]),
            _flis("resultat", f"Resultat {hittil}", round(r["res"]), "kr", round(rf["res"]), "i fjor", +1,
                  "driftsregnskap", res[-UKER:], et[-UKER:]),
            _flis("billett_per_besok", "Billettinntekt per besøk", round(billett / besok, 1) if besok else None, "kr",
                  round(billett_f / besok_f, 1) if besok_f else None, "i fjor", +1,
                  "driftsregnskap og dagsbesok", des=1),
        ],
        "flater": [
            _linje("resultat_maaned", "Resultat per måned", "driftsregnskap", et,
                   [{"navn": "I år", "verdier": res, "hoved": True}, {"navn": "I fjor", "verdier": res_f}], "kr",
                   forklaring="Inntekter minus kostnader. Bare hele måneder."),
            _stolper("kostnader_konto", f"Kostnader per konto {hittil}", "driftsregnskap", konto, "kr"),
            _utstillinger(con, d.year),
        ],
        "forslag": ["Hvorfor er resultatet annerledes enn i fjor?", "Hvilke kostnader har økt mest i år?",
                    "Hvordan utvikler billettinntekten seg?", "Hvilken utstilling ga best resultat?"],
    }


def _publikum(con: Any, d: date, dato: str) -> dict[str, Any]:
    b = _besok(con, d)

    def tilfreds(a: date, c: date) -> float | None:
        v = con.execute("SELECT sum(score_totalt * antall_svar) * 1.0 / sum(antall_svar) FROM besok_tilfredshet "
                        "WHERE dato BETWEEN ? AND ?", (a.isoformat(), c.isoformat())).fetchone()[0]
        return round(v, 2) if v is not None else None
    tf = _ukeserie(con, d, "besok_tilfredshet", tilfreds)

    def kafe(a: date, c: date) -> float | None:
        bes = _sum(con, "SELECT sum(besok_totalt) FROM dagsbesok WHERE dato BETWEEN ? AND ?", a.isoformat(), c.isoformat())
        oms = _sum(con, "SELECT sum(omsetning_nok) FROM kafe_varesalg WHERE dato BETWEEN ? AND ?", a.isoformat(), c.isoformat())
        return round(oms / bes, 1) if bes else None
    kf = _ukeserie(con, d, "kafe_varesalg", kafe)
    lave = _ukeserie(con, d, "anmeldelser", lambda a, c: _sum(
        con, "SELECT count(*) FROM anmeldelser WHERE stjerner <= 2 AND dato BETWEEN ? AND ?", a.isoformat(), c.isoformat()))
    stjerner = con.execute("SELECT stjerner, count(*) FROM anmeldelser WHERE dato BETWEEN ? AND ? GROUP BY 1 ORDER BY 1 DESC",
                           (f"{d.year}-01-01", (d - timedelta(days=1)).isoformat())).fetchall()
    return {
        "id": "publikum", "navn": "Publikum og kafé", "kort": "Publikum",
        "fliser": [
            _uke_flis("besok_uke", "Besøk", b, "besøk", +1, "dagsbesok"),
            _uke_flis("tilfredshet_uke", "Tilfredshet", tf, "av 5", +1, "besok_tilfredshet", 2),
            _uke_flis("kafe_uke", "Kafésalg per besøk", kf, "kr", +1, "kafe_varesalg og dagsbesok", 1),
            _uke_flis("lave_uke", "Anmeldelser med 1–2 stjerner", lave, "", -1, "anmeldelser", min_endring=2),
        ],
        "flater": [
            _linje("besok", "Besøk per uke", "dagsbesok", b["etiketter"],
                   [{"navn": "I år", "verdier": b["i_aar"], "hoved": True}, {"navn": "I fjor", "verdier": b["i_fjor"]}],
                   "besøk", forklaring="Hele uker, uten uka som pågår."),
            _linje("tilfredshet", "Tilfredshet per uke", "besok_tilfredshet", tf["etiketter"],
                   [{"navn": "I år", "verdier": tf["i_aar"], "hoved": True}, {"navn": "I fjor", "verdier": tf["i_fjor"]}],
                   "av 5", 2, forklaring="Snitt av alle svar i uka, 1–5."),
            _stolper("stjerner", "Anmeldelser per antall stjerner i år", "anmeldelser",
                     [(f"{s} stjerner", n) for s, n in stjerner], ""),
            _frister_flate("frister", ["Kafeansvarlig", "Kommunikasjon"], dato, d),
        ],
        "forslag": ["Hva klager publikum mest på i år?", "Hvordan var besøket forrige uke mot i fjor?",
                    "Hvilke kafévarer selger best per besøkende?", "Hvordan har tilfredsheten utviklet seg i høst?"],
    }


def _samling(con: Any, d: date, dato: str) -> dict[str, Any]:
    def klima(paa: date) -> float:
        return _sum(con, """SELECT count(*) FROM driftsmeldinger_epost e LEFT JOIN driftsmeldinger_tiltak t USING (melding_id)
                            WHERE e.kategori = 'klima_og_samling' AND e.dato <= ? AND (t.lost_dato IS NULL OR t.lost_dato > ?)""",
                    paa.isoformat(), paa.isoformat())
    netto = _sum(con, """SELECT sum(o.netto_resultat_nok) FROM utstillinger_historikk h JOIN utstilling_okonomi o
                         USING (utstilling_id) WHERE h.aar = ?""", d.year)
    netto_f = _sum(con, """SELECT sum(o.netto_resultat_nok) FROM utstillinger_historikk h JOIN utstilling_okonomi o
                           USING (utstilling_id) WHERE h.aar = ?""", d.year - 1)
    aar = list(range(d.year - UKER + 1, d.year + 1))
    netto_serie = [_sum(con, """SELECT sum(o.netto_resultat_nok) FROM utstillinger_historikk h JOIN utstilling_okonomi o
                               USING (utstilling_id) WHERE h.aar = ?""", a) or None for a in aar]
    roller = ["Samlingsforvalter", "Kurator"]
    forfalt, forfalt_7 = _forfalte(roller, dato), _forfalte(roller, (d - timedelta(days=7)).isoformat())
    nye_klima = _ukeserie(con, d, "driftsmeldinger_epost", lambda a, b: _sum(
        con, "SELECT count(*) FROM driftsmeldinger_epost WHERE kategori = 'klima_og_samling' AND dato BETWEEN ? AND ?",
        a.isoformat(), b.isoformat()))
    return {
        "id": "samling", "navn": "Samling og utstilling", "kort": "Samling",
        "fliser": [
            _flis("netto_utst", "Netto resultat utstillinger i år", round(netto), "kr", round(netto_f), "i fjor", +1,
                  "utstillinger_historikk og utstilling_okonomi", netto_serie, [str(a) for a in aar]),
            _beholdning(con, d, "klima_aapne", "Åpne meldinger om klima", klima,
                        "driftsmeldinger_epost og driftsmeldinger_tiltak"),
            _flis("forfalt", "Forfalte frister, samling", forfalt, "", forfalt_7, "for en uke siden", -1,
                  "frister for Samlingsforvalter og Kurator"),
        ],
        "flater": [
            _utstillinger(con, d.year),
            _frister_flate("frister", roller, dato, d),
            _linje("klima_uke", "Nye meldinger om klima og samling per uke", "driftsmeldinger_epost", nye_klima["etiketter"],
                   [{"navn": "I år", "verdier": nye_klima["i_aar"], "hoved": True},
                    {"navn": "I fjor", "verdier": nye_klima["i_fjor"]}], "meldinger"),
            _vet_ikke(con, d, ["driftsmeldinger_epost"], _uenige_utstillinger(con, d)),
        ],
        "forslag": ["Hvilke klimameldinger har vært åpne lengst?", "Hvilken utstilling ga best resultat i år?",
                    "Hvilke tilstandskontroller kommer snart?", "Hvilke innlån hadde vi i år, og fra hvem?"],
    }


def _utstillinger(con: Any, aar: int) -> dict[str, Any]:
    rader = con.execute("""SELECT h.utstilling_id, h.tittel, h.sesong, o.netto_resultat_nok
                           FROM utstillinger_historikk h JOIN utstilling_okonomi o USING (utstilling_id)
                           WHERE h.aar = ? ORDER BY o.netto_resultat_nok DESC""", (aar,)).fetchall()
    navn = [f"{re.sub(r'\s*\(\d{4}\)$', '', t).split(':')[0]} · {s}" for _, t, s, _ in rader]
    return _stolper("utstillinger", "Utstillingene i år: netto resultat", "utstillinger_historikk og utstilling_okonomi",
                    [(n, round(v)) for n, (_, _, _, v) in zip(navn, rader)], "kr", 0,
                    {"kolonner": ["ID", "Full tittel"], "rader": [[i, t] for i, t, _, _ in rader]})


def _uenige_utstillinger(con: Any, d: date) -> list[str]:
    iso = d.isoformat()
    aktive = sorted(r[0] for r in con.execute("SELECT tittel FROM utstillinger WHERE status = 'aktiv'"))
    hist = sorted({re.sub(r"\s*\(\d{4}\)$", "", r[0]).split(":")[0] for r in con.execute(
        "SELECT tittel FROM utstillinger_historikk WHERE periode_start <= ? AND periode_slutt >= ?", (iso, iso))})
    if aktive and hist and not set(aktive) & set(hist):
        return [f"To lister er uenige om hva som vises nå: {', '.join(aktive)}, eller {', '.join(hist)}"]
    return []


def lag_roller(dato: str) -> list[dict[str, Any]]:
    """Alle seks rollevisningene for `dato` (ISO, ikke etter i dag)."""
    d = date.fromisoformat(dato)
    if d > _idag():
        raise ValueError("Datoen er i fremtiden. Tall etter i dag vises ikke.")
    with db.get_db_connection() as con:
        return [f(con, d, dato) for f in (_direktor, _drift, _hr, _okonomi, _publikum, _samling)]
