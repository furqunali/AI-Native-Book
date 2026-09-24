import pytest

from term_consistency import (
    TermVariant,
    deviations,
    is_consistent,
    term_variants,
)


def test_single_spelling_is_consistent():
    text = "JavaScript is great. I love JavaScript.\n"
    variants = term_variants(text, "JavaScript")
    assert len(variants) == 1
    assert variants[0].form == "JavaScript"
    assert variants[0].count == 2
    assert is_consistent(text, "JavaScript") is True


def test_mixed_capitalisation_detected():
    text = "JavaScript here. Javascript there. javascript too.\n"
    variants = term_variants(text, "javascript")
    forms = {v.form for v in variants}
    assert forms == {"JavaScript", "Javascript", "javascript"}
    assert is_consistent(text, "javascript") is False


def test_variants_sorted_by_count():
    text = "API API API Api api\n"
    variants = term_variants(text, "api")
    assert variants[0].form == "API"
    assert variants[0].count == 3


def test_line_numbers_recorded():
    text = "Agent one\n\nagent two\n"
    variants = term_variants(text, "agent")
    by_form = {v.form: v for v in variants}
    assert by_form["Agent"].lines == (1,)
    assert by_form["agent"].lines == (3,)


def test_word_boundary_prevents_substring_match():
    text = "reagent agents management\n"
    assert term_variants(text, "agent") == []


def test_expected_makes_others_deviations():
    text = "API and Api and api\n"
    devs = deviations(text, "api", expected="API")
    forms = {d.form for d in devs}
    assert forms == {"Api", "api"}
    assert is_consistent(text, "api", expected="API") is False


def test_expected_all_match_is_consistent():
    text = "API and API\n"
    assert is_consistent(text, "api", expected="API") is True
    assert deviations(text, "api", expected="API") == []


def test_code_span_ignored():
    text = "The `Agent` class. We call it agent in prose.\n"
    variants = term_variants(text, "agent")
    assert [v.form for v in variants] == ["agent"]


def test_fenced_code_ignored():
    text = "agent\n```\nAgent Agent Agent\n```\n"
    variants = term_variants(text, "agent")
    assert len(variants) == 1
    assert variants[0].form == "agent"


def test_absent_term_is_consistent():
    assert term_variants("nothing to see", "agent") == []
    assert is_consistent("nothing to see", "agent") is True


def test_multiword_term():
    text = "context window and Context Window\n"
    variants = term_variants(text, "context window")
    assert len(variants) == 2


def test_rejects_empty_term():
    with pytest.raises(ValueError, match="term must not be empty"):
        term_variants("hello", "  ")


def test_rejects_non_string():
    with pytest.raises(TypeError):
        term_variants(None, "agent")


def test_variant_is_immutable():
    (variant,) = term_variants("agent\n", "agent")
    assert isinstance(variant, TermVariant)
    with pytest.raises(AttributeError):
        variant.count = 0
