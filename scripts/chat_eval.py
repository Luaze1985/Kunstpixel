"""Kjør eval-settet for KI-chatten mot en ekte modell og skriv rapport.

Bruk (PowerShell, med KI-innstillingene satt som for Datafinner):
    $env:LLM_PROVIDER="anthropic"; $env:LLM_MODEL="claude-sonnet-5-5"; $env:LLM_API_KEY="<nøkkel>"; $env:LLM_MAX_TOKENS="1500"
    py -3.13 scripts/chat_eval.py --dry-run                 # vis oppgaver og maks antall KI-kall, uten nettverk
    py -3.13 scripts/chat_eval.py --k 3 --maks-kall 300     # full kjøring
    py -3.13 scripts/chat_eval.py --oppgaver B1,U1 --k 1    # bare noen oppgaver
    py -3.13 scripts/chat_eval.py --sammenlign .scratch/chat_eval/kjoring-<tid>.jsonl

Resultater: .scratch/chat_eval/kjoring-<tid>.jsonl (hele transkriptet per forsøk) og .md (rapport).
Hver KI-runde teller mot --maks-kall. Når taket nås, stopper kjøringen og rapporten sier hva som mangler.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.adapters import datafinner, datafinner_api
from src.kunstpixel.core import chat_eval, llm

UTMAPPE = PROJECT_ROOT / ".scratch" / "chat_eval"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Eval av KI-chatten i Datafinner")
    p.add_argument("--k", type=int, default=3, help="forsøk per oppgave (standard 3)")
    p.add_argument("--oppgaver", default="", help="kommaseparerte id-er, f.eks. B1,U1 (standard: alle)")
    p.add_argument("--maks-kall", type=int, default=300, help="tak på KI-kall for hele kjøringen (standard 300)")
    p.add_argument("--dry-run", action="store_true", help="vis plan uten å kalle KI")
    p.add_argument("--sammenlign", default="", help="eldre kjoring-*.jsonl å sammenligne med")
    p.add_argument("--utmappe", default=str(UTMAPPE))
    a = p.parse_args(argv)

    data = chat_eval.last()
    valgte = {x.strip() for x in a.oppgaver.split(",") if x.strip()}
    oppgaver = [o for o in data["oppgaver"] if not valgte or o["id"] in valgte]
    if valgte - {o["id"] for o in oppgaver}:
        print(f"Ukjente oppgaver: {', '.join(sorted(valgte - {o['id'] for o in oppgaver}))}", file=sys.stderr)
        return 2

    turer = sum(len(o["turer"]) for o in oppgaver)
    print(f"{len(oppgaver)} oppgaver, {turer} turer, {a.k} forsøk hver. "
          f"Høyst {turer * a.k * llm.CHAT_MAKS_RUNDER} KI-kall ({llm.CHAT_MAKS_RUNDER} runder per tur), tak {a.maks_kall}.")
    if a.dry_run:
        for o in oppgaver:
            print(f"  {o['id']:<3} {o['kategori']:<11} {o['turer'][0][:90]}")
        return 0

    from src.kunstpixel.core import miljo
    miljo.last_env_fil()
    konfig = llm.fra_miljo(os.environ)
    if konfig is None:
        print("KI er av. Sett LLM_PROVIDER, LLM_MODEL og LLM_API_KEY i .env i prosjektroten (se .env.eksempel).", file=sys.stderr)
        return 2
    print(f"KI: {konfig.leverandor} {konfig.modell}")

    begrenser = llm.Begrenser(a.maks_kall, vindu=10**9)  # tak for hele kjøringen, ikke per time
    verktoy = datafinner_api.verktoyskjema(datafinner.VERKTOY)
    poster, stoppet = [], ""
    for o in oppgaver:
        for i in range(1, a.k + 1):
            post = chat_eval.kjor_forsok(o, i, konfig=konfig, verktoy=verktoy, kjor=datafinner.run_tool,
                                         system_mal=datafinner.SYSTEM_CHAT, dato_i_dag=data["dato_i_dag"], begrenser=begrenser)
            poster.append(post)
            merke = "-" if post["bestatt"] is None else ("OK" if post["bestatt"] else "FEIL")
            print(f"{o['id']} forsøk {i}: {merke} ({post['antall_kall']} verktøykall, {post['sekunder']} s)")
            if post["tak_nadd"]:
                stoppet = f"Taket på {a.maks_kall} KI-kall ble nådd i {o['id']} forsøk {i}. Resten er ikke kjørt."
                break
        if stoppet:
            break

    tid = datetime.now().strftime("%Y%m%d-%H%M%S")
    ut = Path(a.utmappe)
    jsonl = ut / f"kjoring-{tid}.jsonl"
    chat_eval.skriv_jsonl(poster, jsonl)
    forrige = chat_eval.les_jsonl(Path(a.sammenlign)) if a.sammenlign else None
    meta = {"tidspunkt": tid, "modell": konfig.modell, "leverandor": konfig.leverandor, "k": a.k,
            "dato_i_dag": data["dato_i_dag"], "stoppet": stoppet}
    md = ut / f"kjoring-{tid}.md"
    md.write_text(chat_eval.rapport_md(poster, meta, jsonl.name, forrige), encoding="utf-8")
    t = chat_eval.oppsummer(poster)["total"]
    print(f"\npass^k {t['pass_hat_k']}/{t['oppgaver']}, pass@k {t['pass_at_k']}/{t['oppgaver']}. Rapport: {md}")
    if stoppet:
        print(stoppet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
