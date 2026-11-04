"""Oppslagsmotor for Kunstpixel virksomhetshåndbøker (spec internside-oppslagsverk).

Tilbyr deterministisk søk i museets håndbøker (Personal, HMS, Drift/Kvalitet, Ledelse/Beredskap)
og operative rutiner i museum.db uten AI, samt kildetvunget AI-svar med kildekontroll.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from src.kunstpixel.core import llm
from src.kunstpixel.core.db import query_handbook


def sok(
    sporsmal: str,
    handbok: str | None = None,
    role: str | None = None,
    db_path: Path | str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Søker deterministisk i håndbøkene i museum.db.

    Hvert treff har minst:
    - punkt_id: str (f.eks. 'PERSONAL-5.2')
    - handbok_kode: str ('PERSONAL', 'DRIFT_KVALITET', 'HMS_SIKKERHET', 'LEDER_BEREDSKAP', 'RUTINER_SOP')
    - avsnitt_tittel: str
    - innhold: str
    Samt tilleggsfelter: handbok_navn, kapittel_nr, kapittel_tittel, lovhjemmel, stikkord.
    """
    if not sporsmal or not sporsmal.strip():
        return []

    return query_handbook(
        query=sporsmal.strip(),
        handbok=handbok,
        role=role,
        limit=limit,
        db_path=db_path,
    )


def svar(
    sporsmal: str,
    konfig: llm.LlmKonfig | None = None,
    begrenser: llm.Begrenser | None = None,
    apne: Any = urllib.request.urlopen,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Håndbokoppslag med et kort AI-svar over treffene. Treffene kommer alltid med."""
    treff = sok(sporsmal, db_path=db_path)
    if not treff:
        return {"treff": [], "ai": None, "status": "ingen_kilde"}
    if konfig is None:
        return {"treff": treff, "ai": None, "status": "ai_av"}
    if begrenser is not None and not begrenser.tillat():
        return {"treff": treff, "ai": None, "status": "grense_naadd"}
    try:
        ai = llm.svar_fra_handbok(sporsmal, treff, konfig, apne=apne)
    except llm.LlmFeil as feil:
        return {"treff": treff, "ai": None, "status": "ai_feil", "feilkode": feil.kode, "melding": str(feil)}
    return {"treff": treff, "ai": ai, "status": "ok"}
