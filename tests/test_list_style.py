import pytest

from list_style import (
    ListStyleIssue,
    check_list_style,
    is_consistent,
)


def test_consistent_bullets_pass():
    text = "- one\n- two\n- three\n"
    assert check_list_style(text) == []
    assert is_consistent(text) is True


def test_mixed_bullets_flag_the_minority():
    text = "- one\n* two\n- three\n"
    (issue,) = check_list_style(text)
    assert issue.kind == "bullet"
    assert issue.found == "*"
    assert issue.expected == "-"
    assert issue.line == 2
    assert is_consistent(text) is False


def test_explicit_preferred_bullet_overrides_first_seen():
    text = "* one\n* two\n"
    issues = check_list_style(text, bullet="-")
    assert len(issues) == 2
    assert all(i.expected == "-" for i in issues)


def test_ordered_delimiter_consistency():
    text = "1. first\n2. second\n"
    assert check_list_style(text) == []


def test_mixed_ordered_delimiter_flagged():
    text = "1. first\n2) second\n"
    (issue,) = check_list_style(text)
    assert issue.kind == "ordered"
    assert issue.found == ")"
    assert issue.expected == "."


def test_explicit_ordered_style():
    text = "1) a\n2) b\n"
    issues = check_list_style(text, ordered=".")
    assert [i.found for i in issues] == [")", ")"]


def test_indented_nested_items_are_checked():
    text = "- top\n  * nested\n"
    (issue,) = check_list_style(text)
    assert issue.line == 2
    assert issue.found == "*"


def test_list_markers_inside_code_fence_are_ignored():
    text = "- real\n\n```\n* not a list\n+ also not\n```\n"
    assert check_list_style(text) == []


def test_marker_needs_content_and_space():
    # A horizontal rule "---" or a bare "*" is not a list item.
    assert check_list_style("- real\n\n---\n") == []
    assert check_list_style("- real\n*\n") == []


def test_bullets_and_ordered_tracked_independently():
    text = "- b\n1. o\n* b2\n2) o2\n"
    kinds = sorted(i.kind for i in check_list_style(text))
    assert kinds == ["bullet", "ordered"]


def test_invalid_preferred_values_rejected():
    with pytest.raises(ValueError, match="bullet must be"):
        check_list_style("- a\n", bullet="x")
    with pytest.raises(ValueError, match="ordered must be"):
        check_list_style("1. a\n", ordered="!")


def test_check_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_list_style(None)


def test_issue_is_immutable():
    (issue,) = check_list_style("- a\n* b\n")
    assert isinstance(issue, ListStyleIssue)
    with pytest.raises(AttributeError):
        issue.found = "-"
