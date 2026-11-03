"""Syntetisk HR- og HMS-pakke for Kunstpixel, 2010 til 2026.

Alt lages av koden med fast frø, så pakken er identisk hver gang. Totalene henger sammen med historikken i
`leveranse._H` (årsverk, sykefravær, RUH, skader, tilsyn, avvik, vernerunder, temperaturavvik). Ansattregisteret er de
samme (syntetiske) personene som hr_ansatte, og alle e-poster ligger på det reserverte domenet .example.test.
Ingen modell skriver data her.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import zipfile
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from src.kunstpixel.core.intern import leveranse as L

IDAG = date(2026, 10, 27)  # siste dato i dataene. 2026 er foreløpig
AAR = L.HISTORIKK_AAR
H = L._H
KLASSE = "syntetisk"
FIL_DATO = (2026, 10, 27, 0, 0, 0)  # fast tidsstempel i zip, så filen blir lik hver gang

# Ansattregisteret er de samme personene som hr_ansatte i museum.db. Kilden er datafila museum.db bygges fra.
HR_ANSATTE_CSV = Path(__file__).resolve().parents[4] / "05_data" / "arkiv_hr_ansatte.csv"

# Stillingstittel (eller avdeling) -> nærmeste rolle i tilgangsmatrisen (L.ROLLER_TILLATT).
ROLLE_FOR_STILLING = {
    "Kvalitets- og complianceansvarlig": "Kvalitetsvokter",
    "Sikkerhetsleder / RVR": "Brannvernleder",
    "Malerikonservator NKF-N": "Konservator",
    "Papir- og fotokonservator": "Konservator",
    "Museumsvert og omviser (Deltid)": "Museumsvert",
    "Seniorvert / Skrankeleder": "Museumsvert",
    "Butikkmedarbeider (Deltid)": "Museumsvert",
    "Museumsbutikkleder": "Museumsvert",
    "Kaféleder": "Kafeansvarlig",
    "Kafémedarbeider (Deltid)": "Kafeansvarlig",
    "Kommunikasjons- og markedssjef": "Formidler",
    "Digital innholdsprodusent / Web": "Formidler",
}
ROLLE_FOR_AVDELING = {
    "Ledelse": "Museumsdirektør", "Kuratering": "Kurator", "Samling": "Samlingsforvalter",
    "Formidling": "Formidler", "Drift": "Driftsansvarlig", "Marked": "Formidler",
}
SLUTTARSAKER = ["ny jobb", "ny jobb", "pensjon", "flytting", "studier", "midlertidig utløpt"]

STEDER = ["Sal A", "Sal B", "Sal C", "Sal D", "Sal E", "Kafé", "Foajé og butikk", "Lager og verksted", "Kontor"]
KATEGORIER = {
    "fall og snubling": (18, ["Løs ledning over gulv sikret", "Gulvet merket og friksjonsmatte lagt ut", "Belysning ved trapp forbedret"]),
    "ergonomi og løft": (16, ["Løfteopplæring gjentatt for berørte", "Rullevogn innkjøpt til transport av rammer", "Arbeidsstasjon justert sammen med verneombud"]),
    "kafé og hygiene": (14, ["Rutine for håndvask gjennomgått på vaktmøte", "Utstyr rengjort og kontrollert på nytt", "Sjekkliste i kafeen oppdatert"]),
    "brann og elektrisk": (8, ["Elektriker kontrollerte anlegget", "Utstyr tatt ut av bruk til det er reparert", "Branncelle og slokkeutstyr kontrollert"]),
    "sikring og tyveri": (8, ["Adgangsrutine skjerpet", "Kamera flyttet for bedre oversikt", "Vaktrutine justert for kveldsarrangement"]),
    "publikum og trengsel": (12, ["Kø ledet om og antall personer i salen kontrollert", "Ekstra vert satt inn ved arrangement", "Skilting av rømningsvei forbedret"]),
    "psykososialt arbeidsmiljø": (6, ["Samtale med leder og tillitsvalgt gjennomført", "Oppgavefordeling gjennomgått i teamet", "Tema tatt opp i AMU"]),
    "teknisk feil": (14, ["Servicetekniker tilkalt og feilen rettet", "Reservedel bestilt og midlertidig løsning satt opp", "Vedlikeholdsplan oppdatert"]),
    "kjemikalier og renhold": (4, ["Sikkerhetsdatablad oppdatert og lagt ut", "Verneutstyr kontrollert", "Merking av beholdere rettet"]),
}  # fmt: skip
SYKEVEKT = [1.30, 1.25, 1.15, 0.95, 0.85, 0.70, 0.55, 0.65, 0.95, 1.10, 1.20, 1.15]
MND = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"]


def _ascii(s: str) -> str:
    for a, b in (("æ", "a"), ("ø", "o"), ("å", "a"), ("Æ", "A"), ("Ø", "O"), ("Å", "A"), (" ", ".")):
        s = s.replace(a, b)
    return s.lower()


def _rng(seksjon: str) -> random.Random:
    return random.Random(f"kunstpixel-{seksjon}-2010")


def ansatte() -> list[dict[str, Any]]:
    """Ansattregister: de samme personene som hr_ansatte, unntatt de som starter etter siste dato i dataene.

    Navn, stilling, avdeling, stillingsprosent og datoer kopieres. E-posten bruker samme lokale del som i
    hr_ansatte, men på det reserverte domenet .example.test (pakken skal ikke inneholde adresser som kan virke ekte).
    """
    with open(HR_ANSATTE_CSV, encoding="utf-8", newline="") as f:
        kilde = [r for r in csv.DictReader(f) if r["ansatt_fra"] <= IDAG.isoformat()]
    lokal = [r["epost"].split("@")[0] for r in kilde]
    stillinger = sorted({r["stilling"] for r in kilde})
    rng = _rng("ansatte")
    rad: list[dict[str, Any]] = []
    for r in sorted(kilde, key=lambda r: r["ansatt_id"]):
        lok = r["epost"].split("@")[0]
        if lokal.count(lok) > 1:
            lok = f"{lok}.{r['ansatt_id'].split('-')[-1]}"
        andel = round(float(r["stillingsprosent"]) * 100)
        rad.append(
            {
                "ansatt_id": r["ansatt_id"], "stilling_id": f"S-{stillinger.index(r['stilling']) + 1:02d}", "navn": r["navn"],
                "epost": f"{lok}@kunstpixel.example.test", "stillingstittel": r["stilling"],
                "rolle": ROLLE_FOR_STILLING.get(r["stilling"], ROLLE_FOR_AVDELING[r["avdeling"]]), "avdeling": r["avdeling"],
                "stillingsandel_prosent": andel, "ansettelsesform": "midlertidig" if "Sesong" in r["status"] else "fast",
                "ansatt_fra": r["ansatt_fra"], "ansatt_til": r["ansatt_til"],
                "sluttarsak": rng.choice(SLUTTARSAKER) if r["ansatt_til"] else "",
            }
        )  # fmt: skip
    return rad


def _lengst_ansatt(reg: list[dict[str, Any]], d: date, rolle: str) -> dict[str, Any] | None:
    aktive = [a for a in reg if a["rolle"] == rolle and _aktiv(a, d)]
    return min(aktive, key=lambda a: (a["ansatt_fra"], a["ansatt_id"])) if aktive else None


def _aktiv(a: dict[str, Any], d: date) -> bool:
    return date.fromisoformat(a["ansatt_fra"]) <= d and (not a["ansatt_til"] or d <= date.fromisoformat(a["ansatt_til"]))


def _slutt(ar: int) -> date:
    return min(date(ar, 12, 31), IDAG)


def aarsverk_ved_aarsslutt(reg: list[dict[str, Any]], ar: int) -> float:
    return sum(a["stillingsandel_prosent"] for a in reg if _aktiv(a, _slutt(ar))) / 100


def _status(ar: int) -> str:
    return "foreløpig" if ar == AAR[-1] else "endelig"


# ---------------------------------------------------------------- tabellene


def hr_nokkeltall(reg: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = _rng("hr")
    ut = []
    for i, ar in enumerate(AAR):
        slutt = sum(_aktiv(a, _slutt(ar)) for a in reg)
        start = sum(_aktiv(a, date(ar - 1, 12, 31)) for a in reg) if ar > AAR[0] else slutt  # årsstart = forrige årsslutt
        nye = sum(a["ansatt_fra"].startswith(str(ar)) and a["ansatt_fra"] > f"{AAR[0]}-01-01" for a in reg)  # de som var med fra oppstart er ikke nyansatte
        gaar = sum(a["ansatt_til"].startswith(str(ar)) for a in reg)
        ut.append(
            {
                "ar": ar, "status_ar": _status(ar), "ansatte_arsverk": H["ansatte_arsverk"][i], "hoder_1_1": start, "hoder_31_12": slutt,
                "nyansatte": nye, "avganger": gaar, "turnover_prosent": round(100 * gaar / ((start + slutt) / 2), 1),
                "overtid_timer": H["arrangementer_antall"][i] * 9 + rng.randint(0, 24),
                "permisjoner_antall": rng.randint(0, 2), "medarbeidersamtaler_gjennomfort_prosent": {2020: 82, 2021: 91}.get(ar, 100),
                "kursdager_per_ansatt": round(1.5 + rng.random() * 1.5, 1), "sykefravaer_prosent": H["sykefravaer_prosent"][i],
                "skader_med_fravaer": H["skader_med_fravaer"][i],
            }
        )  # fmt: skip
    return ut


def sykefravaer_aar(reg: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = _rng("syk")
    ut = []
    for i, ar in enumerate(AAR):
        p, ars = H["sykefravaer_prosent"][i], H["ansatte_arsverk"][i]
        dager = round(p / 100 * ars * 225)
        ut.append(
            {
                "ar": ar, "status_ar": _status(ar), "sykefravaer_prosent": p, "sykedager_totalt": dager,
                "egenmeldt_andel_prosent": rng.randint(24, 36), "langtidssaker_over_16_dager": max(1, round(p / 2.2 + rng.random())),
            }
        )  # fmt: skip
    return ut


def sykefravaer_maned() -> list[dict[str, Any]]:
    ut = []
    for i, ar in enumerate(AAR):
        n = 9 if ar == AAR[-1] else 12  # 2026 har bare fullførte måneder til og med september
        vekt = list(SYKEVEKT[:n])
        if ar == 2020:
            vekt[2] *= 1.5
            vekt[3] *= 1.4
        if ar == 2021:
            for m in (0, 1):
                vekt[m] *= 1.3
        snitt = sum(vekt) / n
        for m in range(n):
            ut.append({"ar": ar, "maned": m + 1, "maned_navn": MND[m], "sykefravaer_prosent": round(H["sykefravaer_prosent"][i] * vekt[m] / snitt, 1)})
    return ut


def ruh(reg: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Interne avviksmeldinger. Antall per år og personskader med fravær følger historikken."""
    rng = _rng("ruh")
    ut: list[dict[str, Any]] = []
    for i, ar in enumerate(AAR):
        n, skader = H["ruh_registrert"][i], H["skader_med_fravaer"][i]
        slutt = _slutt(ar)
        dager = sorted(date(ar, 1, 1) + timedelta(days=rng.randrange((slutt - date(ar, 1, 1)).days + 1)) for _ in range(n))
        kats = rng.choices(list(KATEGORIER), weights=[v[0] for v in KATEGORIER.values()], k=n)
        for s in rng.sample(range(n), skader):
            kats[s] = "personskade"
        roder = max(0, n // 12)
        rader = []
        for j, (d, kat) in enumerate(zip(dager, kats), 1):
            if kat == "personskade":
                fravaer = rng.randint(3, 21)
                alvor = "rød" if fravaer >= 14 else "gul"
                tiltak = "Skaden fulgt opp med leder og verneombud, og arbeidsplassen vurdert på nytt"
            else:
                fravaer, alvor = 0, rng.choices(["grønn", "gul", "rød"], weights=[72, 24, 4])[0]
                tiltak = rng.choice(KATEGORIER[kat][1])
            if alvor == "rød" and roder <= 0:
                alvor = "gul"
            roder -= alvor == "rød"
            frist = {"grønn": 0, "gul": 14, "rød": 1}[alvor]
            if alvor == "grønn":
                tid = rng.randint(1, 14)
            elif alvor == "gul":
                tid = rng.randint(2, 14) if rng.random() < 0.92 else rng.randint(15, 25)
            else:
                tid = 1 if rng.random() < 0.9 else rng.randint(2, 3)
            lukket = d + timedelta(days=tid)
            aktive = [a for a in reg if _aktiv(a, d)]
            melder = rng.choice(aktive)
            rader.append(
                {
                    "ruh_id": f"RUH-{ar}-{j:03d}", "dato": d.isoformat(), "kategori": kat, "alvorlighet": alvor, "sted": rng.choice(STEDER),
                    "melder_id": melder["ansatt_id"], "melder_rolle": melder["rolle"], "fravaersdager": fravaer,
                    "frist_dager": frist if alvor != "grønn" else "", "status": "lukket" if lukket <= IDAG else "åpen",
                    "lukket_dato": lukket.isoformat() if lukket <= IDAG else "",
                    "lukket_innen_frist": ("ja" if (alvor == "grønn" or tid <= frist) else "nei") if lukket <= IDAG else "",
                    "tiltak": tiltak,
                }
            )  # fmt: skip
        ut += rader
    return ut


def tilsyn() -> list[dict[str, Any]]:
    rng = _rng("tilsyn")
    syklus = [("Mattilsynet", "varslet tilsyn"), ("Brann- og redningsetaten", "brannsyn"), ("Arbeidstilsynet", "varslet tilsyn"),
              ("Mattilsynet", "uvarslet besøk"), ("Arbeidstilsynet", "oppfølging av avvik"), ("Brann- og redningsetaten", "brannsyn")]  # fmt: skip
    id_for = {n: i for i, n, _, _ in L.MYNDIGHETER}
    ut = []
    for i, ar in enumerate(AAR):
        n, funn, innen, palegg = H["tilsyn_antall"][i], H["avvik_funnet"][i], H["avvik_lukket_innen_frist"][i], H["palegg_antall"][i]
        vindu = (_slutt(ar) - date(ar, 2, 1)).days if ar == AAR[-1] else (date(ar, 11, 30) - date(ar, 2, 1)).days
        per_rad = [funn // n + (1 if k < funn % n else 0) for k in range(n)]
        igjen, pl = innen, palegg
        for k in range(n):
            mynd, type_ = syklus[k % len(syklus)]
            d = date(ar, 2, 1) + timedelta(days=int(vindu * (k + 0.5) / n) + rng.randint(-5, 5) * (ar != AAR[-1]))
            lukket = min(per_rad[k], igjen)
            igjen -= lukket
            pal = 1 if pl > 0 and per_rad[k] > 0 else 0
            pl -= pal
            mid = id_for[mynd]
            ut.append(
                {
                    "tilsyn_id": f"TIL-{ar}-{k + 1:02d}", "dato": min(d, IDAG).isoformat(), "myndighet": mynd, "myndighet_id": mid, "type": type_,
                    "kontaktperson": L.KONTAKTPERSONER[mid][0], "avvik_funnet": per_rad[k], "avvik_lukket_innen_frist": lukket, "palegg": pal,
                    "resultat": "uten avvik" if per_rad[k] == 0 else ("avvik og pålegg" if pal else ("avvik, alle lukket innen frist" if lukket == per_rad[k] else "avvik, noen lukket etter frist")),
                }
            )  # fmt: skip
    return ut


def vernerunder(reg: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = _rng("verne")
    maler = [(3, 12), (6, 4), (9, 17), (11, 26)]
    omr = ["Sal A og B", "Sal C og D", "Kafé og kjøkken", "Lager, verksted og kontor", "Sal E og foajé"]
    ut = []
    for i, ar in enumerate(AAR):
        for k in range(H["vernerunder_gjennomfort"][i]):
            m, dag = (10, 20) if (ar == AAR[-1] and k == 3) else maler[k]
            funn = rng.randint(2, 7)
            ut.append(
                {
                    "runde_id": f"VR-{ar}-{k + 1}", "dato": date(ar, m, dag).isoformat(), "omrade": omr[(k + i) % len(omr)],
                    "deltakere": "Verneombud, Driftsansvarlig, Museumsdirektør", "funn_antall": funn,
                    "funn_lukket": funn - (1 if (ar == AAR[-1] and k == 3) else 0),
                }
            )  # fmt: skip
    return ut


def temperaturavvik() -> list[dict[str, Any]]:
    rng = _rng("temp")
    utstyr = [("kjøleskap", "maks +4 °C", 4.0, 6.5, 9.5), ("fryser", "maks -18 °C", -18.0, -14.0, -10.0), ("varmholding", "minimum +60 °C", 60.0, 52.0, 58.0)]
    ut = []
    for i, ar in enumerate(AAR):
        aar_rader = []
        for _ in range(H["ik_mat_temperaturavvik"][i]):
            navn, krav, _grense, lo, hi = utstyr[rng.choices([0, 1, 2], weights=[60, 15, 25])[0]]
            d = date(ar, 1, 1) + timedelta(days=rng.randrange((_slutt(ar) - date(ar, 1, 1)).days + 1))
            malt, timer = round(rng.uniform(lo, hi), 1), rng.randint(1, 5)
            kassert = (navn == "kjøleskap" and malt > 8 and timer > 2) or (navn == "varmholding" and timer > 2)
            aar_rader.append(
                {
                    "dato": d.isoformat(), "utstyr": navn, "krav": krav, "malt_celsius": malt,
                    "varighet_timer": timer, "varer_kassert": "ja" if kassert else "nei",
                    "tiltak": "Varer kassert og servicetekniker tilkalt" if kassert else "Temperatur justert og kontrollert på nytt",
                }
            )  # fmt: skip
        for k, r in enumerate(sorted(aar_rader, key=lambda r: r["dato"]), 1):
            ut.append({"avvik_id": f"TEMP-{ar}-{k:02d}", **r})
    return ut


def opplaering(reg: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = _rng("kurs")
    ut = []
    for ar in AAR:
        slutt = _slutt(ar)
        akt = [a for a in reg if _aktiv(a, slutt)]
        grupper = [
            ("Brannvern", True, len(akt)), ("Varslingsrutiner", True, len(akt)),
            ("HLR og førstehjelp", ar % 2 == 0 and ar != 2020, len(akt)),
            ("Løfteteknikk", (ar - 2010) % 3 == 0, sum(a["rolle"] in ("Museumsvert", "Driftsansvarlig", "Konservator") for a in akt)),
            ("IK-Mat", True, sum(a["rolle"] == "Kafeansvarlig" for a in akt)),
        ]  # fmt: skip
        for kurs, holdt, maal in grupper:
            delt = maal - (1 if rng.random() < 0.2 and maal >= 6 else 0) if holdt else 0
            ut.append({"ar": ar, "kurs": kurs, "gjennomfort": "ja" if holdt else "nei", "malgruppe_antall": maal, "deltakere": delt, "dekning_prosent": round(100 * delt / maal) if holdt and maal else 0})
    return ut


def brannovelser(reg: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = _rng("brann")
    ut = []
    for i, ar in enumerate(AAR):
        for k, (m, dag) in enumerate([(4, 15), (10, 7)][: 1 if ar == 2020 else 2]):
            ut.append(
                {
                    "ovelse_id": f"BO-{ar}-{k + 1}", "dato": date(ar, m, dag).isoformat(), "type": "evakuering uten varsel" if k else "planlagt evakuering",
                    "evakueringstid_sekunder": 420 - (ar - 2010) * 11 + rng.randint(-12, 12),
                    "deltakere_ansatte": sum(_aktiv(a, date(ar, m, dag)) for a in reg), "merknad": rng.choice(["Ingen funn", "Rømningsvei ryddet etterpå", "Samlingsplass flyttet"]),
                }
            )  # fmt: skip
    return ut


def hms_organisering(reg: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Verneombud og brannvernleder per år: den lengst ansatte i rollen som var i jobb ved årsslutt."""
    ut = []
    for ar in AAR:
        d = _slutt(ar)
        vo = _lengst_ansatt(reg, d, "Museumsvert")
        bl = _lengst_ansatt(reg, d, "Brannvernleder") or _lengst_ansatt(reg, d, "Driftsansvarlig")
        ut.append(
            {"ar": ar, "verneombud_id": vo["ansatt_id"], "brannvernleder_id": bl["ansatt_id"], "amu_moter": 3 if ar == 2020 else 4,
             "hms_handlingsplan_godkjent": date(ar, 1, 20).isoformat()}
        )  # fmt: skip
    return ut


def tabeller() -> dict[str, list[dict[str, Any]]]:
    reg = ansatte()
    return {
        "ansatte.csv": reg, "hr_nokkeltall_per_ar.csv": hr_nokkeltall(reg), "sykefravaer_per_ar.csv": sykefravaer_aar(reg),
        "sykefravaer_per_maned.csv": sykefravaer_maned(), "ruh_avviksmeldinger.csv": ruh(reg), "tilsyn.csv": tilsyn(),
        "vernerunder.csv": vernerunder(reg), "temperaturavvik_kafe.csv": temperaturavvik(), "opplaering.csv": opplaering(reg),
        "brannovelser.csv": brannovelser(reg), "hms_organisering.csv": hms_organisering(reg),
    }  # fmt: skip


def csv_bytes(rader: list[dict[str, Any]]) -> bytes:
    ut = io.StringIO()
    felt = list(rader[0]) + ["klassifisering"]
    w = csv.DictWriter(ut, fieldnames=felt, delimiter=";", lineterminator="\n")
    w.writeheader()
    for r in rader:
        w.writerow({**r, "klassifisering": KLASSE})
    return b"\xef\xbb\xbf" + ut.getvalue().encode("utf-8")  # BOM, så norsk Excel åpner æøå riktig


README = """# HR- og HMS-data for Kunstpixel, 2010 til 2026

Alt er **syntetisk** (klassifisering `syntetisk` i hver rad). Personene er de samme som i `hr_ansatte`
(også syntetiske, ansatt-ID `KP-ANS-…`), og e-postene ligger på `.example.test`. Navn kan gå igjen, så bruk ansatt-ID som nøkkel. Dataene passer til historikken i `historikk_tall.yaml`: samme årsverk, sykefravær, antall RUH,
skader, tilsyn, avvik, pålegg, vernerunder og temperaturavvik. 2026 er foreløpig og går til og med 2026-10-27.

Filformat: UTF-8 med BOM, semikolon som skilletegn, datoer som ÅÅÅÅ-MM-DD. Excel på norsk åpner dem direkte.

| Fil | Innhold |
|---|---|
| ansatte.csv | Ansattregister: person, stilling, rolle, stillingsandel, fra og til dato |
| hr_nokkeltall_per_ar.csv | Årsverk, hoder, nyansatte, avganger, turnover, overtid, permisjon, medarbeidersamtaler |
| sykefravaer_per_ar.csv | Sykefravær i prosent, sykedager, egenmeldt andel, langtidssaker |
| sykefravaer_per_maned.csv | Samme per måned med sesong og pandemitopper (2020 og 2021) |
| ruh_avviksmeldinger.csv | Interne avviksmeldinger med kategori, alvorlighet, frist og lukking |
| tilsyn.csv | Tilsyn og brannsyn med avvik, avvik lukket innen frist og pålegg |
| vernerunder.csv | Vernerunder med funn og lukking |
| temperaturavvik_kafe.csv | Temperaturavvik i kafeen mot kravene i IK-Mat |
| opplaering.csv | Kurs per år med målgruppe, deltakere og dekning |
| brannovelser.csv | Brannøvelser med evakueringstid |
| hms_organisering.csv | Verneombud, brannvernleder og AMU-møter per år |

Kolonnen `rolle` i ansatte.csv er nærmeste rolle i tilgangsmatrisen, ikke stillingstittelen.
Gule avvik skal lukkes innen 14 dager og røde innen 24 timer (som i hms_arbeidsmiljo.yaml).
Dataene er laget for trening og demo. De er ikke rettesnor og skal aldri blandes med ekte HR-data.
"""


def pakke() -> dict[str, bytes]:
    tab = tabeller()
    filer = {n: csv_bytes(r) for n, r in tab.items()}
    manifest = {
        "klassifisering": KLASSE, "periode": "2010-2026", "til_og_med": IDAG.isoformat(),
        "filer": {n: {"rader": len(tab[n]), "sha256": hashlib.sha256(b).hexdigest()} for n, b in filer.items()},
    }  # fmt: skip
    filer["README.md"] = README.encode("utf-8")
    filer["MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    return filer


def zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for navn, data in sorted(pakke().items()):
            info = zipfile.ZipInfo(navn, FIL_DATO)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    return buf.getvalue()
