"""Entrypoint for Kunstpixel HR/HMS/Quality FastMCP server."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    server_path = Path(__file__).parent / "kunstpixel" / "core" / "hrdemo_mcp.py"
    runpy.run_path(str(server_path), run_name="__main__")
