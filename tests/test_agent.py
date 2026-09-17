"""Tier 3: Museumsvert Agent Persona & Acceptance Tests (R2 Acceptance Criteria).

Verifies:
- Agent locates 'Skrik' in Sal D (2. etasje).
- Agent answers ticket prices from FAQ table in NOK (120 kr adult, 80 kr student, free under 16).
- Agent provides 30-minute highlights with currently exhibited artworks only (never magazine).
- Agent never hallucinates facts/years not in DB.
- Agent tone follows masterprompt style (friendly, concrete, non-academic, no forbidden jargon).
- AgentResponse dataclass contract adherence.
"""

import re
import pytest

agent_module = pytest.importorskip(
    "src.aura_museum.core.agent",
    reason="Milestone 2 (src.aura_museum.core.agent) not yet implemented. Progressive testability enabled.",
)
MuseumsvertAgent = agent_module.MuseumsvertAgent
AgentResponse = agent_module.AgentResponse


def get_response_text(resp) -> str:
    """Helper to safely extract textual response."""
    if hasattr(resp, "text"):
        return resp.text
    return str(resp)


@pytest.fixture
def agent(db_path):
    """Instantiate a MuseumsvertAgent connected to the test database."""
    return MuseumsvertAgent(db_path=db_path)


class TestMuseumsvertLocationAndCollection:
    """Verifies artwork localization and collection knowledge."""

    def test_locate_skrik_in_sal_d(self, agent):
        """R2 criterion: Agent besvarer 'Hvor finner jeg Skrik?' med korrekt salhenvisning (Sal D)."""
        resp = agent.handle_message("Hvor finner jeg Skrik?")
        text = get_response_text(resp)

        assert len(text.strip()) > 0, "Agent returned an empty response"
        # Must locate Skrik in Sal D
        assert re.search(r"Sal\s+D\b", text, re.IGNORECASE) or "SAL-D" in text.upper(), (
            f"Expected 'Sal D' in response: '{text}'"
        )
        # Should reference Munch
        assert "Munch" in text, f"Expected mention of Munch in response: '{text}'"

        # Check metadata attributes if returned as AgentResponse
        if isinstance(resp, AgentResponse):
            assert "SAL-D" in [r.upper() for r in resp.rooms_referenced] or any("D" in r.upper() for r in resp.rooms_referenced)

    def test_locate_kittelsen_artworks_in_sal_a(self, agent):
        """Agent locates Theodor Kittelsen's works in Sal A."""
        resp = agent.handle_message("Hvor henger bildene til Theodor Kittelsen?")
        text = get_response_text(resp)

        assert re.search(r"Sal\s+A\b", text, re.IGNORECASE) or "SAL-A" in text.upper(), (
            f"Expected 'Sal A' in response: '{text}'"
        )
        assert "Nøkken" in text or "Soria Moria" in text


class TestMuseumsvertPricing:
    """Verifies ticket pricing from FAQ table in NOK."""

    def test_ticket_prices_from_faq_in_nok(self, agent):
        """R2 criterion: Agent besvarer 'Hva koster det?' med faktiske priser fra FAQ-tabellen i NOK."""
        resp = agent.handle_message("Hva koster det å komme inn på museet?")
        text = get_response_text(resp)

        assert len(text.strip()) > 0, "Agent returned an empty response"
        # Adult price: 120 kr
        assert "120" in text, f"Expected adult price '120' in response: '{text}'"
        # Student/senior price: 80 kr
        assert "80" in text, f"Expected concession price '80' in response: '{text}'"
        # Children free / gratis
        assert "gratis" in text.lower() or "0" in text, f"Expected 'gratis' for children in response: '{text}'"
        # Currency specification
        assert "kr" in text.lower() or "nok" in text.lower(), f"Expected currency 'kr' or 'NOK' in response: '{text}'"

    def test_ticket_prices_student_inquiry(self, agent):
        """Agent confirms student ticket is 80 kr."""
        resp = agent.handle_message("Har dere studentrabatt og hva koster det?")
        text = get_response_text(resp)
        assert "80" in text
        assert "kr" in text.lower()


class TestMuseumsvertRecommendations:
    """Verifies recommendations adherence to exhibition status."""

    def test_30_minute_recommendation_exhibited_only(self, agent, db_conn):
        """R2 criterion: Agent besvarer 'Hva anbefaler du hvis jeg har 30 minutter?'

        med et personlig forslag basert på faktiske utstilte verk.
        Must NEVER recommend magazine works (Brudeferd i Hardanger, Selvportrett med sigarett).
        """
        resp = agent.handle_message("Hva anbefaler du hvis jeg har 30 minutter?")
        text = get_response_text(resp)

        assert len(text.strip()) > 0, "Agent returned an empty response"

        # Must mention a recommended starting room (Sal A or Sal D)
        assert re.search(r"Sal\s+[AD]\b", text, re.IGNORECASE), (
            f"Expected recommendation to point to Sal A or Sal D: '{text}'"
        )

        # Must NOT recommend artworks in magazine
        assert "Brudeferd i Hardanger" not in text, "Agent recommended magazine artwork 'Brudeferd i Hardanger'!"
        assert "Selvportrett med sigarett" not in text, "Agent recommended magazine artwork 'Selvportrett med sigarett'!"
        assert "AURA-2026-011" not in text
        assert "AURA-2026-012" not in text

        # Must recommend at least one genuine exhibited work
        exhibited_titles = ["Skrik", "Nøkken", "Soria Moria slott", "Vinternatt i Rondane", "Pikene på broen"]
        assert any(t in text for t in exhibited_titles), (
            f"Expected recommendation to mention one of {exhibited_titles}, got: '{text}'"
        )


class TestMuseumsvertAntiHallucination:
    """Verifies strict anti-hallucination and factual fidelity."""

    def test_anti_hallucination_unknown_artwork(self, agent):
        """R2 criterion: Agent finner aldri på kunstnerfakta eller verk som ikke finnes i databasen."""
        resp = agent.handle_message("Har dere Mona Lisa av Leonardo da Vinci utstilt?")
        text = get_response_text(resp)

        assert len(text.strip()) > 0
        # Agent must clarify that the work/artist is NOT in the collection
        negative_signals = ["har vi dessverre ikke", "ikke i museets samling", "ikke i samlingen", "finnes ikke", "finner ikke"]
        assert any(sig in text.lower() for sig in negative_signals), (
            f"Expected agent to decline having Mona Lisa: '{text}'"
        )
        # Must not fabricate accession ID
        assert "AURA-2026-9" not in text

    def test_anti_hallucination_skrik_year_and_facts(self, agent):
        """Historical facts for Skrik must match DB exactly (1893, tempera/oljekritt)."""
        resp = agent.handle_message("Når ble Skrik malt og hvilken teknikk ble brukt?")
        text = get_response_text(resp)

        assert "1893" in text, f"Expected 1893 in response: '{text}'"
        assert not re.search(r"\b(1895|1910|1880)\b", text), f"Agent hallucinated wrong year in: '{text}'"

    def test_anti_hallucination_kittelsen_lifespan(self, agent):
        """Artist lifespan must match DB (1857-1914)."""
        resp = agent.handle_message("Fortell om Theodor Kittelsen, når levde han?")
        text = get_response_text(resp)

        assert "1857" in text and "1914" in text, (
            f"Expected Kittelsen lifespans 1857 and 1914 in response: '{text}'"
        )


class TestMuseumsvertToneAndStyle:
    """Verifies tone, non-academic style, and absence of forbidden jargon."""

    FORBIDDEN_ARTSPEAK = [
        "interrogere",
        "subjektsposisjon",
        "romlig negasjon",
        "diskurs",
        "ontologisk",
        "dekonstruere",
    ]

    FORBIDDEN_INSTITUTIONAL = [
        "varelager",
        "artefakt",
        "helpdesk",
        "billettselger",
    ]

    def test_tone_avoids_artspeak_and_forbidden_terms(self, agent):
        """R2 criterion: Agentens tone matcher stilreglene i masterprompten (vennlig, konkret, ikke akademisk)."""
        questions = [
            "Hva forestiller bildet Nøkken?",
            "Hvorfor er Skrik så kjent?",
            "Hva koster det for en familie?",
            "Hva skjer på museet i helgen?",
        ]

        for q in questions:
            resp = agent.handle_message(q)
            text = get_response_text(resp).lower()

            for term in self.FORBIDDEN_ARTSPEAK:
                assert term not in text, f"Prohibited artspeak term '{term}' found in response to '{q}': {text}"

            for term in self.FORBIDDEN_INSTITUTIONAL:
                assert term not in text, f"Prohibited institutional term '{term}' found in response to '{q}': {text}"

    def test_agent_response_dataclass_contract(self, agent):
        """Verifies AgentResponse contract fields."""
        resp = agent.handle_message("Hvor finner jeg Skrik?")
        assert isinstance(resp, AgentResponse)
        assert isinstance(resp.text, str) and len(resp.text) > 0
        assert isinstance(resp.category, str) and len(resp.category) > 0
        assert isinstance(resp.tools_used, list)
        assert isinstance(resp.artworks_referenced, list)
        assert isinstance(resp.rooms_referenced, list)
