"""Datalag for intern assistent.

Leser YAML, JSON og markdown og gjør dem om til små, adresserbare funn (`Finding`) med
kilde (fil) og sti (avsnitt i filen). Alt er skrivebeskyttet. Hver kilde har klassifisering
og en liste over roller som har tilgang. Mangler en rolle tilgang, finnes ikke funnene for den.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from src.kunstpixel.core.datapolicy import SYNTETISK, normalize_classification
from src.kunstpixel.core.db import FAQ_STOPWORDS

SEP = " › "

# Interne roller (kanoniske id-er). Ukjent rolle får ingen tilgang (fail-closed).
ROLLER: tuple[str, ...] = (
    "museumsdirektor",
    "samlingsforvalter",
    "kurator",
    "formidler",
    "museumsvert",
    "driftsansvarlig",
    "kvalitetsvokter",
)
ALLE: frozenset[str] = frozenset(ROLLER)
LEDELSE: frozenset[str] = frozenset({"museumsdirektor", "driftsansvarlig", "kvalitetsvokter"})


class InternDataError(Exception):
    """Datafil mangler eller har ugyldig format. Meldingen nevner alltid filen."""


def fold(text: str) -> str:
    """Slå sammen skrivemåter: æøå, ae/oe/aa og ASCII-versjoner gir samme tegn.

    Datafilene blander ekte bokstaver og forenklet ASCII (`palagt`, `hoest`), så både
    spørsmål og data foldes likt før søk.
    """
    t = text.lower().replace("æ", "a").replace("ø", "o").replace("å", "a")
    return t.replace("ae", "a").replace("oe", "o").replace("aa", "a")


def role_id(value: Any) -> str | None:
    """Kanonisk rolle-id, eller None hvis rollen er ukjent. Eksakt treff etter folding."""
    if not isinstance(value, str):
        return None
    rid = fold(value.strip())
    canon = {fold(r): r for r in ROLLER}
    return canon.get(rid)


@dataclass(frozen=True)
class Finding:
    kilde: str  # fil, relativ til prosjektroten, med skråstrek
    sti: str  # avsnitt i filen
    tekst: str
    tema: str  # hms | ik_mat | brann | tilsyn | rolle | tiltak | myndighet | rapportering | arbeidsoppgaver | historikk
    klassifisering: str
    kontekst: str = ""  # verdier fra overordnet avsnitt, brukt i søk og vist til modellen
    rolle: str | None = None  # kanonisk rolle-id for rolleoppføringer

    def to_dict(self) -> dict[str, Any]:
        d = {
            "kilde": self.kilde,
            "sti": self.sti,
            "tekst": self.tekst,
            "tema": self.tema,
            "klassifisering": self.klassifisering,
        }
        if self.kontekst:
            d["kontekst"] = self.kontekst
        if self.rolle:
            d["rolle"] = self.rolle
        return d

    @property
    def soketekst(self) -> str:
        return f"{self.sti} {self.kontekst} {self.tekst}"


@dataclass(frozen=True)
class SourceSpec:
    path: str  # relativt til prosjektroten
    tema: str
    klassifisering: str
    tilgang: frozenset[str]
    kind: str  # yaml | json | roster | tool_access


DEFAULT_SOURCES: tuple[SourceSpec, ...] = (
    SourceSpec("05_data/governance/hms_arbeidsmiljo.yaml", "hms", SYNTETISK, ALLE, "yaml"),
    SourceSpec("05_data/governance/ik_mat_kafe.yaml", "ik_mat", SYNTETISK, ALLE, "yaml"),
    SourceSpec("05_data/governance/brann_sikring_kapasitet.yaml", "brann", SYNTETISK, ALLE, "yaml"),
    SourceSpec("05_data/governance/tilsynskalender.json", "tilsyn", SYNTETISK, ALLE, "json"),
    SourceSpec("03_team/team_roster.md", "rolle", SYNTETISK, ALLE, "roster"),
    SourceSpec("04_knowledge/04_domain/operations/tool_access.md", "rolle", SYNTETISK, ALLE, "tool_access"),
    SourceSpec("05_data/governance/noexcuse_prioriterte_tiltak.yaml", "tiltak", SYNTETISK, LEDELSE, "yaml"),
    SourceSpec("05_data/governance/myndighetskontakter.yaml", "myndighet", SYNTETISK, ALLE, "yaml"),
    SourceSpec("05_data/governance/tilsynsbesok_rutine.yaml", "myndighet", SYNTETISK, ALLE, "yaml"),
    SourceSpec("05_data/governance/rapporteringskalender.yaml", "rapportering", SYNTETISK, ALLE, "yaml"),
    SourceSpec("05_data/governance/rapportmaler.yaml", "rapportering", SYNTETISK, ALLE, "yaml"),
    SourceSpec("05_data/governance/arbeidsoppgaver_tidsbruk.yaml", "arbeidsoppgaver", SYNTETISK, LEDELSE, "yaml"),
    SourceSpec("05_data/governance/historikk_tall.yaml", "historikk", SYNTETISK, LEDELSE, "yaml"),
    SourceSpec("05_data/governance/historikk_tekst.yaml", "historikk", SYNTETISK, LEDELSE, "yaml"),
)

# Syntetiske personnavn og e-postadresser i myndighetskontakter skjermes i InternData (bruk rolle, aldri personnavn).
_SKJERMEDE_KONTAKTFELT = frozenset({"kontaktperson", "kontakt_epost", "intern_eier_navn", "intern_eier_epost"})


def _strip_contact_fields(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_contact_fields(v) for k, v in obj.items() if k not in _SKJERMEDE_KONTAKTFELT}
    if isinstance(obj, list):
        return [_strip_contact_fields(v) for v in obj]
    return obj


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


# ---------------------------------------------------------------- flatting av YAML/JSON


def _human(key: Any) -> str:
    return str(key).replace("_", " ")


def _scalar(value: Any) -> bool:
    return not isinstance(value, (dict, list))


def _label(item: dict[str, Any], index: int) -> str:
    for k in ("id", "maned", "navn", "tittel", "ar"):
        if k in item and _scalar(item[k]):
            return str(item[k])
    return str(index + 1)


def _fmt_pairs(d: dict[str, Any]) -> str:
    # Tomme verdier (None) hoppes over. De ville blitt vist som teksten «None», et oppdiktet faktum.
    return "; ".join(f"{_human(k)}: {v}" for k, v in d.items() if _scalar(v) and v is not None)


def flatten(obj: Any, kilde: str, tema: str, klass: str, path: tuple[str, ...] = (), kontekst: str = "") -> list[Finding]:
    """Gjør en nøstet struktur om til funn. Hver 'løvpost' blir ett funn.

    - En dict med bare enkeltverdier er ett funn.
    - En dict med blandet innhold gir ett funn for enkeltverdiene og rekurserer på resten.
      Enkeltverdiene gis videre som kontekst til underfunn, unntatt på rotnivå.
    - En liste med enkeltverdier er ett funn. En liste med dicts gir ett funn per dict.
    """
    out: list[Finding] = []
    if obj is None:
        return out
    if isinstance(obj, dict):
        scalars = {k: v for k, v in obj.items() if _scalar(v) and v is not None}
        complex_items = {k: v for k, v in obj.items() if not _scalar(v)}  # None er hverken enkelt eller sammensatt
        if scalars:
            out.append(Finding(kilde, SEP.join(path) if path else "(rot)", _fmt_pairs(scalars), tema, klass, kontekst))
        child_ctx = _fmt_pairs(scalars) if (scalars and path) else kontekst
        for k, v in complex_items.items():
            out.extend(flatten(v, kilde, tema, klass, path + (_human(k),), child_ctx))
    elif isinstance(obj, list):
        obj = [v for v in obj if v is not None]
        if not obj:
            return out
        if all(_scalar(v) for v in obj):
            out.append(Finding(kilde, SEP.join(path), "; ".join(str(v) for v in obj), tema, klass, kontekst))
        else:
            for i, item in enumerate(obj):
                if isinstance(item, dict):
                    out.extend(flatten(item, kilde, tema, klass, path + (_label(item, i),), kontekst))
                elif _scalar(item):
                    out.append(Finding(kilde, SEP.join(path + (str(i + 1),)), str(item), tema, klass, kontekst))
    else:
        out.append(Finding(kilde, SEP.join(path), str(obj), tema, klass, kontekst))
    return out


# ---------------------------------------------------------------- markdown


def _strip_md(s: str) -> str:
    return re.sub(r"\*\*|`", "", s).strip()


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for line in lines:
        s = line.strip()
        if s.startswith("|") and not re.match(r"^\|\s*:?-{2,}", s):
            rows.append([_strip_md(c) for c in s.strip("|").split("|")])
    return rows


def parse_roster(text: str, kilde: str, klass: str) -> list[Finding]:
    """team_roster.md: oversiktstabell (§1) og rollekontrakter (### A. Navn (`/trigger`))."""
    findings: list[Finding] = []
    lines = text.splitlines()

    # Tabeller: alle tabeller med kolonnen 'Rolle / Agent'
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and "Rolle" in lines[i]:
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            rows = _table_rows(block)
            if rows:
                header = rows[0]
                for r in rows[1:]:
                    if len(r) == len(header):
                        pairs = "; ".join(f"{h.lower()}: {v}" for h, v in zip(header[1:], r[1:]))
                        findings.append(
                            Finding(kilde, f"Team-oversikt{SEP}{r[0]}", pairs, "rolle", klass, rolle=role_id(r[0]))
                        )
            continue
        i += 1

    # Rollekontrakter
    heading = re.compile(r"^###\s+[A-Z]\.\s+(.+?)\s+\(`/[\w-]+`\)")
    current: str | None = None
    label: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf, label
        if current and label and buf:
            text_ = " ".join(b.strip() for b in buf).strip()
            findings.append(
                Finding(kilde, f"Rollekontrakter{SEP}{current}{SEP}{label}", _strip_md(text_), "rolle", klass, rolle=role_id(current))
            )
        buf = []
        label = None

    for line in lines:
        m = heading.match(line)
        if m:
            flush()
            current = m.group(1)
            continue
        if line.startswith("## ") or line.strip() == "---":
            flush()
            current = None
            continue
        if current is None:
            continue
        b = re.match(r"^\*\s+\*\*(.+?):\*\*\s*(.*)$", line)
        if b:
            flush()
            label = b.group(1)
            buf = [b.group(2)] if b.group(2) else []
        elif label and line.strip():
            buf.append(line.strip().lstrip("*").strip())
    flush()
    return findings


def parse_tool_access(text: str, kilde: str, klass: str) -> list[Finding]:
    rows = _table_rows(text.splitlines())
    findings: list[Finding] = []
    if not rows:
        return findings
    header = rows[0]
    for r in rows[1:]:
        if len(r) == len(header):
            pairs = "; ".join(f"{h.lower()}: {v}" for h, v in zip(header[1:], r[1:]))
            findings.append(Finding(kilde, f"Verktøytilganger{SEP}{r[0]}", pairs, "rolle", klass, rolle=role_id(r[0])))
    return findings


# ---------------------------------------------------------------- søk

INTERN_STOPWORDS = {
    "mange", "mye", "hvilke", "hvilken", "hvilket", "hvor", "noe", "alle", "gjelder", "regler", "reglene",
    "når", "naar", "ofte", "lenge", "finnes", "bruke", "brukes", "bruker", "sitt", "sin", "ansvar", "ansvaret",
    "trenger", "leveres", "sendes", "ut", "forste", "første", "dagen", "innen", "mest",
}  # fmt: skip
_STOP = {fold(w) for w in FAQ_STOPWORDS} | {fold(w) for w in INTERN_STOPWORDS}

# Enkel synonymhjelp for den regelbaserte baselinjen (folded former). Modellen i H4 trenger ikke dette.
SYNONYMER: dict[str, tuple[str, ...]] = {
    "sta": ("staing", "felt"),
    "staende": ("staing",),
    "lukkes": ("lukking",),
    "magesyke": ("sykdom", "oppkast", "diare"),
    "datakilder": ("kilder", "kilde"),
    "skriver": ("eier",),
    "tid": ("timer",),
    "forst": ("hoy",),
    "kontakt": ("myndigheter", "eier"),
    "kontakten": ("myndigheter", "eier"),
    "kontaktpunkt": ("myndigheter", "eier"),
}

MIN_DEKNING = 0.6
BRED_DEKNING = 0.25  # bredt søk gir modellen flere kandidater. Modellen avgjør hva som faktisk svarer.
# Et innholdsord som ikke finnes noe sted i dataene gjør treffet svakere. Uten dette ville
# «Hva er været i morgen?» fått et svar om kjøleskap fordi «morgen» står i en loggrutine.
UKJENT_VEKT = 3.0


def _tokens(text: str) -> list[str]:
    t = fold(text)
    t = re.sub(r"\bsal[\s_]+([a-e])\b", r"sal\1", t)
    return [w for w in re.findall(r"[a-z0-9+\-]+", t) if (len(w) >= 2 or w.isdigit())]


def tokens_match(q: str, d: str) -> bool:
    """To ord er samme ord hvis de er like, eller deler en lang nok begynnelse (tåler norsk bøyning)."""
    if q == d:
        return True
    p = 0
    for a, b in zip(q, d):
        if a != b:
            break
        p += 1
    return p >= 5 and p >= max(5, min(len(q), len(d)) - 2)


def query_terms(query: str) -> list[str]:
    seen: list[str] = []
    for w in _tokens(query):
        if w not in _STOP and w not in seen:
            seen.append(w)
    return seen


def _has(term: str, doc: set[str]) -> bool:
    if any(tokens_match(term, d) for d in doc):
        return True
    return any(tokens_match(alt, d) for alt in SYNONYMER.get(term, ()) for d in doc)


def n_treff(terms: list[str], f: Finding) -> int:
    doc = set(_tokens(f.soketekst))
    return sum(1 for t in terms if _has(t, doc))


def _full_word_hits(terms: list[str], f: Finding) -> int:
    """Tie-breaker: foretrekk funn der hele sammensatte ord treffer (f.eks. 'avviksrapport' over 'avvik')."""
    doc = set(_tokens(f.soketekst))
    return sum(
        1
        for t in terms
        if any(abs(len(t) - len(d)) <= 3 and tokens_match(t, d) for d in doc)
    )


def score(terms: list[str], f: Finding, weight: Any = None) -> float:
    """Vektet dekning: andelen av spørsmålets innholdsord (vektet etter hvor sjeldne de er) som finnes i funnet."""
    if not terms:
        return 0.0
    w = weight or (lambda s: 1.0)
    doc = set(_tokens(f.soketekst))
    total = sum(w(t) for t in terms)
    hit = sum(w(t) for t in terms if _has(t, doc))
    return hit / total if total else 0.0


# ---------------------------------------------------------------- selve datalaget


@dataclass
class InternData:
    base: Path = field(default_factory=repo_root)
    sources: tuple[SourceSpec, ...] = DEFAULT_SOURCES
    findings: list[Finding] = field(default_factory=list)
    tilgang: dict[str, frozenset[str]] = field(default_factory=dict)  # kilde -> roller

    def __post_init__(self) -> None:
        self.base = Path(self.base)
        self.findings = []
        self.tilgang = {}
        for spec in self.sources:
            self.findings.extend(self._load(spec))
            self.tilgang[spec.path] = spec.tilgang
        self._build_weights()

    def _build_weights(self) -> None:
        self._docs = [set(_tokens(f.soketekst)) for f in self.findings]
        self._df_cache: dict[str, int] = {}
        self._n = max(1, len(self.findings))

    def weight(self, stem: str) -> float:
        """Sjeldne ord veier tyngre. Ukjente ord har en middels vekt (UKJENT_VEKT)."""
        d = self._df_cache.get(stem)
        if d is None:
            d = sum(1 for doc in self._docs if _has(stem, doc))
            self._df_cache[stem] = d
        w = UKJENT_VEKT if d == 0 else math.log(self._n / d) + 0.5
        # "Sal A" er det spørsmålet handler om, ikke et tilfeldig ord.
        if len(stem) == 4 and stem.startswith("sal") and stem[3] in "abcde":
            w *= 2
        return w

    def _load(self, spec: SourceSpec) -> list[Finding]:
        path = self.base / spec.path
        klass = normalize_classification(spec.klassifisering)
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise InternDataError(f"Kan ikke lese {spec.path}: {exc.__class__.__name__}") from exc
        try:
            if spec.kind == "yaml":
                loaded = _strip_contact_fields(yaml.safe_load(raw))
                return flatten(loaded, spec.path, spec.tema, klass)
            if spec.kind == "json":
                return flatten(json.loads(raw), spec.path, spec.tema, klass)
            if spec.kind == "roster":
                return parse_roster(raw, spec.path, klass)
            if spec.kind == "tool_access":
                return parse_tool_access(raw, spec.path, klass)
        except (yaml.YAMLError, json.JSONDecodeError, ValueError, TypeError) as exc:
            raise InternDataError(f"Ugyldig format i {spec.path}: {exc.__class__.__name__}") from exc
        raise InternDataError(f"Ukjent kildetype for {spec.path}: {spec.kind}")

    def allowed(self, role: str | None, f: Finding) -> bool:
        rid = role_id(role)
        return rid is not None and rid in self.tilgang.get(f.kilde, frozenset())

    def for_role(self, role: str | None, temaer: tuple[str, ...] | None = None) -> list[Finding]:
        return [f for f in self.findings if self.allowed(role, f) and (temaer is None or f.tema in temaer)]

    def has_tema(self, tema: str) -> bool:
        return any(f.tema == tema for f in self.findings)

    def restricted_for(self, role: str | None, temaer: tuple[str, ...]) -> bool:
        """True hvis temaene finnes, men rollen ikke har tilgang til noen av dem."""
        return any(f.tema in temaer for f in self.findings) and not self.for_role(role, temaer)

    def search(
        self, query: str, role: str | None, temaer: tuple[str, ...] | None = None, limit: int = 5, bred: bool = False
    ) -> list[tuple[float, Finding]]:
        stems = query_terms(query)
        scored = [(score(stems, f, self.weight), f) for f in self.for_role(role, temaer)]
        # Minst to ordtreff når spørsmålet har flere innholdsord. Ett løsrevet treff
        # («morgen» i «Hva er været i morgen?») er ikke et svar.
        min_treff = 1 if bred else (2 if len(stems) >= 2 else 1)
        min_dekning = BRED_DEKNING if bred else MIN_DEKNING
        hits = [(s, f) for s, f in scored if s >= min_dekning and n_treff(stems, f) >= min_treff]
        hits.sort(key=lambda x: (-x[0], -_full_word_hits(stems, x[1])))
        return hits[: max(1, min(int(limit), 20))]
