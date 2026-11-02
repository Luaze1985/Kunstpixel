"""Styrt løkke mot en annen språkmodell (Colab eller annet). Modellen er en funksjon som tar tekst og gir tekst.

    kjor(spor_modell, ut_mappe)

For hver fil: send bestillingen, kontroller svaret, send rettelisten ved feil, høyst tre runder. Hard grense på
antall modellkall. Modellen får aldri se noe annet enn bestillingen, sitt eget forrige svar og rettelisten.
Funksjonen skriver ingenting utenfor `ut_mappe` og installerer ingenting i prosjektet.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

try:  # i repoet
    from src.kunstpixel.core.intern import leveranse as L
    from src.kunstpixel.core.intern.leveranse_bestilling import bestilling_for
except ImportError:  # i Colab-pakken
    import leveranse as L  # type: ignore[no-redef]
    from leveranse_bestilling import bestilling_for  # type: ignore[no-redef]

MAKS_RUNDER = 3
MAKS_KALL = 20


def kodeblokker(tekst: str) -> list[tuple[str, str]]:
    """Linjebasert lesing av ```-blokker. Returnerer [(språk, innhold)]. Ulukket blokk tas ut teksten slutt."""
    ut: list[tuple[str, str]] = []
    sprak: str | None = None
    buf: list[str] = []
    for linje in tekst.splitlines():
        s = linje.strip()
        if s.startswith("```"):
            if sprak is None:
                sprak, buf = s[3:].strip().lower(), []
            else:
                ut.append((sprak, "\n".join(buf)))
                sprak = None
            continue
        if sprak is not None:
            buf.append(linje)
    if sprak is not None:
        ut.append((sprak, "\n".join(buf)))
    return ut


def yaml_blokker(tekst: str) -> list[str]:
    """Bare blokker uten språk eller merket yaml/yml. Python, json og annet hoppes over."""
    return [b for s, b in kodeblokker(tekst) if s in ("", "yaml", "yml")]


def hent_yaml(svar: Any) -> str:
    """Plukker ut YAML fra et modellsvar. Tar første YAML-blokk hvis det finnes, ellers hele teksten."""
    if not isinstance(svar, str):
        return ""
    blokker = yaml_blokker(svar)
    return (blokker[0] if blokker else svar).strip() + "\n"


MAKS_SVAR = 1_000_000  # tegn. Større svar importeres ikke.
_NOKKEL_TIL_KODE = {"myndigheter": "A", "steg": "B", "rapporter": "C", "maler": "D", "oppgaver": "E", "historikk": "F"}
_TOPPNIVA_RE = re.compile(r"^(myndigheter|steg|rapporter|maler|oppgaver|historikk):", re.M)


def del_svar(tekst: str, fil: str | None = None) -> tuple[dict[str, str], list[str]]:
    """Deler et innlimt chat-svar i YAML per fil. Returnerer ({kode: yaml}, advarsler).

    Hver kodeblokk får filkode ut fra sitt toppnivåfelt (myndigheter, steg, rapporter, maler, oppgaver).
    Uten kodeblokker brukes hele teksten, og da må `fil` oppgis. Står samme fil flere ganger, vinner den siste.
    """
    adv: list[str] = []
    if not isinstance(tekst, str) or not tekst.strip():
        return {}, ["Tomt svar"]
    if len(tekst) > MAKS_SVAR:
        return {}, [f"Svaret er over {MAKS_SVAR} tegn og importeres ikke"]
    alle = kodeblokker(tekst)
    kandidater = yaml_blokker(tekst) or ([] if alle else [tekst])
    for s, _ in alle:
        if s not in ("", "yaml", "yml"):
            adv.append(f"En {s}-blokk ble hoppet over")
    ut: dict[str, str] = {}
    for blokk in kandidater:
        m = _TOPPNIVA_RE.search(blokk)
        kode = _NOKKEL_TIL_KODE[m.group(1)] if m else fil
        if kode is None or kode not in L.FILER:
            adv.append("En blokk ble hoppet over: kunne ikke avgjøre hvilken fil den er. Bruk --fil A, B, C, D eller E")
            continue
        if fil and m and kode != fil:
            adv.append(f"En blokk for {L.FILER[kode]} ble hoppet over fordi du ba om {L.FILER[fil]}")
            continue
        if kode in ut:
            adv.append(f"{L.FILER[kode]} sto flere ganger. Bruker den siste")
        ut[kode] = blokk.strip() + "\n"
    return ut, adv


def importer_svar(tekst: str, mappe: Path, fil: str | None = None) -> tuple[list[str], list[str]]:
    """Skriver filene fra et chat-svar til `mappe`. Returnerer (skrevne filkoder, advarsler)."""
    deler, adv = del_svar(tekst, fil.upper() if fil else None)
    mappe.mkdir(parents=True, exist_ok=True)
    skrevet: list[str] = []
    for kode, yaml_tekst in deler.items():
        (mappe / L.FILER[kode]).write_text(yaml_tekst, encoding="utf-8")
        skrevet.append(kode)
    return skrevet, adv


def rettemelding(bestilling: str, forrige: str, retteliste: str) -> str:
    return f"{bestilling}\n\n## Din forrige leveranse\n```yaml\n{forrige}```\n\n## Feil som må rettes\n{retteliste}"


def kjor(
    spor_modell: Callable[[str], str],
    ut: Path,
    koder: list[str] | None = None,
    maks_runder: int = MAKS_RUNDER,
    maks_kall: int = MAKS_KALL,
    logg: Callable[[str], None] = print,
) -> dict[str, dict[str, Any]]:
    """Returnerer {filkode: {"ok": bool, "runder": int, "feil": int, "stopp": str | None}}."""
    ut.mkdir(parents=True, exist_ok=True)
    resultat: dict[str, dict[str, Any]] = {}
    kall = 0
    for k in koder or list(L.FILER):
        bestilling = bestilling_for([k])
        forrige, liste = None, ""
        res: dict[str, Any] = {"ok": False, "runder": 0, "feil": None, "stopp": None}
        resultat[k] = res
        for runde in range(1, maks_runder + 1):
            if kall >= maks_kall:
                res["stopp"] = "kallgrense"
                logg(f"{L.FILER[k]}: kallgrensen på {maks_kall} er nådd")
                break
            prompt = bestilling if forrige is None else rettemelding(bestilling, forrige, liste)
            try:
                svar = spor_modell(prompt)
            except Exception as exc:  # noqa: BLE001 - en feil hos modellen stopper bare denne filen
                kall += 1
                res["runder"], res["stopp"] = runde, f"modellfeil: {type(exc).__name__}"
                logg(f"{L.FILER[k]}: modellen feilet ({type(exc).__name__})")
                break
            kall += 1
            tekst = hent_yaml(svar)
            (ut / L.FILER[k]).write_text(tekst, encoding="utf-8")
            funn = L.kontroller_tekst(k, tekst)
            feil = [f for f in funn if f.alvor == "FEIL"]
            res["runder"], res["feil"] = runde, len(feil)
            logg(f"{L.FILER[k]}: runde {runde}, {len(feil)} feil, {len(funn) - len(feil)} advarsler")
            if not feil:
                res["ok"] = True
                break
            forrige, liste = tekst, L.retteliste_fil(funn)
        if not res["ok"] and not res["stopp"]:
            res["stopp"] = "maks runder uten å bestå"
    logg(f"Modellkall brukt: {kall} av {maks_kall}")
    return resultat
