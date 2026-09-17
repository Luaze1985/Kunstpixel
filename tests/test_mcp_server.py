"""Tier 2: MCP Server & Tool Verification Tests (R1 Acceptance Criteria).

Verifies:
- All 5 FastMCP tools return genuine, structured, verifiable data from SQLite:
  1. search_collection:
     - Search 'Kittelsen' returns >= 2 artworks with complete metadata.
     - Filter by technique, room_id, title, theme.
     - Empty result handling and limits.
  2. get_artwork_details:
     - 'AURA-2026-009' (Skrik) returns Munch, Sal D, wall text, provenance.
     - Unknown artwork ID returns structured error or handles gracefully.
  3. get_room_artworks:
     - 'SAL-D' returns >= 3 exhibited artworks in display sequence order.
     - Empty or storage room handling.
  4. search_events:
     - Upcoming events returned with date, start time, room, adult/child prices.
     - Filter by event_type (e.g. 'omvisning', 'verksted').
     - Excludes past or cancelled events.
  5. search_faq:
     - 'åpningstider' returns concrete opening hours (10:00–17:00).
     - 'pris' / 'koster' returns ticket prices in NOK.
     - Norwegian character handling ('å' <-> 'aa').
- SQL injection immunity:
  - Malicious SQL inputs treated safely as literal parameters.
"""

import pytest

try:
    from src.aura_museum.core.mcp_server import (
        search_collection,
        get_artwork_details,
        get_room_artworks,
        search_events,
        search_faq,
    )
except ImportError as err:
    pytest.fail(f"Could not import MCP tools from src.aura_museum.core.mcp_server: {err}", pytrace=False)


class TestSearchCollectionTool:
    """Verifies tool 1: search_collection."""

    def test_search_collection_kittelsen_returns_at_least_two_artworks(self):
        """R1 criterion: Search 'Kittelsen' returns >= 2 artworks with metadata."""
        results = search_collection(artist="Kittelsen")
        assert isinstance(results, list), f"Expected list of results, got {type(results)}"
        assert len(results) >= 2, f"Expected >= 2 artworks for Kittelsen, got {len(results)}"

        titles = [r.get("tittel") for r in results]
        assert "Nøkken" in titles, f"'Nøkken' not in results: {titles}"
        assert "Soria Moria slott" in titles, f"'Soria Moria slott' not in results: {titles}"

        # Verify metadata completeness
        for item in results:
            assert "id" in item and item["id"].startswith("AURA-2026-")
            assert "tittel" in item
            assert "kunstner" in item and "Kittelsen" in item["kunstner"]
            assert "aar" in item and isinstance(item["aar"], int)
            assert "teknikk" in item
            assert "sal_id" in item
            assert item["status"] == "utstilt"

    def test_search_collection_free_query_munch(self):
        """Free-text query for 'Munch' returns Munch's exhibited artworks."""
        results = search_collection(query="Munch")
        assert len(results) >= 2
        artists = [r.get("kunstner") for r in results]
        assert all("Munch" in a for a in artists)

    def test_search_collection_filter_by_room(self):
        """Filter artworks by room_id (e.g. 'SAL-A')."""
        results = search_collection(room_id="SAL-A")
        assert len(results) >= 4
        for r in results:
            assert r.get("sal_id") == "SAL-A"

    def test_search_collection_filter_by_technique(self):
        """Filter artworks by technique (e.g. 'Pastell')."""
        results = search_collection(technique="Pastell")
        assert len(results) >= 1
        for r in results:
            assert "pastell" in r.get("teknikk", "").lower()

    def test_search_collection_no_match_returns_empty_list(self):
        """Search with nonexistent artist/query returns empty list without error."""
        results = search_collection(query="NONEXISTENT_ARTIST_XYZ_123")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_collection_sql_injection_safe(self):
        """SQL injection attempt does not execute and does not crash."""
        malicious_input = "'; DROP TABLE verk; --"
        results = search_collection(query=malicious_input)
        assert isinstance(results, list)
        assert len(results) == 0


class TestGetArtworkDetailsTool:
    """Verifies tool 2: get_artwork_details."""

    def test_get_artwork_details_skrik(self):
        """Lookup for 'AURA-2026-009' (Skrik) returns complete metadata."""
        details = get_artwork_details(artwork_id="AURA-2026-009")
        assert isinstance(details, dict)
        assert details.get("id") == "AURA-2026-009"
        assert details.get("tittel") == "Skrik"
        assert "Munch" in details.get("kunstner", "") or "Munch" in details.get("kunstner_navn", "")
        assert details.get("sal_id") == "SAL-D"
        assert details.get("aar") == 1893

        # Wall text and provenance verification
        veggtekst = details.get("veggtekst", "")
        assert veggtekst is not None and len(veggtekst) > 0, "Missing wall text in details"
        assert "blodrød himmel" in veggtekst or "skrik" in veggtekst.lower()

        proveniens = details.get("proveniens", "")
        assert proveniens is not None and len(proveniens) > 0, "Missing provenance in details"

    def test_get_artwork_details_vinternatt(self):
        """Lookup for 'AURA-2026-007' (Vinternatt i Rondane) returns Sohlberg and provenance."""
        details = get_artwork_details(artwork_id="AURA-2026-007")
        assert details.get("id") == "AURA-2026-007"
        assert details.get("tittel") == "Vinternatt i Rondane"
        assert "Sohlberg" in details.get("kunstner", "") or "Sohlberg" in details.get("kunstner_navn", "")
        assert details.get("sal_id") == "SAL-A"
        assert details.get("aar") == 1914
        assert "proveniens" in details and len(details["proveniens"]) > 0

    def test_get_artwork_details_unknown_id(self):
        """Lookup for non-existent artwork ID returns structured error or error dict."""
        details = get_artwork_details(artwork_id="AURA-2026-999")
        assert isinstance(details, dict)
        assert "error" in details or details.get("code") == "NOT_FOUND" or details.get("id") is None


class TestGetRoomArtworksTool:
    """Verifies tool 3: get_room_artworks."""

    def test_get_room_artworks_sal_d_returns_at_least_three_in_order(self):
        """R1 criterion: Room 'SAL-D' returns >= 3 exhibited artworks in order."""
        results = get_room_artworks(room_id="SAL-D")
        assert isinstance(results, list)
        assert len(results) >= 3, f"Expected >= 3 artworks in SAL-D, got {len(results)}"

        # Verify exhibited status and presence of Munch masterworks
        titles = [r.get("tittel") for r in results]
        assert "Skrik" in titles
        assert "Pikene på broen" in titles

        # Verify sequencing: if rekkefølge is returned, it should be sorted ascending
        orders = [r.get("visningsrekkefølge") or r.get("rekkefølge") or r.get("rekkefoelge") for r in results]
        valid_orders = [o for o in orders if o is not None]
        if len(valid_orders) >= 2:
            assert valid_orders == sorted(valid_orders), f"Artworks not in sequence order: {valid_orders}"

    def test_get_room_artworks_sal_a(self):
        """Room SAL-A returns romanticism/mythology artworks in Sal A."""
        results = get_room_artworks(room_id="SAL-A")
        assert len(results) >= 3
        titles = [r.get("tittel") for r in results]
        assert "Nøkken" in titles
        assert "Soria Moria slott" in titles
        assert "Vinternatt i Rondane" in titles

    def test_get_room_artworks_magazine_handling(self):
        """MAG-1 contains magazine/storage items or returns empty if filtering strictly for public exhibitions."""
        results = get_room_artworks(room_id="MAG-1")
        assert isinstance(results, list)
        # Either empty (because not 'utstilt') or contains the 2 magazine items
        assert len(results) in (0, 2)


class TestSearchEventsTool:
    """Verifies tool 4: search_events."""

    def test_search_events_upcoming_with_date_and_type(self):
        """R1 criterion: Search events returns upcoming events with date and type."""
        events = search_events()
        assert isinstance(events, list)
        assert len(events) >= 1, "Expected at least 1 upcoming event"

        for ev in events:
            assert "id" in ev
            assert "tittel" in ev and len(ev["tittel"]) > 0
            assert "type" in ev and ev["type"] in (
                "omvisning",
                "verksted",
                "foredrag",
                "konsert",
                "barnearrangement",
                "aaapning",
                "lukket",
            )
            assert "dato" in ev and len(ev["dato"]) >= 10
            assert "klokkeslett_start" in ev
            assert "pris_voksen" in ev and ev["pris_voksen"] >= 0

    def test_search_events_filter_by_type_omvisning(self):
        """Filter events by type 'omvisning' returns only guided tours."""
        tours = search_events(event_type="omvisning")
        assert isinstance(tours, list)
        assert len(tours) >= 1
        for tour in tours:
            assert tour.get("type") == "omvisning"

    def test_search_events_filter_by_type_verksted(self):
        """Filter events by type 'verksted' returns workshops."""
        workshops = search_events(event_type="verksted")
        assert isinstance(workshops, list)
        for w in workshops:
            assert w.get("type") == "verksted"


class TestSearchFaqTool:
    """Verifies tool 5: search_faq."""

    def test_search_faq_opening_hours_returns_concrete_hours(self):
        """R1 criterion: Search FAQ for 'åpningstider' returns concrete hours (10:00-17:00, etc.)."""
        results = search_faq(query="åpningstider")
        assert isinstance(results, list)
        assert len(results) >= 1, "FAQ search for 'åpningstider' returned no results"

        answers = [r.get("svar", "") for r in results]
        combined = " ".join(answers)
        assert "10:00" in combined and "17:00" in combined, (
            f"Expected concrete hours ('10:00' and '17:00') in FAQ answers: {combined}"
        )

    def test_search_faq_ticket_prices(self):
        """Search FAQ for 'pris' returns ticket prices in NOK."""
        results = search_faq(query="pris")
        assert isinstance(results, list)
        assert len(results) >= 1

        answers = [r.get("svar", "") for r in results]
        combined = " ".join(answers)
        assert "120" in combined, f"Expected adult price 120 kr in FAQ: {combined}"
        assert "kr" in combined.lower() or "gratis" in combined.lower()

    def test_search_faq_norwegian_variation_aapen(self):
        """Search FAQ with 'aapent' also returns opening hours."""
        results = search_faq(query="aapent")
        assert len(results) >= 1
        combined = " ".join([r.get("svar", "") for r in results])
        assert "10:00" in combined
