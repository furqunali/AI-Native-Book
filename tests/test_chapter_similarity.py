import pytest

from chapter_similarity import (
    SimilarityResult,
    chapter_similarity,
    keyword_set,
)


def test_identical_chapters_score_one():
    text = "agents orchestrate prompts and context windows"
    result = chapter_similarity(text, text)
    assert result.jaccard == 1.0
    assert result.intersection == result.union


def test_disjoint_chapters_score_zero():
    result = chapter_similarity("alpha beta gamma", "delta epsilon zeta")
    assert result.jaccard == 0.0
    assert result.intersection == 0
    assert result.shared == ()


def test_partial_overlap_jaccard():
    # sets {alpha, beta, gamma} vs {beta, gamma, delta}
    # intersection 2, union 4 -> 0.5
    result = chapter_similarity("alpha beta gamma", "beta gamma delta")
    assert result.jaccard == 0.5
    assert result.intersection == 2
    assert result.union == 4


def test_shared_is_sorted_tuple():
    result = chapter_similarity("gamma beta alpha", "beta gamma")
    assert result.shared == ("beta", "gamma")


def test_similarity_is_case_insensitive():
    result = chapter_similarity("Agent Model", "agent model")
    assert result.jaccard == 1.0


def test_stopwords_do_not_contribute():
    # Only the stopwords overlap; keyword sets are disjoint.
    result = chapter_similarity("the model and the agent", "the tool and the loop")
    assert "the" not in result.shared
    assert result.intersection == 0


def test_two_empty_chapters_score_zero():
    result = chapter_similarity("", "")
    assert result.jaccard == 0.0
    assert result.union == 0


def test_keyword_set_ignores_fenced_code():
    text = "prose keyword\n```\nsecretcode secretcode\n```\n"
    kws = keyword_set(text)
    assert "secretcode" not in kws
    assert "keyword" in kws


def test_keyword_set_min_length():
    kws = keyword_set("ab abc abcd", min_length=4)
    assert kws == frozenset({"abcd"})


def test_symmetry():
    a = "one two three four"
    b = "three four five"
    assert chapter_similarity(a, b).jaccard == chapter_similarity(b, a).jaccard


def test_rejects_non_string():
    with pytest.raises(TypeError):
        keyword_set(123)


def test_rejects_bad_min_length():
    with pytest.raises(ValueError):
        keyword_set("hi", min_length=0)


def test_result_is_immutable():
    result = chapter_similarity("agent", "agent")
    assert isinstance(result, SimilarityResult)
    with pytest.raises(AttributeError):
        result.jaccard = 0.0
