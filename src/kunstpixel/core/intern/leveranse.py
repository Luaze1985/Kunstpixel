"""Bestilling og kontroll av syntetisk fyll (H5) laget av en annen språkmodell.

Arbeidsmåten gjør leveransen kontrollerbar:
1. Vi lager et SKJELETT per fil der alle faste felt (id-er, navn, roller, tall, valg) er ferdig utfylt.
   Den andre modellen skriver bare fritekst der det står TODO_FYLL.
2. Kontrollen sammenligner leveransen med skjelettet. Faste felt må være uendret. Fritekst må oppfylle
   skrivereglene (ingen tall, personnavn, kontaktdetaljer, paragrafer, KI-snakk eller kopierte setninger).
3. Feil blir en retteliste som kan limes rett tilbake til modellen. Maks tre runder, deretter menneske.
4. Ingenting installeres i datamappen uten at et menneske ber om det, og bare filer som består kontrollen.

Kontrollen er regex og struktur, ikke en modell. Den kan ikke avgjøre om en setning er faglig god. Det er menneskets jobb.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PLASSHOLDER = "TODO_FYLL"
MAX_FILSTORRELSE = 200_000  # byte. Større filer avvises før de leses som YAML.
MAX_YAML_HENDELSER = 20_000


class _DuplikatNokkel(yaml.YAMLError):
    pass


class _StrengLoader(yaml.SafeLoader):
    """SafeLoader som nekter duplikate nøkler (ellers vinner den siste i stillhet og skjuler felt)."""

    def construct_mapping(self, node, deep=False):  # type: ignore[override]
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=True)
            if key in seen:
                raise _DuplikatNokkel(f"Nøkkelen {key!r} står flere ganger. Hvert felt skal bare stå én gang")
            seen.add(key)
        return super().construct_mapping(node, deep)

FILER: dict[str, str] = {
    "A": "myndighetskontakter.yaml",
    "B": "tilsynsbesok_rutine.yaml",
    "C": "rapporteringskalender.yaml",
    "D": "rapportmaler.yaml",
    "E": "arbeidsoppgaver_tidsbruk.yaml",
    "F": "historikk_tekst.yaml",
}
NAVN: dict[str, str] = {
    "A": "Myndighetskontakter",
    "B": "Tilsynsbesøk",
    "C": "Rapporteringskalender",
    "D": "Rapportmaler",
    "E": "Arbeidsoppgaver og tidsbruk",
    "F": "Historikk, tekst per år",
}
# Filer som lages av koden og aldri av en modell. Kontrolleres mot koden, byte for byte i innhold.
GENERERT_FIL: dict[str, str] = {"T": "historikk_tall.yaml"}
FILNAVN: dict[str, str] = {**FILER, **GENERERT_FIL}

HEADER: dict[str, Any] = {
    "klassifisering": "syntetisk",
    "syntetisk": True,
    "merknad": "Treningsdata, ikke rettesnor. Alle frister, terskler og timer er oppdiktet.",
    "versjon": 1,
}

ROLLER_TILLATT = (
    "Museumsdirektør", "Samlingsforvalter", "Kurator", "Formidler", "Museumsvert", "Driftsansvarlig",
    "Kvalitetsvokter", "Kafeansvarlig", "Verneombud", "Brannvernleder", "Konservator", "Styret",
)  # fmt: skip
KILDER_TILLATT = (
    "besøkstall", "utstillinger", "regnskap", "hendelser", "avviksregister", "temperaturlogg", "vernerunder",
    "samlingsdatabase", "brannøvelser", "innlån", "styrereferat", "driftslogg", "manuell",
)  # fmt: skip

# ---------------------------------------------------------------- faste tabeller (én kilde til sannhet)

MYNDIGHETER = [
    ("MK-01", "Arbeidstilsynet", "HMS og arbeidsmiljø", "Museumsdirektør"),
    ("MK-02", "Mattilsynet", "Kafé og IK-Mat", "Kafeansvarlig"),
    ("MK-03", "Brann- og redningsetaten", "Brannsikkerhet og beredskap", "Driftsansvarlig"),
    ("MK-04", "Kommunen", "Skjenke- og serveringsbevilling", "Kafeansvarlig"),
    ("MK-05", "Fylkeskommunen", "Tilskudd og regionalt kulturarbeid", "Museumsdirektør"),
    ("MK-06", "Kulturdirektoratet", "Museumsstatistikk, tilskudd og samlingsforvaltning", "Museumsdirektør"),
    ("MK-07", "Datatilsynet", "Personvern", "Driftsansvarlig"),
    ("MK-08", "Stiftelsestilsynet", "Årsregnskap og tilsyn med stiftelsen", "Museumsdirektør"),
]

# Oppdiktede personer og adresser på det reserverte domenet .test (RFC 2606), så de aldri kan peke på ekte mennesker.
# De lages av koden og er faste felt. Modellen skriver aldri navn eller e-post selv.
KONTAKTPERSONER = {
    "MK-01": ("Harald Oskar Vinje", "harald.oskar.vinje@arbeidstilsynet.example.test"),
    "MK-02": ("Theodor Sæther", "theodor.sather@mattilsynet.example.test"),
    "MK-03": ("Kristian Hovland", "kristian.hovland@brann.example.test"),
    "MK-04": ("Gunnar Eilif Lunde", "gunnar.eilif.lunde@kommunen.example.test"),
    "MK-05": ("Harriet Dahlen", "harriet.dahlen@fylkeskommunen.example.test"),
    "MK-06": ("Frits Strømme", "frits.stromme@kulturdirektoratet.example.test"),
    "MK-07": ("Oda Marie Skogen", "oda.marie.skogen@datatilsynet.example.test"),
    "MK-08": ("Gerhard Nygaard", "gerhard.nygaard@stiftelsestilsynet.example.test"),
}
INTERNE_PERSONER = {
    "Museumsdirektør": ("Thorvald Berntsen", "thorvald.berntsen@kunstpixel.example.test"),
    "Kafeansvarlig": ("Astrid Moe", "astrid.moe@kunstpixel.example.test"),
    "Driftsansvarlig": ("Edvard Rønning", "edvard.ronning@kunstpixel.example.test"),
}

AVVIK_FRISTER = {"gult_avvik_lukkes_innen": "14 dager", "rodt_avvik_lukkes_innen": "24 timer"}  # samme som hms_arbeidsmiljo.yaml

TILSYNSSTEG = [
    (1, "Varsel kommer", "Driftsansvarlig"),
    (2, "Samle dokumentasjon", "Driftsansvarlig"),
    (3, "Under besøket", "Museumsdirektør"),
    (4, "Tilbakemelding", "Museumsdirektør"),
    (5, "Skriftlig svar", "Museumsdirektør"),
    (6, "Lukke avvik", "Driftsansvarlig"),
]

# id, rapport, mottaker, mottakertype, frekvens, antall_per_ar, maned, eier, timer_per_gang, godkjenning, potensial
RAPPORTER = [
    ("RP-01", "Månedlig driftsrapport", "Museumsdirektør", "intern", "månedlig", 12, "Månedlig", "Driftsansvarlig", 2, "ingen", "Høy"),
    ("RP-02", "Besøkstall og statistikk", "Kulturdirektoratet", "ekstern", "årlig", 1, "Mars", "Driftsansvarlig", 14, "eier", "Høy"),
    ("RP-03", "Tilskuddsrapport", "Kulturdirektoratet", "ekstern", "årlig", 1, "Mars", "Museumsdirektør", 36, "eier", "Middels"),
    ("RP-04", "Årsregnskap og årsberetning", "Stiftelsestilsynet", "ekstern", "årlig", 1, "Juni", "Museumsdirektør", 24, "eier", "Lav"),
    ("RP-05", "HMS-årsrapport", "Styret", "intern", "årlig", 1, "Januar", "Museumsdirektør", 10, "ingen", "Høy"),
    ("RP-06", "Avviksrapport", "Internt arkiv", "intern", "løpende", 10, "Løpende", "Driftsansvarlig", 2, "ingen", "Høy"),
    ("RP-07", "IK-Mat-sammenstilling", "Internt arkiv", "intern", "månedlig", 12, "Månedlig", "Kafeansvarlig", 1.5, "ingen", "Høy"),
    ("RP-08", "Vernerundeprotokoll", "Verneombud", "intern", "kvartalsvis", 4, "Kvartalsvis", "Driftsansvarlig", 1, "ingen", "Middels"),
    ("RP-09", "Tilstandsrapport samling", "Museumsdirektør", "intern", "årlig", 1, "November", "Samlingsforvalter", 6, "ingen", "Middels"),
    ("RP-10", "Brannøvelsesrapport", "Internt arkiv", "intern", "årlig", 1, "Mars", "Driftsansvarlig", 3, "ingen", "Høy"),
    ("RP-11", "Innlånsoversikt", "Museumsdirektør", "intern", "årlig", 1, "Desember", "Samlingsforvalter", 4, "ingen", "Høy"),
    ("RP-12", "Styrerapport", "Styret", "intern", "kvartalsvis", 4, "Kvartalsvis", "Museumsdirektør", 3, "ingen", "Middels"),
]  # fmt: skip

# id, rapport, brukes_til, godkjenning, felt (faste navn)
MALER = [
    ("ML-01", "Driftsrapport", ["RP-01"], "ingen", ["Periode", "Gjennomførte arrangementer", "Kommende arrangementer", "Avvik og tiltak", "Vedlikehold"]),
    ("ML-02", "Avviksrapport", ["RP-06"], "ingen", ["Hva skjedde", "Når og hvor", "Alvorlighetsgrad", "Umiddelbart tiltak", "Varig tiltak", "Frist for lukking"]),
    ("ML-03", "Tilskuddsrapport", ["RP-02", "RP-03"], "eier", ["Periode", "Besøkstall", "Gjennomførte aktiviteter", "Utstillinger", "Måloppnåelse"]),
    ("ML-04", "Svar til tilsyn", ["Tilsynsbesøk steg 5"], "eier", ["Saksreferanse", "Kort oppsummering", "Funn og vår vurdering", "Tiltak med frist", "Ansvarlig rolle"]),
]

# id, oppgave, myndighet, rolle, timer_per_ar, potensial
MYNDIGHETSOPPGAVER = [
    ("AO-01", "Tilskuddssøknad", "Kulturdirektoratet", "Museumsdirektør", 40, "Middels"),
    ("AO-02", "Følge opp avvik og pålegg", "Flere", "Driftsansvarlig", 20, "Middels"),
    ("AO-03", "Forberede tilsyn fra Arbeidstilsynet", "Arbeidstilsynet", "Museumsdirektør", 16, "Høy"),
    ("AO-04", "Forberede tilsyn fra Mattilsynet", "Mattilsynet", "Kafeansvarlig", 12, "Høy"),
    ("AO-05", "Forberede brannøvelse og brannsyn", "Brann- og redningsetaten", "Driftsansvarlig", 10, "Høy"),
    ("AO-06", "Fornye skjenkebevilling", "Kommunen", "Kafeansvarlig", 8, "Lav"),
    ("AO-07", "Svare på personvernhenvendelser", "Datatilsynet", "Driftsansvarlig", 6, "Lav"),
]


def timer_per_ar(r: tuple) -> float:
    return r[5] * r[8]


def summer() -> dict[str, int]:
    m = sum(o[4] for o in MYNDIGHETSOPPGAVER)
    r = sum(timer_per_ar(x) for x in RAPPORTER)
    return {"myndighetskontakt": int(m), "rapportering": int(r), "totalt": int(m + r)}


# ---------------------------------------------------------------- skjelett


# ---------------------------------------------------------------- historikk 2010 til 2026
# Tallene lages her, ikke av en modell. Seriene er skrevet ut og avledede tall regnes ut, så alt henger sammen.

HISTORIKK_AAR = list(range(2010, 2027))
HISTORIKK_TEMA = [
    "oppstart", "vekst", "vekst", "vekst", "digital samlingsdatabase", "vekst", "ombygging", "ny kafé", "vekst",
    "rekordår", "pandemi og stengt", "pandemi og gjenåpning", "gjenoppbygging", "digital satsing",
    "nye rapporteringsrutiner", "første automatisering", "KI-pilot",
]  # fmt: skip
_H: dict[str, list[Any]] = {
    "besok_totalt": [21400, 23100, 24800, 26200, 28900, 30500, 29800, 33600, 36200, 38400, 11200, 15900, 31200, 35400, 37900, 39800, 41200],
    "betalende_andel_prosent": [72, 72, 71, 71, 70, 70, 69, 69, 68, 68, 66, 66, 67, 67, 68, 68, 69],
    "skoleelever": [3100, 3300, 3600, 3900, 4200, 4600, 4400, 4900, 5200, 5600, 900, 1500, 4300, 5000, 5400, 5700, 5900],
    "arrangementer_antall": [14, 16, 18, 21, 24, 27, 25, 29, 32, 35, 8, 14, 31, 36, 39, 41, 43],
    "utstillinger_antall": [2, 2, 3, 3, 3, 3, 2, 3, 3, 3, 1, 2, 3, 3, 3, 3, 2],
    "ansatte_arsverk": [6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.0, 9.5, 10.0, 10.5, 10.0, 9.5, 10.0, 10.5, 11.0, 11.0, 11.5],
    "snittpris_kr": [48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 66, 68, 72, 76, 80, 84, 88],
    "tilskudd_tkr": [4100, 4300, 4600, 4900, 5200, 5400, 5500, 5800, 6100, 6400, 6900, 7200, 7000, 7300, 7600, 7900, 8100],
    "kafeinntekter_tkr": [820, 900, 980, 1040, 1130, 1200, 1150, 1290, 1400, 1480, 380, 560, 1250, 1420, 1560, 1650, 1720],
    "andre_inntekter_tkr": [260, 280, 310, 340, 380, 410, 390, 450, 500, 540, 140, 210, 480, 560, 610, 650, 690],
    "resultat_tkr": [120, 150, 90, 160, 140, 210, -60, 180, 230, 310, -420, -180, 60, 140, 220, 260, 190],
    "tilsyn_antall": [2, 2, 3, 3, 3, 4, 3, 4, 4, 5, 2, 3, 4, 5, 5, 6, 6],
    "avvik_funnet": [5, 6, 7, 6, 6, 5, 5, 4, 4, 3, 2, 3, 4, 3, 3, 2, 2],
    "avvik_lukket_innen_frist": [3, 4, 6, 5, 5, 4, 5, 4, 4, 3, 2, 3, 4, 3, 3, 2, 2],
    "palegg_antall": [1, 1, 2, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    "ruh_registrert": [12, 15, 19, 22, 26, 30, 28, 34, 38, 41, 15, 22, 36, 40, 43, 45, 47],
    "skader_med_fravaer": [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "sykefravaer_prosent": [4.8, 5.1, 4.6, 5.3, 4.9, 4.5, 4.7, 4.4, 4.2, 4.0, 5.6, 5.9, 5.1, 4.6, 4.3, 4.1, 4.0],
    "ik_mat_temperaturavvik": [6, 5, 6, 4, 4, 3, 3, 3, 2, 2, 1, 2, 3, 2, 2, 2, 1],
    "vernerunder_gjennomfort": [3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 4, 4],
    "rapporter_levert": [9, 9, 10, 10, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    "rapporter_for_sent": [2, 2, 1, 2, 1, 1, 1, 1, 0, 0, 2, 1, 1, 1, 0, 0, 0],
    "tilskuddssoknader": [2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 4, 4, 4, 4, 4],
    "tilskudd_innvilget": [1, 2, 2, 2, 2, 3, 2, 3, 3, 3, 5, 4, 3, 3, 4, 3, 3],
    "timer_myndighetskontakt": [64, 68, 72, 80, 88, 94, 98, 104, 110, 118, 96, 102, 124, 128, 126, 118, 112],
    "timer_rapportering": [70, 76, 84, 92, 104, 112, 118, 126, 134, 142, 120, 128, 150, 158, 170, 176, 175],
    "automatiseringsgrad_prosent": [0] * 13 + [5, 10, 18, 25],
}  # fmt: skip
HISTORIKK_NOKKELTALL = ("besok_totalt", "resultat_tkr", "tilsyn_antall", "avvik_funnet", "timer_totalt", "automatiseringsgrad_prosent")
HISTORIKK_FORKLARING = {
    "tkr": "tusen kroner",
    "ar": "kalenderår",
    "status_ar": "endelig, eller foreløpig for inneværende år",
    "tema": "hovedtema for året",
    "betalende_andel_prosent": "andel av besøkende som betalte billett",
    "avvik_lukket_innen_frist": "avvik fra tilsyn som ble lukket innen fristen",
    "ruh_registrert": "interne avviksmeldinger (RUH)",
    "automatiseringsgrad_prosent": "andel av rapporteringstimene som er automatisert",
    "timer_totalt": "timer på myndighetskontakt og rapportering til sammen",
}


def historikk_rader() -> list[dict[str, Any]]:
    """Én rad per år 2010 til 2026 med 35 parametre. Avledede tall regnes ut her."""
    n = len(HISTORIKK_AAR)
    assert len(HISTORIKK_TEMA) == n and all(len(v) == n for v in _H.values()), "alle serier må ha ett tall per år"
    rader: list[dict[str, Any]] = []
    for i, ar in enumerate(HISTORIKK_AAR):
        g = {k: v[i] for k, v in _H.items()}
        betalende = g["besok_totalt"] * g["betalende_andel_prosent"] // 100
        billett = betalende * g["snittpris_kr"] // 1000
        inntekter = billett + g["tilskudd_tkr"] + g["kafeinntekter_tkr"] + g["andre_inntekter_tkr"]
        rader.append(
            {
                "ar": ar,
                "status_ar": "foreløpig" if ar == HISTORIKK_AAR[-1] else "endelig",
                "tema": HISTORIKK_TEMA[i],
                "besok_totalt": g["besok_totalt"],
                "betalende_andel_prosent": g["betalende_andel_prosent"],
                "betalende_besokende": betalende,
                "skoleelever": g["skoleelever"],
                "arrangementer_antall": g["arrangementer_antall"],
                "utstillinger_antall": g["utstillinger_antall"],
                "ansatte_arsverk": g["ansatte_arsverk"],
                "snittpris_kr": g["snittpris_kr"],
                "billettinntekter_tkr": billett,
                "tilskudd_tkr": g["tilskudd_tkr"],
                "kafeinntekter_tkr": g["kafeinntekter_tkr"],
                "andre_inntekter_tkr": g["andre_inntekter_tkr"],
                "inntekter_totalt_tkr": inntekter,
                "kostnader_tkr": inntekter - g["resultat_tkr"],
                "resultat_tkr": g["resultat_tkr"],
                "tilsyn_antall": g["tilsyn_antall"],
                "avvik_funnet": g["avvik_funnet"],
                "avvik_lukket_innen_frist": g["avvik_lukket_innen_frist"],
                "palegg_antall": g["palegg_antall"],
                "ruh_registrert": g["ruh_registrert"],
                "skader_med_fravaer": g["skader_med_fravaer"],
                "sykefravaer_prosent": g["sykefravaer_prosent"],
                "ik_mat_temperaturavvik": g["ik_mat_temperaturavvik"],
                "vernerunder_gjennomfort": g["vernerunder_gjennomfort"],
                "rapporter_levert": g["rapporter_levert"],
                "rapporter_for_sent": g["rapporter_for_sent"],
                "tilskuddssoknader": g["tilskuddssoknader"],
                "tilskudd_innvilget": g["tilskudd_innvilget"],
                "timer_myndighetskontakt": g["timer_myndighetskontakt"],
                "timer_rapportering": g["timer_rapportering"],
                "timer_totalt": g["timer_myndighetskontakt"] + g["timer_rapportering"],
                "automatiseringsgrad_prosent": g["automatiseringsgrad_prosent"],
            }
        )
    return rader


def _fri(beskrivelse: str, maks: int = 160) -> str:
    return f"{PLASSHOLDER} (1 setning, norsk, maks {maks} tegn, uten tall): {beskrivelse}"


def _kilder() -> str:
    return f"{PLASSHOLDER}_KILDER (2 eller 3 av: {', '.join(KILDER_TILLATT)})"


def _liste(beskrivelse: str) -> str:
    return f"{PLASSHOLDER}_LISTE (2 eller 3 korte regler, uten tall): {beskrivelse}"


def skjelett(kode: str) -> dict[str, Any]:
    """Faste felt er ferdig utfylt. TODO_FYLL står der modellen skal skrive."""
    d: dict[str, Any] = dict(HEADER)
    if kode == "A":
        d["myndigheter"] = [
            {
                "id": i, "myndighet": n, "omrade": o, "intern_eier": e,
                "kontaktperson": KONTAKTPERSONER[i][0], "kontakt_epost": KONTAKTPERSONER[i][1],
                "intern_eier_navn": INTERNE_PERSONER[e][0], "intern_eier_epost": INTERNE_PERSONER[e][1],
                "hva_de_vil": _fri("hva myndigheten ber om fra oss"),
                "utloser": _fri("hva som utløser kontakt"),
                "dokumentasjon": _fri("hvilken dokumentasjon de vanligvis ber om"),
                "merknad": "treningsdata, ikke rettesnor",
            }
            for i, n, o, e in MYNDIGHETER
        ]  # fmt: skip
    elif kode == "B":
        d["avvik_frister"] = dict(AVVIK_FRISTER)
        d["steg"] = [
            {
                "nr": nr, "navn": navn, "ansvarlig": ans,
                "handling": _fri("hva som gjøres i dette steget"),
                "dokumentasjon": _fri("hvilken dokumentasjon som trengs"),
            }
            for nr, navn, ans in TILSYNSSTEG
        ]  # fmt: skip
    elif kode == "C":
        d["rapporter"] = [
            {
                "id": r[0], "rapport": r[1], "mottaker": r[2], "mottakertype": r[3], "frekvens": r[4],
                "antall_per_ar": r[5], "maned": r[6], "eier": r[7], "timer_per_gang": r[8], "godkjenning": r[9],
                "formal": _fri("hva rapporten brukes til"),
                "kilder": _kilder(),
            }
            for r in RAPPORTER
        ]  # fmt: skip
    elif kode == "D":
        d["maler"] = [
            {
                "id": i, "navn": navn, "brukes_til": brukes, "godkjenning": god, "status_ved_opprettelse": "Utkast",
                "formal": _fri("hva malen brukes til"),
                "felt": [{"navn": f, "beskrivelse": _fri(f"hva som skal stå i feltet {f}", 140), "kilde": _kilder().replace("2 eller 3", "1 eller 2")} for f in felt],
                "regler": _liste("regler for utfylling og bruk av malen"),
            }
            for i, navn, brukes, god, felt in MALER
        ]  # fmt: skip
    elif kode == "E":
        rader: list[dict[str, Any]] = []
        for i, oppg, myn, rolle, t, pot in MYNDIGHETSOPPGAVER:
            rader.append({"id": i, "omrade": "Myndighetskontakt", "oppgave": oppg, "myndighet": myn, "rolle": rolle, "timer_per_ar": t, "automatiseringspotensial": pot, "begrunnelse": _fri("hvorfor potensialet er som angitt", 140)})
        for n, r in enumerate(RAPPORTER, start=8):
            rader.append({"id": f"AO-{n:02d}", "omrade": "Rapportering", "oppgave": r[1], "rapport_id": r[0], "rolle": r[7], "timer_per_ar": int(timer_per_ar(r)), "automatiseringspotensial": r[10], "begrunnelse": _fri("hvorfor potensialet er som angitt", 140)})
        d["oppgaver"] = rader
        d["sum"] = summer()
    elif kode == "F":
        d["historikk"] = [
            {
                "ar": r["ar"], "status_ar": r["status_ar"], "tema": r["tema"],
                "nokkeltall": {k: r[k] for k in HISTORIKK_NOKKELTALL},
                "hendelse": _fri("hva som preget året for myndighetskontakt og rapportering, i tråd med temaet og nøkkeltallene"),
                "laerdom": _fri("hva museet lærte det året, ut fra temaet og nøkkeltallene"),
            }
            for r in historikk_rader()
        ]  # fmt: skip
    elif kode == "T":
        d["forklaring"] = dict(HISTORIKK_FORKLARING)
        d["aar"] = historikk_rader()
    else:
        raise KeyError(kode)
    return d


def skjelett_tekst(kode: str) -> str:
    return yaml.safe_dump(skjelett(kode), sort_keys=False, allow_unicode=True, width=1000)


def skriv_skjelett(mappe: Path) -> list[Path]:
    mappe.mkdir(parents=True, exist_ok=True)
    ut = []
    for k, f in FILER.items():
        p = mappe / f
        p.write_text(skjelett_tekst(k), encoding="utf-8")
        ut.append(p)
    return ut


def skriv_historikk_tall(mappe: Path) -> Path:
    """Skriver den kodegenererte tallfilen (2010 til 2026). Ingen modell er involvert."""
    mappe.mkdir(parents=True, exist_ok=True)
    p = mappe / GENERERT_FIL["T"]
    p.write_text(skjelett_tekst("T"), encoding="utf-8")
    return p


# ---------------------------------------------------------------- kontroll


@dataclass(frozen=True)
class Funn:
    fil: str
    sti: str
    alvor: str  # FEIL | ADVARSEL
    kode: str
    melding: str


@dataclass
class Rapport:
    funn: list[Funn] = field(default_factory=list)
    filer: dict[str, bool] = field(default_factory=dict)  # kode -> består (ingen FEIL)

    @property
    def feil(self) -> list[Funn]:
        return [f for f in self.funn if f.alvor == "FEIL"]

    @property
    def advarsler(self) -> list[Funn]:
        return [f for f in self.funn if f.alvor == "ADVARSEL"]

    @property
    def ok(self) -> bool:
        # Alle modellfiler må være levert og bestå. Den genererte tallfilen (T) er valgfri, men må bestå hvis den ligger der.
        return not self.feil and all(self.filer.values()) and all(k in self.filer for k in FILER)


FORNAVN = {
    "Lars", "Ola", "Kari", "Nina", "Jens", "Erik", "Hanne", "Ingrid", "Magnus", "Silje", "Henrik", "Marte", "Thomas",
    "Camilla", "Anders", "Kristian", "Maria", "Sofie", "Emma", "Jon", "Hans", "Bjørn", "Tone", "Siv", "Trond", "Morten",
    "Ida", "Knut", "Rune", "Stein", "Svein", "Vidar", "Ellen", "Julie", "Sara", "Nora", "Johan", "Jonas", "Mathias", "Andreas", "Martin", "Olav",
}  # fmt: skip
KI_SNAKK = (
    "som en språkmodell", "som språkmodell", "as an ai", "language model", "her er", "selvfølgelig", "jeg har laget",
    "her kommer", "lorem ipsum", "[...]", "<<", ">>", "```", "todo",
)  # fmt: skip
ENGELSK = {"the", "and", "of", "are", "with", "that", "this", "will", "must", "should", "have", "from"}  # ikke ord som også er norske (for, to, is)
KJENTE_EGENNAVN = {
    "Kunstpixel", "Kunstmuseum", "Arbeidstilsynet", "Mattilsynet", "Datatilsynet", "Stiftelsestilsynet", "Kulturdirektoratet",
    "Brann", "Kommunen", "Fylkeskommunen", "Museumsdirektør", "Samlingsforvalter", "Kurator", "Formidler", "Museumsvert", "Driftsansvarlig",
    "Kvalitetsvokter", "Kafeansvarlig", "Verneombud", "Brannvernleder", "Konservator", "Styret", "Januar", "Februar", "Mars", "April", "Mai",
    "Juni", "Juli", "August", "September", "Oktober", "November", "Desember", "Sal", "Utkast", "Excel", "Word", "Teams",
}  # fmt: skip
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿]")
KONTAKT_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|https?://|www\.|\b\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}\b|\+\d{2}")
PARAGRAF_RE = re.compile(r"§|\bparagraf\b|\bLOV-\d|\bforskrift\s+nr\b|\blov\s+om\b", re.I)


def _norske_ord(tekst: str) -> list[str]:
    return re.findall(r"[A-Za-zÆØÅæøå]+", tekst)


def _sjekk_fritekst(tekst: Any, fil: str, sti: str, funn: list[Funn], maks: int = 220) -> None:
    def f(kode: str, melding: str, alvor: str = "FEIL") -> None:
        funn.append(Funn(fil, sti, alvor, kode, melding))

    if not isinstance(tekst, str):
        f("TYPE", f"Skal være tekst, fikk {type(tekst).__name__}")
        return
    t = tekst.strip()
    if PLASSHOLDER in t:
        f("PLASSHOLDER", "TODO_FYLL er ikke erstattet")
        return
    if len(t) < 20:
        f("FOR_KORT", f"Bare {len(t)} tegn. Skriv minst 20")
    if len(t) > maks:
        f("FOR_LANG", f"{len(t)} tegn. Maks {maks}")
    if len(_norske_ord(t)) < 4:
        f("FOR_KORT", "Mindre enn fire ord")
    if re.search(r"\d", t):
        f("TALL_I_TEKST", "Teksten inneholder tall. Fritekst skal ikke ha tall, frister eller terskler")
    if KONTAKT_RE.search(t):
        f("KONTAKTDETALJER", "E-post, telefonnummer eller lenke er ikke tillatt")
    if PARAGRAF_RE.search(t):
        f("PARAGRAF", "Ingen paragrafer eller henvisninger til lovtekst")
    if EMOJI_RE.search(t):
        f("EMOJI", "Ingen emoji")
    low = t.lower()
    for frase in KI_SNAKK:
        if frase in low:
            f("KI_SNAKK", f"Teksten ser ut som svar fra en chat, ikke som data: «{frase}»")
            break
    for ord_ in _norske_ord(t):
        if ord_ in FORNAVN:
            f("PERSONNAVN", f"Ser ut som et personnavn: {ord_}. Bruk bare roller")
            break
    ord_liste = [w.lower() for w in _norske_ord(t)]
    if ord_liste and sum(w in ENGELSK for w in ord_liste) / len(ord_liste) > 0.2:
        f("ENGELSK", "Ser ut som engelsk. Skriv norsk bokmål", "ADVARSEL")
    for m in re.finditer(r"(?<![.!?:]\s)(?<!^)\b[A-ZÆØÅ][a-zæøå]{2,}\b", t):
        if m.group(0) not in KJENTE_EGENNAVN and m.group(0) not in ROLLER_TILLATT:
            f("EGENNAVN", f"Mulig egennavn: {m.group(0)}. Sjekk at det ikke er en person", "ADVARSEL")
            break


def _sjekk_kilder(v: Any, fil: str, sti: str, funn: list[Funn], lo: int, hi: int) -> None:
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        funn.append(Funn(fil, sti, "FEIL", "TYPE", "Skal være en liste med kilder"))
        return
    if not lo <= len(v) <= hi:
        funn.append(Funn(fil, sti, "FEIL", "ANTALL", f"Skal ha {lo} til {hi} kilder, har {len(v)}"))
    for x in v:
        if x not in KILDER_TILLATT:
            funn.append(Funn(fil, sti, "FEIL", "UKJENT_KILDE", f"«{x}» er ikke i listen: {', '.join(KILDER_TILLATT)}"))
    if len(set(v)) != len(v):
        funn.append(Funn(fil, sti, "FEIL", "DUPLIKAT", "Samme kilde flere ganger"))


def _sammenlign(skel: Any, lev: Any, fil: str, sti: str, funn: list[Funn], tekster: list[tuple[str, str]]) -> None:
    if isinstance(skel, str) and skel.startswith(PLASSHOLDER):
        if skel.startswith(f"{PLASSHOLDER}_KILDER"):
            lo, hi = (1, 2) if "1 eller 2" in skel else (2, 3)
            _sjekk_kilder(lev, fil, sti, funn, lo, hi)
        elif skel.startswith(f"{PLASSHOLDER}_LISTE"):
            if not isinstance(lev, list) or not 2 <= len(lev) <= 3:
                funn.append(Funn(fil, sti, "FEIL", "ANTALL", "Skal være en liste med 2 eller 3 regler"))
            else:
                for i, x in enumerate(lev):
                    _sjekk_fritekst(x, fil, f"{sti}[{i}]", funn, 160)
                    if isinstance(x, str):
                        tekster.append((f"{sti}[{i}]", x.strip().lower()))
        else:
            maks = int(m.group(1)) if (m := re.search(r"maks (\d+) tegn", skel)) else 220
            _sjekk_fritekst(lev, fil, sti, funn, maks)
            if isinstance(lev, str):
                tekster.append((sti, lev.strip().lower()))
        return
    if isinstance(skel, dict):
        if not isinstance(lev, dict):
            funn.append(Funn(fil, sti, "FEIL", "STRUKTUR", f"Skal være en gruppe med felt, fikk {type(lev).__name__}"))
            return
        for k in skel:
            if k not in lev:
                funn.append(Funn(fil, f"{sti}.{k}".lstrip("."), "FEIL", "MANGLER", f"Feltet {k} mangler"))
        for k in lev:
            if k not in skel:
                funn.append(Funn(fil, f"{sti}.{k}".lstrip("."), "FEIL", "UKJENT_FELT", f"Feltet {k} skal ikke være med"))
        for k, v in skel.items():
            if k in lev:
                _sammenlign(v, lev[k], fil, f"{sti}.{k}".lstrip("."), funn, tekster)
        return
    if isinstance(skel, list):
        if not isinstance(lev, list):
            funn.append(Funn(fil, sti, "FEIL", "STRUKTUR", f"Skal være en liste, fikk {type(lev).__name__}"))
            return
        if len(lev) != len(skel):
            funn.append(Funn(fil, sti, "FEIL", "ANTALL", f"Skal ha {len(skel)} oppføringer, har {len(lev)}"))
        for i, (s, v) in enumerate(zip(skel, lev)):
            _sammenlign(s, v, fil, f"{sti}[{i}]", funn, tekster)
        return
    # fast felt: må være uendret, også typen (1 er ikke true, 1.5 er ikke «1,5»)
    if lev != skel or type(lev) is not type(skel):
        funn.append(Funn(fil, sti, "FEIL", "FAST_FELT_ENDRET", f"Fast felt er endret. Skal være {skel!r}, er {lev!r}. Endre det tilbake"))


def _rens(tekst: str) -> tuple[str, bool]:
    """Fjerner kodegjerder rundt filen. Returnerer (tekst, hadde_gjerder)."""
    lines = tekst.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines), True
    return tekst, False


def kontroller_tekst(kode: str, tekst: str) -> list[Funn]:
    fil = FILNAVN[kode]
    funn: list[Funn] = []
    if len(tekst.encode("utf-8", errors="ignore")) > MAX_FILSTORRELSE:
        return [Funn(fil, "", "FEIL", "FOR_STOR", f"Filen er over {MAX_FILSTORRELSE} byte")]
    if not tekst.strip():
        return [Funn(fil, "", "FEIL", "TOM", "Filen er tom")]
    tekst, gjerder = _rens(tekst)
    if gjerder:
        funn.append(Funn(fil, "", "ADVARSEL", "KODEGJERDER", "Filen hadde ``` rundt seg. Fjernet ved kontroll. Lever ren YAML"))
    tekst = tekst.lstrip("\ufeff")
    try:
        # Ankere og alias avvises før noe bygges: et lite «billion laughs»-dokument kan ellers fylle minnet.
        antall = 0
        for ev in yaml.parse(tekst):
            antall += 1
            if isinstance(ev, yaml.AliasEvent) or getattr(ev, "anchor", None):
                return funn + [Funn(fil, "", "FEIL", "ANKER", "YAML-ankere og alias (&, *) er ikke tillatt. Skriv ut verdiene")]
            if antall > MAX_YAML_HENDELSER:
                return funn + [Funn(fil, "", "FEIL", "FOR_STOR", "Filen har uvanlig mange YAML-elementer")]
        lev = yaml.load(tekst, Loader=_StrengLoader)  # trygg loader: ingen kode kjøres, !!python avvises, duplikate nøkler avvises
    except yaml.YAMLError as exc:
        kode = "DUPLIKAT_NOKKEL" if isinstance(exc, _DuplikatNokkel) else "UGYLDIG_YAML"
        melding = str(exc) if kode == "DUPLIKAT_NOKKEL" else f"Kan ikke leses som YAML: {type(exc).__name__}. Lever hele filen som ren YAML"
        return funn + [Funn(fil, "", "FEIL", kode, melding)]
    if not isinstance(lev, dict):
        return funn + [Funn(fil, "", "FEIL", "STRUKTUR", "Toppnivået skal være en gruppe med felt")]
    tekster: list[tuple[str, str]] = []
    _sammenlign(skjelett(kode), lev, fil, "", funn, tekster)
    seen: dict[str, str] = {}
    for sti, t in tekster:
        if t in seen:
            funn.append(Funn(fil, sti, "FEIL", "KOPIERT_TEKST", f"Samme tekst som i {seen[t]}. Hver tekst skal være unik"))
        else:
            seen[t] = sti
    return funn


def kontroller_mappe(mappe: Path) -> Rapport:
    r = Rapport()
    for kode, filnavn in FILER.items():
        p = mappe / filnavn
        if not p.is_file():
            r.funn.append(Funn(filnavn, "", "FEIL", "MANGLER_FIL", "Filen er ikke levert"))
            r.filer[kode] = False
            continue
        try:
            tekst = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            r.funn.append(Funn(filnavn, "", "FEIL", "KAN_IKKE_LESES", type(exc).__name__))
            r.filer[kode] = False
            continue
        f = kontroller_tekst(kode, tekst)
        r.funn.extend(f)
        r.filer[kode] = not any(x.alvor == "FEIL" for x in f)
    # Den genererte tallfilen er valgfri i leveransen, men skal være uendret hvis den ligger der.
    for kode, filnavn in GENERERT_FIL.items():
        p = mappe / filnavn
        if p.is_file():
            try:
                f = kontroller_tekst(kode, p.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError) as exc:
                f = [Funn(filnavn, "", "FEIL", "KAN_IKKE_LESES", type(exc).__name__)]
            r.funn.extend(f)
            r.filer[kode] = not any(x.alvor == "FEIL" for x in f)
    return r


def retteliste(r: Rapport) -> str:
    """Tekst som kan limes rett tilbake til den andre modellen. Tom hvis alt er ok."""
    if not r.feil and all(r.filer.values()):
        return ""
    ut = [
        "Leveransen din har feil. Rett dem og lever HELE filene på nytt som ren YAML (ikke bare endringene).",
        "Ikke endre faste felt (id-er, navn, roller, tall, valg). Skriv bare fritekst der det står TODO_FYLL.",
        "Fritekst skal ha ingen tall, ingen personnavn, ingen kontaktdetaljer, ingen paragrafer, og hver tekst skal være unik.",
        "",
    ]
    per_fil: dict[str, list[Funn]] = {}
    for f in r.feil:
        per_fil.setdefault(f.fil, []).append(f)
    for fil, liste in per_fil.items():
        ut.append(f"## {fil}")
        for f in liste[:40]:
            ut.append(f"- {f.sti or '(hele filen)'} [{f.kode}]: {f.melding}")
        if len(liste) > 40:
            ut.append(f"- ... og {len(liste) - 40} flere feil av samme slag")
        ut.append("")
    return "\n".join(ut).rstrip() + "\n"


def retteliste_fil(funn: list[Funn]) -> str:
    """Retteliste for én fil, uten overskrift. Tom hvis ingen FEIL."""
    feil = [f for f in funn if f.alvor == "FEIL"]
    if not feil:
        return ""
    ut = [
        "Leveransen din har feil. Rett dem og lever HELE filen på nytt som ren YAML (ikke bare endringene).",
        "Ikke endre faste felt (id-er, navn, roller, tall, valg). Skriv bare fritekst der det står TODO_FYLL.",
        "Fritekst skal ha ingen tall, ingen personnavn, ingen kontaktdetaljer, ingen paragrafer, og hver tekst skal være unik.",
        "",
    ]
    for f in feil[:40]:
        ut.append(f"- {f.sti or '(hele filen)'} [{f.kode}]: {f.melding}")
    if len(feil) > 40:
        ut.append(f"- ... og {len(feil) - 40} flere feil av samme slag")
    return "\n".join(ut) + "\n"


def installer(mappe: Path, koder: list[str], mal: Path, overskriv: bool = False) -> tuple[list[str], list[str]]:
    """Kopierer filer som består kontrollen til `mal`. Returnerer (installert, avvist). Overskriver ikke uten `overskriv`."""
    r = kontroller_mappe(mappe)
    ok: list[str] = []
    avvist: list[str] = []
    for k in koder:
        k = k.strip().upper()
        if k not in FILNAVN:
            avvist.append(f"{k}: ukjent filkode")
            continue
        if k in GENERERT_FIL:
            # Tallfilen lages av koden. Ligger den i leveransen, må den være uendret. Ellers lages den på nytt.
            if (mappe / FILNAVN[k]).is_file() and not r.filer.get(k):
                avvist.append(f"{k}: består ikke kontrollen")
                continue
            kilde = (mappe / FILNAVN[k]).read_text(encoding="utf-8") if (mappe / FILNAVN[k]).is_file() else skjelett_tekst(k)
        else:
            if not r.filer.get(k):
                avvist.append(f"{k}: består ikke kontrollen")
                continue
            kilde = (mappe / FILNAVN[k]).read_text(encoding="utf-8")
        ut = mal / FILNAVN[k]
        if ut.exists() and not overskriv:
            avvist.append(f"{k}: finnes allerede ({FILNAVN[k]}), bruk overskriv")
            continue
        mal.mkdir(parents=True, exist_ok=True)
        tekst, _ = _rens(kilde)
        ut.write_text(tekst.strip() + "\n", encoding="utf-8")
        ok.append(k)
    return ok, avvist
