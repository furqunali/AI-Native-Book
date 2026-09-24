import pytest

from trailing_heading_punct import (
    TrailingPunctIssue,
    check_trailing_punct,
    has_trailing_punct,
)


def test_clean_heading_passes():
    assert check_trailing_punct("# Introduction\n") == []


def test_trailing_period_flagged():
    (issue,) = check_trailing_punct("# Introduction.\n")
    assert issue.char == "."
    assert issue.line == 1


def test_trailing_colon_flagged():
    (issue,) = check_trailing_punct("## Steps:\n")
    assert issue.char == ":"


def test_all_default_punct_flagged():
    text = "# A.\n\n# B,\n\n# C:\n\n# D;\n\n# E!\n"
    chars = [i.char for i in check_trailing_punct(text)]
    assert chars == [".", ",", ":", ";", "!"]


def test_question_mark_allowed_by_default():
    assert check_trailing_punct("# Why Bother?\n") == []


def test_question_mark_configurable():
    (issue,) = check_trailing_punct("# Why Bother?\n", punctuation="?")
    assert issue.char == "?"


def test_closing_hashes_stripped_before_check():
    (issue,) = check_trailing_punct("## Title. ##\n")
    assert issue.char == "."


def test_inline_code_heading_trailing_backtick_ok():
    # After stripping inline code the heading ends with a letter.
    assert check_trailing_punct("# The `run` command\n") == []


def test_non_heading_lines_ignored():
    assert check_trailing_punct("A sentence ending in a period.\n") == []


def test_code_fence_headings_ignored():
    text = "# Clean\n\n```\n# fake.\n```\n"
    assert check_trailing_punct(text) == []


def test_multiple_headings_ordered():
    text = "# One.\n\n## Two\n\n### Three!\n"
    lines = [i.line for i in check_trailing_punct(text)]
    assert lines == [1, 5]


def test_has_trailing_punct_boolean():
    assert has_trailing_punct("# Bad.\n") is True
    assert has_trailing_punct("# Good\n") is False


def test_result_is_immutable():
    (issue,) = check_trailing_punct("# Bad.\n")
    assert isinstance(issue, TrailingPunctIssue)
    with pytest.raises(AttributeError):
        issue.line = 3


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_trailing_punct(None)


def test_rejects_empty_punctuation():
    with pytest.raises(ValueError, match="punctuation must not be empty"):
        check_trailing_punct("# T\n", punctuation="")
