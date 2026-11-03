"""Lokal nettside for å melde feil (ingen chatbot, ingen KI).

Start: py -3.13 scripts/meld_feil.py   (åpner http://127.0.0.1:8770)

Lytter bare på 127.0.0.1, så siden er ikke tilgjengelig fra andre maskiner.
"""

from __future__ import annotations

import json
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.kunstpixel.feilmelding import objekter, register

SIDE = Path(__file__).with_name("side.html")
STANDARD_PORT = 8770


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:  # hold terminalen rolig
        pass

    def _svar(self, kode: int, data, type_: str = "application/json") -> None:
        kropp = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(kode)
        self.send_header("Content-Type", f"{type_}; charset=utf-8")
        self.send_header("Content-Length", str(len(kropp)))
        self.end_headers()
        self.wfile.write(kropp)

    def do_GET(self) -> None:
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/":
                return self._svar(200, SIDE.read_bytes(), "text/html")
            if url.path == "/api/objekttyper":
                return self._svar(200, objekter.objekttyper())
            if url.path == "/api/ansatte":
                return self._svar(200, objekter.aktive_ansatte(date.today()))
            if url.path == "/api/objekter":
                return self._svar(200, objekter.list_objekter(q.get("type", ""), q.get("sok", "")))
            if url.path == "/api/objekt":
                obj = objekter.hent_objekt(q.get("type", ""), q.get("id", ""))
                return self._svar(200 if obj else 404, obj or {"feil": "Fant ikke objektet."})
            if url.path == "/api/meldinger":
                return self._svar(200, list(reversed(register.liste())))
            return self._svar(404, {"feil": "Ukjent adresse."})
        except (ValueError, FileNotFoundError) as e:
            return self._svar(400, {"feil": str(e)})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/meld":
            return self._svar(404, {"feil": "Ukjent adresse."})
        try:
            lengde = min(int(self.headers.get("Content-Length", 0)), 100_000)
            melding = json.loads(self.rfile.read(lengde) or b"{}")
            return self._svar(200, {"melding_id": register.registrer(melding)})
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            return self._svar(400, {"feil": str(e)})


def lag_server(port: int = STANDARD_PORT, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), _Handler)
