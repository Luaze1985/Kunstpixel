"""Arenaen: øvelsescaser som viser hva dataene kan brukes til, hvor GDPR-grensen går og hva KI vinner.

Casene ligger i 04_knowledge/07_arena/caser.yaml. Modulen laster dem og kjører hver case
deterministisk (KI av). Hvert svar sjekkes mot casens «forventet», og datamerket regnes ut live:
  - verktoy:    hvitelistede Datafinner-verktøy (samme sperrer som siden)
  - intern:     den interne assistenten, med rolle
  - datapolicy: bare datamerket for tabellene i casen
  - lesecase:   ingen kjøring

Datamerket kommer fra kolonnen datakilde i museum.db (mode=ro). Mangler merket, regnes tabellen som
ekte (fail-closed, se core/datapolicy.py). Ingenting skrives.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from src.kunstpixel.core import datapolicy, db

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CASEFIL = PROJECT_ROOT / "04_knowledge" / "07_arena" / "caser.yaml"
TYPER = {"verktoy", "intern", "datapolicy", "lesecase"}

# Ekte, offentlige tall uten persondata. Datapolicyen regner dem likevel som ekte.
OFFENTLIGE = {"ssb_sykefraver_kultur", "norske_helligdager", "leverandor_enhetsregister", "arbeidstilsynet_renhold"}


@lru_cache(maxsize=1)
def last_caser() -> dict[str, Any]:
    return yaml.safe_load(CASEFIL.read_text(encoding="utf-8"))


def _case(case_id: str) -> dict[str, Any]:
    for c in last_caser()["caser"]:
        if c["id"] == case_id:
            return c
    raise ValueError(f"Ukjent case: {case_id}")


def datamerke(tabeller: list[str]) -> list[dict[str, Any]]:
    """Merket per tabell: syntetisk, umerket (behandles som ekte), offentlig eller ekte."""
    merker = []
    with db.get_db_connection() as con:
        finnes = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        for t in tabeller:
            if t not in finnes:
                raise ValueError(f"Ukjent tabell: {t}")
            kolonner = {r[1] for r in con.execute(f'PRAGMA table_info("{t}")')}
            verdier = (
                [r[0] for r in con.execute(f'SELECT DISTINCT datakilde FROM "{t}"')] if "datakilde" in kolonner else []
            )
            if t in OFFENTLIGE:
                merke, klass = "offentlig", datapolicy.EKTE
            elif not verdier:
                merke, klass = "umerket", None
            elif all(datapolicy.normalize_classification(v) == datapolicy.SYNTETISK for v in verdier):
                merke, klass = "syntetisk", verdier[0]
            else:
                merke, klass = "ekte", datapolicy.EKTE
            merker.append({"tabell": t, "merke": merke, "klassifisering": klass})
    return merker


def _policy(entries: list[dict[str, Any]]) -> dict[str, Any]:
    if not entries:
        return {"ekstern_ki": None, "grunn": None}
    grunn = datapolicy.check_policy(datapolicy.EXTERNAL, entries)
    return {"ekstern_ki": grunn is None, "grunn": grunn}


def _mangler(tekst: str, forventet: list[str]) -> list[str]:
    return [f for f in forventet if f.lower() not in tekst.lower()]


@lru_cache(maxsize=1)
def _intern_agent() -> Any:
    from src.kunstpixel.core.intern.agent import InternAgent

    return InternAgent(llm=None)


def _standard_verktoy(navn: str, args: dict[str, Any]) -> Any:
    from src.kunstpixel.adapters.datafinner import run_tool

    return run_tool(navn, args)


def kjor(case_id: str, kjor_verktoy: Callable[[str, dict[str, Any]], Any] | None = None) -> dict[str, Any]:
    """Kjør én case og sjekk svaret. `kjor_verktoy` er Datafinners run_tool (hviteliste og argumentkontroll)."""
    case = _case(case_id)
    kjoring = case["kjoring"]
    kjor_verktoy = kjor_verktoy or _standard_verktoy
    steg: list[dict[str, Any]] = []
    intern_klass: list[dict[str, Any]] = []
    intern_merker: list[dict[str, Any]] = []  # kildefilene til den interne assistenten

    if kjoring["type"] == "verktoy":
        for s in kjoring["steg"]:
            svar = kjor_verktoy(s["verktoy"], dict(s.get("args") or {}))
            mangler = _mangler(json.dumps(svar, ensure_ascii=False, default=str), s.get("forventet", []))
            steg.append({"verktoy": s["verktoy"], "args": s.get("args") or {}, "svar": svar, "ok": not mangler, "mangler": mangler})
    elif kjoring["type"] == "intern":
        for s in kjoring["steg"]:
            resp = _intern_agent().handle_message(s["sporsmal"], s["rolle"])
            mangler = _mangler(resp.text, s.get("forventet", []))
            if resp.klassifisering:
                intern_klass.append({"klassifisering": resp.klassifisering})
                merke = "syntetisk" if datapolicy.normalize_classification(resp.klassifisering) == datapolicy.SYNTETISK else "ekte"
                for fil in sorted({k.split(" › ")[0] for k in resp.kilder}):
                    if fil not in {m["tabell"] for m in intern_merker}:
                        intern_merker.append({"tabell": fil, "merke": merke, "klassifisering": resp.klassifisering})
            steg.append({
                "sporsmal": s["sporsmal"],
                "rolle": s["rolle"],
                "svar": resp.text,
                "kategori": resp.category,
                "verktoy_brukt": resp.tools_used,
                "kilder": resp.kilder,
                "ok": not mangler and resp.category == s["kategori"],
                "mangler": mangler + ([f"kategori {s['kategori']}"] if resp.category != s["kategori"] else []),
            })

    merker = datamerke(case.get("datagrunnlag") or [])
    return {
        "id": case_id,
        "ok": all(s["ok"] for s in steg),
        "steg": steg,
        "datamerke": merker + intern_merker,
        "policy": _policy(merker + intern_klass),
    }
