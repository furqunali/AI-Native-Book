import pytest

from chapter_keywords import (
    STOPWORDS,
    Keyword,
    extract_keywords,
    tokenize,
)


def test_counts_and_ranks_by_frequency():
    text = "Agents plan. Agents act. Agents learn from feedback."
    keywords = extract_keywords(text)
    assert keywords[0].term == "agents"
    assert keywords[0].count == 3


def test_stopwords_are_removed():
    terms = [kw.term for kw in extract_keywords("The model and the agent are here.")]
    assert "the" not in terms
    assert "and" not in terms
    assert "are" not in terms
    assert "model" in terms
    assert "agent" in terms


def test_short_words_are_dropped_by_min_length():
    # "ai" is length 2 and dropped at the default min_length of 3.
    terms = [kw.term for kw in extract_keywords("AI ai ai models scale")]
    assert "ai" not in terms
    assert "models" in terms
    # Lowering min_length keeps it.
    terms2 = [kw.term for kw in extract_keywords("AI ai ai models", min_length=2)]
    assert "ai" in terms2


def test_pure_numbers_are_ignored():
    terms = [kw.term for kw in extract_keywords("release 2024 shipped models 2024")]
    assert "2024" not in terms
    assert "models" in terms


def test_fenced_code_is_excluded():
    prose = "Prompts guide models today."
    with_code = prose + "\n\n```python\nprompts = models = models = models\n```\n"
    assert extract_keywords(with_code) == extract_keywords(prose)


def test_link_target_ignored_but_text_kept():
    keywords = extract_keywords("See [context windows](https://example.com/context/window/spec)")
    terms = [kw.term for kw in keywords]
    assert "context" in terms
    assert "windows" in terms
    assert "example" not in terms
    assert "https" not in terms


def test_curly_and_straight_apostrophes_folded_as_stopwords():
    # Both spellings of "don't" are stopwords and must be dropped.
    terms = [kw.term for kw in extract_keywords("Don't panic. Don’t worry. Ship models.")]
    assert "don't" not in terms
    assert terms == ["models", "panic", "ship", "worry"]


def test_ties_broken_alphabetically():
    keywords = extract_keywords("zebra apple mango zebra apple mango")
    # All three tie at count 2; order must be alphabetical.
    assert [kw.term for kw in keywords] == ["apple", "mango", "zebra"]


def test_top_n_limits_results():
    text = "alpha alpha alpha beta beta gamma"
    keywords = extract_keywords(text, top_n=2)
    assert len(keywords) == 2
    assert [kw.term for kw in keywords] == ["alpha", "beta"]


def test_min_count_filters_rare_terms():
    text = "common common common rare"
    terms = [kw.term for kw in extract_keywords(text, min_count=2)]
    assert terms == ["common"]


def test_frequency_is_share_of_counted_tokens():
    # Four counted tokens: alpha, alpha, beta, gamma.
    keywords = extract_keywords("alpha alpha beta gamma")
    by_term = {kw.term: kw for kw in keywords}
    assert by_term["alpha"].frequency == 0.5
    assert by_term["beta"].frequency == 0.25


def test_empty_and_code_only_return_empty():
    assert extract_keywords("   \n\n ") == []
    assert extract_keywords("```\nonly code here\n```") == []


def test_stopword_only_text_returns_empty():
    assert extract_keywords("the and or but if") == []


def test_custom_stopwords_override_default():
    # With an empty stopword set, otherwise-common words survive.
    terms = [kw.term for kw in extract_keywords("the model", stopwords=frozenset())]
    assert "the" in terms
    # And custom stopwords are honoured.
    terms2 = [kw.term for kw in extract_keywords("model agent", stopwords={"model"})]
    assert "model" not in terms2
    assert "agent" in terms2


def test_tokenize_preserves_reading_order_and_duplicates():
    assert tokenize("Models beat models beating baselines") == [
        "models",
        "beat",
        "models",
        "beating",
        "baselines",
    ]


def test_default_stopwords_is_frozenset():
    assert isinstance(STOPWORDS, frozenset)
    assert "the" in STOPWORDS


def test_rejects_non_string_text():
    with pytest.raises(TypeError, match="text must be a string"):
        extract_keywords(None)


def test_rejects_non_positive_min_length():
    with pytest.raises(ValueError, match="min_length must be positive"):
        extract_keywords("hello world", min_length=0)


def test_rejects_bool_min_length():
    with pytest.raises(TypeError, match="min_length must be an int"):
        extract_keywords("hello world", min_length=True)


def test_rejects_non_positive_top_n():
    with pytest.raises(ValueError, match="top_n must be positive"):
        extract_keywords("hello world", top_n=0)


def test_rejects_bool_top_n():
    with pytest.raises(TypeError, match="top_n must be an int or None"):
        extract_keywords("hello world", top_n=True)


def test_rejects_non_positive_min_count():
    with pytest.raises(ValueError, match="min_count must be positive"):
        extract_keywords("hello world", min_count=0)


def test_keyword_is_immutable():
    keyword = extract_keywords("models models")[0]
    with pytest.raises(AttributeError):
        keyword.count = 99
    assert isinstance(keyword, Keyword)
