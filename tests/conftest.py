"""Pytest fixtures for Aura Kunstmuseum E2E Test Suite (Tiers 1-4).

Provides shared database connection, configuration paths, expected oracle values,
and optional MCP server and agent fixtures.
"""

import os
import sqlite3
from pathlib import Path
from typing import Generator

import pytest

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def db_path() -> Path:
    """Resolve database path following config precedence:

    1. AURA_DB_PATH environment variable
    2. data/museum.db (project local mirror)
    3. C:\\Users\\larse\\Documents\\.headroom\\memory.db (fallback original)
    """
    env_path = os.environ.get("AURA_DB_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    local_path = (
        (PROJECT_ROOT / "05_data" / "museum.db")
        if (PROJECT_ROOT / "05_data" / "museum.db").is_file()
        else (PROJECT_ROOT / "data" / "museum.db")
    )
    if local_path.exists():
        return local_path

    headroom_path = Path(r"C:\Users\larse\Documents\.headroom\memory.db")
    if headroom_path.exists():
        return headroom_path

    raise FileNotFoundError(
        "Could not find Aura Kunstmuseum database. Checked AURA_DB_PATH, "
        f"{local_path}, and {headroom_path}"
    )


@pytest.fixture
def db_conn(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Yield a read-only sqlite3 connection with sqlite3.Row row factory."""
    # Using URI read-only mode to guarantee no accidental database mutations
    uri_path = f"file:{db_path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri_path, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(scope="session")
def db_baseline() -> dict:
    """Authoritative baseline counts and constants derived from ORIGINAL_REQUEST.md."""
    return {
        "expected_total_rows": 72,
        "table_counts": {
            "kunstnere": 12,
            "saler": 6,
            "verk": 16,
            "utstillinger": 3,
            "utstilling_verk": 15,
            "hendelser": 8,
            "publikum_faq": 12,
        },
        "exhibited_artworks_count": 14,
        "magazine_artworks_count": 2,
        "sal_d_artworks_count": 3,
        "kittelsen_artworks_count": 2,
        "ticket_prices": {
            "voksen": 120,
            "student": 80,
            "pensjonist": 80,
            "barn": 0,
            "familiepass": 250,
        },
        "opening_hours_fragment": "10:00–17:00",
        "skrik_room_id": "SAL-D",
        "skrik_artwork_id": "AURA-2026-009",
    }


@pytest.fixture
def agent_instance(db_path: Path):
    """Provide an instance of MuseumsvertAgent if src.kunstpixel.core.agent is implemented."""
    try:
        from src.kunstpixel.core.agent import MuseumsvertAgent
        return MuseumsvertAgent(db_path=db_path)
    except ImportError as e:
        pytest.skip(f"src.kunstpixel.core.agent not available yet: {e}")
