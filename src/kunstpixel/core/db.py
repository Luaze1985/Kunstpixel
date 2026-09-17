"""Database access layer for Aura Kunstmuseum.

Provides safe, read-only parameterized SQLite queries with Norwegian character handling,
query normalization, and table/column quoting.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from src.aura_museum.core.config import get_db_path

# Prohibited keywords to strictly enforce read-only access at the application boundary
FORBIDDEN_SQL_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "REINDEX",
}

VALID_ROOM_IDS = ["SAL-A", "SAL-B", "SAL-C", "SAL-D", "SAL-E", "MAG-1"]


def get_db_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Return a read-only SQLite connection using sqlite3.Row row factory."""
    if db_path is None:
        db_file = get_db_path()
    else:
        db_file = Path(db_path)

    if not db_file.is_file():
        raise FileNotFoundError(f"Database file not found at: {db_file}")

    # Use SQLite URI with mode=ro to enforce read-only at the SQLite engine level
    conn = sqlite3.connect(f"file:{db_file.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def validate_read_only_query(sql: str) -> None:
    """Enforce that queries are strictly read-only SELECT or WITH statements."""
    stripped = sql.strip()
    upper = stripped.upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise PermissionError("Read-only violation: Only SELECT or WITH queries are permitted.")

    tokens = set(re.findall(r"\b[A-Za-z_]+\b", upper))
    forbidden_used = tokens.intersection(FORBIDDEN_SQL_KEYWORDS)
    if forbidden_used:
        raise PermissionError(
            f"Read-only violation: Forbidden keyword(s) detected: {', '.join(sorted(forbidden_used))}"
        )


def execute_read_query(
    sql: str,
    params: dict[str, Any] | tuple[Any, ...] = (),
    db_path: Path | str | None = None,
) -> list[sqlite3.Row]:
    """Execute a parameterized read-only query safely and return rows."""
    validate_read_only_query(sql)
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def normalize_room_identifier(room_id: str) -> str:
    """Normalize room identifiers like 'Sal D', 'sal-d', 'd', 'SAL-D' to 'SAL-D'."""
    raw = room_id.strip()
    upper = raw.upper()
    if upper in VALID_ROOM_IDS:
        return upper

    cleaned = re.sub(r"[^A-Z0-9]", "", upper)
    if cleaned.startswith("SAL") and len(cleaned) > 3:
        letter = cleaned[3:]
        candidate = f"SAL-{letter}"
        if candidate in VALID_ROOM_IDS:
            return candidate
    if cleaned.startswith("MAG") and len(cleaned) > 3:
        num = cleaned[3:]
        candidate = f"MAG-{num}"
        if candidate in VALID_ROOM_IDS:
            return candidate
    if cleaned in ["A", "B", "C", "D", "E"]:
        return f"SAL-{cleaned}"
    return upper


def normalize_norwegian_text(text: str) -> str:
    """Normalize Norwegian characters and spelling variations for robust search."""
    lowered = text.lower()
    return (
        lowered.replace("å", "aa")
        .replace("æ", "ae")
        .replace("ø", "oe")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
    )


def query_collection(
    query: str | None = None,
    artist: str | None = None,
    title: str | None = None,
    technique: str | None = None,
    theme: str | None = None,
    room_id: str | None = None,
    limit: int = 10,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Search artworks by artist, title, technique, theme, or room."""
    sql = """
    SELECT 
        v.id,
        v.tittel,
        k.navn AS kunstner,
        v.aar,
        v.teknikk,
        v.dimensjoner,
        v.sal_id,
        s.navn AS sal_navn,
        v.status,
        v.temaer,
        v.beskrivelse
    FROM verk v
    JOIN kunstnere k ON v.kunstner_id = k.id
    LEFT JOIN saler s ON v.sal_id = s.id
    WHERE 1=1
    """
    params: dict[str, Any] = {}

    if query and query.strip():
        q = query.strip()
        sql += """
        AND (
            k.navn LIKE :query
            OR v.tittel LIKE :query
            OR v.teknikk LIKE :query
            OR v.temaer LIKE :query
            OR v.beskrivelse LIKE :query
            OR v.sal_id LIKE :query
            OR s.navn LIKE :query
        )
        """
        params["query"] = f"%{q}%"

    if artist and artist.strip():
        sql += " AND k.navn LIKE :artist"
        params["artist"] = f"%{artist.strip()}%"

    if title and title.strip():
        sql += " AND v.tittel LIKE :title"
        params["title"] = f"%{title.strip()}%"

    if technique and technique.strip():
        sql += " AND v.teknikk LIKE :technique"
        params["technique"] = f"%{technique.strip()}%"

    if theme and theme.strip():
        sql += " AND v.temaer LIKE :theme"
        params["theme"] = f"%{theme.strip()}%"

    if room_id and room_id.strip():
        norm_room = normalize_room_identifier(room_id)
        sql += " AND (UPPER(v.sal_id) = :norm_room OR UPPER(v.sal_id) LIKE :raw_room OR LOWER(s.navn) LIKE :raw_room_lower)"
        params["norm_room"] = norm_room
        params["raw_room"] = f"%{room_id.strip().upper()}%"
        params["raw_room_lower"] = f"%{room_id.strip().lower()}%"

    sql += " ORDER BY v.aar ASC, v.id ASC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 50))

    rows = execute_read_query(sql, params, db_path=db_path)
    results = []
    for r in rows:
        d = dict(r)
        d["tema"] = [t.strip() for t in d["temaer"].split(",") if t.strip()] if d.get("temaer") else []
        results.append(d)
    return results


def query_artwork_details(
    artwork_id: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve full metadata, wall text, and provenance for an artwork by ID or title."""
    if not artwork_id or not artwork_id.strip():
        return None

    ident = artwork_id.strip()
    # Quotes [rekkefølge] to safely handle special character ø in column name
    sql = """
    SELECT 
        v.id,
        v.tittel,
        k.id AS kunstner_id,
        k.navn AS kunstner,
        k.fodt AS kunstner_fodt,
        k.dod AS kunstner_dod,
        k.nasjonalitet AS kunstner_nasjonalitet,
        k.kunstretning AS kunstner_kunstretning,
        k.biografi AS kunstner_biografi,
        v.aar,
        v.teknikk,
        v.dimensjoner,
        v.sal_id,
        s.navn AS sal_navn,
        s.etasje AS sal_etasje,
        v.status,
        v.tilstand,
        v.temaer,
        v.beskrivelse,
        v.veggtekst,
        v.veggtekst_status,
        v.proveniens,
        v.audioguide_manus,
        v.audioguide_status,
        v.barneformidling,
        u.id AS aktiv_utstilling_id,
        u.tittel AS aktiv_utstilling_tittel,
        uv.sal_plassering,
        uv.[rekkefølge] AS rekkefoelge
    FROM verk v
    JOIN kunstnere k ON v.kunstner_id = k.id
    LEFT JOIN saler s ON v.sal_id = s.id
    LEFT JOIN utstilling_verk uv ON v.id = uv.verk_id
    LEFT JOIN utstillinger u ON uv.utstilling_id = u.id AND u.status = 'aktiv'
    WHERE UPPER(v.id) = UPPER(:ident) OR LOWER(v.tittel) = LOWER(:ident)
    LIMIT 1
    """
    rows = execute_read_query(sql, {"ident": ident}, db_path=db_path)
    if not rows:
        return None

    d = dict(rows[0])
    d["tema"] = [t.strip() for t in d["temaer"].split(",") if t.strip()] if d.get("temaer") else []

    fodt = d.get("kunstner_fodt")
    dod = d.get("kunstner_dod")
    if fodt and dod:
        d["kunstner_levetid"] = f"{fodt}–{dod}"
    elif fodt:
        d["kunstner_levetid"] = f"f. {fodt}"
    else:
        d["kunstner_levetid"] = "ukjent"

    vegg = d.get("veggtekst")
    d["veggtekst_ordantall"] = len(vegg.split()) if vegg else 0
    return d


def query_room_artworks(
    room_id: str,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Retrieve all exhibited artworks in a given room in sequence order."""
    if not room_id or not room_id.strip():
        return []

    norm_room = normalize_room_identifier(room_id)
    raw = room_id.strip()

    # Quotes [rekkefølge] to safely handle special character ø in column name
    sql = """
    SELECT 
        v.id,
        v.tittel,
        k.navn AS kunstner,
        v.aar,
        v.teknikk,
        v.dimensjoner,
        v.sal_id,
        s.navn AS sal_navn,
        v.status,
        COALESCE(uv.sal_plassering, 'Ikke spesifisert') AS sal_plassering,
        COALESCE(uv.[rekkefølge], 0) AS rekkefoelge
    FROM verk v
    JOIN kunstnere k ON v.kunstner_id = k.id
    LEFT JOIN saler s ON v.sal_id = s.id
    LEFT JOIN utstilling_verk uv ON v.id = uv.verk_id
    WHERE (UPPER(v.sal_id) = :norm_room OR UPPER(v.sal_id) = :upper_raw OR LOWER(s.navn) LIKE :raw_lower)
      AND v.status = 'utstilt'
    ORDER BY rekkefoelge ASC, v.aar ASC
    """
    rows = execute_read_query(
        sql,
        {
            "norm_room": norm_room,
            "upper_raw": raw.upper(),
            "raw_lower": f"%{raw.lower()}%",
        },
        db_path=db_path,
    )
    return [dict(r) for r in rows]


def query_events(
    event_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 5,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Retrieve upcoming events, filtered by type or date."""
    sql = """
    SELECT 
        h.id,
        h.type,
        h.tittel,
        h.dato,
        h.klokkeslett_start,
        h.klokkeslett_slutt,
        h.sal_id,
        s.navn AS sal_navn,
        h.maks_deltakere,
        h.pris_voksen,
        h.pris_barn,
        h.beskrivelse,
        h.ansvarlig_rolle,
        h.status
    FROM hendelser h
    LEFT JOIN saler s ON h.sal_id = s.id
    WHERE h.status != 'avlyst'
    """
    params: dict[str, Any] = {}

    if date_from and date_from.strip():
        sql += " AND h.dato >= :date_from"
        params["date_from"] = date_from.strip()
    else:
        sql += " AND h.dato >= date('now')"

    if date_to and date_to.strip():
        sql += " AND h.dato <= :date_to"
        params["date_to"] = date_to.strip()

    if event_type and event_type.strip():
        t = event_type.strip().lower()
        sql += " AND (LOWER(h.type) = :type OR LOWER(h.type) LIKE :type_like OR LOWER(h.tittel) LIKE :type_like)"
        params["type"] = t
        params["type_like"] = f"%{t}%"

    sql += " ORDER BY h.dato ASC, h.klokkeslett_start ASC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 50))

    rows = execute_read_query(sql, params, db_path=db_path)
    return [dict(r) for r in rows]


# Norwegian and common English stopwords to prevent false-positive FAQ matches
FAQ_STOPWORDS: set[str] = {
    # Norwegian question words & pronouns
    "hva", "hvem", "hvor", "hvorfor", "hvordan", "hvilken", "hvilket", "hvilke",
    "jeg", "meg", "min", "mitt", "mine",
    "du", "deg", "din", "ditt", "dine",
    "han", "ham", "hans", "hun", "henne", "hennes",
    "den", "det", "dets", "dette", "disse",
    "vi", "oss", "vår", "vårt", "våre", "vaar", "vaart", "vaare",
    "dere", "deres", "de", "dem",
    "man", "seg", "sin", "sitt", "sine",
    "en", "et", "ei", "noen", "noe", "hver", "hvert",
    # Norwegian auxiliary/copula verbs & high-frequency action verbs
    "er", "var", "vært", "vaert", "være", "vaere",
    "har", "hadde", "hatt", "ha",
    "kan", "kunne", "skal", "skulle", "vil", "ville", "må", "maa", "måtte", "maatte", "bør", "boer", "burde",
    "bli", "blir", "ble", "blev", "blitt",
    "få", "faa", "får", "faar", "fikk", "fått", "faatt",
    "se", "ser", "så", "saa", "sett",
    "gjøre", "gjør", "gjoer", "gjorde", "gjort",
    "finne", "finner", "fant", "funnet",
    "gå", "gaa", "går", "gaar", "gikk", "gått", "gaatt",
    "komme", "kommer", "kom", "kommet",
    # Norwegian prepositions, conjunctions, subjunctions
    "i", "på", "paa", "til", "fra", "med", "av", "om", "for", "ved", "under", "over", "etter", "mellom", "mot", "hos", "uten",
    "og", "eller", "men", "så", "saa", "som", "at", "da", "hvis", "dersom",
    # Norwegian adverbs / conversational particles
    "ja", "nei", "jo", "ikke", "ikkje", "her", "der", "bare", "nok", "vel", "også", "ogsaa", "gjerne",
    # Generic museum environment words that appear in almost all FAQs
    "museet", "museum", "sal", "saler", "salene",
    # English conversational words from foreign tourists
    "the", "a", "an", "is", "are", "was", "were", "do", "does", "did",
    "have", "has", "had", "can", "could", "will", "would",
    "you", "your", "i", "my", "we", "our", "it", "its", "they", "them",
    "what", "where", "when", "who", "how", "why",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "about",
    "and", "or", "but", "not", "hello", "hi", "please",
}


def query_faq(
    query: str,
    category: str | None = None,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Keyword-normalized, word-boundary search for visitor FAQ."""
    if not query or not query.strip():
        return []

    raw_query = query.strip()
    words = re.findall(r"\b[\w-]+\b", raw_query.lower())
    tokens = [w for w in words if (len(w) >= 3 or w == "hc") and w not in FAQ_STOPWORDS]
    if not tokens:
        return []

    synonyms: list[str] = []
    for t in list(tokens):
        norm_t = normalize_norwegian_text(t)
        # Opening hours
        if any(k in t or k in norm_t for k in ["åpn", "aapn", "apn", "tid", "klokk", "stengt"]):
            synonyms.extend(["aapen", "åpen", "aapent", "åpent", "tid", "tider", "stengt", "tirsdag"])
        # Prices and tickets
        if any(k in t or k in norm_t for k in ["pris", "kost", "billett", "betal", "inngang", "honnør", "honnoer", "student", "gratis"]):
            synonyms.extend(["koster", "pris", "billett", "voksne", "studenter", "pensjonister", "kr", "gratis"])
        # Café / food (guarding against "mat" substring in words like "automat")
        if any(k in t or k in norm_t for k in ["kafe", "kafé", "drikk", "lunsj", "spis"]) or t in ("mat", "maten"):
            synonyms.extend(["kafé", "kafe", "museumskaféen", "lunsj"])
        # Cloakroom
        if any(k in t or k in norm_t for k in ["garderobe", "sekk", "veske", "laas", "lås", "oppbevar"]):
            synonyms.extend(["garderobe", "sekker", "vesker", "laas"])
        # Photography
        if any(k in t or k in norm_t for k in ["foto", "bilde", "kamera", "blits"]):
            synonyms.extend(["fotografere", "blits", "foto"])
        # Accessibility / stroller (guarding "hc" against substring matches in "munch")
        if any(k in t or k in norm_t for k in ["barnevogn", "vogn", "baby", "rullestol", "heis", "tilgjengelig"]) or t in ("hc", "handicap") or t.startswith("hc-"):
            synonyms.extend(["barnevogn", "heis", "universelt", "baereseler", "hc"])
        # Parking (guarding against "bil" matching inside "billett" or "bilde")
        if any(k in t or k in norm_t for k in ["parker", "parkering", "sykkel"]) or t in ("bil", "bilen", "biler", "bilparkering"):
            synonyms.extend(["parkering", "parkeringsplasser"])
        # Munch / Skrik
        if any(k in t or k in norm_t for k in ["skrik", "munch"]):
            synonyms.extend(["skrik", "edvard munch", "sal d"])
        # Shop
        if any(k in t or k in norm_t for k in ["butikk", "shop", "bok", "bøker", "boeker", "plakat"]):
            synonyms.extend(["museumsbutikken", "plakater", "kunstbøker"])
        # Audioguide (guarding "app" against "trapp")
        if any(k in t or k in norm_t for k in ["audioguide", "lydguide"]) or t in ("guide", "guiden", "app", "appen", "apper"):
            synonyms.extend(["audioguide", "app"])

    search_terms = list(dict.fromkeys(tokens + synonyms))

    sql = "SELECT id, spoersmaal, svar, kategori, hyppighet, sist_stilt FROM publikum_faq"
    params: dict[str, Any] = {}
    if category and category.strip():
        sql += " WHERE LOWER(kategori) = :category"
        params["category"] = category.strip().lower()

    rows = execute_read_query(sql, params, db_path=db_path)

    scored_results = []
    norm_raw_query = normalize_norwegian_text(raw_query)

    for r in rows:
        d = dict(r)
        q_text = d["spoersmaal"].lower()
        a_text = d["svar"].lower()
        c_text = (d.get("kategori") or "").lower()
        norm_q = normalize_norwegian_text(q_text)
        norm_a = normalize_norwegian_text(a_text)

        score = 0
        if len(raw_query) >= 4 and (raw_query.lower() in q_text or norm_raw_query in norm_q):
            score += 20

        for term in search_terms:
            norm_term = normalize_norwegian_text(term)
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            norm_pattern = re.compile(rf"\b{re.escape(norm_term)}\b", re.IGNORECASE)

            if pattern.search(q_text) or norm_pattern.search(norm_q):
                score += 5
            elif pattern.search(a_text) or norm_pattern.search(norm_a):
                score += 3
            elif c_text and (term == c_text or norm_term == c_text):
                score += 2

        if score > 0:
            scored_results.append((score, d.get("hyppighet", 0), d))

    scored_results.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [item[2] for item in scored_results]
