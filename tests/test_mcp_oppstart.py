"""MCP-serveren skal kunne startes av Claude (Code/Desktop) via .mcp.json (DECISIONS 2026-11-09, punkt 13).

Claude starter serveren som en egen prosess over stdio, ikke nødvendigvis fra prosjektmappen.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def _list_og_kall(cwd: Path) -> tuple[int, str]:
    p = StdioServerParameters(command=sys.executable, args=[str(ROOT / "src" / "mcp_server.py")], cwd=str(cwd))
    async with stdio_client(p) as (r, w), ClientSession(r, w) as s:
        await s.initialize()
        verktoy = (await s.list_tools()).tools
        svar = await s.call_tool("get_artwork_details", {"artwork_id": "kp-2026-009"})
        return len(verktoy), svar.content[0].text


def test_mcp_server_starter_utenfor_prosjektmappen(tmp_path: Path) -> None:
    antall, tekst = asyncio.run(_list_og_kall(tmp_path))
    assert antall >= 45
    assert "KP-2026-009" in tekst


def test_mcp_json_registrerer_kunstpixel() -> None:
    oppsett = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    server = oppsett["mcpServers"]["kunstpixel"]
    assert server["args"][-1].replace("\\", "/").endswith("src/mcp_server.py")
    # Ingen nøkler eller hemmeligheter i fila som committes.
    assert "env" not in server or not any("KEY" in k.upper() for k in server["env"])
