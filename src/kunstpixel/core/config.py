"""Configuration and database path resolution for Aura Kunstmuseum."""

import os
import shutil
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOCAL_DB_PATH = PROJECT_ROOT / "data" / "museum.db"
EXTERNAL_FALLBACK_DB_PATH = Path(r"C:\Users\larse\Documents\.headroom\memory.db")


def get_db_path() -> Path:
    """Resolve the SQLite database path using strict precedence:
    1. AURA_DB_PATH environment variable (if set and exists)
    2. Repository local copy at data/museum.db
    3. External fallback at C:\\Users\\larse\\Documents\\.headroom\\memory.db
    """
    env_path = os.environ.get("KUNSTPIXEL_DB_PATH") or os.environ.get("AURA_DB_PATH")
    if env_path:
        p = Path(env_path)
        if p.is_file():
            return p
        raise FileNotFoundError(f"AURA_DB_PATH was set to '{env_path}', but file does not exist.")

    if LOCAL_DB_PATH.is_file():
        return LOCAL_DB_PATH

    if EXTERNAL_FALLBACK_DB_PATH.is_file():
        return EXTERNAL_FALLBACK_DB_PATH

    raise FileNotFoundError(
        "Aura Kunstmuseum database not found. Checked:\n"
        f"  1. AURA_DB_PATH env var: {env_path}\n"
        f"  2. Local repo copy: {LOCAL_DB_PATH}\n"
        f"  3. External fallback: {EXTERNAL_FALLBACK_DB_PATH}"
    )


def ensure_local_db() -> Path:
    """Ensure the local repository database copy exists.
    If missing, attempts to copy from the external fallback.
    Returns the resolved Path to the local database.
    """
    if LOCAL_DB_PATH.is_file():
        return LOCAL_DB_PATH

    if EXTERNAL_FALLBACK_DB_PATH.is_file():
        LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(EXTERNAL_FALLBACK_DB_PATH, LOCAL_DB_PATH)
        return LOCAL_DB_PATH

    raise FileNotFoundError(
        f"Cannot initialize local database: source {EXTERNAL_FALLBACK_DB_PATH} not found."
    )


# Export current resolved path
try:
    DB_PATH = get_db_path()
except FileNotFoundError:
    DB_PATH = LOCAL_DB_PATH
