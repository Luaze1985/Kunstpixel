"""Lag syntetiske medarbeidersamtaler (vurdering og erfaring) for ansatte i Kunstpixel.

Leser 05_data/arkiv_hr_ansatte.csv og skriver 05_data/arkiv_hr_medarbeidersamtaler.csv.
Én samtale per ansatt som var ansatt 1. oktober i 2025 og 2026. Fast seed: samme fil hver gang.
Alt er syntetisk og merket «syntetisk (medarbeidersamtaler_2026)».

    py -3.13 src/kunstpixel/data/lag_medarbeidersamtaler.py
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANSATTE = ROOT / "05_data" / "arkiv_hr_ansatte.csv"
UT = ROOT / "05_data" / "arkiv_hr_medarbeidersamtaler.csv"
SEED = 20261031
AAR = (2025, 2026)
DATAKILDE = "syntetisk (medarbeidersamtaler_2026)"
VURDERINGER = ["Overgår", "Innfrir", "Delvis", "Under"]
VEKTER = [18, 60, 18, 4]  # de fleste innfrir

LEDER = {"Ledelse": "Styreleder", "Drift": "Driftsansvarlig"}

# Tekster per type stilling: (styrker, utviklingsområder, erfaring)
TEKSTER = {
    "sikkerhet": (
        ["Rolig og tydelig i hendelser", "God på adgangskontroll og rutiner", "Følger opp avvik raskt", "Trygg på brann- og evakueringsrutiner"],
        ["Dokumentere avvik grundigere", "Fornye førstehjelpskurs i tide", "Bedre overlevering ved vaktskifte"],
        ["Har stått vakt i vaktrommet ved vernissasjer", "Har ledet evakueringsøvelse", "Erfaring fra kveldsarrangementer med mange gjester"],
    ),
    "publikum": (
        ["Varm og imøtekommende mot publikum", "Gode omvisninger for skoleklasser", "Løser klager uten å eskalere", "God på flere språk"],
        ["Holde seg oppdatert på nye utstillinger", "Si fra tidligere om behov for avløsning", "Bruke kassasystemet sikrere"],
        ["Har dekket flere saler på travle helger", "Har hatt omvisninger på engelsk og tysk", "Erfaring fra familiedager og ferieaktiviteter"],
    ),
    "kafe": (
        ["Rask og ryddig i kaféen", "God kontroll på allergener", "Holder orden på IK-mat-rutinene"],
        ["Planlegge varebestilling bedre", "Lære opp nyansatte i kassen"],
        ["Har drevet kaféen alene på stille dager", "Erfaring fra catering ved arrangementer"],
    ),
    "fag": (
        ["Sterk faglig kunnskap", "Gode tekster og formidling", "Nøyaktig med registrering og dokumentasjon"],
        ["Dele kunnskap mer med publikumsvertene", "Prioritere bedre mellom prosjekter"],
        ["Har bidratt til flere utstillinger", "Erfaring med innlån fra andre museer"],
    ),
    "teknisk": (
        ["Løser tekniske feil raskt", "God på lys og AV ved arrangementer", "Planlegger monteringer godt"],
        ["Melde fra om feil i systemet tidligere", "Skrive bedre sjekklister"],
        ["Har rigget flere utstillinger", "Erfaring med kveldsarrangementer og konserter"],
    ),
    "annet": (
        ["Pålitelig og punktlig", "God samarbeidspartner", "Tar ansvar for egne oppgaver"],
        ["Si fra tidligere om kapasitet", "Bli tryggere i møter med publikum"],
        ["Har dekket vakter ved behov", "Kjenner museets rutiner godt"],
    ),
}


def _type(stilling: str) -> str:
    s = stilling.lower()
    if any(o in s for o in ("vekter", "sikkerhet", "vakt")):
        return "sikkerhet"
    if any(o in s for o in ("vert", "omvis", "pedagog", "formidl", "resepsjon", "skranke", "butikk")):
        return "publikum"
    if "kaf" in s:
        return "kafe"
    if any(o in s for o in ("kurator", "konservator", "registrar", "samling", "forsk")):
        return "fag"
    if any(o in s for o in ("tekniker", "montør", "av-", "lys", "bygg")):
        return "teknisk"
    return "annet"


def lag(ansatte: list[dict[str, str]]) -> list[dict[str, str]]:
    rng = random.Random(SEED)
    rader: list[dict[str, str]] = []
    for aar in AAR:
        frist = f"{aar}-10-01"
        for a in sorted(ansatte, key=lambda r: r["ansatt_id"]):
            if a["ansatt_fra"] > frist or (a["ansatt_til"] and a["ansatt_til"] < frist):
                continue
            styrker, utvikling, erfaring = TEKSTER[_type(a["stilling"])]
            rader.append({
                "samtale_id": f"MS-{aar}-{len([r for r in rader if r['samtale_id'].startswith(f'MS-{aar}')]) + 1:03d}",
                "ansatt_id": a["ansatt_id"],
                "dato": f"{aar}-10-{rng.randint(5, 30):02d}",
                "leder_rolle": LEDER.get(a["avdeling"], f"Avdelingsleder {a['avdeling']}"),
                "samlet_vurdering": rng.choices(VURDERINGER, weights=VEKTER)[0],
                "styrker": "; ".join(rng.sample(styrker, 2)),
                "utviklingsomrade": rng.choice(utvikling),
                "erfaring_notat": rng.choice(erfaring),
                "onsker_flere_helgevakter": rng.choice(["ja", "nei", "nei"]),
                "datakilde": DATAKILDE,
            })
    return rader


def main() -> None:
    with ANSATTE.open(encoding="utf-8") as f:
        ansatte = list(csv.DictReader(f))
    rader = lag(ansatte)
    with UT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rader[0]), quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writeheader()
        w.writerows(rader)
    print(f"Skrev {len(rader)} samtaler til {UT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
