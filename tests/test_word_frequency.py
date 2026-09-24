import pytest

from word_frequency import (
    STOPWORDS,
    WordCount,
    total_words,
    word_frequencies,
)


def test_counts_are_case_insensitive():
    result = word_frequencies("Agent agent AGENT", include_stopwords=True)
    assert result[0].word == "agent"
    assert result[0].count == 3


def test_stopwords_removed_by_default():
    words = {wc.word for wc in word_frequencies("the model is a model")}
    assert "the" not in words
    assert "is" not in words
    assert "model" in words


def test_include_stopwords_keeps_them():
    words = {wc.word for wc in word_frequencies("the the model", include_stopwords=True)}
    assert "the" in words


def test_ranking_by_count_then_alpha():
    text = "beta beta alpha alpha gamma"
    result = word_frequencies(text, include_stopwords=True)
    # alpha and beta both appear twice; alpha sorts first, gamma last.
    assert [wc.word for wc in result] == ["alpha", "beta", "gamma"]


def test_top_n_limits_result():
    text = "one one one two two three"
    result = word_frequencies(text, include_stopwords=True, top_n=2)
    assert len(result) == 2
    assert result[0].word == "one"


def test_frequency_is_proportion():
    result = word_frequencies("aa aa bb bb", include_stopwords=True)
    assert result[0].frequency == pytest.approx(0.5)


def test_fenced_code_is_ignored():
    text = "prose word\n```\ncodeword codeword codeword\n```\n"
    words = {wc.word for wc in word_frequencies(text, include_stopwords=True)}
    assert "codeword" not in words
    assert "prose" in words


def test_link_target_dropped_text_kept():
    text = "see [documentation](https://example.com/page)"
    words = {wc.word for wc in word_frequencies(text, include_stopwords=True)}
    assert "documentation" in words
    assert "example" not in words


def test_min_length_filters_short_words():
    result = word_frequencies("ab abc abcd", include_stopwords=True, min_length=3)
    assert {wc.word for wc in result} == {"abc", "abcd"}


def test_empty_text_returns_empty_list():
    assert word_frequencies("") == []
    assert word_frequencies("the a an is") == []


def test_total_words_matches_sum_of_counts():
    text = "model model agent prompt"
    result = word_frequencies(text, include_stopwords=True)
    assert total_words(text, include_stopwords=True) == sum(wc.count for wc in result)


def test_stopwords_set_is_frozen():
    assert isinstance(STOPWORDS, frozenset)


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        word_frequencies(None)


def test_rejects_non_positive_min_length():
    with pytest.raises(ValueError, match="min_length must be positive"):
        word_frequencies("hi", min_length=0)


def test_rejects_non_positive_top_n():
    with pytest.raises(ValueError, match="top_n must be positive"):
        word_frequencies("hi", top_n=0)


def test_wordcount_is_immutable():
    (wc, *_rest) = word_frequencies("agent", include_stopwords=True)
    assert isinstance(wc, WordCount)
    with pytest.raises(AttributeError):
        wc.count = 5
