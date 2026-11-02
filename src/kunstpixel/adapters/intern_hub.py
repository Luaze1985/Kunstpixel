"""Intern web-chat for HR, HMS og drift (H3).

Egen server, adskilt fra den offentlige museumsvert-chatten:
- binder bare til 127.0.0.1, aldri til nettverket
- avviser fremmede Host- og Origin-headere (DNS rebinding og kryss-nettsted-kall)
- krever JSON på POST, med tak på størrelse
- sender strenge sikkerhetshoder og en CSP med nonce

Start: py -3.13 src/kunstpixel/adapters/intern_hub.py   (åpner http://127.0.0.1:8001)
"""

from __future__ import annotations

import json
import secrets
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.intern.agent import InternAgent  # noqa: E402
from src.kunstpixel.core.intern.data import ROLLER  # noqa: E402
from src.kunstpixel.core.llm import build_llm  # noqa: E402

HOST = "127.0.0.1"  # med vilje ikke konfigurerbar
PORT = 8001
MAX_BODY_BYTES = 20_000
MAX_MESSAGE_CHARS = 1000

ADAPTERS = Path(__file__).resolve().parent
PAGE_PATH = ADAPTERS / "intern" / "intern.html"
CSS_PATH = ADAPTERS / "datafinner" / "af.css"  # delt designsystem-fil (Arbeidsflyt)

ROLLE_NAVN = {
    "museumsdirektor": "Museumsdirektør",
    "samlingsforvalter": "Samlingsforvalter",
    "kurator": "Kurator",
    "formidler": "Formidler",
    "museumsvert": "Museumsvert",
    "driftsansvarlig": "Driftsansvarlig",
    "kvalitetsvokter": "Kvalitetsvokter",
}
assert set(ROLLE_NAVN) == set(ROLLER)


def create_agent() -> InternAgent:
    """KUNSTPIXEL_LLM=off|fake|anthropic velger modell. Feil oppsett gir regelbasert assistent."""
    try:
        llm = build_llm()
    except Exception as exc:  # noqa: BLE001 - demoen skal aldri krasje på manglende oppsett
        print(f"LLM ikke tilgjengelig ({type(exc).__name__}). Kjører regelbasert assistent.")
        llm = None
    return InternAgent(llm=llm)


class InternHubHandler(BaseHTTPRequestHandler):
    agent: InternAgent | None = None

    # ---------------------------------------------------------------- hjelpere

    def _port(self) -> int:
        return self.server.server_address[1]

    def _allowed_hosts(self) -> set[str]:
        p = self._port()
        return {f"127.0.0.1:{p}", f"localhost:{p}", f"[::1]:{p}"}

    def _allowed_origins(self) -> set[str]:
        return {f"http://{h}" for h in self._allowed_hosts()}

    def _security_headers(self, nonce: str | None = None) -> None:
        csp = (
            "default-src 'none'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; "
            + (f"script-src 'nonce-{nonce}'; style-src 'self' 'nonce-{nonce}'" if nonce else "style-src 'self'")
        )
        self.send_header("Content-Security-Policy", csp)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")

    def _send(self, status: int, body: bytes, content_type: str, nonce: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._security_headers(nonce)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: object) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _host_ok(self) -> bool:
        """Avvis fremmede Host (DNS rebinding) og fremmede Origin (kall fra andre nettsteder)."""
        host = self.headers.get("Host", "")
        if host not in self._allowed_hosts():
            self._json(403, {"error": "Ugyldig vert."})
            return False
        origin = self.headers.get("Origin")
        if origin is not None and origin not in self._allowed_origins():
            self._json(403, {"error": "Ugyldig opprinnelse."})
            return False
        return True

    # ---------------------------------------------------------------- GET

    def do_GET(self) -> None:
        if not self._host_ok():
            return
        path = self.path.split("?", 1)[0]
        if path == "/":
            try:
                html = PAGE_PATH.read_text(encoding="utf-8")
            except OSError:
                self._json(500, {"error": "Siden mangler."})
                return
            nonce = secrets.token_urlsafe(16)
            self._send(200, html.replace("{{NONCE}}", nonce).encode("utf-8"), "text/html; charset=utf-8", nonce)
        elif path == "/af.css":
            try:
                css = CSS_PATH.read_bytes()
            except OSError:
                self._json(500, {"error": "Stilfil mangler."})
                return
            self._send(200, css, "text/css; charset=utf-8")
        elif path == "/api/roller":
            self._json(200, [{"id": r, "navn": ROLLE_NAVN[r]} for r in ROLLER])
        else:
            self._json(404, {"error": "Ikke funnet."})

    # ---------------------------------------------------------------- POST

    def do_POST(self) -> None:
        # Les kroppen (innenfor taket) før noe avvises. Svarer vi uten å lese, kan Windows avbryte
        # tilkoblingen før klienten får svaret.
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = None
        raw_body = self.rfile.read(length) if (length is not None and 0 < length <= MAX_BODY_BYTES) else b""

        if not self._host_ok():
            return
        if self.path != "/api/chat":
            self._json(404, {"error": "Ikke funnet."})
            return
        if not (self.headers.get("Content-Type") or "").lower().startswith("application/json"):
            self._json(415, {"error": "Bruk Content-Type application/json."})
            return
        if length is None or length < 0:
            self._json(400, {"error": "Ugyldig Content-Length."})
            return
        if length > MAX_BODY_BYTES:
            self._json(413, {"error": "Meldingen er for stor."})
            return
        body = raw_body.decode("utf-8", errors="replace")

        message, role = "", None
        try:
            data = json.loads(body)
            if isinstance(data, dict):
                m = data.get("message", "")
                message = m.strip()[:MAX_MESSAGE_CHARS] if isinstance(m, str) else ""
                role = data.get("rolle") if isinstance(data.get("rolle"), str) else None
        except Exception:  # noqa: BLE001 - ugyldig JSON behandles som tom melding
            pass

        cls = type(self)
        if cls.agent is None:
            cls.agent = create_agent()
        try:
            r = cls.agent.handle_message(message, role)
        except Exception:  # noqa: BLE001 - aldri vis feilspor
            self._json(500, {"error": "Beklager, noe gikk galt. Prøv igjen."})
            return

        self._json(
            200,
            {
                "text": r.text,
                "category": r.category,
                "tools_used": r.tools_used,
                "kilder": r.kilder,
                "funnet": r.funnet,
                "rolle": r.rolle,
                "klassifisering": r.klassifisering,
                "llm_used": r.llm_used,
                "model": r.model,
                "fallback_reason": r.fallback_reason,
            },
        )

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - ingen forespørselslogg (kan inneholde spørsmål)
        return


def make_server(agent: InternAgent | None = None, port: int = PORT) -> HTTPServer:
    """Lag server bundet til 127.0.0.1. port=0 gir ledig port (brukes i tester)."""
    handler = type("BoundInternHandler", (InternHubHandler,), {"agent": agent})
    return HTTPServer((HOST, port), handler)


def main() -> None:
    agent = create_agent()
    httpd = make_server(agent, PORT)
    url = f"http://{HOST}:{httpd.server_address[1]}"
    print("=" * 60)
    print("Kunstpixel intern assistent (kun lesing, kun denne maskinen)")
    print("=" * 60)
    print(f"Åpne: {url}")
    print(f"Modell: {getattr(agent.llm, 'name', None) or 'ingen, regelbasert'}")
    print("Trykk Ctrl+C for å stoppe.\n")
    try:
        webbrowser.open(url)
    except Exception:  # noqa: BLE001
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nAvslutter.")
        httpd.server_close()


if __name__ == "__main__":
    main()
