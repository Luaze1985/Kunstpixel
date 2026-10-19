"""Kunstpixel — Datafinner.

Lokal side der gründerne velger hva de vil finne i museum.db og får svaret
fra de samme fem MCP-verktøyene som LLM-en bruker. Siden viser også selve
verktøykallet, slik at man ser nøyaktig hvordan LLM-en ville spurt.

Kun for internt bruk: serveren bindes til 127.0.0.1 og kan ikke nås fra
andre maskiner. Ikke endre vertsadressen før databasen er klarert for deling.

100 % standardbibliotek for webdelen. Databasen åpnes skrivebeskyttet via
src.kunstpixel.core.db (mode=ro), og bare verktøyene i VERKTOY kan kalles.

Kjøres med:
    py -3.13 src/kunstpixel/adapters/datafinner.py

Åpnes på http://127.0.0.1:8010
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

from src.kunstpixel.core.mcp_server import (
    get_artwork_details,
    get_room_artworks,
    search_collection,
    search_events,
    search_faq,
)

ASSET_DIR = Path(__file__).resolve().parent / "datafinner"
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/af.css": ("af.css", "text/css; charset=utf-8"),
}

# Hvitliste: verktøynavn -> (funksjon, tillatte argumenter)
VERKTOY: dict[str, tuple[Callable[..., Any], set[str]]] = {
    "search_collection": (
        search_collection,
        {"query", "artist", "title", "technique", "theme", "room_id", "limit"},
    ),
    "get_artwork_details": (get_artwork_details, {"artwork_id"}),
    "get_room_artworks": (get_room_artworks, {"room_id"}),
    "search_events": (search_events, {"event_type", "date_from", "date_to", "limit"}),
    "search_faq": (search_faq, {"query", "category"}),
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
                self._json(500, {"error": f"Feil ved oppslag: {exc}"})
                return
            self._json(200, {"verktoy": name, "args": args, "resultat": result})
            return
        self._json(404, {"error": "Finnes ikke"})

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("[datafinner] " + (format % args) + "\n")


def main() -> None:
    port = int(os.environ.get("DATAFINNER_PORT", "8010"))
    server = ThreadingHTTPServer(("127.0.0.1", port), DatafinnerHandler)
    print(f"Datafinner kjører på http://127.0.0.1:{port} (Ctrl+C for å stoppe)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
