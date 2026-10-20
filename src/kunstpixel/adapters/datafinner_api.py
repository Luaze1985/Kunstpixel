"""Åpent API for Datafinner: verktøyskjema og faste rapporter.

To ting en språkmodell (eller et annet program) trenger for å bruke Datafinner:

  1. verktoyskjema(): en maskinlesbar liste over verktøyene med parametere (JSON Schema). Kan oversettes
     direkte til verktøydefinisjoner for Claude, OpenAI, Ollama m.fl.
  2. lag_rapport(): den deterministiske rapporten for ett spørsmål: fakta fra databasen, og vurdering og
     forslag valgt av faste regler. Samme input gir alltid samme svar. Ingen KI er med.

Modulen kjører ingen verktøy selv. Den får en funksjon `kjor(navn, args)` fra serveren, slik at den samme
hviteliste og de samme sperrene gjelder.
"""

from __future__ import annotations

import inspect
import re
import types
import typing
from collections.abc import Callable
from typing import Any

# Hvert spørsmål peker på ett verktøy. Reglene i museum.db (rapport_regler) velger vurdering og forslag.
# Denne listen må stemme med spørsmålene i museum.db (rolle_sporsmal) og med index.html. Det vokter en test.
SPORSMAL: dict[str, dict[str, Any]] = {
    "vakt-i-dag": {"tekst": "Hvem har vakt i dag?", "verktoy": "get_staff_on_shift"},
    "vaktplan": {"tekst": "Vaktplan for en dag", "verktoy": "get_shifts_for_date"},
    "arbeidstid": {"tekst": "Arbeidstid i perioden", "verktoy": "get_working_hours_report"},
    "sykefravaer": {"tekst": "Sykefravær i museet", "verktoy": "get_absence_report"},
    "utstilling": {"tekst": "Økonomi per utstilling", "verktoy": "get_exhibition_economy"},
    "vaktkostnad": {"tekst": "Kostnad for vakter", "verktoy": "get_shift_cost_for_period"},
}


def regelverdier(sporsmal_id: str, fakta: Any) -> dict[str, float]:
    """Tallene fra svaret som reglene sammenlignes mot. Vaktplanen er en liste, så den telles."""
    if sporsmal_id == "vaktplan":
        return {"antall_vakter": len(fakta) if isinstance(fakta, list) else 0}
    if isinstance(fakta, dict):
        return {k: v for k, v in fakta.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    return {}


def lag_rapport(sporsmal_id: str, args: dict[str, Any], kjor: Callable[[str, dict[str, Any]], Any]) -> dict[str, Any]:
    """Lag den deterministiske rapporten. `kjor` er serverens run_tool (hvitelistet og med argumentkontroll)."""
    spec = SPORSMAL.get(sporsmal_id)
    if spec is None:
        raise ValueError(f"Ukjent spørsmål: {sporsmal_id}. Gyldige: {', '.join(sorted(SPORSMAL))}")
    fakta = kjor(spec["verktoy"], args)
    verdier = regelverdier(sporsmal_id, fakta)
    regel = kjor("get_report_assessment", {"sporsmal_id": sporsmal_id, "verdier": verdier})
    har_regel = "mangler" not in regel
    return {
        "sporsmal_id": sporsmal_id,
        "sporsmal": spec["tekst"],
        "verktoy": spec["verktoy"],
        "args": args,
        "fakta": fakta,
        "regelverdier": verdier,
        "vurdering": regel,
        # Samme ord som designsystemet Arbeidsflyt bruker. Ingenting er bekreftet før en person har sett på det.
        "merker": {
            "fakta": "Bør verifiseres",
            "vurdering": "Systemforslag" if har_regel else "Mangler",
            "forslag": "Systemforslag" if har_regel else "Mangler",
        },
        "status": "Utkast",
    }


# ---------- verktøyskjema ----------

def _json_type(tp: Any) -> str:
    """JSON Schema-typen for en Python-type. Ukjent blir tekst."""
    opprinnelse = typing.get_origin(tp)
    if opprinnelse in (typing.Union, types.UnionType):
        deler = [a for a in typing.get_args(tp) if a is not type(None)]
        return _json_type(deler[0]) if deler else "string"
    if opprinnelse is not None:
        tp = opprinnelse
    return {int: "integer", float: "number", bool: "boolean", dict: "object", list: "array", str: "string"}.get(tp, "string")


def _beskrivelser(doc: str) -> tuple[str, dict[str, str]]:
    """Første avsnitt som beskrivelse, og 'Args:'-linjene (Google-stil) som parameterbeskrivelser."""
    avsnitt = doc.strip().split("\n\n", 1)[0].replace("\n", " ").strip() if doc else ""
    params: dict[str, str] = {}
    if "Args:" in doc:
        blokk = doc.split("Args:", 1)[1].split("\n\n", 1)[0]
        for linje in blokk.splitlines():
            m = re.match(r"\s+(\w+):\s*(.+)", linje)
            if m:
                params[m.group(1)] = m.group(2).strip()
    return avsnitt, params


def verktoyskjema(verktoy: dict[str, tuple[Callable[..., Any], set[str]]]) -> list[dict[str, Any]]:
    """Beskriv hvert hvitelistet verktøy med JSON Schema for parameterne. Sortert på navn."""
    ut = []
    for navn in sorted(verktoy):
        fn, tillatt = verktoy[navn]
        try:
            hint = typing.get_type_hints(fn)
        except Exception:  # manglende import i en annotasjon skal ikke velte hele listen
            hint = {}
        sig = inspect.signature(fn)
        beskrivelse, param_tekst = _beskrivelser(inspect.getdoc(fn) or "")
        egenskaper: dict[str, Any] = {}
        pakrevd: list[str] = []
        for p in sorted(tillatt):
            egenskap: dict[str, Any] = {"type": _json_type(hint.get(p, str))}
            if p in param_tekst:
                egenskap["description"] = param_tekst[p]
            egenskaper[p] = egenskap
            par = sig.parameters.get(p)
            if par is not None and par.default is inspect.Parameter.empty:
                pakrevd.append(p)
        ut.append({
            "navn": navn,
            "beskrivelse": beskrivelse,
            "parametre": {"type": "object", "properties": egenskaper, "required": pakrevd, "additionalProperties": False},
        })
    return ut
