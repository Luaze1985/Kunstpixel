"""
Byggeskript for interaktivt 2.5D isometrisk bygningskart, 2D-plantegninger og Trondheim-galleri for Kunstpixel.
Leser 06_kart/bygning_geometri.json og genererer:
- 06_kart/index.html (Interaktiv 2.5D og 2D-viser med Trondheim-galleri)
- 06_kart/plantegning_u1.svg (2D Blueprint Kjeller)
- 06_kart/plantegning_p1.svg (2D Blueprint 1. etasje)
- 06_kart/plantegning_p2.svg (2D Blueprint 2. etasje)
"""

import html
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "bygning_geometri.json"
HTML_PATH = BASE_DIR / "index.html"


OFFSET_X = 65
OFFSET_Y = 100

ROMFARGER = {
    # type: (fyll, kant, tittel)
    "sal": ("rgba(245, 158, 11, 0.20)", "#f59e0b", "#fef08a"),
    "magasin": ("rgba(239, 68, 68, 0.20)", "#ef4444", "#fecaca"),
    "trapp": ("rgba(100, 116, 139, 0.35)", "#94a3b8", "#ffffff"),
    "heis": ("rgba(100, 116, 139, 0.35)", "#94a3b8", "#ffffff"),
    "gang": ("rgba(30, 41, 59, 0.55)", "#475569", "#94a3b8"),
    "wc": ("rgba(20, 184, 166, 0.15)", "#14b8a6", "#ccfbf1"),
    "kontor": ("rgba(99, 102, 241, 0.15)", "#6366f1", "#e0e7ff"),
    "reserve": ("rgba(236, 72, 153, 0.12)", "#ec4899", "#fbcfe8"),
    "maskin": ("rgba(236, 72, 153, 0.18)", "#ec4899", "#fbcfe8"),
}
ROMFARGER_ID = {
    "KAF-1": ("rgba(16, 185, 129, 0.20)", "#10b981", "#a7f3d0"),
    "BUT-1": ("rgba(168, 85, 247, 0.20)", "#a855f7", "#e9d5ff"),
    "RES-1": ("rgba(14, 165, 233, 0.20)", "#0ea5e9", "#bae6fd"),
    "VER-1": ("rgba(239, 68, 68, 0.20)", "#ef4444", "#fecaca"),
}
STANDARDFARGE = ("rgba(51, 65, 85, 0.30)", "#64748b", "#f8fafc")
HATCH = {"tegl": "hatch-tegl-400", "glass": "hatch-betong-300"}


def _tall(v: float) -> str:
    """Norsk tallformat: 4 350 eller 4 174,2."""
    tekst = f"{v:,.1f}" if v != int(v) else f"{int(v):,}"
    return tekst.replace(",", " ").replace(".", ",")


def _mm(enheter: int) -> str:
    return f"{enheter * 100:,} mm".replace(",", " ")


def _romfarge(r: dict) -> tuple[str, str, str]:
    return ROMFARGER_ID.get(r["id"]) or ROMFARGER.get(r.get("type", ""), STANDARDFARGE)


def _sx(x: float) -> float:
    return x + OFFSET_X


def _sy(y: float) -> float:
    return y + OFFSET_Y


def _vegger(fot: dict, rooms: list[dict]) -> list[str]:
    ut = ['  <g class="architectural-walls">']
    for v in fot["volumer"]:
        x, y, b, d = v["x"], v["y"], v["b"], v["d"]
        t = v["vegg_mm"] // 100
        inn = v["innvendig"]
        hatch = HATCH.get(v["materiale"], "hatch-tegl-400")
        sider = [(x, y, b, t), (x, y + d - t, b, t)]  # nord, sør
        if inn["x"] > x:
            sider.append((x, y, t, d))  # vest
        if inn["x"] + inn["b"] < x + b:
            sider.append((x + b - t, y, t, d))  # øst
        ut.append(f'    <!-- {v["navn"]}: {v["vegg_mm"]} mm yttervegg ({v["materiale"]}) -->')
        for sx, sy, sb, sd in sider:
            ut.append(f'    <rect class="yttervegg" data-volum="{v["id"]}" x="{_sx(sx)}" y="{_sy(sy)}" width="{sb}" height="{sd}" '
                      f'fill="url(#{hatch})" stroke="#38bdf8" stroke-width="1.2"/>')
    f = fot["fasadevegg"]
    ut.append('    <!-- Den gamle østfasaden fra 1912, nå innervegg mellom fløyene -->')
    ut.append(f'    <rect class="fasadevegg" x="{_sx(f["x"])}" y="{_sy(f["y"])}" width="{f["b"]}" height="{f["d"]}" '
              f'fill="url(#hatch-tegl-400)" stroke="#38bdf8" stroke-width="1"/>')
    for r in rooms:
        if r.get("type") == "gang":
            for ky in (r["y"], r["y"] + r["h"]):
                ut.append(f'    <rect class="baerevegg" x="{_sx(r["x"])}" y="{_sy(ky) - 1}" width="{r["w"]}" height="2" '
                          f'fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="0.6"/>')
    ut.append('  </g>')
    return ut


def _malkjeder(fot: dict) -> list[str]:
    vol = fot["volumer"]
    x0, x1 = min(v["x"] for v in vol), max(v["x"] + v["b"] for v in vol)
    y0, y1 = min(v["y"] for v in vol), max(v["y"] + v["d"] for v in vol)

    def kjede(ax: float, bx: float, yy: float, tekst: str) -> list[str]:
        return [
            f'    <line x1="{ax}" y1="{yy}" x2="{bx}" y2="{yy}" stroke="#64748b" stroke-width="0.8" marker-start="url(#tick-45)" marker-end="url(#tick-45)"/>',
            f'    <line x1="{ax}" y1="{yy - 5}" x2="{ax}" y2="{yy + 5}" stroke="#38bdf8" stroke-width="1.2" class="arch-tick" transform="rotate(45 {ax} {yy})"/>',
            f'    <line x1="{bx}" y1="{yy - 5}" x2="{bx}" y2="{yy + 5}" stroke="#38bdf8" stroke-width="1.2" class="arch-tick" transform="rotate(45 {bx} {yy})"/>',
            f'    <text x="{(ax + bx) / 2}" y="{yy - 5}" font-family="sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle">{tekst}</text>',
        ]

    ut = ['  <!-- Målekjeder iht. NS 8351, regnet fra fotavtrykket -->', '  <g class="dimension-chain" style="opacity: 0.75;">']
    ut += kjede(_sx(x0), _sx(x1), _sy(y0) - 30, f"{_mm(x1 - x0)} ({(x1 - x0) / 10:g} m)")
    for v in vol:
        ut += kjede(_sx(v["x"]), _sx(v["x"] + v["b"]), _sy(y0) - 14, f'{_mm(v["b"])} · {v["byggeaar"]}')
    lx = _sx(x0) - 20
    ut += [
        f'    <line x1="{lx}" y1="{_sy(y0)}" x2="{lx}" y2="{_sy(y1)}" stroke="#64748b" stroke-width="0.8" marker-start="url(#tick-45)" marker-end="url(#tick-45)"/>',
        f'    <text x="{lx - 6}" y="{(_sy(y0) + _sy(y1)) / 2}" font-family="sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle" '
        f'transform="rotate(-90 {lx - 6} {(_sy(y0) + _sy(y1)) / 2})">{_mm(y1 - y0)}</text>',
        '  </g>',
    ]
    return ut


def _rom(r: dict) -> list[str]:
    rx, ry, rw, rh = _sx(r["x"]), _sy(r["y"]), r["w"], r["h"]
    fyll, kant, tittelfarge = _romfarge(r)
    areal = r["areal_m2"]
    brann = html.escape(str((r.get("brannklasse") or "EI-60").split()[0]))
    smal = min(rw, rh) < 40
    fs = 11 if (rw >= 100 and rh >= 80) else 8.5
    if smal:
        tittel = html.escape(str(r["romnummer"]))
    elif r.get("type") == "trapp":
        tittel = "TRAPP"
    elif r.get("type") == "heis":
        tittel = "HEIS"
    else:
        # Lengste navn som får plass i rommet: kortnavn, så første ord, ellers romnummer.
        kort = r.get("romnavn_kort", r["navn"].split("–")[0].strip())
        tittel = next((t for t in (kort, kort.split()[0]) if len(t) * fs * 0.68 <= rw - 6), str(r["romnummer"]))
        tittel = html.escape(tittel)
    cx, cy = rx + rw / 2, ry + rh / 2
    strek = ' stroke-dasharray="5,3"' if r.get("type") == "reserve" else ""
    ut = [
        f'  <g class="blueprint-room" data-room-id="{r["id"]}" style="cursor: pointer;">',
        f'    <desc>H: {r.get("takhoyde_m", 4.0):.1f} m | BRA {areal} m² | {brann} | {r.get("sikkerhetssone", "S1")}/{r.get("klimasone", "K3")}</desc>',
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{fyll}" stroke="{kant}" stroke-width="1.4"{strek}/>',
    ]
    if smal:
        rot = f' transform="rotate(-90 {cx} {cy})"' if rh > rw else ""
        ut.append(f'    <text x="{cx}" y="{cy + 3}" font-family="sans-serif" font-size="8" font-weight="bold" fill="{tittelfarge}" text-anchor="middle"{rot}>{tittel}</text>')
    else:
        ut.append(f'    <text x="{cx}" y="{cy - 2}" font-family="sans-serif" font-size="{fs}" font-weight="bold" fill="{tittelfarge}" text-anchor="middle">{tittel}</text>')
        ut.append(f'    <text x="{cx}" y="{cy + 11}" font-family="sans-serif" font-size="{fs * 0.8:.1f}" font-weight="500" fill="#cbd5e1" text-anchor="middle">{_tall(areal)} m²</text>')
    ut.append('  </g>')
    if r.get("type") == "trapp":
        if rh >= rw:
            ut += [f'  <line x1="{rx + 3}" y1="{ty}" x2="{rx + rw - 3}" y2="{ty}" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>'
                   for ty in range(int(ry + 5), int(ry + rh - 4), 6)]
        else:
            ut += [f'  <line x1="{tx}" y1="{ry + 3}" x2="{tx}" y2="{ry + rh - 3}" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>'
                   for tx in range(int(rx + 5), int(rx + rw - 4), 6)]
    elif r.get("type") == "heis":
        ut.append(f'  <line x1="{rx + 3}" y1="{ry + 3}" x2="{rx + rw - 3}" y2="{ry + rh - 3}" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>')
        ut.append(f'  <line x1="{rx + rw - 3}" y1="{ry + 3}" x2="{rx + 3}" y2="{ry + rh - 3}" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>')
    dor = r.get("dor_pos", "sor")
    langs = r.get("dor_langs")  # valgfri modellkoordinat langs veggen, ellers midt på
    if dor in ("sor", "nord"):
        dx, dy = (_sx(langs) if langs is not None else rx + rw / 2), ry + (rh if dor == "sor" else 0)
        retning = -8 if dor == "sor" else 8
        ut.append(f'  <line x1="{dx - 6}" y1="{dy}" x2="{dx + 6}" y2="{dy}" stroke="#0a0f1d" stroke-width="3"/>')
        ut.append(f'  <line x1="{dx - 6}" y1="{dy}" x2="{dx + 6}" y2="{dy + retning}" stroke="{kant}" stroke-width="1.2"/>')
    elif dor in ("vest", "ost"):
        dx, dy = rx + (0 if dor == "vest" else rw), (_sy(langs) if langs is not None else ry + rh / 2)
        retning = 8 if dor == "vest" else -8
        ut.append(f'  <line x1="{dx}" y1="{dy - 6}" x2="{dx}" y2="{dy + 6}" stroke="#0a0f1d" stroke-width="3"/>')
        ut.append(f'  <line x1="{dx}" y1="{dy - 6}" x2="{dx + retning}" y2="{dy + 6}" stroke="{kant}" stroke-width="1.2"/>')
    return ut


def generate_blueprint_svg(floor_data: dict, model_data: dict) -> str:
    kode = floor_data["kode"]
    rooms = floor_data.get("rom", [])
    museum = model_data["museum"]
    fot = museum["fotavtrykk"]
    matrikkel = museum.get("matrikkel", {})
    arealer = museum["arealer_ns3940"]
    brann = museum.get("brannkonsept", {})
    vol = fot["volumer"]
    x0, x1 = min(v["x"] for v in vol), max(v["x"] + v["b"] for v in vol)
    y0, y1 = min(v["y"] for v in vol), max(v["y"] + v["d"] for v in vol)
    midt_y = (_sy(y0) + _sy(y1)) / 2

    kote = f'KOTE FG: {floor_data["kote_relativ"]} ({floor_data["kote_moh"]:+.2f} moh)'
    if kode == "P1":
        kote += f' | TERRENG: {matrikkel.get("kote_terreng_moh", 0):+.2f} moh DTM1'
    elif kode == "P2":
        kote += f' | GESIMS: {matrikkel.get("kote_gesims_moh", 0):+.2f} moh'

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 680" width="100%" height="100%" class="blueprint-svg">',
        '  <defs>',
        '    <!-- NS 8351 Skravurmønstre (Hatch Patterns) -->',
        '    <pattern id="hatch-tegl-400" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">',
        '      <line x1="0" y1="0" x2="0" y2="8" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1.2"/>',
        '    </pattern>',
        '    <pattern id="hatch-betong-300" width="10" height="10" patternUnits="userSpaceOnUse">',
        '      <line x1="0" y1="0" x2="10" y2="10" stroke="rgba(56, 189, 248, 0.3)" stroke-width="0.8"/>',
        '      <line x1="10" y1="0" x2="0" y2="10" stroke="rgba(56, 189, 248, 0.3)" stroke-width="0.8"/>',
        '      <circle cx="5" cy="5" r="1.2" fill="rgba(56, 189, 248, 0.3)"/>',
        '    </pattern>',
        '    <pattern id="hatch-baerevegg-200" width="4" height="4" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">',
        '      <line x1="0" y1="0" x2="0" y2="4" stroke="rgba(2, 132, 199, 0.5)" stroke-width="1.2"/>',
        '    </pattern>',
        '    <marker id="tick-45" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto">',
        '      <line x1="1" y1="9" x2="9" y2="1" stroke="#38bdf8" stroke-width="1.8" class="arch-tick"/>',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#0a0f1d"/>',
        f'  <text x="{_sx(x0)}" y="{_sy(y0) - 52}" font-family="sans-serif" font-size="11" font-weight="600" fill="#38bdf8">{html.escape(kote)}</text>',
        '  <!-- Bygningskropp underlag -->',
        f'  <rect x="{_sx(x0)}" y="{_sy(y0)}" width="{x1 - x0}" height="{y1 - y0}" fill="rgba(15, 23, 42, 0.45)" stroke="#38bdf8" stroke-width="1"/>',
    ]
    svg += _vegger(fot, rooms)
    for r in rooms:
        svg += _rom(r)
    svg += _malkjeder(fot)

    # Himmelretninger og adkomst
    svg += [
        f'  <text x="{_sx(x0) - 42}" y="{midt_y}" font-family="sans-serif" font-size="9" font-weight="600" fill="#64748b" transform="rotate(-90 {_sx(x0) - 42} {midt_y})" letter-spacing="2" text-anchor="middle">◀ VEST · MOT NIDAROSDOMEN</text>',
        f'  <text x="{_sx(x1) + 18}" y="{midt_y}" font-family="sans-serif" font-size="9" font-weight="600" fill="#0284c7" transform="rotate(90 {_sx(x1) + 18} {midt_y})" letter-spacing="2" text-anchor="middle">≋ ØST · NIDELVA ≋</text>',
        f'  <text x="{(_sx(x0) + _sx(x1)) / 2}" y="{_sy(y1) + 46}" font-family="sans-serif" font-size="9" fill="#64748b" text-anchor="middle" letter-spacing="2">SØR · BISPEGATA</text>',
    ]
    if kode in ("P1", "U1"):
        svg.append(f'  <text x="{_sx(x1) - 60}" y="{_sy(y0) - 52}" font-family="sans-serif" font-size="9" fill="#64748b" text-anchor="middle" letter-spacing="1">NORD · BAKGÅRD{" OG RAMPE" if kode == "U1" else ""}</text>')
    res = next((r for r in rooms if r["id"] == "RES-1"), None)
    if res:
        ex = _sx(res["x"] + res["w"] / 2)
        svg += [
            f'  <g class="entrance-portal" transform="translate({ex}, {_sy(y1) + 18})">',
            '    <polygon points="0,-10 6,-3 -6,-3" fill="#38bdf8"/>',
            '    <text x="0" y="9" font-family="sans-serif" font-size="10" font-weight="bold" fill="#38bdf8" text-anchor="middle" letter-spacing="1">HOVEDINNGANG FRA BISPEGATA</text>',
            '  </g>',
        ]

    # Tegningshode og romliste
    svg += [
        '  <g class="title-block" transform="translate(760, 60)">',
        '    <text x="0" y="0" font-family="sans-serif" font-size="20" font-weight="bold" fill="#ffffff" letter-spacing="1">KUNSTPIXEL</text>',
        f'    <text x="0" y="22" font-family="sans-serif" font-size="12" font-weight="600" fill="#38bdf8">PLAN {html.escape(kode)} • {html.escape(floor_data["navn"].upper())}</text>',
        f'    <text x="0" y="40" font-family="sans-serif" font-size="9.5" fill="#94a3b8">{html.escape(matrikkel.get("adresse", ""))} • Gnr {matrikkel.get("gnr")} / Bnr {matrikkel.get("bnr")}</text>',
        '    <line x1="0" y1="52" x2="300" y2="52" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>',
        '    <text x="0" y="72" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#64748b" letter-spacing="1">ROMLISTE &amp; AREALER (BRA)</text>',
    ]
    yc = 92
    for r in rooms:
        _, kant, _ = _romfarge(r)
        navn = html.escape(r["navn"].split("–")[0].strip())
        svg += [
            f'    <circle cx="5" cy="{yc - 3.5}" r="3.5" fill="{kant}"/>',
            f'    <text x="14" y="{yc}" font-family="sans-serif" font-size="9.5" fill="#64748b">{html.escape(str(r["romnummer"]))}</text>',
            f'    <text x="40" y="{yc}" font-family="sans-serif" font-size="10" font-weight="500" fill="#f8fafc">{navn}</text>',
            f'    <text x="300" y="{yc}" font-family="sans-serif" font-size="10" font-weight="600" fill="#cbd5e1" text-anchor="end">{_tall(r["areal_m2"])} m²</text>',
        ]
        yc += 18
    bta, bra, bya = arealer["bta_m2"], arealer["bra_m2"], arealer["bya_m2"]
    svg += [
        f'    <line x1="0" y1="{yc}" x2="300" y2="{yc}" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>',
        f'    <text x="0" y="{yc + 18}" font-family="sans-serif" font-size="9.5" fill="#94a3b8">BTA: {_tall(bta)} m² • BRA: {_tall(bra)} m² • BYA: {_tall(bya)} m²</text>',
        f'    <text x="0" y="{yc + 32}" font-family="sans-serif" font-size="8.5" fill="#64748b">NS 3940 ({bta} / {bra} / {bya}) · etasje: BTA {_tall(floor_data["bta_etasje_m2"])}, BRA {_tall(floor_data["bra_etasje_m2"])}</text>',
        f'    <text x="0" y="{yc + 46}" font-family="sans-serif" font-size="8.5" fill="#64748b">Brannklasse {brann.get("brannklasse", "")} / Risikoklasse {brann.get("risikoklasse", "")} • {matrikkel.get("gnr")}/{matrikkel.get("bnr")} • Tegning {html.escape(floor_data.get("tegningsnummer", ""))}</text>',
        f'    <text x="0" y="{yc + 62}" font-family="sans-serif" font-size="10" font-weight="bold" fill="#38bdf8">MÅLESTOKK {html.escape(floor_data.get("malestokk", "1:100"))}</text>',
        '  </g>',
        '</svg>',
    ]
    return "\n".join(svg)


def generate_html(data: dict) -> str:
    data_json = json.dumps(data, ensure_ascii=False)
    mp_sti = BASE_DIR / "maskinpark.json"
    maskinpark_json = mp_sti.read_text(encoding="utf-8") if mp_sti.is_file() else '{"maskiner": [], "hendelser": []}'

    room_images = {
        "FASADE": "bilder/01_eksterior_hovedfasade.jpg",
        "TILBYGG": "bilder/02_eksterior_tilbygg_nidelva.jpg",
        "HAGE": "bilder/03_eksterior_skulpturhage.jpg",
        "RES-1": "bilder/04_vestibyle_resepsjon.jpg",
        "BUT-1": "bilder/05_museumsbutikk.jpg",
        "KAF-1": "bilder/06_museumskafe.jpg",
        "SAL-A": "bilder/07_sal_a_mytologi.jpg",
        "SAL-D": "bilder/11_sal_d_munch.jpg",
        "MAG-1": "bilder/13_magasin_1_hovedlager.jpg",
    }
    room_images_json = json.dumps(room_images)

    gallery_items = [
        {"file": "bilder/01_eksterior_hovedfasade.jpg", "title": "01. Hovedfasade fra Bispegata", "cat": "Eksteriør", "desc": "Kunstpixel i Bispegata. Hovedfløy fra 1912 i rød håndbanket tegl, trondhjemitt-granittsokkel, irrgrønt kobbertak og Nidarosdomens spir i bakgrunnen."},
        {"file": "bilder/02_eksterior_tilbygg_nidelva.jpg", "title": "02. Tilbygg Øst ved Nidelva", "cat": "Eksteriør", "desc": "2016-fløyen i strukturelt glass med vertikale spiler i lys eik og slipt betong, med de historiske trebryggene i Trondheim langs elvebredden."},
        {"file": "bilder/03_eksterior_skulpturhage.jpg", "title": "03. Skulpturhage i atriet", "cat": "Eksteriør", "desc": "Skjermet indre museumshage med granittheller, vannspeil, bronseskulpturer og åpen siktlinje mot Marinen-parken."},
        {"file": "bilder/04_vestibyle_resepsjon.jpg", "title": "04. Vestibyle & Resepsjon (P1)", "cat": "Publikum", "desc": "Ankomsthall med overlys fra glasstaket, lys grå terrazzo, minimalistisk skranke i mørk røkt eik med 'KUNSTPIXEL'-tekst og adgangsporter."},
        {"file": "bilder/05_museumsbutikk.jpg", "title": "05. Museumsbutikk / Kunstpixel Bokhandel (P1)", "cat": "Publikum", "desc": "Kunstbøker, utstillingskataloger og skandinavisk formgivning i spesialbygde eikehyller med integrert LED-lys."},
        {"file": "bilder/06_museumskafe.jpg", "title": "06. Museumskafé mot Nidelva (P1)", "cat": "Publikum", "desc": "Kafé med 45 sitteplasser, skandinaviske designstoler i lys eik og panoramavinduer mot skulpturhagen, Nidelva og trebryggene."},
        {"file": "bilder/07_sal_a_mytologi.jpg", "title": "07. Sal A – Mytologi & Natur (P1)", "cat": "Utstilling", "desc": "Museets største sal med 6 meters takhøyde, matte antrasittgrå vegger, fiskebensparkett og spotbelysning over Kittelsen og Sohlberg."},
        {"file": "bilder/11_sal_d_munch.jpg", "title": "08. Sal D – Eksistens & Modernisme (P2)", "cat": "Utstilling", "desc": "Dype karmosinrøde vegger med dempet belysning for Edvard Munch, og frittstående klimastyrte glassmontre med 50 luks for papirverk."},
        {"file": "bilder/13_magasin_1_hovedlager.jpg", "title": "09. Magasin 1 – Klimastyrt lager (U1)", "cat": "Høysikkerhet", "desc": "Sone 4 Høysikkerhet: Automatiserte elektriske rullehyller i stål, Inergen-gasslukkeanlegg og digital klimakontroll (18.0 °C / 50 % RF)."}
    ]
    gallery_items_json = json.dumps(gallery_items, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kunstpixel Trondheim – 2.5D Bygningskart &amp; Galleri</title>
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: rgba(17, 24, 39, 0.94);
      --border: rgba(255, 255, 255, 0.12);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --accent: #0284c7;
      --s1: #10b981;
      --s2: #f59e0b;
      --s3: #3b82f6;
      --s4: #ef4444;
      --k1: #06b6d4;
      --k2: #8b5cf6;
      --k3: #64748b;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}

    body {{
      background: radial-gradient(circle at 50% 20%, #1e293b 0%, #0b0f19 80%);
      color: var(--text);
      overflow: hidden;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    header {{
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 20;
    }}

    .logo-group {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #0284c7, #3b82f6);
      color: #fff;
      font-weight: 700;
      font-size: 13px;
      padding: 6px 10px;
      border-radius: 6px;
      letter-spacing: 0.5px;
    }}

    .title-group h1 {{
      font-size: 17px;
      font-weight: 600;
      letter-spacing: -0.2px;
    }}

    .title-group p {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    .toolbar {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .control-pill {{
      display: flex;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 3px;
    }}

    .btn-toggle {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.18s ease;
    }}

    .btn-toggle.active {{
      background: var(--accent);
      color: #ffffff;
      box-shadow: 0 2px 6px rgba(2, 132, 199, 0.4);
    }}

    .btn-toggle:hover:not(.active) {{
      color: var(--text);
      background: rgba(255, 255, 255, 0.08);
    }}

    .viewport {{
      position: relative;
      flex: 1;
      width: 100%;
      height: 100%;
      overflow: hidden;
      cursor: grab;
    }}

    .viewport:active {{
      cursor: grabbing;
    }}

    canvas {{
      display: block;
      width: 100%;
      height: 100%;
    }}

    #blueprint-container {{
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      padding: 24px;
      align-items: center;
      justify-content: center;
      z-index: 5;
    }}

    #blueprint-frame {{
      width: 90%;
      max-width: 1050px;
      height: 85%;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 15px 35px rgba(0,0,0,0.7);
      border: 1px solid rgba(56, 189, 248, 0.3);
      background: #0a101d;
    }}

    #gallery-container {{
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      padding: 28px;
      overflow-y: auto;
      z-index: 8;
      background: rgba(11, 15, 25, 0.96);
    }}

    .gallery-header {{
      max-width: 1280px;
      margin: 0 auto 20px auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 12px;
    }}

    .gallery-header h2 {{
      font-size: 18px;
      font-weight: 600;
      color: #fff;
    }}

    .gallery-header p {{
      font-size: 13px;
      color: var(--text-muted);
    }}

    .gallery-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 22px;
      max-width: 1280px;
      margin: 0 auto;
      padding-bottom: 60px;
    }}

    .gallery-card {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }}

    .gallery-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 24px rgba(0,0,0,0.5);
      border-color: var(--accent);
    }}

    .gallery-card img {{
      width: 100%;
      height: 225px;
      object-fit: cover;
      display: block;
      background: #1e293b;
    }}

    .gallery-card-body {{
      padding: 14px 16px;
    }}

    .gallery-card-badge {{
      display: inline-block;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 2px 6px;
      border-radius: 3px;
      background: rgba(2, 132, 199, 0.25);
      color: #38bdf8;
      margin-bottom: 6px;
    }}

    .gallery-card-title {{
      font-size: 14px;
      font-weight: 600;
      color: #fff;
      margin-bottom: 4px;
    }}

    .gallery-card-desc {{
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.45;
    }}

    .legend-overlay {{
      position: absolute;
      bottom: 20px;
      left: 20px;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 18px;
      z-index: 10;
      font-size: 12px;
      max-width: 300px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}

    .legend-title {{
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--text);
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 6px;
    }}

    .legend-color {{
      width: 14px;
      height: 14px;
      border-radius: 3px;
      flex-shrink: 0;
    }}

    .angle-controls {{
      position: absolute;
      bottom: 20px;
      right: 20px;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 8px;
      display: flex;
      gap: 6px;
      z-index: 10;
    }}

    .icon-btn {{
      background: transparent;
      border: none;
      color: var(--text);
      width: 34px;
      height: 34px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 15px;
    }}

    .icon-btn:hover {{
      background: rgba(255, 255, 255, 0.1);
    }}

    .drawer {{
      position: absolute;
      top: 0;
      right: 0;
      width: 420px;
      height: 100%;
      background: rgba(15, 23, 42, 0.98);
      backdrop-filter: blur(20px);
      border-left: 1px solid var(--border);
      padding: 24px;
      box-shadow: -10px 0 30px rgba(0,0,0,0.6);
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 30;
      overflow-y: auto;
    }}

    .drawer.open {{
      transform: translateX(0);
    }}

    .drawer-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 12px;
    }}

    .drawer-close {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 22px;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
    }}

    .drawer-close:hover {{
      color: #fff;
      background: rgba(255,255,255,0.1);
    }}

    .drawer-image-box {{
      margin-bottom: 16px;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--border);
      display: none;
      background: #0f172a;
    }}

    .drawer-image-box img {{
      width: 100%;
      height: 200px;
      object-fit: cover;
      display: block;
    }}

    .drawer-image-caption {{
      padding: 8px 12px;
      font-size: 11px;
      color: var(--text-muted);
      background: rgba(0,0,0,0.5);
    }}

    .badge-row {{
      display: flex;
      gap: 8px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }}

    .badge {{
      font-size: 11px;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .stat-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }}

    .stat-card {{
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
    }}

    .stat-label {{
      font-size: 11px;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    .stat-val {{
      font-size: 15px;
      font-weight: 600;
      margin-top: 2px;
    }}

    .section-title {{
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin: 14px 0 6px 0;
    }}

    .info-box {{
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      font-size: 13px;
      line-height: 1.5;
      color: #e2e8f0;
      margin-bottom: 10px;
    }}

    .tag-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .tag {{
      background: rgba(2, 132, 199, 0.15);
      border: 1px solid rgba(2, 132, 199, 0.3);
      color: #7dd3fc;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 4px;
    }}

    #hover-tooltip {{
      position: absolute;
      pointer-events: none;
      background: rgba(15, 23, 42, 0.94);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 12px;
      color: #fff;
      display: none;
      z-index: 25;
      box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    }}
  </style>
</head>
<body>

  <header>
    <div class="logo-group">
      <div class="logo-badge">TRONDHEIM</div>
      <div class="title-group">
        <h1>{data['museum']['navn']} – Bygnings-, Sone- &amp; Plantegningskart</h1>
        <p>{data['museum']['fiktiv_adresse']} • Nidelva &amp; Bispegata • BRA: {_tall(data['museum']['arealer_ns3940']['bra_m2'])} m² ({data['museum']['arealer_ns3940']['bra_m2']}) • BTA: {_tall(data['museum']['arealer_ns3940']['bta_m2'])} m² • BYA: {_tall(data['museum']['arealer_ns3940']['bya_m2'])} m² • {data['museum']['georeferanse']['moh']} m.o.h.</p>
      </div>
    </div>

    <div class="toolbar">
      <div class="control-pill" title="Velg hovedvisning">
        <button class="btn-toggle active" id="btn-view-25d" onclick="setMainView('25d')">2.5D Isometrisk</button>
        <button class="btn-toggle" id="btn-view-2d" onclick="setMainView('2d')">2D Blueprint</button>
        <button class="btn-toggle" id="btn-view-gallery" onclick="setMainView('gallery')">Trondheim Galleri</button>
      </div>

      <div class="control-pill" id="pill-shell-mode" title="Bygningskropp utenfra eller snitt innenfor">
        <button class="btn-toggle active" id="btn-mode-interior" onclick="setMode('interior')">Røntgen / Interiør</button>
        <button class="btn-toggle" id="btn-mode-exterior" onclick="setMode('exterior')">Skall / Fasade</button>
      </div>

      <div class="control-pill" id="pill-floor-select" title="Velg etasje">
        <button class="btn-toggle active" id="floor-all" onclick="setFloor('all')">Alle etasjer</button>
        <button class="btn-toggle" id="floor-0" onclick="setFloor(0)">U1 Kjeller</button>
        <button class="btn-toggle" id="floor-1" onclick="setFloor(1)">P1 Hovedplan</button>
        <button class="btn-toggle" id="floor-2" onclick="setFloor(2)">P2 Galleri</button>
      </div>

      <div class="control-pill" id="pill-zone-select" title="Filter for soner">
        <button class="btn-toggle active" id="zone-ark" onclick="setZone('ark')">Arkitektur</button>
        <button class="btn-toggle" id="zone-sikkerhet" onclick="setZone('sikkerhet')">Sikkerhetssoner</button>
        <button class="btn-toggle" id="zone-klima" onclick="setZone('klima')">Klimasoner</button>
        <button class="btn-toggle" id="zone-maskin" onclick="setZone('maskin')">Maskiner</button>
      </div>
    </div>
  </header>

  <div class="viewport" id="viewport">
    <canvas id="mapCanvas"></canvas>

    <div id="blueprint-container">
      <iframe id="blueprint-frame" src="plantegning_p1.svg"></iframe>
    </div>

    <div id="gallery-container">
      <div class="gallery-header">
        <div>
          <h2>Kunstpixel Trondheim – Arkitektonisk Fotoserie</h2>
          <p>Forankret i Bispegata ved Nidelva og Nidarosdomen. 100% konsistent materialpalett og arkitekturfotografi.</p>
        </div>
      </div>
      <div class="gallery-grid" id="gallery-grid-items">
      </div>
    </div>

    <div class="legend-overlay" id="legend">
      <div class="legend-title">
        <span id="legend-heading">Tegnforklaring</span>
      </div>
      <div id="legend-content"></div>
    </div>

    <div class="angle-controls" id="angle-controls">
      <button class="icon-btn" title="Roter mot klokken (90°)" onclick="rotateView(-1)">↺</button>
      <button class="icon-btn" title="Roter med klokken (90°)" onclick="rotateView(1)">↻</button>
      <button class="icon-btn" title="Zoom inn" onclick="zoomView(1.2)">+</button>
      <button class="icon-btn" title="Zoom ut" onclick="zoomView(0.8)">−</button>
      <button class="icon-btn" title="Nullstill kameravisning" onclick="resetView()">⟲</button>
    </div>

    <div id="hover-tooltip"></div>

    <div class="drawer" id="drawer">
      <div class="drawer-header">
        <div>
          <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;" id="drawer-room-id">SAL-A</div>
          <h2 style="font-size: 18px; margin-top: 2px;" id="drawer-room-name">Sal A</h2>
        </div>
        <button class="drawer-close" onclick="closeDrawer()">&times;</button>
      </div>

      <div class="drawer-image-box" id="drawer-image-box">
        <img id="drawer-img" src="" alt="Romvisning">
        <div class="drawer-image-caption" id="drawer-img-caption">Arkitektonisk visualisering</div>
      </div>

      <div class="badge-row">
        <span class="badge" id="drawer-badge-sone">S2 Utstilling</span>
        <span class="badge" id="drawer-badge-klima">K2 Standard</span>
        <span class="badge" id="drawer-badge-etasje" style="background: rgba(255,255,255,0.1); color: #fff;">1. etasje</span>
      </div>

      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">Areal (BRA)</div>
          <div class="stat-val" id="drawer-areal">216 m²</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Takhøyde</div>
          <div class="stat-val" id="drawer-hoyde">6.0 m</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Brannklasse</div>
          <div class="stat-val" id="drawer-brann">EI-60</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Romnummer</div>
          <div class="stat-val" id="drawer-romnr">101</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Kapasitet verk</div>
          <div class="stat-val" id="drawer-kapasitet">20 verk</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Lysforhold</div>
          <div class="stat-val" id="drawer-lys">150–200 luks</div>
        </div>
      </div>

      <div class="section-title">Materialer &amp; Overflater (NS 8351)</div>
      <div class="info-box" id="drawer-materialer">
        <strong>Gulv:</strong> Hvitoljet eikeparkett<br>
        <strong>Vegg:</strong> Pusset tegl koksgrå<br>
        <strong>Himling:</strong> Akustisk dagslyslanternetak
      </div>

      <div class="section-title">Beskrivelse &amp; Utforming</div>
      <div class="info-box" id="drawer-desc">
        Beskrivelse her...
      </div>

      <div class="section-title">Klimakrav &amp; Miljøstyring</div>
      <div class="info-box" id="drawer-klima-desc">
        Temperatur, RF % og luks...
      </div>

      <div class="section-title">Sikkerhet & Adgangskontroll</div>
      <div class="info-box" id="drawer-sikkerhet-desc">
        Krav og vaktposter...
      </div>

      <div class="section-title">Aktive Sensorer & Instrumentering</div>
      <div class="tag-list" id="drawer-sensorer">
      </div>

      <div class="section-title">Maskiner i rommet (maskinpark)</div>
      <div class="tag-list" id="drawer-maskiner">
      </div>
    </div>
  </div>

  <script>
    const MODEL = {data_json};
    const ROOM_IMAGES = {room_images_json};
    const MASKINPARK = {maskinpark_json};
    const MASKINSTATUS = {{ i_drift: '#10b981', varsel: '#f59e0b', feil: '#ef4444', vedlikehold: '#3b82f6' }};
    const STATUSRANG = {{ i_drift: 0, vedlikehold: 1, varsel: 2, feil: 3 }};
    function maskinerIRom(romId) {{ return MASKINPARK.maskiner.filter(m => m.rom_id === romId); }}
    const GALLERY_ITEMS = {gallery_items_json};

    let mainView = '25d';
    let currentMode = 'interior';
    let currentFloor = 'all';
    let currentZone = 'ark';
    let rotationIndex = 0;

    let camera = {{
      x: 0,
      y: 0,
      zoom: 1.0,
      baseZoom: 1.0,
      isDragging: false,
      startX: 0,
      startY: 0
    }};

    let hoveredRoom = null;
    let selectedRoom = null;
    let clickableHitBoxes = [];

    const canvas = document.getElementById('mapCanvas');
    const ctx = canvas.getContext('2d');
    const viewport = document.getElementById('viewport');
    const tooltip = document.getElementById('hover-tooltip');
    const blueprintContainer = document.getElementById('blueprint-container');
    const blueprintFrame = document.getElementById('blueprint-frame');
    const galleryContainer = document.getElementById('gallery-container');
    const legendEl = document.getElementById('legend');
    const angleControlsEl = document.getElementById('angle-controls');

    function initGalleryGrid() {{
      const grid = document.getElementById('gallery-grid-items');
      grid.innerHTML = '';
      GALLERY_ITEMS.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'gallery-card';
        card.onclick = () => openImageModal(item.file, item.title, item.desc);
        card.innerHTML = `
          <img src="${{item.file}}" alt="${{item.title}}">
          <div class="gallery-card-body">
            <span class="gallery-card-badge">${{item.cat}}</span>
            <div class="gallery-card-title">${{item.title}}</div>
            <div class="gallery-card-desc">${{item.desc}}</div>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function resizeCanvas() {{
      canvas.width = viewport.clientWidth * window.devicePixelRatio;
      canvas.height = viewport.clientHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      if (mainView === '25d') render();
    }}

    window.addEventListener('resize', resizeCanvas);

    // Fotavtrykket styrer alt som tegnes utenfor rommene (fasit: bygning_geometri.json).
    const FOT = MODEL.museum.fotavtrykk;
    const BX0 = Math.min(...FOT.volumer.map(v => v.x));
    const BX1 = Math.max(...FOT.volumer.map(v => v.x + v.b));
    const BY0 = Math.min(...FOT.volumer.map(v => v.y));
    const BY1 = Math.max(...FOT.volumer.map(v => v.y + v.d));
    const BCX = (BX0 + BX1) / 2;
    const BCY = (BY0 + BY1) / 2;

    function toIso(x, y, z) {{
      let cx = x - BCX;
      let cy = y - BCY;

      let rx = cx, ry = cy;
      if (rotationIndex === 1) {{ rx = -cy; ry = cx; }}
      else if (rotationIndex === 2) {{ rx = -cx; ry = -cy; }}
      else if (rotationIndex === 3) {{ rx = cy; ry = -cx; }}

      const cos30 = 0.866025;
      const sin30 = 0.5;

      const screenX = (rx - ry) * cos30;
      const screenY = (rx + ry) * sin30 - z;

      return {{
        x: screenX * camera.zoom + camera.x + viewport.clientWidth / 2,
        y: screenY * camera.zoom + camera.y + viewport.clientHeight / 2 + 30
      }};
    }}

    function setMainView(view) {{
      mainView = view;
      ['25d', '2d', 'gallery'].forEach(v => {{
        const btn = document.getElementById('btn-view-' + v);
        if (btn) btn.classList.toggle('active', v === view);
      }});

      const shellPill = document.getElementById('pill-shell-mode');
      const zonePill = document.getElementById('pill-zone-select');
      const floorPill = document.getElementById('pill-floor-select');

      if (view === '25d') {{
        canvas.style.display = 'block';
        blueprintContainer.style.display = 'none';
        galleryContainer.style.display = 'none';
        legendEl.style.display = 'block';
        angleControlsEl.style.display = 'flex';
        shellPill.style.display = 'flex';
        zonePill.style.display = 'flex';
        floorPill.style.display = 'flex';
        render();
      }} else if (view === '2d') {{
        canvas.style.display = 'none';
        blueprintContainer.style.display = 'flex';
        galleryContainer.style.display = 'none';
        legendEl.style.display = 'none';
        angleControlsEl.style.display = 'none';
        shellPill.style.display = 'none';
        zonePill.style.display = 'none';
        floorPill.style.display = 'flex';
        updateBlueprintFloor();
      }} else if (view === 'gallery') {{
        canvas.style.display = 'none';
        blueprintContainer.style.display = 'none';
        galleryContainer.style.display = 'block';
        legendEl.style.display = 'none';
        angleControlsEl.style.display = 'none';
        shellPill.style.display = 'none';
        zonePill.style.display = 'none';
        floorPill.style.display = 'none';
      }}
    }}

    function updateBlueprintFloor() {{
      let targetFloor = currentFloor;
      if (targetFloor === 'all') targetFloor = 1;
      const files = {{ 0: 'plantegning_u1.svg', 1: 'plantegning_p1.svg', 2: 'plantegning_p2.svg' }};
      blueprintFrame.src = files[targetFloor] || 'plantegning_p1.svg';
    }}

    function render() {{
      const width = viewport.clientWidth;
      const height = viewport.clientHeight;

      ctx.clearRect(0, 0, width, height);
      clickableHitBoxes = [];

      drawGround();

      let floorsToRender = (currentFloor === 'all') ? [0, 1, 2] : [parseInt(currentFloor)];

      const floorOffsets = {{
        0: 0,
        1: (currentFloor === 'all') ? 130 : 0,
        2: (currentFloor === 'all') ? 260 : 0
      }};

      if (currentFloor === 'all' && currentMode === 'interior') {{
        drawShafts(floorOffsets);
      }}

      floorsToRender.forEach(floorNr => {{
        const zOffset = floorOffsets[floorNr];
        const floorData = MODEL.etasjer.find(e => e.etasje_nr === floorNr);
        if (!floorData) return;

        drawFloorSlab(floorData, zOffset);

        if (currentMode === 'exterior') {{
          drawExteriorShell(floorData, zOffset);
        }} else {{
          const sortedRooms = sortRoomsByDepth(floorData.rom);
          sortedRooms.forEach(room => {{
            drawRoom25D(room, floorData, zOffset);
          }});
        }}
      }});

      updateLegendUI();
    }}

    function drawGround() {{
      ctx.save();
      const p1 = toIso(BX0 - 60, BY0 - 60, -10);
      const p2 = toIso(BX1 + 60, BY0 - 60, -10);
      const p3 = toIso(BX1 + 60, BY1 + 50, -10);
      const p4 = toIso(BX0 - 60, BY1 + 50, -10);

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.lineTo(p4.x, p4.y);
      ctx.closePath();
      ctx.fillStyle = "rgba(15, 23, 42, 0.75)";
      ctx.fill();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
      ctx.lineWidth = 1;
      ctx.stroke();

      const s1 = toIso(BX0 - 60, BY1 + 20, -9);
      const s2 = toIso(BX1 + 60, BY1 + 20, -9);
      ctx.beginPath();
      ctx.moveTo(s1.x, s1.y);
      ctx.lineTo(s2.x, s2.y);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
      ctx.lineWidth = 2;
      ctx.stroke();

      const streetLabel = toIso(BCX, BY1 + 38, -9);
      ctx.font = "11px sans-serif";
      ctx.fillStyle = "rgba(156, 163, 175, 0.6)";
      ctx.textAlign = "center";
      ctx.fillText("BISPEGATA TRONDHEIM (HOVEDADKOMST)", streetLabel.x, streetLabel.y);
      ctx.restore();
    }}

    function drawFloorSlab(floorData, z) {{
      ctx.save();
      const p1 = toIso(BX0, BY0, z);
      const p2 = toIso(BX1, BY0, z);
      const p3 = toIso(BX1, BY1, z);
      const p4 = toIso(BX0, BY1, z);

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.lineTo(p4.x, p4.y);
      ctx.closePath();
      ctx.fillStyle = (floorData.etasje_nr === 0) ? "rgba(30, 41, 59, 0.85)" : "rgba(30, 41, 59, 0.65)";
      ctx.fill();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.18)";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      const slabH = 6;
      const b3 = toIso(BX1, BY1, z - slabH);
      const b4 = toIso(BX0, BY1, z - slabH);

      ctx.beginPath();
      ctx.moveTo(p4.x, p4.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.lineTo(b3.x, b3.y);
      ctx.lineTo(b4.x, b4.y);
      ctx.closePath();
      ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
      ctx.fill();
      ctx.stroke();

      const labelPos = toIso(BX0 + 10, BY1 - 10, z);
      ctx.font = "bold 12px sans-serif";
      ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
      ctx.fillText(floorData.kode + " • " + floorData.navn.toUpperCase(), labelPos.x, labelPos.y);

      ctx.restore();
    }}

    function drawShafts(offsets) {{
      ctx.save();
      const grupper = {{}};
      MODEL.etasjer.forEach(e => e.rom.forEach(r => {{
        if (!r.sjakt) return;
        (grupper[r.sjakt] = grupper[r.sjakt] || {{ rom: r, etasjer: [] }}).etasjer.push(e.etasje_nr);
      }}));
      ctx.strokeStyle = "rgba(59, 130, 246, 0.35)";
      ctx.lineWidth = 1.5;
      ctx.font = "10px sans-serif";
      ctx.fillStyle = "rgba(147, 197, 253, 0.8)";
      Object.entries(grupper).forEach(([navn, g]) => {{
        if (g.etasjer.length < 2) return;
        const zBunn = offsets[Math.min(...g.etasjer)];
        const zTopp = offsets[Math.max(...g.etasjer)] + 40;
        const r = g.rom;
        const hjorner = [[r.x, r.y], [r.x + r.w, r.y], [r.x + r.w, r.y + r.h], [r.x, r.y + r.h]];
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        hjorner.forEach(([x, y]) => {{
          const p = toIso(x, y, zBunn);
          const q = toIso(x, y, zTopp);
          ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
        }});
        ctx.stroke();
        ctx.setLineDash([]);
        const midt = toIso(r.x + r.w / 2, r.y + r.h / 2, (zBunn + zTopp) / 2);
        ctx.fillText("↕ " + navn.toUpperCase(), midt.x, midt.y);
      }});
      ctx.restore();
    }}

    function sortRoomsByDepth(rooms) {{
      return [...rooms].sort((a, b) => {{
        let dA = a.x + a.y;
        let dB = b.x + b.y;
        if (rotationIndex === 1) {{ dA = -a.y + a.x; dB = -b.y + b.x; }}
        else if (rotationIndex === 2) {{ dA = -a.x - a.y; dB = -b.x - b.y; }}
        else if (rotationIndex === 3) {{ dA = a.y - a.x; dB = b.y - b.x; }}
        return dA - dB;
      }});
    }}

    function getRoomColor(room) {{
      if (currentZone === 'sikkerhet') {{
        const sone = MODEL.soner_definisjon.sikkerhet[room.sikkerhetssone];
        return sone ? sone.farge : "#3b82f6";
      }} else if (currentZone === 'klima') {{
        const klima = MODEL.soner_definisjon.klima[room.klimasone];
        return klima ? klima.farge : "#8b5cf6";
      }} else if (currentZone === 'maskin') {{
        // Rommet får fargen til den verste maskinstatusen i rommet; rom uten maskiner tones ned.
        const ms = maskinerIRom(room.id);
        if (!ms.length) return "#111827";
        const verst = ms.reduce((a, m) => STATUSRANG[m.status] > STATUSRANG[a] ? m.status : a, 'i_drift');
        return MASKINSTATUS[verst];
      }} else {{
        if (room.id.startsWith("SAL")) return "#475569";
        if (room.id.startsWith("MAG")) return "#334155";
        return "#1e293b";
      }}
    }}

    function drawRoom25D(room, floorData, zBase) {{
      const x = room.x;
      const y = room.y;
      const w = room.w;
      const h = room.h;
      const wallH = (room.takhoyde_m || 4.0) * 3.5;

      const isHovered = (hoveredRoom && hoveredRoom.id === room.id);
      const isSelected = (selectedRoom && selectedRoom.id === room.id);
      const baseColor = getRoomColor(room);

      const b1 = toIso(x, y, zBase);
      const b2 = toIso(x + w, y, zBase);
      const b3 = toIso(x + w, y + h, zBase);
      const b4 = toIso(x, y + h, zBase);

      const t1 = toIso(x, y, zBase + wallH);
      const t2 = toIso(x + w, y, zBase + wallH);
      const t3 = toIso(x + w, y + h, zBase + wallH);
      const t4 = toIso(x, y + h, zBase + wallH);

      ctx.save();

      clickableHitBoxes.push({{
        room: room,
        floor: floorData,
        poly: [t1, t2, t3, t4, b3, b4]
      }});

      ctx.beginPath();
      ctx.moveTo(b1.x, b1.y);
      ctx.lineTo(b2.x, b2.y);
      ctx.lineTo(b3.x, b3.y);
      ctx.lineTo(b4.x, b4.y);
      ctx.closePath();
      ctx.fillStyle = baseColor;
      ctx.globalAlpha = isHovered ? 0.95 : (isSelected ? 1.0 : 0.75);
      ctx.fill();

      ctx.globalAlpha = isHovered ? 0.45 : (isSelected ? 0.55 : 0.25);

      ctx.beginPath();
      ctx.moveTo(b2.x, b2.y);
      ctx.lineTo(b3.x, b3.y);
      ctx.lineTo(t3.x, t3.y);
      ctx.lineTo(t2.x, t2.y);
      ctx.closePath();
      ctx.fillStyle = baseColor;
      ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,0.4)";
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(b4.x, b4.y);
      ctx.lineTo(b3.x, b3.y);
      ctx.lineTo(t3.x, t3.y);
      ctx.lineTo(t4.x, t4.y);
      ctx.closePath();
      ctx.fillStyle = baseColor;
      ctx.fill();
      ctx.stroke();

      ctx.globalAlpha = 1.0;
      ctx.strokeStyle = isSelected ? "#ffffff" : (isHovered ? "#93c5fd" : "rgba(255,255,255,0.4)");
      ctx.lineWidth = isSelected ? 2.5 : (isHovered ? 2.0 : 1.0);

      ctx.beginPath();
      ctx.moveTo(t1.x, t1.y);
      ctx.lineTo(t2.x, t2.y);
      ctx.lineTo(t3.x, t3.y);
      ctx.lineTo(t4.x, t4.y);
      ctx.closePath();
      ctx.stroke();

      const centerPos = toIso(x + w / 2, y + h / 2, zBase + 2);
      ctx.textAlign = "center";
      ctx.fillStyle = "#ffffff";
      // Smale rom (under 4 m) viser bare romnummer, som i plantegningene.
      if (Math.min(room.w, room.h) < 40) {{
        ctx.font = "bold " + Math.max(7, Math.round(9 * camera.zoom)) + "px sans-serif";
        ctx.fillText(room.romnummer, centerPos.x, centerPos.y + 3);
        ctx.restore();
        return;
      }}
      ctx.font = isHovered ? "bold 12px sans-serif" : "bold 11px sans-serif";
      ctx.fillText(room.id, centerPos.x, centerPos.y - 6);

      ctx.font = "10px sans-serif";
      ctx.fillStyle = "rgba(255,255,255,0.8)";
      const shortName = room.navn.split("–")[0].trim();
      ctx.fillText(shortName, centerPos.x, centerPos.y + 7);

      ctx.font = "9px sans-serif";
      ctx.fillStyle = "rgba(203, 213, 225, 0.7)";
      ctx.fillText(room.areal_m2 + " m²", centerPos.x, centerPos.y + 18);

      ctx.restore();
    }}

    function drawExteriorShell(floorData, zBase) {{
      ctx.save();
      const wallH = (floorData.takhoyde_m || 5.0) * 8.0;
      // Dybde mot betrakteren etter rotasjon (samme transform som toIso): større = nærmere.
      function dybde(x, y) {{
        let rx = x - BCX, ry = y - BCY;
        if (rotationIndex === 1) {{ [rx, ry] = [-ry, rx]; }}
        else if (rotationIndex === 2) {{ rx = -rx; ry = -ry; }}
        else if (rotationIndex === 3) {{ [rx, ry] = [ry, -rx]; }}
        return rx + ry;
      }}
      const volumer = [...FOT.volumer].sort((a, b) => dybde(a.x + a.b / 2, a.y + a.d / 2) - dybde(b.x + b.b / 2, b.y + b.d / 2));
      volumer.forEach(v => {{
        const tegl = v.materiale === "tegl";
        const b3 = toIso(v.x + v.b, v.y + v.d, zBase), b4 = toIso(v.x, v.y + v.d, zBase), b2 = toIso(v.x + v.b, v.y, zBase);
        const t3 = toIso(v.x + v.b, v.y + v.d, zBase + wallH), t4 = toIso(v.x, v.y + v.d, zBase + wallH), t2 = toIso(v.x + v.b, v.y, zBase + wallH);
        const hj = [[v.x, v.y], [v.x + v.b, v.y], [v.x + v.b, v.y + v.d], [v.x, v.y + v.d]];
        const alle = [0, 1, 2, 3].map(i => {{
          const [a, c] = [hj[i], hj[(i + 1) % 4]];
          return {{ d: dybde((a[0] + c[0]) / 2, (a[1] + c[1]) / 2),
                   p: [toIso(a[0], a[1], zBase), toIso(c[0], c[1], zBase), toIso(c[0], c[1], zBase + wallH), toIso(a[0], a[1], zBase + wallH)] }};
        }});
        const flater = alle.sort((a, b) => a.d - b.d).slice(2).map(f => f.p);
        flater.forEach((f, i) => {{
          ctx.beginPath();
          ctx.moveTo(f[0].x, f[0].y);
          f.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
          ctx.closePath();
          ctx.fillStyle = tegl ? (i === 0 ? "#991b1b" : "#7f1d1d") : (i === 0 ? "rgba(56, 189, 248, 0.45)" : "rgba(56, 189, 248, 0.30)");
          ctx.fill();
          ctx.strokeStyle = tegl ? "rgba(255,255,255,0.2)" : "#38bdf8";
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }});
        if (tegl && floorData.etasje_nr === 2) {{
          const t1 = toIso(v.x, v.y, zBase + wallH);
          const topp = toIso(v.x + v.b / 2, v.y + v.d / 2, zBase + wallH + 40);
          [[t1, t2, "#0d9488"], [t4, t3, "#0f766e"]].forEach(([a, b, farge]) => {{
            ctx.beginPath();
            ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.lineTo(topp.x, topp.y);
            ctx.closePath();
            ctx.fillStyle = farge;
            ctx.fill();
          }});
        }}
      }});
      const annotPos = toIso(BCX, BY1 + 5, zBase + wallH / 2);
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 12px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(floorData.navn + " – tegl 1912 og glass 2016", annotPos.x, annotPos.y);
      ctx.restore();
    }}

    function updateLegendUI() {{
      const content = document.getElementById('legend-content');
      const heading = document.getElementById('legend-heading');

      if (currentMode === 'exterior') {{
        heading.innerText = "Fasade & Eksteriør";
        content.innerHTML = `
          <div class="legend-item"><div class="legend-color" style="background:#991b1b;"></div><span>Hovedfløy (1912) – Rød håndbanket tegl</span></div>
          <div class="legend-item"><div class="legend-color" style="background:#0d9488;"></div><span>Mansardtak – Patinert kobber</span></div>
          <div class="legend-item"><div class="legend-color" style="background:#38bdf8;"></div><span>Tilbygg Øst (2016) – Strukturelt glass & eik</span></div>
          <div class="legend-item"><div class="legend-color" style="background:#64748b;"></div><span>Sokkel – Råhugget Trondhjemitt-granitt</span></div>
        `;
        return;
      }}

      if (currentZone === 'maskin') {{
        heading.innerText = "Maskinpark (" + MASKINPARK.maskiner.length + " maskiner)";
        const antall = {{}};
        MASKINPARK.maskiner.forEach(m => antall[m.status] = (antall[m.status] || 0) + 1);
        const tekst = {{ i_drift: 'I drift', varsel: 'Varsel', feil: 'Feil', vedlikehold: 'Vedlikehold' }};
        content.innerHTML = Object.keys(MASKINSTATUS).map(s =>
          `<div class="legend-item"><div class="legend-color" style="background:${{MASKINSTATUS[s]}};"></div><span>${{tekst[s]}} (${{antall[s] || 0}})</span></div>`).join('');
        return;
      }}

      if (currentZone === 'sikkerhet') {{
        heading.innerText = "Sikkerhetssoner (Adgang)";
        const defs = MODEL.soner_definisjon.sikkerhet;
        let html = '';
        for (let k in defs) {{
          html += `<div class="legend-item"><div class="legend-color" style="background:${{defs[k].farge}};"></div><span>${{defs[k].navn}}</span></div>`;
        }}
        content.innerHTML = html;
      }} else if (currentZone === 'klima') {{
        heading.innerText = "Klimasoner (Konservering)";
        const defs = MODEL.soner_definisjon.klima;
        let html = '';
        for (let k in defs) {{
          html += `<div class="legend-item"><div class="legend-color" style="background:${{defs[k].farge}};"></div><span>${{defs[k].navn}} (${{defs[k].temp}})</span></div>`;
        }}
        content.innerHTML = html;
      }} else {{
        heading.innerText = "Arkitektur & Rom";
        content.innerHTML = `
          <div class="legend-item"><div class="legend-color" style="background:#475569;"></div><span>Faste samlingssaler (A, B, C, D)</span></div>
          <div class="legend-item"><div class="legend-color" style="background:#334155;"></div><span>Magasiner & lager</span></div>
          <div class="legend-item"><div class="legend-color" style="background:#1e293b;"></div><span>Publikum & Kafé / Butikk</span></div>
          <div class="legend-item"><div class="legend-color" style="background:#3b82f6;"></div><span>Heis- og trappeforbindelse</span></div>
        `;
      }}
    }}

    function isPointInPoly(pt, poly) {{
      let inside = false;
      for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {{
        const xi = poly[i].x, yi = poly[i].y;
        const xj = poly[j].x, yj = poly[j].y;
        const intersect = ((yi > pt.y) !== (yj > pt.y)) && (pt.x < (xj - xi) * (pt.y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
      }}
      return inside;
    }}

    viewport.addEventListener('mousedown', (e) => {{
      camera.isDragging = true;
      camera.startX = e.clientX - camera.x;
      camera.startY = e.clientY - camera.y;
    }});

    window.addEventListener('mouseup', () => {{
      camera.isDragging = false;
    }});

    viewport.addEventListener('mousemove', (e) => {{
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      if (camera.isDragging) {{
        camera.x = e.clientX - camera.startX;
        camera.y = e.clientY - camera.startY;
        render();
        return;
      }}

      let hit = null;
      for (let i = clickableHitBoxes.length - 1; i >= 0; i--) {{
        const item = clickableHitBoxes[i];
        if (isPointInPoly({{ x: mouseX, y: mouseY }}, item.poly)) {{
          hit = item.room;
          break;
        }}
      }}

      if (hit !== hoveredRoom) {{
        hoveredRoom = hit;
        render();
      }}

      if (hoveredRoom) {{
        tooltip.style.display = 'block';
        tooltip.style.left = (e.clientX + 14) + 'px';
        tooltip.style.top = (e.clientY + 14) + 'px';
        tooltip.innerHTML = `<strong>${{hoveredRoom.id}}</strong> • ${{hoveredRoom.navn}}<br><span style="color:#94a3b8">${{hoveredRoom.areal_m2}} m² | ${{hoveredRoom.sikkerhetssone}} | ${{hoveredRoom.klimasone}}</span>`;
      }} else {{
        tooltip.style.display = 'none';
      }}
    }});

    viewport.addEventListener('click', (e) => {{
      if (hoveredRoom) {{
        openDrawer(hoveredRoom);
      }}
    }});

    function openDrawer(room) {{
      selectedRoom = room;
      render();

      document.getElementById('drawer-room-id').innerText = room.id;
      document.getElementById('drawer-room-name').innerText = room.navn;
      document.getElementById('drawer-areal').innerText = room.areal_m2 + ' m²';
      document.getElementById('drawer-hoyde').innerText = (room.takhoyde_m || 4.0) + ' m';
      document.getElementById('drawer-kapasitet').innerText = room.kapasitet_verk ? room.kapasitet_verk + ' verk' : '–';
      document.getElementById('drawer-brann').innerText = room.brannklasse || 'EI-60';
      document.getElementById('drawer-romnr').innerText = room.romnummer || '–';
      document.getElementById('drawer-desc').innerText = room.beskrivelse;

      const mat = room.materialer || {{}};
      document.getElementById('drawer-materialer').innerHTML = `
        <strong>Gulv:</strong> ${{mat.gulv || '–'}}<br>
        <strong>Vegg:</strong> ${{mat.vegg || '–'}}<br>
        <strong>Himling:</strong> ${{mat.himling || '–'}}
      `;

      const imgBox = document.getElementById('drawer-image-box');
      const imgEl = document.getElementById('drawer-img');
      const imgCaption = document.getElementById('drawer-img-caption');

      if (ROOM_IMAGES[room.id]) {{
        imgBox.style.display = 'block';
        imgEl.src = ROOM_IMAGES[room.id];
        imgCaption.innerText = "Arkitektonisk gjengivelse av " + room.id + " (Trondheim)";
      }} else {{
        imgBox.style.display = 'none';
      }}

      const sDef = MODEL.soner_definisjon.sikkerhet[room.sikkerhetssone];
      const kDef = MODEL.soner_definisjon.klima[room.klimasone];

      const sBadge = document.getElementById('drawer-badge-sone');
      sBadge.innerText = sDef ? sDef.kode + " " + sDef.navn.split("–")[1] : room.sikkerhetssone;
      sBadge.style.background = sDef ? sDef.farge : "#3b82f6";
      sBadge.style.color = "#ffffff";

      const kBadge = document.getElementById('drawer-badge-klima');
      kBadge.innerText = kDef ? kDef.kode + " " + kDef.navn.split("–")[1] : room.klimasone;
      kBadge.style.background = kDef ? kDef.farge : "#8b5cf6";
      kBadge.style.color = "#ffffff";

      if (kDef) {{
        document.getElementById('drawer-lys').innerText = kDef.luks || '–';
        document.getElementById('drawer-klima-desc').innerHTML = `
          <strong>Krav:</strong> ${{kDef.temp}} | ${{kDef.rf}}<br>
          <strong>Belysning:</strong> ${{kDef.luks}} | UV: ${{kDef.uv}}<br>
          <em>${{kDef.beskrivelse}}</em>
        `;
      }}

      if (sDef) {{
        document.getElementById('drawer-sikkerhet-desc').innerHTML = `
          <strong>Beskrivelse:</strong> ${{sDef.beskrivelse}}<br>
          <strong>Operative krav:</strong> ${{sDef.krav}}
        `;
      }}

      const sensorDiv = document.getElementById('drawer-sensorer');
      sensorDiv.innerHTML = '';
      if (room.sensorer && room.sensorer.length > 0) {{
        room.sensorer.forEach(s => {{
          const span = document.createElement('span');
          span.className = 'tag';
          span.innerText = s;
          sensorDiv.appendChild(span);
        }});
      }} else {{
        sensorDiv.innerHTML = '<span style="color:#64748b; font-size:12px;">Ingen dedikerte kartsensorer</span>';
      }}

      const maskinDiv = document.getElementById('drawer-maskiner');
      const ms = maskinerIRom(room.id);
      maskinDiv.innerHTML = ms.length ? '' : '<span style="color:#64748b; font-size:12px;">Ingen maskiner i rommet</span>';
      ms.forEach(m => {{
        const apne = MASKINPARK.hendelser.filter(h => h.maskin_id === m.maskin_id && !h.lukket);
        const span = document.createElement('span');
        span.className = 'tag';
        span.style.borderLeft = '3px solid ' + MASKINSTATUS[m.status];
        span.title = apne.map(h => h.beskrivelse).join('; ');
        span.innerText = m.maskin_id.replace('KP-MASK-', '') + ' · ' + m.navn + ' · ' + m.status.replace('_', ' ') + (apne.length ? ' (' + apne.length + ' åpen)' : '');
        maskinDiv.appendChild(span);
      }});

      document.getElementById('drawer').classList.add('open');
    }}

    function closeDrawer() {{
      selectedRoom = null;
      document.getElementById('drawer').classList.remove('open');
      render();
    }}

    function openImageModal(src, title, desc) {{
      openDrawer({{
        id: title,
        navn: title,
        areal_m2: "–",
        takhoyde_m: "–",
        brannklasse: "–",
        romnummer: "–",
        materialer: {{ gulv: "–", vegg: "–", himling: "–" }},
        sikkerhetssone: "S1",
        klimasone: "K3",
        beskrivelse: desc,
        sensorer: []
      }});
      const imgBox = document.getElementById('drawer-image-box');
      const imgEl = document.getElementById('drawer-img');
      const imgCaption = document.getElementById('drawer-img-caption');
      imgBox.style.display = 'block';
      imgEl.src = src;
      imgCaption.innerText = title;
    }}

    function setMode(mode) {{
      currentMode = mode;
      document.getElementById('btn-mode-interior').classList.toggle('active', mode === 'interior');
      document.getElementById('btn-mode-exterior').classList.toggle('active', mode === 'exterior');
      render();
    }}

    function setFloor(floor) {{
      currentFloor = floor;
      ['all', 0, 1, 2].forEach(f => {{
        const btn = document.getElementById('floor-' + f);
        if (btn) btn.classList.toggle('active', currentFloor === f);
      }});
      if (mainView === '2d') {{
        updateBlueprintFloor();
      }} else {{
        render();
      }}
    }}

    function setZone(zone) {{
      currentZone = zone;
      ['ark', 'sikkerhet', 'klima', 'maskin'].forEach(z => {{
        const btn = document.getElementById('zone-' + z);
        if (btn) btn.classList.toggle('active', currentZone === z);
      }});
      render();
    }}

    function rotateView(dir) {{
      rotationIndex = (rotationIndex + dir + 4) % 4;
      render();
    }}

    function zoomView(factor) {{
      camera.zoom *= factor;
      camera.zoom = Math.max(0.4, Math.min(camera.zoom, 3.0));
      render();
    }}

    function resetView() {{
      camera.x = 0;
      camera.y = 0;
      // Startzoom slik at hele fotavtrykket (pluss bakke) får plass i vinduet.
      const isoBredde = (BX1 - BX0 + BY1 - BY0 + 220) * 0.866;
      camera.zoom = Math.min(1.0, viewport.clientWidth / isoBredde, viewport.clientHeight / (isoBredde * 0.75));
      rotationIndex = 0;
      render();
    }}

    viewport.addEventListener('wheel', (e) => {{
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      zoomView(zoomFactor);
    }}, {{ passive: false }});

    initGalleryGrid();
    resizeCanvas();
    resetView();
  </script>
</body>
</html>
"""
    return html


def build():
    print(f"Leser geometri fra {JSON_PATH}...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    floor_filenames = {
        0: "plantegning_u1.svg",
        1: "plantegning_p1.svg",
        2: "plantegning_p2.svg"
    }

    for floor in data.get("etasjer", []):
        fnr = floor["etasje_nr"]
        svg_content = generate_blueprint_svg(floor, data)
        svg_path = BASE_DIR / floor_filenames[fnr]
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Skrev 2D blueprint SVG for etasje {fnr}: {svg_path.name}")

    # Fasader og snitt tegnes fra samme modell (06_kart/fasader.py).
    import importlib.util
    spec = importlib.util.spec_from_file_location("kp_fasader", BASE_DIR / "fasader.py")
    fasader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fasader)
    for sti in fasader.skriv_alle(data, BASE_DIR):
        print(f"Skrev fasade/snitt: {sti.name}")

    print(f"Genererer interaktivt bygningskart til {HTML_PATH}...")
    html_content = generate_html(data)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Fullført! {HTML_PATH.name} er skrevet ({len(html_content)} tegn).")


if __name__ == "__main__":
    build()
