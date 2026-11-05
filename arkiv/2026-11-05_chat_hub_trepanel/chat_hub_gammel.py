"""Aura Kunstmuseum — Gründer Chat Hub.

Superenkel lokal web-chat for de to gründerne.
100 % standardbibliotek (ingen eksterne pakker kreves, null dependencies).

Kjøres med:
    py -3.13 src/chat_hub.py

Åpnes automatisk i nettleseren på http://localhost:8000
"""

from __future__ import annotations

import json
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.agent import MuseumsvertAgent

agent = MuseumsvertAgent()

HTML_PAGE = (Path(__file__).resolve().parent / "chat_hub.html").read_text(encoding="utf-8")

# Arbeidsflyt-designsystemet leses fra disk, slik at siden alltid bruker gjeldende versjon.
ARBEIDSFLYT_DIR = Path(
    os.environ.get("ARBEIDSFLYT_DIR", "G:/Min disk/Designssystemer/arbeidsflyt")
)
CSS_FILES = {"/bundle.css": "bundle.css", "/tokens.css": "tokens.css"}


class ChatHubHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path in CSS_FILES:
            css_path = ARBEIDSFLYT_DIR / CSS_FILES[self.path]
            if not css_path.is_file():
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.end_headers()
            self.wfile.write(css_path.read_bytes())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(body)
                query = data.get("message", "").strip()
            except Exception:
                query = ""

            resp = agent.handle_message(query)
            payload = {
                "text": resp.text,
                "category": resp.category,
                "tools_used": resp.tools_used,
                "artworks_referenced": resp.artworks_referenced,
                "rooms_referenced": resp.rooms_referenced,
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args) -> None:
        # Suppress noisy standard request logs
        return


def main() -> None:
    port = 8000
    server_address = ("", port)
    httpd = HTTPServer(server_address, ChatHubHandler)

    print("=" * 65)
    print("🏛️  Aura Kunstmuseum — Gründer Chat Hub")
    print("=" * 65)
    print(f"👉 Kjører på: http://localhost:{port}")
    print("✨ Null eksterne pakker kreves. Koblet rett på FastMCP og SQLite.")
    print("Trykk Ctrl+C i terminalen for å stoppe.\n")

    # Open browser automatically
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nAvslutter Gründer Chat Hub...")
        httpd.server_close()


if __name__ == "__main__":
    main()
