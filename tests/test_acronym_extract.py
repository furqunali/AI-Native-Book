import pytest

from acronym_extract import Acronym, acronym_set, extract_acronyms


def test_extracts_basic_acronym():
    (a,) = extract_acronyms("The API is documented here.")
    assert a.text == "API"
    assert a.first_line == 1
    assert a.count == 1


def test_first_seen_line_recorded():
    text = "intro line\nWe use RAG here.\nRAG again later.\n"
    (a,) = extract_acronyms(text)
    assert a.text == "RAG"
    assert a.first_line == 2
    assert a.count == 2


def test_order_is_by_first_appearance():
    text = "LLM then API then RAG"
    assert [a.text for a in extract_acronyms(text)] == ["LLM", "API", "RAG"]


def test_acronym_with_digits():
    (a,) = extract_acronyms("Store it in S3 today.")
    assert a.text == "S3"


def test_plural_acronym_and_singular_are_distinct():
    text = "Many APIs exist. One API here."
    texts = {a.text for a in extract_acronyms(text)}
    assert texts == {"APIs", "API"}


def test_single_capital_letter_not_acronym():
    assert extract_acronyms("A cat sat.") == []


def test_stop_words_excluded_by_default():
    # "OK" and "I" are in the default stop set.
    assert extract_acronyms("I said OK to it.") == []


def test_inline_code_ignored():
    assert extract_acronyms("Call `API` directly.") == []


def test_fenced_code_ignored():
    text = "```\nAPI = 1\n```\nreal API here\n"
    (a,) = extract_acronyms(text)
    assert a.first_line == 4


def test_custom_stop_words():
    result = extract_acronyms("HTTP and API", stop_words=frozenset({"HTTP"}))
    assert [a.text for a in result] == ["API"]


def test_acronym_set_helper():
    assert acronym_set("API and LLM and API") == {"API", "LLM"}


def test_result_is_immutable():
    (a,) = extract_acronyms("API")
    assert isinstance(a, Acronym)
    with pytest.raises(AttributeError):
        a.count = 9


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        extract_acronyms(None)


def test_rejects_bad_stop_words():
    with pytest.raises(TypeError, match="stop_words must be a set"):
        extract_acronyms("API", stop_words=["API"])
