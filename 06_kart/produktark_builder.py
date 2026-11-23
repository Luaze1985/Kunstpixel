"""Skriver produktark for maskinparken: ett ark per maskintype + en oversikt med dataflyten.

Kilde: 06_kart/maskinpark.json (fasit) og hendelseskodene i maskinpark_builder.py.
Mål: 04_knowledge/04_domain/operations/maskinpark/. Ikke rediger arkene for hånd; endre teksten her
og kjør: py -3.13 06_kart/produktark_builder.py (maskinpark_builder.py kjører den også).
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

KART = Path(__file__).resolve().parent
ROOT = KART.parent
UT = ROOT / "04_knowledge" / "04_domain" / "operations" / "maskinpark"

# Produkttekst per type: (produktnavn, hva den gjør, telemetri [(signal, enhet, intervall)], regler som gjelder)
PRODUKT: dict[str, tuple[str, str, list[tuple[str, str, str]], list[str]]] = {
    "gpu_node": ("GPU-node for KI", "Kjører språkmodellene, MCP-serveren og telemetrien lokalt i serverrommet. Ingen data forlater bygget.",
                 [("GPU-temperatur", "°C", "30 s"), ("Effektforbruk", "W", "30 s"), ("GPU-last", "%", "30 s"), ("Aktive tjenester", "liste", "60 s")],
                 ["SEC-M1"]),
    "lagring": ("Lagringsserver", "Lagrer samlingsdata, bilder og logger, og tar nattlig sikkerhetskopi.",
                [("Diskhelse (SMART)", "status", "1 t"), ("Ledig plass", "%", "15 min"), ("Siste sikkerhetskopi", "tidspunkt", "daglig")],
                ["SEC-M1"]),
    "nettverk": ("Nettverkskjerne og brannmur", "Knytter sammen servere, roboter og anlegg, og stenger alt som ikke er tillatt utenfra.",
                 [("Portstatus", "opp/ned", "10 s"), ("Trafikk", "Mbit/s", "60 s"), ("Brannmurregler", "versjon", "ved endring")],
                 ["SEC-M1", "Bare lesbar for KI: nettverket kan ikke styres av KI-en."]),
    "ups": ("UPS (avbruddsfri strøm)", "Holder serverrommet i drift ved strømbrudd til aggregatet tar over.",
            [("Batterinivå", "%", "60 s"), ("Belastning", "%", "60 s"), ("Siste batteritest", "resultat", "månedlig")],
            ["SEC-M1"]),
    "kjoler": ("Kjøleenhet i rad", "Kjøler serverrackene fra kald gang til varm gang.",
               [("Tilluft", "°C", "30 s"), ("Returluft", "°C", "30 s"), ("Viftehastighet", "%", "60 s")],
               ["SEC-M1"]),
    "renholdsrobot": ("Renholdsrobot", "Vasker og støvsuger publikumsarealer etter stengetid. Kjører selv til lading.",
                      [("Batteri", "%", "30 s"), ("Posisjon", "rom-ID", "5 s"), ("Børsteslitasje", "%", "per runde"), ("Hjulmotor", "status", "5 s")],
                      ["SEC-M1", "SEC-M5"]),
    "vaktrobot": ("Vaktrobot", "Går nattrunder med kamera og sensorer, og melder avvik til vaktrommet.",
                  [("Batteri", "%", "30 s"), ("Posisjon", "rom-ID", "2 s"), ("Runde", "framdrift i %", "per rom"), ("Kamera", "status", "10 s")],
                  ["SEC-M1", "SEC-M5"]),
    "transportrobot": ("Transportrobot", "Frakter kunstkasser, emballasje og utstyr mellom magasin, kunstmottak og saler.",
                       [("Batteri", "%", "30 s"), ("Posisjon", "rom-ID", "2 s"), ("Last", "kg", "1 s"), ("Støt og vibrasjon", "g", "1 s")],
                       ["SEC-M1", "SEC-M4"]),
    "hengerobot": ("Hengerobot for bildebytte", "Mobil robotarm med polstret rammegriper. Tar ned og henger opp malerier i salene, og legger dem i en kunstkasse. En konservator er alltid til stede.",
                   [("Gripekraft", "N", "50 ms"), ("Armposisjon", "mm", "50 ms"), ("Last i griperen", "kg", "50 ms"), ("Batteri", "%", "30 s")],
                   ["SEC-M1", "SEC-M4"]),
    "kunstkasse": ("Selvkjørende kunstkasse", "Klimastyrt kasse på eget hjulunderstell. Kjører et pakket verk fra salen til magasinet via vareheisen.",
                   [("RF i kassen", "%", "60 s"), ("Temperatur i kassen", "°C", "60 s"), ("Støt og vibrasjon", "g", "1 s"), ("Posisjon", "rom-ID", "2 s"), ("Lokk", "låst/åpent", "ved endring")],
                   ["SEC-M1", "SEC-M4"]),
    "lading": ("Ladestasjoner", "Lader robotene i robotgarasjen.",
               [("Ladeplass i bruk", "plass-nr.", "ved endring"), ("Ladeeffekt", "W", "60 s"), ("Feil på lader", "status", "ved endring")],
               ["SEC-M1"]),
    "ventilasjon": ("Ventilasjonsaggregat", "Gir frisk luft til hele bygget og gjenvinner varmen.",
                    [("Luftmengde", "%", "60 s"), ("Trykkfall over filter", "Pa", "5 min"), ("Tilluftstemperatur", "°C", "60 s")],
                    ["SEC-M1"]),
    "befukter": ("Dampbefukter", "Holder fuktigheten oppe om vinteren, så kunsten ikke tørker ut.",
                 [("Ytelse", "%", "60 s"), ("Ledningsevne i damptank", "µS/cm", "15 min")],
                 ["SEC-M1"]),
    "kjolemaskin": ("Kjølemaskin", "Lager kaldt vann til ventilasjon og serverrom.",
                    [("Turtemperatur", "°C", "60 s"), ("Returtemperatur", "°C", "60 s"), ("Høytrykksvakt", "status", "ved endring")],
                    ["SEC-M1"]),
    "klimastyring": ("Klimastyring per sone", "Styrer temperatur og fukt i magasiner og montre etter klimasonen til rommet.",
                     [("Temperatur", "°C", "60 s"), ("Relativ fuktighet", "%", "60 s"), ("Settpunkt", "°C og %", "ved endring")],
                     ["SEC-M1", "SEC-M3"]),
    "lysstyring": ("Lysstyring (DALI)", "Styrer spotter og arbeidslys i salene, og slukker utenom åpningstid.",
                   [("Lysnivå på verk", "luks", "60 s"), ("UV-andel", "µW/lm", "15 min"), ("DALI-buss", "status", "10 s")],
                   ["SEC-M1", "SEC-M3"]),
    "inergen": ("Inergen-slokkeanlegg", "Slokker brann med inert gass uten vann, så kunsten ikke skades.",
                [("Flasketrykk", "%", "15 min"), ("Selvtest", "resultat", "ukentlig"), ("Utløst", "ja/nei", "ved endring")],
                ["SEC-M1", "SEC-M2", "Bare lesbar for KI: bare selvtest kan foreslås."]),
    "adgangskontroll": ("Adgangskontroll", "Kort, PIN og biometri på dører til magasiner, kunstmottak og teknikk.",
                        [("Dørhendelser", "inn/ut", "ved endring"), ("Dør holdt åpen", "sekunder", "ved endring"), ("Selvtest", "resultat", "daglig")],
                        ["SEC-M1", "SEC-M2", "Bare lesbar for KI: bare selvtest kan foreslås."]),
    "cctv": ("Kameraovervåking (CCTV)", "Tar opp bilde fra 48 kamera og viser dem på videoveggen i vaktrommet.",
             [("Kamerastatus", "per kamera", "10 s"), ("Lagringstid igjen", "døgn", "1 t")],
             ["SEC-M1", "SEC-M2", "Bare lesbar for KI: bare selvtest kan foreslås."]),
    "brannsentral": ("Brannsentral", "Samler branndetektorene og varsler brannvesenet direkte.",
                     [("Detektorstatus", "per sløyfe", "10 s"), ("Alarm", "ja/nei", "ved endring"), ("Selvtest", "resultat", "daglig")],
                     ["SEC-M1", "SEC-M2", "Bare lesbar for KI: bare selvtest kan foreslås."]),
    "vareheis": ("Vare- og kunstheis", "Godsheis på 3,5 tonn fra kunstmottaket til alle etasjer. Kunstmodus gir myk start og stopp.",
                 [("Etasje", "nr.", "ved endring"), ("Dørsensor", "status", "ved endring"), ("Last", "kg", "ved endring"), ("Kunstmodus", "på/av", "ved endring")],
                 ["SEC-M1", "SEC-M2"]),
    "publikumsheis": ("Publikumsheis", "Glassheis for besøkende mellom 1. og 2. etasje.",
                      [("Etasje", "nr.", "ved endring"), ("Turer per dag", "antall", "daglig")],
                      ["SEC-M1", "SEC-M2"]),
}

REGELTEKST = {
    "SEC-M1": "KI-en utfører aldri. Den foreslår, og et menneske godkjenner og utfører.",
    "SEC-M2": "Forbudte kommandoer avvises alltid (slå av slokking, alarm, kamera eller adgang, låse opp S4, overstyre heis).",
    "SEC-M3": "Settpunkt må ligge innenfor klimasonen til rommet.",
    "SEC-M4": "Kunst flyttes bare utenom åpningstid (17:00–10:00), med to personer ved S4 og via vareheisen mellom etasjer.",
    "SEC-M5": "Kjører ikke inn i sikringssone S4. Til annen etasje via vareheisen.",
}
KATEGORINAVN = {"server": "KI-servere", "robot": "Roboter", "anlegg": "Bygningsanlegg", "sikkerhet": "Sikkerhet", "heis": "Heiser"}
KUNSTKOMMANDOER = {"flytt_verk", "ta_ned_verk", "heng_opp_verk", "pakk_verk", "kjor_kasse_til_magasin"}


def _builder():
    spec = importlib.util.spec_from_file_location("kp_maskinpark_builder_ark", KART / "maskinpark_builder.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _grenser(tekst: str) -> tuple[float, float]:
    tall = [float(t.replace(",", ".")) for t in re.findall(r"\d+(?:[.,]\d+)?", tekst)]
    if "±" in tekst:
        return tall[0] - tall[1], tall[0] + tall[1]
    if tekst.lower().startswith("maks"):
        return 0.0, tall[0]
    return tall[0], tall[1]


def _regel(regel, navn: str, sone: str) -> str:
    if regel == "rom":
        return "rom-ID som finnes i bygget"
    if regel == "sal":
        return "en utstillingssal (SAL-A … SAL-E)"
    if regel == "kasse":
        return "maskin-ID til en kunstkasse"
    if regel == "sone":
        return f"innenfor klimasonen {sone}"
    if isinstance(regel, list) and regel and isinstance(regel[0], str):
        return "én av " + ", ".join(f"`{v}`" for v in regel)
    if isinstance(regel, list):
        return f"{regel[0]}–{regel[1]}"
    return str(regel)


def _eksempel(navn: str, regel, sone: str, klima: dict):
    if regel in ("rom", "sal"):
        return {"rom_id": "SAL-B", "fra_rom": "SAL-B", "til_rom": "SAL-E"}.get(navn, "SAL-B")
    if regel == "kasse":
        return "KP-MASK-KAS-01"
    if regel == "sone":
        felt = {"temperatur_c": "temp", "rf_prosent": "rf", "luks": "luks"}[navn]
        lav, hoy = _grenser(klima[sone][felt])
        return hoy if navn == "luks" else round((lav + hoy) / 2, 1)
    if isinstance(regel, list) and regel and isinstance(regel[0], str):
        return regel[0]
    if isinstance(regel, list):
        return int((regel[0] + regel[1]) / 2)
    return None


def _neste_service(m: dict) -> str:
    from datetime import date, timedelta
    return (date.fromisoformat(m["sist_service"]) + timedelta(days=m["serviceintervall_dager"])).isoformat()


def _ark(typ: str, maskiner: list[dict], data: dict, rom: dict, klima: dict, koder: list) -> str:
    navn, hva, telemetri, regler = PRODUKT[typ]
    f = maskiner[0]
    apne = {m["maskin_id"]: sum(1 for h in data["hendelser"] if h["maskin_id"] == m["maskin_id"] and not h["lukket"])
            for m in maskiner}
    linjer = [
        f"# {navn} (`{typ}`)",
        "",
        "> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.",
        "",
        hva,
        "",
        "| Felt | Verdi |",
        "|---|---|",
        f"| Kategori | {KATEGORINAVN[f['kategori']]} (`{f['kategori']}`) |",
        f"| Leverandør (fiktiv) | {f['leverandor']} |",
        f"| Serviceintervall | {f['serviceintervall_dager']} dager |",
        f"| KI-tilgang | `{f['ki_tilgang']}` ({'kan bare lese' if f['ki_tilgang'] == 'les' else 'kan lese og foreslå kommandoer'}) |",
        "",
        "## Enheter i Kunstpixel",
        "",
        "| Maskin-ID | Navn | Står i | Kritikalitet | Status | Åpne hendelser | Neste service | Godkjennes av |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for m in maskiner:
        r = rom[m["rom_id"]]
        godkj = "driftsansvarlig" + (" + sikkerhetsansvarlig" if m["kritikalitet"] == "A" or m["kategori"] == "sikkerhet" else "")
        linjer.append(f"| `{m['maskin_id']}` | {m['navn']} | {r['navn']} (`{m['rom_id']}`, {r['etasje']}) | {m['kritikalitet']} "
                      f"| {m['status']} | {apne[m['maskin_id']]} | {_neste_service(m)} | {godkj} |")
    linjer += [
        "",
        "## Datastrøm",
        "",
        "Dette sender maskinen til driftsplattformen. I demoen er strømmen syntetisk: det som er lagret, er hendelsene i "
        "`maskinpark.json`.",
        "",
        "| Signal | Enhet | Hvor ofte |",
        "|---|---|---|",
    ]
    linjer += [f"| {s} | {e} | {i} |" for s, e, i in telemetri]
    linjer += ["", "**Hendelseskoder** (havner i `hendelser[]`):", "", "| Kode | Alvorlighet | Betyr |", "|---|---|---|"]
    linjer += [f"| `{k}` | {a} | {t} |" for k, a, t in koder]
    linjer += [
        "",
        "## Slik følger du den",
        "",
        f"1. Hele typen: `get_machine_park(kategori=\"{f['kategori']}\")`, og se på radene med type `{typ}`.",
        f"2. Én enhet: `get_machine_health(maskin_id=\"{f['maskin_id']}\")` gir status, åpne og siste hendelser, "
        "arbeidsordrer, neste service og kommandologg.",
        "3. Service fremover: `get_maintenance_plan(dager=30)`.",
        "4. I kartet: `06_kart/index.html`, sonen **Maskiner**.",
        "",
        "## Slik styrer du den",
        "",
    ]
    if f["kommandoer"]:
        linjer += ["| Kommando | Parametre og grenser |", "|---|---|"]
        sone = rom[f["rom_id"]]["klimasone"]
        for k, param in f["kommandoer"].items():
            tekst = "; ".join(f"`{p}`: {_regel(r, p, sone)}" for p, r in param.items()) or "ingen"
            linjer.append(f"| `{k}` | {tekst} |")
        lov = [(k, p) for k, p in f["kommandoer"].items()
               if f["ki_tilgang"] == "foresla" or k.startswith(("kjor_selvtest", "test_"))]
        if lov:
            k, param = lov[0]
            eks = {p: _eksempel(p, r, sone, klima) for p, r in param.items()}
            kall = {"maskin_id": f["maskin_id"], "kommando": k, "parametre": eks}
            if k in KUNSTKOMMANDOER:
                kall["tidspunkt"] = "2026-11-23T21:00"
            linjer += ["", "Eksempel på forslag (KI-en sender, et menneske godkjenner):", "", "```json",
                       json.dumps(kall, ensure_ascii=False), "```", "",
                       "Svaret har `status: \"venter_godkjenning\"` eller `\"avvist\"` med grunner. Ingenting blir utført av "
                       "verktøyet (`propose_machine_command`)."]
        else:
            linjer += ["", "KI-en kan ikke foreslå noen av disse kommandoene; de gjøres av et menneske. "
                       "`propose_machine_command` avviser dem."]
    linjer += ["", "**Regler som gjelder:**", ""]
    linjer += [f"- **{r}:** {REGELTEKST[r]}" if r in REGELTEKST else f"- {r}" for r in regler]
    return "\n".join(linjer) + "\n"


def _oversikt(per_type: dict[str, list[dict]]) -> str:
    linjer = [
        "# Maskinparken – produktark",
        "",
        "> Generert av `06_kart/produktark_builder.py` fra `06_kart/maskinpark.json`. Ikke rediger for hånd.",
        "",
        "Ett ark per maskintype. Hvert ark viser hvor enhetene står, hvilke data de sender, hvordan du følger dem og hvilke "
        "kommandoer KI-en kan foreslå. Reglene og skillen står i `.claude/skills/maskinpark/SKILL.md`.",
        "",
        "## Dataflyten",
        "",
        "```mermaid",
        "flowchart LR",
        "  M[Maskin] -->|telemetri| P[Driftsplattform]",
        "  P -->|hendelser| J[(maskinpark.json)]",
        "  J --> V[MCP: get_machine_park, get_machine_health, get_maintenance_plan]",
        "  V --> K[KI-agent]",
        "  K -->|propose_machine_command| R{Regelsjekk SEC-M1..M5}",
        "  R -->|avvist + grunner| K",
        "  R -->|venter_godkjenning| G[Menneske godkjenner]",
        "  G -->|utfører selv| M",
        "  G --> L[(kommandologg)]",
        "```",
        "",
        "## Kunst fra sal til magasin",
        "",
        "1. `hengerobot` tar ned verket i salen (`ta_ned_verk`) med konservator til stede.",
        "2. `hengerobot` legger verket i en `kunstkasse` (`pakk_verk`).",
        "3. `kunstkasse` kjører selv til magasinet via vareheisen i kunstmodus (`kjor_kasse_til_magasin`), med to personer ved S4.",
        "",
        "Alt skjer utenom åpningstid, og hvert steg er et eget forslag som må godkjennes.",
        "",
        "## Alle typer",
        "",
        "| Produkt | Kategori | Antall | KI-tilgang | Ark |",
        "|---|---|---|---|---|",
    ]
    for typ, ms in sorted(per_type.items(), key=lambda t: (t[1][0]["kategori"], t[0])):
        linjer.append(f"| {PRODUKT[typ][0]} | {KATEGORINAVN[ms[0]['kategori']]} | {len(ms)} | `{ms[0]['ki_tilgang']}` "
                      f"| [{typ}]({typ}.md) |")
    linjer += ["", f"Totalt {sum(len(m) for m in per_type.values())} maskiner av {len(per_type)} typer."]
    return "\n".join(linjer) + "\n"


def lag_alle() -> dict[str, str]:
    data = json.loads((KART / "maskinpark.json").read_text(encoding="utf-8"))
    g = json.loads((KART / "bygning_geometri.json").read_text(encoding="utf-8"))
    rom = {r["id"]: {**r, "etasje": e["kode"]} for e in g["etasjer"] for r in e["rom"]}
    klima = g["soner_definisjon"]["klima"]
    koder = _builder().KODER
    per_type: dict[str, list[dict]] = {}
    for m in data["maskiner"]:
        per_type.setdefault(m["type"], []).append(m)
    mangler = set(per_type) - set(PRODUKT)
    if mangler:
        raise ValueError(f"Mangler produkttekst for: {sorted(mangler)}")
    filer = {f"{typ}.md": _ark(typ, ms, data, rom, klima, koder[typ]) for typ, ms in per_type.items()}
    filer["README.md"] = _oversikt(per_type)
    return filer


def skriv_alle(mappe: Path = UT) -> list[Path]:
    mappe.mkdir(parents=True, exist_ok=True)
    skrevet = []
    for navn, innhold in lag_alle().items():
        p = mappe / navn
        p.write_text(innhold, encoding="utf-8", newline="\n")
        skrevet.append(p)
    return skrevet


if __name__ == "__main__":
    filer = skriv_alle()
    print(f"Skrev {len(filer)} produktark til {UT}")
