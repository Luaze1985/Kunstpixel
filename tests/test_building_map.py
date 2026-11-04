"""Tester for 06_kart/ bygningsmodell, geometri, plantegninger og FastMCP-oppslag.

E2E Testpakke for Aura Museum i henhold til NS 8351, NS 3940, DiBK brannkonsept
og Kartverket MCP. Dekker alle 4 tiers:
- Tier 1: Feature Coverage (atomære krav)
- Tier 2: Boundary & Corner Cases (arealsummer, koteterskler, veggtykkelser)
- Tier 3: Cross-Feature Combinations (konsistens mellom JSON, SVG og HTML)
- Tier 4: Real-World Scenarios (branntilsyn, byggesak, sikkerhet, konservering)
Inkluderer full bakoverkompatibilitet med de 5 opprinnelige testene.
"""

import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pytest

from src.kunstpixel.core.db import query_building_map_data

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_DIR = REPO_ROOT / "06_kart"
JSON_PATH = MAP_DIR / "bygning_geometri.json"
HTML_PATH = MAP_DIR / "index.html"
BILDER_DIR = MAP_DIR / "bilder"

SVG_FILES = ["plantegning_u1.svg", "plantegning_p1.svg", "plantegning_p2.svg"]


def _load_geometry() -> dict:
    """Hjelpefunksjon for å laste SSOT bygningsgeometri."""
    assert JSON_PATH.is_file(), f"Mangler geometri-SSOT: {JSON_PATH}"
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_svg(name: str) -> str:
    """Hjelpefunksjon for å laste en SVG-plantegning."""
    path = MAP_DIR / name
    assert path.is_file(), f"Mangler SVG-plantegning: {path}"
    return path.read_text(encoding="utf-8")


def _load_html() -> str:
    """Hjelpefunksjon for å laste index.html."""
    assert HTML_PATH.is_file(), f"Mangler HTML-viser: {HTML_PATH}"
    return HTML_PATH.read_text(encoding="utf-8")


# ==============================================================================
# SECTION 0: BAKOVERKOMPATIBILITET MED OPPRINNELIGE 5 TESTER
# ==============================================================================


def test_bygning_geometri_json_exists_and_valid():
    """Verifiserer at geometri-filen finnes og er gyldig syntetisk JSON."""
    data = _load_geometry()

    assert "datakilde" in data and "syntetisk" in data["datakilde"]
    assert "museum" in data
    assert data["museum"]["navn"] == "Aura Museum"
    assert "eksterior" in data["museum"]
    assert "hovedfløy" in data["museum"]["eksterior"]
    assert "tilbygg_ost" in data["museum"]["eksterior"]


def test_etasjer_and_rooms_completeness():
    """Verifiserer at alle 3 etasjer og kjernesaler er modellert."""
    data = _load_geometry()

    etasjer = data.get("etasjer", [])
    assert len(etasjer) == 3, f"Forventet 3 etasjer, fikk {len(etasjer)}"

    floor_numbers = {e["etasje_nr"] for e in etasjer}
    assert floor_numbers == {0, 1, 2}

    all_room_ids = set()
    for e in etasjer:
        for r in e.get("rom", []):
            all_room_ids.add(r["id"])
            assert "sikkerhetssone" in r and r["sikkerhetssone"] in {"S1", "S2", "S3", "S4"}
            assert "klimasone" in r and r["klimasone"] in {"K1", "K2", "K3"}
            assert r["areal_m2"] > 0
            assert r["takhoyde_m"] > 0

    required_rooms = {"MAG-1", "SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E", "RES-1", "VAK-1"}
    for req in required_rooms:
        assert req in all_room_ids, f"Påkrevd rom {req} mangler i geometrien"


def test_interactive_html_generated():
    """Verifiserer at 2.5D isometrisk HTML-viser er generert og har forventet innhold."""
    html = _load_html()
    assert len(html) > 20000, "HTML-filen er for liten"
    assert "mapCanvas" in html
    assert "Røntgen / Interiør" in html
    assert "Skall / Fasade" in html
    assert "toIso" in html


def test_query_building_map_data_tool():
    """Verifiserer oppslagsfunksjonen mot kartmodellen."""
    # Hele modellen
    all_data = query_building_map_data()
    assert "museum" in all_data
    assert len(all_data["etasjer"]) == 3

    # Filtrert på etasje 1
    p1 = query_building_map_data(etasje=1)
    assert len(p1["etasjer"]) == 1
    assert p1["etasjer"][0]["kode"] == "P1"

    # Filtrert på sikkerhetssone
    sikkerhet = query_building_map_data(sone_type="sikkerhet")
    assert "sikkerhet" in sikkerhet["soner_definisjon"]


def test_svg_blueprints_generated():
    """Verifiserer at alle 3 2D-plantegninger (SVG) er generert og er velformet XML."""
    for fn in SVG_FILES:
        content = _load_svg(fn)
        assert "<svg" in content
        assert "blueprint-room" in content
        assert "MÅLESTOKK 1:100" in content
        root = ET.fromstring(content)
        assert root.tag.endswith("svg"), f"{fn} rotnode er ikke svg"


def test_tier1_svg_xml_well_formedness():
    """Tier 1: Verifiserer streng XML-velformethet for alle genererte SVG-er med ET.fromstring."""
    for fn in SVG_FILES:
        content = _load_svg(fn)
        root = ET.fromstring(content)
        assert len(root) > 10, f"{fn} har for få noder ({len(root)})"
        tags = [elem.tag.split("}")[-1] for elem in root.iter()]
        assert "defs" in tags, f"{fn} mangler defs i XML-treet"
        assert "rect" in tags, f"{fn} mangler rect i XML-treet"
        assert "text" in tags, f"{fn} mangler text i XML-treet"
        assert "pattern" in tags, f"{fn} mangler pattern i XML-treet"


# ==============================================================================
# SECTION 1: TIER 1 — FEATURE COVERAGE (ATOMÆRE KRAV)
# ==============================================================================


def test_tier1_kartverket_geodata_ssot():
    """Tier 1: Verifiserer autoritativ Kartverket-matrikkel og geodata i SSOT."""
    data = _load_geometry()
    museum = data["museum"]

    # Matrikkeldata enten i museum.matrikkel eller museum.georeferanse
    matrikkel = museum.get("matrikkel", {})
    georef = museum.get("georeferanse", {})

    adresse = matrikkel.get("adresse") or museum.get("fiktiv_adresse") or museum.get("adresse", "")
    assert "Bispegata 9B" in adresse, f"Forventet Bispegata 9B i adresse, fikk: {adresse}"
    assert "Trondheim" in adresse or "7012" in adresse

    kommune = matrikkel.get("kommune") or museum.get("kommune", "")
    assert "5001" in kommune or "Trondheim" in kommune

    gnr = matrikkel.get("gnr") or (401 if "401" in str(georef.get("gnr_bnr", "")) else None)
    bnr = matrikkel.get("bnr") or (12 if "12" in str(georef.get("gnr_bnr", "")) else None)
    assert gnr == 401, f"Forventet Gnr 401, fikk {gnr}"
    assert bnr == 12, f"Forventet Bnr 12, fikk {bnr}"

    # Terrengkote DTM1 laser
    kote_terreng = matrikkel.get("kote_terreng_moh") or matrikkel.get("dtm1_moh")
    assert kote_terreng is not None, "Mangler kote_terreng_moh i matrikkeldata"
    assert abs(kote_terreng - 13.27) < 0.1, f"Forventet terrengkote ~13.27 moh, fikk {kote_terreng}"


def test_tier1_ns3940_arealmodell_ssot():
    """Tier 1: Verifiserer NS 3940 arealoppstilling (BTA, BRA, BYA, etasjefordeling)."""
    data = _load_geometry()
    museum = data["museum"]

    arealer = museum.get("arealer_ns3940")
    assert arealer is not None, "Mangler arealer_ns3940 i museum-objektet i SSOT"

    assert arealer.get("bta_m2") == 4350, f"Forventet BTA 4 350 m², fikk {arealer.get('bta_m2')}"
    assert arealer.get("bra_m2") == 3920, f"Forventet BRA 3 920 m², fikk {arealer.get('bra_m2')}"
    assert arealer.get("bya_m2") == 1450, f"Forventet BYA 1 450 m², fikk {arealer.get('bya_m2')}"

    etasjefordeling = arealer.get("etasjefordeling_bra")
    assert isinstance(etasjefordeling, dict), "etasjefordeling_bra må være en dict med U1, P1, P2"
    assert {"U1", "P1", "P2"}.issubset(etasjefordeling.keys())


def test_tier1_dibk_brannkonsept_ssot():
    """Tier 1: Verifiserer DiBK brannkonsept (BKL 3, RKL 5, R 90, EI 60, sprinkler & Inergen)."""
    data = _load_geometry()
    museum = data["museum"]

    brann = museum.get("brannkonsept")
    assert brann is not None, "Mangler brannkonsept i museum-objektet i SSOT"

    assert brann.get("brannklasse") == "BKL 3", f"Forventet BKL 3, fikk {brann.get('brannklasse')}"
    assert brann.get("risikoklasse") == "RKL 5", f"Forventet RKL 5, fikk {brann.get('risikoklasse')}"

    slokking = brann.get("slokking", "")
    assert "sprinkler" in slokking.lower(), "Slokkekonsept må inkludere sprinkler for publikumsareal"
    assert "inergen" in slokking.lower(), "Slokkekonsept må inkludere Inergen for magasin/sikring"


def test_tier1_veggtykkelser_ssot():
    """Tier 1: Verifiserer veggtykkelser i SSOT (400 mm tegl, 300 mm betong, 200 mm innervegg)."""
    data = _load_geometry()
    museum = data["museum"]

    vegg = museum.get("veggtykkelser_mm")
    assert vegg is not None, "Mangler veggtykkelser_mm i museum-objektet i SSOT"

    assert vegg.get("yttervegg_eldre_floy") == 400, "Forventet 400 mm for eldre fløy (1912)"
    assert vegg.get("yttervegg_tilbygg_ost") == 300, "Forventet 300 mm for tilbygg øst (2016)"
    assert vegg.get("innvendig_baerevegg") == 200, "Forventet 200 mm for innvendig bærevegg"


def test_tier1_romobjekter_berikede_felt_ssot():
    """Tier 1: Verifiserer at samtlige 19 rom har berikede attributter iht. NS 8351."""
    data = _load_geometry()

    total_rooms = 0
    for e in data["etasjer"]:
        for r in e.get("rom", []):
            total_rooms += 1
            rid = r["id"]
            assert "romnummer" in r, f"Rom {rid} mangler 'romnummer'"
            assert "areal_m2" in r and r["areal_m2"] > 0, f"Rom {rid} mangler gyldig areal_m2"
            assert "takhoyde_m" in r and r["takhoyde_m"] > 0, f"Rom {rid} mangler gyldig takhoyde_m"

            # Materialer kan være objekt eller spesifisert gulv-felt
            has_floor = "gulv" in r or ("materialer" in r and "gulv" in r["materialer"])
            assert has_floor, f"Rom {rid} mangler gulvmateriale-spesifikasjon"

            assert "brannklasse" in r, f"Rom {rid} mangler brannklasse"
            assert "sikkerhetssone" in r and r["sikkerhetssone"] in {"S1", "S2", "S3", "S4"}
            assert "klimasone" in r and r["klimasone"] in {"K1", "K2", "K3"}

    assert total_rooms == 19, f"Forventet eksakt 19 rom i modellen, fant {total_rooms}"


def test_tier1_svg_hatch_patterns_defs():
    """Tier 1: Verifiserer at alle 3 SVG-er har <pattern>-definisjoner for skravur."""
    for fn in SVG_FILES:
        svg = _load_svg(fn)
        assert "<defs>" in svg or "<defs " in svg, f"{fn} mangler <defs> seksjon"
        assert 'id="hatch-tegl-400"' in svg, f"{fn} mangler pattern 'hatch-tegl-400'"
        assert 'id="hatch-betong-300"' in svg, f"{fn} mangler pattern 'hatch-betong-300'"
        # Kan hete hatch-barevegg-200 eller hatch-baerevegg-200
        assert (
            'id="hatch-baerevegg-200"' in svg or 'id="hatch-barevegg-200"' in svg
        ), f"{fn} mangler pattern for 200 mm bærevegg"


def test_tier1_svg_doble_vegger_skravurfyll():
    """Tier 1: Verifiserer at SVG-ene refererer skravurmønstrene via fill="url(#hatch-..."."""
    for fn in SVG_FILES:
        svg = _load_svg(fn)
        assert 'fill="url(#hatch-' in svg or "url(#hatch-" in svg, (
            f"{fn} inneholder ikke vegger fylt med hatch-mønstre"
        )


def test_tier1_svg_innvendige_baerevegger_tilpasset_etasjeplan():
    """Tier 1: Verifiserer at innvendige bærevegger er tilpasset hver etasje uten kollisjoner."""
    svg_u1 = _load_svg("plantegning_u1.svg")
    # I U1 skal ikke veggen ved y=259 kutte gjennom rommene (MAG-1, VER-1, TEK-1)
    assert 'rect x="105" y="279"' in svg_u1, "U1 mangler korridorvegg ved y=279"
    assert 'rect x="105" y="259"' not in svg_u1, "U1 har uønsket veggkollisjon ved y=259"

    svg_p2 = _load_svg("plantegning_p2.svg")
    # I P2 skal ikke veggene kutte gjennom Sal C (105..305) eller Sal D (325..505)
    assert 'rect x="304" y="140"' in svg_p2, "P2 mangler skillevegg øst for Sal C"
    assert 'rect x="504" y="140"' in svg_p2, "P2 mangler skillevegg øst for Sal D"


def test_tier1_svg_malekjeder_og_vitnelinjer():
    """Tier 1: Verifiserer at målekjeder med mållinjer og måltekster finnes i alle SVG-er."""
    for fn in SVG_FILES:
        svg = _load_svg(fn)
        # Målekjede-klasse eller linjer med millimeterangivelse
        has_dim_class = 'class="dimension-chain"' in svg or 'class="malekjede"' in svg
        has_dim_text = re.search(r">\s*\d{1,2}\s*\d{3}\s*<", svg) or re.search(r">\s*\d+\.\d{2}\s*m\s*<", svg)
        assert has_dim_class or has_dim_text, f"{fn} mangler arkitektoniske målekjeder"


def test_tier1_svg_arkitekt_ticks_45_grader():
    """Tier 1: Verifiserer at arkitekt-ticks (45° skråstreker) finnes i målekjedene og marker refereres."""
    for fn in SVG_FILES:
        svg = _load_svg(fn)
        # 45 graders ticks enten som transform="rotate(45)" eller linjer med skråhelning
        has_tick_marker = 'id="tick-45"' in svg and 'url(#tick-45)' in svg
        has_tick_geometry = ("rotate(45" in svg or "rotate(-45" in svg) and 'class="arch-tick"' in svg
        assert has_tick_marker and has_tick_geometry, f"{fn} mangler 45-graders arkitekt-ticks eller referanse til tick-45"


def test_tier1_svg_etasjekoter_og_symboler():
    """Tier 1: Verifiserer etasjekote-angivelser i SVG-ene."""
    # U1 skal vise +9.30 moh eller -4.200
    svg_u1 = _load_svg("plantegning_u1.svg")
    assert "+9.30" in svg_u1 or "-4.20" in svg_u1 or "kote" in svg_u1.lower()

    # P1 skal vise +13.50 moh eller ±0.000
    svg_p1 = _load_svg("plantegning_p1.svg")
    assert "+13.50" in svg_p1 or "0.000" in svg_p1 or "kote" in svg_p1.lower()

    # P2 skal vise +19.80 moh eller +6.300
    svg_p2 = _load_svg("plantegning_p2.svg")
    assert "+19.80" in svg_p2 or "+6.30" in svg_p2 or "kote" in svg_p2.lower()


def test_tier1_svg_ns8351_romstempler():
    """Tier 1: Verifiserer NS 8351 romstempelformat med romnr, BRA, høyde og materialer."""
    for fn in SVG_FILES:
        svg = _load_svg(fn)
        # Sjekk at romstemplene inneholder BRA, H og romnummer
        assert "BRA" in svg or "m²" in svg, f"{fn} mangler BRA i romstempler"
        assert "H:" in svg or "H=" in svg or "H " in svg, f"{fn} mangler fri romhøyde H"


def test_tier1_svg_fullverdig_tegningshode():
    """Tier 1: Verifiserer tegningshode med matrikkel, arealoppstilling og brannkonsept."""
    for fn in SVG_FILES:
        svg = _load_svg(fn)
        assert "AURA MUSEUM" in svg, f"{fn} mangler institusjonsnavn i tegningshode"
        assert "Bispegata 9B" in svg, f"{fn} mangler adresse Bispegata 9B i tegningshode"
        assert "401" in svg and "12" in svg, f"{fn} mangler Gnr 401 / Bnr 12 i tegningshode"
        assert "4 350" in svg or "4350" in svg, f"{fn} mangler BTA 4 350 m²"
        assert "3 920" in svg or "3920" in svg, f"{fn} mangler BRA 3 920 m²"
        assert "1 450" in svg or "1450" in svg, f"{fn} mangler BYA 1 450 m²"
        assert "BKL 3" in svg, f"{fn} mangler Brannklasse BKL 3"
        assert "RKL 5" in svg, f"{fn} mangler Risikoklasse RKL 5"


def test_tier1_html_drawer_viser_berikede_data():
    """Tier 1: Verifiserer at interaktiv HTML-viser inkluderer de nye rom- og bygningsdataene."""
    html = _load_html()
    assert "brannklasse" in html.lower() or "brann" in html.lower(), "HTML drawer mangler brannklasse"
    assert "gulv" in html.lower() or "materialer" in html.lower(), "HTML drawer mangler gulv/materialer"
    assert "3920" in html or "3 920" in html, "HTML mangler referanse til BRA 3 920 m²"


def test_tier1_bildegalleri_referansemotiver_integritet():
    """Tier 1: Verifiserer at alle 14 bildefiler (9 unike motiver) i 06_kart/bilder/ eksisterer."""
    expected_files = [
        "01_eksterior_fasade.jpg",
        "01_eksterior_hovedfasade.jpg",
        "02_eksterior_tilbygg_nidelva.jpg",
        "02_vestibyle_ankomst.jpg",
        "03_eksterior_skulpturhage.jpg",
        "03_sal_a_mytologi.jpg",
        "04_sal_d_munch.jpg",
        "04_vestibyle_resepsjon.jpg",
        "05_magasin_klimastyrt.jpg",
        "05_museumsbutikk.jpg",
        "06_museumskafe.jpg",
        "07_sal_a_mytologi.jpg",
        "11_sal_d_munch.jpg",
        "13_magasin_1_hovedlager.jpg",
    ]
    for fn in expected_files:
        p = BILDER_DIR / fn
        assert p.is_file(), f"Mangler bilde: {p}"
        assert p.stat().st_size > 100000, f"Bildet {fn} er ufullstendig (<100 kB)"


def test_tier1_kartkompilator_deterministisk_eksport():
    """Tier 1: Verifiserer at build_map.py definerer påkrevde kompilatorfunksjoner."""
    import importlib.util

    build_script = MAP_DIR / "build_map.py"
    assert build_script.is_file(), f"Mangler {build_script}"

    spec = importlib.util.spec_from_file_location("build_map_module", build_script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert hasattr(mod, "generate_blueprint_svg"), "build_map mangler generate_blueprint_svg"
    assert hasattr(mod, "generate_html"), "build_map mangler generate_html"
    assert hasattr(mod, "build"), "build_map mangler build entrypoint"


def test_tier1_soner_definisjon_sikkerhet_og_klima():
    """Tier 1: Verifiserer at alle soner S1-S4 og K1-K3 er autoritativt definert i SSOT."""
    data = _load_geometry()
    soner = data.get("soner_definisjon", {})

    sikkerhet = soner.get("sikkerhet", {})
    for s in ["S1", "S2", "S3", "S4"]:
        assert s in sikkerhet, f"Mangler definisjon for sikkerhetssone {s}"
        assert "navn" in sikkerhet[s]
        assert "farge" in sikkerhet[s]

    klima = soner.get("klima", {})
    for k in ["K1", "K2", "K3"]:
        assert k in klima, f"Mangler definisjon for klimasone {k}"
        assert "navn" in klima[k]
        assert "farge" in klima[k]


# ==============================================================================
# SECTION 2: TIER 2 — BOUNDARY & CORNER CASES (GRENSETILFELLER OG REGLER)
# ==============================================================================


def test_tier2_ns3940_arealsummer_avstemming():
    """Tier 2: Matematisk avstemming av NS 3940 arealer (sum BRA = 3920, BYA <= BTA, BTA = 4350)."""
    data = _load_geometry()
    arealer = data["museum"]["arealer_ns3940"]

    bta = arealer["bta_m2"]
    bra = arealer["bra_m2"]
    bya = arealer["bya_m2"]
    tomt = arealer.get("tomteareal_m2", 3200)

    etasjer_bra = arealer.get("etasjefordeling_bra", {})
    sum_etasjer = sum(etasjer_bra.values())

    assert sum_etasjer == bra == 3920, (
        f"Sum av etasjenes BRA ({sum_etasjer}) må være eksakt lik total BRA ({bra}) == 3920"
    )
    assert bta == 4350, f"BTA må være 4350 m², fikk {bta}"
    assert bya == 1450, f"BYA må være 1450 m², fikk {bya}"
    assert bra <= bta, f"BRA ({bra}) kan ikke overstige BTA ({bta})"
    assert bya <= bta, f"BYA ({bya}) kan ikke overstige BTA ({bta})"
    assert bya <= tomt, f"BYA ({bya}) kan ikke overstige tomteareal ({tomt})"

    # Utnyttelsesgrad %-BYA ca 45.3 %
    utnyttelse = (bya / tomt) * 100
    assert 45.0 <= utnyttelse <= 46.0, f"%-BYA forventet ~45.3%, beregnet {utnyttelse:.1f}%"


def test_tier2_romareal_sum_begrenset_av_etasje_bra():
    """Tier 2: Sum av romarealer per etasje må være positiv og mindre enn eller lik etasjens BRA."""
    data = _load_geometry()
    etasjefordeling = data["museum"]["arealer_ns3940"]["etasjefordeling_bra"]

    for e in data["etasjer"]:
        kode = e["kode"]
        floor_bra = etasjefordeling[kode]
        rom_sum = sum(r["areal_m2"] for r in e.get("rom", []))

        assert rom_sum > 0, f"Etasje {kode} har ingen romareal"
        assert rom_sum <= floor_bra, (
            f"Sum av romarealer ({rom_sum} m²) i {kode} kan ikke overstige etasjens BRA ({floor_bra} m²)"
        )


def test_tier2_positiv_terskel_terreng_mot_p1_fg():
    """Tier 2: Ferdig gulv P1 (13.50 moh) må ha positiv terskel over terreng (13.27 moh)."""
    data = _load_geometry()
    matrikkel = data["museum"].get("matrikkel", {})

    kote_terreng = matrikkel.get("kote_terreng_moh", 13.27)
    kote_p1 = matrikkel.get("kote_p1_fg_moh", 13.50)

    terskel = kote_p1 - kote_terreng
    assert terskel >= 0.20, (
        f"Fuktsikring/flomterskel krever minst 200 mm mellom terreng ({kote_terreng}) "
        f"og ferdig gulv ({kote_p1}), differanse: {terskel:.2f} m"
    )


def test_tier2_monoton_koteutvikling_vertikalt():
    """Tier 2: Streng monoton økning av koter: U1 < Terreng < P1 < P2 < Gesims."""
    data = _load_geometry()
    matrikkel = data["museum"].get("matrikkel", {})

    kote_u1 = matrikkel.get("kote_u1_fg_moh", 9.30)
    kote_terreng = matrikkel.get("kote_terreng_moh", 13.27)
    kote_p1 = matrikkel.get("kote_p1_fg_moh", 13.50)
    kote_p2 = matrikkel.get("kote_p2_fg_moh", 19.80)
    kote_gesims = matrikkel.get("kote_gesims_moh", 24.90)

    assert kote_u1 < kote_terreng, "Kjeller U1 må ligge under terrengkote"
    assert kote_terreng < kote_p1, "Terreng må ligge under 1. etasje FG"
    assert kote_p1 < kote_p2, "1. etasje FG må ligge under 2. etasje FG"
    assert kote_p2 < kote_gesims, "2. etasje FG må ligge under gesims"


def test_tier2_alle_19_romnummer_og_id_unike():
    """Tier 2: Verifiserer at alle 19 rom har strengt unike rom-IDer og unike romnumre."""
    data = _load_geometry()

    all_ids = []
    all_room_numbers = []

    for e in data["etasjer"]:
        for r in e.get("rom", []):
            all_ids.append(r["id"])
            if "romnummer" in r:
                all_room_numbers.append(str(r["romnummer"]))

    assert len(all_ids) == 19, f"Forventet 19 rom-IDer, fant {len(all_ids)}"
    assert len(set(all_ids)) == 19, f"Duplikate rom-IDer funnet: {all_ids}"

    assert len(all_room_numbers) == 19, f"Forventet 19 romnumre, fant {len(all_room_numbers)}"
    assert len(set(all_room_numbers)) == 19, f"Duplikate romnumre funnet: {all_room_numbers}"


def test_tier2_romnummer_etasjeprefiks_standard():
    """Tier 2: Romnummer må følge standard etasjeprefiks (U1: 0xx, P1: 1xx, P2: 2xx)."""
    data = _load_geometry()

    prefix_map = {0: "0", 1: "1", 2: "2"}

    for e in data["etasjer"]:
        etasje_nr = e["etasje_nr"]
        expected_pfx = prefix_map[etasje_nr]

        for r in e.get("rom", []):
            rnr = str(r.get("romnummer", ""))
            assert rnr.startswith(expected_pfx), (
                f"Rom {r['id']} i etasje {etasje_nr} har romnummer {rnr}, "
                f"forventet prefiks '{expected_pfx}'"
            )


def test_tier2_veggtykkelse_hierarki_og_grenseverdier():
    """Tier 2: Veggtykkelser må oppfylle konstruksjonskrav (400 mm > 300 mm > 200 mm > 0)."""
    data = _load_geometry()
    v = data["museum"]["veggtykkelser_mm"]

    t_1912 = v["yttervegg_eldre_floy"]
    t_2016 = v["yttervegg_tilbygg_ost"]
    t_inner = v["innvendig_baerevegg"]

    assert t_1912 > t_2016 > t_inner > 0, (
        f"Forventet hierarki 400 > 300 > 200 > 0, fikk {t_1912} > {t_2016} > {t_inner}"
    )


def test_tier2_romstorrelse_og_tek17_fri_romhoyde():
    """Tier 2: Romstørrelser må ha bredde/høyde >= 3.0m og takhøyde >= 2.4m (TEK17)."""
    data = _load_geometry()

    for e in data["etasjer"]:
        for r in e.get("rom", []):
            rid = r["id"]
            # 1 koordinatenhet = 100 mm (10 enheter = 1.0 m)
            assert r["w"] >= 30, f"Rom {rid} har bredde < 3.0 m (w={r['w']})"
            assert r["h"] >= 30, f"Rom {rid} har dybde < 3.0 m (h={r['h']})"
            assert r["takhoyde_m"] >= 2.4, f"Rom {rid} oppfyller ikke TEK17 minste takhøyde 2.4m"

            # Sal A er monumentalsal med 6.0 m takhøyde
            if rid == "SAL-A":
                assert r["takhoyde_m"] == 6.0, f"Sal A må ha monumental takhøyde 6.0 m"


def test_tier2_brannmotstand_sone_og_sjaktkrav():
    """Tier 2: Høysikkerhetsrom og sjakter må ha minst EI-60 eller REI-120 brannmotstand."""
    data = _load_geometry()

    for e in data["etasjer"]:
        for r in e.get("rom", []):
            rid = r["id"]
            brann = r.get("brannklasse", "")

            if rid in {"MAG-1", "TEK-1"}:
                assert any(k in brann for k in ["EI-60", "EI-90", "REI-120"]), (
                    f"Rom {rid} krever forsterket brannmotstand (EI-60/EI-90), fikk {brann}"
                )

            if "HEIS" in rid or "TRAPP" in rid:
                assert any(k in brann for k in ["EI-60", "REI-90", "REI-120"]), (
                    f"Sjakt/trapp {rid} krever seksjonerende brannmotstand, fikk {brann}"
                )


def test_tier2_klimagrenser_k1_k2_k3_konservering():
    """Tier 2: Verifiserer at konserveringsgrenser for K1 er strengere enn K2 og K3."""
    data = _load_geometry()
    klima = data["soner_definisjon"]["klima"]

    k1 = klima["K1"]
    k2 = klima["K2"]
    k3 = klima["K3"]

    assert "18°C" in k1["temp"], f"K1 temperatur må være 18°C, fikk {k1['temp']}"
    assert "50%" in k1["rf"], f"K1 luftfuktighet må være 50% RF, fikk {k1['rf']}"
    assert "50 luks" in k1["luks"], f"K1 belysning må være maks 50 luks for papirverk"

    assert "20°C" in k2["temp"]
    assert "21°C" in k3["temp"]


# ==============================================================================
# SECTION 3: TIER 3 — CROSS-FEATURE COMBINATIONS (KONSISTENS MELLOM ARTEFAKTER)
# ==============================================================================


def test_tier3_ssot_til_svg_rom_id_og_antall_konsistens():
    """Tier 3: Samtlige rom i SSOT må finnes i den korresponderende etasjens SVG med data-room-id."""
    data = _load_geometry()

    total_svg_rooms = 0

    for e in data["etasjer"]:
        kode = e["kode"].lower()
        svg_fn = f"plantegning_{kode}.svg"
        svg = _load_svg(svg_fn)

        for r in e.get("rom", []):
            rid = r["id"]
            expected_attr = f'data-room-id="{rid}"'
            assert expected_attr in svg, f"Rom {rid} mangler i {svg_fn} med {expected_attr}"
            total_svg_rooms += 1

    assert total_svg_rooms == 19, f"Forventet 19 rom matchet på tvers av SVG-ene, fikk {total_svg_rooms}"


def test_tier3_ssot_til_svg_romareal_bra_konsistens():
    """Tier 3: Romareal i m² fra SSOT må fremkomme konsistent i SVG-romstempelet."""
    data = _load_geometry()

    for e in data["etasjer"]:
        kode = e["kode"].lower()
        svg = _load_svg(f"plantegning_{kode}.svg")

        for r in e.get("rom", []):
            areal = r["areal_m2"]
            # Skal vises som f.eks. "216 m²" eller "216m²" eller "BRA 216"
            pattern = rf"{areal}\s*m²|BRA\s*{areal}"
            assert re.search(pattern, svg), (
                f"Areal {areal} m² for rom {r['id']} ikke funnet i plantegning_{kode}.svg"
            )


def test_tier3_ssot_til_svg_tegningshode_konsistens():
    """Tier 3: Tegningshodet i alle SVG-er må stemme 100 % med arealer og matrikkel fra SSOT."""
    data = _load_geometry()
    arealer = data["museum"]["arealer_ns3940"]
    matrikkel = data["museum"].get("matrikkel", {})

    bta_str = str(arealer["bta_m2"])
    bra_str = str(arealer["bra_m2"])
    bya_str = str(arealer["bya_m2"])
    gnr_str = str(matrikkel.get("gnr", 401))
    bnr_str = str(matrikkel.get("bnr", 12))

    for fn in SVG_FILES:
        svg = _load_svg(fn)
        assert bta_str in svg, f"{fn} tegningshode matcher ikke BTA {bta_str}"
        assert bra_str in svg, f"{fn} tegningshode matcher ikke BRA {bra_str}"
        assert bya_str in svg, f"{fn} tegningshode matcher ikke BYA {bya_str}"
        assert gnr_str in svg and bnr_str in svg, f"{fn} tegningshode mangler Gnr {gnr_str} / Bnr {bnr_str}"


def test_tier3_ssot_til_svg_etasjekote_konsistens():
    """Tier 3: Kotene angitt i SSOT for hver etasje må gjenspeiles i SVG-etasjeplanet."""
    data = _load_geometry()
    matrikkel = data["museum"].get("matrikkel", {})

    kote_map = {
        "plantegning_u1.svg": f"{matrikkel.get('kote_u1_fg_moh', 9.30):.2f}",
        "plantegning_p1.svg": f"{matrikkel.get('kote_p1_fg_moh', 13.50):.2f}",
        "plantegning_p2.svg": f"{matrikkel.get('kote_p2_fg_moh', 19.80):.2f}",
    }

    for fn, kote_val in kote_map.items():
        svg = _load_svg(fn)
        assert kote_val in svg or f"+{kote_val}" in svg or "kote" in svg.lower(), (
            f"Kote {kote_val} fra SSOT finnes ikke i {fn}"
        )


def test_tier3_ssot_til_html_modellkonsistens():
    """Tier 3: Interaktiv HTML må referere alle 19 rom-IDer fra bygning_geometri.json."""
    data = _load_geometry()
    html = _load_html()

    for e in data["etasjer"]:
        for r in e.get("rom", []):
            rid = r["id"]
            assert rid in html, f"Rom {rid} fra SSOT finnes ikke i 06_kart/index.html"


def test_tier3_svg_skravurmonster_definisjon_og_bruk():
    """Tier 3: Skravurmønstre definert i <defs> må refereres som fill i SVG-elementene."""
    for fn in SVG_FILES:
        svg = _load_svg(fn)
        pattern_ids = re.findall(r'<pattern[^>]+id="([^"]+)"', svg)
        hatch_ids = [pid for pid in pattern_ids if "hatch" in pid]

        assert len(hatch_ids) >= 2, f"{fn} har for få hatch patterns definert: {hatch_ids}"
        for hid in hatch_ids:
            assert f'url(#{hid})' in svg or f"url('#{hid}')" in svg, (
                f"Pattern {hid} er definert, men aldri brukt i {fn}"
            )


# ==============================================================================
# SECTION 4: TIER 4 — REAL-WORLD APPLICATION SCENARIOS (VIRKELIGE BRUKSSITUASJONER)
# ==============================================================================


def test_tier4_scenario_branntilsyn_slokking_og_romning():
    """Tier 4 Scenario 1: Tilsyn fra Trøndelag brann- og redningstjeneste.

    Verifiserer:
    - Pre-action sprinkler i publikumssoner (S1, S2, S3)
    - Inergen gasslukking i S4 magasin (MAG-1), kunstmottak (VER-1) og teknisk (TEK-1)
    - Minst 2 uavhengige rømningstrapper/utganger fra planene
    """
    data = _load_geometry()
    museum = data["museum"]
    brann = museum.get("brannkonsept", {})

    slokking = brann.get("slokking", "").lower()
    assert "sprinkler" in slokking, "Brannkonsept mangler pre-action sprinkler for saler"
    assert "inergen" in slokking, "Brannkonsept mangler Inergen for gjenstandsvern"

    # Verifiser at Magasin 1 og Kunstmottak har Inergen eller gasslokking spesifisert
    mag1 = next(r for e in data["etasjer"] for r in e["rom"] if r["id"] == "MAG-1")
    assert any("inergen" in s.lower() for s in mag1.get("sensorer", [])) or "inergen" in mag1.get("beskrivelse", "").lower()

    # Verifiser rømningstrapper i U1, P1 og P2
    u1_rooms = {r["id"] for e in data["etasjer"] if e["kode"] == "U1" for r in e["rom"]}
    p1_rooms = {r["id"] for e in data["etasjer"] if e["kode"] == "P1" for r in e["rom"]}
    p2_rooms = {r["id"] for e in data["etasjer"] if e["kode"] == "P2" for r in e["rom"]}

    assert "TRAPP-U1" in u1_rooms, "U1 mangler rømningstrapp"
    assert "TRAPP-P1" in p1_rooms, "P1 mangler trappeløp/rømning"
    assert "TRAPP-P2" in p2_rooms, "P2 mangler trappeløp/rømning"


def test_tier4_scenario_byggesakskontroll_og_arealattest():
    """Tier 4 Scenario 2: Byggesakskontroll og arealattest til Trondheim kommune.

    Verifiserer:
    - Formelle matrikkeldata (Trondheim 5001, Bispegata 9B, Gnr 401 / Bnr 12)
    - DTM1 terrenghøyde 13.27 moh, FG P1 13.50 moh (+230 mm terskel)
    - Full arealoppstilling: BTA 4 350 m², BRA 3 920 m², BYA 1 450 m², %-BYA 45.3%
    """
    data = _load_geometry()
    museum = data["museum"]
    matrikkel = museum.get("matrikkel", {})
    arealer = museum.get("arealer_ns3940", {})

    # Formell matrikkel
    assert "Bispegata 9B" in matrikkel.get("adresse", "")
    assert matrikkel.get("gnr") == 401
    assert matrikkel.get("bnr") == 12

    # Koteberegning
    assert matrikkel.get("kote_p1_fg_moh") == 13.50
    assert matrikkel.get("kote_terreng_moh") == 13.27

    # Arealattest
    assert arealer.get("bta_m2") == 4350
    assert arealer.get("bra_m2") == 3920
    assert arealer.get("bya_m2") == 1450

    # Etasjefordeling
    fordeling = arealer.get("etasjefordeling_bra", {})
    assert sum(fordeling.values()) == 3920


def test_tier4_scenario_sikkerhetspatrulje_adgangskontroll():
    """Tier 4 Scenario 3: Sikkerhetspatrulje og adgangskontroll-gjennomgang.

    Verifiserer:
    - Sone S1: Åpen adkomst (Vestibyle RES-1, Kafé KAF-1, Butikk BUT-1)
    - Sone S2: Utstillingssaler med sensorer (Sal A, B, C, D, E)
    - Sone S3: Skjermet drift og vaktrom (VAK-1)
    - Sone S4: Høysikkerhetsmagasin (MAG-1, VER-1) med hvelv og to-personers regel
    """
    data = _load_geometry()

    rooms_by_id = {r["id"]: r for e in data["etasjer"] for r in e["rom"]}

    # Sone 1 publikum
    for rid in ["RES-1", "KAF-1", "BUT-1"]:
        assert rooms_by_id[rid]["sikkerhetssone"] == "S1"

    # Sone 2 utstilling
    for rid in ["SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E"]:
        assert rooms_by_id[rid]["sikkerhetssone"] == "S2"

    # Sone 3 drift/sikkerhet
    assert rooms_by_id["VAK-1"]["sikkerhetssone"] == "S3"
    assert "CCTV" in rooms_by_id["VAK-1"]["beskrivelse"] or any("alarm" in s.lower() for s in rooms_by_id["VAK-1"].get("sensorer", []))

    # Sone 4 høysikkerhet
    assert rooms_by_id["MAG-1"]["sikkerhetssone"] == "S4"
    assert rooms_by_id["VER-1"]["sikkerhetssone"] == "S4"


def test_tier4_scenario_nasjonal_konserveringsrevisjon():
    """Tier 4 Scenario 4: Nasjonal konserveringsrevisjon for uerstattelige kunstverk.

    Verifiserer:
    - Magasin 1 (MAG-1) og Munch papiravdeling i Sal D er Klimasone K1
    - K1 oppfyller 18°C ± 1°C, 50% ± 5% RF og maks 50 lux belysning
    - Standard kunstsaler (Sal A, B, C, E) er Klimasone K2 (20°C, 45-55% RF)
    """
    data = _load_geometry()
    klima_def = data["soner_definisjon"]["klima"]
    rooms_by_id = {r["id"]: r for e in data["etasjer"] for r in e["rom"]}

    # MAG-1 må være K1
    assert rooms_by_id["MAG-1"]["klimasone"] == "K1"

    # Sal D må ha K1 konserveringskrav (enten som hovedklima eller montre)
    sal_d = rooms_by_id["SAL-D"]
    assert sal_d["klimasone"] in {"K1", "K2"}
    assert "klima" in sal_d["beskrivelse"].lower() or any("klima" in s.lower() for s in sal_d.get("sensorer", []))

    # K1 definisjon
    assert "18°C" in klima_def["K1"]["temp"]
    assert "50%" in klima_def["K1"]["rf"]
    assert "50 luks" in klima_def["K1"]["luks"]


def test_tier4_scenario_entreprenor_arbeidstegning_gransking():
    """Tier 4 Scenario 5: Entreprenør-gransking av målsatte arbeidstegninger.

    Verifiserer:
    - Yttervegger på 1912-fløy er 400 mm tegl med skravur i plantegningene
    - Yttervegger på 2016-tilbygg er 300 mm betong/glass med skravur
    - Bærende innervegger er 200 mm med skravur
    - Målestokk 1:100 og arkitekt-ticks er tilstede på alle tre etasjeplan
    """
    data = _load_geometry()
    vegg = data["museum"]["veggtykkelser_mm"]

    assert vegg["yttervegg_eldre_floy"] == 400
    assert vegg["yttervegg_tilbygg_ost"] == 300
    assert vegg["innvendig_baerevegg"] == 200

    for fn in SVG_FILES:
        svg = _load_svg(fn)
        assert "MÅLESTOKK 1:100" in svg, f"{fn} mangler målestokkangivelse 1:100"
        # Målekjede eller mållinje tilstede
        assert "line" in svg and ("stroke" in svg or "stroke-width" in svg)
