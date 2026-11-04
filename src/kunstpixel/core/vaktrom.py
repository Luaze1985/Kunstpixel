"""Vaktrom: finn kandidater til én vakt på én stasjon, og kontroller utvalget.

Alt leses fra museum.db med mode=ro. Dataene er syntetiske. Reglene kommer fra databasen:
krav fra stasjon_krav, kurs fra org_ansatt_kompetanse (gyldig på datoen), fravær fra hr_fravaer,
ansettelse fra hr_ansatte, timepris fra virke_tariff og hviletid fra arbeidstid_grenser.

Datafinner kjører uten sperrer på syntetiske data (spec vaktrom-uten-sperrer, 2026-10-31):
fraværstype vises, og KI får hele kandidatgrunnlaget med navn og kontaktinfo.
Innleide filtreres på kurs fra hr_innleide_kompetanse. Vakter for innleide er ikke registrert, så hviletid og
overlapp kan ikke kontrolleres for dem.

Dette er ikke oppgave 08 (bemanningsmotoren i bemanning.py). Vaktrommet rangerer ikke folk, det sorterer på
pris uten tillegg innenfor hver gruppe og lar et menneske velge.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from src.kunstpixel.core import bemanning, db

MERKNAD_KONTROLL = "Kontrollen bygger bare på registrerte vakter og fravær i museum.db."
MERKNAD_PRIS = "Timepris er ordinær sats uten tillegg (Virke for egne ansatte, avtalt pris for innleide). Det er ikke vaktkostnaden."
MERKNAD_INNLEID = "Kurs fra registeret for innleide. Vakter hos oss er ikke registrert, så hviletid kan ikke kontrolleres."


def _dato(tekst: str) -> date:
    try:
        return date.fromisoformat(tekst)
    except (TypeError, ValueError):
        raise ValueError(f"Ugyldig dato: {tekst!r}. Bruk ÅÅÅÅ-MM-DD.") from None


def _tid(dag: date, hhmm: str) -> datetime:
    try:
        t = datetime.strptime(hhmm, "%H:%M").time()
    except (TypeError, ValueError):
        raise ValueError(f"Ugyldig klokkeslett: {hhmm!r}. Bruk TT:MM.") from None
    return datetime.combine(dag, t)


def _intervall(dag: date, start: str, slutt: str) -> tuple[datetime, datetime]:
    a, b = _tid(dag, start), _tid(dag, slutt)
    if b <= a:  # nattevakt over midnatt
        b += timedelta(days=1)
    return a, b


def _grense(con: Any, navn: str) -> float | None:
    rad = con.execute("SELECT verdi FROM arbeidstid_grenser WHERE navn = ?", (navn,)).fetchone()
    return float(rad[0]) if rad else None


def _krav_med_navn(con: Any, stasjon: str) -> list[dict[str, str]]:
    koder = bemanning.krav(stasjon)
    navn = dict(con.execute("SELECT skill_code, navn FROM org_ferdigheter").fetchall())
    return [{"kode": k, "navn": navn.get(k, k)} for k in koder]


def list_stations(db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Alle stasjoner med krav (fra stasjon_krav), sortert på navn."""
    with db.get_db_connection(db_path) as con:
        stasjoner = [r[0] for r in con.execute("SELECT DISTINCT stasjon FROM stasjon_krav ORDER BY stasjon")]
        return [{"stasjon": s, "krav": _krav_med_navn(con, s)} for s in stasjoner]


def get_weekend_shift_history(
    fra: str, til: str, stasjon: str | None = None, db_path: Path | str | None = None
) -> dict[str, Any]:
    """Helgevakter (lørdag og søndag) per person og stasjon i perioden, flest først."""
    f, t = _dato(fra), _dato(til)
    if t < f:
        raise ValueError("Til-dato er før fra-dato.")
    sql = (
        "SELECT v.ansatt_id, a.navn, a.stilling, v.stasjon, COUNT(*) AS helgevakter, "
        "ROUND(SUM(v.timer), 1) AS timer, MAX(v.dato) AS siste_dato "
        "FROM hr_vakter v JOIN hr_ansatte a ON a.ansatt_id = v.ansatt_id "
        "WHERE v.dato BETWEEN ? AND ? AND strftime('%w', v.dato) IN ('0', '6')"
    )
    params: list[Any] = [f.isoformat(), t.isoformat()]
    if stasjon:
        sql += " AND v.stasjon = ?"
        params.append(stasjon)
    sql += " GROUP BY v.ansatt_id, v.stasjon ORDER BY helgevakter DESC, v.ansatt_id, v.stasjon"
    with db.get_db_connection(db_path) as con:
        rader = [dict(r) for r in con.execute(sql, params)]
    return {
        "fra": f.isoformat(), "til": t.isoformat(), "stasjon": stasjon or "alle",
        "antall_personer": len({r["ansatt_id"] for r in rader}),
        "helgevakter_totalt": sum(r["helgevakter"] for r in rader),
        "rader": rader,
    }


def _gyldige_kurs(con: Any, dag: str, tabell: str = "org_ansatt_kompetanse", id_kolonne: str = "ansatt_id") -> dict[str, set[str]]:
    """id -> kurs som er gyldige på datoen. Samme regel for egne ansatte og innleide."""
    rader = con.execute(
        f"SELECT {id_kolonne}, skill_code FROM {tabell} "
        "WHERE sertifisert_dato <= :d AND (gyldig_til IS NULL OR gyldig_til >= :d) "
        "AND NOT (status = 'utlopt' AND gyldig_til IS NULL)",
        {"d": dag},
    ).fetchall()
    kurs: dict[str, set[str]] = {}
    for aid, kode in rader:
        kurs.setdefault(aid, set()).add(kode)
    return kurs


def _fravaerende(con: Any, dag: str) -> dict[str, str]:
    """ansatt_id -> fraværstype for alle som er borte på datoen."""
    return {r[0]: r[1] for r in con.execute("SELECT ansatt_id, type FROM hr_fravaer WHERE fra <= ? AND til >= ?", (dag, dag))}


def get_staffing_candidates(
    stasjon: str, dato: str, start: str, slutt: str, db_path: Path | str | None = None
) -> dict[str, Any]:
    """Kandidater til én vakt: egne ansatte med alle kravene gyldige på datoen først, så innleide.

    Innenfor hver gruppe sorteres det på lavest timepris uten tillegg. Ukjent pris kommer sist, aldri som null.
    Fravær gir «utilgjengelig» med fraværstypen.
    """
    dag = _dato(dato).isoformat()
    vakt_fra, vakt_til = _intervall(_dato(dato), start, slutt)
    vaktlengde = round((vakt_til - vakt_fra).total_seconds() / 3600, 2)
    ett_aar_for = (_dato(dato) - timedelta(days=365)).isoformat()
    with db.get_db_connection(db_path) as con:
        krav = _krav_med_navn(con, stasjon)
        if not krav:
            raise ValueError(f"Ukjent stasjon eller stasjon uten krav: {stasjon}")
        kravkoder = {k["kode"] for k in krav}
        kurs = _gyldige_kurs(con, dag)
        borte = _fravaerende(con, dag)
        tidligere = dict(con.execute(
            "SELECT ansatt_id, COUNT(*) FROM hr_vakter WHERE stasjon = ? AND dato >= ? AND dato < ? GROUP BY ansatt_id",
            (stasjon, ett_aar_for, dag),
        ).fetchall())
        ansatte = con.execute(
            "SELECT a.ansatt_id, a.navn, a.stilling, a.avdeling, a.stillingsprosent, a.epost, a.telefon, "
            "a.lonnstrinn_virke, t.timesats_ordinar FROM hr_ansatte a "
            "LEFT JOIN virke_tariff t ON t.lonnstrinn = a.lonnstrinn_virke "
            "WHERE a.ansatt_fra <= :d AND (a.ansatt_til IS NULL OR a.ansatt_til = '' OR a.ansatt_til >= :d)",
            {"d": dag},
        ).fetchall()
        egne, utilgjengelige = [], []
        for a in ansatte:
            if not kravkoder <= kurs.get(a["ansatt_id"], set()):
                continue
            rad = {
                "id": a["ansatt_id"], "type": "egen", "navn": a["navn"], "stilling": a["stilling"],
                "avdeling": a["avdeling"], "stillingsprosent": a["stillingsprosent"],
                "kompetanse": sorted(kravkoder), "timepris_uten_tillegg": a["timesats_ordinar"],
                "prisgrunnlag": f"Virke lønnstrinn {a['lonnstrinn_virke']}" if a["timesats_ordinar"] is not None else "Ukjent",
                "vakter_paa_stasjonen_siste_12_mnd": tidligere.get(a["ansatt_id"], 0),
                "epost": a["epost"], "telefon": a["telefon"],
            }
            if a["ansatt_id"] in borte:
                utilgjengelige.append({"id": rad["id"], "navn": rad["navn"], "stilling": rad["stilling"],
                                       "status": "utilgjengelig", "fravaerstype": borte[a["ansatt_id"]]})
            else:
                egne.append(rad)
        kontakter = dict(con.execute(
            "SELECT orgnr, kontaktperson_ekstern FROM hr_innleie WHERE kontaktperson_ekstern IS NOT NULL "
            "AND kontaktperson_ekstern != '' ORDER BY aar"
        ).fetchall())
        # Innleide filtreres på samme måte som egne: alle kravene må være gyldige på datoen.
        innleid_kurs = _gyldige_kurs(con, dag, "hr_innleide_kompetanse", "innleid_id")
        innleide = [
            {
                "id": r["innleid_id"], "type": "innleid", "navn": r["navn"], "stilling": r["stilling"],
                "firma": r["firma"], "orgnr": r["orgnr"], "kategori": r["kategori"],
                "timepris_uten_tillegg": r["timepris_nok"],
                "prisgrunnlag": "Avtalt timepris" if r["timepris_nok"] is not None else "Ukjent",
                "avtale": f"{r['avtale_fra']} til {r['avtale_til']}",
                "kontaktperson_firma": kontakter.get(r["orgnr"]),
                "kompetanse": sorted(kravkoder), "merknad": MERKNAD_INNLEID,
                "epost": r["epost"], "telefon": r["telefon"],
            }
            for r in con.execute(
                "SELECT * FROM hr_innleide_personer WHERE status = 'Aktiv' AND avtale_fra <= :d AND avtale_til >= :d",
                {"d": dag},
            )
            if kravkoder <= innleid_kurs.get(r["innleid_id"], set())
        ]

    def nokkel(r: dict[str, Any]) -> tuple[int, float, str]:
        pris = r["timepris_uten_tillegg"]
        return (pris is None, pris if pris is not None else 0.0, r["id"])

    egne.sort(key=nokkel)
    innleide.sort(key=nokkel)
    for i, r in enumerate(egne + innleide, start=1):
        r["nr"] = i
    return {
        "stasjon": stasjon, "dato": dag, "start": start, "slutt": slutt, "vaktlengde_timer": vaktlengde, "krav": krav,
        "egne": egne, "innleide": innleide, "utilgjengelige": utilgjengelige,
        "antall_egne": len(egne), "antall_innleide": len(innleide), "antall_utilgjengelige": len(utilgjengelige),
        "sortering": "Egne ansatte først, så innleide. Innenfor hver gruppe lavest timepris uten tillegg. Ukjent pris sist.",
        "merknad_pris": MERKNAD_PRIS,
    }


def check_staffing_selection(
    stasjon: str, dato: str, start: str, slutt: str, ids: list[str], db_path: Path | str | None = None,
    unnta_vakter: list[str] | None = None,
) -> dict[str, Any]:
    """Kontroller valgte kandidater: kompetanse, fravær, overlapp og hviletid mot registrerte vakter.

    `unnta_vakter`: vakter som ikke teller (vakten en person gir fra seg i et bytte).
    """
    unntatt = set(unnta_vakter or [])
    if not ids:
        raise ValueError("Velg minst én kandidat.")
    d = _dato(dato)
    ny_a, ny_b = _intervall(d, start, slutt)
    dag = d.isoformat()
    resultater = []
    with db.get_db_connection(db_path) as con:
        hvile = _grense(con, "daglig_hvile_timer")
        dognmaks = _grense(con, "dognmaks_timer")
        kravkoder = set(bemanning.krav(stasjon))
        if not kravkoder:
            raise ValueError(f"Ukjent stasjon eller stasjon uten krav: {stasjon}")
        kurs = _gyldige_kurs(con, dag)
        borte = _fravaerende(con, dag)
        innleide = {r[0] for r in con.execute("SELECT innleid_id FROM hr_innleide_personer")}
        innleid_kurs = _gyldige_kurs(con, dag, "hr_innleide_kompetanse", "innleid_id")
        for pid in ids[:50]:
            if pid in innleide:
                # Kurs kan kontrolleres. Vakter, overlapp og hviletid kan ikke: de er ikke registrert hos oss.
                mangler = sorted(kravkoder - innleid_kurs.get(pid, set()))
                funn = ["Mangler gyldig kurs på datoen: " + ", ".join(mangler)] if mangler else ["Kurs ok."]
                funn.append("Innleid: vakter er ikke registrert hos oss, så overlapp og hviletid kan ikke kontrolleres.")
                resultater.append({"id": pid, "status": "avvik" if mangler else "delvis", "funn": funn})
                continue
            funn: list[str] = []
            mangler = sorted(kravkoder - kurs.get(pid, set()))
            if mangler:
                funn.append("Mangler gyldig kurs på datoen: " + ", ".join(mangler))
            if pid in borte:
                funn.append(f"Utilgjengelig på datoen ({borte[pid]}).")
            vakter = con.execute(
                "SELECT vakt_id, dato, start, slutt, stasjon FROM hr_vakter WHERE ansatt_id = ? AND dato BETWEEN ? AND ? "
                "AND start IS NOT NULL AND slutt IS NOT NULL ORDER BY dato, start",
                (pid, (d - timedelta(days=1)).isoformat(), (d + timedelta(days=1)).isoformat()),
            ).fetchall()
            for v in vakter:
                if v["vakt_id"] in unntatt:
                    continue
                a, b = _intervall(date.fromisoformat(v["dato"]), v["start"], v["slutt"])
                if a < ny_b and ny_a < b:
                    funn.append(f"Overlapper med registrert vakt {v['vakt_id']} ({v['dato']} {v['start']}–{v['slutt']}, {v['stasjon']}).")
                    continue
                fri = (ny_a - b) if b <= ny_a else (a - ny_b)
                timer = fri.total_seconds() / 3600
                if hvile is not None and timer < hvile:
                    funn.append(f"For kort hviletid: {timer:.1f} timer mellom denne og vakt {v['vakt_id']} (krav {hvile:g} timer, AML § 10-8).")
            lengde = (ny_b - ny_a).total_seconds() / 3600
            if dognmaks is not None and lengde > dognmaks:
                funn.append(f"Vakten er {lengde:g} timer, over døgnmaks på {dognmaks:g} timer. Må i så fall merkes som overtid.")
            resultater.append({"id": pid, "status": "ok" if not funn else "avvik", "funn": funn or ["Ingen funn."]})
    return {
        "stasjon": stasjon, "dato": dag, "start": start, "slutt": slutt,
        "hviletid_krav_timer": hvile, "dognmaks_timer": dognmaks,
        "resultater": resultater, "merknad": MERKNAD_KONTROLL,
    }


def _vakt(con: Any, vakt_id: str) -> dict[str, Any]:
    rad = con.execute(
        "SELECT v.vakt_id, v.ansatt_id, a.navn, v.dato, v.start, v.slutt, v.stasjon FROM hr_vakter v "
        "JOIN hr_ansatte a ON a.ansatt_id = v.ansatt_id WHERE v.vakt_id = ?", (str(vakt_id).strip().upper(),)
    ).fetchone()
    if rad is None:
        raise ValueError(f"Finner ingen vakt med ID {vakt_id}. Bruk get_shifts_for_date for å finne vakt-ID.")
    if not rad["start"] or not rad["slutt"]:
        raise ValueError(f"Vakten {vakt_id} mangler klokkeslett og kan ikke kontrolleres.")
    return dict(rad)


def _navn(con: Any, ansatt_id: str) -> str:
    rad = con.execute("SELECT navn FROM hr_ansatte WHERE ansatt_id = ?", (ansatt_id,)).fetchone()
    if rad is None:
        raise ValueError(f"Finner ingen ansatt med ID {ansatt_id}.")
    return rad[0]


def check_shift_takeover(vakt_id: str, ansatt_id: str, db_path: Path | str | None = None) -> dict[str, Any]:
    """Kan en ansatt ta over en registrert vakt? Kurs, fravær, overlapp, hviletid og døgnmaks for den som tar over."""
    with db.get_db_connection(db_path) as con:
        v = _vakt(con, vakt_id)
        ny = str(ansatt_id).strip().upper()
        navn = _navn(con, ny)
    if ny == v["ansatt_id"]:
        raise ValueError(f"{navn} har allerede vakten {v['vakt_id']}.")
    k = check_staffing_selection(v["stasjon"], v["dato"], v["start"], v["slutt"], [ny], db_path)
    return {"vakt": v, "tar_over": {"ansatt_id": ny, "navn": navn}, "status": k["resultater"][0]["status"],
            "funn": k["resultater"][0]["funn"], "hviletid_krav_timer": k["hviletid_krav_timer"], "merknad": MERKNAD_KONTROLL}


def check_shift_swap(vakt_a: str, vakt_b: str, db_path: Path | str | None = None) -> dict[str, Any]:
    """Bytte mellom to registrerte vakter: hver person tar den andres vakt og gir fra seg sin egen.

    Begge retninger sjekkes. Vakten personen gir fra seg teller ikke i overlapp og hviletid.
    """
    with db.get_db_connection(db_path) as con:
        va, vb = _vakt(con, vakt_a), _vakt(con, vakt_b)
    if va["ansatt_id"] == vb["ansatt_id"]:
        raise ValueError("Begge vaktene tilhører samme person. Et bytte trenger to personer.")
    retninger = []
    for gir, tar in ((va, vb), (vb, va)):
        k = check_staffing_selection(tar["stasjon"], tar["dato"], tar["start"], tar["slutt"], [gir["ansatt_id"]], db_path,
                                     unnta_vakter=[gir["vakt_id"]])
        r = k["resultater"][0]
        retninger.append({"ansatt_id": gir["ansatt_id"], "navn": gir["navn"], "gir_fra_seg": gir["vakt_id"],
                          "tar": tar["vakt_id"], "status": r["status"], "funn": r["funn"]})
    return {"vakt_a": va, "vakt_b": vb, "retninger": retninger,
            "status": "ok" if all(r["status"] == "ok" for r in retninger) else "avvik",
            "hviletid_krav_timer": k["hviletid_krav_timer"], "merknad": MERKNAD_KONTROLL}


def find_employee(sok: str, per_dato: str | None = None, db_path: Path | str | None = None, maks_treff: int | None = 15) -> list[dict[str, Any]]:
    """Finn ansatte på navn, ID, stilling eller avdeling. Med ansettelsesdato, ansiennitet, kontaktinfo og kurs."""
    s = str(sok or "").strip()
    if not s:
        raise ValueError("Oppgi navn, ansatt-ID, stilling eller avdeling.")
    per = _dato(per_dato) if per_dato else date.today()
    # Treff på starten av et ord i navn, stilling eller avdeling («HR» finner HR-rådgivere, ikke «Christian»).
    ord_start = re.compile(r"(?<![0-9a-zæøåA-ZÆØÅ])" + re.escape(s), re.IGNORECASE)
    with db.get_db_connection(db_path) as con:
        alle = con.execute(
            "SELECT ansatt_id, navn, stilling, avdeling, ansatt_fra, ansatt_til, stillingsprosent, epost, telefon FROM hr_ansatte "
            "ORDER BY (ansatt_til IS NOT NULL AND ansatt_til != ''), ansatt_id"
        ).fetchall()
        rader = [r for r in alle if r["ansatt_id"] == s.upper()
                 or any(ord_start.search(r[f] or "") for f in ("navn", "stilling", "avdeling"))][:maks_treff]
        navn = dict(con.execute("SELECT skill_code, navn FROM org_ferdigheter").fetchall())
        ut = []
        for r in rader:
            fra = date.fromisoformat(r["ansatt_fra"])
            kurs = [{"kurs": navn.get(k["skill_code"], k["skill_code"]), "gyldig_til": k["gyldig_til"], "status": k["status"]}
                    for k in con.execute("SELECT skill_code, gyldig_til, status FROM org_ansatt_kompetanse WHERE ansatt_id = ? "
                                         "ORDER BY skill_code", (r["ansatt_id"],))]
            aktiv = not r["ansatt_til"] or r["ansatt_til"] >= per.isoformat()
            ut.append({**dict(r), "aktiv": aktiv, "ansiennitet_aar": max(0, (per - fra).days // 365), "kurs": kurs})
    return ut


def get_employee_reviews(ansatt_id: str, db_path: Path | str | None = None) -> dict[str, Any]:
    """Medarbeidersamtalene til én ansatt (søk på ID eller navn), nyeste først."""
    s = str(ansatt_id or "").strip()
    if not s:
        raise ValueError("Oppgi ansatt-ID eller navn.")
    with db.get_db_connection(db_path) as con:
        rader = [dict(r) for r in con.execute(
            "SELECT m.samtale_id, m.ansatt_id, a.navn, a.stilling, m.dato, m.leder_rolle, m.samlet_vurdering, m.styrker, "
            "m.utviklingsomrade, m.erfaring_notat, m.onsker_flere_helgevakter FROM hr_medarbeidersamtaler m "
            "JOIN hr_ansatte a ON a.ansatt_id = m.ansatt_id WHERE m.ansatt_id = ? OR lower(a.navn) LIKE ? "
            "ORDER BY m.dato DESC", (s.upper(), f"%{s.lower()}%"),
        )]
    return {"sok": s, "antall": len(rader), "samtaler": rader}


# ---------------------------------------------------------------------------
# Grunnlag til KI-laget. Uten sperrer: hele kandidatraden sendes, med navn, kontaktinfo og fraværstype.

SYSTEM_SAMMENLIGN = (
    "Du hjelper ledelsen i et norsk kunstmuseum med å velge hvem som skal ta én vakt.\n"
    "Bruk opplysningene i JSON-en. Sammenlign kandidatene, ranger dem og anbefal hvem ledelsen bør spørre først.\n"
    "Skriv på norsk bokmål, maks 150 ord. Bruk navnene."
)

SYSTEM_KONTAKT = (
    "Du skriver et kort, høflig utkast til en forespørsel om å ta én vakt i et norsk kunstmuseum.\n"
    "Bruk mottakerens navn og opplysningene i JSON-en. Be om svar.\n"
    "Skriv på norsk bokmål, maks 90 ord, uten emnelinje."
)

KILDER_EGNE = ["hr_ansatte", "hr_vakter", "hr_fravaer", "org_ansatt_kompetanse", "virke_tariff", "stasjon_krav"]
KILDER_INNLEIDE = ["hr_innleide_personer", "stasjon_krav"]


def grunnlag_sammenligning(kandidater: dict[str, Any], ids: list[str]) -> tuple[dict[str, Any], list[str]]:
    """Grunnlag og kildetabeller for sammenligningen. Hele kandidatradene sendes, i rapportens rekkefølge."""
    valgt = set(ids)
    rader = [r for r in kandidater["egne"] + kandidater["innleide"] if r["id"] in valgt]
    if not rader:
        raise ValueError("Ingen av de valgte er blant kandidatene.")
    kilder = ["stasjon_krav"]
    if any(r["type"] == "egen" for r in rader):
        kilder = KILDER_EGNE
    if any(r["type"] == "innleid" for r in rader):
        kilder = sorted(set(kilder) | set(KILDER_INNLEIDE))
    grunnlag = {
        "vakt": {k: kandidater[k] for k in ("stasjon", "dato", "start", "slutt")},
        "krav": [k["navn"] for k in kandidater["krav"]],
        "sortering": kandidater["sortering"],
        "kandidater": rader,
        "utilgjengelige": kandidater["utilgjengelige"],
    }
    return grunnlag, kilder


def grunnlag_kontakt(kandidater: dict[str, Any], pid: str) -> tuple[dict[str, Any], list[str]]:
    """Grunnlag for kontaktutkastet: vakten, kravene og hele raden til mottakeren."""
    rad = next((r for r in kandidater["egne"] + kandidater["innleide"] if r["id"] == pid), None)
    if rad is None:
        raise ValueError("Kandidaten finnes ikke blant kandidatene til vakten.")
    grunnlag = {
        "vakt": {k: kandidater[k] for k in ("stasjon", "dato", "start", "slutt")},
        "krav": [k["navn"] for k in kandidater["krav"]],
        "mottaker": rad,
    }
    return grunnlag, (KILDER_INNLEIDE if rad["type"] == "innleid" else KILDER_EGNE)


def get_personnel_file(ansatt_id: str, db_path: Path | str | None = None) -> dict[str, Any]:
    """Personalmappen til én ansatt, søkt på ansatt-ID eller navn. Uten rollesperre i Datafinner."""
    nokkel = (ansatt_id or "").strip()
    if not nokkel:
        raise ValueError("Oppgi ansatt-ID eller navn.")
    with db.get_db_connection(db_path) as con:
        saker = [dict(r) for r in con.execute(
            "SELECT * FROM hr_personalmapper WHERE ansatt_id = ? OR navn LIKE ? ORDER BY opprettet_dato",
            (nokkel.upper(), f"%{nokkel}%"),
        )]
    return {"ansatt_id": nokkel, "antall_saker": len(saker), "saker": saker}


def get_absence_by_person(
    fra: str, til: str, stasjon: str | None = None, db_path: Path | str | None = None
) -> dict[str, Any]:
    """Fravær per person i perioden, med antall perioder, dager og type.

    Med stasjon tas bare de med som har hatt vakt der i perioden.
    """
    f, t = _dato(fra).isoformat(), _dato(til).isoformat()
    sql = (
        "SELECT f.ansatt_id, a.navn, a.stilling, COUNT(*) AS perioder, "
        "CAST(SUM(julianday(MIN(f.til, :t)) - julianday(MAX(f.fra, :f)) + 1) AS INTEGER) AS dager, "
        "SUM(f.type = 'egenmelding') AS egenmeldinger, SUM(f.type != 'egenmelding') AS andre_fravaer "
        "FROM hr_fravaer f JOIN hr_ansatte a ON a.ansatt_id = f.ansatt_id WHERE f.fra <= :t AND f.til >= :f"
    )
    params: dict[str, Any] = {"f": f, "t": t}
    if stasjon:
        sql += " AND f.ansatt_id IN (SELECT ansatt_id FROM hr_vakter WHERE stasjon = :s AND dato BETWEEN :f AND :t)"
        params["s"] = stasjon
    sql += " GROUP BY f.ansatt_id ORDER BY dager DESC, f.ansatt_id"
    with db.get_db_connection(db_path) as con:
        rader = [dict(r) for r in con.execute(sql, params)]
    return {"fra": f, "til": t, "stasjon": stasjon or "alle", "antall_personer": len(rader), "personer": rader}
