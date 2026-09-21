"""Entrypoint for Kunstpixel FastMCP server."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    server_path = Path(__file__).parent / "kunstpixel" / "core" / "mcp_server.py"
    runpy.run_path(str(server_path), run_name="__main__")
