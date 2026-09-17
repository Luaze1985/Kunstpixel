"""Entrypoint for Kunstpixel CLI (kunstpixel.com)."""
import sys, runpy
from pathlib import Path

if __name__ == "__main__":
    cli_path = Path(__file__).parent / "kunstpixel" / "adapters" / "cli.py"
    runpy.run_path(str(cli_path), run_name="__main__")
