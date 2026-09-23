import pytest

from whitespace_lint import (
    WhitespaceIssue,
    check_whitespace,
    is_clean,
)


def test_clean_document_passes():
    text = "# Title\n\nA paragraph.\n\nAnother.\n"
    assert check_whitespace(text) == []
    assert is_clean(text) is True


def test_trailing_whitespace_reported():
    text = "line with space   \nclean line\n"
    (issue,) = check_whitespace(text)
    assert issue.kind == "trailing-whitespace"
    assert issue.line == 1


def test_hard_tab_reported():
    text = "no tab\n\tindented with tab\n"
    kinds = [i.kind for i in check_whitespace(text)]
    assert "hard-tab" in kinds


def test_consecutive_blank_lines_reported_once():
    text = "a\n\n\n\nb\n"
    issues = [i for i in check_whitespace(text) if i.kind == "consecutive-blanks"]
    assert len(issues) == 1
    assert issues[0].line == 2


def test_single_blank_line_is_allowed():
    text = "a\n\nb\n"
    assert check_whitespace(text) == []


def test_max_blank_run_is_configurable():
    text = "a\n\n\nb\n"
    assert check_whitespace(text, max_blank_run=2) == []
    assert check_whitespace(text, max_blank_run=1) != []


def test_missing_final_newline_reported():
    (issue,) = check_whitespace("no newline at end")
    assert issue.kind == "missing-final-newline"


def test_empty_string_is_clean():
    assert check_whitespace("") == []


def test_trailing_whitespace_inside_code_fence_ignored():
    text = "```\ncode with trailing   \n```\n"
    assert check_whitespace(text) == []


def test_tabs_inside_code_fence_ignored():
    text = "```\n\ttabbed code\n```\n"
    assert check_whitespace(text) == []


def test_blank_runs_inside_code_fence_ignored():
    text = "```\n\n\n\n```\n"
    assert [i for i in check_whitespace(text)
            if i.kind == "consecutive-blanks"] == []


def test_multiple_issues_sorted_by_line():
    text = "trailing  \n\ttab line\n"
    lines = [i.line for i in check_whitespace(text)]
    assert lines == sorted(lines)


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_whitespace(None)


def test_rejects_bad_max_blank_run():
    with pytest.raises(TypeError, match="must be an int"):
        check_whitespace("a\n", max_blank_run=True)
    with pytest.raises(ValueError, match="not be negative"):
        check_whitespace("a\n", max_blank_run=-1)


def test_issue_is_immutable():
    (issue,) = check_whitespace("bad   \n")
    assert isinstance(issue, WhitespaceIssue)
    with pytest.raises(AttributeError):
        issue.line = 5
