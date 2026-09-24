import pytest

from reading_time import (
    ReadingTime,
    count_words,
    estimate_reading_time,
)


def test_word_count_of_plain_prose():
    assert count_words("one two three four five") == 5


def test_word_count_ignores_punctuation_only_markers():
    # The '#' and '-' are markers, not words.
    assert count_words("# Heading\n\n- item one\n") == 3


def test_estimate_rounds_up_to_whole_minute():
    text = " ".join(["word"] * 250)  # 250 words
    rt = estimate_reading_time(text, words_per_minute=200)
    assert rt.words == 250
    assert rt.minutes == 2  # 1.25 -> rounds up to 2


def test_estimate_at_least_one_minute_for_short_text():
    rt = estimate_reading_time("a few words here", words_per_minute=200)
    assert rt.minutes == 1


def test_empty_text_is_zero_minutes():
    rt = estimate_reading_time("", words_per_minute=200)
    assert rt.words == 0
    assert rt.code_words == 0
    assert rt.minutes == 0


def test_code_words_counted_separately():
    text = "prose word\n\n```\ncode line here\n```\n"
    rt = estimate_reading_time(text)
    assert rt.words == 2
    assert rt.code_words == 3


def test_slower_code_rate_increases_minutes():
    text = "```\n" + " ".join(["x"] * 100) + "\n```\n"
    fast = estimate_reading_time(text, words_per_minute=200)
    slow = estimate_reading_time(text, words_per_minute=200, code_words_per_minute=50)
    assert slow.minutes > fast.minutes


def test_count_words_can_exclude_code():
    text = "prose\n\n```\ncode here now\n```\n"
    assert count_words(text, include_code=False) == 1
    assert count_words(text, include_code=True) == 4


def test_label_is_carried_through():
    rt = estimate_reading_time("hello world", label="Chapter1")
    assert rt.label == "Chapter1"


def test_default_label():
    rt = estimate_reading_time("hi there")
    assert rt.label == "chapter"


def test_result_is_immutable():
    rt = estimate_reading_time("hello world")
    assert isinstance(rt, ReadingTime)
    with pytest.raises(AttributeError):
        rt.minutes = 99


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        estimate_reading_time(None)


def test_rejects_non_positive_wpm():
    with pytest.raises(ValueError, match="words_per_minute must be positive"):
        estimate_reading_time("hi", words_per_minute=0)


def test_rejects_non_positive_code_wpm():
    with pytest.raises(ValueError, match="code_words_per_minute must be positive"):
        estimate_reading_time("hi", code_words_per_minute=-3)


def test_rejects_non_string_label():
    with pytest.raises(TypeError, match="label must be a string"):
        estimate_reading_time("hi", label=5)
