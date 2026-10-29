"""Fase 2: faktakontroll. LLM-tekst må bare inneholde fakta fra verktøyresultatene."""

import shutil
import sqlite3

import pytest

from src.kunstpixel.core.agent import FORBIDDEN_WORDS, MuseumsvertAgent
from src.kunstpixel.core.fact_check import load_entities, verify_facts
from src.kunstpixel.core.llm import FakeLLM
from tests.canonical_questions import CANONICAL_QUESTIONS, KNOWN_UNGROUNDED


@pytest.fixture
def entities(db_path):
    return load_entities(db_path)


# ---------- Ingen falsk alarm: dagens egne svar må bestå kontrollen ----------


@pytest.mark.parametrize("question", [q for q in CANONICAL_QUESTIONS if q.strip()])
def test_rule_based_answers_pass_their_own_fact_check(db_path, entities, question):
    r = MuseumsvertAgent(db_path=db_path).handle_message(question)
    if not any(tr["result"] for tr in r.tool_results):
        pytest.skip("ingen verktøyfakta, LLM brukes ikke")
    violations = verify_facts(r.text, r.tool_results, entities, FORBIDDEN_WORDS)
    if question in KNOWN_UNGROUNDED:
        # Kjent avvik: svartekst har hardkodede fakta. Når dette begynner å passere,
        # fjern spørsmålet fra KNOWN_UNGROUNDED (da er hardkodingen fikset).
        assert violations != [], "Svaret er nå grunnet i verktøy. Fjern det fra KNOWN_UNGROUNDED."
    else:
        assert violations == []


# ---------- Korrekte omskrivinger skal slippe gjennom ----------

GOOD_PARAPHRASES = [
    (
        "Hva koster det?",
        "Voksne betaler 120 kr, studenter og pensjonister 80 kr, og barn kommer gratis inn. "
        "Familiepass koster 250 kr.",
    ),
    ("Hva koster det for studenter?", "Som student betaler du 80 kr. Pensjonister betaler det samme."),
    ("Hvor finner jeg Skrik?", "Skrik fra 1893 av Edvard Munch henger i Sal D i 2. etasje."),
    ("Hva er i Sal D?", "I Sal D kan du se blant annet Skrik (1893) og Pikene på broen (1901)."),
]


@pytest.mark.parametrize("question,answer", GOOD_PARAPHRASES, ids=[g[0] for g in GOOD_PARAPHRASES])
def test_correct_paraphrase_is_accepted(db_path, question, answer):
    r = MuseumsvertAgent(db_path=db_path, llm=FakeLLM(responder=lambda _: answer)).handle_message(question)
    assert r.fallback_reason is None, r.fallback_reason
    assert r.llm_used is True
    assert r.text == answer


# ---------- Fiendtlige skript: oppdiktede fakta skal avvises ----------

BAD_ANSWERS = [
    ("Hva koster det?", "Voksne betaler 999 kr.", "beløp"),
    ("Hva koster det?", "Voksne betaler hundre og tjue kroner.", "bokstaver"),
    ("Hvor finner jeg Skrik?", "Skrik henger i Sal B.", "Sal B"),
    ("Hvor finner jeg Skrik?", "Skrik ble malt i 1925 og henger i Sal D.", "årstall"),
    ("Hvor finner jeg Skrik?", "Skrik av Edvard Munch finnes som AURA-2026-099.", "AURA-2026-099"),
    ("Hvor henger bildene til Theodor Kittelsen?", "Kittelsen henger sammen med Edvard Munch.", "Munch"),
    (
        "Hva anbefaler du hvis jeg har 30 minutter?",
        "Se Brudeferd i Hardanger i Sal A, og Skrik i Sal D.",
        "magasin",
    ),
    ("Hva koster det?", f"Jeg er en {FORBIDDEN_WORDS[0]}. Voksne betaler 120 kr.", "forbudt"),
]


@pytest.mark.parametrize("question,answer,expected", BAD_ANSWERS, ids=[b[2] for b in BAD_ANSWERS])
def test_invented_facts_are_rejected_and_rule_based_text_is_shown(db_path, question, answer, expected):
    base = MuseumsvertAgent(db_path=db_path).handle_message(question)
    r = MuseumsvertAgent(db_path=db_path, llm=FakeLLM(responder=lambda _: answer)).handle_message(question)
    assert r.llm_used is False
    assert r.text == base.text
    assert r.fallback_reason and r.fallback_reason.startswith("faktakontroll:")
    assert expected.lower() in r.fallback_reason.lower()


# ---------- Verktøyene eier sannheten (mutasjonstest) ----------


def test_changed_database_price_beats_stale_llm_answer(tmp_path, db_path, monkeypatch):
    """Databasen får ny pris. Modellen 'husker' gammel pris og må avvises."""
    monkeypatch.setenv("AURA_DB_PATH", str(db_path))  # agent overstyrer env; monkeypatch rydder opp
    mutated = tmp_path / "museum_mutert.db"
    shutil.copyfile(db_path, mutated)
    conn = sqlite3.connect(mutated)
    conn.execute(
        "UPDATE publikum_faq SET svar = ? WHERE id = 1",
        ("Voksne: 175 kr. Studenter: 110 kr. Barn: gratis. Familiepass: 390 kr.",),
    )
    conn.commit()
    conn.close()

    stale = "Voksne betaler 120 kr og studenter 80 kr."
    agent = MuseumsvertAgent(db_path=mutated, llm=FakeLLM(responder=lambda _: stale))
    r = agent.handle_message("Hva koster det?")
    assert r.llm_used is False
    assert "175 kr" in r.text and "110 kr" in r.text
    assert "120 kr" not in r.text
    assert r.fallback_reason.startswith("faktakontroll:")
    agent.db_conn._conn.close()


# ---------- Enhetstester av verify_facts ----------


def test_century_phrases_are_not_year_violations(entities):
    text = "Samlingen dekker norsk kunst fra 1800- og 1900-tallet."
    assert verify_facts(text, [{"tool": "x", "args": {}, "result": [{"a": 1}]}], entities) == []


def test_amount_formats_are_normalised(entities):
    results = [{"tool": "search_faq", "args": {}, "result": [{"svar": "Voksne: 120 kr"}]}]
    for form in ("120 kr", "120 kroner", "kr 120", "NOK 120", "120,-"):
        assert verify_facts(f"Billetten koster {form}.", results, entities) == [], form
    assert verify_facts("Billetten koster 121 kr.", results, entities) != []


def test_magazine_work_allowed_only_with_storage_caveat(entities):
    results = [{"tool": "get_artwork_details", "args": {}, "result": {"tittel": "Brudeferd i Hardanger"}}]
    assert verify_facts("Brudeferd i Hardanger henger i Sal A.", results, entities) != []
    assert verify_facts("Brudeferd i Hardanger ligger i magasinet og vises ikke nå.", results, entities) == []
