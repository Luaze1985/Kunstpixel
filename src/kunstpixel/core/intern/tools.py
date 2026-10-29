"""Skrivebeskyttede verktøy for intern assistent.

Ingen fri SQL, ingen fri filsti. Hvert verktøy leser bare de kildene det er laget for, og bare
det rollen har tilgang til. Alle funn har kilde, sti og klassifisering.

Verktøy: search_hms, search_ik_mat, search_brann_sikring, get_tilsyn, get_rolle, search_tiltak,
search_myndighet, search_rapportering, search_arbeidsoppgaver.
"""

from __future__ import annotations

from typing import Any

from src.kunstpixel.core.intern.data import Finding, InternData, role_id

TOOL_TEMA: dict[str, tuple[str, ...]] = {
    "search_hms": ("hms",),
    "search_ik_mat": ("ik_mat",),
    "search_brann_sikring": ("brann",),
    "get_tilsyn": ("tilsyn",),
    "get_rolle": ("rolle",),
    "search_tiltak": ("tiltak",),
    "search_myndighet": ("myndighet",),
    "search_rapportering": ("rapportering",),
    "search_arbeidsoppgaver": ("arbeidsoppgaver", "historikk"),
}

TOOL_NAMES: tuple[str, ...] = tuple(TOOL_TEMA)


class InternTools:
    def __init__(self, data: InternData | None = None) -> None:
        self.data = data if data is not None else InternData()

    # ---- felles ----

    def _error(self, code: str, message: str) -> dict[str, Any]:
        return {"error": message, "code": code, "funn": [], "antall": 0}

    def _pack(self, hits: list[tuple[float, Finding]]) -> dict[str, Any]:
        funn = [dict(f.to_dict(), score=round(s, 2)) for s, f in hits]
        return {"funn": funn, "antall": len(funn)}

    def _guard(self, tool: str, role: Any) -> dict[str, Any] | None:
        """Avvis ukjent rolle og roller uten tilgang til verktøyets kilder."""
        if role_id(role) is None:
            return self._error("UNKNOWN_ROLE", "Ukjent rolle. Ingen tilgang.")
        if self.data.restricted_for(role, TOOL_TEMA[tool]):
            return self._error("FORBIDDEN", f"Rollen har ikke tilgang til {tool}.")
        return None

    def call(self, name: str, role: Any, **kwargs: Any) -> dict[str, Any]:
        if name not in TOOL_TEMA:
            raise ValueError(f"Ukjent intern verktøy: '{name}'")
        return getattr(self, name)(role=role, **kwargs)

    # ---- verktøyene ----

    def _search(self, tool: str, query: str, role: Any, limit: int, bred: bool = False) -> dict[str, Any]:
        denied = self._guard(tool, role)
        if denied:
            return denied
        if not isinstance(query, str) or not query.strip():
            return self._error("EMPTY_QUERY", "Tomt søk.")
        return self._pack(self.data.search(query, role, TOOL_TEMA[tool], limit, bred))

    def search_hms(self, query: str, role: Any, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Søk i HMS og arbeidsmiljø: ergonomi, løft, verneutstyr, alenearbeid, varsling, vernerunder, avvik."""
        return self._search("search_hms", query, role, limit, bred)

    def search_ik_mat(self, query: str, role: Any, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Søk i IK-Mat for kaféen: temperaturer, hygiene, sykdom og karantene, renhold, skadedyr."""
        return self._search("search_ik_mat", query, role, limit, bred)

    def search_brann_sikring(self, query: str, role: Any, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Søk i brann, sikring og kapasitet: personantall per rom, rømningsveier, evakuering av kunst."""
        return self._search("search_brann_sikring", query, role, limit, bred)

    def get_tilsyn(self, role: Any, query: str | None = None, maaned: str | None = None, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Tilsynskalenderen: hva, når, myndighet og ansvarlig rolle. Filtrer på måned eller søk fritt."""
        denied = self._guard("get_tilsyn", role)
        if denied:
            return denied
        from src.kunstpixel.core.intern.data import fold

        if maaned and maaned.strip():
            m = fold(maaned.strip())
            hits = [
                (1.0, f)
                for f in self.data.for_role(role, TOOL_TEMA["get_tilsyn"])
                if f.sti.lower().endswith(m) or fold(f.sti).split(" › ")[-1] == m
            ]
            return self._pack(hits[:limit])
        if not isinstance(query, str) or not query.strip():
            return self._error("EMPTY_QUERY", "Oppgi måned eller søketekst.")
        return self._pack(self.data.search(query, role, TOOL_TEMA["get_tilsyn"], limit, bred))

    def get_rolle(self, role: Any, rolle: str | None = None, query: str | None = None, limit: int = 8, bred: bool = False) -> dict[str, Any]:
        """Roller og ansvar. Med `rolle`: alt om rollen. Med `query`: fritekstsøk."""
        denied = self._guard("get_rolle", role)
        if denied:
            return denied
        if rolle and rolle.strip():
            rid = role_id(rolle)
            if rid is None:
                return self._pack([])
            hits = [(1.0, f) for f in self.data.for_role(role, TOOL_TEMA["get_rolle"]) if f.rolle == rid]
            return self._pack(hits[: max(1, min(int(limit), 20))])
        if not isinstance(query, str) or not query.strip():
            return self._error("EMPTY_QUERY", "Oppgi rolle eller søketekst.")
        return self._pack(self.data.search(query, role, TOOL_TEMA["get_rolle"], limit, bred))

    def search_tiltak(self, query: str, role: Any, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Søk i prioriterte tiltak (No Excuse). Bare for ledelsesroller."""
        return self._search("search_tiltak", query, role, limit, bred)

    def search_myndighet(self, query: str, role: Any, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Søk i myndighetskontakter og tilsynsbesøksrutine."""
        return self._search("search_myndighet", query, role, limit, bred)

    def search_rapportering(self, query: str, role: Any, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Søk i rapporteringskalender og rapportmaler."""
        return self._search("search_rapportering", query, role, limit, bred)

    def search_arbeidsoppgaver(self, query: str, role: Any, limit: int = 5, bred: bool = False) -> dict[str, Any]:
        """Søk i gjentakende arbeidsoppgaver, tidsbruk, automatiseringspotensial og 17-årshistorikk. Bare for ledelsen."""
        return self._search("search_arbeidsoppgaver", query, role, limit, bred)
