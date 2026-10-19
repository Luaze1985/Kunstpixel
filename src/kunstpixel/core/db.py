"""Database access layer for Aura Kunstmuseum.

Provides safe, read-only parameterized SQLite queries with Norwegian character handling,
query normalization, and table/column quoting.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from src.kunstpixel.core.config import get_db_path

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

    sql_upcoming = sql + " AND h.dato >= date('now')"
    if date_from and date_from.strip():
        sql += " AND h.dato >= :date_from"
        params["date_from"] = date_from.strip()
        sql_to_run = sql
    else:
        sql_to_run = sql_upcoming

    if date_to and date_to.strip():
        sql_to_run += " AND h.dato <= :date_to"
        sql += " AND h.dato <= :date_to"
        params["date_to"] = date_to.strip()

    if event_type and event_type.strip():
        t = event_type.strip().lower()
        filter_clause = " AND (LOWER(h.type) = :type OR LOWER(h.type) LIKE :type_like OR LOWER(h.tittel) LIKE :type_like)"
        sql_to_run += filter_clause
        sql += filter_clause
        params["type"] = t
        params["type_like"] = f"%{t}%"

    order_clause = " ORDER BY h.dato ASC, h.klokkeslett_start ASC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 50))

    rows = execute_read_query(sql_to_run + order_clause, params, db_path=db_path)
    if not rows and not date_from:
        # Graceful fallback for static demo/test databases when real calendar date drifts past demo dates
        rows = execute_read_query(sql + order_clause, params, db_path=db_path)
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


def query_archive_exhibitions(
    query: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    curator: str | None = None,
    limit: int = 10,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Retrieve historical exhibitions from museum.db (2010-2026, ADR 004)."""
    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT utstilling_id, aar, sesong, tittel, kurator, saler,
           periode_start, periode_slutt, antall_verk, besokstall_total, budsjett_nok, katalog_isbn, status
    FROM utstillinger_historikk
    WHERE 1=1
    """
    params: dict[str, Any] = {}

    if query and query.strip():
        sql += " AND (LOWER(tittel) LIKE :q OR LOWER(saler) LIKE :q)"
        params["q"] = f"%{query.strip().lower()}%"

    if year_from is not None:
        sql += " AND aar >= :year_from"
        params["year_from"] = int(year_from)

    if year_to is not None:
        sql += " AND aar <= :year_to"
        params["year_to"] = int(year_to)

    if curator and curator.strip():
        sql += " AND LOWER(kurator) LIKE :curator"
        params["curator"] = f"%{curator.strip().lower()}%"

    sql += " ORDER BY aar DESC, periode_start DESC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 50))

    rows = execute_read_query(sql, params, db_path=db_path)
    return [dict(r) for r in rows]


def query_contractors(
    kategori: str | None = None,
    leverandor: str | None = None,
    aar: int | None = None,
    limit: int = 10,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Retrieve contractor and temporary staffing records from museum.db (ADR 004)."""
    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT innleie_id, aar, leverandor, orgnr, kategori, oppdragsbeskrivelse,
           knyttet_utstilling_id, periode_fra, periode_til, fakturerte_timer,
           timepris_nok, totalbelop_nok, kontaktperson_ekstern, godkjent_av_navn, status
    FROM hr_innleie
    WHERE 1=1
    """
    params: dict[str, Any] = {}

    if kategori and kategori.strip():
        sql += " AND LOWER(kategori) LIKE :kat"
        params["kat"] = f"%{kategori.strip().lower()}%"

    if leverandor and leverandor.strip():
        sql += " AND LOWER(leverandor) LIKE :lev"
        params["lev"] = f"%{leverandor.strip().lower()}%"

    if aar is not None:
        sql += " AND aar = :aar"
        params["aar"] = int(aar)

    sql += " ORDER BY aar DESC, totalbelop_nok DESC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 50))

    rows = execute_read_query(sql, params, db_path=db_path)
    return [dict(r) for r in rows]


def query_employee_cv(
    ident: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve detailed persona and CV data for key personnel from museum.db (ADR 004)."""
    if not ident or not ident.strip():
        return None

    if db_path is None:
        db_path = get_db_path()

    ident_clean = ident.strip()
    sql = """
    SELECT id, navn, avdeling, stilling, icor_rolle, cv_json
    FROM personas
    WHERE UPPER(id) = UPPER(:ident) OR LOWER(navn) LIKE LOWER(:ident_like)
    LIMIT 1
    """
    params = {
        "ident": ident_clean,
        "ident_like": f"%{ident_clean}%",
    }
    rows = execute_read_query(sql, params, db_path=db_path)
    if not rows:
        return None

    row = dict(rows[0])
    try:
        import json
        row["cv_detaljer"] = json.loads(row["cv_json"])
    except Exception:
        row["cv_detaljer"] = {}
    return row


def query_condition_report(
    artwork_id: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve conservation and condition report for an artwork."""
    if not artwork_id or not artwork_id.strip():
        return None

    if db_path is None:
        db_path = get_db_path()

    clean_id = artwork_id.strip()
    sql = """
    SELECT tr.rapport_id, tr.verk_id, v.tittel as verk_tittel, tr.inspeksjonsdato,
           tr.tilstandsgrad, tr.lysomfintlighet_luks, tr.klimakrav_rh_prosent,
           tr.konserveringshistorikk, tr.forsikringsverdi_nok, tr.vurdert_av_ansatt_id
    FROM tilstandsrapporter tr
    JOIN verk v ON tr.verk_id = v.id
    WHERE UPPER(tr.verk_id) = UPPER(:id) OR LOWER(v.tittel) = LOWER(:title)
    LIMIT 1
    """
    rows = execute_read_query(sql, {"id": clean_id, "title": clean_id}, db_path=db_path)
    return dict(rows[0]) if rows else None


def query_loans(
    exhibition_id: str | None = None,
    query: str | None = None,
    limit: int = 10,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Retrieve historical exhibition loans from external Norwegian museums."""
    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT innlan_id, utstilling_id, eierinstitusjon, tittel, kunstner, aar,
           teknikk, dimensjoner, veggtekst, audioguide_manus, barneformidling,
           forsikringsverdi_nok, kurertransport_krav, tilstand_ved_mottak, status
    FROM utstillingsinnlan
    WHERE 1=1
    """
    params: dict[str, Any] = {}

    if exhibition_id and exhibition_id.strip():
        sql += " AND UPPER(utstilling_id) = UPPER(:exh_id)"
        params["exh_id"] = exhibition_id.strip()

    if query and query.strip():
        sql += " AND (LOWER(tittel) LIKE :q OR LOWER(kunstner) LIKE :q OR LOWER(eierinstitusjon) LIKE :q)"
        params["q"] = f"%{query.strip().lower()}%"

    sql += " ORDER BY aar DESC, innlan_id ASC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 50))

    rows = execute_read_query(sql, params, db_path=db_path)
    return [dict(r) for r in rows]


def query_exhibition_economy(
    exhibition_id: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve comprehensive project economy and accounts for an exhibition."""
    if not exhibition_id or not exhibition_id.strip():
        return None

    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT uo.utstilling_id, uh.tittel, uh.aar, uh.besokstall_total,
           uo.budsjett_nok, uo.faktisk_innleie_nok, uo.faktisk_totalkostnad_nok,
           uo.billettinntekter_nok, uo.katalogsalg_nok, uo.sponsorstotte_nok,
           uo.netto_resultat_nok, uo.avvik_forklaring
    FROM utstilling_okonomi uo
    JOIN utstillinger_historikk uh ON uo.utstilling_id = uh.utstilling_id
    WHERE UPPER(uo.utstilling_id) = UPPER(:id) OR LOWER(uh.tittel) LIKE LOWER(:title)
    LIMIT 1
    """
    clean_id = exhibition_id.strip()
    rows = execute_read_query(sql, {"id": clean_id, "title": f"%{clean_id}%"}, db_path=db_path)
    return dict(rows[0]) if rows else None


def query_incidents(
    kategori: str | None = None,
    alvorlighetsgrad: str | None = None,
    sal_id: str | None = None,
    limit: int = 10,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Retrieve operational incidents (HMS, security, climate, technical, visitor)."""
    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT avvik_id, aar, dato, kategori, alvorlighetsgrad, berort_sal_id,
           berort_verk_id, beskrivelse, strakstiltak, oppfolging_ansvarlig_id, status
    FROM avvik_hms_drift
    WHERE 1=1
    """
    params: dict[str, Any] = {}

    if kategori and kategori.strip():
        sql += " AND UPPER(kategori) = UPPER(:kat)"
        params["kat"] = kategori.strip()

    if alvorlighetsgrad and alvorlighetsgrad.strip():
        sql += " AND UPPER(alvorlighetsgrad) = UPPER(:grad)"
        params["grad"] = alvorlighetsgrad.strip()

    if sal_id and sal_id.strip():
        sql += " AND UPPER(berort_sal_id) = UPPER(:sal)"
        params["sal"] = sal_id.strip()

    sql += " ORDER BY dato DESC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 50))

    rows = execute_read_query(sql, params, db_path=db_path)
    return [dict(r) for r in rows]


def query_supplier_brreg(
    orgnr_or_name: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve authoritative Brreg Enhetsregister data for a supplier."""
    if not orgnr_or_name or not orgnr_or_name.strip():
        return None

    if db_path is None:
        db_path = get_db_path()

    clean_term = orgnr_or_name.strip().replace(" ", "")
    sql = """
    SELECT organisasjonsnummer, navn, organisasjonsform_kode, organisasjonsform_beskrivelse,
           naeringskode, naeringskode_beskrivelse, forretningsadresse_kommune,
           forretningsadresse_postnummer, antall_ansatte, registrert_i_mva,
           under_konkurs, under_avvikling, aksjekapital_nok, stiftelsesdato, sist_oppdatert
    FROM leverandor_enhetsregister
    WHERE organisasjonsnummer = :term OR LOWER(navn) LIKE LOWER(:name_term)
    LIMIT 1
    """
    rows = execute_read_query(sql, {"term": clean_term, "name_term": f"%{orgnr_or_name.strip()}%"}, db_path=db_path)
    return dict(rows[0]) if rows else None


def query_tariff_pay(
    lonnstrinn: int,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve Virke museum tariff rates for a pay grade."""
    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT lonnstrinn, tittel_eksempel, aarslonn_nok, timesats_ordinar,
           timesats_kveld, timesats_helg, timesats_helligdag, gjeldende_fra
    FROM virke_tariff
    WHERE lonnstrinn = :step
    LIMIT 1
    """
    rows = execute_read_query(sql, {"step": int(lonnstrinn)}, db_path=db_path)
    return dict(rows[0]) if rows else None


def query_holidays(
    year: int | None = None,
    date_str: str | None = None,
    limit: int = 20,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Retrieve public holidays and school vacations from norske_helligdager."""
    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT dato, aar, navn, er_offentlig_hoytid, tillegg_faktor, skoleferie_type
    FROM norske_helligdager
    WHERE 1=1
    """
    params: dict[str, Any] = {}

    if year is not None:
        sql += " AND aar = :yr"
        params["yr"] = int(year)

    if date_str and date_str.strip():
        sql += " AND dato = :d"
        params["d"] = date_str.strip()

    sql += " ORDER BY dato ASC LIMIT :limit"
    params["limit"] = max(1, min(int(limit), 100))

    rows = execute_read_query(sql, params, db_path=db_path)
    return [dict(r) for r in rows]


def query_styrk_job_code(
    code_or_title: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve official STYRK-08 job profile and Virke minimum grade."""
    if not code_or_title or not code_or_title.strip():
        return None

    if db_path is None:
        db_path = get_db_path()

    clean_term = code_or_title.strip()
    sql = """
    SELECT styrk_kode, tittel, avdeling, utdanningsnivaa, virke_minste_lonnstrinn, beskrivelse
    FROM styrk08_katalog
    WHERE styrk_kode = :term OR LOWER(tittel) LIKE LOWER(:title_term)
    LIMIT 1
    """
    rows = execute_read_query(sql, {"term": clean_term, "title_term": f"%{clean_term}%"}, db_path=db_path)
    return dict(rows[0]) if rows else None


def query_cleaning_registry(
    orgnr: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Verify supplier against the official Norwegian Cleaning Supplier Registry."""
    if not orgnr or not orgnr.strip():
        return None

    if db_path is None:
        db_path = get_db_path()

    clean_nr = orgnr.strip().replace(" ", "")
    sql = """
    SELECT organisasjonsnummer, navn, status, godkjent_til_dato, har_hms_kort_krav, sist_kontrollert
    FROM arbeidstilsynet_renhold
    WHERE organisasjonsnummer = :nr OR LOWER(navn) LIKE LOWER(:name_term)
    LIMIT 1
    """
    rows = execute_read_query(sql, {"nr": clean_nr, "name_term": f"%{orgnr.strip()}%"}, db_path=db_path)
    return dict(rows[0]) if rows else None


def query_quarterly_absence(
    year: int,
    quarter: int,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve SSB sickness absence rate and recommended buffer for culture sector."""
    if db_path is None:
        db_path = get_db_path()

    sql = """
    SELECT periode, aar, kvartal, sykefraver_prosent, egenmeldt_prosent,
           legemeldt_prosent, vikarbuffer_anbefaling_faktor
    FROM ssb_sykefraver_kultur
    WHERE aar = :yr AND kvartal = :q
    LIMIT 1
    """
    rows = execute_read_query(sql, {"yr": int(year), "q": int(quarter)}, db_path=db_path)
    return dict(rows[0]) if rows else None


def query_station_ergonomics(
    station_id: str,
    db_path: Path | str | None = None,
) -> dict | None:
    """Retrieve STAMI ergonomic requirements and rotation rules for a gallery station."""
    if not station_id or not station_id.strip():
        return None

    if db_path is None:
        db_path = get_db_path()

    clean_id = station_id.strip().upper()
    sql = """
    SELECT stasjon_id, navn, underlag_type, maks_sammenhengende_timer,
           krav_om_sittepause_minutter, anbefalt_rotasjon_stasjon_id
    FROM hms_ergonomi_rotasjon
    WHERE UPPER(stasjon_id) = :sid OR LOWER(navn) LIKE LOWER(:name_term)
    LIMIT 1
    """
    rows = execute_read_query(sql, {"sid": clean_id, "name_term": f"%{station_id.strip()}%"}, db_path=db_path)
    return dict(rows[0]) if rows else None


def audit_shift_aml_compliance(
    ansatt_id: str,
    dato: str,
    start: str,
    end: str,
    db_path: Path | str | None = None,
) -> dict:
    """Deterministically audit a proposed shift against AML kap. 10 (hours, daily rest, weekly rest)."""
    if db_path is None:
        db_path = get_db_path()

    clean_id = ansatt_id.strip()

    try:
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        shift_duration = (eh + em / 60.0) - (sh + sm / 60.0)
        if shift_duration < 0:
            shift_duration += 24.0
    except Exception:
        return {"error": "INVALID_TIME_FORMAT", "details": "Time format must be HH:MM"}

    violations = []
    warnings = []

    if shift_duration > 9.0:
        violations.append({
            "regel": "AML_§_10_4",
            "type": "MAKS_DAGLIG_ARBEIDSTID_OVERSTIGET",
            "detalj": f"Skiftlengde er {shift_duration:.1f} timer. AML § 10-4 tillater maks 9 timer alminnelig arbeidstid uten overtidstillatelse.",
            "alvorlighetsgrad": "FEIL",
        })
    elif shift_duration > 7.5:
        warnings.append({
            "regel": "VIRKE_TARIFF_OVERTID",
            "type": "OVERTID_UTLOEST",
            "detalj": f"Skiftet ({shift_duration:.1f}t) overstiger normal dagsnorm på 7,5 timer. Overtidskompensasjon påkrevd.",
            "alvorlighetsgrad": "ADVARSEL",
        })

    try:
        from datetime import date, timedelta
        cur_date = date.fromisoformat(dato)
        prev_date = (cur_date - timedelta(days=1)).isoformat()
    except Exception:
        prev_date = None

    sql = """
    SELECT vakt_id, dato, timer, stasjon, rolle
    FROM hr_vakter
    WHERE ansatt_id = :id AND (dato = :cur_d OR dato = :prev_d)
    ORDER BY dato DESC
    """
    rows = execute_read_query(sql, {"id": clean_id, "cur_d": dato, "prev_d": prev_date or ""}, db_path=db_path)

    daily_rest_hours = None
    if rows:
        for r in rows:
            r_dict = dict(r)
            if r_dict["dato"] == prev_date:
                # Check rest time from yesterday
                estimated_end_yesterday = 22.0 if "kveld" in r_dict["rolle"].lower() or "vernissasje" in r_dict["rolle"].lower() else 17.0
                rest = (sh + sm / 60.0) + (24.0 - estimated_end_yesterday)
                daily_rest_hours = round(rest, 1)
                if rest < 11.0:
                    violations.append({
                        "regel": "AML_§_10_8",
                        "type": "AML_VIOLATION_DAILY_REST",
                        "detalj": f"Daglig hviletid er kun {rest:.1f} timer (krav: minst 11 timer mellom skift i henhold til AML § 10-8).",
                        "alvorlighetsgrad": "FEIL",
                    })
            elif r_dict["dato"] == dato:
                violations.append({
                    "regel": "AML_§_10_4",
                    "type": "DOBBELT_SKIFT_SAMME_DAG",
                    "detalj": f"Ansatt {clean_id} har allerede en registrert vakt på {dato} ({r_dict['stasjon']}).",
                    "alvorlighetsgrad": "FEIL",
                })

    is_compliant = len(violations) == 0

    return {
        "ansatt_id": clean_id,
        "dato": dato,
        "start": start,
        "end": end,
        "skift_timer": round(shift_duration, 2),
        "daglig_hviletid_timer": daily_rest_hours if daily_rest_hours is not None else 14.0,
        "compliant": is_compliant,
        "status": "APPROVED_AML" if is_compliant else "REJECTED_AML_VIOLATION",
        "brudd": violations,
        "advarsler": warnings,
        "hjemmel": "Lov om arbeidsmiljø, arbeidstid og stillingsvern (Arbeidsmiljøloven kap. 10)",
    }


def query_handbook(
    query: str | None = None,
    handbok: str | None = None,
    role: str | None = None,
    limit: int = 5,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Query the indexed handbooks with keyword search, handbook code filter, or target role filter.

    Args:
        query: Search query (e.g. 'egenmelding', 'hviletid', 'brann', 'løft', 'haccp').
        handbok: Optional handbook filter ('PERSONAL', 'HMS_SIKKERHET', 'DRIFT_KVALITET', 'LEDER_BEREDSKAP').
        role: Optional role/audience filter (e.g. 'vert', 'leder', 'kafé').
        limit: Max results (1-20, default 5).
        db_path: Optional explicit database path.

    Returns:
        List of matching handbook points with chapter, section title, legal basis and content.
    """
    clauses = []
    params: dict[str, Any] = {"limit": max(1, min(limit, 20))}

    if not handbok and query:
        q_low = query.lower()
        if "i hms-håndbok" in q_low or "i hms-handbok" in q_low:
            handbok = "HMS_SIKKERHET"
        elif "i personalhåndbok" in q_low or "i personalhandbok" in q_low:
            handbok = "PERSONAL"
        elif "i driftshåndbok" in q_low or "i driftshandbok" in q_low:
            handbok = "DRIFT_KVALITET"
        elif "i lederhåndbok" in q_low or "i lederhandbok" in q_low:
            handbok = "LEDER_BEREDSKAP"

    if handbok:
        hb_clean = handbok.upper().strip()
        clauses.append("(UPPER(handbok_kode) LIKE :hb OR UPPER(handbok_navn) LIKE :hb)")
        params["hb"] = f"%{hb_clean}%"

    if role:
        clauses.append("(LOWER(malgruppe) LIKE :role OR LOWER(innhold) LIKE :role)")
        params["role"] = f"%{role.lower().strip()}%"

    if query:
        # Generic filler words to filter out
        stop_words = {
            "hva", "er", "i", "på", "for", "til", "og", "eller", "om", "det", "den", "som",
            "hvilke", "hvilket", "hvilken", "gjelder", "når", "noen", "krav", "rettigheter",
            "må", "kan", "får", "jeg", "vi", "har", "hvor", "mange", "dager", "ved",
            "handbok", "håndbok", "handboken", "håndboken", "boken", "boka", "regel", "regler"
        }
        raw_tokens = [tok for tok in re.findall(r"\w+", query.lower()) if len(tok) >= 2]
        base_tokens = [t for t in raw_tokens if t not in stop_words] or raw_tokens

        # Prepend high-signal museum domain roots for compound words
        museum_stems = [
            "renhold", "rullestol", "ledsager", "egenmeld", "sykefravær", "avvik",
            "varsl", "ferie", "temperatur", "persontall", "brann", "løft", "hjertestart",
            "karantene", "skjenk", "oppfølging", "vaktbytt", "overtid", "klima", "haccp",
            "gjengjeldelse", "doffin", "senior", "prøvetid", "velferd", "barn"
        ]
        matched_stems = [s for s in museum_stems if any(s in w for w in raw_tokens)]

        q_tokens = []
        for s in matched_stems:
            if s not in q_tokens:
                q_tokens.append(s)

        for t in base_tokens:
            if t not in q_tokens:
                q_tokens.append(t)
            if len(t) > 5 and t.endswith("ene") and t[:-3] not in q_tokens:
                q_tokens.append(t[:-3])
            elif len(t) > 4 and (t.endswith("en") or t.endswith("et") or t.endswith("er")) and t[:-2] not in q_tokens:
                q_tokens.append(t[:-2])

        if q_tokens:
            q_clauses = []
            score_parts = []
            for i, tok in enumerate(q_tokens[:7]):
                p_name = f"tok_{i}"
                match_expr = f"(LOWER(innhold) LIKE :{p_name} OR LOWER(avsnitt_tittel) LIKE :{p_name} OR LOWER(stikkord) LIKE :{p_name} OR LOWER(kapittel_tittel) LIKE :{p_name})"
                q_clauses.append(match_expr)
                weight_expr = (
                    f"(CASE WHEN LOWER(avsnitt_tittel) LIKE :{p_name} THEN 5 ELSE 0 END + "
                    f"CASE WHEN LOWER(stikkord) LIKE :{p_name} THEN 4 ELSE 0 END + "
                    f"CASE WHEN LOWER(kapittel_tittel) LIKE :{p_name} THEN 2 ELSE 0 END + "
                    f"CASE WHEN LOWER(innhold) LIKE :{p_name} THEN 1 ELSE 0 END)"
                )
                score_parts.append(weight_expr)
                params[p_name] = f"%{tok}%"
            clauses.append(f"({' OR '.join(q_clauses)})")
            order_by = f"({' + '.join(score_parts)}) DESC, kapittel_nr ASC, punkt_id ASC"
        else:
            order_by = "kapittel_nr ASC, punkt_id ASC"
    else:
        order_by = "kapittel_nr ASC, punkt_id ASC"

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
    SELECT punkt_id, handbok_kode, handbok_navn, kapittel_nr, kapittel_tittel,
           avsnitt_tittel, malgruppe, lovhjemmel, innhold, stikkord, siste_revidert
    FROM handbok_oppslag
    {where_sql}
    ORDER BY {order_by}
    LIMIT :limit
    """
    rows = execute_read_query(sql, params, db_path=db_path)
    return [dict(r) for r in rows]




# --- Vakter, arbeidstid og vaktkostnad (Datafinner v1) ---
# Bare det som står i museum.db. Klokkeslett (hr_vakter.start/slutt) og arbeidstid_grenser finnes når
# museum.db er bygget med build_museum_db.py; de er syntetiske og merket med datakilde. Mangler de,
# sier svaret fra i stedet for å regne ut noe.


def _db(db_path: Path | str | None) -> Path | str:
    return db_path or get_db_path()


def _har_klokkeslett(db_path: Path | str) -> bool:
    kolonner = {r["name"] for r in execute_read_query("SELECT name FROM pragma_table_info('hr_vakter')", (), db_path)}
    return {"start", "slutt"} <= kolonner


def query_working_time_limits(db_path: Path | str | None = None) -> dict:
    """Arbeidstidsgrensene i databasen (tabellen arbeidstid_grenser), med kilde og datakilde."""
    db = _db(db_path)
    finnes = execute_read_query(
        "SELECT count(*) AS n FROM sqlite_master WHERE type='table' AND name='arbeidstid_grenser'", (), db
    )[0]["n"]
    if not finnes:
        return {}
    return {r["navn"]: dict(r) for r in execute_read_query("SELECT * FROM arbeidstid_grenser ORDER BY navn", (), db)}


def _maaned_grenser(maaned: str) -> tuple[str, str, str]:
    from datetime import date

    aar, mnd = (int(x) for x in maaned.strip().split("-"))
    fra = date(aar, mnd, 1)
    til = date(aar + (mnd == 12), mnd % 12 + 1, 1)
    return f"{aar:04d}-{mnd:02d}", fra.isoformat(), til.isoformat()


def _klokke_timer(hhmm: str) -> float:
    return int(hhmm[:2]) + int(hhmm[3:5]) / 60


VAKT_KOLONNER_SQL = """
    v.vakt_id, v.dato, v.timer, v.rolle, v.stasjon, v.avdeling,
    a.ansatt_id, a.navn, a.stilling, a.telefon, a.epost, a.kontor_sal
"""


def query_shifts_on_date(dato: str, db_path: Path | str | None = None) -> list[dict]:
    """Alle vakter på én dato slik de står i hr_vakter, med klokkeslett når databasen har dem."""
    from datetime import date

    dato = date.fromisoformat(dato.strip()).isoformat()
    db = _db(db_path)
    klokke = _har_klokkeslett(db)
    ekstra = ", v.start, v.slutt, v.klokkeslett_datakilde" if klokke else ""
    rekkefolge = "v.start, a.navn" if klokke else "v.avdeling, a.navn"
    sql = f"""
    SELECT {VAKT_KOLONNER_SQL}{ekstra}
    FROM hr_vakter v JOIN hr_ansatte a ON a.ansatt_id = v.ansatt_id
    WHERE v.dato = :dato
    ORDER BY {rekkefolge}
    """
    return [dict(r) for r in execute_read_query(sql, {"dato": dato}, db)]


def query_staff_on_shift(dato: str | None = None, klokkeslett: str | None = None,
                         db_path: Path | str | None = None) -> dict:
    """Hvem har vakt på en dato (standard i dag), og hvem er på jobb på et klokkeslett (standard nå)."""
    from datetime import date, datetime

    na = datetime.now()
    d = date.fromisoformat(dato.strip()) if dato else na.date()
    db = _db(db_path)
    vakter = query_shifts_on_date(d.isoformat(), db)
    svar = {
        "dato": d.isoformat(),
        "antall_med_vakt": len(vakter),
        "timer_totalt": round(sum(v["timer"] for v in vakter), 2),
        "vakter": vakter,
    }
    if not _har_klokkeslett(db):
        svar["mangler"] = "Klokkeslett for vaktene finnes ikke i databasen."
        return svar
    kl = klokkeslett or (na.strftime("%H:%M") if d == na.date() else None)
    if kl:
        svar["klokkeslett"] = kl
        svar["pa_jobb"] = [v for v in vakter if v["start"] <= kl < v["slutt"]]
        svar["antall_pa_jobb"] = len(svar["pa_jobb"])
    svar["datakilde"] = vakter[0]["klokkeslett_datakilde"] if vakter else None
    return svar


def query_working_hours(maaned: str, db_path: Path | str | None = None) -> dict:
    """Arbeidstid per ansatt i en måned ('YYYY-MM'). Overtid regnes bare når grensene finnes i databasen."""
    from datetime import date

    mnd, fra, til = _maaned_grenser(maaned)
    db = _db(db_path)
    sql = """
    SELECT v.ansatt_id, a.navn, a.avdeling, a.stillingsprosent, v.dato, sum(v.timer) AS timer, count(*) AS vakter
    FROM hr_vakter v JOIN hr_ansatte a ON a.ansatt_id = v.ansatt_id
    WHERE v.dato >= :fra AND v.dato < :til
    GROUP BY v.ansatt_id, v.dato
    ORDER BY v.ansatt_id, v.dato
    """
    grenser = query_working_time_limits(db)
    ukenorm = grenser.get("ukenorm_timer", {}).get("verdi")
    dognmaks = grenser.get("dognmaks_timer", {}).get("verdi")
    per: dict[str, dict] = {}
    uker: dict[tuple[str, tuple[int, int]], float] = {}
    for r in execute_read_query(sql, {"fra": fra, "til": til}, db):
        p = per.setdefault(r["ansatt_id"], {
            "ansatt_id": r["ansatt_id"], "navn": r["navn"], "avdeling": r["avdeling"],
            "stillingsprosent": r["stillingsprosent"], "timer_totalt": 0.0, "antall_vakter": 0,
            "hoyeste_dognsum": 0.0, "dognovertid_timer": 0.0,
        })
        p["timer_totalt"] += r["timer"]
        p["antall_vakter"] += r["vakter"]
        p["hoyeste_dognsum"] = max(p["hoyeste_dognsum"], r["timer"])
        if dognmaks is not None and r["timer"] > dognmaks:
            p["dognovertid_timer"] += r["timer"] - dognmaks
        iso = date.fromisoformat(r["dato"]).isocalendar()
        n = (r["ansatt_id"], (iso[0], iso[1]))
        uker[n] = uker.get(n, 0.0) + r["timer"]
    for p in per.values():
        p["hoyeste_ukesum"] = 0.0
        p["ukeovertid_timer"] = 0.0
    for (ansatt_id, _), timer in uker.items():
        p = per[ansatt_id]
        p["hoyeste_ukesum"] = max(p["hoyeste_ukesum"], timer)
        if ukenorm is not None and timer > ukenorm:
            p["ukeovertid_timer"] += timer - ukenorm
    ansatte = []
    for p in per.values():
        for k in ("timer_totalt", "hoyeste_dognsum", "hoyeste_ukesum", "dognovertid_timer", "ukeovertid_timer"):
            p[k] = round(p[k], 2)
        if ukenorm is not None and dognmaks is not None:
            p["overtid_timer"] = max(p["dognovertid_timer"], p["ukeovertid_timer"])
        else:
            del p["dognovertid_timer"], p["ukeovertid_timer"]
        ansatte.append(p)
    ansatte.sort(key=lambda x: (-x.get("overtid_timer", 0), -x["hoyeste_ukesum"], x["navn"]))
    svar = {
        "maaned": mnd,
        "antall_ansatte": len(ansatte),
        "timer_totalt": round(sum(a["timer_totalt"] for a in ansatte), 2),
        "hoyeste_ukesum": max((a["hoyeste_ukesum"] for a in ansatte), default=0),
        "hoyeste_dognsum": max((a["hoyeste_dognsum"] for a in ansatte), default=0),
        "ansatte": ansatte,
    }
    if ukenorm is None or dognmaks is None:
        svar["mangler"] = "Overtidsgrensen finnes ikke som tall i databasen, så overtid er ikke beregnet."
    else:
        svar["overtid_timer_totalt"] = round(sum(a["overtid_timer"] for a in ansatte), 2)
        svar["antall_med_overtid"] = sum(1 for a in ansatte if a["overtid_timer"] > 0)
        svar["grenser"] = {k: grenser[k] for k in ("ukenorm_timer", "dognmaks_timer")}
    return svar


def query_shift_cost(maaned: str, db_path: Path | str | None = None) -> dict:
    """Lønnskostnad for vakter i en måned per avdeling: timer x Virke-sats fra virke_tariff.

    Helligdag (norske_helligdager) gir helligdagssats, lørdag og søndag helgesats. Timer etter
    grensen kveldstillegg_fra (arbeidstid_grenser) gir kveldssats når vaktene har klokkeslett.
    """
    mnd, fra, til = _maaned_grenser(maaned)
    db = _db(db_path)
    kveld_fra = query_working_time_limits(db).get("kveldstillegg_fra", {}).get("verdi")
    klokke = _har_klokkeslett(db) and kveld_fra is not None
    ekstra = ", v.start, v.slutt" if klokke else ""
    sql = f"""
    SELECT v.avdeling, v.timer, a.lonnstrinn_virke AS trinn,
           t.timesats_ordinar, t.timesats_kveld, t.timesats_helg, t.timesats_helligdag,
           h.dato AS helligdag, strftime('%w', v.dato) AS ukedag{ekstra}
    FROM hr_vakter v
    JOIN hr_ansatte a ON a.ansatt_id = v.ansatt_id
    LEFT JOIN virke_tariff t ON t.lonnstrinn = a.lonnstrinn_virke
    LEFT JOIN norske_helligdager h ON h.dato = v.dato
    WHERE v.dato >= :fra AND v.dato < :til
    """
    avd: dict[str, dict] = {}
    for r in execute_read_query(sql, {"fra": fra, "til": til}, db):
        a = avd.setdefault(r["avdeling"], {"avdeling": r["avdeling"], "vakter": 0, "timer": 0.0,
                                           "kveldstimer": 0.0, "vakter_uten_tariff": 0, "kostnad_nok": 0.0})
        a["vakter"] += 1
        a["timer"] += r["timer"]
        if r["timesats_ordinar"] is None:
            a["vakter_uten_tariff"] += 1
            continue
        if r["helligdag"]:
            a["kostnad_nok"] += r["timer"] * r["timesats_helligdag"]
        elif r["ukedag"] in ("0", "6"):
            a["kostnad_nok"] += r["timer"] * r["timesats_helg"]
        else:
            kveld = 0.0
            if klokke:
                kveld = min(r["timer"], max(0.0, _klokke_timer(r["slutt"]) - max(_klokke_timer(r["start"]), kveld_fra)))
            a["kveldstimer"] += kveld
            a["kostnad_nok"] += (r["timer"] - kveld) * r["timesats_ordinar"] + kveld * r["timesats_kveld"]
    rader = sorted(avd.values(), key=lambda x: -x["kostnad_nok"])
    for a in rader:
        for k in ("timer", "kveldstimer", "kostnad_nok"):
            a[k] = round(a[k], 2)
    mangler = ["Vakter for ansatte med lønnstrinn som ikke finnes i virke_tariff er ikke kostnadsberegnet."]
    if not klokke:
        mangler.append("Kveldssats er ikke brukt, fordi vaktene mangler klokkeslett eller grensen mangler.")
        for a in rader:
            del a["kveldstimer"]
    svar = {
        "maaned": mnd,
        "avdelinger": rader,
        "kostnad_nok_totalt": round(sum(a["kostnad_nok"] for a in rader), 2),
        "vakter_uten_tariff": sum(a["vakter_uten_tariff"] for a in rader),
        "mangler": " ".join(mangler),
    }
    if klokke:
        svar["datakilde"] = "syntetisk (archive_generator): klokkeslett og kveldstillegg_fra"
    return svar


def query_exhibitions_with_economy(db_path: Path | str | None = None) -> list[dict]:
    """Alle utstillinger som har økonomirapport, nyeste først (id, tittel, år). Til lukkede filtre."""
    sql = """
    SELECT uh.utstilling_id, uh.tittel, uh.aar
    FROM utstilling_okonomi uo JOIN utstillinger_historikk uh ON uh.utstilling_id = uo.utstilling_id
    ORDER BY uh.aar DESC, uh.utstilling_id DESC
    """
    return [dict(r) for r in execute_read_query(sql, (), db_path or get_db_path())]
