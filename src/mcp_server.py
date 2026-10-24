"""Entrypoint for Kunstpixel FastMCP server."""
import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    # Prosjektroten må ligge på sys.path slik at `src.kunstpixel...` kan importeres
    # uansett hvilken mappe serveren startes fra (f.eks. av Claude eller Codex).
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    server_path = Path(__file__).parent / "kunstpixel" / "core" / "mcp_server.py"
    runpy.run_path(str(server_path), run_name="__main__")
