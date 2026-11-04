"""Eval av KI-chatten i Datafinner: last oppgaver, kjør dem mot en modell, vurder svarene med kode, lag rapport.

Oppgavene ligger i 04_knowledge/07_arena/chat_eval.yaml (formatet står øverst i filen).
Vurderingen er bare kodebasert: tekster som må eller ikke må stå i svaret, verktøy som må være brukt,
argumenter, tak på antall kall og tallkontrollen fra llm.tallkontroll. Ingen KI-dommer ennå.

Kjøres fra scripts/chat_eval.py. Fasiten vokses uten KI av tests/test_chat_eval_fasit.py.
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from src.kunstpixel.core import llm

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVALFIL = PROJECT_ROOT / "04_knowledge" / "07_arena" / "chat_eval.yaml"
GRENSEFIL = PROJECT_ROOT / "04_knowledge" / "07_arena" / "grensecaser.yaml"
KATEGORIER = ("fakta", "utregning", "bemanning", "kant", "samtale", "observasjon")
STANDARD_MAKS_KALL = 6


# ---------- lasting ----------

def last(sti: Path = EVALFIL) -> dict[str, Any]:
    """Les eval-settet og fyll inn turer for observasjonsoppgaver fra grensecasene."""
    data = yaml.safe_load(sti.read_text(encoding="utf-8"))
    grense = {c["id"]: c for c in yaml.safe_load(GRENSEFIL.read_text(encoding="utf-8"))["caser"]}
    for o in data["oppgaver"]:
        if "fra_grense" in o:
            o["turer"] = [grense[o["fra_grense"]]["foresporsel"].strip()]
        o.setdefault("rolle", data.get("standard_rolle", "ukjent rolle"))
        o.setdefault("fasit", [])
        o.setdefault("forventet", [])
        o.setdefault("utregnet", [])
        o.setdefault("forbudt", [])
        o.setdefault("verktoy_krav", [])
        o.setdefault("args_krav", [])
        o.setdefault("maks_kall", STANDARD_MAKS_KALL)
        o.setdefault("tallkontroll", "ignorer")
    return data


# ---------- tekstsjekk ----------

def normaliser(tekst: str) -> str:
    """Små bokstaver, vanlig minus, tall uten mellomrom og med desimalpunktum («2 279,36» blir «2279.36»)."""
    t = str(tekst).lower().replace("−", "-").replace("–", "-")
    forrige = None
    while forrige != t:  # «1 057 720» trenger flere runder
        forrige = t
        t = re.sub(r"(?<=\d)[   ](?=\d{3}(?!\d))", "", t)
    return re.sub(r"(?<=\d),(?=\d)", ".", t)


def finnes(punkt: str | list[str], tekst: str) -> bool:
    """Et punkt er en tekst eller en liste med alternativer. Ett alternativ holder."""
    alternativer = punkt if isinstance(punkt, list) else [punkt]
    norm = normaliser(tekst)
    return any(normaliser(a) in norm for a in alternativer)


def _visning(punkt: str | list[str]) -> str:
    return " / ".join(punkt) if isinstance(punkt, list) else punkt


def regn_ut(uttrykk: str) -> float:
    """Regn et enkelt uttrykk med tall og + - * / ( ). Alt annet avvises."""
    if not re.fullmatch(r"[\d.\s+\-*/()]+", uttrykk):
        raise ValueError(f"Ugyldig uttrykk: {uttrykk}")
    return float(eval(uttrykk, {"__builtins__": {}}, {}))


# ---------- vurdering ----------

def vurder(oppgave: dict[str, Any], svar: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Kodesjekkene for ett forsøk. `svar` er chat-svarene for hver tur. Tekstsjekkene gjelder siste svar,
    verktøysjekkene gjelder alle kall i samtalen."""
    siste = svar[-1]
    tekst = siste.get("tekst", "")
    kall = [k for s in svar for k in s.get("verktoykall", [])]
    brukt = {k["navn"] for k in kall}
    sjekker: list[dict[str, Any]] = []

    def legg(navn: str, ok: bool, detalj: str = "") -> None:
        sjekker.append({"sjekk": navn, "ok": ok, "detalj": detalj})

    for p in oppgave["forventet"]:
        legg(f"forventet: {_visning(p)}", finnes(p, tekst))
    for u in oppgave["utregnet"]:
        legg(f"utregnet: {u['uttrykk']} = {u['verdi']}", finnes(str(u["verdi"]), tekst))
    for f in oppgave["forbudt"]:
        legg(f"forbudt: {f}", not finnes(f, tekst))
    if oppgave["verktoy_krav"]:
        ok = any(set(sett) <= brukt for sett in oppgave["verktoy_krav"])
        legg("verktøy brukt", ok, "brukt: " + (", ".join(sorted(brukt)) or "ingen"))
    for a in oppgave["args_krav"]:
        ok = any(k["navn"] == a["verktoy"] and isinstance(k.get("args"), dict)
                 and all(str(k["args"].get(n)) == str(v) for n, v in a["args"].items()) for k in kall)
        legg(f"argumenter: {a['verktoy']} {json.dumps(a['args'], ensure_ascii=False)}", ok)
    legg(f"høyst {oppgave['maks_kall']} verktøykall", len(kall) <= oppgave["maks_kall"], f"{len(kall)} kall")
    if oppgave["tallkontroll"] == "ok":
        tk = siste.get("tallkontroll", {})
        legg("tallkontroll ok", bool(tk.get("ok")), json.dumps(tk, ensure_ascii=False))
    legg("ikke avbrutt", not siste.get("avbrutt") and not siste.get("feil"), siste.get("avbrutt") or siste.get("feil") or "")
    return sjekker


# ---------- kjøring ----------

UKEDAGER = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]


def systemprompt(mal: str, dato_i_dag: str, rolle: str) -> str:
    d = date.fromisoformat(dato_i_dag)
    return mal.format(dato=d.isoformat(), ukedag=UKEDAGER[d.weekday()], rolle=rolle)


def kjor_forsok(
    oppgave: dict[str, Any], forsok: int, *, konfig: llm.LlmKonfig, verktoy: list[dict[str, Any]],
    kjor: Callable[[str, dict[str, Any]], Any], system_mal: str, dato_i_dag: str,
    begrenser: llm.Begrenser | None = None, apne: Any = None,
) -> dict[str, Any]:
    """Kjør alle turene i én oppgave én gang og vurder resultatet."""
    system = systemprompt(system_mal, dato_i_dag, oppgave["rolle"])
    historikk: list[dict[str, str]] = []
    svar: list[dict[str, Any]] = []
    start = time.monotonic()
    for tur in oppgave["turer"]:
        historikk.append({"rolle": "bruker", "tekst": tur})
        try:
            ekstra = {"apne": apne} if apne is not None else {}
            s = llm.chat_med_verktoy(historikk, verktoy, kjor, konfig, system, begrenser=begrenser, **ekstra)
        except llm.LlmFeil as exc:
            s = {"tekst": "", "verktoykall": [], "feil": f"{exc.kode}: {exc}", "feilkode": exc.kode}
            svar.append(s)
            break
        svar.append(s)
        historikk.append({"rolle": "assistent", "tekst": s["tekst"]})
        if s.get("avbrutt"):
            break
    sek = round(time.monotonic() - start, 2)
    vurdert = oppgave["kategori"] != "observasjon"
    sjekker = vurder(oppgave, svar) if vurdert else []
    return {
        "id": oppgave["id"], "kategori": oppgave["kategori"], "forsok": forsok, "rolle": oppgave["rolle"],
        "turer": oppgave["turer"], "svar": svar, "sjekker": sjekker,
        "bestatt": all(s["ok"] for s in sjekker) if vurdert else None,
        "sekunder": sek, "antall_kall": sum(len(s.get("verktoykall", [])) for s in svar),
        "tak_nadd": any(s.get("avbrutt") == "tak" or s.get("feilkode") == "tak" for s in svar),
    }


# ---------- oppsummering og rapport ----------

def oppsummer(poster: list[dict[str, Any]]) -> dict[str, Any]:
    """Per oppgave: forsøk, bestått, pass-rate, pass@k (minst ett) og pass^k (alle). Totalt og per kategori."""
    per: dict[str, dict[str, Any]] = {}
    for p in poster:
        o = per.setdefault(p["id"], {"id": p["id"], "kategori": p["kategori"], "forsok": 0, "bestatt": 0, "vurdert": p["bestatt"] is not None})
        o["forsok"] += 1
        o["bestatt"] += 1 if p["bestatt"] else 0
    for o in per.values():
        if o["vurdert"]:
            o["pass_rate"] = round(o["bestatt"] / o["forsok"], 3)
            o["pass_at_k"] = o["bestatt"] > 0
            o["pass_hat_k"] = o["bestatt"] == o["forsok"]
    vurderte = [o for o in per.values() if o["vurdert"]]
    kategorier: dict[str, dict[str, Any]] = {}
    for o in vurderte:
        k = kategorier.setdefault(o["kategori"], {"oppgaver": 0, "pass_at_k": 0, "pass_hat_k": 0})
        k["oppgaver"] += 1
        k["pass_at_k"] += int(o["pass_at_k"])
        k["pass_hat_k"] += int(o["pass_hat_k"])
    return {
        "oppgaver": per,
        "kategorier": kategorier,
        "total": {
            "oppgaver": len(vurderte),
            "pass_at_k": sum(o["pass_at_k"] for o in vurderte),
            "pass_hat_k": sum(o["pass_hat_k"] for o in vurderte),
            "forsok": sum(o["forsok"] for o in vurderte),
            "bestatt_forsok": sum(o["bestatt"] for o in vurderte),
        },
    }


def skriv_jsonl(poster: list[dict[str, Any]], sti: Path) -> None:
    sti.parent.mkdir(parents=True, exist_ok=True)
    with sti.open("w", encoding="utf-8") as f:
        for p in poster:
            f.write(json.dumps(p, ensure_ascii=False, default=str) + "\n")


def les_jsonl(sti: Path) -> list[dict[str, Any]]:
    return [json.loads(linje) for linje in sti.read_text(encoding="utf-8").splitlines() if linje.strip()]


def rapport_md(poster: list[dict[str, Any]], meta: dict[str, Any], jsonl_navn: str,
               forrige: list[dict[str, Any]] | None = None) -> str:
    """Lesbar rapport: totalt, per kategori, per oppgave, og hva som feilet i hvert forsøk."""
    s = oppsummer(poster)
    t = s["total"]
    ut = [
        f"# Chat-eval {meta.get('tidspunkt', '')}",
        "",
        f"Modell: {meta.get('modell')} ({meta.get('leverandor')}). Forsøk per oppgave: {meta.get('k')}. "
        f"Fast «i dag»: {meta.get('dato_i_dag')}. Transkripter: `{jsonl_navn}`.",
        "",
        f"**Totalt:** {t['pass_hat_k']} av {t['oppgaver']} oppgaver besto alle forsøk (pass^k). "
        f"{t['pass_at_k']} besto minst ett (pass@k). {t['bestatt_forsok']} av {t['forsok']} forsøk besto.",
        "",
    ]
    if meta.get("stoppet"):
        ut += [f"**Stoppet:** {meta['stoppet']}", ""]
    ut += ["| Kategori | Oppgaver | pass@k | pass^k |", "|---|---|---|---|"]
    for navn, k in s["kategorier"].items():
        ut.append(f"| {navn} | {k['oppgaver']} | {k['pass_at_k']} | {k['pass_hat_k']} |")
    ut += ["", "| Oppgave | Kategori | Bestått | pass@k | pass^k |", "|---|---|---|---|---|"]
    for o in s["oppgaver"].values():
        if o["vurdert"]:
            ut.append(f"| {o['id']} | {o['kategori']} | {o['bestatt']}/{o['forsok']} | {'ja' if o['pass_at_k'] else 'nei'} | {'ja' if o['pass_hat_k'] else 'nei'} |")
        else:
            ut.append(f"| {o['id']} | {o['kategori']} | ikke vurdert | | |")
    if forrige is not None:
        gammel = oppsummer(forrige)["oppgaver"]
        endret = []
        for oid, o in s["oppgaver"].items():
            g = gammel.get(oid)
            if o["vurdert"] and g and g.get("vurdert") and g["pass_rate"] != o["pass_rate"]:
                retning = "bedre" if o["pass_rate"] > g["pass_rate"] else "dårligere"
                endret.append(f"- {oid}: {g['pass_rate']:.2f} → {o['pass_rate']:.2f} ({retning})")
        ut += ["", "## Endring fra forrige kjøring", ""] + (endret or ["Ingen endring i pass-rate."])
    ut += ["", "## Feilede forsøk", ""]
    feilet = [p for p in poster if p["bestatt"] is False]
    if not feilet:
        ut.append("Ingen.")
    for p in feilet:
        ut.append(f"### {p['id']} forsøk {p['forsok']}")
        ut.append("")
        for sj in p["sjekker"]:
            if not sj["ok"]:
                ut.append(f"- Feilet: {sj['sjekk']}" + (f" ({sj['detalj']})" if sj["detalj"] else ""))
        siste = (p["svar"] or [{}])[-1]
        ut += ["", "> " + (siste.get("tekst") or siste.get("feil") or "(tomt svar)").replace("\n", "\n> "), ""]
    ut += ["", "## Observasjoner (ingen poeng)", ""]
    for p in poster:
        if p["bestatt"] is None:
            siste = (p["svar"] or [{}])[-1]
            ut += [f"### {p['id']} forsøk {p['forsok']}", "", "> " + (siste.get("tekst") or siste.get("feil") or "(tomt svar)").replace("\n", "\n> "), ""]
    return "\n".join(ut) + "\n"
