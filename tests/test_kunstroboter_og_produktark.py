"""Kunstroboter (hengerobot og selvkjørende kunstkasse) og produktark for maskinparken.

Produktarkene lages av 06_kart/produktark_builder.py fra maskinpark.json, så de kan ikke bli utdaterte.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from src.kunstpixel.core import maskinpark as mp

ROOT = Path(__file__).resolve().parents[1]
KART = ROOT / "06_kart"
ARK = ROOT / "04_knowledge" / "04_domain" / "operations" / "maskinpark"
DATA = json.loads((KART / "maskinpark.json").read_text(encoding="utf-8"))
TYPER = sorted({m["type"] for m in DATA["maskiner"]})


def _modul(navn: str):
    spec = importlib.util.spec_from_file_location(f"kp_{navn}", KART / f"{navn}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- Kunstroboter ---------------------------------------------------------------------------

def test_kunstrobotene_finnes_i_maskinparken() -> None:
    per_type = {}
    for m in DATA["maskiner"]:
        per_type.setdefault(m["type"], []).append(m)
    assert len(per_type["hengerobot"]) >= 1 and len(per_type["kunstkasse"]) >= 2
    for m in per_type["hengerobot"] + per_type["kunstkasse"]:
        assert m["kategori"] == "robot" and m["hjem_rom_id"] == "ROB-1" and m["ki_tilgang"] == "foresla"


def test_hengerobot_tar_ned_verk_etter_stengetid_med_konservator() -> None:
    svar = mp.foresla_kommando("KP-MASK-HNG-01", "ta_ned_verk", {"rom_id": "SAL-B"}, tidspunkt="2026-11-23T21:00")
    assert svar["status"] == "venter_godkjenning", svar["grunner"]
    assert any("konservator" in k for k in svar["krav"])


def test_hengerobot_avvises_i_apningstid() -> None:
    svar = mp.foresla_kommando("KP-MASK-HNG-01", "ta_ned_verk", {"rom_id": "SAL-B"}, tidspunkt="2026-11-23T14:00")
    assert svar["status"] == "avvist"
    assert any("SEC-M4" in g for g in svar["grunner"])


def test_hengerobot_jobber_bare_i_utstillingssaler() -> None:
    svar = mp.foresla_kommando("KP-MASK-HNG-01", "heng_opp_verk", {"rom_id": "MAG-1"}, tidspunkt="2026-11-23T21:00")
    assert svar["status"] == "avvist"
    assert any("sal" in g for g in svar["grunner"])


def test_pakk_verk_krever_en_kunstkasse_som_finnes() -> None:
    ok = mp.foresla_kommando("KP-MASK-HNG-01", "pakk_verk", {"kasse_id": "KP-MASK-KAS-01"}, tidspunkt="2026-11-23T21:10")
    assert ok["status"] == "venter_godkjenning", ok["grunner"]
    feil = mp.foresla_kommando("KP-MASK-HNG-01", "pakk_verk", {"kasse_id": "KP-MASK-KAS-99"}, tidspunkt="2026-11-23T21:10")
    assert feil["status"] == "avvist"


def test_kunstkasse_til_magasin_krever_to_personer_og_vareheis() -> None:
    svar = mp.foresla_kommando("KP-MASK-KAS-01", "kjor_kasse_til_magasin", {"fra_rom": "SAL-B", "til_rom": "MAG-1"},
                               tidspunkt="2026-11-23T21:30")
    assert svar["status"] == "venter_godkjenning", svar["grunner"]
    assert any("to personer" in k for k in svar["krav"])
    assert any("vareheis" in k for k in svar["krav"])


def test_kunstkasse_kjorer_bare_til_magasin() -> None:
    svar = mp.foresla_kommando("KP-MASK-KAS-01", "kjor_kasse_til_magasin", {"fra_rom": "SAL-B", "til_rom": "SAL-A"},
                               tidspunkt="2026-11-23T21:30")
    assert svar["status"] == "avvist"


def test_kunstkasse_avvises_i_apningstid() -> None:
    svar = mp.foresla_kommando("KP-MASK-KAS-01", "kjor_kasse_til_magasin", {"fra_rom": "SAL-B", "til_rom": "MAG-1"},
                               tidspunkt="2026-11-23T12:00")
    assert svar["status"] == "avvist"


# --- Produktark -----------------------------------------------------------------------------

@pytest.mark.parametrize("typ", TYPER)
def test_et_produktark_per_maskintype(typ: str) -> None:
    assert (ARK / f"{typ}.md").is_file(), typ


@pytest.mark.parametrize("typ", TYPER)
def test_arket_viser_enheter_datastrom_og_styring(typ: str) -> None:
    tekst = (ARK / f"{typ}.md").read_text(encoding="utf-8")
    for overskrift in ("## Enheter i Kunstpixel", "## Datastrøm", "## Slik følger du den", "## Slik styrer du den"):
        assert overskrift in tekst, (typ, overskrift)
    maskiner = [m for m in DATA["maskiner"] if m["type"] == typ]
    for m in maskiner:
        assert m["maskin_id"] in tekst, (typ, m["maskin_id"])
        for kommando in m["kommandoer"]:
            assert f"`{kommando}`" in tekst, (typ, kommando)
    for kode, _alv, _tekst in _modul("maskinpark_builder").KODER[typ]:
        assert kode in tekst, (typ, kode)
    assert "get_machine_health" in tekst and "propose_machine_command" in tekst


@pytest.mark.parametrize("typ", TYPER)
def test_eksempelforslaget_i_arket_godtas_av_regelsjekken(typ: str) -> None:
    tekst = (ARK / f"{typ}.md").read_text(encoding="utf-8")
    if "```json\n" not in tekst:  # bare lesbar for KI og ingen selvtest: ingen eksempel
        assert all(m["ki_tilgang"] == "les" for m in DATA["maskiner"] if m["type"] == typ)
        return
    blokk = tekst.split("```json\n", 1)[1].split("\n```", 1)[0]
    kall = json.loads(blokk)
    svar = mp.foresla_kommando(kall["maskin_id"], kall["kommando"], kall["parametre"], tidspunkt=kall.get("tidspunkt"))
    assert svar["status"] == "venter_godkjenning", (typ, svar["grunner"])


def test_oversikten_lenker_til_alle_arkene_og_viser_flyten() -> None:
    tekst = (ARK / "README.md").read_text(encoding="utf-8")
    for typ in TYPER:
        assert f"({typ}.md)" in tekst, typ
    assert "```mermaid" in tekst
    assert "venter_godkjenning" in tekst


def test_produktarkene_er_laget_fra_dagens_data() -> None:
    filer = _modul("produktark_builder").lag_alle()
    assert set(filer) == {p.name for p in ARK.glob("*.md")}
    for navn, innhold in filer.items():
        assert (ARK / navn).read_text(encoding="utf-8") == innhold, f"{navn} er utdatert: kjør produktark_builder.py"
