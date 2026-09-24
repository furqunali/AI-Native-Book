import pytest

from blockquote_style import (
    BlockquoteIssue,
    check_blockquote_style,
    is_consistent,
)


def test_well_formed_blockquote_passes():
    assert check_blockquote_style("> a proper quote\n") == []
    assert is_consistent("> a proper quote\n") is True


def test_missing_space_flagged():
    (issue,) = check_blockquote_style(">glued text\n")
    assert issue.kind == "missing-space"
    assert issue.line == 1


def test_extra_space_flagged():
    (issue,) = check_blockquote_style(">   too much space\n")
    assert issue.kind == "extra-space"


def test_bare_marker_line_allowed():
    text = "> first para\n>\n> second para\n"
    assert check_blockquote_style(text) == []


def test_trailing_space_only_allowed():
    assert check_blockquote_style("> \n") == []


def test_nested_quote_well_formed():
    assert check_blockquote_style("> > nested quote\n") == []


def test_nested_quote_missing_space_flagged():
    (issue,) = check_blockquote_style(">>glued\n")
    assert issue.kind == "missing-space"


def test_indented_blockquote_checked():
    (issue,) = check_blockquote_style("   >glued\n")
    assert issue.kind == "missing-space"


def test_non_blockquote_lines_ignored():
    assert check_blockquote_style("normal prose here\n") == []


def test_code_fence_ignored():
    text = "```\n>glued in code\n```\n"
    assert check_blockquote_style(text) == []


def test_multiple_issues_ordered():
    text = ">one\n\n>  two\n"
    kinds = [(i.line, i.kind) for i in check_blockquote_style(text)]
    assert kinds == [(1, "missing-space"), (3, "extra-space")]


def test_original_text_preserved():
    (issue,) = check_blockquote_style(">glued\n")
    assert issue.text == ">glued"


def test_result_is_immutable():
    (issue,) = check_blockquote_style(">glued\n")
    assert isinstance(issue, BlockquoteIssue)
    with pytest.raises(AttributeError):
        issue.line = 9


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_blockquote_style(None)
