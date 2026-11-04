"""Faktakontroll v2 for intern assistent.

Modellen svarer med henvisninger som [1], [2] til nummererte funn (KONTEKST). Kontrollen krever:
- minst én gyldig henvisning, og ingen henvisning til nummer som ikke finnes
- tall, enheter, klokkeslett, måneder, myndigheter, roller og lovnavn finnes i de HENVISTE funnene
- ingen juridiske vurderinger, lenker eller e-postadresser som ikke står i funnene
- tall skrevet med sifre (ikke bokstaver) og riktig fortegn

Kontrollen er regex, ikke en modell. Den fanger det som kan telles og gjenkjennes. Den kan IKKE avgjøre
om en påstand uten tall, enhet eller navn er riktig. Se tests/test_intern_llm.py for avgrensningen.
"""

from __future__ import annotations

import re
from typing import Any

from src.kunstpixel.core.intern.data import ROLLER, fold

REFUSAL_TOKEN = "IKKE_I_DATAENE"
MAX_ANSWER_CHARS = 1500

CITE_RE = re.compile(r"\[(\d{1,3})\]")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\b")
NUM_RE = re.compile(r"(?<![\w.,])([+\-−]?)(\d+(?:[.,]\d+)?)")
LIST_NUMBER_RE = re.compile(r"(?m)^\s*\d+[.)]\s+")

UNIT_WORDS: dict[str, str] = {
    "minutt": "min", "minutter": "min",
    "time": "time", "timer": "time", "timen": "time", "timene": "time",
    "dag": "dag", "dager": "dag", "dagen": "dag",
    "kg": "kg",
    "grad": "grad", "grader": "grad", "°c": "grad", "°": "grad",
    "%": "prosent", "prosent": "prosent",
    "kr": "kr", "kroner": "kr",
    "person": "person", "personer": "person",
    "m2": "m2", "m²": "m2",
    "ar": "ar",  # folded "år"
    "gang": "gang", "ganger": "gang",
    "sekund": "sek", "sekunder": "sek",
    "meter": "meter",
    "gjest": "gjest", "gjester": "gjest",
    "uke": "uke", "uker": "uke",
    "maned": "mnd", "maneder": "mnd",
}  # fmt: skip
_UNIT_RE = r"(?:%|°\s?c|°|[a-zæøåA-ZÆØÅ0-9²]+)"
AFTER_NUMBER_RE = re.compile(rf"^\s*({_UNIT_RE})", re.I)
RANGE_RE = re.compile(
    rf"(\d+(?:[.,]\d+)?)\s*(?:til|–|—|-)\s*(\d+(?:[.,]\d+)?)\s*({_UNIT_RE})", re.I
)
SPELLED_RE = re.compile(
    r"\b(?:null|to|tre|fire|fem|seks|sju|syv|åtte|ni|ti|elleve|tolv|tjue|tretti|førti|femti|seksti|sytti|åtti|nitti|hundre|tusen)\b"
    r"(?:\s+\w+){0,2}?\s+(?:minutt\w*|time[rn]?|dag\w*|kg|prosent|kroner|kr|person\w*|ganger|gang|sekund\w*|meter|gjester|uke\w*|måned\w*)\b",
    re.I,
)  # fmt: skip

MONTHS = "januar februar mars april mai juni juli august september oktober november desember".split()
AUTHORITY_RE = re.compile(r"\b(\w+tilsyn\w*|\w+etaten|\w+direktoratet|\w+loven|\w+forskriften|dsb|nav|politiet|brannvesenet|forsikring\w*)\b")
ROLE_WORDS = tuple(fold(r) for r in ROLLER) + (
    "verneombud", "tillitsvalgt", "brannvernleder", "kafeansvarlig", "kafeleder", "styreleder", "konservator",
    "hr-sjef", "personalsjef", "direktoren",
)  # fmt: skip
LEGAL_PHRASES = (
    "du har rett til", "du har krav pa", "du kan kreve", "erstatning", "soksmal", "saksok", "ulovlig",
    "lovbrudd", "straffbart", "rettslig", "juridisk",
)  # fmt: skip
EXFIL_RE = re.compile(r"https?://|www\.|\S+@\S+\.\S+|\]\(|<\s*/?\s*[a-z]+[^>]*>", re.I)


def extract_citations(text: str) -> list[int]:
    seen: list[int] = []
    for m in CITE_RE.finditer(text):
        n = int(m.group(1))
        if n not in seen:
            seen.append(n)
    return seen


def _key(num: str) -> float:
    return abs(float(num.replace(",", ".")))


def _unit(word: str) -> str | None:
    return UNIT_WORDS.get(fold(word.replace(" ", "")))


def _numbers_and_pairs(text: str) -> tuple[set[tuple[str, float]], set[float], set[tuple[float, str]], list[tuple[str, float, str | None]]]:
    """Returnerer (fortegn+tall, tall, (tall, enhet), liste over alle forekomster)."""
    signed: set[tuple[str, float]] = set()
    keys: set[float] = set()
    pairs: set[tuple[float, str]] = set()
    occurrences: list[tuple[str, float, str | None]] = []

    for m in RANGE_RE.finditer(text):  # «15 til 40 kg» gjelder begge tallene
        u = _unit(m.group(3))
        if u:
            pairs.add((_key(m.group(1)), u))
            pairs.add((_key(m.group(2)), u))

    for m in NUM_RE.finditer(text):
        sign = "-" if m.group(1) in ("-", "−") else ("+" if m.group(1) == "+" else "")
        k = _key(m.group(2))
        tail = AFTER_NUMBER_RE.match(text[m.end() : m.end() + 24])
        u = _unit(tail.group(1)) if tail else None
        signed.add((sign, k))
        keys.add(k)
        if u:
            pairs.add((k, u))
        occurrences.append((sign, k, u))
    return signed, keys, pairs, occurrences


def verify_intern(
    text: str,
    kontekst: list[dict[str, Any]],
    ignore_roles: frozenset[str] | set[str] = frozenset(),
    max_chars: int = MAX_ANSWER_CHARS,
) -> list[str]:
    """Returnerer brudd. Tom liste betyr at svaret kan vises."""
    violations: list[str] = []
    if len(text) > max_chars:
        violations.append(f"for langt svar ({len(text)} tegn)")

    by_nr = {int(f["nr"]): f for f in kontekst}
    cited = extract_citations(text)
    bad = [n for n in cited if n not in by_nr]
    for n in bad:
        violations.append(f"ugyldig kildehenvisning [{n}]")
    valid = [n for n in cited if n in by_nr]
    if not valid:
        violations.append("mangler kildehenvisning")

    # Alt kontrolleres mot de HENVISTE funnene, ikke mot alle funn modellen fikk se.
    raw_corpus = " ".join(f"{by_nr[n].get('kilde','')} {by_nr[n].get('sti','')} {by_nr[n].get('kontekst','')} {by_nr[n].get('tekst','')}" for n in valid)
    corpus = fold(raw_corpus)
    body = CITE_RE.sub(" ", text)
    folded = fold(body)

    # Lenker, e-post og HTML som ikke står i funnene
    for m in EXFIL_RE.finditer(body):
        if m.group(0).lower() not in raw_corpus.lower():
            violations.append("lenke, e-post eller HTML i svaret")
            break

    # Juridiske vurderinger
    for phrase in LEGAL_PHRASES:
        if phrase in folded and phrase not in corpus:
            violations.append(f"juridisk vurdering: {phrase}")

    # Klokkeslett må stå ordrett
    for t in sorted(set(TIME_RE.findall(body))):
        if t not in raw_corpus:
            violations.append(f"klokkeslett ikke i funnene: {t}")
    body_no_time = TIME_RE.sub(" ", LIST_NUMBER_RE.sub("", body))

    # Tall, fortegn og enheter
    c_signed, c_keys, c_pairs, _ = _numbers_and_pairs(raw_corpus)
    c_units: dict[float, set[str]] = {}
    for ck, cu in c_pairs:
        c_units.setdefault(ck, set()).add(cu)
    _, _, _, a_occ = _numbers_and_pairs(body_no_time)
    for sign, k, u in a_occ:
        label = f"{sign}{k:g}"
        if k not in c_keys:
            violations.append(f"tall ikke i funnene: {label}")
        elif sign in ("-", "+") and (sign, k) not in c_signed:
            violations.append(f"feil fortegn: {label}")
        elif sign == "" and ("", k) not in c_signed and ("+", k) not in c_signed:
            violations.append(f"mangler minustegn i funnene: {k:g}")
        elif u and (k, u) not in c_pairs and c_units.get(k):
            # Tallet står i funnet med en ANNEN enhet. Står det uten enhet («maks personer: 50»), er det ok.
            violations.append(f"enhet stemmer ikke: {k:g} {u}")
    # Tall med bokstaver kan ikke kontrolleres, med mindre akkurat den formuleringen står i funnene
    # («grense to personer: 15 til 40 kg» er data, ikke noe modellen har funnet på).
    for m in SPELLED_RE.finditer(body):
        if fold(m.group(0)) not in corpus:
            violations.append("tall skrevet med bokstaver")
            break

    # Måneder
    for month in MONTHS:
        if re.search(rf"\b{month}\b", folded) and month not in corpus:
            violations.append(f"måned ikke i funnene: {month}")

    # Myndigheter og lovnavn (bøyning tåles: Mattilsynets -> Mattilsynet)
    for m in AUTHORITY_RE.finditer(folded):
        base = re.sub(r"(ets|et|s)$", "", m.group(1))
        if base not in corpus:
            violations.append(f"myndighet eller lov ikke i funnene: {m.group(1)}")

    # Roller
    ignore = {fold(r) for r in ignore_roles}
    for word in ROLE_WORDS:
        if word in ignore:
            continue
        if re.search(rf"\b{re.escape(word)}", folded) and word not in corpus:
            violations.append(f"rolle ikke i funnene: {word}")

    return list(dict.fromkeys(violations))
