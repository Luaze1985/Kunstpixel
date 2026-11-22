"""Bygget som geometri: fotavtrykk, arealregning og regler for romoppsettet.

Spec: docs/specs/2026-11-22-bygg-tegninger-design.md · Plan: docs/plans/2026-11-22-bygg-tegninger.md
BTA og BYA står fast (1 450 per etasje). BRA regnes fra tegningen (Lars, 2026-11-22).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
KART = ROOT / "06_kart"


def _last_geometri():
    spec = importlib.util.spec_from_file_location("kp_geometri", KART / "geometri.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


geo = _last_geometri()
MODELL = json.loads((KART / "bygning_geometri.json").read_text(encoding="utf-8"))
ROM = {r["id"]: r for e in MODELL["etasjer"] for r in e["rom"]}


def test_modellen_har_ingen_feil() -> None:
    assert geo.feil(MODELL) == []


def test_bta_og_bya_er_1450() -> None:
    a = MODELL["museum"]["arealer_ns3940"]
    assert geo.bta_etasje(MODELL) == pytest.approx(1450)
    assert a["bta_m2"] == 4350
    assert a["bya_m2"] == 1450


def test_bra_regnes_fra_tegningen() -> None:
    a = MODELL["museum"]["arealer_ns3940"]
    assert geo.bra_etasje(MODELL) == pytest.approx(1391.4, abs=0.01)
    assert a["etasjefordeling_bra"] == {"U1": 1391.4, "P1": 1391.4, "P2": 1391.4}
    assert a["bra_m2"] == pytest.approx(4174.2, abs=0.01)
    for e in MODELL["etasjer"]:
        assert e["bra_etasje_m2"] == pytest.approx(1391.4, abs=0.01)
        assert e["bta_etasje_m2"] == 1450


def test_innvendig_stemmer_med_veggtykkelse() -> None:
    hoved, glass = MODELL["museum"]["fotavtrykk"]["volumer"]
    t_h, t_g = hoved["vegg_mm"] // 100, glass["vegg_mm"] // 100
    assert hoved["innvendig"] == {"x": hoved["x"] + t_h, "y": hoved["y"] + t_h,
                                  "b": hoved["b"] - 2 * t_h, "d": hoved["d"] - 2 * t_h}
    # Glassfløyen har ingen egen vestvegg; den gamle fasadeveggen står mellom fløyene.
    assert glass["innvendig"] == {"x": glass["x"], "y": glass["y"] + t_g,
                                  "b": glass["b"] - t_g, "d": glass["d"] - 2 * t_g}
    fasade = MODELL["museum"]["fotavtrykk"]["fasadevegg"]
    assert fasade == {"x": glass["x"] - t_h, "y": hoved["y"] + t_h, "b": t_h, "d": hoved["d"] - 2 * t_h}


def test_de_19_opprinnelige_rommene_finnes() -> None:
    opprinnelige = {"MAG-1", "VER-1", "TEK-1", "HEIS-U1", "TRAPP-U1", "SAL-A", "SAL-B", "SAL-E", "RES-1",
                    "BUT-1", "KAF-1", "HEIS-P1", "TRAPP-P1", "SAL-C", "SAL-D", "VAK-1", "PAU-1", "HEIS-P2", "TRAPP-P2"}
    assert opprinnelige <= set(ROM)


def test_salene_har_samme_areal() -> None:
    assert {k: ROM[k]["areal_m2"] for k in ("SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E")} == {
        "SAL-A": 216, "SAL-B": 156, "SAL-C": 240, "SAL-D": 216, "SAL-E": 156}


def test_hver_etasje_har_to_trapper() -> None:
    for e in MODELL["etasjer"]:
        trapper = [r for r in e["rom"] if r["type"] == "trapp"]
        assert len(trapper) >= 2, e["kode"]


def test_maskinrom_i_U1() -> None:
    """Reservearealet (177 m²) er delt i KI-serverrom og robotgarasje (maskinpark, 2026-11-22)."""
    u1 = {r["id"]: r for r in next(e for e in MODELL["etasjer"] if e["kode"] == "U1")["rom"]}
    assert u1["SRV-1"]["type"] == u1["ROB-1"]["type"] == "maskin"
    assert u1["SRV-1"]["areal_m2"] + u1["ROB-1"]["areal_m2"] == 177
    assert "MASK-RES-1" not in u1
    for rid in ("SRV-1", "ROB-1"):
        assert geo.dor_mot(u1[rid], list(u1.values())) == "GANG-U1G", rid


def test_ingen_beskrivelse_nevner_gamle_mal() -> None:
    tekst = json.dumps(MODELL, ensure_ascii=False)
    for gammelt in ("48 m", "24 m ", "1980"):
        assert gammelt not in tekst, gammelt


def test_feil_fanger_overlapp_og_feil_areal() -> None:
    """Regelsjekken skal faktisk slå til, ikke bare være tom."""
    kopi = json.loads(json.dumps(MODELL))
    p1 = next(e for e in kopi["etasjer"] if e["kode"] == "P1")
    p1["rom"][1]["x"] -= 10   # Sal B inn i Sal A
    p1["rom"][2]["areal_m2"] += 1
    feil = geo.feil(kopi)
    assert any("overlapp" in f for f in feil)
    assert any("areal" in f for f in feil)


# --- Oppgave 2: plantegningene tegnes fra fotavtrykket -------------------------------------

SVG = {k: (KART / f"plantegning_{k}.svg").read_text(encoding="utf-8") for k in ("u1", "p1", "p2")}


def test_tier3_svg_vegger_fra_fotavtrykk() -> None:
    for kode, svg in SVG.items():
        assert 'class="yttervegg" data-volum="HOVEDFLOY"' in svg and "url(#hatch-tegl-400)" in svg, kode
        assert 'class="yttervegg" data-volum="GLASSFLOY"' in svg and "url(#hatch-betong-300)" in svg, kode
        assert 'class="fasadevegg"' in svg, kode
        assert 'class="baerevegg"' in svg and "url(#hatch-baerevegg-200)" in svg, kode


def test_svg_malkjeder_viser_fotavtrykk() -> None:
    for kode, svg in SVG.items():
        for mal in ("58 000 mm", "25 000 mm", "34 000 mm", "24 000 mm"):
            assert mal in svg, f"{kode} mangler {mal}"


def test_svg_tegningshode_fra_data() -> None:
    for kode, svg in SVG.items():
        assert "BTA: 4 350 m²" in svg and "BRA: 4 174,2 m²" in svg and "BYA: 1 450 m²" in svg, kode


def test_ingen_faste_byggmal_i_build_map() -> None:
    kilde = (KART / "build_map.py").read_text(encoding="utf-8")
    for fast in ("48 000", "24 000 mm</text>", 'x="105" y="279"', "3 920", "4 350 m²"):
        assert fast not in kilde, fast


def test_smale_rom_far_kortnavn() -> None:
    import re
    for e in MODELL["etasjer"]:
        svg = SVG[e["kode"].lower()]
        for r in e["rom"]:
            if min(r["w"], r["h"]) < 40:
                blokk = re.search(rf'data-room-id="{re.escape(r["id"])}".*?</g>', svg, re.S).group(0)
                titler = re.findall(r'font-weight="bold"[^>]*>([^<]+)<', blokk)
                assert titler == [r["romnummer"]], f"{r['id']}: {titler}"


def test_romtitler_far_plass_i_rommet() -> None:
    """Romnavn skal ikke flyte utover rommet (anslag: 0,68 × skriftstørrelse per tegn)."""
    import re
    for e in MODELL["etasjer"]:
        svg = SVG[e["kode"].lower()]
        for r in e["rom"]:
            blokk = re.search(rf'data-room-id="{re.escape(r["id"])}".*?</g>', svg, re.S).group(0)
            m = re.search(r'font-size="([\d.]+)" font-weight="bold"[^>]*>([^<]+)<', blokk)
            fs, tittel = float(m.group(1)), html_unescape(m.group(2))
            plass = max(r["w"], r["h"]) if min(r["w"], r["h"]) < 40 else r["w"]
            assert len(tittel) * fs * 0.68 <= plass - 4, f"{r['id']}: «{tittel}» er for bred"


def html_unescape(t: str) -> str:
    import html
    return html.unescape(t)


# --- Oppgave 3: 2.5D-kartet tegnes fra fotavtrykket -----------------------------------------

def test_html_bruker_fotavtrykk() -> None:
    kilde = (KART / "build_map.py").read_text(encoding="utf-8")
    assert "MODEL.museum.fotavtrykk" in kilde
    for fast in ("toIso(540, 20", "toIso(370, 20", "toIso(240, 180", "let cx = x - 280", "toIso(580, -20"):
        assert fast not in kilde, fast
    html_ut = (KART / "index.html").read_text(encoding="utf-8")
    assert "4 174,2" in html_ut


# --- Rettinger etter gjennomgangen 2026-11-22 ------------------------------------------------

def _endre(endring):
    kopi = json.loads(json.dumps(MODELL))
    endring(kopi)
    return geo.feil(kopi)


def test_feil_fanger_rom_utenfor_flyene() -> None:
    assert any("utenfor" in f for f in _endre(lambda m: m["etasjer"][0]["rom"][0].update(x=20)))


def test_feil_fanger_hull_i_etasjen() -> None:
    def fjern(m):
        r = m["etasjer"][0]["rom"].pop()
    assert any("fyller ikke" in f for f in _endre(fjern))


def test_feil_fanger_sjakt_som_ikke_star_over_hverandre() -> None:
    def flytt(m):
        for e in m["etasjer"]:
            for r in e["rom"]:
                if r["id"] == "VHEIS-P2":
                    r["sjakt"] = "vareheis"; r["x"] += 1
    assert any("sjakt" in f for f in _endre(flytt))


def test_feil_fanger_for_fa_trapper() -> None:
    def fjern_trapp(m):
        for r in m["etasjer"][1]["rom"]:
            if r["id"] == "TRAPP2-P1":
                r["type"] = "drift"
    assert any("trapper" in f for f in _endre(fjern_trapp))


def test_dorer_gar_ikke_inn_i_heis_eller_ut_i_yttervegg() -> None:
    assert geo.dorfeil(MODELL) == []


def test_dorfeil_fanger_dor_inn_i_heis() -> None:
    def feil_dor(m):
        for r in m["etasjer"][1]["rom"]:
            if r["id"] == "LAG-P1":
                r["dor_pos"] = "nord"
    assert any("LAG-P1" in f for f in geo.dorfeil(json.loads(json.dumps(MODELL)) if False else _kopi(feil_dor)))


def _kopi(endring):
    kopi = json.loads(json.dumps(MODELL))
    endring(kopi)
    return kopi


def test_romningstrapp_2_leder_til_nodutgang_i_p1() -> None:
    """Rømningstrapp 2 har ingen yttervegg; den leder via gangen til nødutgangen i øst."""
    p1 = {r["id"]: r for r in next(e for e in MODELL["etasjer"] if e["kode"] == "P1")["rom"]}
    assert geo.dor_mot(p1["TRAPP2-P1"], list(p1.values())) == "GANG-P1G"
    glass_inn = MODELL["museum"]["fotavtrykk"]["volumer"][1]["innvendig"]
    gang = p1["GANG-P1G"]
    assert gang["x"] + gang["w"] == glass_inn["x"] + glass_inn["b"], "gangen må nå østveggen"
    assert "nødutgang" in gang["beskrivelse"].lower() and "nødutgang" in p1["TRAPP2-P1"]["beskrivelse"].lower()


def test_pdf_tar_med_hele_plantegningen() -> None:
    import re
    kilde = (ROOT / "02_deliverables" / "bygningsdokumentasjon" / "lag_pdf.py").read_text(encoding="utf-8")
    b, h = map(int, re.search(r"--window-size=(\d+),(\d+)", kilde).groups())
    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', SVG["p1"]).groups()
    assert abs(h / b - int(vb[1]) / int(vb[0])) < 0.01, "vindu og viewBox har ulikt forhold, så tegningen kuttes"


def test_2_5d_bruker_romnummer_i_smale_rom() -> None:
    kilde = (KART / "build_map.py").read_text(encoding="utf-8")
    assert "Math.min(room.w, room.h) < 40" in kilde


def test_skallet_folger_rotasjonen() -> None:
    kilde = (KART / "build_map.py").read_text(encoding="utf-8")
    a = kilde.index("function drawExteriorShell"); b = kilde.index("function updateLegendUI")
    assert "dybde(" in kilde[a:b], "skallet må velge synlige flater etter rotasjon"
