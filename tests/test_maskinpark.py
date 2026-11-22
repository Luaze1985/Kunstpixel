"""Maskinparken: data, oppslag og regelsjekk for KI-forslag (skill: .claude/skills/maskinpark/SKILL.md).

KI-en utfører aldri. propose_machine_command gir bare et forslag som et menneske må godkjenne (SEC-M1).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from src.kunstpixel.core import maskinpark as mp

ROOT = Path(__file__).resolve().parents[1]
KART = ROOT / "06_kart"
JSON_STI = KART / "maskinpark.json"
GEOMETRI = json.loads((KART / "bygning_geometri.json").read_text(encoding="utf-8"))
ROM = {r["id"]: r for e in GEOMETRI["etasjer"] for r in e["rom"]}


def _builder():
    spec = importlib.util.spec_from_file_location("kp_maskinpark_builder", KART / "maskinpark_builder.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


DATA = json.loads(JSON_STI.read_text(encoding="utf-8"))
MASKINER = {m["maskin_id"]: m for m in DATA["maskiner"]}


# --- Data ------------------------------------------------------------------------------------

def test_byggeren_er_deterministisk_og_fila_er_oppdatert(tmp_path: Path) -> None:
    b = _builder()
    a, c = tmp_path / "a.json", tmp_path / "c.json"
    b.skriv(a)
    b.skriv(c)
    assert _sha(a) == _sha(c)
    assert _sha(a) == _sha(JSON_STI), "maskinpark.json er ikke laget på nytt etter endring i byggeren"


def test_alle_data_er_syntetiske() -> None:
    assert DATA["datakilde"].startswith("syntetisk")
    assert DATA["i_dag"] == "2026-11-22"


def test_maskinparken_dekker_alle_kategorier() -> None:
    kategorier = {m["kategori"] for m in DATA["maskiner"]}
    assert kategorier == {"server", "robot", "anlegg", "sikkerhet", "heis"}
    typer = {m["type"] for m in DATA["maskiner"]}
    for t in ("gpu_node", "renholdsrobot", "vaktrobot", "transportrobot", "klimastyring", "lysstyring", "inergen"):
        assert t in typer, t


def test_alle_rom_finnes_i_bygget() -> None:
    for m in DATA["maskiner"]:
        assert m["rom_id"] in ROM, (m["maskin_id"], m["rom_id"])
        assert m["hjem_rom_id"] in ROM, (m["maskin_id"], m["hjem_rom_id"])
    roboter = [m for m in DATA["maskiner"] if m["kategori"] == "robot"]
    assert all(m["hjem_rom_id"] == "ROB-1" for m in roboter)
    assert all(m["rom_id"] == "SRV-1" for m in DATA["maskiner"] if m["kategori"] == "server")


def test_id_er_unike_og_referanser_peker_pa_maskiner() -> None:
    assert len(MASKINER) == len(DATA["maskiner"])
    for liste, felt in (("hendelser", "hendelse_id"), ("vedlikehold", "arbeidsordre_id"), ("kommandologg", "kommando_id")):
        ider = [x[felt] for x in DATA[liste]]
        assert len(ider) == len(set(ider)), liste
        assert all(x["maskin_id"] in MASKINER for x in DATA[liste]), liste


def test_ingen_maskin_lar_ki_utfore() -> None:
    assert {m["ki_tilgang"] for m in DATA["maskiner"]} <= {"les", "foresla"}
    assert all(m["ki_tilgang"] == "les" for m in DATA["maskiner"] if m["kategori"] == "sikkerhet")


def test_status_folger_apne_hendelser() -> None:
    for m in DATA["maskiner"]:
        apne = {h["alvorlighet"] for h in DATA["hendelser"] if h["maskin_id"] == m["maskin_id"] and not h["lukket"]}
        if apne & {"feil", "kritisk"}:
            assert m["status"] in ("feil", "vedlikehold"), m["maskin_id"]
        elif "varsel" in apne:
            assert m["status"] in ("varsel", "vedlikehold"), m["maskin_id"]


def test_ingen_datoer_etter_i_dag() -> None:
    assert all(h["tidspunkt"][:10] <= "2026-11-22" for h in DATA["hendelser"])
    assert all((v["utfort"] or "0") <= "2026-11-22" for v in DATA["vedlikehold"])
    assert all(m["sist_service"] <= "2026-11-22" for m in DATA["maskiner"])


# --- Oppslag ---------------------------------------------------------------------------------

def test_hent_maskinpark_summerer_riktig() -> None:
    alt = mp.hent_maskinpark()
    assert alt["antall"] == len(DATA["maskiner"])
    assert sum(alt["per_status"].values()) == alt["antall"]
    roboter = mp.hent_maskinpark(kategori="robot")
    assert roboter["antall"] > 0 and all(m["kategori"] == "robot" for m in roboter["maskiner"])
    u1 = mp.hent_maskinpark(etasje=0)
    assert all(ROM[m["rom_id"]]["romnummer"].startswith("0") for m in u1["maskiner"])


def test_maskinhelse_viser_apne_hendelser_og_service() -> None:
    h = mp.maskinhelse("KP-MASK-ANL-04")
    assert h["maskin"]["rom_id"] == "MAG-1"
    assert any(x["kode"] == "RF_AVVIK" for x in h["apne_hendelser"])
    assert h["neste_service"] > h["maskin"]["sist_service"]
    with pytest.raises(ValueError):
        mp.maskinhelse("KP-MASK-FINNES-IKKE")


def test_vedlikeholdsplan_skiller_forfalt_og_kommende() -> None:
    plan = mp.vedlikeholdsplan(dager=30)
    assert plan["forfalt"], "byggeren skal lage minst én forfalt service"
    assert all(x["neste_service"] < "2026-11-22" for x in plan["forfalt"])
    assert all("2026-11-22" <= x["neste_service"] <= "2026-12-22" for x in plan["kommende"])
    assert [x["neste_service"] for x in plan["kommende"]] == sorted(x["neste_service"] for x in plan["kommende"])


# --- Regelsjekk for forslag (SEC-M1..M5) -----------------------------------------------------

@pytest.mark.parametrize("kommando", ["deaktiver_slukking", "las_opp_dor", "sla_av_kamera", "sla_av_alarm",
                                      "deaktiver_adgang", "overstyr_heis"])
def test_forbudte_kommandoer_avvises_alltid(kommando: str) -> None:
    for mid in ("KP-MASK-SIK-01", "KP-MASK-SIK-05", "KP-MASK-HEI-02"):
        svar = mp.foresla_kommando(mid, kommando, rolle="museumsdirektor")
        assert svar["tillatt"] is False and svar["status"] == "avvist"
        assert any("forbudt" in g for g in svar["grunner"])


def test_klimasettpunkt_ma_ligge_i_sonen() -> None:
    ut = mp.foresla_kommando("KP-MASK-ANL-04", "sett_klima", {"temperatur_c": 22, "rf_prosent": 50})
    assert ut["tillatt"] is False and any("K1" in g for g in ut["grunner"])
    inn = mp.foresla_kommando("KP-MASK-ANL-04", "sett_klima", {"temperatur_c": 18.5, "rf_prosent": 52})
    assert inn["tillatt"] is True and inn["status"] == "venter_godkjenning"
    assert inn["forslag"]["maskin_id"] == "KP-MASK-ANL-04"


def test_lysniva_folger_sonen() -> None:
    assert mp.foresla_kommando("KP-MASK-ANL-10", "sett_lysniva", {"luks": 120})["tillatt"] is False  # Sal D, K1
    assert mp.foresla_kommando("KP-MASK-ANL-07", "sett_lysniva", {"luks": 180})["tillatt"] is True  # Sal A, K2


def test_kunsttransport_bare_utenom_apningstid_og_to_personer_i_S4() -> None:
    dag = mp.foresla_kommando("KP-MASK-TRA-01", "flytt_verk", {"fra_rom": "MAG-1", "til_rom": "SAL-A"},
                              tidspunkt="2026-11-23T14:00")
    assert dag["tillatt"] is False and any("åpningstid" in g for g in dag["grunner"])
    natt = mp.foresla_kommando("KP-MASK-TRA-01", "flytt_verk", {"fra_rom": "MAG-1", "til_rom": "SAL-A"},
                               tidspunkt="2026-11-23T22:00")
    assert natt["tillatt"] is True
    assert any("to personer" in k for k in natt["krav"])
    assert any("vareheis" in k for k in natt["krav"])  # U1 -> P1


def test_renholdsrobot_kjorer_ikke_inn_i_S4() -> None:
    svar = mp.foresla_kommando("KP-MASK-REN-01", "send_til_rom", {"rom_id": "MAG-1"})
    assert svar["tillatt"] is False and any("S4" in g for g in svar["grunner"])
    assert mp.foresla_kommando("KP-MASK-REN-01", "send_til_rom", {"rom_id": "SAL-B"})["tillatt"] is True


def test_sikkerhetsutstyr_tillater_bare_selvtest() -> None:
    assert mp.foresla_kommando("KP-MASK-SIK-01", "kjor_selvtest")["tillatt"] is True
    assert mp.foresla_kommando("KP-MASK-SIK-01", "start_slukking")["tillatt"] is False


def test_ukjent_kommando_og_ukjent_rom_avvises() -> None:
    assert mp.foresla_kommando("KP-MASK-REN-01", "dans")["tillatt"] is False
    assert mp.foresla_kommando("KP-MASK-REN-01", "send_til_rom", {"rom_id": "TULL"})["tillatt"] is False


def test_forslag_endrer_ingenting() -> None:
    for_ = _sha(JSON_STI)
    mp.foresla_kommando("KP-MASK-ANL-04", "sett_klima", {"temperatur_c": 18.5, "rf_prosent": 52})
    mp.foresla_kommando("KP-MASK-SIK-01", "deaktiver_slukking")
    assert _sha(JSON_STI) == for_


def test_mcp_verktoyene_er_registrert() -> None:
    from src.kunstpixel.core.mcp_server import mcp
    navn = {t.name for t in mcp._tool_manager.list_tools()}
    assert {"get_machine_park", "get_machine_health", "get_maintenance_plan", "propose_machine_command"} <= navn
