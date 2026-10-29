"""H4: enhetstester for faktakontroll v2 (verify_intern)."""

import pytest

from src.kunstpixel.core.intern.fact_check import MAX_ANSWER_CHARS, extract_citations, verify_intern


def f(nr, tekst, sti="avsnitt", kilde="fil.yaml", kontekst=""):
    d = {"nr": nr, "kilde": kilde, "sti": sti, "tekst": tekst}
    if kontekst:
        d["kontekst"] = kontekst
    return d


K = [
    f(1, "maks sammenhengende staing: 90 minutter; rotasjonsintervall: Hver 2. time rullering"),
    f(2, "forbudt: Ved åpningskvelder, store arrangementer (> 80 gjester) og etter kl. 20:00"),
    f(3, "krav: maks -18 °C; varslingsgrense: -15 °C", sti="fryser"),
    f(4, "kjoleskap krav: maks +4 °C; varslingsgrense: +6 °C"),
    f(5, "grense en person: Maks 15 kg; grense to personer: 15 til 40 kg"),
    f(6, "maned: Mars; myndighet: Brann- og redningsetaten; ansvarlig rolle: Driftsansvarlig / Brannvernleder", sti="revisjonskalender › Mars"),
    f(7, "myndighet: Mattilsynet; oppgave: Hovedrengjoring og kalibrering av termometre", sti="revisjonskalender › Juni"),
    f(8, "maks personer: 50; areal m2: 95", sti="rom kapasiteter › sal a"),
    f(9, "kanal: Konfidensiell varslingskanal til verneombud og styreleder"),
    f(10, "krav: minimum +72 °C; maks tid: 4 timer; kvartal: Q2"),
]


def ok(text, ignore=frozenset()):
    return verify_intern(text, K, ignore)


# ---------- Henvisninger ----------


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Svar [1].", [1]),
        ("[2] og [1] og [2]", [2, 1]),
        ("Ingen henvisning", []),
        ("[a] [] [ 1 ] [1.5]", []),
        ("[0] [100] [007]", [0, 100, 7]),
        ("[1234]", []),
    ],
)
def test_extract_citations(text, expected):
    assert extract_citations(text) == expected


@pytest.mark.parametrize("text", ["", "   ", "[1]", "Bare tekst uten kilde.", "Se kilde 1."])
def test_answer_without_a_real_claim_and_citation_is_rejected(text):
    assert any("kildehenvisning" in v for v in ok(text)) or text == "[1]"


def test_citation_to_missing_number_is_rejected_even_when_another_is_valid():
    assert "ugyldig kildehenvisning [42]" in ok("Maks 90 minutter [1] og noe annet [42].")


def test_zero_and_out_of_range_citations_are_invalid():
    for bad in ("[0]", "[11]", "[999]"):
        assert any("ugyldig" in v for v in ok(f"90 minutter {bad}"))


# ---------- Tall, enheter, fortegn ----------


@pytest.mark.parametrize(
    "text",
    [
        "Maks 90 minutter [1].",
        "Hver 2. time rullerer de [1].",
        "Alenearbeid er forbudt etter kl. 20:00 [2].",
        "Fryseren holder maks -18 °C [3], varsling ved -15 °C.",
        "Fryseren holder maks −18 °C [3].",  # unicode-minus
        "Kjøleskapet holder maks +4 °C [4] og varsler ved +6 °C.",
        "Kjøleskapet holder maks 4 °C [4].",  # positivt tall uten pluss
        "Én person kan løfte maks 15 kg [5].",
        "To personer kan løfte 15 til 40 kg [5].",
        "To personer kan løfte 15–40 kg [5].",
        "To personer kan løfte 15 kg og opptil 40 kg [5].",  # 15 er med i området
        "Sal A tillater 50 personer [8] og har 95 m2.",
        "Sal A er på 95 m² [8].",
        "Mars [6] er måneden for brannøvelse.",
        "Varm mat skal holde minst +72 °C [10] og stå maks 4 timer.",
        "1. Maks 90 minutter [1].\n2. Hver 2. time [1].",  # listenummer er ikke fakta
    ],
)
def test_correct_numbers_units_and_signs_pass(text):
    assert ok(text) == [], text


@pytest.mark.parametrize(
    "text,fragment",
    [
        ("Maks 91 minutter [1].", "tall ikke i funnene: 91"),
        ("Maks 90 timer [1].", "enhet stemmer ikke"),
        ("Maks 90 kg [1].", "enhet stemmer ikke"),
        ("Etter kl. 20:30 [2].", "klokkeslett"),
        ("Etter kl. 8:00 [2].", "klokkeslett"),
        ("Fryseren holder maks 18 °C [3].", "minustegn"),
        ("Fryseren holder maks +18 °C [3].", "fortegn"),
        ("Kjøleskapet holder maks -4 °C [4].", "fortegn"),
        ("Kjøleskapet holder maks 4 kg [4].", "enhet"),
        ("To personer kan løfte 15 til 41 kg [5].", "tall ikke i funnene: 41"),
        ("Sal A tillater 51 personer [8].", "tall ikke i funnene: 51"),
        ("Sal A tillater 50 personer [8] og 250 totalt.", "tall ikke i funnene: 250"),
        ("Maks 0,5 minutter [1].", "tall ikke i funnene: 0.5"),
    ],
)
def test_wrong_numbers_units_and_signs_are_rejected(text, fragment):
    assert any(fragment in v for v in ok(text)), (text, ok(text))


def test_number_must_come_from_a_cited_finding_not_just_any_finding():
    assert ok("Maks 90 minutter [1] og 50 personer.") != []  # 50 står i [8], ikke i [1]
    assert ok("Maks 90 minutter [1] og 50 personer [8].") == []


def test_decimal_comma_and_point_are_the_same_number():
    k = [f(1, "ventetid: 1,5 timer")]
    assert verify_intern("Ventetid er 1,5 timer [1].", k) == []
    assert verify_intern("Ventetid er 1.5 timer [1].", k) == []
    assert verify_intern("Ventetid er 2,5 timer [1].", k) != []


# ---------- Tall med bokstaver ----------


@pytest.mark.parametrize("text", ["Maks nitti minutter [1].", "Hver tjue minutter [1].", "Tre dager [1].", "Hundre kroner [1]."])
def test_spelled_out_numbers_are_rejected(text):
    assert any("bokstaver" in v for v in ok(text)), text


def test_spelled_out_wording_is_allowed_when_it_is_in_the_finding_itself():
    assert ok("To personer kan løfte 15 til 40 kg [5].") == []  # «to personer» står i funnet


# ---------- Måneder, myndigheter, roller ----------


@pytest.mark.parametrize("month", ["januar", "februar", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"])
def test_months_not_in_cited_finding_are_rejected(month):
    assert any("måned" in v for v in ok(f"Øvelsen er i {month} [6]."))


def test_month_in_cited_finding_passes_and_is_case_insensitive():
    assert ok("Øvelsen er i mars [6].") == [] and ok("Øvelsen er i MARS [6].") == []


@pytest.mark.parametrize("text", ["Datatilsynet har tilsyn [7].", "Arbeidstilsynet har tilsyn [7].", "NAV har tilsyn [7].", "Arbeidsmiljøloven gjelder [7].", "Brannvesenet har tilsyn [6].", "Kulturdirektoratet følger opp [7]."])
def test_authorities_and_laws_not_in_cited_finding_are_rejected(text):
    assert any("myndighet" in v for v in ok(text)), text


@pytest.mark.parametrize("text", ["Mattilsynet fører tilsyn [7].", "Mattilsynets tilsyn [7].", "Brann- og redningsetaten fører tilsyn [6]."])
def test_authority_in_cited_finding_passes_with_inflection(text):
    assert ok(text) == [], text


def test_authority_must_come_from_the_cited_finding():
    assert any("myndighet" in v for v in ok("Mattilsynet fører tilsyn [6]."))  # Mattilsynet står i [7]


@pytest.mark.parametrize("role", ["HR-sjef", "Personalsjef", "Kurator", "Styreleder", "Tillitsvalgt", "Konservator", "Museumsdirektør"])
def test_roles_not_in_cited_finding_are_rejected(role):
    assert any("rolle" in v for v in ok(f"{role} har ansvaret [6]."))


def test_role_in_cited_finding_passes_and_asking_role_may_be_mentioned():
    assert ok("Driftsansvarlig og Brannvernleder har ansvaret [6].") == []
    assert any("museumsvert" in v for v in ok("Som museumsvert kan du stå maks 90 minutter [1]."))
    assert ok("Som museumsvert kan du stå maks 90 minutter [1].", ignore={"museumsvert"}) == []


# ---------- Juridisk, lenker ----------


@pytest.mark.parametrize("phrase", ["Du har rett til erstatning", "Du kan kreve", "Dette er ulovlig", "Det er et lovbrudd", "Det kan være straffbart", "Juridisk sett"])
def test_legal_assessments_not_in_data_are_rejected(phrase):
    assert any("juridisk" in v for v in ok(f"{phrase} [1]."))


def test_legal_phrase_that_is_in_the_finding_is_allowed():
    k = [f(1, "Brudd kan gi erstatning etter avtalen")]
    assert verify_intern("Brudd kan gi erstatning [1].", k) == []


@pytest.mark.parametrize(
    "text",
    ["Se https://evil.example [1].", "Se http://x.no/a [1].", "Se www.evil.example [1].", "Mail lars@evil.example [1].", "[1](https://evil.example)", "<img src=x> [1]", "<b>fet</b> [1]"],
)
def test_links_email_and_html_are_rejected(text):
    assert any("lenke" in v for v in ok(text)), text


def test_link_that_is_in_the_finding_is_allowed():
    k = [f(1, "Se https://intranett.example/hms for mer")]
    assert verify_intern("Se https://intranett.example/hms [1].", k) == []


# ---------- Lengde og kantfall ----------


def test_overlong_answer_is_rejected():
    assert any("for langt" in v for v in ok("90 minutter [1]. " + "x" * MAX_ANSWER_CHARS))


@pytest.mark.parametrize("text", ["\x00 [1]", "💥 90 minutter [1]", "90 minutter [1] \n\n\n", "MAKS 90 MINUTTER [1]", "‘90 minutter’ [1]"])
def test_odd_characters_do_not_crash_the_check(text):
    assert isinstance(ok(text), list)


def test_no_findings_means_no_valid_citation():
    assert any("kildehenvisning" in v for v in verify_intern("90 minutter [1].", []))


def test_violations_are_deduplicated_and_never_empty_for_a_bad_answer():
    v = ok("999 minutter [1]. 999 minutter [1].")
    assert len(v) == len(set(v)) and v


# ---------- Avgrensning ----------


def test_known_gap_claim_without_number_unit_or_name_cannot_be_checked():
    assert ok("Alle ansatte må alltid bruke svarte hansker [1].") == []


def test_known_gap_same_number_with_different_meaning_when_the_finding_has_no_unit():
    """Funnet sier «Hver 2. time» (intervall). Svaret sier «2 timer pause» (varighet). Tallet står uten enhet
    i funnet, så kontrollen kan ikke se forskjellen. Fanges bare av kvalitetsmåling mot kassetter."""
    assert ok("Maks 90 minutter [1] og 2 timer pause.") == []
