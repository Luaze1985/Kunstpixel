"""Arealregning og regelsjekk for bygningsmodellen i 06_kart/bygning_geometri.json.

Koordinater: 10 enheter = 1 m. Areal = b × d / 100.
BTA = summen av volumene. BRA = innvendige rektangler + fasadeveggen mellom fløyene
(den gamle østfasaden er innervegg nå og regnes med i BRA).
"""

from __future__ import annotations

from itertools import combinations

TOLERANSE = 0.5  # m²


def _areal(r: dict) -> float:
    return round(r["b"] * r["d"] / 100, 2)


def rom_areal(rom: dict) -> float:
    return round(rom["w"] * rom["h"] / 100, 2)


def bta_etasje(modell: dict) -> float:
    return round(sum(_areal(v) for v in modell["museum"]["fotavtrykk"]["volumer"]), 2)


def bra_etasje(modell: dict) -> float:
    fot = modell["museum"]["fotavtrykk"]
    return round(sum(_areal(v["innvendig"]) for v in fot["volumer"]) + _areal(fot["fasadevegg"]), 2)


def _inni(rom: dict, f: dict) -> bool:
    return (rom["x"] >= f["x"] and rom["y"] >= f["y"]
            and rom["x"] + rom["w"] <= f["x"] + f["b"] and rom["y"] + rom["h"] <= f["y"] + f["d"])


def _overlapper(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]
            and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])


def feil(modell: dict) -> list[str]:
    """Returnerer alle brudd på reglene. Tom liste betyr at modellen henger sammen."""
    fot = modell["museum"]["fotavtrykk"]
    innsider = [v["innvendig"] for v in fot["volumer"]]
    bra = bra_etasje(modell)
    fasade = _areal(fot["fasadevegg"])
    ut: list[str] = []
    sjakter: dict[str, set[tuple]] = {}

    for etasje in modell["etasjer"]:
        kode = etasje["kode"]
        rom = etasje["rom"]
        for r in rom:
            if abs(r["areal_m2"] - rom_areal(r)) > 0.01:
                ut.append(f"{kode}: {r['id']} har areal {r['areal_m2']}, men b×d gir {rom_areal(r)}")
            if not any(_inni(r, f) for f in innsider):
                ut.append(f"{kode}: {r['id']} ligger utenfor fløyene")
            if r.get("sjakt"):
                sjakter.setdefault(r["sjakt"], set()).add((r["x"], r["y"], r["w"], r["h"]))
        for a, b in combinations(rom, 2):
            if _overlapper(a, b):
                ut.append(f"{kode}: overlapp mellom {a['id']} og {b['id']}")
        sum_rom = sum(rom_areal(r) for r in rom)
        if abs(sum_rom + fasade - bra) > TOLERANSE:
            ut.append(f"{kode}: rommene ({sum_rom:.2f}) + fasadevegg ({fasade}) fyller ikke BRA ({bra})")
        if sum(1 for r in rom if r.get("type") == "trapp") < 2:
            ut.append(f"{kode}: færre enn to trapper")

    for navn, plasser in sjakter.items():
        if len(plasser) > 1:
            ut.append(f"sjakt {navn} står på ulike steder: {sorted(plasser)}")
    return ut


# --- Dører ----------------------------------------------------------------------------------
# Rom som har lov til å ha dør rett ut (hovedinngang og kjøresluse).
DOR_UT_TILLATT = {"RES-1", "KJS-U1"}


def _dorpunkt(rom: dict) -> tuple[float, float, float, float]:
    """Punktet midt i døra og retningen ut av rommet (dx, dy)."""
    side = rom.get("dor_pos", "sor")
    langs = rom.get("dor_langs")
    if side in ("sor", "nord"):
        x = langs if langs is not None else rom["x"] + rom["w"] / 2
        return (x, rom["y"] + rom["h"], 0, 1) if side == "sor" else (x, rom["y"], 0, -1)
    y = langs if langs is not None else rom["y"] + rom["h"] / 2
    return (rom["x"] + rom["w"], y, 1, 0) if side == "ost" else (rom["x"], y, -1, 0)


def dor_mot(rom: dict, rom_i_etasjen: list[dict]) -> str | None:
    """ID-en til rommet døra åpner mot, «UTE» for yttervegg, None hvis ingenting."""
    x, y, dx, dy = _dorpunkt(rom)
    for steg in (1, 3, 5, 7):  # inntil 0,7 m: krysser også fasadeveggen (0,4 m) mellom fløyene
        px, py = x + dx * steg, y + dy * steg
        for andre in rom_i_etasjen:
            if andre is not rom and andre["x"] < px < andre["x"] + andre["w"] and andre["y"] < py < andre["y"] + andre["h"]:
                return andre["id"]
    return "UTE"


def dorfeil(modell: dict) -> list[str]:
    """Dører som åpner inn i en heissjakt eller rett ut, uten at rommet har lov til det."""
    ut = []
    for etasje in modell["etasjer"]:
        rom = etasje["rom"]
        typer = {r["id"]: r.get("type") for r in rom}
        for r in rom:
            mot = dor_mot(r, rom)
            if mot == "UTE" and r["id"] not in DOR_UT_TILLATT:
                ut.append(f"{etasje['kode']}: døra i {r['id']} går rett ut i yttervegg")
            elif mot != "UTE" and typer.get(mot) == "heis" and r.get("type") != "heis":
                ut.append(f"{etasje['kode']}: døra i {r['id']} går inn i heissjakta {mot}")
    return ut
