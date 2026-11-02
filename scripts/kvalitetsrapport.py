"""Én samlet kvalitetsrapport for Lars (0 tokens). Skrives av de stille sjekkene i VS Code og git.

Sjekkene kjører i bakgrunnen og viser ingenting. Hver av dem erstatter bare sin egen seksjon i
.scratch/kvalitet/RAPPORT.md, så rapporten alltid viser siste resultat fra hver:

  apning   VS Code åpnes            (db_kvalitet.py mot museum.db)
  lagring  en datafil i 05_data lagres (db_kvalitet.py --fra-data)
  commit   noen committer            (statusporten, via scripts/githooks/pre-commit)

Fra kommandolinjen (innholdet leses fra stdin):
    <kommando> | py -3.13 scripts/kvalitetsrapport.py commit OK|OBS|FEIL
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAPPORT = ROOT / ".scratch" / "kvalitet" / "RAPPORT.md"

SEKSJONER = {
    "apning": "Når VS Code åpnes (museum.db slik den ligger)",
    "lagring": "Når en datafil i 05_data lagres (bygget fra datafilene)",
    "commit": "Ved siste commit (statusporten)",
}
STATUSER = ("OK", "OBS", "FEIL")
_SEKSJON = re.compile(
    r"<!-- seksjon:(\w+) status:(\w+) tid:(.+?) -->\n## .*?\n\n```text\n(.*?)\n```\n<!-- /seksjon -->", re.S
)


def les(sti: Path = RAPPORT) -> dict[str, tuple[str, str, str]]:
    """Seksjonene som finnes: navn -> (status, tid, innhold)."""
    if not sti.is_file():
        return {}
    return {m[1]: (m[2], m[3], m[4]) for m in _SEKSJON.finditer(sti.read_text(encoding="utf-8"))}


def oppdater(seksjon: str, status: str, innhold: str, sti: Path = RAPPORT, na: datetime | None = None) -> Path:
    if seksjon not in SEKSJONER:
        raise ValueError(f"Ukjent seksjon: {seksjon}. Gyldige: {', '.join(SEKSJONER)}")
    if status not in STATUSER:
        raise ValueError(f"Ukjent status: {status}. Gyldige: {', '.join(STATUSER)}")
    data = les(sti)
    data[seksjon] = (status, (na or datetime.now()).strftime("%Y-%m-%d %H:%M"), innhold.strip().replace("```", "'''"))

    linjer = [
        "# Kvalitetsrapport",
        "",
        "Sjekkene kjører av seg selv i bakgrunnen. Her står siste resultat fra hver av dem.",
        "OK = alt i orden. OBS = du bør ta stilling til noe. FEIL = noe må rettes.",
        "",
        "| Når | Sist kjørt | Resultat |",
        "|---|---|---|",
    ]
    for navn, tittel in SEKSJONER.items():
        status_, tid, _ = data.get(navn, ("-", "ikke kjørt ennå", ""))
        linjer.append(f"| {tittel} | {tid} | **{status_}** |")
    for navn, tittel in SEKSJONER.items():
        if navn in data:
            status_, tid, tekst = data[navn]
            linjer += ["", f"<!-- seksjon:{navn} status:{status_} tid:{tid} -->", f"## {tittel}", "",
                       "```text", tekst, "```", "<!-- /seksjon -->"]

    sti.parent.mkdir(parents=True, exist_ok=True)
    midlertidig = sti.with_suffix(".tmp")
    midlertidig.write_text("\n".join(linjer) + "\n", encoding="utf-8")
    os.replace(midlertidig, sti)  # hel fil eller ingenting, også om to sjekker skriver samtidig
    return sti


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    innhold = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    oppdater(argv[0], argv[1], innhold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
