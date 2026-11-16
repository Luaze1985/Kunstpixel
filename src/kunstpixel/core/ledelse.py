"""Rene beregninger for ledelsessiden (spec datafinner-ledelse, B1/B2/D1).

Funksjonene her leser ingenting fra databasen. De tar rader og datoer inn og gir tall ut, så de kan testes
med faste verdier. Verktøyene i driftsoversikt.py henter radene og kaller dem.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, timedelta
from typing import Any

# Terskler per måltall (B2). Forslag godtatt av Lars 2026-11-16: dataene er simulert, så grensene kan justeres her.
# folg_med/over_terskel er andel avvik fra normalt i den «dårlige» retningen (grensen er med).
TERSKLER: dict[str, dict[str, Any]] = {
    "besok": {"lavere_er_bra": False, "folg_med": 0.15, "over_terskel": 0.30},
    "apne_driftsmeldinger": {"lavere_er_bra": True, "folg_med": 0.15, "over_terskel": 0.30},
}


# Fristregler (B7). Lars 2026-11-16: uke 4/7 fra første fraværsdag, 14 dager for åpne saker.
# Forslag som ikke er avklart: 12 måneder mellom tilstandskontroller, 365 dager bakover for åpne saker, 60 dager fram.
FRISTREGLER: dict[str, Any] = {
    "sykefravaer_uker": (4, 7),
    "aapen_sak_dager": 14,
    "aapen_sak_maks_alder_dager": 365,
    "tilstand_maaneder": 12,
    "horisont_dager": 60,
}
_MAANEDER = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober",
             "november", "desember"]


def _d(tekst: str) -> date:
    return date.fromisoformat(tekst)


def normalt_for_ukedag(serie: Mapping[str, float | None], dag: str, uker: int = 4, maks_tilbake: int = 8) -> float | None:
    """Snitt for samme ukedag de siste `uker` åpne ukene før `dag`.

    `serie` er dato -> verdi. Stengte dager er None eller mangler og hoppes over. Det letes høyst `maks_tilbake`
    uker bakover. Færre enn to sammenligningsdager gir None (Ukjent), fordi ett tall ikke er et «normalt».
    """
    d0 = _d(dag)
    funnet: list[float] = []
    for n in range(1, maks_tilbake + 1):
        v = serie.get((d0 - timedelta(weeks=n)).isoformat())
        if v is not None:
            funnet.append(float(v))
            if len(funnet) == uker:
                break
    if len(funnet) < 2:
        return None
    return round(sum(funnet) / len(funnet), 1)


def vurder(verdi: float | None, normalt: float | None, maaltall: str, aapent: bool = True) -> dict[str, Any]:
    """Endring mot normalt og status: Normal, Følg med, Over terskel, Ukjent (mangler data) eller Stengt."""
    ut: dict[str, Any] = {"verdi": verdi, "normalt": normalt, "endring": None, "endring_pst": None}
    if not aapent:
        return {**ut, "status": "Stengt"}
    if verdi is None or normalt is None or normalt == 0:
        return {**ut, "status": "Ukjent"}
    andel = (verdi - normalt) / normalt
    ut["endring"] = round(verdi - normalt, 1)
    ut["endring_pst"] = round(andel * 100, 1)
    t = TERSKLER[maaltall]
    daarlig = andel if t["lavere_er_bra"] else -andel
    # Avrunding på 4 desimaler, så nøyaktig 15 % ikke havner under grensen på grunn av flyttall.
    daarlig = round(daarlig, 4)
    if daarlig >= t["over_terskel"]:
        status = "Over terskel"
    elif daarlig >= t["folg_med"]:
        status = "Følg med"
    else:
        status = "Normal"
    return {**ut, "status": status}


def kutt_fremtid(rader: list[dict[str, Any]], idag: str, felt: str = "dato") -> list[dict[str, Any]]:
    """Bare rader før `idag` (D1). Dagens tall er ikke ferdige, og senere tall er syntetiske."""
    return [r for r in rader if str(r.get(felt) or "") < idag]


def frist_gruppe(frist: date, idag: date) -> str | None:
    """Forfalt, I dag, Denne uka (til og med søndag) eller Senere (innen horisonten). None er for langt fram."""
    if frist < idag:
        return "Forfalt"
    if frist == idag:
        return "I dag"
    if frist <= idag + timedelta(days=6 - idag.weekday()):
        return "Denne uka"
    if frist <= idag + timedelta(days=FRISTREGLER["horisont_dager"]):
        return "Senere"
    return None


def beregn_frister(kandidater: list[dict[str, Any]], idag: date) -> list[dict[str, Any]]:
    """Legg til id, dager_til og gruppe. Tar bort det som er for langt fram, og sorterer på frist."""
    ut = []
    for k in kandidater:
        frist = _d(k["frist_dato"])
        gruppe = frist_gruppe(frist, idag)
        if gruppe is None:
            continue
        ut.append({**k, "id": f"{k['type']}:{k['ref']}:{k['frist_dato']}", "dager_til": (frist - idag).days,
                   "gruppe": gruppe})
    return sorted(ut, key=lambda f: (f["frist_dato"], f["type"], f["ref"]))


def sykefravaer_frister(fra: str, til: str | None, idag: date) -> list[tuple[str, date]]:
    """Oppfølgingsplan (uke 4) og dialogmøte (uke 7) regnet fra første fraværsdag.

    Bare pågående fravær (til er i dag eller senere, eller ukjent), og bare frister fraværet varer fram til.
    """
    slutt = _d(til) if til else None
    if slutt is not None and slutt < idag:
        return []
    start = _d(fra)
    ut = []
    for uke, navn in zip(FRISTREGLER["sykefravaer_uker"], ("sykefravaer_uke4", "sykefravaer_uke7")):
        frist = start + timedelta(weeks=uke)
        if slutt is None or frist <= slutt:
            ut.append((navn, frist))
    return ut


def _siste_dag(aar: int, maaned: int) -> date:
    return (date(aar + (maaned == 12), maaned % 12 + 1, 1)) - timedelta(days=1)


def rapport_frist(maned: str, idag: date) -> date | None:
    """Siste dag i måneden (Lars, Å2). Månedlig: denne måneden. Kvartalsvis: kvartalets siste måned.
    Navngitt måned: neste gang den måneden slutter. Løpende og ukjent: ingen frist."""
    m = (maned or "").strip().lower()
    if m == "månedlig":
        return _siste_dag(idag.year, idag.month)
    if m == "kvartalsvis":
        return _siste_dag(idag.year, ((idag.month - 1) // 3 + 1) * 3)
    if m in _MAANEDER:
        nr = _MAANEDER.index(m) + 1
        frist = _siste_dag(idag.year, nr)
        return frist if frist >= idag else _siste_dag(idag.year + 1, nr)
    return None


def fyll_dager(rader: list[dict[str, Any]], fra: str, til: str, felt: str = "dato") -> list[dict[str, Any]]:
    """Én rad per dag fra og med `fra` til og med `til`. Dager uten rad får {"mangler": True}."""
    per_dag = {r[felt]: r for r in rader}
    ut, d, slutt = [], _d(fra), _d(til)
    while d <= slutt:
        ut.append(per_dag.get(d.isoformat(), {felt: d.isoformat(), "mangler": True}))
        d += timedelta(days=1)
    return ut
