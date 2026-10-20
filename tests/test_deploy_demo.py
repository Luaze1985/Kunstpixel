"""Statiske tester for hostingoppsettet (deploy/demo). De kjører ikke Docker.

Selve oppsettet testes ende til ende av scripts/test_demo_container.ps1 (krever Docker). Her sikrer vi
at reglene som holder demoen trygg ikke forsvinner ved en senere endring.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "deploy" / "demo"
INTERNE_MAPPER = ("01_inbox", "02_deliverables", "03_team", "04_knowledge", "00_felles", "arkiv")


def _les(navn: str) -> str:
    return (DEMO / navn).read_text(encoding="utf-8")


def _krav() -> dict[str, str]:
    ut = {}
    for linje in _les("requirements.txt").splitlines():
        linje = linje.strip()
        if linje and not linje.startswith("#"):
            navn, versjon = linje.split("==")  # alt skal være låst med ==
            ut[navn.lower()] = versjon
    return ut


def test_alle_krav_i_bildet_er_last_til_en_versjon() -> None:
    linjer = [linje.strip() for linje in _les("requirements.txt").splitlines() if linje.strip() and not linje.startswith("#")]
    assert linjer and all("==" in linje for linje in linjer)


def test_laste_versjoner_oppfyller_kravene_i_pyproject() -> None:
    """Bildet bruker låste versjoner, men de skal ikke stride mot det prosjektet krever."""
    from packaging.requirements import Requirement
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["dependencies"]
    krav = {Requirement(r).name.lower(): Requirement(r) for r in pyproject}
    for navn, versjon in _krav().items():
        if navn in krav:
            assert versjon in krav[navn].specifier, f"{navn}=={versjon} oppfyller ikke {krav[navn]}"


def test_bildet_har_alle_pakkene_koden_importerer() -> None:
    """Skanner koden som kopieres inn. Importerer den en tredjepartspakke som ikke står i requirements.txt,
    feiler containeren først på serveren (slik mcp 2.x gjorde). Forste-parts og standardbibliotek er unntatt."""
    import ast
    import sys
    kjent = {"mcp": "mcp", "pydantic": "pydantic", "yaml": "pyyaml"}  # importnavn -> pakkenavn
    kode = list((ROOT / "src/kunstpixel/core").glob("*.py")) + [ROOT / "src/kunstpixel/adapters/datafinner.py"]
    mangler = set()
    for fil in kode:
        for node in ast.walk(ast.parse(fil.read_text(encoding="utf-8"))):
            moduler = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                      [node.module] if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module else []
            for modul in moduler:
                topp = modul.split(".")[0]
                if topp in sys.stdlib_module_names or topp in ("src", "__future__"):
                    continue
                pakke = kjent.get(topp)
                if pakke is None or pakke not in _krav():
                    mangler.add(f"{topp} (i {fil.name})")
    assert not mangler, f"Ikke i requirements.txt: {sorted(mangler)}"


def test_dockerfile_kjorer_som_vanlig_bruker_i_demomodus() -> None:
    d = _les("Dockerfile")
    assert "USER 10001:10001" in d
    assert "DATAFINNER_DEMO=1" in d
    assert "KUNSTPIXEL_DB_PATH=/app/data/museum_demo.db" in d


def test_dockerfile_tar_ikke_med_interne_mapper_eller_hele_repoet() -> None:
    d = _les("Dockerfile")
    kopier = [linje for linje in d.splitlines() if linje.startswith("COPY")]
    assert kopier
    for linje in kopier:
        assert not re.search(r"COPY\s+(--from=\w+\s+)?\.\s", linje), linje
        for mappe in INTERNE_MAPPER:
            assert mappe not in linje, linje
    # museum.db hentes bare inn i byggetrinnet. Sluttbildet får bare demokopien.
    sluttbilde = d.split("AS bygg", 1)[1].split("FROM python", 1)[1]
    assert "05_data/museum.db" not in sluttbilde
    assert "COPY --from=bygg /ut/museum_demo.db" in sluttbilde


def test_byggekonteksten_er_en_tillatelsesliste() -> None:
    linjer = [linje.strip() for linje in _les("Dockerfile.dockerignore").splitlines() if linje.strip() and not linje.startswith("#")]
    assert linjer[0] == "*"
    tillatt = {linje[1:] for linje in linjer if linje.startswith("!")}
    assert tillatt == {"src", "05_data/museum.db", "deploy/demo/requirements.txt"}


def _tjenester() -> dict:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_load(_les("compose.yaml"))["services"]


def test_bare_caddy_er_apen_mot_nettet() -> None:
    t = _tjenester()
    assert "ports" not in t["datafinner"]
    assert t["caddy"]["ports"]
    assert t["datafinner"]["expose"] == ["8010"]


@pytest.mark.parametrize("tjeneste", ["datafinner", "caddy"])
def test_containerne_er_last_ned(tjeneste: str) -> None:
    c = _tjenester()[tjeneste]
    assert c["read_only"] is True
    assert c["cap_drop"] == ["ALL"]
    assert "no-new-privileges:true" in c["security_opt"]
    assert c["mem_limit"] and c["pids_limit"]


def test_caddy_krever_innlogging_og_sender_til_datafinner() -> None:
    c = _les("Caddyfile")
    assert "basic_auth bcrypt" in c
    assert "import /etc/caddy/brukere.caddy" in c
    assert "reverse_proxy datafinner:8010" in c
    assert c.index("basic_auth") < c.index("reverse_proxy"), "Innlogging må komme før proxyen"


def test_ingen_hemmeligheter_i_eksempelfilen() -> None:
    linjer = [linje for linje in _les(".env.example").splitlines() if linje.strip() and not linje.startswith("#")]
    assert linjer == ["DEMO_DOMAIN=demo.mittnavn.no"]


def test_brukerliste_og_env_er_ikke_i_git() -> None:
    ignorert = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "deploy/demo/brukere.caddy" in ignorert
    assert "deploy/demo/.env" in ignorert


def test_skript_til_serveren_har_lf_og_er_markert_i_gitattributes() -> None:
    attr = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "deploy/demo/*.sh text eol=lf" in attr
    for sh in DEMO.glob("*.sh"):
        data = sh.read_bytes()
        assert b"\r" not in data, f"{sh.name} har Windows-linjeskift og vil feile på Linux"
        assert data.startswith(b"#!/usr/bin/env bash"), sh.name


def test_serveroppsettet_sjekker_nokkel_for_det_slar_av_passord() -> None:
    s = _les("server-oppsett.sh")
    assert s.index("authorized_keys") < s.index("PasswordAuthentication no")
    assert "ufw allow OpenSSH" in s and "ufw allow 80/tcp" in s and "ufw allow 443/tcp" in s
    assert "curl" not in s and "get.docker.com" not in s, "Ingen nedlasting av skript fra nettet"


def test_brukerskriptet_tar_ikke_imot_passord() -> None:
    b = _les("bruker.sh")
    assert "caddy hash-password" in b
    assert "--plaintext" not in b and "read -s" not in b


def test_bildet_har_alle_adaptermodulene_datafinner_importerer() -> None:
    """datafinner.py importerer egne moduler fra adapters/. Mangler en i Dockerfile, krasjer containeren ved oppstart."""
    import ast
    d = _les("Dockerfile")
    kilde = ast.parse((ROOT / "src/kunstpixel/adapters/datafinner.py").read_text(encoding="utf-8"))
    for node in ast.walk(kilde):
        if isinstance(node, ast.ImportFrom) and node.module == "src.kunstpixel.adapters":
            for navn in node.names:
                assert f"adapters/{navn.name}.py" in d, f"{navn.name}.py mangler i Dockerfile"


def test_ki_noekkelen_kommer_fra_miljoet_og_ingen_ligger_i_filene() -> None:
    compose = _les("compose.yaml")
    assert "LLM_API_KEY: ${LLM_API_KEY:-}" in compose
    assert "LLM_PROVIDER: ${LLM_PROVIDER:-}" in compose, "Tom verdi skal bety at KI-laget er av"
    ukommentert = [linje for linje in _les(".env.example").splitlines() if linje.strip() and not linje.startswith("#")]
    assert not any(linje.startswith("LLM_") for linje in ukommentert), "KI-laget skal være av i eksempelfilen"
    for fil in ("Dockerfile", "compose.yaml", "Caddyfile", ".env.example"):
        assert not re.search(r"sk-[A-Za-z0-9_-]{16,}", _les(fil)), f"Ser ut som en nøkkel i {fil}"
