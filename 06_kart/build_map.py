"""
Byggeskript for interaktivt 2.5D isometrisk bygningskart, 2D-plantegninger og Trondheim-galleri for Aura Museum.
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


def generate_blueprint_svg(floor_data: dict, model_data: dict) -> str:
    floor_nr = floor_data["etasje_nr"]
    kode = floor_data["kode"]
    navn = floor_data["navn"]
    rooms = floor_data.get("rom", [])
    
    museum = model_data["museum"]
    matrikkel = museum.get("matrikkel", {})
    arealer = museum.get("arealer_ns3940", {})
    brann = museum.get("brannkonsept", {})

    bta_val = arealer.get("bta_m2", 4350)
    bra_val = arealer.get("bra_m2", 3920)
    bya_val = arealer.get("bya_m2", 1450)
    tomt_val = arealer.get("tomteareal_m2", 3200)
    utnyttelse_val = arealer.get("utnyttelsesgrad_prosent_bya", 45.3)

    bkl_val = brann.get("brannklasse", "BKL 3")
    rkl_val = brann.get("risikoklasse", "RKL 5")

    if floor_nr == 0:
        kote_display = "KOTE FG: -4.200 m (+9.30 moh / 9.30 moh)"
        kote_val_str = "+9.30 moh"
        tegningsnr_display = "A-001 (A-10-01)"
    elif floor_nr == 1:
        kote_display = "KOTE FG: ±0.000 m (+13.50 moh / 13.50 moh) | TERRENG: +13.27 moh DTM1"
        kote_val_str = "+13.50 moh (±0.000)"
        tegningsnr_display = "A-101 (A-10-02)"
    else:
        kote_display = "KOTE FG: +6.300 m (+19.80 moh / 19.80 moh) | GESIMS: +11.400 m (+24.90 moh)"
        kote_val_str = "+19.80 moh (+6.30m)"
        tegningsnr_display = "A-201 (A-10-03)"

    OFFSET_X = 65
    OFFSET_Y = 100

    svg_parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 680" width="100%" height="100%" class="blueprint-svg">',
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
        '',
        '  <!-- Ren, minimalistisk mørk bakgrunn -->',
        '  <rect width="100%" height="100%" fill="#0a0f1d"/>',
        '',
        '  <!-- Diskret etasjekote over bygget -->',
        f'  <text x="105" y="65" font-family="sans-serif" font-size="11" font-weight="600" fill="#38bdf8">{kote_display}</text>',
        '',
        '  <!-- Bygningsvegger med skravur iht. NS 8351 -->',
        '  <g class="architectural-walls">',
        '    <!-- Hovedfløy 400 mm Yttervegg i tegl/mur -->',
        '    <rect x="101" y="136" width="4" height="248" fill="url(#hatch-tegl-400)" stroke="#38bdf8" stroke-width="1.2"/>',
        '    <rect x="101" y="136" width="344" height="4" fill="url(#hatch-tegl-400)" stroke="#38bdf8" stroke-width="1.2"/>',
        '    <rect x="101" y="380" width="344" height="4" fill="url(#hatch-tegl-400)" stroke="#38bdf8" stroke-width="1.2"/>',
        '    <!-- Tilbygg Øst 300 mm Yttervegg i slipt betong -->',
        '    <rect x="585" y="137" width="3" height="246" fill="url(#hatch-betong-300)" stroke="#38bdf8" stroke-width="1.2"/>',
        '    <rect x="445" y="137" width="143" height="3" fill="url(#hatch-betong-300)" stroke="#38bdf8" stroke-width="1.2"/>',
        '    <rect x="445" y="380" width="143" height="3" fill="url(#hatch-betong-300)" stroke="#38bdf8" stroke-width="1.2"/>',
    ]

    # Etasjetilpassede bærevegger
    if floor_nr == 0:
        svg_parts.extend([
            '    <rect x="444" y="140" width="2" height="240" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
            '    <rect x="105" y="279" width="480" height="2" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
            '    <rect x="284" y="140" width="2" height="140" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
        ])
    elif floor_nr == 1:
        svg_parts.extend([
            '    <rect x="444" y="140" width="2" height="240" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
            '    <rect x="105" y="259" width="480" height="2" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
            '    <rect x="284" y="140" width="2" height="120" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
        ])
    else:
        svg_parts.extend([
            '    <rect x="444" y="140" width="2" height="240" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
            '    <rect x="304" y="140" width="2" height="120" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
            '    <rect x="504" y="140" width="2" height="120" fill="url(#hatch-baerevegg-200)" stroke="#38bdf8" stroke-width="1"/>',
        ])

    svg_parts.extend([
        '  </g>',
        '',
        '  <!-- Bygningskropp underlag -->',
        '  <rect x="105" y="140" width="480" height="240" fill="rgba(15, 23, 42, 0.45)" stroke="#38bdf8" stroke-width="1"/>',
    ])

    if floor_nr == 1:
        svg_parts.extend([
            '  <!-- Enkel, innbydende inngang fra Bispegata -->',
            '  <line x1="105" y1="420" x2="585" y2="420" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="4,4"/>',
            '  <g class="entrance-portal" transform="translate(345, 405)">',
            '    <polygon points="0,-10 6,-3 -6,-3" fill="#38bdf8"/>',
            '    <text x="0" y="8" font-family="sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle" letter-spacing="1">▲ HOVEDINNGANG FRA BISPEGATA</text>',
            '  </g>',
            '  <text x="50" y="260" font-family="sans-serif" font-size="10" font-weight="600" fill="#64748b" transform="rotate(-90 50 260)" letter-spacing="2" text-anchor="middle">◀ MOT NIDAROSDOMEN</text>',
            '  <text x="635" y="260" font-family="sans-serif" font-size="10" font-weight="600" fill="#0284c7" transform="rotate(90 635 260)" letter-spacing="2" text-anchor="middle">≋ NIDELVA ≋</text>',
        ])

    # Tegn rommene - RENT OG MINIMALISTISK
    for r in rooms:
        rx = r["x"] + OFFSET_X
        ry = r["y"] + OFFSET_Y
        rw = r["w"]
        rh = r["h"]
        rid = r["id"]
        rnummer = html.escape(str(r.get("romnummer", "")))
        rnavn_kort = html.escape(r.get("romnavn_kort", r["navn"].split("–")[0].strip()))
        areal = r["areal_m2"]
        hoyde = r.get("takhoyde_m", 4.0)
        sone_s = html.escape(str(r.get("sikkerhetssone", "S1")))
        sone_k = html.escape(str(r.get("klimasone", "K3")))
        brann_str = r.get("brannklasse", "EI-60")
        brann_kort = html.escape(str(brann_str.split()[0] if brann_str else "EI-60"))

        # Rene, stilige fargetoner
        if rid in ["SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E"]:
            fill_color = "rgba(245, 158, 11, 0.20)"
            border_color = "#f59e0b"
            title_color = "#fef08a"
        elif rid in ["KAF-1"]:
            fill_color = "rgba(16, 185, 129, 0.20)"
            border_color = "#10b981"
            title_color = "#a7f3d0"
        elif rid in ["BUT-1"]:
            fill_color = "rgba(168, 85, 247, 0.20)"
            border_color = "#a855f7"
            title_color = "#e9d5ff"
        elif rid in ["RES-1"]:
            fill_color = "rgba(14, 165, 233, 0.20)"
            border_color = "#0ea5e9"
            title_color = "#bae6fd"
        elif rid.startswith("MAG") or rid.startswith("VER"):
            fill_color = "rgba(239, 68, 68, 0.20)"
            border_color = "#ef4444"
            title_color = "#fecaca"
        elif rid.startswith("TRAPP") or rid.startswith("HEIS"):
            fill_color = "rgba(100, 116, 139, 0.35)"
            border_color = "#94a3b8"
            title_color = "#ffffff"
        else:
            fill_color = "rgba(51, 65, 85, 0.30)"
            border_color = "#64748b"
            title_color = "#f8fafc"

        cx = rx + rw / 2
        cy = ry + rh / 2
        if rid == "RES-1":
            cy = ry + 70

        # Enkel tittel og areal (KUN 2 RENE LINJER!)
        display_title = rnavn_kort
        if rid.startswith("TRAPP"):
            display_title = "TRAPP"
        elif rid.startswith("HEIS"):
            display_title = "HEIS"

        font_size = 12 if (rw >= 100 and rh >= 80) else 9.5

        svg_parts.extend([
            f'  <g class="blueprint-room" data-room-id="{rid}" style="cursor: pointer;">',
            f'    <desc>H: {hoyde:.1f} m | BRA {areal} m² | {brann_kort} | {sone_s}/{sone_k}</desc>',
            f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{fill_color}" stroke="{border_color}" stroke-width="1.8"/>',
            f'    <!-- Minimalistisk romtekst -->',
            f'    <text x="{cx}" y="{cy - 2}" font-family="sans-serif" font-size="{font_size}" font-weight="bold" fill="{title_color}" text-anchor="middle">{display_title}</text>',
            f'    <text x="{cx}" y="{cy + 13}" font-family="sans-serif" font-size="{font_size * 0.75:.1f}" font-weight="500" fill="#cbd5e1" text-anchor="middle">{areal} m²</text>',
            f'  </g>',
        ])

        # Trappetrinn
        if rid.startswith("TRAPP"):
            for ty in range(int(ry + 6), int(ry + rh - 6), 5):
                svg_parts.append(f'  <line x1="{rx + 4}" y1="{ty}" x2="{rx + rw - 4}" y2="{ty}" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>')
        elif rid.startswith("HEIS"):
            svg_parts.append(f'  <line x1="{rx + 4}" y1="{ry + 4}" x2="{rx + rw - 4}" y2="{ry + rh - 4}" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>')
            svg_parts.append(f'  <line x1="{rx + rw - 4}" y1="{ry + 4}" x2="{rx + 4}" y2="{ry + rh - 4}" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>')

        # Døråpning
        dor_pos = r.get("dor_pos", "sor")
        if dor_pos == "sor":
            dx = rx + rw / 2
            dy = ry + rh
            svg_parts.append(f'  <line x1="{dx - 8}" y1="{dy}" x2="{dx + 8}" y2="{dy}" stroke="#0a0f1d" stroke-width="3"/>')
            svg_parts.append(f'  <line x1="{dx - 8}" y1="{dy}" x2="{dx + 8}" y2="{dy - 10}" stroke="{border_color}" stroke-width="1.2"/>')
        elif dor_pos == "nord":
            dx = rx + rw / 2
            dy = ry
            svg_parts.append(f'  <line x1="{dx - 8}" y1="{dy}" x2="{dx + 8}" y2="{dy}" stroke="#0a0f1d" stroke-width="3"/>')
            svg_parts.append(f'  <line x1="{dx - 8}" y1="{dy}" x2="{dx + 8}" y2="{dy + 10}" stroke="{border_color}" stroke-width="1.2"/>')
        elif dor_pos == "vest":
            dx = rx
            dy = ry + rh / 2
            svg_parts.append(f'  <line x1="{dx}" y1="{dy - 8}" x2="{dx}" y2="{dy + 8}" stroke="#0a0f1d" stroke-width="3"/>')
            svg_parts.append(f'  <line x1="{dx}" y1="{dy - 8}" x2="{dx + 10}" y2="{dy + 8}" stroke="{border_color}" stroke-width="1.2"/>')
        elif dor_pos == "ost":
            dx = rx + rw
            dy = ry + rh / 2
            svg_parts.append(f'  <line x1="{dx}" y1="{dy - 8}" x2="{dx}" y2="{dy + 8}" stroke="#0a0f1d" stroke-width="3"/>')
            svg_parts.append(f'  <line x1="{dx}" y1="{dy - 8}" x2="{dx - 10}" y2="{dy + 8}" stroke="{border_color}" stroke-width="1.2"/>')

    # Subtile målekjeder (diskrete og ryddige)
    svg_parts.extend([
        '  <!-- Diskrete arkitektoniske målekjeder iht. NS 8351 -->',
        '  <g class="dimension-chain" style="opacity: 0.7;">',
        '    <line x1="105" y1="115" x2="585" y2="115" stroke="#64748b" stroke-width="0.8" marker-start="url(#tick-45)" marker-end="url(#tick-45)"/>',
        '    <line x1="105" y1="110" x2="105" y2="120" stroke="#38bdf8" stroke-width="1.2" class="arch-tick" transform="rotate(45 105 115)"/>',
        '    <line x1="585" y1="110" x2="585" y2="120" stroke="#38bdf8" stroke-width="1.2" class="arch-tick" transform="rotate(45 585 115)"/>',
        '    <text x="345" y="108" font-family="sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle">48 000 mm (48 m)</text>',
        '    <line x1="85" y1="140" x2="85" y2="380" stroke="#64748b" stroke-width="0.8" marker-start="url(#tick-45)" marker-end="url(#tick-45)"/>',
        '    <line x1="85" y1="135" x2="85" y2="145" stroke="#38bdf8" stroke-width="1.2" class="arch-tick" transform="rotate(45 85 140)"/>',
        '    <line x1="85" y1="375" x2="85" y2="385" stroke="#38bdf8" stroke-width="1.2" class="arch-tick" transform="rotate(45 85 380)"/>',
        '    <text x="75" y="260" font-family="sans-serif" font-size="9" fill="#94a3b8" text-anchor="end">24 000 mm</text>',
        '  </g>',
    ])

    # HØYRESIDE: ELEGANT SKANDINAVISK PLANOVERSIKT
    svg_parts.extend([
        '  <!-- Elegant skandinavisk planoversikt og romguide -->',
        '  <g class="title-block" transform="translate(680, 80)">',
        '    <text x="0" y="0" font-family="sans-serif" font-size="20" font-weight="bold" fill="#ffffff" letter-spacing="1">AURA MUSEUM</text>',
        f'    <text x="0" y="24" font-family="sans-serif" font-size="13" font-weight="600" fill="#38bdf8">PLAN {html.escape(kode)} • {html.escape(navn.upper())}</text>',
        '    <text x="0" y="44" font-family="sans-serif" font-size="10" fill="#94a3b8">Bispegata 9B, 7012 Trondheim • Gnr 401 / Bnr 12</text>',
        '    <line x1="0" y1="60" x2="280" y2="60" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>',
        '    <text x="0" y="85" font-family="sans-serif" font-size="10" font-weight="bold" fill="#64748b" letter-spacing="1">ROMLISTE &amp; AREALER (BRA)</text>',
    ])

    y_cursor = 110
    for r in rooms:
        rid = r["id"]
        rnavn = html.escape(r["navn"].split("–")[0].strip())
        areal = r["areal_m2"]
        hoyde = r.get("takhoyde_m", 4.0)
        
        dot_color = "#94a3b8"
        if rid in ["SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E"]:
            dot_color = "#f59e0b"
        elif rid in ["KAF-1"]:
            dot_color = "#10b981"
        elif rid in ["BUT-1"]:
            dot_color = "#a855f7"
        elif rid in ["RES-1"]:
            dot_color = "#0ea5e9"
        elif rid.startswith("MAG") or rid.startswith("VER"):
            dot_color = "#ef4444"

        svg_parts.extend([
            f'    <circle cx="6" cy="{y_cursor - 4}" r="4" fill="{dot_color}"/>',
            f'    <text x="18" y="{y_cursor}" font-family="sans-serif" font-size="11" font-weight="500" fill="#f8fafc">{rnavn}</text>',
            f'    <text x="280" y="{y_cursor}" font-family="sans-serif" font-size="11" font-weight="600" fill="#cbd5e1" text-anchor="end">{areal} m²</text>',
        ])
        y_cursor += 24

    svg_parts.extend([
        f'    <line x1="0" y1="{y_cursor + 10}" x2="280" y2="{y_cursor + 10}" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>',
        f'    <text x="0" y="{y_cursor + 32}" font-family="sans-serif" font-size="10" fill="#94a3b8">BTA: 4 350 m² (4350) • BRA: 3 920 m² (3920) • BYA: 1 450 m² (1450)</text>',
        f'    <text x="0" y="{y_cursor + 50}" font-family="sans-serif" font-size="10" fill="#94a3b8">Kote FG: {kote_val_str}</text>',
        f'    <text x="0" y="{y_cursor + 68}" font-family="sans-serif" font-size="9" fill="#64748b">Brannklasse BKL 3 / Risikoklasse RKL 5 • 401/12</text>',
        f'    <text x="0" y="{y_cursor + 86}" font-family="sans-serif" font-size="10" font-weight="bold" fill="#38bdf8">MÅLESTOKK 1:100</text>',
        '  </g>',
        '</svg>',
    ])

    return "\n".join(svg_parts)


def generate_html(data: dict) -> str:
    data_json = json.dumps(data, ensure_ascii=False)

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
        {"file": "bilder/01_eksterior_hovedfasade.jpg", "title": "01. Hovedfasade fra Bispegata", "cat": "Eksteriør", "desc": "Aura Museum i Bispegata. Hovedfløy fra 1912 i rød håndbanket tegl, trondhjemitt-granittsokkel, irrgrønt kobbertak og Nidarosdomens spir i bakgrunnen."},
        {"file": "bilder/02_eksterior_tilbygg_nidelva.jpg", "title": "02. Tilbygg Øst ved Nidelva", "cat": "Eksteriør", "desc": "2016-fløyen i strukturelt glass med vertikale spiler i lys eik og slipt betong, med de historiske trebryggene i Trondheim langs elvebredden."},
        {"file": "bilder/03_eksterior_skulpturhage.jpg", "title": "03. Skulpturhage i atriet", "cat": "Eksteriør", "desc": "Skjermet indre museumshage med granittheller, vannspeil, bronseskulpturer og åpen siktlinje mot Marinen-parken."},
        {"file": "bilder/04_vestibyle_resepsjon.jpg", "title": "04. Vestibyle & Resepsjon (P1)", "cat": "Publikum", "desc": "Ankomsthall med overlys fra glasstaket, lys grå terrazzo, minimalistisk skranke i mørk røkt eik med 'AURA MUSEUM'-tekst og adgangsporter."},
        {"file": "bilder/05_museumsbutikk.jpg", "title": "05. Museumsbutikk / Aura Bokhandel (P1)", "cat": "Publikum", "desc": "Kunstbøker, utstillingskataloger og skandinavisk formgivning i spesialbygde eikehyller med integrert LED-lys."},
        {"file": "bilder/06_museumskafe.jpg", "title": "06. Museumskafé mot Nidelva (P1)", "cat": "Publikum", "desc": "Kafé med 60 sitteplasser, skandinaviske designstoler i lys eik og panoramavinduer mot skulpturhagen, Nidelva og trebryggene."},
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
  <title>Aura Museum Trondheim – 2.5D Bygningskart &amp; Galleri</title>
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
        <p>{data['museum']['fiktiv_adresse']} • Nidelva &amp; Bispegata • BRA: 3 920 m² • BTA: 4 350 m² • BYA: 1 450 m² • {data['museum']['georeferanse']['moh']} m.o.h.</p>
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
          <h2>Aura Museum Trondheim – Arkitektonisk Fotoserie</h2>
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
    </div>
  </div>

  <script>
    const MODEL = {data_json};
    const ROOM_IMAGES = {room_images_json};
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

    function toIso(x, y, z) {{
      let cx = x - 280;
      let cy = y - 160;

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
      const p1 = toIso(-20, -20, -10);
      const p2 = toIso(580, -20, -10);
      const p3 = toIso(580, 340, -10);
      const p4 = toIso(-20, 340, -10);

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

      const s1 = toIso(-20, 310, -9);
      const s2 = toIso(580, 310, -9);
      ctx.beginPath();
      ctx.moveTo(s1.x, s1.y);
      ctx.lineTo(s2.x, s2.y);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
      ctx.lineWidth = 2;
      ctx.stroke();

      const streetLabel = toIso(280, 328, -9);
      ctx.font = "11px sans-serif";
      ctx.fillStyle = "rgba(156, 163, 175, 0.6)";
      ctx.textAlign = "center";
      ctx.fillText("BISPEGATA TRONDHEIM (HOVEDADKOMST)", streetLabel.x, streetLabel.y);
      ctx.restore();
    }}

    function drawFloorSlab(floorData, z) {{
      ctx.save();
      const p1 = toIso(20, 20, z);
      const p2 = toIso(540, 20, z);
      const p3 = toIso(540, 300, z);
      const p4 = toIso(20, 300, z);

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
      const b3 = toIso(540, 300, z - slabH);
      const b4 = toIso(20, 300, z - slabH);

      ctx.beginPath();
      ctx.moveTo(p4.x, p4.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.lineTo(b3.x, b3.y);
      ctx.lineTo(b4.x, b4.y);
      ctx.closePath();
      ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
      ctx.fill();
      ctx.stroke();

      const labelPos = toIso(30, 290, z);
      ctx.font = "bold 12px sans-serif";
      ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
      ctx.fillText(floorData.kode + " • " + floorData.navn.toUpperCase(), labelPos.x, labelPos.y);

      ctx.restore();
    }}

    function drawShafts(offsets) {{
      ctx.save();
      const zBottom = offsets[0];
      const zTop = offsets[2] + 40;

      const p1 = toIso(240, 180, zBottom);
      const p2 = toIso(280, 180, zBottom);
      const p3 = toIso(280, 220, zBottom);
      const p4 = toIso(240, 220, zBottom);

      const t1 = toIso(240, 180, zTop);
      const t2 = toIso(280, 180, zTop);
      const t3 = toIso(280, 220, zTop);
      const t4 = toIso(240, 220, zTop);

      ctx.strokeStyle = "rgba(59, 130, 246, 0.35)";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y); ctx.lineTo(t1.x, t1.y);
      ctx.moveTo(p2.x, p2.y); ctx.lineTo(t2.x, t2.y);
      ctx.moveTo(p3.x, p3.y); ctx.lineTo(t3.x, t3.y);
      ctx.moveTo(p4.x, p4.y); ctx.lineTo(t4.x, t4.y);
      ctx.stroke();
      ctx.setLineDash([]);

      const midPos = toIso(260, 200, (zBottom + zTop)/2);
      ctx.font = "10px sans-serif";
      ctx.fillStyle = "rgba(147, 197, 253, 0.8)";
      ctx.fillText("↕ HEIS- OG TRAPPESJAKT", midPos.x, midPos.y);

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

      const b1 = toIso(20, 20, zBase);
      const b2 = toIso(370, 20, zBase);
      const b3 = toIso(370, 300, zBase);
      const b4 = toIso(20, 300, zBase);

      const t1 = toIso(20, 20, zBase + wallH);
      const t2 = toIso(370, 20, zBase + wallH);
      const t3 = toIso(370, 300, zBase + wallH);
      const t4 = toIso(20, 300, zBase + wallH);

      ctx.beginPath();
      ctx.moveTo(b4.x, b4.y);
      ctx.lineTo(b3.x, b3.y);
      ctx.lineTo(t3.x, t3.y);
      ctx.lineTo(t4.x, t4.y);
      ctx.closePath();
      ctx.fillStyle = "#991b1b";
      ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,0.2)";
      ctx.stroke();

      const gb2 = toIso(540, 20, zBase);
      const gb3 = toIso(540, 300, zBase);
      const gt2 = toIso(540, 20, zBase + wallH);
      const gt3 = toIso(540, 300, zBase + wallH);

      ctx.beginPath();
      ctx.moveTo(b3.x, b3.y);
      ctx.lineTo(gb3.x, gb3.y);
      ctx.lineTo(gt3.x, gt3.y);
      ctx.lineTo(t3.x, t3.y);
      ctx.closePath();
      ctx.fillStyle = "rgba(56, 189, 248, 0.45)";
      ctx.fill();
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      if (floorData.etasje_nr === 2) {{
        const rTop = toIso(195, 160, zBase + wallH + 40);
        ctx.beginPath();
        ctx.moveTo(t1.x, t1.y);
        ctx.lineTo(t2.x, t2.y);
        ctx.lineTo(rTop.x, rTop.y);
        ctx.closePath();
        ctx.fillStyle = "#0d9488";
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(t4.x, t4.y);
        ctx.lineTo(t3.x, t3.y);
        ctx.lineTo(rTop.x, rTop.y);
        ctx.closePath();
        ctx.fillStyle = "#0f766e";
        ctx.fill();
      }}

      const annotPos = toIso(195, 305, zBase + wallH / 2);
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 12px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(floorData.navn + " – Rød Tegl & Glassfasade (Trondheim)", annotPos.x, annotPos.y);

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
      ['ark', 'sikkerhet', 'klima'].forEach(z => {{
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
      camera.zoom = 1.0;
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

    print(f"Genererer interaktivt bygningskart til {HTML_PATH}...")
    html_content = generate_html(data)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Fullført! {HTML_PATH.name} er skrevet ({len(html_content)} tegn).")


if __name__ == "__main__":
    build()
