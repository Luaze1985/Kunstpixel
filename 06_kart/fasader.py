"""Fasade- og snittegninger fra bygningsmodellen (06_kart/bygning_geometri.json).

Lager fasade_sor.svg, fasade_ost.svg, snitt_a.svg (gjennom hovedfløyen) og snitt_b.svg (gjennom glassfløyen).
Målestokk 1:100: 10 enheter = 1 m både horisontalt og vertikalt. Høyder er koter (moh) fra modellen.
Kalles fra build_map.build(); kan også kjøres alene: py -3.13 06_kart/fasader.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BUNN = 345          # svg-y for laveste kote i tegningen
KOTE_MIN = 8.6      # under kjellergulvet
DEKKE = 0.3         # etasjeskiller, m


def _y(kote: float) -> float:
    return round(BUNN - (kote - KOTE_MIN) * 10, 1)


def _kote(v: float) -> str:
    return f"+{v:.2f}".replace(".", ",")


def _mm(enheter: float) -> str:
    return f"{int(enheter * 100):,} mm".replace(",", " ")


def snitt_x(modell: dict, navn: str) -> float:
    """Snittlinja: midt i hovedfløyen (A) eller glassfløyen (B), i modellkoordinater."""
    hoved, glass = modell["museum"]["fotavtrykk"]["volumer"]
    v = hoved if navn.startswith("snitt_a") else glass
    return v["x"] + v["b"] / 2


def _start(bredde: int, tittel: str, under: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {bredde} 400" width="100%" height="100%" class="fasade-svg">',
        '  <defs>',
        '    <pattern id="tegl" width="6" height="3" patternUnits="userSpaceOnUse"><rect width="6" height="3" fill="#7f1d1d"/>'
        '<line x1="0" y1="3" x2="6" y2="3" stroke="#991b1b" stroke-width="0.5"/></pattern>',
        '    <pattern id="jord" width="8" height="8" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
        '<line x1="0" y1="0" x2="0" y2="8" stroke="rgba(148,163,184,0.25)" stroke-width="1"/></pattern>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#0a0f1d"/>',
        f'  <text x="30" y="34" font-family="sans-serif" font-size="18" font-weight="bold" fill="#ffffff">KUNSTPIXEL · {html.escape(tittel)}</text>',
        f'  <text x="30" y="54" font-family="sans-serif" font-size="10.5" fill="#94a3b8">{html.escape(under)}</text>',
        f'  <text x="{bredde - 30}" y="34" font-family="sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="end">MÅLESTOKK 1:100</text>',
    ]


def _koter(modell: dict, x0: float, x1: float, med_u1: bool) -> list[str]:
    m = modell["museum"]["matrikkel"]
    koter = [(m["kote_gesims_moh"], "gesims"), (m["kote_p2_fg_moh"], "P2 FG"), (m["kote_p1_fg_moh"], "P1 FG"),
             (m["kote_terreng_moh"], "terreng")]
    if med_u1:
        koter.append((m["kote_u1_fg_moh"], "U1 FG"))
    ut = ['  <g class="koter">']
    forrige = None
    for v, navn in koter:
        y = _y(v)
        # To koter tett i tett (P1 FG og terreng): flytt teksten til den nederste ned.
        tekst_y = y + 3 if forrige is None or abs(forrige - y) > 9 else forrige + 13
        forrige = tekst_y - 3
        ut.append(f'    <line x1="{x0}" y1="{y}" x2="{x1 + 12}" y2="{y}" stroke="rgba(56,189,248,0.35)" stroke-width="0.6" stroke-dasharray="3,3"/>')
        ut.append(f'    <polygon points="{x1 + 12},{y} {x1 + 18},{y - 5} {x1 + 6},{y - 5}" fill="#38bdf8"/>')
        ut.append(f'    <text x="{x1 + 22}" y="{tekst_y}" font-family="sans-serif" font-size="9.5" fill="#bae6fd">{_kote(v)} {navn}</text>')
    ut.append('  </g>')
    return ut


def _terreng(x0: float, x1: float, kote: float, kjeller_fra: float | None = None) -> list[str]:
    y = _y(kote)
    ut = [f'  <rect x="{x0 - 40}" y="{y}" width="{x1 - x0 + 80}" height="{BUNN + 30 - y}" fill="url(#jord)"/>',
          f'  <line class="terreng" x1="{x0 - 40}" y1="{y}" x2="{x1 + 40}" y2="{y}" stroke="#a3a3a3" stroke-width="1.6"/>']
    return ut


def _malkjede(x0: float, x1: float, y: float, tekst: str) -> list[str]:
    return [f'  <line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#64748b" stroke-width="0.8"/>',
            f'  <line x1="{x0}" y1="{y - 4}" x2="{x0}" y2="{y + 4}" stroke="#38bdf8" stroke-width="1.2" transform="rotate(45 {x0} {y})"/>',
            f'  <line x1="{x1}" y1="{y - 4}" x2="{x1}" y2="{y + 4}" stroke="#38bdf8" stroke-width="1.2" transform="rotate(45 {x1} {y})"/>',
            f'  <text x="{(x0 + x1) / 2}" y="{y - 5}" font-family="sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle">{tekst}</text>']


def _mansard(x0: float, x1: float, gesims: float, topp: float) -> str:
    inn = 20  # 2 m innrykk
    return (f'  <polygon class="mansardtak" points="{x0},{_y(gesims)} {x0 + inn},{_y(topp)} {x1 - inn},{_y(topp)} {x1},{_y(gesims)}" '
            f'fill="#0f766e" stroke="#5eead4" stroke-width="1"/>')


def fasade_sor(modell: dict) -> str:
    m = modell["museum"]["matrikkel"]
    hoved, glass = modell["museum"]["fotavtrykk"]["volumer"]
    off = 80
    X = lambda x: x + off
    x0, x1 = X(hoved["x"]), X(glass["x"] + glass["b"])
    svg = _start(1000, "FASADE SØR (mot Bispegata)", f'{hoved["navn"]} i tegl og {glass["navn"].lower()} i glass · koter i moh')
    svg += _terreng(x0, x1, m["kote_terreng_moh"])
    # Hovedfløy
    hx0, hx1 = X(hoved["x"]), X(hoved["x"] + hoved["b"])
    svg.append(f'  <rect class="vegg-tegl" x="{hx0}" y="{_y(m["kote_gesims_moh"])}" width="{hoved["b"]}" '
               f'height="{_y(m["kote_terreng_moh"]) - _y(m["kote_gesims_moh"])}" fill="url(#tegl)" stroke="#fca5a5" stroke-width="0.8"/>')
    svg.append(f'  <rect class="sokkel" x="{hx0}" y="{_y(m["kote_p1_fg_moh"] + 1.0)}" width="{hoved["b"]}" '
               f'height="{_y(m["kote_terreng_moh"]) - _y(m["kote_p1_fg_moh"] + 1.0)}" fill="#64748b"/>')
    svg.append(_mansard(hx0, hx1, m["kote_gesims_moh"], hoved["tak_topp_moh"]))
    res = next(r for e in modell["etasjer"] for r in e["rom"] if r["id"] == "RES-1")
    dor_x = X(res["x"] + res["w"] / 2)
    for fg in (m["kote_p1_fg_moh"], m["kote_p2_fg_moh"]):
        for wx in range(int(hx0) + 25, int(hx1) - 20, 40):
            if fg == m["kote_p1_fg_moh"] and abs(wx + 7 - dor_x) < 30:
                continue
            svg.append(f'  <rect class="vindu" x="{wx}" y="{_y(fg + 4.0)}" width="14" height="{_y(fg + 1.2) - _y(fg + 4.0)}" fill="#1e3a5f" stroke="#e2e8f0" stroke-width="0.8"/>')
    svg.append(f'  <rect class="hovedinngang" x="{dor_x - 12}" y="{_y(m["kote_p1_fg_moh"] + 3.6)}" width="24" '
               f'height="{_y(m["kote_p1_fg_moh"]) - _y(m["kote_p1_fg_moh"] + 3.6)}" fill="#78350f" stroke="#fde68a" stroke-width="1"/>')
    svg.append(f'  <polygon class="trapp" points="{dor_x - 30},{_y(m["kote_terreng_moh"])} {dor_x - 16},{_y(m["kote_p1_fg_moh"])} '
               f'{dor_x + 16},{_y(m["kote_p1_fg_moh"])} {dor_x + 30},{_y(m["kote_terreng_moh"])}" fill="#94a3b8"/>')
    # Glassfløy
    gx0, gx1 = X(glass["x"]), X(glass["x"] + glass["b"])
    svg.append(f'  <rect class="vegg-glass" x="{gx0}" y="{_y(glass["tak_topp_moh"])}" width="{glass["b"]}" '
               f'height="{_y(m["kote_terreng_moh"]) - _y(glass["tak_topp_moh"])}" fill="rgba(56,189,248,0.25)" stroke="#38bdf8" stroke-width="1"/>')
    for sx in range(int(gx0) + 15, int(gx1), 15):
        svg.append(f'  <line class="spile" x1="{sx}" y1="{_y(glass["tak_topp_moh"])}" x2="{sx}" y2="{_y(m["kote_terreng_moh"])}" stroke="#d6a868" stroke-width="1.2"/>')
    svg.append(f'  <line x1="{gx0}" y1="{_y(m["kote_p2_fg_moh"])}" x2="{gx1}" y2="{_y(m["kote_p2_fg_moh"])}" stroke="#38bdf8" stroke-width="0.8"/>')
    svg += _malkjede(x0, x1, _y(hoved["tak_topp_moh"]) - 40, f"{_mm(glass['x'] + glass['b'] - hoved['x'])}")
    svg += _malkjede(hx0, hx1, _y(hoved["tak_topp_moh"]) - 20, f"{_mm(hoved['b'])} · {hoved['byggeaar']}")
    svg += _malkjede(gx0, gx1, _y(hoved["tak_topp_moh"]) - 20, f"{_mm(glass['b'])} · {glass['byggeaar']}")
    svg += _koter(modell, x0, x1, med_u1=False)
    svg.append(f'  <text x="{dor_x}" y="{_y(m["kote_terreng_moh"]) + 18}" font-family="sans-serif" font-size="9" fill="#fde68a" text-anchor="middle">HOVEDINNGANG</text>')
    svg.append('</svg>')
    return "\n".join(svg)


def fasade_ost(modell: dict) -> str:
    m = modell["museum"]["matrikkel"]
    hoved, glass = modell["museum"]["fotavtrykk"]["volumer"]
    off = 180
    Y = lambda y: y - hoved["y"] + off
    x0, x1 = Y(glass["y"]), Y(glass["y"] + glass["d"])
    svg = _start(760, "FASADE ØST (mot Nidelva)", "Glassfløyen foran, mansardtaket på hovedfløyen bak · nord til venstre")
    svg += _terreng(x0, x1, m["kote_terreng_moh"])
    svg.append(f'  <polygon class="mansardtak" points="{x0 + 4},{_y(m["kote_gesims_moh"])} {x0 + 24},{_y(hoved["tak_topp_moh"])} '
               f'{x1 - 24},{_y(hoved["tak_topp_moh"])} {x1 - 4},{_y(m["kote_gesims_moh"])}" fill="#0f766e" stroke="#5eead4" stroke-width="1" opacity="0.8"/>')
    svg.append(f'  <rect class="vegg-glass" x="{x0}" y="{_y(glass["tak_topp_moh"])}" width="{glass["d"]}" '
               f'height="{_y(m["kote_terreng_moh"]) - _y(glass["tak_topp_moh"])}" fill="rgba(56,189,248,0.25)" stroke="#38bdf8" stroke-width="1"/>')
    for sx in range(int(x0) + 12, int(x1), 12):
        svg.append(f'  <line class="spile" x1="{sx}" y1="{_y(glass["tak_topp_moh"])}" x2="{sx}" y2="{_y(m["kote_terreng_moh"])}" stroke="#d6a868" stroke-width="1.2"/>')
    svg.append(f'  <line x1="{x0}" y1="{_y(m["kote_p2_fg_moh"])}" x2="{x1}" y2="{_y(m["kote_p2_fg_moh"])}" stroke="#38bdf8" stroke-width="0.8"/>')
    svg.append(f'  <text x="{(x0 + x1) / 2}" y="{_y(m["kote_p1_fg_moh"] + 2)}" font-family="sans-serif" font-size="9" fill="#e0f2fe" text-anchor="middle">NØDUTGANG / KAFÉ</text>')
    svg += _malkjede(x0, x1, _y(hoved["tak_topp_moh"]) - 20, _mm(glass["d"]))
    svg += _koter(modell, x0, x1, med_u1=False)
    svg.append(f'  <text x="{x0 - 30}" y="{_y(m["kote_terreng_moh"]) - 6}" font-family="sans-serif" font-size="9" fill="#64748b" text-anchor="end">NORD · bakgård</text>')
    svg.append(f'  <text x="{x1 + 120}" y="{_y(m["kote_terreng_moh"]) + 22}" font-family="sans-serif" font-size="9" fill="#64748b">SØR · Bispegata</text>')
    svg.append('</svg>')
    return "\n".join(svg)


def snitt(modell: dict, navn: str) -> str:
    m = modell["museum"]["matrikkel"]
    hoved, glass = modell["museum"]["fotavtrykk"]["volumer"]
    v = hoved if navn.startswith("snitt_a") else glass
    x = snitt_x(modell, navn)
    off = 180
    Y = lambda y: y - v["y"] + off
    y0, y1 = Y(v["y"]), Y(v["y"] + v["d"])
    bokstav = "A–A" if navn.startswith("snitt_a") else "B–B"
    svg = _start(760, f"SNITT {bokstav}", f'Nord–sør gjennom {v["navn"].lower()} (x = {x / 10 - 4:.1f} m fra vestfasaden) · nord til venstre')
    svg += _terreng(y0, y1, m["kote_terreng_moh"])
    # Kjeller under terreng: vegg og fundament
    svg.append(f'  <rect x="{y0}" y="{_y(m["kote_terreng_moh"])}" width="{y1 - y0}" height="{_y(m["kote_u1_fg_moh"] - DEKKE) - _y(m["kote_terreng_moh"])}" fill="#0a0f1d" stroke="#94a3b8" stroke-width="1.2"/>')
    fg = {e["kode"]: e["kote_moh"] for e in modell["etasjer"]}
    tak = {"U1": fg["P1"], "P1": fg["P2"], "P2": m["kote_gesims_moh"]}
    # Bygningskropp over terreng
    svg.append(f'  <rect x="{y0}" y="{_y(m["kote_gesims_moh"])}" width="{y1 - y0}" height="{_y(m["kote_terreng_moh"]) - _y(m["kote_gesims_moh"])}" '
               f'fill="none" stroke="{"#fca5a5" if v["materiale"] == "tegl" else "#38bdf8"}" stroke-width="2"/>')
    for e in modell["etasjer"]:
        k = e["kote_moh"]
        svg.append(f'  <rect class="dekke" x="{y0}" y="{_y(k)}" width="{y1 - y0}" height="{DEKKE * 10}" fill="#94a3b8"/>')
        for r in e["rom"]:
            if not r["x"] < x < r["x"] + r["w"]:
                continue
            ry0, ry1 = Y(r["y"]), Y(r["y"] + r["h"])
            topp = min(k + r.get("takhoyde_m", 3.0), tak[e["kode"]] - DEKKE)
            smal = (ry1 - ry0) < 40
            kort = r.get("romnavn_kort", r["navn"]).split("–")[0].strip()
            tittel = r["romnummer"] if smal else next(
                (t for t in (kort, kort.split()[0]) if len(t) * 8 * 0.62 <= ry1 - ry0 - 6), r["romnummer"])
            svg.append(f'  <g class="snittrom" data-room-id="{r["id"]}">')
            svg.append(f'    <rect x="{ry0}" y="{_y(topp)}" width="{ry1 - ry0}" height="{_y(k + DEKKE) - _y(topp)}" fill="rgba(51,65,85,0.35)" stroke="#475569" stroke-width="0.8"/>')
            rot = f' transform="rotate(-90 {(ry0 + ry1) / 2} {(_y(topp) + _y(k)) / 2})"' if smal else ""
            svg.append(f'    <text x="{(ry0 + ry1) / 2}" y="{(_y(topp) + _y(k)) / 2 + 3}" font-family="sans-serif" font-size="8" fill="#e2e8f0" text-anchor="middle"{rot}>{html.escape(tittel)}</text>')
            svg.append('  </g>')
    svg.append(f'  <rect class="dekke" x="{y0}" y="{_y(m["kote_gesims_moh"])}" width="{y1 - y0}" height="{DEKKE * 10}" fill="#94a3b8"/>')
    if v.get("takform") == "mansard":
        svg.append(_mansard(y0, y1, m["kote_gesims_moh"], v["tak_topp_moh"]))
    else:
        svg.append(f'  <rect class="sedumtak" x="{y0}" y="{_y(v["tak_topp_moh"]) - 4}" width="{y1 - y0}" height="4" fill="#4d7c0f"/>')
        svg.append(f'  <text x="{(y0 + y1) / 2}" y="{_y(v["tak_topp_moh"]) - 8}" font-family="sans-serif" font-size="9" fill="#a3e635" text-anchor="middle">SEDUMTAK</text>')
    svg += _malkjede(y0, y1, _y(v["tak_topp_moh"]) - 24, _mm(v["d"]))
    svg += _koter(modell, y0, y1, med_u1=True)
    svg.append(f'  <text x="{y0 - 30}" y="{_y(m["kote_terreng_moh"]) - 6}" font-family="sans-serif" font-size="9" fill="#64748b" text-anchor="end">NORD</text>')
    svg.append(f'  <text x="{y1 + 120}" y="{_y(m["kote_terreng_moh"]) + 22}" font-family="sans-serif" font-size="9" fill="#64748b">SØR</text>')
    svg.append('</svg>')
    return "\n".join(svg)


def skriv_alle(modell: dict, mappe: Path = BASE_DIR) -> list[Path]:
    filer = {"fasade_sor.svg": fasade_sor(modell), "fasade_ost.svg": fasade_ost(modell),
             "snitt_a.svg": snitt(modell, "snitt_a.svg"), "snitt_b.svg": snitt(modell, "snitt_b.svg")}
    ut = []
    for navn, innhold in filer.items():
        sti = mappe / navn
        sti.write_text(innhold, encoding="utf-8")
        ut.append(sti)
    return ut


if __name__ == "__main__":
    modell = json.loads((BASE_DIR / "bygning_geometri.json").read_text(encoding="utf-8"))
    for p in skriv_alle(modell):
        print("Skrev", p.name)
