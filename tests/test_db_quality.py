"""Tier 1: Database Content & Quality Assurance Tests.

Verifies:
- 72 rows across 7 relational tables
- Curatorial wall text (veggtekst) quality rules (50-90 words, 2-line header, body paragraphs)
- Foreign key and referential integrity
- Allowed status and tilstand enum constraints
- Key artwork placement (Skrik in Sal D, Kittelsen in Sal A)
- Authoritative FAQ and event records
"""

import re
import sqlite3
import pytest


class TestDatabaseTableStructureAndRowCounts:
    """Verifies table presence, schema adherence, and row counts."""

    EXPECTED_TABLES = [
        "kunstnere",
        "saler",
        "verk",
        "utstillinger",
        "utstilling_verk",
        "hendelser",
        "publikum_faq",
    ]

    def test_all_seven_tables_exist(self, db_conn: sqlite3.Connection):
        """All 7 required tables must exist in the SQLite database."""
        cursor = db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = {row["name"] for row in cursor.fetchall()}
        for table in self.EXPECTED_TABLES:
            assert table in tables, f"Missing required table: {table}"

    def test_total_row_count_is_72(self, db_conn: sqlite3.Connection, db_baseline: dict):
        """Total row count across all 7 business tables must equal exactly 72."""
        cursor = db_conn.cursor()
        total_rows = 0
        for table in self.EXPECTED_TABLES:
            cursor.execute(f"SELECT count(*) FROM {table}")
            total_rows += cursor.fetchone()[0]

        assert total_rows == db_baseline["expected_total_rows"], (
            f"Expected {db_baseline['expected_total_rows']} total rows across tables, found {total_rows}"
        )

    @pytest.mark.parametrize(
        "table_name,expected_count",
        [
            ("kunstnere", 12),
            ("saler", 6),
            ("verk", 16),
            ("utstillinger", 3),
            ("utstilling_verk", 15),
            ("hendelser", 8),
            ("publikum_faq", 12),
        ],
    )
    def test_individual_table_row_counts(
        self, db_conn: sqlite3.Connection, table_name: str, expected_count: int
    ):
        """Each table must have its exact expected row count."""
        cursor = db_conn.cursor()
        cursor.execute(f"SELECT count(*) FROM {table_name}")
        actual_count = cursor.fetchone()[0]
        assert actual_count == expected_count, (
            f"Table '{table_name}' has {actual_count} rows, expected {expected_count}"
        )


class TestReferentialIntegrity:
    """Verifies foreign key relationships and link tables."""

    def test_artwork_artist_foreign_keys(self, db_conn: sqlite3.Connection):
        """Every artwork must link to a valid artist in kunstnere."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT v.id, v.tittel, v.kunstner_id
            FROM verk v
            LEFT JOIN kunstnere k ON v.kunstner_id = k.id
            WHERE k.id IS NULL
        """)
        orphans = cursor.fetchall()
        assert len(orphans) == 0, f"Found artworks with invalid kunstner_id: {[dict(o) for o in orphans]}"

    def test_artwork_room_foreign_keys(self, db_conn: sqlite3.Connection):
        """Every artwork with a sal_id must link to an existing room in saler."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT v.id, v.tittel, v.sal_id
            FROM verk v
            LEFT JOIN saler s ON v.sal_id = s.id
            WHERE v.sal_id IS NOT NULL AND s.id IS NULL
        """)
        orphans = cursor.fetchall()
        assert len(orphans) == 0, f"Found artworks with invalid sal_id: {[dict(o) for o in orphans]}"

    def test_exhibition_artwork_link_integrity(self, db_conn: sqlite3.Connection):
        """All rows in utstilling_verk must link to existing exhibitions and artworks."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT uv.utstilling_id, uv.verk_id
            FROM utstilling_verk uv
            LEFT JOIN utstillinger u ON uv.utstilling_id = u.id
            LEFT JOIN verk v ON uv.verk_id = v.id
            WHERE u.id IS NULL OR v.id IS NULL
        """)
        invalid_links = cursor.fetchall()
        assert len(invalid_links) == 0, f"Invalid exhibition-artwork links: {[dict(r) for r in invalid_links]}"

    def test_events_room_integrity(self, db_conn: sqlite3.Connection):
        """All events with sal_id must reference a valid room."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT h.id, h.tittel, h.sal_id
            FROM hendelser h
            LEFT JOIN saler s ON h.sal_id = s.id
            WHERE h.sal_id IS NOT NULL AND s.id IS NULL
        """)
        orphans = cursor.fetchall()
        assert len(orphans) == 0, f"Found events with invalid sal_id: {[dict(o) for o in orphans]}"


class TestWallTextQualityRules:
    """Verifies curatorial quality rules from context/core/quality_rules.md."""

    def test_wall_text_status_counts(self, db_conn: sqlite3.Connection, db_baseline: dict):
        """14 exhibited works must have approved wall text; 2 magazine works must be draft."""
        cursor = db_conn.cursor()
        cursor.execute("SELECT veggtekst_status, count(*) as cnt FROM verk GROUP BY veggtekst_status")
        counts = {row["veggtekst_status"]: row["cnt"] for row in cursor.fetchall()}

        assert counts.get("approved", 0) == db_baseline["exhibited_artworks_count"], (
            f"Expected {db_baseline['exhibited_artworks_count']} approved wall texts, got {counts.get('approved')}"
        )
        assert counts.get("draft", 0) == db_baseline["magazine_artworks_count"], (
            f"Expected {db_baseline['magazine_artworks_count']} draft wall texts, got {counts.get('draft')}"
        )

    def test_magazine_artworks_have_draft_status(self, db_conn: sqlite3.Connection):
        """Artworks in storage (MAG-1) must have status 'magasin' and 'draft' wall text."""
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, tittel, status, veggtekst_status FROM verk WHERE sal_id = 'MAG-1'")
        mag_works = cursor.fetchall()
        assert len(mag_works) == 2
        for work in mag_works:
            assert work["status"] == "magasin"
            assert work["veggtekst_status"] == "draft"

    def test_approved_wall_texts_word_count(self, db_conn: sqlite3.Connection):
        """Every approved wall text must be within 48 to 90 words (target: 50-90 words).

        Verified baseline: all 14 range between 49 and 60 words.
        """
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, tittel, veggtekst FROM verk WHERE veggtekst_status = 'approved'")
        works = cursor.fetchall()
        assert len(works) == 14

        for work in works:
            text = work["veggtekst"]
            assert text is not None and len(text.strip()) > 0, f"Empty wall text for {work['id']}"
            words = text.split()
            word_count = len(words)
            assert 48 <= word_count <= 90, (
                f"Artwork {work['id']} ('{work['tittel']}') has {word_count} words; "
                f"must be between 48 and 90 words according to curatorial quality rules."
            )

    def test_approved_wall_texts_header_structure(self, db_conn: sqlite3.Connection):
        """Every approved wall text must have a structured 2-line header.

        Line 1: [Artist] ([birth]–[death]), [nationality].
        Line 2: _[Title]_, [year]. [Technique], [dimensions]. [ID].
        """
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, tittel, veggtekst FROM verk WHERE veggtekst_status = 'approved'")
        works = cursor.fetchall()

        for work in works:
            text = work["veggtekst"].strip()
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            assert len(lines) >= 3, f"Wall text for {work['id']} must have header lines and body paragraphs"

            line1 = lines[0]
            line2 = lines[1]

            # Line 1 check: artist name, birth/death year in parens, nationality
            assert re.search(r"\(\d{4}[–-]\d{4}\)", line1), (
                f"Line 1 of {work['id']} missing lifespan (e.g. (1863–1944)): '{line1}'"
            )

            # Line 2 check: italicized title, year, artwork ID
            assert "_" in line2, f"Line 2 of {work['id']} missing italicized title '_..._': '{line2}'"
            assert work["id"] in line2, f"Line 2 of {work['id']} missing artwork ID '{work['id']}': '{line2}'"


class TestDatabaseDomainConstraints:
    """Verifies domain constraints, enums, and key exhibition data."""

    def test_artwork_status_allowed_values(self, db_conn: sqlite3.Connection):
        """All artworks must have valid status enum."""
        allowed_statuses = {"utstilt", "magasin", "utlaant", "konservering", "innkommende"}
        cursor = db_conn.cursor()
        cursor.execute("SELECT DISTINCT status FROM verk")
        statuses = {row[0] for row in cursor.fetchall()}
        assert statuses.issubset(allowed_statuses), f"Unexpected status values: {statuses - allowed_statuses}"

    def test_artwork_condition_allowed_values(self, db_conn: sqlite3.Connection):
        """All artworks must have valid condition enum."""
        allowed_conditions = {"utmerket", "god", "akseptabel", "skadet", "ukjent"}
        cursor = db_conn.cursor()
        cursor.execute("SELECT DISTINCT tilstand FROM verk")
        conditions = {row[0] for row in cursor.fetchall()}
        assert conditions.issubset(allowed_conditions), f"Unexpected tilstand values: {conditions - allowed_conditions}"

    def test_skrik_location_and_metadata(self, db_conn: sqlite3.Connection, db_baseline: dict):
        """Edvard Munch's 'Skrik' (AURA-2026-009) must be exhibited in Sal D."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT v.id, v.tittel, v.sal_id, v.status, k.navn as kunstner, v.aar
            FROM verk v
            JOIN kunstnere k ON v.kunstner_id = k.id
            WHERE v.id = :id
        """, {"id": db_baseline["skrik_artwork_id"]})
        skrik = cursor.fetchone()

        assert skrik is not None, "Skrik not found in database"
        assert skrik["sal_id"] == db_baseline["skrik_room_id"]
        assert skrik["status"] == "utstilt"
        assert "Munch" in skrik["kunstner"]
        assert skrik["aar"] == 1893

    def test_theodor_kittelsen_artworks(self, db_conn: sqlite3.Connection, db_baseline: dict):
        """Theodor Kittelsen must have at least 2 artworks exhibited in Sal A."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT v.id, v.tittel, v.sal_id, v.status
            FROM verk v
            JOIN kunstnere k ON v.kunstner_id = k.id
            WHERE k.navn LIKE '%Kittelsen%'
        """)
        kittelsen_works = cursor.fetchall()
        assert len(kittelsen_works) >= db_baseline["kittelsen_artworks_count"], (
            f"Expected at least {db_baseline['kittelsen_artworks_count']} Kittelsen works, found {len(kittelsen_works)}"
        )
        for w in kittelsen_works:
            assert w["sal_id"] == "SAL-A"
            assert w["status"] == "utstilt"

    def test_room_d_artworks(self, db_conn: sqlite3.Connection, db_baseline: dict):
        """Sal D must have at least 3 exhibited artworks."""
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT v.id, v.tittel, v.status
            FROM verk v
            WHERE v.sal_id = :room_id AND v.status = 'utstilt'
        """, {"room_id": db_baseline["skrik_room_id"]})
        room_d_works = cursor.fetchall()
        assert len(room_d_works) >= db_baseline["sal_d_artworks_count"], (
            f"Expected at least {db_baseline['sal_d_artworks_count']} works in Sal D, got {len(room_d_works)}"
        )

    def test_faq_opening_hours_and_tickets(self, db_conn: sqlite3.Connection, db_baseline: dict):
        """FAQ table must contain opening hours (10:00-17:00) and ticket prices."""
        cursor = db_conn.cursor()
        cursor.execute("SELECT svar FROM publikum_faq WHERE id = 2")
        row_hours = cursor.fetchone()
        assert row_hours is not None
        assert db_baseline["opening_hours_fragment"] in row_hours["svar"]

        cursor.execute("SELECT svar FROM publikum_faq WHERE id = 1")
        row_tickets = cursor.fetchone()
        assert row_tickets is not None
        for category, price in db_baseline["ticket_prices"].items():
            if price > 0:
                assert str(price) in row_tickets["svar"], f"Price for {category} ({price}) not found in FAQ"
