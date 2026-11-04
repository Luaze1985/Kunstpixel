"""Faktakontroll av LLM-tekst mot verktøyresultater.

verify_facts() returnerer en liste med brudd. Tom liste = teksten kan vises.
Kontrollen er bevisst streng på tall, ID-er, navn og magasinverk, og bevisst enkel
(regex, ingen modell). Den kan ikke oppdage oppdiktede titler eller påstander uten tall.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.kunstpixel.core.db import execute_read_query

AURA_ID_RE = re.compile(r"AURA-\d{4}-\d{3}")
ROOM_ID_RE = re.compile(r"\b(?:SAL-[A-Z]|MAG-\d)\b")
SAL_NAME_RE = re.compile(r"\bSal ([A-E])\b")
YEAR_RE = re.compile(r"\b(1[5-9]\d{2}|20\d{2})\b")
CENTURY_TAIL_RE = re.compile(r"-?\s*(?:(?:og|eller|til)\s+\d{4}-?\s*)?tallet")
AMOUNT_RE = re.compile(
    r"(?:\b(?:kr\.?|nok)\s*(\d[\d ]*)|(\d[\d ]*)\s*(?:kr\b|kroner\b|nok\b|,-))",
    re.IGNORECASE,
)
SPELLED_AMOUNT_RE = re.compile(
    r"\b(?:null|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni|ti|elleve|tolv|tjue|tretti|førti|femti|"
    r"seksti|sytti|åtti|nitti|hundre|tusen)\b(?:\s+\w+){0,2}\s+(?:kr|kroner)\b",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")


@dataclass
class Entities:
    """Kjente navn og verk fra databasen, brukt til å oppdage ugrunnede omtaler."""

    artists: list[str] = field(default_factory=list)
    works: list[tuple[str, str, str]] = field(default_factory=list)  # (id, tittel, status)


def load_entities(db_path: Path | str | None = None) -> Entities:
    artists = [r["navn"] for r in execute_read_query("SELECT navn FROM kunstnere", {}, db_path=db_path)]
    works = [
        (r["id"], r["tittel"], r["status"])
        for r in execute_read_query("SELECT id, tittel, status FROM verk", {}, db_path=db_path)
    ]
    return Entities(artists=artists, works=works)


def _corpus(tool_results: list[dict[str, Any]]) -> str:
    return json.dumps(tool_results, ensure_ascii=False, default=str).lower()


def _corpus_numbers(corpus: str) -> set[int]:
    out: set[int] = set()
    for tok in NUMBER_RE.findall(corpus):
        try:
            val = float(tok.replace(",", "."))
        except ValueError:
            continue
        if val == int(val):
            out.add(int(val))
    return out


def verify_facts(
    text: str,
    tool_results: list[dict[str, Any]],
    entities: Entities,
    forbidden_words: list[str] | None = None,
) -> list[str]:
    """Sjekk at alle fakta i `text` finnes i `tool_results`. Returnerer brudd (tom liste = OK)."""
    violations: list[str] = []
    corpus = _corpus(tool_results)
    numbers = _corpus_numbers(corpus)
    lower = text.lower()

    # 1. ID-er først, så fjernes de fra teksten før årstallsjekk.
    for aura_id in sorted(set(AURA_ID_RE.findall(text))):
        if aura_id.lower() not in corpus:
            violations.append(f"verks-ID ikke i verktøyresultat: {aura_id}")
    for room_id in sorted(set(ROOM_ID_RE.findall(text))):
        if room_id.lower() not in corpus:
            violations.append(f"sal-ID ikke i verktøyresultat: {room_id}")
    for letter in sorted(set(SAL_NAME_RE.findall(text))):
        if f"sal-{letter.lower()}" not in corpus and f"sal {letter.lower()}" not in corpus:
            violations.append(f"Sal {letter} ikke i verktøyresultat")

    # 2. Årstall (hopp over "1800- og 1900-tallet").
    stripped = AURA_ID_RE.sub(" ", text)
    for m in YEAR_RE.finditer(stripped):
        year = m.group(1)
        if CENTURY_TAIL_RE.match(stripped[m.end() : m.end() + 25]):
            continue
        if int(year) not in numbers:
            violations.append(f"årstall ikke i verktøyresultat: {year}")

    # 3. Beløp: sifre må finnes i resultatet; tall skrevet med bokstaver er ikke tillatt.
    for m in AMOUNT_RE.finditer(text):
        raw = (m.group(1) or m.group(2) or "").replace(" ", "")
        if raw and int(raw) not in numbers:
            violations.append(f"beløp ikke i verktøyresultat: {raw} kr")
    if SPELLED_AMOUNT_RE.search(text):
        violations.append("beløp skrevet med bokstaver (kan ikke kontrolleres)")

    # 4. Kunstnere (fullt navn eller etternavn) må være nevnt i resultatet.
    for name in entities.artists:
        surname = name.split()[-1]
        if re.search(rf"\b{re.escape(surname)}", text) and surname.lower() not in corpus:
            violations.append(f"kunstner ikke i verktøyresultat: {name}")

    # 5. Verk: tittel må være i resultatet, og magasinverk skal ikke omtales som utstilt.
    for work_id, title, status in entities.works:
        title_in_text = re.search(rf"(?<!\w){re.escape(title)}(?!\w)", text) is not None
        id_in_text = work_id in text
        if not (title_in_text or id_in_text):
            continue
        if status != "utstilt" and "magasin" not in lower:
            violations.append(f"magasinverk omtalt uten magasin-forbehold: {title}")
        elif title.lower() not in corpus and work_id.lower() not in corpus:
            violations.append(f"verk ikke i verktøyresultat: {title}")

    # 6. Forbudte ord.
    for word in forbidden_words or []:
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            violations.append(f"forbudt ord: {word}")

    return violations
