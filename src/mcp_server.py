"""Entrypoint for Kunstpixel FastMCP server.

Startes av Claude via .mcp.json, ofte fra en annen mappe. Prosjektroten legges derfor
først i sys.path, så `from src.kunstpixel...` virker uansett hvor prosessen starter.
"""
import runpy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    server_path = Path(__file__).parent / "kunstpixel" / "core" / "mcp_server.py"
    runpy.run_path(str(server_path), run_name="__main__")
