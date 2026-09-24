import pytest

from sentence_stats import (
    SentenceStats,
    sentence_stats,
    split_sentences,
)


def test_splits_basic_sentences():
    sentences = split_sentences("First one. Second one! Third one?")
    assert sentences == ["First one.", "Second one!", "Third one?"]


def test_average_length_is_words_over_sentences():
    stats = sentence_stats("One two three. Four five.")
    assert stats.sentences == 2
    assert stats.words == 5
    assert stats.average_length == 2.5


def test_abbreviation_does_not_split():
    sentences = split_sentences("Use tools, e.g. a linter, in CI.")
    assert sentences == ["Use tools, e.g. a linter, in CI."]


def test_headings_and_code_excluded():
    text = "# Heading\n\nA real sentence here.\n\n```\ncode. more.\n```\n"
    stats = sentence_stats(text)
    assert stats.sentences == 1
    assert stats.words == 4


def test_final_sentence_without_terminator_counted():
    sentences = split_sentences("This has a period. This does not")
    assert sentences == ["This has a period.", "This does not"]


def test_ellipsis_counts_as_single_boundary():
    sentences = split_sentences("Wait... really?")
    assert sentences == ["Wait...", "really?"]


def test_decimal_number_does_not_split():
    # The '.' in 3.5 is not followed by whitespace, so no split.
    sentences = split_sentences("The value is 3.5 today.")
    assert sentences == ["The value is 3.5 today."]


def test_empty_text_has_zero_stats():
    stats = sentence_stats("")
    assert stats.sentences == 0
    assert stats.words == 0
    assert stats.average_length == 0.0


def test_whitespace_only_is_zero():
    assert split_sentences("   \n\n   ") == []


def test_multiline_prose_collapsed():
    text = "This sentence spans\ntwo lines here. Done."
    sentences = split_sentences(text)
    assert sentences == ["This sentence spans two lines here.", "Done."]


def test_label_carried_through():
    stats = sentence_stats("Hi there.", label="Chapter2")
    assert stats.label == "Chapter2"


def test_result_is_immutable():
    stats = sentence_stats("Hello world.")
    assert isinstance(stats, SentenceStats)
    with pytest.raises(AttributeError):
        stats.sentences = 5


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        split_sentences(None)


def test_rejects_non_string_label():
    with pytest.raises(TypeError, match="label must be a string"):
        sentence_stats("hi.", label=object())
