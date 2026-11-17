"""E-postmaler som data (spec datafinner-ledelse, B9).

Utkastet fylles på serveren med fakta fra databasen og åpnes som `mailto:` i nettleseren.
Ingenting sendes fra appen. Malene spør aldri om diagnose eller årsak (sykefravær).
"""

from __future__ import annotations

import re
from typing import Any

PLASSHOLDERE = {"tittel", "frist_dato", "frist_tekst", "kilde", "vurdering"}
_FELT = re.compile(r"\{([a-z_]+)\}")
_MAKS = 300

_SLUTT = "\n\nKilde: {kilde} (Kunstpixel, syntetiske øvingsdata)."
MALER: dict[str, dict[str, str]] = {
    "sykefravaer": {
        "overskrift": "Oppfølging: {tittel}",
        "tekst": "Hei,\n\n{tittel} har frist {frist_dato} ({frist_tekst}).\n"
                 "Kan vi finne en tid som passer for samtalen?" + _SLUTT,
    },
    "aapen_sak": {
        "overskrift": "Oppfølging: {tittel}",
        "tekst": "Hei,\n\nSaken «{tittel}» er fortsatt åpen. Frist var {frist_dato} ({frist_tekst}).\n"
                 "Kan du gi en kort status og når den kan lukkes?" + _SLUTT,
    },
    "rapportfrist": {
        "overskrift": "Oppfølging: {tittel}",
        "tekst": "Hei,\n\n{tittel} har frist {frist_dato} ({frist_tekst}).\n"
                 "Hvordan ligger vi an?" + _SLUTT,
    },
    "tilstand": {
        "overskrift": "Oppfølging: {tittel}",
        "tekst": "Hei,\n\n{tittel} skulle vært gjort innen {frist_dato} ({frist_tekst}).\n"
                 "Kan du sette opp en ny kontroll?" + _SLUTT,
    },
    "innlan": {
        "overskrift": "Oppfølging: {tittel}",
        "tekst": "Hei,\n\n{tittel}: utstillingen sluttet {frist_dato} ({frist_tekst}).\n"
                 "Kan du bekrefte status for returen?" + _SLUTT,
    },
    "rapport": {
        "overskrift": "Rapport: {tittel}",
        "tekst": "Hei,\n\nHer er «{tittel}».\n\nVurdering: {vurdering}" + _SLUTT,
    },
}
_MAL_FOR_TYPE = {
    "sykefravaer_uke4": "sykefravaer", "sykefravaer_uke7": "sykefravaer",
    "driftsmelding": "aapen_sak", "hms_avvik": "aapen_sak",
    "rapport": "rapportfrist", "tilstandskontroll": "tilstand", "innlan": "innlan",
}


def _vask(verdi: Any) -> str:
    """Én linje, kort. Hindrer at en verdi lager nye linjer i emnet."""
    return re.sub(r"\s*[\r\n]+\s*", " ", str(verdi)).strip()[:_MAKS]


def fyll_mal(mal: str, verdier: dict[str, Any]) -> str:
    """Sett inn verdiene i én omgang. Feiler hvis en plassholder mangler. Ekstra verdier ignoreres."""
    mangler = sorted({f for f in _FELT.findall(mal) if f not in verdier})
    if mangler:
        raise ValueError(f"Mangler verdi for {', '.join(mangler)}")
    return _FELT.sub(lambda m: _vask(verdier[m.group(1)]), mal)


def _frist_tekst(dager: int) -> str:
    """Samme ord som fristTekst i ledelse.js."""
    if dager == 0:
        return "i dag"
    n = abs(dager)
    ord_ = "dag" if n == 1 else "dager"
    return f"{n} {ord_} over fristen" if dager < 0 else f"om {n} {ord_}"


def _utkast(mal_id: str, verdier: dict[str, Any]) -> dict[str, str]:
    mal = MALER[mal_id]
    return {"overskrift": fyll_mal(mal["overskrift"], verdier), "tekst": fyll_mal(mal["tekst"], verdier)}


def utkast_for_frist(frist: dict[str, Any]) -> dict[str, str] | None:
    """E-postutkast for én frist fra get_my_deadlines. None for ukjente typer."""
    mal_id = _MAL_FOR_TYPE.get(frist.get("type"))
    if mal_id is None:
        return None
    return _utkast(mal_id, {"tittel": frist["tittel"], "frist_dato": frist["frist_dato"],
                            "frist_tekst": _frist_tekst(int(frist["dager_til"])), "kilde": frist["kilde"]})


def utkast_for_rapport(rapport: dict[str, Any]) -> dict[str, str]:
    """E-postutkast for en deterministisk rapport: spørsmålet, vurderingen fra regelen og verktøyet."""
    v = rapport.get("vurdering") or {}
    return _utkast("rapport", {"tittel": rapport["sporsmal"],
                               "vurdering": v.get("vurdering") or v.get("mangler") or "Ingen regel for dette spørsmålet.",
                               "kilde": f"museum.db via {rapport['verktoy']}"})
