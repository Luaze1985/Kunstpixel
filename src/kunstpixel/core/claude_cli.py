"""KI via din egen Claude: den lokale claude-kommandoen (Claude Code) i stedet for API-nøkkel.

Brukes når LLM_PROVIDER=claude-cli (DECISIONS 2026-11-09, punkt 14). Går på Claude-abonnementet,
uten nøkkel og uten egen regning. Svarene får samme form som API-veien i llm.py.

Låst ned:
- --tools ""                 ingen innebygde verktøy (ingen kommandolinje, filer eller nett)
- --strict-mcp-config        bare Kunstpixel-serveren som gis her
- --allowedTools             bare verktøyene på Datafinners hviteliste
- --setting-sources ""       ingen innstillinger eller hooks fra brukeren
- --no-session-persistence   ingenting lagres
- tom arbeidsmappe           ingen CLAUDE.md eller .mcp.json fra prosjektet
- spørsmålet går på stdin    ikke synlig i prosesslisten, og ingen grense for lengde på kommandolinjen
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MCP_SERVER = PROJECT_ROOT / "src" / "mcp_server.py"
SERVERNAVN = "kunstpixel"
PREFIKS = f"mcp__{SERVERNAVN}__"
MAKS_RUNDER = 8
_GYLDIG_NAVN = re.compile(r"^[A-Za-z0-9_]+$")

Kjor = Callable[..., subprocess.CompletedProcess]


def _feil(kode: str, melding: str) -> Exception:
    from src.kunstpixel.core.llm import (
        LlmFeil,  # sen import: llm importerer denne modulen
    )

    return LlmFeil(kode, melding)


def _claude() -> str:
    return shutil.which("claude") or "claude"


def _grunnkommando(konfig: Any, system: str) -> list[str]:
    return [
        _claude(), "-p",
        "--output-format", "stream-json", "--verbose",
        "--model", konfig.modell,
        "--tools", "",
        "--strict-mcp-config",
        "--setting-sources", "",
        "--permission-mode", "default",
        "--no-session-persistence",
        "--system-prompt", system,
    ]


def _kjor(cmd: list[str], inn: str, konfig: Any, kjor: Kjor) -> list[dict[str, Any]]:
    """Kjør claude i en tom mappe og les hendelsene. Feil blir LlmFeil med trygg melding."""
    with tempfile.TemporaryDirectory(prefix="kunstpixel-claude-") as tom:
        try:
            p = kjor(cmd, input=inn, cwd=tom, capture_output=True, text=True, encoding="utf-8",
                     timeout=konfig.timeout)
        except subprocess.TimeoutExpired:
            raise _feil("tidsavbrudd", "Claude svarte ikke i tide.") from None
        except FileNotFoundError:
            raise _feil("leverandorfeil", "Fant ikke claude-kommandoen. Installer Claude Code og logg inn.") from None
        except OSError:
            raise _feil("leverandorfeil", "Fikk ikke startet Claude.") from None
    hendelser = []
    for linje in (p.stdout or "").splitlines():
        try:
            hendelser.append(json.loads(linje))
        except json.JSONDecodeError:
            continue
    if p.returncode != 0 and not any(h.get("type") == "result" for h in hendelser):
        # Detaljene (stier, kontoinfo) står i serverloggen, ikke i svaret til nettleseren.
        sys.stderr.write(f"[claude-cli] avsluttet med kode {p.returncode}: {(p.stderr or '')[:500]}\n")
        raise _feil("leverandorfeil", "Claude ga en feil. Sjekk at du er logget inn i Claude Code.")
    return hendelser


def _resultat(hendelser: list[dict[str, Any]]) -> str:
    res = next((h for h in reversed(hendelser) if h.get("type") == "result"), None)
    if res is None:
        raise _feil("leverandorfeil", "Claude ga ikke noe svar.")
    if res.get("subtype") == "error_max_turns":
        raise _feil("for_mange_runder", "Claude brukte for mange runder med verktøy uten å svare.")
    # Siden viser ren tekst, så markdown-fet (**x**) vises uten stjerner.
    tekst = re.sub(r"\*\*(.+?)\*\*", r"\1", str(res.get("result") or "")).strip()
    if res.get("is_error") or not tekst:
        raise _feil("leverandorfeil", "Claude ga et tomt svar eller en feil.")
    return tekst


def _innhold_tekst(innhold: Any) -> str:
    if isinstance(innhold, str):
        return innhold
    if isinstance(innhold, list):
        return "".join(b.get("text", "") for b in innhold if isinstance(b, dict))
    return json.dumps(innhold, ensure_ascii=False)


def _samtale(meldinger: list[dict[str, str]]) -> str:
    if len(meldinger) == 1:
        return meldinger[0]["tekst"]
    deler = ["Samtalen så langt (eldste først). Svar på den siste meldingen fra brukeren.", ""]
    for m in meldinger:
        deler.append(("Bruker: " if m["rolle"] == "bruker" else "Datafinner: ") + m["tekst"])
    return "\n".join(deler)


def tekst(bruker_tekst: str, konfig: Any, system: str, kjor: Kjor = subprocess.run) -> str:
    """Én oppgave uten verktøy (forklar, vaktrom, grense). Dataene står i bruker_tekst."""
    cmd = _grunnkommando(konfig, system) + ["--max-turns", "1"]
    return _resultat(_kjor(cmd, bruker_tekst, konfig, kjor))


def chat(meldinger: list[dict[str, str]], verktoy: list[dict[str, Any]], konfig: Any, system: str,
         kjor: Kjor = subprocess.run) -> dict[str, Any]:
    """Én chattur: Claude kaller Kunstpixel-verktøyene selv via MCP og svarer i tekst."""
    from src.kunstpixel.core.llm import tallkontroll

    tillatt = [PREFIKS + v["navn"] for v in verktoy if _GYLDIG_NAVN.match(str(v.get("navn", ""))) and v["navn"] != "Bash"]
    mcp = {"mcpServers": {SERVERNAVN: {"command": sys.executable, "args": [str(MCP_SERVER)]}}}
    cmd = _grunnkommando(konfig, system) + [
        "--mcp-config", json.dumps(mcp),
        "--allowedTools", ",".join(tillatt),
        "--max-turns", str(MAKS_RUNDER),
    ]
    hendelser = _kjor(cmd, _samtale(meldinger), konfig, kjor)
    svar_tekst = _resultat(hendelser)

    kall: list[dict[str, Any]] = []
    resultater: dict[str, tuple[str, bool]] = {}
    rekkefolge: list[str] = []
    for h in hendelser:
        innhold = (h.get("message") or {}).get("content")
        if not isinstance(innhold, list):
            continue
        for b in innhold:
            if not isinstance(b, dict):
                continue
            if h.get("type") == "assistant" and b.get("type") == "tool_use":
                navn = str(b.get("name", ""))
                kall.append({"navn": navn.removeprefix(PREFIKS), "args": b.get("input"), "ok": True})
                rekkefolge.append(str(b.get("id")))
            elif h.get("type") == "user" and b.get("type") == "tool_result":
                resultater[str(b.get("tool_use_id"))] = (_innhold_tekst(b.get("content")), not b.get("is_error"))
    utdrag = []
    for k, tid in zip(kall, rekkefolge):
        r, ok = resultater.get(tid, ("", False))
        k["ok"] = ok
        utdrag.append(r)

    grunnlag: list[Any] = []
    for r in utdrag:
        try:
            grunnlag.append(json.loads(r))
        except json.JSONDecodeError:
            grunnlag.append(r)
    grunnlag += [m["tekst"] for m in meldinger if m["rolle"] == "bruker"]
    return {
        "tekst": svar_tekst,
        "merke": "AI-forslag",
        "modell": konfig.modell,
        "leverandor": konfig.leverandor,
        "verktoykall": kall,
        "data_hentet": [{**k, "utdrag": r[:800] + (" …" if len(r) > 800 else "")} for k, r in zip(kall, utdrag)],
        "tallkontroll": tallkontroll(svar_tekst, grunnlag),
    }
