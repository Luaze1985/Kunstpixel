"""Kunstpixel — Datafinner.

Lokal side der gründerne velger hva de vil finne i museum.db og får svaret
fra de samme fem MCP-verktøyene som LLM-en bruker. Siden viser også selve
verktøykallet, slik at man ser nøyaktig hvordan LLM-en ville spurt.

Serveren bindes til 127.0.0.1 som standard. Ved hosting settes vertsadressen
av driftsoppsettet, som inntil videre krever innlogging i Caddy.

100 % standardbibliotek for webdelen. Databasen åpnes skrivebeskyttet via
src.kunstpixel.core.db (mode=ro), og bare verktøyene i VERKTOY kan kalles.

Kjøres med:
    py -3.13 src/kunstpixel/adapters/datafinner.py

Åpnes på http://127.0.0.1:8010

Hosting:
    DATAFINNER_HOST=0.0.0.0    lytter på alle adresser (bak omvendt proxy)
    KUNSTPIXEL_DB_PATH=<sti>   databasen som skal brukes
Serveren har ingen innlogging selv. Den skal alltid ligge bak noe som krever det.

Åpent API (se docs/DATAFINNER_API.md):
    GET  /api/verktoyskjema    verktøyene med parametere (JSON Schema), klare for en språkmodell
    GET  /api/rapport          deterministisk rapport: fakta + vurdering/forslag fra faste regler
    GET  /api/status           hva som er slått på (KI-lag)
    POST /api/forklar          valgfritt: KI forklarer rapporten, merket AI-forslag (av som standard)
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.adapters import datafinner_api
from src.kunstpixel.core import llm, oppslag
from src.kunstpixel.core.mcp_server import (
    get_absence_report,
    get_artwork_details,
    get_exhibition_economy,
    get_report_assessment,
    get_report_rules,
    get_room_artworks,
    get_shift_cost_for_period,
    get_shifts_for_date,
    get_sickness_absence_statistics,
    get_staff_on_shift,
    get_working_hours_report,
    get_working_time_limits,
    list_exhibitions_with_economy,
    list_roles,
    lookup_handbook,
    search_collection,
    search_events,
    search_faq,
)

ASSET_DIR = Path(__file__).resolve().parent / "datafinner"
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/sok.html": ("sok.html", "text/html; charset=utf-8"),
    "/oppslag.html": ("oppslag.html", "text/html; charset=utf-8"),
    "/af.css": ("af.css", "text/css; charset=utf-8"),
}

# Interne mapper siden kan lese. Bare tekstfiler, aldri skriving.
MAPPER = ["00_felles", "01_inbox", "02_deliverables", "03_team", "04_knowledge", "05_data/governance"]
FILTYPER = {".md", ".yaml", ".yml", ".json", ".txt", ".csv"}
MAKS_FILSTORRELSE = 512_000


def _filer(mappe: str | None) -> list[Path]:
    roots = [mappe] if mappe else MAPPER
    files: list[Path] = []
    for r in roots:
        if r not in MAPPER:
            raise ValueError(f"Ukjent mappe: {r}")
        base = PROJECT_ROOT / r
        if base.is_dir():
            files += [
                p
                for p in sorted(base.rglob("*"))
                if p.is_file() and p.suffix.lower() in FILTYPER and p.stat().st_size <= MAKS_FILSTORRELSE
            ]
    return files


def grep_mappe(query: str, mappe: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Søk etter tekst i interne mapper. Returnerer fil, linje og treff."""
    if not query or not query.strip():
        return []
    needle = query.strip().lower()
    hits: list[dict[str, Any]] = []
    for path in _filer(mappe):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for no, line in enumerate(lines, start=1):
            if needle in line.lower():
                hits.append(
                    {
                        "sti": path.relative_to(PROJECT_ROOT).as_posix(),
                        "linje": no,
                        "treff": line.strip()[:200],
                    }
                )
                if len(hits) >= limit:
                    return hits
    return hits


def les_fil(sti: str) -> dict[str, Any]:
    """Les én tekstfil i en intern mappe. Stier utenfor MAPPER avvises."""
    path = (PROJECT_ROOT / sti).resolve()
    allowed = [(PROJECT_ROOT / m).resolve() for m in MAPPER]
    if not any(path.is_relative_to(a) for a in allowed):
        raise ValueError(f"Stien er utenfor de interne mappene: {sti}")
    if not path.is_file() or path.suffix.lower() not in FILTYPER:
        raise ValueError(f"Fant ingen lesbar tekstfil: {sti}")
    if path.stat().st_size > MAKS_FILSTORRELSE:
        raise ValueError(f"Filen er for stor til å vises: {sti}")
    return {"sti": path.relative_to(PROJECT_ROOT).as_posix(), "tekst": path.read_text(encoding="utf-8", errors="replace")}


def sok_internt(query: str, limit: int = 3) -> dict[str, Any]:
    """Søk på tvers av håndbøker, interne tabeller og interne dokumenter, gruppert per kilde.

    Personer, fravær og varsler er ikke med. Hvert treff har id, tittel, tekst og felt fra kilden.

    Args:
        query: Spørsmålet eller ordene du leter etter (f.eks. 'hviletid', 'egenmelding', 'avvik strøm').
        limit: Maks treff per kilde (1-50, standard 3).
    """
    filer = oppslag.sok_filer(query, PROJECT_ROOT, MAPPER, FILTYPER, MAKS_FILSTORRELSE, limit=max(limit, 5))
    return oppslag.sok_internt(query, limit=limit, filer=filer)


# Hvitliste: verktøynavn -> (funksjon, tillatte argumenter)
VERKTOY: dict[str, tuple[Callable[..., Any], set[str]]] = {
    "sok_internt": (sok_internt, {"query", "limit"}),
    "lookup_handbook": (lookup_handbook, {"query", "handbok", "role", "limit"}),
    "grep_mappe": (grep_mappe, {"query", "mappe", "limit"}),
    "les_fil": (les_fil, {"sti"}),
    "search_collection": (
        search_collection,
        {"query", "artist", "title", "technique", "theme", "room_id", "limit"},
    ),
    "get_artwork_details": (get_artwork_details, {"artwork_id"}),
    "get_room_artworks": (get_room_artworks, {"room_id"}),
    "search_events": (search_events, {"event_type", "date_from", "date_to", "limit"}),
    "search_faq": (search_faq, {"query", "category"}),
    # HR og bemanning
    "get_staff_on_shift": (get_staff_on_shift, {"dato", "klokkeslett"}),
    "get_working_time_limits": (get_working_time_limits, set()),
    "get_shifts_for_date": (get_shifts_for_date, {"dato"}),
    "get_working_hours_report": (get_working_hours_report, {"maaned"}),
    "get_sickness_absence_statistics": (get_sickness_absence_statistics, {"year", "quarter"}),
    "get_absence_report": (get_absence_report, {"aar", "kvartal"}),
    "list_roles": (list_roles, set()),
    "get_report_rules": (get_report_rules, {"sporsmal_id"}),
    "get_report_assessment": (get_report_assessment, {"sporsmal_id", "verdier"}),
    # Økonomi og innkjøp
    "get_exhibition_economy": (get_exhibition_economy, {"exhibition_id"}),
    "get_shift_cost_for_period": (get_shift_cost_for_period, {"maaned"}),
    "list_exhibitions_with_economy": (list_exhibitions_with_economy, set()),
}


# KI-laget er av med mindre LLM_PROVIDER er satt. Feil innstilling stopper oppstarten med en tydelig melding.
LLM_KONFIG = llm.fra_miljo(os.environ)
LLM_BEGRENSER = llm.Begrenser(LLM_KONFIG.maks_per_time) if LLM_KONFIG else None
MAKS_POST_BYTES = 4096

# Siden bruker bare egne filer, ett skript og stilark i samme side. Alt annet er stengt.
SIKKERHETSHODER = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": (
        "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    ),
}


def run_tool(name: str, args: dict[str, Any]) -> Any:
    """Kjør ett hvitelistet MCP-verktøy med kun tillatte argumenter."""
    if name not in VERKTOY:
        raise ValueError(f"Ukjent verktøy: {name}")
    fn, allowed = VERKTOY[name]
    unknown = set(args) - allowed
    if unknown:
        raise ValueError(f"Ukjente argumenter for {name}: {', '.join(sorted(unknown))}")
    clean = {k: v for k, v in args.items() if v not in (None, "")}
    if "limit" in clean:
        clean["limit"] = max(1, min(int(clean["limit"]), 50))
    return fn(**clean)


class DatafinnerHandler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for navn, verdi in SIKKERHETSHODER.items():
            self.send_header(navn, verdi)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: Any) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path in ASSETS:
            filename, ctype = ASSETS[url.path]
            self._send(200, (ASSET_DIR / filename).read_bytes(), ctype)
            return
        if url.path == "/api/status":
            self._json(200, {
                "llm": LLM_KONFIG is not None,
                "llm_modell": LLM_KONFIG.modell if LLM_KONFIG else None,
                "verktoy": len(VERKTOY),
            })
            return
        if url.path == "/api/verktoyskjema":
            self._json(200, {"verktoy": datafinner_api.verktoyskjema(VERKTOY), "sporsmal": datafinner_api.SPORSMAL})
            return
        if url.path == "/api/rapport":
            params = parse_qs(url.query)
            try:
                args = json.loads(params.get("args", ["{}"])[0] or "{}")
                if not isinstance(args, dict):
                    raise ValueError("args må være et JSON-objekt")
                rapport = datafinner_api.lag_rapport(params.get("sporsmal", [""])[0], args, run_tool)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
                return
            except Exception as exc:  # databasefeil o.l.
                sys.stderr.write(f"[datafinner] FEIL i rapport: {exc!r}\n")
                self._json(500, {"error": "Feil ved oppslag. Prøv igjen, eller si ifra til den som drifter siden."})
                return
            self._json(200, rapport)
            return
        if url.path == "/api/verktoy":
            params = parse_qs(url.query)
            name = params.get("navn", [""])[0]
            try:
                args = json.loads(params.get("args", ["{}"])[0] or "{}")
                if not isinstance(args, dict):
                    raise ValueError("args må være et JSON-objekt")
                result = run_tool(name, args)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
                return
            except Exception as exc:  # databasefeil o.l.
                # Detaljene (stier, SQL) står i loggen, ikke i svaret til nettleseren.
                sys.stderr.write(f"[datafinner] FEIL i {name}: {exc!r}\n")
                self._json(500, {"error": "Feil ved oppslag. Prøv igjen, eller si ifra til den som drifter siden."})
                return
            self._json(200, {"verktoy": name, "args": args, "resultat": result})
            return
        self._json(404, {"error": "Finnes ikke"})

    def do_POST(self) -> None:
        """Eneste POST: /api/forklar. Koster penger hos KI-leverandøren, så den har flere sperrer."""
        if urlparse(self.path).path != "/api/forklar":
            self._json(404, {"error": "Finnes ikke"})
            return
        # Nettleseren sender innloggingen din automatisk. Uten disse sperrene kunne en annen nettside
        # få den til å kalle KI-en på din regning. Samme opprinnelse eller ingen opprinnelse (curl) er greit.
        opprinnelse = self.headers.get("Origin")
        if opprinnelse and urlparse(opprinnelse).netloc != self.headers.get("Host", ""):
            self._json(403, {"error": "Forespørselen kom fra en annen side."})
            return
        if self.headers.get("Sec-Fetch-Site") not in (None, "same-origin", "none"):
            self._json(403, {"error": "Forespørselen kom fra en annen side."})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            self._json(415, {"error": "Bruk Content-Type: application/json."})
            return
        try:
            lengde = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            lengde = 0
        if lengde <= 0 or lengde > MAKS_POST_BYTES:
            self._json(413, {"error": f"Kroppen må være mellom 1 og {MAKS_POST_BYTES} byte."})
            return
        if LLM_KONFIG is None:
            self._json(503, {"error": "KI-laget er ikke slått på. Rapportene er likevel tilgjengelige uten KI."})
            return
        try:
            kropp = json.loads(self.rfile.read(lengde).decode("utf-8"))
            if not isinstance(kropp, dict) or not isinstance(kropp.get("args", {}), dict):
                raise ValueError("Send et JSON-objekt: {\"sporsmal\": \"...\", \"args\": {...}}")
            rapport = datafinner_api.lag_rapport(str(kropp.get("sporsmal", "")), kropp.get("args", {}), run_tool)
        except (ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return
        except Exception as exc:
            sys.stderr.write(f"[datafinner] FEIL i forklar/rapport: {exc!r}\n")
            self._json(500, {"error": "Feil ved oppslag. Prøv igjen, eller si ifra til den som drifter siden."})
            return
        if LLM_BEGRENSER is not None and not LLM_BEGRENSER.tillat():
            self._json(429, {"error": "For mange KI-kall den siste timen. Prøv igjen senere."})
            return
        try:
            svar = llm.forklar(rapport, LLM_KONFIG)
        except llm.LlmFeil as exc:
            sys.stderr.write(f"[datafinner] KI-feil ({exc.kode}): {exc}\n")
            self._json(504 if exc.kode == "tidsavbrudd" else 502, {"error": str(exc)})
            return
        self._json(200, {**svar, "status": "Utkast", "rapport": rapport})

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("[datafinner] " + (format % args) + "\n")


def main() -> None:
    port = int(os.environ.get("DATAFINNER_PORT", "8010"))
    host = os.environ.get("DATAFINNER_HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), DatafinnerHandler)
    print(f"Datafinner kjører på http://{host}:{port} (Ctrl+C for å stoppe)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
