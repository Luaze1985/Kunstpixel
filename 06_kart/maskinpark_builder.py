"""Bygger 06_kart/maskinpark.json: maskiner, hendelser, vedlikehold og kommandologg (syntetisk, fast frø).

Skill: .claude/skills/maskinpark/SKILL.md. Kjør: py -3.13 06_kart/maskinpark_builder.py
Samme input gir byte-lik fil (testen sjekker SHA-256). Rom-ID-ene finnes i bygning_geometri.json.
"""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

UT = Path(__file__).resolve().parent / "maskinpark.json"
I_DAG = date(2026, 11, 22)
START_HENDELSER = I_DAG - timedelta(days=90)
FRO = 20261122

# Kommandoer med parametergrenser. Grenser som avhenger av rommet (klima, lys) sjekkes mot klimasonen.
ROBOT = {"send_til_rom": {"rom_id": "rom"}, "start_runde": {}, "pause": {}, "retur_til_lading": {}}
SERVER = {"restart_tjeneste": {"tjeneste": ["inferens", "mcp", "telemetri"]}, "sett_effektgrense": {"watt": [300, 700]}, "flytt_last": {}}
KLIMA = {"sett_klima": {"temperatur_c": "sone", "rf_prosent": "sone"}}
LYS = {"sett_lysniva": {"luks": "sone"}, "slukk_utenom_apningstid": {}}
SIKKERHET = {"kjor_selvtest": {}}

# (id, navn, kategori, type, rom, hjem, kritikalitet, intervall, leverandør, kommandoer, ki_tilgang)
MASKINER = [
    ("SRV-01", "GPU-node 1 (inferens)", "server", "gpu_node", "SRV-1", "SRV-1", "A", 90, "Nordlys Compute AS", SERVER, "foresla"),
    ("SRV-02", "GPU-node 2 (inferens)", "server", "gpu_node", "SRV-1", "SRV-1", "A", 90, "Nordlys Compute AS", SERVER, "foresla"),
    ("SRV-03", "GPU-node 3 (trening og test)", "server", "gpu_node", "SRV-1", "SRV-1", "B", 90, "Nordlys Compute AS", SERVER, "foresla"),
    ("SRV-04", "GPU-node 4 (øvingsdager)", "server", "gpu_node", "SRV-1", "SRV-1", "C", 90, "Nordlys Compute AS", SERVER, "foresla"),
    ("SRV-05", "Lagringsserver (samling og logg)", "server", "lagring", "SRV-1", "SRV-1", "A", 180, "Fjordlager Data AS", {"restart_tjeneste": {"tjeneste": ["telemetri"]}}, "foresla"),
    ("SRV-06", "Nettverkskjerne og brannmur", "server", "nettverk", "SRV-1", "SRV-1", "A", 180, "Fjordlager Data AS", {"restart_tjeneste": {"tjeneste": ["telemetri"]}}, "les"),
    ("SRV-07", "UPS for serverrommet", "server", "ups", "SRV-1", "SRV-1", "A", 180, "Stabil Kraft AS", {"test_batteri": {}}, "foresla"),
    ("SRV-08", "Kjøleenhet i rad (serverrom)", "server", "kjoler", "SRV-1", "SRV-1", "A", 90, "Stabil Kraft AS", {"sett_temperatur": {"temperatur_c": [18, 27]}}, "foresla"),
    ("REN-01", "Renholdsrobot 1 (1. etasje vest)", "robot", "renholdsrobot", "ROB-1", "ROB-1", "B", 60, "Ryddig Robotikk AS", ROBOT, "foresla"),
    ("REN-02", "Renholdsrobot 2 (1. etasje øst)", "robot", "renholdsrobot", "ROB-1", "ROB-1", "B", 60, "Ryddig Robotikk AS", ROBOT, "foresla"),
    ("REN-03", "Renholdsrobot 3 (2. etasje)", "robot", "renholdsrobot", "GANG-P2", "ROB-1", "B", 60, "Ryddig Robotikk AS", ROBOT, "foresla"),
    ("REN-04", "Renholdsrobot 4 (kjeller)", "robot", "renholdsrobot", "ROB-1", "ROB-1", "C", 60, "Ryddig Robotikk AS", ROBOT, "foresla"),
    ("VAK-01", "Vaktrobot 1 (nattrunde 1. etasje)", "robot", "vaktrobot", "ROB-1", "ROB-1", "B", 60, "Ugle Sikkerhetsrobot AS", ROBOT, "foresla"),
    ("VAK-02", "Vaktrobot 2 (nattrunde 2. etasje)", "robot", "vaktrobot", "ROB-1", "ROB-1", "B", 60, "Ugle Sikkerhetsrobot AS", ROBOT, "foresla"),
    ("TRA-01", "Transportrobot 1 (kunst, løft 400 kg)", "robot", "transportrobot", "ROB-1", "ROB-1", "A", 45, "Varsom Logistikk AS",
     {"flytt_verk": {"fra_rom": "rom", "til_rom": "rom"}, "retur_til_lading": {}}, "foresla"),
    ("TRA-02", "Transportrobot 2 (emballasje og utstyr)", "robot", "transportrobot", "ROB-1", "ROB-1", "B", 45, "Varsom Logistikk AS",
     {"flytt_verk": {"fra_rom": "rom", "til_rom": "rom"}, "retur_til_lading": {}}, "foresla"),
    ("LAD-01", "Ladestasjoner (6 plasser)", "anlegg", "lading", "ROB-1", "ROB-1", "C", 180, "Ryddig Robotikk AS", {"test_lading": {}}, "foresla"),
    ("ANL-01", "Ventilasjonsaggregat med varmegjenvinner", "anlegg", "ventilasjon", "TEK-1", "TEK-1", "A", 90, "Trøndelag Luft AS", {"sett_luftmengde": {"prosent": [40, 100]}}, "foresla"),
    ("ANL-02", "Dampbefukter", "anlegg", "befukter", "TEK-1", "TEK-1", "A", 90, "Trøndelag Luft AS", {"sett_ytelse": {"prosent": [0, 100]}}, "foresla"),
    ("ANL-03", "Kjølemaskin", "anlegg", "kjolemaskin", "TEK-1", "TEK-1", "A", 90, "Trøndelag Luft AS", {"sett_turtemperatur": {"temperatur_c": [6, 14]}}, "foresla"),
    ("ANL-04", "Klimastyring Magasin 1", "anlegg", "klimastyring", "MAG-1", "TEK-1", "A", 90, "Trøndelag Luft AS", KLIMA, "foresla"),
    ("ANL-05", "Klimastyring Magasin 2 (papirarkiv)", "anlegg", "klimastyring", "MAG-2", "TEK-1", "A", 90, "Trøndelag Luft AS", KLIMA, "foresla"),
    ("ANL-06", "Klimamontre Sal D (papirverk)", "anlegg", "klimastyring", "SAL-D", "TEK-1", "A", 90, "Trøndelag Luft AS", KLIMA, "foresla"),
    ("ANL-07", "Lysstyring Sal A", "anlegg", "lysstyring", "SAL-A", "TEK-1", "C", 365, "Lysverk Nord AS", LYS, "foresla"),
    ("ANL-08", "Lysstyring Sal B", "anlegg", "lysstyring", "SAL-B", "TEK-1", "C", 365, "Lysverk Nord AS", LYS, "foresla"),
    ("ANL-09", "Lysstyring Sal C", "anlegg", "lysstyring", "SAL-C", "TEK-1", "C", 365, "Lysverk Nord AS", LYS, "foresla"),
    ("ANL-10", "Lysstyring Sal D", "anlegg", "lysstyring", "SAL-D", "TEK-1", "B", 365, "Lysverk Nord AS", LYS, "foresla"),
    ("ANL-11", "Lysstyring Sal E", "anlegg", "lysstyring", "SAL-E", "TEK-1", "C", 365, "Lysverk Nord AS", LYS, "foresla"),
    ("SIK-01", "Inergen-sentral Magasin 1", "sikkerhet", "inergen", "MAG-1", "MAG-1", "A", 365, "Brannvern Midt AS", SIKKERHET, "les"),
    ("SIK-02", "Inergen-sentral Magasin 2", "sikkerhet", "inergen", "MAG-2", "MAG-2", "A", 365, "Brannvern Midt AS", SIKKERHET, "les"),
    ("SIK-03", "Inergen-sentral Kunstmottak", "sikkerhet", "inergen", "VER-1", "VER-1", "A", 365, "Brannvern Midt AS", SIKKERHET, "les"),
    ("SIK-04", "Inergen-sentral Teknisk rom", "sikkerhet", "inergen", "TEK-1", "TEK-1", "A", 365, "Brannvern Midt AS", SIKKERHET, "les"),
    ("SIK-05", "Adgangskontroll (kort, PIN og biometri)", "sikkerhet", "adgangskontroll", "SIK-P2", "SIK-P2", "A", 180, "Låsesmed Nidaros AS", SIKKERHET, "les"),
    ("SIK-06", "CCTV-opptak (48 kamera)", "sikkerhet", "cctv", "SIK-P2", "SIK-P2", "A", 180, "Låsesmed Nidaros AS", SIKKERHET, "les"),
    ("SIK-07", "Brannsentral med direktevarsling", "sikkerhet", "brannsentral", "VAK-1", "VAK-1", "A", 365, "Brannvern Midt AS", SIKKERHET, "les"),
    ("HEI-01", "Vare- og kunstheis (3,5 tonn)", "heis", "vareheis", "HEIS-U1", "HEIS-U1", "A", 90, "Løft Trondheim AS",
     {"kall_til_etasje": {"etasje": [0, 2]}, "sett_kunstmodus": {}}, "foresla"),
    ("HEI-02", "Publikumsheis", "heis", "publikumsheis", "HEIS-P1", "HEIS-P1", "B", 90, "Løft Trondheim AS",
     {"kall_til_etasje": {"etasje": [1, 2]}}, "foresla"),
]

# Hendelseskoder per type: (kode, alvorlighet, tekst)
KODER = {
    "gpu_node": [("GPU_TEMP_HOY", "varsel", "GPU-temperatur over 83 °C"), ("NODE_RESTART", "info", "Noden startet på nytt etter oppdatering")],
    "lagring": [("DISK_SMART", "varsel", "SMART-varsel på disk"), ("BACKUP_OK", "info", "Nattlig sikkerhetskopi fullført")],
    "nettverk": [("LINK_FLAP", "varsel", "Port gikk ned og opp"), ("FW_OPPDATERT", "info", "Brannmurregler oppdatert")],
    "ups": [("BATTERI_TEST_OK", "info", "Batteritest bestått")],
    "kjoler": [("TEMP_AVVIK", "varsel", "Tilluft over 25 °C")],
    "renholdsrobot": [("BATTERI_LAVT", "info", "Batteri under 15 %, kjørte til lading"), ("HJUL_BLOKKERT", "feil", "Hjul blokkert"), ("BORSTE_SLITT", "varsel", "Børste slitt")],
    "vaktrobot": [("NAVIGASJON_TAPT", "varsel", "Mistet posisjon, stoppet"), ("RUNDE_FULLFORT", "info", "Nattrunde fullført")],
    "transportrobot": [("LAST_SENSOR", "varsel", "Avvik på lastsensor"), ("OPPDRAG_FULLFORT", "info", "Transportoppdrag fullført")],
    "lading": [("LADER_FEIL", "varsel", "Ladeplass 4 svarer ikke")],
    "ventilasjon": [("FILTER_SKITTENT", "varsel", "Trykkfall over filter")],
    "befukter": [("VANNKVALITET", "varsel", "Ledningsevne høy i damptank")],
    "kjolemaskin": [("HOYTRYKK", "feil", "Høytrykksvakt løste ut")],
    "klimastyring": [("RF_AVVIK", "varsel", "Relativ fuktighet utenfor sonen"), ("TEMP_AVVIK", "varsel", "Temperatur utenfor sonen")],
    "lysstyring": [("LAMPE_DEFEKT", "info", "Spot defekt"), ("DALI_FEIL", "varsel", "DALI-buss svarer ikke")],
    "inergen": [("SELVTEST_OK", "info", "Ukentlig selvtest bestått"), ("TRYKK_LAVT", "varsel", "Flasketrykk under 95 %")],
    "adgangskontroll": [("SELVTEST_OK", "info", "Selvtest bestått"), ("DOR_HOLDT_APEN", "varsel", "Dør holdt åpen over 60 s")],
    "cctv": [("SELVTEST_OK", "info", "Selvtest bestått"), ("KAMERA_UTFALL", "varsel", "Kamera mistet bilde i 2 min")],
    "brannsentral": [("SELVTEST_OK", "info", "Selvtest bestått")],
    "vareheis": [("DORSENSOR", "varsel", "Dørsensor ustabil"), ("KUNSTMODUS", "info", "Kunstmodus brukt")],
    "publikumsheis": [("SERVICE_VARSEL", "info", "Service nærmer seg")],
}

# Faste scenarier som demoen og øvingsdagene bygger på (åpne hendelser nær i dag).
SCENARIER = [
    ("ANL-04", "2026-11-21T03:40", "RF_AVVIK", "varsel", "Magasin 1: RF 57 % (sone K1 er 50 % ± 5)"),
    ("SRV-02", "2026-11-22T06:12", "GPU_TEMP_HOY", "feil", "GPU-node 2 strupet ved 91 °C, inferens flyttet til node 1"),
    ("REN-03", "2026-11-22T05:55", "HJUL_BLOKKERT", "feil", "Renholdsrobot 3 står fast i gangen i 2. etasje"),
    ("SIK-01", "2026-11-20T09:00", "TRYKK_LAVT", "varsel", "Inergen Magasin 1: flasketrykk 94 %"),
]
KOSTNAD = {"server": 6500, "robot": 3200, "anlegg": 8900, "sikkerhet": 12000, "heis": 9500}
UTFORT_AV = {"server": "driftsansvarlig", "robot": "driftsansvarlig", "anlegg": "driftsansvarlig",
             "sikkerhet": "sikkerhetsansvarlig", "heis": "driftsansvarlig"}


def _ts(d: date, minutt: int) -> str:
    return (datetime(d.year, d.month, d.day) + timedelta(minutes=minutt)).strftime("%Y-%m-%dT%H:%M")


def bygg() -> dict:
    rng = random.Random(FRO)
    maskiner, hendelser, vedlikehold = [], [], []
    for (kort, navn, kat, typ, rom, hjem, krit, intervall, lev, kommandoer, tilgang) in MASKINER:
        mid = f"KP-MASK-{kort}"
        installert = date(2016, 6, 1) + timedelta(days=rng.randint(0, 3000))
        installert = min(installert, I_DAG - timedelta(days=200))
        # Siste service: noen få er forfalt (eldre enn intervallet).
        siden = rng.randint(5, intervall + 25)
        sist = I_DAG - timedelta(days=siden)
        maskiner.append({
            "maskin_id": mid, "navn": navn, "kategori": kat, "type": typ, "rom_id": rom, "hjem_rom_id": hjem,
            "kritikalitet": krit, "status": "i_drift", "leverandor": lev, "installert": installert.isoformat(),
            "serviceintervall_dager": intervall, "sist_service": sist.isoformat(), "kommandoer": kommandoer,
            "ki_tilgang": tilgang,
        })
        # Historiske hendelser (lukket) i 90 dager.
        for _ in range(rng.randint(1, 5)):
            kode, alv, tekst = rng.choice(KODER[typ])
            d = START_HENDELSER + timedelta(days=rng.randint(0, 85))
            hendelser.append({"maskin_id": mid, "tidspunkt": _ts(d, rng.randint(0, 1439)), "alvorlighet": alv,
                              "kode": kode, "beskrivelse": tekst, "lukket": True})
        # Forebyggende vedlikehold bakover fra siste service.
        d = sist
        while d >= date(2025, 1, 1):
            vedlikehold.append({"maskin_id": mid, "type": "forebyggende", "planlagt": d.isoformat(), "utfort": d.isoformat(),
                                "utfort_av_rolle": UTFORT_AV[kat], "kostnad_nok": KOSTNAD[kat],
                                "beskrivelse": f"Planlagt service ({intervall} dagers intervall)"})
            d -= timedelta(days=intervall)
        neste = sist + timedelta(days=intervall)
        if neste <= I_DAG + timedelta(days=30):
            vedlikehold.append({"maskin_id": mid, "type": "forebyggende", "planlagt": max(neste, I_DAG).isoformat(),
                                "utfort": None, "utfort_av_rolle": UTFORT_AV[kat], "kostnad_nok": KOSTNAD[kat],
                                "beskrivelse": "Planlagt service" + (" (forfalt)" if neste < I_DAG else "")})

    for kort, ts, kode, alv, tekst in SCENARIER:
        hendelser.append({"maskin_id": f"KP-MASK-{kort}", "tidspunkt": ts, "alvorlighet": alv, "kode": kode,
                          "beskrivelse": tekst, "lukket": False})
    # Korrektivt vedlikehold for lukkede feil.
    for h in hendelser:
        if h["lukket"] and h["alvorlighet"] in ("feil", "kritisk"):
            m = next(x for x in maskiner if x["maskin_id"] == h["maskin_id"])
            vedlikehold.append({"maskin_id": h["maskin_id"], "type": "korrektiv", "planlagt": h["tidspunkt"][:10],
                                "utfort": h["tidspunkt"][:10], "utfort_av_rolle": UTFORT_AV[m["kategori"]],
                                "kostnad_nok": KOSTNAD[m["kategori"]] // 2, "beskrivelse": f"Rettet: {h['beskrivelse']}"})
    # Renholdsrobot 3 er tatt ut til vedlikehold i dag.
    vedlikehold.append({"maskin_id": "KP-MASK-REN-03", "type": "korrektiv", "planlagt": I_DAG.isoformat(), "utfort": None,
                        "utfort_av_rolle": "driftsansvarlig", "kostnad_nok": 1600, "beskrivelse": "Frigjøre hjul og kalibrere"})

    hendelser.sort(key=lambda h: (h["tidspunkt"], h["maskin_id"]))
    for n, h in enumerate(hendelser, 1):
        h["hendelse_id"] = f"KP-HEN-{n:04d}"
    vedlikehold.sort(key=lambda v: (v["planlagt"], v["maskin_id"], v["type"]))
    for n, v in enumerate(vedlikehold, 1):
        v["arbeidsordre_id"] = f"KP-AO-{n:04d}"

    # Status fra åpne hendelser og pågående vedlikehold.
    for m in maskiner:
        apne = {h["alvorlighet"] for h in hendelser if h["maskin_id"] == m["maskin_id"] and not h["lukket"]}
        if any(v["maskin_id"] == m["maskin_id"] and v["utfort"] is None and v["planlagt"] == I_DAG.isoformat()
               and v["type"] == "korrektiv" for v in vedlikehold):
            m["status"] = "vedlikehold"
        elif apne & {"feil", "kritisk"}:
            m["status"] = "feil"
        elif "varsel" in apne:
            m["status"] = "varsel"

    kommandologg = [
        ("ANL-04", "sett_klima", {"temperatur_c": 18.0, "rf_prosent": 50}, "Rette RF-avvik i Magasin 1", "godkjent", "driftsansvarlig", "2026-11-21T06:10"),
        ("SRV-02", "flytt_last", {}, "GPU-node 2 går varm, flytt inferens til node 1", "utfort", "driftsansvarlig", "2026-11-22T06:20"),
        ("REN-03", "retur_til_lading", {}, "Robot står fast, hent den hjem", "avvist", "driftsansvarlig", "2026-11-22T06:05"),
        ("TRA-01", "flytt_verk", {"fra_rom": "MAG-1", "til_rom": "SAL-E"}, "Montering av høstutstillingen", "utfort", "driftsansvarlig", "2026-10-02T21:30"),
        ("VAK-01", "start_runde", {}, "Ekstra nattrunde etter alarm i Sal B", "utfort", "sikkerhetsansvarlig", "2026-11-14T02:15"),
        ("ANL-10", "sett_lysniva", {"luks": 50}, "Papirverk i Sal D, maks 50 luks", "godkjent", "driftsansvarlig", "2026-10-30T09:00"),
        ("ANL-01", "sett_luftmengde", {"prosent": 100}, "Mange besøkende under familiedag", "avvist", "driftsansvarlig", "2026-11-08T11:00"),
        ("SIK-01", "kjor_selvtest", {}, "Sjekk etter lavt flasketrykk", "utfort", "sikkerhetsansvarlig", "2026-11-20T10:00"),
    ]
    logg = [{"kommando_id": f"KP-KOM-{n:04d}", "maskin_id": f"KP-MASK-{k}", "kommando": c, "parametre": p,
             "foreslatt_av": "KI-agent (maskinpark)", "begrunnelse": b, "status": s, "besluttet_av_rolle": r, "tidspunkt": t}
            for n, (k, c, p, b, s, r, t) in enumerate(kommandologg, 1)]

    return {
        "datakilde": "syntetisk (maskinpark_builder, fast frø 20261122)",
        "versjon": 1,
        "i_dag": I_DAG.isoformat(),
        "apningstid": {"fra": "10:00", "til": "17:00"},
        "forbudte_kommandoer": ["deaktiver_slukking", "las_opp_dor", "sla_av_kamera", "sla_av_alarm",
                                "deaktiver_adgang", "overstyr_heis"],
        "maskiner": maskiner,
        "hendelser": [{"hendelse_id": h.pop("hendelse_id"), **h} for h in hendelser],
        "vedlikehold": [{"arbeidsordre_id": v.pop("arbeidsordre_id"), **v} for v in vedlikehold],
        "kommandologg": logg,
    }


def skriv(sti: Path = UT) -> Path:
    sti.write_text(json.dumps(bygg(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return sti


if __name__ == "__main__":
    p = skriv()
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"Skrev {p}: {len(d['maskiner'])} maskiner, {len(d['hendelser'])} hendelser, "
          f"{len(d['vedlikehold'])} arbeidsordrer, {len(d['kommandologg'])} kommandoer")
