"""Oppslag og regelsjekk for maskinparken (06_kart/maskinpark.json). Skill: .claude/skills/maskinpark/SKILL.md.

Bare lesing. `foresla_kommando` gir et forslag som et menneske må godkjenne; ingenting utføres (SEC-M1).
"""

from __future__ import annotations

import functools
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

KART = Path(__file__).resolve().parents[3] / "06_kart"
MASKINPARK = KART / "maskinpark.json"
GEOMETRI = KART / "bygning_geometri.json"
KATEGORIER = {"server", "robot", "anlegg", "sikkerhet", "heis"}
STATUSER = {"i_drift", "varsel", "feil", "vedlikehold"}
MOBILE_UTEN_S4 = {"renholdsrobot", "vaktrobot"}
UTFORES_ALDRI = "Verktøyet utfører ingenting. Forslaget må godkjennes og utføres av et menneske (SEC-M1)."


@functools.lru_cache(maxsize=1)
def _data() -> dict[str, Any]:
    return json.loads(MASKINPARK.read_text(encoding="utf-8"))


@functools.lru_cache(maxsize=1)
def _bygg() -> dict[str, Any]:
    g = json.loads(GEOMETRI.read_text(encoding="utf-8"))
    rom = {}
    for e in g["etasjer"]:
        for r in e["rom"]:
            rom[r["id"]] = {**r, "etasje_nr": e["etasje_nr"], "etasje": e["kode"]}
    return {"rom": rom, "klima": g["soner_definisjon"]["klima"]}


def _maskin(maskin_id: str) -> dict[str, Any]:
    mid = str(maskin_id).strip().upper()
    for m in _data()["maskiner"]:
        if m["maskin_id"] == mid:
            return m
    raise ValueError(f"Ukjent maskin: {maskin_id}")


def _neste_service(m: dict) -> str:
    return (date.fromisoformat(m["sist_service"]) + timedelta(days=m["serviceintervall_dager"])).isoformat()


def _kort(m: dict) -> dict[str, Any]:
    rom = _bygg()["rom"][m["rom_id"]]
    return {k: m[k] for k in ("maskin_id", "navn", "kategori", "type", "rom_id", "status", "kritikalitet")} | {
        "etasje": rom["etasje"], "neste_service": _neste_service(m)}


def hent_maskinpark(kategori: str | None = None, status: str | None = None, etasje: int | None = None,
                    rom_id: str | None = None) -> dict[str, Any]:
    """Maskinene med filtre, antall per status og kategori, og åpne feil."""
    if kategori is not None and kategori not in KATEGORIER:
        raise ValueError(f"kategori må være en av {sorted(KATEGORIER)}")
    if status is not None and status not in STATUSER:
        raise ValueError(f"status må være en av {sorted(STATUSER)}")
    rom = _bygg()["rom"]
    utvalg = [m for m in _data()["maskiner"]
              if (kategori is None or m["kategori"] == kategori)
              and (status is None or m["status"] == status)
              and (etasje is None or rom[m["rom_id"]]["etasje_nr"] == int(etasje))
              and (rom_id is None or m["rom_id"] == rom_id)]
    ider = {m["maskin_id"] for m in utvalg}
    per_status: dict[str, int] = {}
    per_kategori: dict[str, int] = {}
    for m in utvalg:
        per_status[m["status"]] = per_status.get(m["status"], 0) + 1
        per_kategori[m["kategori"]] = per_kategori.get(m["kategori"], 0) + 1
    apne = [h for h in _data()["hendelser"] if h["maskin_id"] in ider and not h["lukket"]]
    return {
        "i_dag": _data()["i_dag"], "antall": len(utvalg), "per_status": per_status, "per_kategori": per_kategori,
        "apne_hendelser": apne, "maskiner": [_kort(m) for m in utvalg], "datakilde": "maskinpark.json (syntetisk)",
    }


def maskinhelse(maskin_id: str) -> dict[str, Any]:
    """Én maskin: tilstand, åpne og siste hendelser, vedlikehold, neste service og kommandologg."""
    m = _maskin(maskin_id)
    i_dag = _data()["i_dag"]
    hendelser = [h for h in _data()["hendelser"] if h["maskin_id"] == m["maskin_id"]]
    vedl = [v for v in _data()["vedlikehold"] if v["maskin_id"] == m["maskin_id"]]
    neste = _neste_service(m)
    return {
        "maskin": m,
        "rom": {k: _bygg()["rom"][m["rom_id"]][k] for k in ("id", "navn", "etasje", "sikkerhetssone", "klimasone")},
        "apne_hendelser": [h for h in hendelser if not h["lukket"]],
        "siste_hendelser": hendelser[-5:],
        "siste_vedlikehold": [v for v in vedl if v["utfort"]][-5:],
        "apne_arbeidsordrer": [v for v in vedl if v["utfort"] is None],
        "neste_service": neste,
        "dager_til_service": (date.fromisoformat(neste) - date.fromisoformat(i_dag)).days,
        "forfalt": neste < i_dag,
        "kommandologg": [k for k in _data()["kommandologg"] if k["maskin_id"] == m["maskin_id"]],
        "datakilde": "maskinpark.json (syntetisk)",
    }


def vedlikeholdsplan(dager: int = 30, dato: str | None = None) -> dict[str, Any]:
    """Forfalt service, service de neste `dager` dagene og åpne arbeidsordrer."""
    dato = dato or _data()["i_dag"]
    slutt = (date.fromisoformat(dato) + timedelta(days=int(dager))).isoformat()
    forfalt, kommende = [], []
    for m in _data()["maskiner"]:
        rad = _kort(m)
        if rad["neste_service"] < dato:
            forfalt.append(rad)
        elif rad["neste_service"] <= slutt:
            kommende.append(rad)
    nokkel = lambda r: (r["neste_service"], r["maskin_id"])
    return {
        "dato": dato, "til": slutt, "forfalt": sorted(forfalt, key=nokkel), "kommende": sorted(kommende, key=nokkel),
        "apne_arbeidsordrer": [v for v in _data()["vedlikehold"] if v["utfort"] is None],
        "datakilde": "maskinpark.json (syntetisk)",
    }


def _grenser(tekst: str) -> tuple[float, float]:
    """«18°C ± 1°C» → (17, 19); «45–55% RF» → (45, 55); «Maks 50 luks» → (0, 50)."""
    tall = [float(t.replace(",", ".")) for t in re.findall(r"\d+(?:[.,]\d+)?", tekst)]
    if "±" in tekst:
        return tall[0] - tall[1], tall[0] + tall[1]
    if tekst.lower().startswith("maks"):
        return 0.0, tall[0]
    return tall[0], tall[1]


def foresla_kommando(maskin_id: str, kommando: str, parametre: dict | None = None,
                     tidspunkt: str | None = None, rolle: str = "museumsdirektor") -> dict[str, Any]:
    """Sjekker et KI-forslag mot reglene (SEC-M2..M5). Returnerer forslag eller avvisning. Utfører aldri."""
    parametre = dict(parametre or {})
    tidspunkt = tidspunkt or f"{_data()['i_dag']}T22:00"
    grunner: list[str] = []
    krav: list[str] = []
    svar: dict[str, Any] = {"maskin_id": maskin_id, "kommando": kommando, "parametre": parametre,
                            "tidspunkt": tidspunkt, "foreslatt_av_rolle": rolle, "merknad": UTFORES_ALDRI}
    try:
        m = _maskin(maskin_id)
    except ValueError as e:
        return svar | {"tillatt": False, "status": "avvist", "grunner": [str(e)], "krav": [], "godkjennes_av": []}
    rom = _bygg()["rom"]
    klima = _bygg()["klima"]

    if kommando in _data()["forbudte_kommandoer"]:
        grunner.append(f"«{kommando}» er en forbudt kommando (SEC-M2) og avvises alltid")
    elif kommando not in m["kommandoer"]:
        grunner.append(f"«{kommando}» finnes ikke for {m['maskin_id']}. Tillatt: {sorted(m['kommandoer'])}")
    elif m["ki_tilgang"] == "les" and not (kommando.startswith("kjor_selvtest") or kommando.startswith("test_")):
        grunner.append(f"{m['maskin_id']} er bare lesbar for KI; bare selvtest kan foreslås")
    else:
        for navn, regel in m["kommandoer"][kommando].items():
            if navn not in parametre:
                grunner.append(f"mangler parameter «{navn}»")
                continue
            verdi = parametre[navn]
            if regel == "rom":
                if verdi not in rom:
                    grunner.append(f"rommet «{verdi}» finnes ikke i bygget")
            elif regel == "sone":
                sone = rom[m["rom_id"]]["klimasone"]
                felt = {"temperatur_c": "temp", "rf_prosent": "rf", "luks": "luks"}[navn]
                lav, hoy = _grenser(klima[sone][felt])
                if not lav <= float(verdi) <= hoy:
                    grunner.append(f"{navn}={verdi} er utenfor {sone} ({klima[sone][felt]}) for {m['rom_id']} (SEC-M3)")
            elif isinstance(regel, list) and regel and isinstance(regel[0], str):
                if verdi not in regel:
                    grunner.append(f"{navn} må være en av {regel}")
            elif isinstance(regel, list):
                if not regel[0] <= float(verdi) <= regel[1]:
                    grunner.append(f"{navn}={verdi} er utenfor {regel[0]}–{regel[1]}")

    if not grunner and m["kategori"] == "robot":
        if m["type"] == "transportrobot" and kommando == "flytt_verk":
            fra, til = rom[parametre["fra_rom"]], rom[parametre["til_rom"]]
            klokke = datetime.fromisoformat(tidspunkt).strftime("%H:%M")
            if _data()["apningstid"]["fra"] <= klokke < _data()["apningstid"]["til"]:
                grunner.append(f"kunsttransport kl. {klokke} er innenfor åpningstid (SEC-M4)")
            if "S4" in (fra["sikkerhetssone"], til["sikkerhetssone"]):
                krav.append("to personer til stede ved S4 (SEC-M4)")
            if fra["etasje_nr"] != til["etasje_nr"]:
                krav.append("via vareheis KP-MASK-HEI-01 i kunstmodus")
        if kommando == "send_til_rom":
            mal = rom[parametre["rom_id"]]
            if m["type"] in MOBILE_UTEN_S4 and mal["sikkerhetssone"] == "S4":
                grunner.append(f"{m['type']} kjører ikke inn i S4 ({mal['id']}) (SEC-M5)")
            elif mal["etasje_nr"] != rom[m["rom_id"]]["etasje_nr"]:
                krav.append("via vareheis KP-MASK-HEI-01 (ikke publikumsheisen)")

    godkjennes_av = ["driftsansvarlig"]
    if m["kritikalitet"] == "A" or m["kategori"] == "sikkerhet":
        godkjennes_av.append("sikkerhetsansvarlig")
    tillatt = not grunner
    svar |= {"tillatt": tillatt, "status": "venter_godkjenning" if tillatt else "avvist", "grunner": grunner,
             "krav": krav, "godkjennes_av": godkjennes_av}
    if tillatt:
        svar["forslag"] = {"maskin_id": m["maskin_id"], "kommando": kommando, "parametre": parametre,
                           "tidspunkt": tidspunkt, "status": "venter_godkjenning", "begrunnelse_kreves": True}
    return svar
