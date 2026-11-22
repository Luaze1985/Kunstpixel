"""Konsistens mellom byggdata (06_kart/bygning_geometri.json), kunnskapsfila og håndbøkene.

Funnet 2026-11-22: kunnskapsfila beskrev et 1980-bygg med andre arealer, kafeen lå på feil side
av planen (vest, mens Nidelva og glassfløyen er i øst), og kafeen hadde 60 plasser i kartet,
men 45 i HMS-håndboka og kvalitetssystemet.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEOMETRI = json.loads((ROOT / "06_kart" / "bygning_geometri.json").read_text(encoding="utf-8"))
KUNNSKAP = (ROOT / "04_knowledge" / "04_domain" / "core" / "bygning_og_etasjeplaner.md").read_text(encoding="utf-8")
HMS = (ROOT / "04_knowledge" / "01_governance" / "handboker" / "02_hms_sikkerhetshandbok.md").read_text(encoding="utf-8")
ROM = {r["id"]: r for e in GEOMETRI["etasjer"] for r in e["rom"]}


def test_kafeen_ligger_mot_nidelva_i_ost() -> None:
    # Nidelva og 2016-fløyen ligger i øst (høyre side av planen).
    assert ROM["KAF-1"]["x"] > ROM["RES-1"]["x"], "Kafeen skal ligge øst for vestibylen, mot Nidelva"
    assert ROM["BUT-1"]["x"] < ROM["RES-1"]["x"], "Bokhandelen skal ligge vest for vestibylen"


def test_kafeens_sitteplasser_stemmer_med_hms_handboka() -> None:
    hms = int(re.search(r"Museumskafé:\*\*\s*(\d+) sitteplasser", HMS).group(1))
    kart = int(re.search(r"(\d+) sitteplasser", ROM["KAF-1"]["beskrivelse"]).group(1))
    assert kart == hms


def test_kunnskapsfila_beskriver_samme_bygg_som_kartet() -> None:
    assert "1980" not in KUNNSKAP
    assert "1912" in KUNNSKAP and "2016" in KUNNSKAP
    for rid in ["SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E", "KAF-1", "BUT-1", "RES-1", "MAG-1", "VER-1", "TEK-1", "VAK-1", "PAU-1"]:
        areal = ROM[rid]["areal_m2"]
        assert f"{areal} m²" in KUNNSKAP, f"{rid} ({areal} m²) mangler eller har annet areal i kunnskapsfila"


def test_kunnskapsfila_har_samme_arealtall_som_kartet() -> None:
    a = GEOMETRI["museum"]["arealer_ns3940"]
    for tall in (a["bta_m2"], a["bya_m2"]):
        assert f"{tall:,}".replace(",", " ") in KUNNSKAP
    # BRA har desimal (4 174,2) og skrives på norsk.
    assert f"{a['bra_m2']:,.1f}".replace(",", " ").replace(".", ",") in KUNNSKAP
