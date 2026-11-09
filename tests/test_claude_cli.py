"""KI via din egen Claude (claude-kommandoen) i stedet for API-nøkkel (DECISIONS 2026-11-09, punkt 14).

Sikkerhet først: Claude skal bare få Kunstpixel-verktøyene på Datafinners hviteliste, ingen innebygde
verktøy (kommandolinje, filer), ingen innstillinger eller hooks fra brukeren, og ingen lagret økt.
Spørsmålet sendes på stdin, ikke på kommandolinjen. Feilmeldinger til nettleseren lekker ikke detaljer.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from src.kunstpixel.core import claude_cli, llm

KONFIG = llm.LlmKonfig(leverandor="claude-cli", modell="sonnet", timeout=60.0)
VERKTOY = [{"navn": "get_room_artworks", "beskrivelse": "", "parametre": {}},
           {"navn": "search_faq", "beskrivelse": "", "parametre": {}}]


def _linjer(*hendelser: dict[str, Any]) -> str:
    return "\n".join(json.dumps(h, ensure_ascii=False) for h in hendelser) + "\n"


STROM_OK = _linjer(
    {"type": "system", "subtype": "init", "tools": ["mcp__kunstpixel__get_room_artworks"]},
    {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "t1", "name": "mcp__kunstpixel__get_room_artworks", "input": {"room_id": "SAL-A"}}]}},
    {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": "t1", "content": [{"type": "text", "text": '{"result": [{"id": "KP-2026-001"}, {"id": "KP-2026-002"}, {"id": "KP-2026-003"}, {"id": "KP-2026-004"}]}'}]}]}},
    {"type": "result", "subtype": "success", "is_error": False, "result": "Sal A har blant annet KP-2026-001 og KP-2026-004."},
)


class FalskKjoring:
    def __init__(self, stdout: str = STROM_OK, returncode: int = 0, stderr: str = "", unntak: Exception | None = None):
        self.stdout, self.returncode, self.stderr, self.unntak = stdout, returncode, stderr, unntak
        self.kall: list[dict[str, Any]] = []

    def __call__(self, cmd: list[str], **kw: Any) -> subprocess.CompletedProcess:
        self.kall.append({"cmd": cmd, **kw})
        if self.unntak:
            raise self.unntak
        return subprocess.CompletedProcess(cmd, self.returncode, self.stdout, self.stderr)


def _verdi(cmd: list[str], flagg: str) -> str:
    return cmd[cmd.index(flagg) + 1]


# ---------- konfig ----------

def test_konfig_godtar_claude_cli_uten_nokkel_og_med_standardmodell() -> None:
    k = llm.fra_miljo({"LLM_PROVIDER": "claude-cli"})
    assert k is not None and k.leverandor == "claude-cli" and k.modell == "sonnet" and k.api_key == ""


# ---------- sikkerhet i kommandoen ----------

def test_kommandoen_er_last_ned() -> None:
    kjor = FalskKjoring()
    claude_cli.chat([{"rolle": "bruker", "tekst": "Hvor mange verk i sal A?"}], VERKTOY, KONFIG, "system", kjor=kjor)
    kall = kjor.kall[0]
    cmd = kall["cmd"]
    assert _verdi(cmd, "--tools") == ""  # ingen innebygde verktøy: ingen Bash, Edit, Write, Read, WebFetch
    assert "--strict-mcp-config" in cmd  # bare MCP-serveren vi gir den
    assert _verdi(cmd, "--setting-sources") == ""  # ingen hooks eller innstillinger fra brukeren
    assert "--no-session-persistence" in cmd
    assert _verdi(cmd, "--permission-mode") == "default"  # aldri bypassPermissions
    tillatt = _verdi(cmd, "--allowedTools").split(",")
    assert sorted(tillatt) == ["mcp__kunstpixel__get_room_artworks", "mcp__kunstpixel__search_faq"]
    mcp = json.loads(_verdi(cmd, "--mcp-config"))
    assert list(mcp["mcpServers"]) == ["kunstpixel"]
    for farlig in ("bypassPermissions", "--dangerously-skip-permissions", "Bash", "Edit", "Write"):
        assert farlig not in cmd


def test_sporsmalet_sendes_paa_stdin_og_ikke_paa_kommandolinjen() -> None:
    kjor = FalskKjoring()
    hemmelig_tekst = "Tekst som ikke skal stå i prosesslisten"
    claude_cli.chat([{"rolle": "bruker", "tekst": hemmelig_tekst}], VERKTOY, KONFIG, "system", kjor=kjor)
    kall = kjor.kall[0]
    assert all(hemmelig_tekst not in a for a in kall["cmd"])
    assert hemmelig_tekst in kall["input"]


def test_kjores_i_tom_mappe_utenfor_prosjektet() -> None:
    kjor = FalskKjoring()
    claude_cli.chat([{"rolle": "bruker", "tekst": "x"}], VERKTOY, KONFIG, "system", kjor=kjor)
    cwd = Path(kjor.kall[0]["cwd"]).resolve()
    rot = Path(__file__).resolve().parents[1]
    assert rot not in (cwd, *cwd.parents)  # ingen CLAUDE.md eller .mcp.json fra prosjektet lastes


def test_verktoy_utenfor_hvitelisten_slipper_ikke_inn() -> None:
    kjor = FalskKjoring()
    verktoy = VERKTOY + [{"navn": "Bash", "beskrivelse": "", "parametre": {}}, {"navn": "x; rm -rf", "beskrivelse": "", "parametre": {}}]
    claude_cli.chat([{"rolle": "bruker", "tekst": "x"}], verktoy, KONFIG, "system", kjor=kjor)
    tillatt = _verdi(kjor.kall[0]["cmd"], "--allowedTools").split(",")
    assert all(t.startswith("mcp__kunstpixel__") for t in tillatt)
    assert not any("rm" in t or t.endswith("__Bash") for t in tillatt)


# ---------- svar ----------

def test_svaret_faar_samme_form_som_api_veien() -> None:
    svar = claude_cli.chat([{"rolle": "bruker", "tekst": "Hvor mange verk i sal A?"}], VERKTOY, KONFIG, "system", kjor=FalskKjoring())
    assert svar["tekst"] == "Sal A har blant annet KP-2026-001 og KP-2026-004."
    assert svar["merke"] == "AI-forslag"
    assert svar["leverandor"] == "claude-cli"
    assert svar["verktoykall"] == [{"navn": "get_room_artworks", "args": {"room_id": "SAL-A"}, "ok": True}]
    assert "KP-2026-001" in svar["data_hentet"][0]["utdrag"]
    assert svar["tallkontroll"]["ok"] is True


def test_tall_som_ikke_finnes_i_dataene_flagges() -> None:
    strom = STROM_OK.replace("KP-2026-004.", "KP-2026-004, og 9 verk til.")
    svar = claude_cli.chat([{"rolle": "bruker", "tekst": "sal A"}], VERKTOY, KONFIG, "system", kjor=FalskKjoring(stdout=strom))
    assert "9" in svar["tallkontroll"]["ukjente_tall"]


def test_historikken_tas_med() -> None:
    kjor = FalskKjoring()
    meldinger = [{"rolle": "bruker", "tekst": "Første spørsmål"}, {"rolle": "assistent", "tekst": "Første svar"},
                 {"rolle": "bruker", "tekst": "Oppfølging"}]
    claude_cli.chat(meldinger, VERKTOY, KONFIG, "system", kjor=kjor)
    inn = kjor.kall[0]["input"]
    assert inn.index("Første spørsmål") < inn.index("Første svar") < inn.index("Oppfølging")


# ---------- feil ----------

def test_tidsavbrudd_gir_trygg_feil() -> None:
    kjor = FalskKjoring(unntak=subprocess.TimeoutExpired(["claude"], 60))
    with pytest.raises(llm.LlmFeil) as e:
        claude_cli.chat([{"rolle": "bruker", "tekst": "x"}], VERKTOY, KONFIG, "system", kjor=kjor)
    assert e.value.kode == "tidsavbrudd"


def test_manglende_claude_gir_tydelig_feil() -> None:
    kjor = FalskKjoring(unntak=FileNotFoundError("claude"))
    with pytest.raises(llm.LlmFeil) as e:
        claude_cli.chat([{"rolle": "bruker", "tekst": "x"}], VERKTOY, KONFIG, "system", kjor=kjor)
    assert e.value.kode == "leverandorfeil" and "Claude Code" in str(e.value)


def test_feil_fra_claude_lekker_ikke_detaljer() -> None:
    kjor = FalskKjoring(stdout="", returncode=1, stderr="Error at C:\\Users\\larse\\secret\\path token=abc123")
    with pytest.raises(llm.LlmFeil) as e:
        claude_cli.chat([{"rolle": "bruker", "tekst": "x"}], VERKTOY, KONFIG, "system", kjor=kjor)
    assert "larse" not in str(e.value) and "abc123" not in str(e.value)


def test_for_mange_runder() -> None:
    strom = _linjer({"type": "result", "subtype": "error_max_turns", "is_error": True})
    with pytest.raises(llm.LlmFeil) as e:
        claude_cli.chat([{"rolle": "bruker", "tekst": "x"}], VERKTOY, KONFIG, "system", kjor=FalskKjoring(stdout=strom))
    assert e.value.kode == "for_mange_runder"


# ---------- tekst uten verktøy (forklar, vaktrom, grense) ----------

def test_tekst_uten_verktoy_far_ingen_mcp() -> None:
    kjor = FalskKjoring(stdout=_linjer({"type": "result", "subtype": "success", "is_error": False, "result": "Forklaring."}))
    tekst = claude_cli.tekst("Rapport: 4 verk", KONFIG, "system", kjor=kjor)
    assert tekst == "Forklaring."
    cmd = kjor.kall[0]["cmd"]
    assert _verdi(cmd, "--tools") == "" and "--strict-mcp-config" in cmd
    assert "--mcp-config" not in cmd and "--allowedTools" not in cmd


def test_llm_ruter_til_claude_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(claude_cli, "tekst", lambda bruker_tekst, konfig, system, **kw: "Det er 4 verk.")
    svar = llm.utfor("4 verk", {"antall": 4}, KONFIG, "system")
    assert svar["tekst"] == "Det er 4 verk." and svar["tallkontroll"]["ok"] is True
    monkeypatch.setattr(claude_cli, "chat", lambda *a, **kw: {"tekst": "ok", "merke": "AI-forslag"})
    assert llm.chat_med_verktoy([{"rolle": "bruker", "tekst": "x"}], VERKTOY, None, KONFIG, "s")["tekst"] == "ok"


def test_markdown_fet_fjernes_fra_svaret() -> None:
    strom = _linjer({"type": "result", "subtype": "success", "is_error": False, "result": "1. **Nøkken** av Kittelsen"})
    assert claude_cli.tekst("x", KONFIG, "s", kjor=FalskKjoring(stdout=strom)) == "1. Nøkken av Kittelsen"
