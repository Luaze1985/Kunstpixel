"""Felles testhjelpere for KI: en falsk leverandør som svarer i rekkefølge. Ingen ekte KI kalles."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from src.kunstpixel.core import llm


class RekkefolgeKi:
    """Falsk leverandør: svarer med neste svar i lista for hvert kall, og husker hver forespørsel."""

    def __init__(self, svar: list[dict]) -> None:
        self.svar, self.sett = list(svar), []
        falsk = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                kropp = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                falsk.sett.append({"sti": self.path, "kropp": kropp})
                neste = falsk.svar.pop(0) if len(falsk.svar) > 1 else falsk.svar[0]
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(neste).encode())

            def log_message(self, *a: Any) -> None:
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def stopp(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def _konfig(leverandor: str, url: str) -> llm.LlmKonfig:
    return llm.LlmKonfig(leverandor=leverandor, modell="falsk", api_key="n", base_url=url)

