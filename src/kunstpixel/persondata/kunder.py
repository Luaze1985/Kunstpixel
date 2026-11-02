"""Genererer syntetiske kundedata for Kunstpixel (2021-11-02 til 2026-11-02).

Medlemmer med fordeler, gavekort, arrangementer med påmeldinger, skole,
utleie og henvendelser. Alle referanser til ansatte bruker eksisterende
ansatte fra museum.db og peker bare på en ansatt som var i jobb på datoen.

Volum og andeler styres fra `05_data/persondata/innstillinger.yaml`.
"""

from __future__ import annotations

import bisect
import random
import string
from collections import defaultdict
from datetime import date, timedelta

from faker import Faker

from src.kunstpixel.persondata import config
from src.kunstpixel.persondata.ansattkilde import Ansatt, aktive_paa, del_navn

DK = config.DATAKILDE
START, REF = config.KUNDER_START, config.REFERANSEDATO
GENERERTE_ARRANGEMENTER_TIL = date(2026, 8, 31)
PLANT_GRENSE = REF - timedelta(days=1096)  # mer enn 3 år tilbake

TEMAER = [
    "Lys og farge", "Norsk landskap", "Ekspresjonisme", "Portrettet", "Grafikk",
    "Samtidskunst", "Skulptur i rommet", "Kunst og natur", "Kvinner i kunsten", "Fotografi",
]
TITTEL_PER_TYPE = {
    "omvisning": "Guidet omvisning",
    "barnearrangement": "Familiesøndag",
    "verksted": "Verksted",
    "foredrag": "Kveldsforedrag",
    "aaapning": "Åpning",
}
BARNETYPER = {"barnearrangement", "verksted"}

HENVENDELSESMALER: dict[str, list[str]] = {
    "billett": [
        "Hva koster det å besøke museet?", "Er det studentrabatt?", "Kan jeg kjøpe billett i døra?",
        "Gjelder billetten hele dagen?", "Er det gratis for barn?", "Har dere familiebillett?",
        "Kan jeg betale med Vipps?", "Er det gratisdag noen gang?", "Gjelder honnørrabatt?",
        "Kan jeg få refundert en billett?",
    ],
    "praktisk": [
        "Når har museet åpent?", "Er det åpent på mandager?", "Hvor lang tid bør jeg sette av?",
        "Er det parkering ved museet?", "Kan jeg fotografere i utstillingene?", "Har dere åpent i påsken?",
        "Hvor er nærmeste bussholdeplass?", "Kan jeg ta med hund?", "Når er det minst folk?",
        "Er det åpent på julaften?",
    ],
    "fasiliteter": [
        "Er det kafé i museet?", "Har museet garderobe?", "Finnes det stellerom?", "Har dere skap til sekker?",
        "Er det wifi i museet?", "Kan jeg lade telefonen?", "Hva serverer kaféen til lunsj?",
        "Har kaféen glutenfrie alternativer?", "Er det sitteplasser i salene?", "Finnes det toalett i første etasje?",
    ],
    "formidling": [
        "Finnes det audioguide?", "Har dere omvisning på engelsk?", "Når er neste omvisning?",
        "Har dere omvisning for skoleklasser?", "Kan vi bestille privat omvisning?", "Er det verksted for barn?",
        "Hvor lang er omvisningen?", "Må jeg melde meg på foredraget?", "Har dere tegnspråktolket omvisning?",
        "Kan jeg låne audioguide på telefonen?",
    ],
    "tilgjengelighet": [
        "Kan jeg ta med barnevogn?", "Er museet tilgjengelig med rullestol?", "Finnes det heis?",
        "Har dere teleslynge?", "Kan ledsager komme gratis inn?", "Er det HC-parkering?",
        "Kan jeg låne rullestol?", "Er tekstene tilgjengelige i stor skrift?", "Er det trinnfri inngang?",
        "Har dere stille stunder for sensitive besøkende?",
    ],
    "utleie": [
        "Er det mulig å leie museet til private arrangementer?", "Hva koster det å leie foajeen?",
        "Kan vi holde julebord i museet?", "Hvor mange gjester er det plass til?", "Kan vi leie med servering?",
        "Har dere møterom til leie?", "Kan vi ha bryllupsbilder i salene?", "Leier dere ut på kveldstid?",
        "Hvor lang tid i forveien må vi bestille?", "Kan vi få omvisning som del av leien?",
    ],
    "samling": [
        "Hvor finner jeg Skrik?", "Er Harriet Backer utstilt nå?", "Hvilke verk er nye i samlingen?",
        "Hvor mange verk har dere?", "Er grafikksamlingen åpen for publikum?", "Hvorfor er et verk tatt ned?",
        "Har dere skulpturer utendørs?", "Hvor lenge varer den nye utstillingen?", "Låner dere ut verk til andre museer?",
        "Kan jeg se verk som er på magasinet?",
    ],
    "butikk": [
        "Selger dere plakater og kunstbøker?", "Har dere nettbutikk?", "Kan jeg bytte en vare?",
        "Selger dere utstillingskatalogen?", "Har dere postkort med verk fra samlingen?", "Når åpner butikken?",
        "Kan jeg bestille trykk av et maleri?", "Sender dere varer i posten?", "Selger dere gavekort i butikken?",
        "Har dere leker til barn?",
    ],
    "medlemskap": [
        "Hva koster medlemskap?", "Hvilke fordeler får jeg som medlem?", "Kan jeg ta med gjest som medlem?",
        "Hvordan fornyer jeg medlemskapet?", "Får jeg rabatt i kaféen som medlem?", "Hva er forskjellen på venn og enkelt?",
        "Kan jeg si opp medlemskapet?", "Gjelder familiemedlemskap for besteforeldre?", "Har jeg mistet medlemskortet?",
        "Får medlemmer invitasjon til åpninger?",
    ],
    "gavekort": [
        "Hvor lenge er gavekortet gyldig?", "Kan gavekortet brukes i kaféen?", "Hvordan sjekker jeg saldoen?",
        "Gavekortet mitt virker ikke i kassen.", "Kan jeg kjøpe gavekort på nett?", "Kan gavekort brukes på arrangementer?",
        "Kan jeg få gavekortet forlenget?", "Har jeg mistet gavekortet, hva gjør jeg?", "Kan gavekort deles på flere kjøp?",
        "Kan jeg få pengene tilbake for et gavekort?",
    ],
}


def _antall(navn: str, faktor: float) -> int:
    return max(1, round(config.VOLUM[navn] * faktor))


def _dato_mellom(rng: random.Random, fra: date, til: date) -> date:
    if til <= fra:
        return fra
    return fra + timedelta(days=rng.randint(0, (til - fra).days))


def generer_kunder(
    rng: random.Random,
    fake: Faker,
    ansatte: list[Ansatt],
    dagsbesok: dict[date, tuple[int, bool]],
    hendelser: list[dict],
    faktor: float = 1.0,
) -> dict[str, list[dict]]:
    """Generer alle kundetabeller (unntatt katalogtabellene) som lister av rader."""
    aapne_dager = sorted(d for d, (_, er_aapen) in dagsbesok.items() if er_aapen and START <= d <= REF)
    aapen = set(aapne_dager)

    def ansatt_paa(dato: date, avdelinger: set[str] | None = None) -> str | None:
        kandidater = aktive_paa(ansatte, dato, avdelinger)
        return rng.choice(kandidater).ansatt_id if kandidater else None

    def aapen_dag_mellom(fra: date, til: date) -> date | None:
        i, j = bisect.bisect_left(aapne_dager, fra), bisect.bisect_right(aapne_dager, til)
        return aapne_dager[rng.randrange(i, j)] if i < j else None

    # --- Kontakter -------------------------------------------------------
    kontakter: list[dict] = []
    n_kontakter = _antall("kontakter", faktor)
    andel = config.ANDELER
    for i in range(1, n_kontakter + 1):
        fornavn, etternavn = fake.first_name(), fake.last_name()
        opprettet = _dato_mellom(rng, START, REF)
        samtykke = rng.random() < andel["nyhetsbrev_samtykke"]
        samtykke_dato = _dato_mellom(rng, opprettet, min(REF, opprettet + timedelta(days=30))) if samtykke else None
        trukket = None
        if samtykke and samtykke_dato < REF and rng.random() < andel["trekker_samtykke"]:
            trukket = _dato_mellom(rng, samtykke_dato + timedelta(days=1), REF)
        kontakter.append({
            "kontakt_id": f"K{i:06d}",
            "fornavn": fornavn,
            "etternavn": etternavn,
            "epost": config.lag_epost(fornavn, etternavn, i),
            "telefon": config.lag_telefon(rng) if rng.random() < 0.7 else None,
            "ansatt_id": None,
            "opprettet": opprettet,
            "nyhetsbrev_samtykke": int(samtykke),
            "samtykke_dato": samtykke_dato,
            "samtykke_kilde": rng.choice(["nettside", "kasse", "arrangement"]) if samtykke else None,
            "trukket_dato": trukket,
            "siste_aktivitet": opprettet,
            "datakilde": DK,
        })

    # Plantede brudd: trukket samtykke for over 3 år siden, men e-post står fortsatt.
    n_trukket = sum(1 for k in kontakter if k["trukket_dato"])
    plantet: set[str] = set()
    for k in kontakter[: max(1, round(0.02 * n_trukket))]:
        k["opprettet"] = _dato_mellom(rng, START, START + timedelta(days=60))
        k["nyhetsbrev_samtykke"] = 1
        k["samtykke_dato"] = k["opprettet"] + timedelta(days=rng.randint(0, 10))
        k["samtykke_kilde"] = "nettside"
        k["trukket_dato"] = k["samtykke_dato"] + timedelta(days=rng.randint(30, 200))
        k["siste_aktivitet"] = k["trukket_dato"]
        plantet.add(k["kontakt_id"])
    kunde = {k["kontakt_id"]: k for k in kontakter}
    aktive_kunder = [k for k in kontakter if k["kontakt_id"] not in plantet]

    # Ansatte som kontakter (personalmedlemskap). Navn og e-post kopieres eksakt.
    lopenr = n_kontakter
    ansattkontakter: list[tuple[dict, Ansatt]] = []
    for a in ansatte:
        if a.ansatt_fra > REF or (a.ansatt_til is not None and a.ansatt_til < START):
            continue
        lopenr += 1
        fornavn, etternavn = del_navn(a.navn)
        fra = max(START, a.ansatt_fra)
        k = {
            "kontakt_id": f"K{lopenr:06d}", "fornavn": fornavn, "etternavn": etternavn,
            "epost": a.epost, "telefon": None, "ansatt_id": a.ansatt_id, "opprettet": fra,
            "nyhetsbrev_samtykke": 0, "samtykke_dato": None, "samtykke_kilde": None,
            "trukket_dato": None, "siste_aktivitet": min(REF, a.ansatt_til or REF), "datakilde": DK,
        }
        kontakter.append(k)
        ansattkontakter.append((k, a))

    def merk_aktivitet(kontakt_id: str, dato: date) -> None:
        k = kunde.get(kontakt_id)
        if k and dato > k["siste_aktivitet"]:
            k["siste_aktivitet"] = dato

    # --- Medlemskap ------------------------------------------------------
    typer = [t for t, v in config.MEDLEMSKAPSTYPER.items() if v["andel"] > 0]
    vekter = [config.MEDLEMSKAPSTYPER[t]["andel"] for t in typer]
    medlemskap: list[dict] = []
    ledige = aktive_kunder[:]
    rng.shuffle(ledige)
    n_aktive = _antall("aktive_medlemskap", faktor)
    fornyelse = config.VOLUM["fornyelsesandel"]
    innmelding_per_aar = max(1, round(n_aktive * (1 - fornyelse)))

    startdatoer = [_dato_mellom(rng, START, START + timedelta(days=364)) for _ in range(n_aktive)]
    aar_start = START + timedelta(days=365)
    while aar_start <= REF:
        aar_slutt = min(REF, aar_start + timedelta(days=364))
        andel_av_aar = ((aar_slutt - aar_start).days + 1) / 365
        startdatoer += [_dato_mellom(rng, aar_start, aar_slutt) for _ in range(round(innmelding_per_aar * andel_av_aar))]
        aar_start += timedelta(days=365)

    def nytt_medlemskap(kontakt: dict, type_: str, start: date, forrige: int | None) -> dict:
        m = {
            "medlemskap_id": len(medlemskap) + 1, "kontakt_id": kontakt["kontakt_id"], "type": type_,
            "startdato": start, "sluttdato": start + timedelta(days=364),
            "betalt_belop": config.MEDLEMSKAPSTYPER[type_]["aarspris"], "fornyelse_av": forrige,
            "solgt_av_ansatt_id": ansatt_paa(start, {"Formidling", "Drift"}) if start in aapen else None,
            "datakilde": DK,
        }
        medlemskap.append(m)
        return m

    for start in startdatoer:
        if not ledige:
            break
        kontakt = ledige.pop()
        kontakt["opprettet"] = min(kontakt["opprettet"], start)
        if kontakt["samtykke_dato"] and kontakt["samtykke_dato"] < kontakt["opprettet"]:
            kontakt["opprettet"] = kontakt["samtykke_dato"]
        type_ = rng.choices(typer, vekter)[0]
        m = nytt_medlemskap(kontakt, type_, start, None)
        while m["sluttdato"] < REF and rng.random() < fornyelse:
            m = nytt_medlemskap(kontakt, type_, m["sluttdato"] + timedelta(days=1), m["medlemskap_id"])
        merk_aktivitet(kontakt["kontakt_id"], min(REF, m["sluttdato"]))

    for k, a in ansattkontakter:
        start = max(START, a.ansatt_fra)
        slutt = a.ansatt_til if a.ansatt_til else REF + timedelta(days=364)
        medlemskap.append({
            "medlemskap_id": len(medlemskap) + 1, "kontakt_id": k["kontakt_id"], "type": "ansatt",
            "startdato": start, "sluttdato": max(start, slutt), "betalt_belop": 0, "fornyelse_av": None,
            "solgt_av_ansatt_id": None, "datakilde": DK,
        })

    medlemskap_per_kontakt: dict[str, list[dict]] = defaultdict(list)
    for m in medlemskap:
        medlemskap_per_kontakt[m["kontakt_id"]].append(m)

    # --- Medlemsbesøk ----------------------------------------------------
    tak = {d: int(config.ANDELER["maks_medlemsandel_av_dagsbesok"] * b) for d, (b, _) in dagsbesok.items()}
    brukt_tak: dict[date, int] = defaultdict(int)
    medlemsbesok: list[dict] = []
    gjestetyper = set(config.FORDELER.get("medbring_gjest", {}).get("typer", []))
    for m in medlemskap:
        if m["type"] == "ansatt" or m["startdato"] > REF:
            continue
        slutt = min(REF, m["sluttdato"])
        forventet = config.VOLUM["medlemsbesok_per_aar"] * ((slutt - m["startdato"]).days + 1) / 365
        antall = int(forventet) + (1 if rng.random() < forventet - int(forventet) else 0)
        for _ in range(antall):
            for _forsok in range(5):
                dag = aapen_dag_mellom(m["startdato"], slutt)
                if dag is None:
                    break
                if brukt_tak[dag] < tak.get(dag, 0):
                    brukt_tak[dag] += 1
                    medlemsbesok.append({
                        "besok_id": len(medlemsbesok) + 1, "medlemskap_id": m["medlemskap_id"], "dato": dag,
                        "antall_gjester": rng.randint(0, 1) if m["type"] in gjestetyper else 0, "datakilde": DK,
                    })
                    break

    # --- Bruk av fordeler ------------------------------------------------
    def fordelverdi(fordel: str) -> float:
        v = config.FORDELER[fordel].get("verdi", 0)
        if isinstance(v, dict):
            lav, hoy = v["grunnlag"]
            return round(rng.uniform(lav, hoy) * v["prosent"] / 100, 2)
        return float(v)

    brukbare = [m for m in medlemskap if m["startdato"] <= REF]
    fordel_bruk: list[dict] = []
    for _ in range(_antall("fordel_bruk", faktor)):
        m = rng.choice(brukbare)
        mulige = [f for f, v in config.FORDELER.items() if m["type"] in v["typer"] and f != "fri_inngang"]
        if not mulige:
            continue
        fordel = rng.choice(mulige)
        dag = aapen_dag_mellom(m["startdato"], min(REF, m["sluttdato"]))
        if dag is None:
            continue
        fordel_bruk.append({
            "bruk_id": len(fordel_bruk) + 1, "medlemskap_id": m["medlemskap_id"], "fordel": fordel,
            "dato": dag, "rabatt_belop": fordelverdi(fordel), "datakilde": DK,
        })

    # --- Gavekort --------------------------------------------------------
    gavekort: list[dict] = []
    gavekort_bruk: list[dict] = []
    koder: set[str] = set()
    tegn = string.ascii_uppercase + string.digits
    gyldighet = timedelta(days=config.GAVEKORT["gyldighet_dager"])
    aar = (REF - START).days / 365
    for _ in range(max(1, round(config.VOLUM["gavekort_per_aar"] * faktor * aar))):
        kanal = rng.choice(["butikk", "nettbutikk", "skranke"])
        utstedt = _dato_mellom(rng, START, REF) if kanal == "nettbutikk" else aapen_dag_mellom(START, REF)
        while True:
            kode = "GK-" + "".join(rng.choices(tegn, k=4)) + "-" + "".join(rng.choices(tegn, k=4))
            if kode not in koder:
                koder.add(kode)
                break
        kjoper = rng.choice(aktive_kunder)
        mottaker = rng.choice(aktive_kunder) if rng.random() < andel["gavekort_med_mottaker"] else None
        g = {
            "gavekort_id": len(gavekort) + 1, "kode": kode, "belop": rng.choice(config.GAVEKORT["belop"]),
            "kjoper_kontakt_id": kjoper["kontakt_id"],
            "mottaker_kontakt_id": mottaker["kontakt_id"] if mottaker else None,
            "utstedt": utstedt, "gyldig_til": utstedt + gyldighet, "kanal": kanal,
            "solgt_av_ansatt_id": None if kanal == "nettbutikk" else ansatt_paa(utstedt, {"Formidling", "Drift"}),
            "datakilde": DK,
        }
        gavekort.append(g)
        kjoper["opprettet"] = min(kjoper["opprettet"], utstedt)
        merk_aktivitet(kjoper["kontakt_id"], utstedt)
        if rng.random() < andel["gavekort_aldri_brukt"]:
            continue
        rest = float(g["belop"])
        datoer = sorted(
            d for d in (aapen_dag_mellom(utstedt, min(REF, g["gyldig_til"])) for _ in range(rng.randint(1, 3))) if d
        )
        for nr, dato in enumerate(datoer):
            belop = rest if nr == len(datoer) - 1 and rng.random() < 0.6 else round(rest * rng.uniform(0.2, 0.9), 2)
            if belop <= 0:
                break
            rest = round(rest - belop, 2)
            gavekort_bruk.append({
                "bruk_id": len(gavekort_bruk) + 1, "gavekort_id": g["gavekort_id"], "dato": dato, "belop": belop,
                "sted": rng.choice(["billett", "butikk", "kafe"]), "datakilde": DK,
            })
    saldo = {g["gavekort_id"]: float(g["belop"]) for g in gavekort}
    for b in gavekort_bruk:
        saldo[b["gavekort_id"]] = round(saldo[b["gavekort_id"]] - b["belop"], 2)
    gavekort_per_kontakt: dict[str, list[dict]] = defaultdict(list)
    for g in gavekort:
        gavekort_per_kontakt[g["kjoper_kontakt_id"]].append(g)
        if g["mottaker_kontakt_id"]:
            gavekort_per_kontakt[g["mottaker_kontakt_id"]].append(g)

    # --- Arrangementer ---------------------------------------------------
    per_type: dict[str, list[tuple[int, float, float]]] = defaultdict(list)
    for h in hendelser:
        per_type[h["type"]].append((h["maks_deltakere"], float(h["pris_voksen"]), float(h["pris_barn"] or 0)))
    arr_typer = sorted(per_type)
    arr_vekter = [len(per_type[t]) for t in arr_typer]
    arrangementer: list[dict] = []
    for i in range(1, _antall("arrangementer", faktor) + 1):
        dag = aapen_dag_mellom(START, GENERERTE_ARRANGEMENTER_TIL)
        type_ = rng.choices(arr_typer, arr_vekter)[0]
        maks, pv, pb = rng.choice(per_type[type_])
        arrangementer.append({
            "arrangement_id": f"ARR-{i:05d}", "kilde": "generert", "type": type_,
            "tittel": f"{TITTEL_PER_TYPE.get(type_, type_.capitalize())}: {rng.choice(TEMAER)}",
            "dato": dag, "maks_deltakere": maks, "pris_voksen": pv, "pris_barn": pb,
            "ansvarlig_ansatt_id": ansatt_paa(dag, {"Formidling"}), "datakilde": DK,
        })
    for h in hendelser:
        dag = date.fromisoformat(h["dato"])
        if not START <= dag <= REF:
            continue
        arrangementer.append({
            "arrangement_id": f"MDB-{h['id']}", "kilde": "museum.db", "type": h["type"], "tittel": h["tittel"],
            "dato": dag, "maks_deltakere": h["maks_deltakere"], "pris_voksen": float(h["pris_voksen"]),
            "pris_barn": float(h["pris_barn"] or 0), "ansvarlig_ansatt_id": ansatt_paa(dag, {"Formidling"}),
            "datakilde": DK,
        })

    # --- Påmeldinger -----------------------------------------------------
    etter_opprettet = sorted(aktive_kunder, key=lambda k: (k["opprettet"], k["kontakt_id"]))
    opprettet_liste = [k["opprettet"] for k in etter_opprettet]

    def kunde_opprettet_for(dato: date) -> dict | None:
        n = bisect.bisect_right(opprettet_liste, dato)
        return etter_opprettet[rng.randrange(n)] if n else None

    omvisningsmedlem = set(config.FORDELER.get("gratis_omvisning", {}).get("typer", []))
    pameldinger: list[dict] = []
    for a in arrangementer:
        plasser = int(a["maks_deltakere"] * rng.uniform(0.4, 1.0))
        while plasser > 0:
            k = kunde_opprettet_for(a["dato"])
            if k is None:
                break
            voksne = min(plasser, rng.randint(1, 4))
            barn = min(plasser - voksne, rng.randint(0, 3)) if a["type"] in BARNETYPER else 0
            plasser -= voksne + barn
            belop = voksne * a["pris_voksen"] + barn * a["pris_barn"]
            betalt_med = rng.choice(["kort_kasse", "vipps"])
            if a["type"] == "omvisning" and any(
                m["type"] in omvisningsmedlem and m["startdato"] <= a["dato"] <= m["sluttdato"]
                for m in medlemskap_per_kontakt.get(k["kontakt_id"], [])
            ):
                betalt_med, belop = "medlemsfordel", 0.0
            elif belop > 0 and rng.random() < 0.05:
                for g in gavekort_per_kontakt.get(k["kontakt_id"], []):
                    if g["utstedt"] <= a["dato"] <= g["gyldig_til"] and saldo[g["gavekort_id"]] >= belop:
                        saldo[g["gavekort_id"]] = round(saldo[g["gavekort_id"]] - belop, 2)
                        gavekort_bruk.append({
                            "bruk_id": len(gavekort_bruk) + 1, "gavekort_id": g["gavekort_id"], "dato": a["dato"],
                            "belop": belop, "sted": "arrangement", "datakilde": DK,
                        })
                        betalt_med = "gavekort"
                        break
            registrert = max(k["opprettet"], START, a["dato"] - timedelta(days=rng.randint(0, 30)))
            pameldinger.append({
                "pamelding_id": len(pameldinger) + 1, "arrangement_id": a["arrangement_id"],
                "kontakt_id": k["kontakt_id"], "antall_voksne": voksne, "antall_barn": barn, "belop": belop,
                "betalt_med": betalt_med, "registrert": min(registrert, a["dato"]), "datakilde": DK,
            })
            merk_aktivitet(k["kontakt_id"], min(REF, a["dato"]))

    # --- Skolebestillinger og utleie -------------------------------------
    skolebestillinger: list[dict] = []
    for i in range(1, _antall("skolebestillinger", faktor) + 1):
        dag = aapen_dag_mellom(START, REF)
        while dag.weekday() >= 5 or dag.month == 7:
            dag = aapen_dag_mellom(START, REF)
        fornavn, etternavn = fake.first_name(), fake.last_name()
        skolebestillinger.append({
            "bestilling_id": i, "skole": f"{fake.city()} skole", "kontaktlaerer": f"{fornavn} {etternavn}",
            "jobb_epost": config.lag_epost(fornavn, etternavn, 900000 + i), "klassetrinn": rng.randint(1, 13),
            "antall_elever": rng.randint(15, 30), "dato": dag,
            "ansvarlig_ansatt_id": ansatt_paa(dag, {"Formidling"}), "datakilde": DK,
        })

    utleie: list[dict] = []
    for i in range(1, _antall("utleie", faktor) + 1):
        dag = _dato_mellom(rng, START, REF)
        bedrift = rng.random() < 0.6
        fornavn, etternavn = fake.first_name(), fake.last_name()
        utleie.append({
            "foresporsel_id": i, "kundetype": "bedrift" if bedrift else "privat",
            "kontaktperson": f"{fornavn} {etternavn}", "epost": config.lag_epost(fornavn, etternavn, 800000 + i),
            "firmanavn": fake.company() if bedrift else None, "dato": dag,
            "status": rng.choices(["forespurt", "bekreftet", "avlyst", "gjennomfoert"], [1, 2, 1, 4])[0],
            "ansvarlig_ansatt_id": ansatt_paa(dag, {"Ledelse", "Marked"}), "datakilde": DK,
        })

    # --- Henvendelser ----------------------------------------------------
    n_henv = _antall("henvendelser", faktor)
    med_persondata = set(rng.sample(range(n_henv), round(n_henv * andel["henvendelser_med_persondata"])))
    kategorier = sorted(HENVENDELSESMALER)
    henvendelser: list[dict] = []
    for i in range(n_henv):
        dag = _dato_mellom(rng, START, REF)
        kategori = rng.choice(kategorier)
        tekst = rng.choice(HENVENDELSESMALER[kategori])
        kontakt = kunde_opprettet_for(dag) if rng.random() < andel["henvendelser_med_kontakt"] else None
        if i in med_persondata:
            person = kontakt or rng.choice(aktive_kunder)
            form = rng.randrange(3)
            if form == 0:
                tekst = f"Jeg heter {person['fornavn']} {person['etternavn']}. {tekst}"
            elif form == 1:
                tekst = f"{tekst} Ring meg gjerne på {config.lag_telefon(rng)}."
            else:
                tekst = f"{tekst} Svar til {person['epost']}."
        if kontakt:
            merk_aktivitet(kontakt["kontakt_id"], dag)
        henvendelser.append({
            "henvendelse_id": i + 1,
            "tidspunkt": f"{dag.isoformat()}T{rng.randint(9, 20):02d}:{rng.randint(0, 59):02d}",
            "kanal": rng.choice(["cli", "telegram", "skranke", "epost"]), "fritekst": tekst, "kategori": kategori,
            "inneholder_persondata": int(i in med_persondata),
            "kontakt_id": kontakt["kontakt_id"] if kontakt else None,
            "besvart_av_ansatt_id": ansatt_paa(dag), "datakilde": DK,
        })

    tabeller = {
        "kontakter": kontakter, "medlemskap": medlemskap, "medlemsbesok": medlemsbesok,
        "fordel_bruk": fordel_bruk, "gavekort": gavekort, "gavekort_bruk": gavekort_bruk,
        "arrangementer": arrangementer, "pameldinger": pameldinger,
        "skolebestillinger": skolebestillinger, "utleie": utleie, "henvendelser": henvendelser,
    }
    return {navn: [_som_tekst(r) for r in rader] for navn, rader in tabeller.items()}


def _som_tekst(rad: dict) -> dict:
    """Datoer lagres som ISO-tekst."""
    return {k: (v.isoformat() if isinstance(v, date) else v) for k, v in rad.items()}
