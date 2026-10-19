"""Entrypoint for Kunstpixel HR/HMS/Quality local HTTP API (http://127.0.0.1:8765)."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    api_path = Path(__file__).parent / "kunstpixel" / "core" / "hrdemo_api.py"
    runpy.run_path(str(api_path), run_name="__main__")
