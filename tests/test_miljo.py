"""Tester for innlesing av .env (KI-nøkkel). Bruker midlertidige filer, aldri prosjektets ekte .env."""

from __future__ import annotations

from pathlib import Path

from src.kunstpixel.core import miljo


def test_leser_navn_og_verdier_og_hopper_over_kommentarer(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text('# kommentar\nLLM_PROVIDER=anthropic\nLLM_MODEL="claude-sonnet-5-5"\n\nexport LLM_MAX_TOKENS=1500\nsøppel\n', encoding="utf-8")
    m: dict[str, str] = {}
    assert miljo.last_env_fil(f, m) == ["LLM_PROVIDER", "LLM_MODEL", "LLM_MAX_TOKENS"]
    assert m == {"LLM_PROVIDER": "anthropic", "LLM_MODEL": "claude-sonnet-5-5", "LLM_MAX_TOKENS": "1500"}


def test_miljoet_vinner_og_tomme_verdier_settes_ikke(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("LLM_MODEL=fra-fil\nLLM_API_KEY=\n", encoding="utf-8")
    m = {"LLM_MODEL": "fra-terminal"}
    assert miljo.last_env_fil(f, m) == []
    assert m == {"LLM_MODEL": "fra-terminal"}


def test_manglende_fil_gir_ingenting(tmp_path: Path) -> None:
    assert miljo.last_env_fil(tmp_path / "finnes-ikke", {}) == []


def test_import_av_datafinner_leser_ikke_env() -> None:
    """KI-laget slås ikke på av en .env-fil når serveren importeres (bare main() leser filen)."""
    import inspect

    from src.kunstpixel.adapters import datafinner
    kilde = inspect.getsource(datafinner)
    forste_bruk = kilde.index("miljo.last_env_fil()")
    assert forste_bruk > kilde.index("def main()"), "last_env_fil skal bare kalles inne i main()"


def test_eksempelfilen_har_ingen_nokkel() -> None:
    eksempel = (miljo.PROJECT_ROOT / ".env.eksempel").read_text(encoding="utf-8")
    assert "LLM_API_KEY=\n" in eksempel and "claude-sonnet-5-5" in eksempel
