"""Tar opp svar fra ekte modell for de 40 prøvespørsmålene (H4). KOSTER TOKENS.

    py -3.13 tests/record_intern_cassettes.py --dry-run          # viser plan og kostnadstak, kaller ingenting
    py -3.13 tests/record_intern_cassettes.py                    # ekte kjøring, spør før start
    py -3.13 tests/record_intern_cassettes.py --model claude-haiku-5-5 --budget 80000

Krever ANTHROPIC_API_KEY (eller ant-innlogging). Bare syntetiske data sendes. Ekte data nektes av
datapolicyen før noe forlater maskinen. Kassetten lagres i tests/cassettes/intern/kassett.json og
brukes av tests/test_intern_cassettes.py uten nettverk.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
logging.disable(logging.CRITICAL)

from src.kunstpixel.core.intern.agent import InternAgent  # noqa: E402
from src.kunstpixel.core.intern.fact_check import REFUSAL_TOKEN  # noqa: E402
from src.kunstpixel.core.llm import DEFAULT_MODEL, DEFAULT_TOKEN_BUDGET, AnthropicLLM, FakeLLM, RecordingLLM  # noqa: E402
from tests.intern_questions import DEKKET, UBESVARBARE  # noqa: E402

CASSETTE = ROOT / "tests" / "cassettes" / "intern" / "kassett.json"
SUMMARY = ROOT / "tests" / "cassettes" / "intern" / "oppsummering.json"

# USD per million tokens (inn, ut). Kilde: prisliste i claude-api-ferdigheten 2026-10-06. Sjekk mot gjeldende priser.
PRICES = {
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def questions() -> list[dict]:
    return DEKKET + UBESVARBARE


def plan_calls() -> int:
    """Hvor mange av spørsmålene som faktisk når modellen (de andre stoppes av faste regler)."""
    fake = FakeLLM(responder=lambda req: REFUSAL_TOKEN)
    agent = InternAgent(llm=fake)
    for item in questions():
        agent.handle_message(item["sporsmal"], item["rolle"])
    return len(fake.calls)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help=f"standard {DEFAULT_MODEL}")
    ap.add_argument("--budget", type=int, default=DEFAULT_TOKEN_BUDGET, help="tak på inn- og uttokens totalt")
    ap.add_argument("--dry-run", action="store_true", help="vis plan og kostnadstak, kall ingenting")
    ap.add_argument("--yes", action="store_true", help="ikke spør før start")
    args = ap.parse_args()

    model = args.model or DEFAULT_MODEL
    n_calls = plan_calls()
    price_in, price_out = PRICES.get(model, (None, None))
    print(f"Modell:            {model}")
    print(f"Spørsmål totalt:   {len(questions())}  (av dem når {n_calls} modellen)")
    print(f"Kostnadstak:       {args.budget:,} tokens totalt".replace(",", " "))
    if price_out is not None:
        print(f"Høyeste mulige kost: ca. {args.budget / 1_000_000 * price_out:.2f} USD (hele taket til utpris)")
    else:
        print("Pris for modellen er ukjent i skriptet. Sjekk prisliste før kjøring.")
    print(f"Kassett:           {rel(CASSETTE)}")
    if args.dry_run:
        print("Tørrkjøring: ingenting ble sendt.")
        return 0

    try:
        llm = AnthropicLLM(model=model, token_budget=args.budget)
    except Exception as exc:  # noqa: BLE001
        print(f"Kan ikke starte klienten: {type(exc).__name__}: {exc}")
        return 2
    if not args.yes and input("Dette sender syntetiske spørsmål til Anthropic og koster tokens. Skriv ja for å starte: ").strip().lower() != "ja":
        print("Avbrutt.")
        return 1

    agent = InternAgent(llm=RecordingLLM(CASSETTE, inner=llm))
    rows = []
    for item in questions():
        r = agent.handle_message(item["sporsmal"], item["rolle"])
        # Stopp ved første feil før noe kall har lyktes (typisk manglende legitimasjon). Ellers ville
        # skriptet gått gjennom alle spørsmålene og lagret en oppsummering av bare fallback.
        if llm.calls == 0 and (r.fallback_reason or "").startswith("llm_feil"):
            print(f"Første modellkall feilet ({r.fallback_reason}). Sjekk ANTHROPIC_API_KEY eller ant-innlogging. Ingenting lagret.")
            return 2
        rows.append(
            {
                "sporsmal": item["sporsmal"],
                "dekket": "kilde" in item,
                "llm_used": r.llm_used,
                "funnet": r.funnet,
                "fallback_reason": (r.fallback_reason or "").split(":")[0] or None,
            }
        )
        print(f"{'LLM ' if r.llm_used else 'fall'} {r.category:<12} {item['sporsmal'][:60]}")

    cost = None if price_out is None else llm.tokens_in / 1e6 * price_in + llm.tokens_out / 1e6 * price_out
    summary = {
        "modell": model,
        "kall": llm.calls,
        "tokens_inn": llm.tokens_in,
        "tokens_ut": llm.tokens_out,
        "kostnad_usd": None if cost is None else round(cost, 4),
        "svar": rows,
    }
    print(f"\nKall: {llm.calls}  Tokens inn/ut: {llm.tokens_in}/{llm.tokens_out}  Kostnad: {summary['kostnad_usd']} USD")
    if llm.calls == 0:
        print("Ingen modellkall lyktes. Ingenting lagret.")
        return 2
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Lagret {rel(CASSETTE)} og {rel(SUMMARY)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
