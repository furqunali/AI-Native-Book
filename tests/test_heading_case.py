import pytest

from heading_case import (
    HeadingCaseIssue,
    check_heading_case,
    is_title_case,
)


def test_proper_title_case_passes():
    assert check_heading_case("# Hello World\n") == []
    assert is_title_case("# Hello World\n") is True


def test_minor_words_lowercase_in_middle_ok():
    assert check_heading_case("# The Lord of the Rings\n") == []


def test_lowercase_first_and_last_flagged():
    (issue,) = check_heading_case("# hello world\n")
    assert issue.words == ("hello", "world")


def test_lowercase_major_word_in_middle_flagged():
    (issue,) = check_heading_case("# Building a great Product\n")
    assert issue.words == ("great",)


def test_acronym_not_flagged():
    assert check_heading_case("# Using the API Today\n") == []


def test_internal_capital_word_not_flagged():
    assert check_heading_case("# The iPhone Era\n") == []


def test_minor_word_first_must_be_capital():
    (issue,) = check_heading_case("# an Introduction\n")
    assert issue.words == ("an",)


def test_multiple_headings_reported_in_order():
    text = "# good Title\n\n## Another bad one\n"
    lines = [i.line for i in check_heading_case(text)]
    assert lines == [1, 3]


def test_code_fence_heading_ignored():
    text = "# Good Heading\n\n```\n# bad heading\n```\n"
    assert check_heading_case(text) == []


def test_heading_with_only_acronym_passes():
    assert check_heading_case("# API\n") == []


def test_non_heading_lines_ignored():
    assert check_heading_case("just some prose words here\n") == []


def test_message_mentions_heading():
    (issue,) = check_heading_case("# broken heading\n")
    assert "broken heading" in issue.message


def test_result_is_immutable():
    (issue,) = check_heading_case("# bad title\n")
    assert isinstance(issue, HeadingCaseIssue)
    with pytest.raises(AttributeError):
        issue.line = 5


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_heading_case(None)
