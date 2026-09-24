import pytest

from long_paragraph import (
    LongParagraph,
    find_long_paragraphs,
    has_long_paragraphs,
)


def _para(n):
    return " ".join(["word"] * n)


def test_long_paragraph_flagged():
    text = _para(20)
    (lp,) = find_long_paragraphs(text, max_words=10)
    assert lp.words == 20
    assert lp.start_line == 1


def test_short_paragraph_not_flagged():
    assert find_long_paragraphs(_para(5), max_words=10) == []


def test_threshold_is_strict_greater_than():
    # Exactly max_words is allowed.
    assert find_long_paragraphs(_para(10), max_words=10) == []
    assert len(find_long_paragraphs(_para(11), max_words=10)) == 1


def test_paragraphs_separated_by_blank_lines():
    text = _para(20) + "\n\n" + _para(3) + "\n\n" + _para(15)
    results = find_long_paragraphs(text, max_words=10)
    assert [r.start_line for r in results] == [1, 5]


def test_multiline_paragraph_words_summed():
    text = "word word word\nword word word\n"  # 6 words, one paragraph
    (lp,) = find_long_paragraphs(text, max_words=5)
    assert lp.words == 6


def test_headings_not_counted_as_paragraphs():
    text = "# " + _para(30) + "\n"
    assert find_long_paragraphs(text, max_words=10) == []


def test_list_items_not_counted_as_paragraphs():
    text = "- " + _para(30) + "\n"
    assert find_long_paragraphs(text, max_words=10) == []


def test_blockquote_not_counted():
    text = "> " + _para(30) + "\n"
    assert find_long_paragraphs(text, max_words=10) == []


def test_code_block_ignored():
    text = "```\n" + _para(50) + "\n```\n"
    assert find_long_paragraphs(text, max_words=10) == []


def test_preview_contains_first_words():
    (lp,) = find_long_paragraphs(_para(20), max_words=5)
    assert lp.preview == "word word word word word word word word"


def test_start_line_after_blank_lines():
    text = "\n\n" + _para(20)
    (lp,) = find_long_paragraphs(text, max_words=5)
    assert lp.start_line == 3


def test_has_long_paragraphs_boolean():
    assert has_long_paragraphs(_para(20), max_words=5) is True
    assert has_long_paragraphs(_para(3), max_words=5) is False


def test_result_is_immutable():
    (lp,) = find_long_paragraphs(_para(20), max_words=5)
    assert isinstance(lp, LongParagraph)
    with pytest.raises(AttributeError):
        lp.words = 1


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        find_long_paragraphs(None)


def test_rejects_bad_threshold():
    with pytest.raises(ValueError, match="max_words must be at least 1"):
        find_long_paragraphs("x", max_words=0)
