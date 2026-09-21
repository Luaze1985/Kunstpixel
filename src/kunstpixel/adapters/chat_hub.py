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

HTML_PAGE = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🏛️ Aura Kunstmuseum — Gründer Chat</title>
<style>
  :root {
    --bg: #0b0f19;
    --panel: #151d30;
    --border: #273553;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --primary: #38bdf8;
    --primary-hover: #0284c7;
    --bubble-user: #0284c7;
    --bubble-agent: #1e293b;
    --accent: #10b981;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100dvh;
    display: flex;
    flex-direction: column;
  }
  header {
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .brand { display: flex; align-items: center; gap: 0.75rem; }
  .brand h1 { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.01em; }
  .status-badge {
    background: rgba(16, 185, 129, 0.15);
    color: var(--accent);
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
  }
  .role-indicator { font-size: 0.85rem; color: var(--muted); }
  main {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
  }
  .msg {
    display: flex;
    flex-direction: column;
    max-width: 82%;
    gap: 0.35rem;
  }
  .msg.user { align-self: flex-end; }
  .msg.agent { align-self: flex-start; }
  .bubble {
    padding: 0.9rem 1.25rem;
    border-radius: 1.1rem;
    line-height: 1.6;
    font-size: 0.95rem;
  }
  .msg.user .bubble {
    background: var(--bubble-user);
    color: white;
    border-bottom-right-radius: 0.25rem;
  }
  .msg.agent .bubble {
    background: var(--bubble-agent);
    border: 1px solid var(--border);
    border-bottom-left-radius: 0.25rem;
  }
  .meta-tag {
    font-size: 0.75rem;
    color: var(--muted);
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
  }
  .badge-tool {
    background: rgba(56, 189, 248, 0.15);
    color: var(--primary);
    padding: 0.15rem 0.5rem;
    border-radius: 0.3rem;
    font-family: monospace;
    font-size: 0.72rem;
  }
  .quick-prompts {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding: 0.6rem 1.5rem;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
  }
  .quick-chip {
    background: var(--panel);
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 0.4rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.82rem;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
  }
  .quick-chip:hover {
    color: var(--text);
    border-color: var(--primary);
  }
  footer {
    background: var(--panel);
    border-top: 1px solid var(--border);
    padding: 1.2rem 1.5rem;
  }
  form {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    gap: 0.75rem;
  }
  input[type="text"] {
    flex: 1;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 0.6rem;
    padding: 0.85rem 1.15rem;
    color: var(--text);
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
  }
  input[type="text"]:focus { border-color: var(--primary); }
  button {
    background: var(--primary);
    color: #0b0f19;
    border: none;
    padding: 0.85rem 1.5rem;
    border-radius: 0.6rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s;
  }
  button:hover { background: var(--primary-hover); color: white; }
</style>
</head>
<body>

<header>
  <div class="brand">
    <h1>🏛️ Aura Kunstmuseum</h1>
    <span class="status-badge">● FastMCP Live</span>
  </div>
  <div class="role-indicator">Aktiv Agent: <strong>Museumsvert</strong> (Samlings-MCP tilkoblet)</div>
</header>

<main id="chatBox">
  <div class="msg agent">
    <div class="meta-tag">🏛️ Aura Museumsvert</div>
    <div class="bubble">
      Hei! Jeg er koblet direkte på museets SQLite-samlingsdatabase og verktøy. Hva vil dere utforske eller teste i dag?
    </div>
  </div>
</main>

<div class="quick-prompts">
  <button class="quick-chip" onclick="quickAsk('Hvor finner jeg Skrik?')">📍 Hvor finner jeg Skrik?</button>
  <button class="quick-chip" onclick="quickAsk('Hva koster det for en student og to voksne?')">🎟️ Billettpriser</button>
  <button class="quick-chip" onclick="quickAsk('Hva anbefaler du hvis jeg har 30 minutter?')">⏱️ 30-minutters rute</button>
  <button class="quick-chip" onclick="quickAsk('Hvilke arrangementer finnes for barn?')">🎨 Barneaktiviteter</button>
  <button class="quick-chip" onclick="quickAsk('Hva henger i Sal C?')">🖼️ Sal C oversikt</button>
</div>

<footer>
  <form id="chatForm" onsubmit="sendMessage(event)">
    <input type="text" id="userInput" placeholder="Spør museumsverten eller test et verktøykall..." autocomplete="off" />
    <button type="submit">Send</button>
  </form>
</footer>

<script>
  const chatBox = document.getElementById('chatBox');
  const userInput = document.getElementById('userInput');

  function quickAsk(text) {
    userInput.value = text;
    sendMessage(new Event('submit'));
  }

  async function sendMessage(e) {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;

    // Append user message
    const userDiv = document.createElement('div');
    userDiv.className = 'msg user';
    userDiv.innerHTML = `<div class="bubble">${escapeHtml(query)}</div>`;
    chatBox.appendChild(userDiv);
    userInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Loading placeholder
    const agentDiv = document.createElement('div');
    agentDiv.className = 'msg agent';
    agentDiv.innerHTML = `
      <div class="meta-tag">🏛️ Aura Museumsvert <span class="badge-tool">kaller verktøy...</span></div>
      <div class="bubble">Søker i samlingen og verktøyene...</div>
    `;
    chatBox.appendChild(agentDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      });
      const data = await res.json();

      let toolsHtml = (data.tools_used && data.tools_used.length > 0)
        ? data.tools_used.map(t => `<span class="badge-tool">🔧 ${t}</span>`).join(' ')
        : `<span class="badge-tool">database</span>`;

      let roomsHtml = (data.rooms_referenced && data.rooms_referenced.length > 0)
        ? `<span>📍 ${data.rooms_referenced.join(', ')}</span>`
        : '';

      agentDiv.innerHTML = `
        <div class="meta-tag">
          🏛️ Museumsvert | Kat: ${data.category} | ${toolsHtml} ${roomsHtml}
        </div>
        <div class="bubble">${escapeHtml(data.text).replace(/\\n/g, '<br>')}</div>
      `;
    } catch (err) {
      agentDiv.innerHTML = `
        <div class="meta-tag">⚠️ Feil</div>
        <div class="bubble">Kunne ikke koble til agenten: ${err.message}</div>
      `;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
</script>

</body>
</html>
"""


class ChatHubHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
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
