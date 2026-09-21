"""FastMCP server for Aura Kunstmuseum exposing 5 collection and visitor tools.

Strictly read-only, SQL-injection safe, and adhering to museum domain terminology.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from src.kunstpixel.core.db import (
    VALID_ROOM_IDS,
    normalize_room_identifier,
    query_artwork_details,
    query_collection,
    query_events,
    query_faq,
    query_room_artworks,
)

# Initialize FastMCP application
mcp = FastMCP("Kunstpixel")


@mcp.tool()
def search_collection(
    query: str | None = None,
    artist: str | None = None,
    title: str | None = None,
    technique: str | None = None,
    theme: str | None = None,
    room_id: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Søk i museets samling etter verk basert på kunstner, tittel, teknikk, tema eller sal.

    Args:
        query: Fritekstsøk i tittel, kunstner, teknikk, temaer, sal og beskrivelse.
        artist: Filtrer på kunstnerens navn (f.eks. 'Theodor Kittelsen' eller 'Kittelsen').
        title: Filtrer på verktittel (f.eks. 'Skrik' eller 'Nøkken').
        technique: Filtrer på teknikk (f.eks. 'Olje på lerret' eller 'Pastell').
        theme: Filtrer på tematisk emneord (f.eks. 'mytologi', 'natur', 'angst').
        room_id: Filtrer på sal-ID (f.eks. 'SAL-A', 'SAL-D').
        limit: Maksimalt antall verk (standard 10, maks 50).

    Returns:
        Liste med verkskort som matcher kriteriene.
    """
    return query_collection(
        query=query,
        artist=artist,
        title=title,
        technique=technique,
        theme=theme,
        room_id=room_id,
        limit=limit,
    )


@mcp.tool()
def get_artwork_details(artwork_id: str) -> dict[str, Any]:
    """Hent komplette og autoritative metadata for et spesifikt kunstverk, inkludert veggtekst og proveniens.

    Args:
        artwork_id: Kunstverkets unike inventarnummer (f.eks. 'AURA-2026-009') eller eksakt tittel.

    Returns:
        Fullstendig verkskort med kunstnerbiografi, teknikk, sal, tilstand, veggtekst og proveniens.
        Returnerer strukturert feilobjekt med code='NOT_FOUND' dersom verket ikke finnes.
    """
    details = query_artwork_details(artwork_id)
    if details is None:
        return {
            "error": f"Verk med ID eller tittel '{artwork_id}' ble ikke funnet i samlingsdatabasen.",
            "artwork_id": artwork_id,
            "code": "NOT_FOUND",
        }
    return details


@mcp.tool()
def get_room_artworks(room_id: str) -> list[dict[str, Any]] | dict[str, Any]:
    """List alle utstilte verk i en gitt sal, ordnet etter visningsrekkefølge.

    Args:
        room_id: Salens identifikator (f.eks. 'SAL-A', 'SAL-B', 'SAL-C', 'SAL-D', 'SAL-E', 'MAG-1').

    Returns:
        Liste over utstilte verk i salen ordnet etter visningsrekkefølge.
        Returnerer feilmelding dersom sal-ID er ugyldig.
    """
    norm_room = normalize_room_identifier(room_id)
    if norm_room not in VALID_ROOM_IDS:
        return {
            "error": f"Ukjent sal-ID '{room_id}'",
            "valid_rooms": VALID_ROOM_IDS,
            "code": "INVALID_ROOM",
        }
    return query_room_artworks(room_id)


@mcp.tool()
def search_events(
    event_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Finn kommende hendelser og arrangementer på museet (omvisninger, verksteder, foredrag).

    Args:
        event_type: Type hendelse (f.eks. 'omvisning', 'verksted', 'foredrag', 'barnearrangement').
        date_from: Fra og med dato (ISO-format YYYY-MM-DD). Standard er dagens dato.
        date_to: Til og med dato (ISO-format YYYY-MM-DD).
        limit: Maksimalt antall hendelser som returneres (standard 5).

    Returns:
        Liste over bekreftede og planlagte arrangementer med dato, tid, sal og billettpriser.
    """
    return query_events(
        event_type=event_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )


@mcp.tool()
def search_faq(
    query: str,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Søk i publikums-FAQ etter autoritative svar på praktiske spørsmål.

    Args:
        query: Søkeord fra den besøkendes spørsmål (f.eks. 'åpningstider', 'pris', 'billett', 'kafé', 'parkering').
        category: Valgfri kategori for filtrering (f.eks. 'billett', 'praktisk', 'fasiliteter', 'formidling').

    Returns:
        Liste med relevante FAQ-oppslag rangert etter relevans og hyppighet.
    """
    return query_faq(query=query, category=category)


if __name__ == "__main__":
    mcp.run()
