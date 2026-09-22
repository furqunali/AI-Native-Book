import pytest

from chapter_readability import (
    ReadabilityReport,
    count_syllables,
    estimate_readability,
)


def test_counts_words_and_sentences():
    report = estimate_readability("The cat sat. The dog ran fast.")
    assert report.words == 7
    assert report.sentences == 2


def test_reading_minutes_follow_pace():
    text = " ".join(["word"] * 400)
    assert estimate_readability(text, words_per_minute=200).reading_minutes == 2.0
    assert estimate_readability(text, words_per_minute=400).reading_minutes == 1.0


def test_fenced_code_is_excluded_from_counts():
    prose = "Read this sentence here."
    with_code = prose + "\n\n```python\nfor x in range(100):\n    print(x)\n```\n"
    assert estimate_readability(with_code).words == estimate_readability(prose).words


def test_link_targets_are_ignored_but_text_kept():
    report = estimate_readability("See [the guide](https://example.com/very/long/path).")
    assert report.words == 3


def test_inline_code_and_headings_are_stripped():
    # Heading marker "#" is dropped but its text "Title" is prose; `x` keeps its word.
    report = estimate_readability("# Title\n\nUse `x` here.")
    assert report.words == 4


def test_words_without_terminator_count_as_one_sentence():
    report = estimate_readability("a chapter with no ending punctuation")
    assert report.sentences == 1
    assert report.words == 6


def test_empty_text_returns_zeroed_report():
    report = estimate_readability("   \n\n  ")
    assert report == ReadabilityReport(0, 0, 0, 0.0, 0.0, 0.0)


def test_code_only_chapter_returns_zeroed_report():
    report = estimate_readability("```\ncode only\n```")
    assert report.words == 0
    assert report.reading_minutes == 0.0


def test_flesch_scores_are_computed():
    # Simple one-syllable prose scores as very easy / low grade.
    report = estimate_readability("The cat sat on the mat. The dog ran.")
    assert report.flesch_reading_ease > 90
    assert report.flesch_kincaid_grade < 3


def test_syllable_heuristic():
    assert count_syllables("cat") == 1
    assert count_syllables("apple") == 2
    assert count_syllables("make") == 1  # trailing silent e dropped
    assert count_syllables("bee") == 1  # ee not treated as silent e
    assert count_syllables("") == 0
    assert count_syllables("123") == 0


def test_rejects_non_string_text():
    with pytest.raises(TypeError, match="text must be a string"):
        estimate_readability(None)


def test_rejects_non_positive_pace():
    with pytest.raises(ValueError, match="must be positive"):
        estimate_readability("hello world", words_per_minute=0)


def test_rejects_bool_pace():
    with pytest.raises(TypeError, match="must be an int"):
        estimate_readability("hello world", words_per_minute=True)


def test_report_is_immutable():
    report = estimate_readability("Hello world.")
    with pytest.raises(AttributeError):
        report.words = 99
