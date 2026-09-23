import pytest

from emphasis_balance import (
    EmphasisIssue,
    check_emphasis,
    is_balanced,
)


def test_balanced_document_passes():
    text = "This has `code` and **bold** and *em* text.\n"
    assert check_emphasis(text) == []
    assert is_balanced(text) is True


def test_unclosed_code_span_reported():
    text = "Here is an `unclosed span.\n"
    (issue,) = check_emphasis(text)
    assert issue.kind == "unclosed-code-span"
    assert issue.line == 1
    assert is_balanced(text) is False


def test_balanced_code_span_passes():
    assert check_emphasis("A `b` c `d` e\n") == []


def test_unbalanced_strong_reported():
    text = "This is **bold that never ends.\n"
    (issue,) = check_emphasis(text)
    assert issue.kind == "unbalanced-strong"


def test_balanced_strong_passes():
    assert check_emphasis("**one** and **two**\n") == []


def test_strong_inside_code_span_is_ignored():
    # The ** here is literal text inside a code span, not emphasis.
    assert check_emphasis("Use `a ** b` in code.\n") == []


def test_escaped_backtick_not_counted():
    assert check_emphasis("A literal \\` backtick.\n") == []


def test_escaped_asterisks_not_counted():
    assert check_emphasis("Literal \\*\\* markers.\n") == []


def test_unterminated_fence_reported():
    text = "intro\n\n```python\nx = 1\n"
    (issue,) = check_emphasis(text)
    assert issue.kind == "unterminated-fence"
    assert issue.line == 3


def test_closed_fence_passes():
    text = "```python\n**not bold** `not code\n```\n"
    assert check_emphasis(text) == []


def test_content_inside_fence_not_checked():
    text = "```\nthis has `one backtick and **one strong\n```\n"
    assert check_emphasis(text) == []


def test_multiple_issues_sorted_by_line():
    text = "`bad\n\n**alsobad\n"
    lines = [i.line for i in check_emphasis(text)]
    assert lines == [1, 3]


def test_odd_backticks_suppress_strong_check_on_same_line():
    # Odd backticks make the strong count unreliable, so only one issue.
    text = "`open **bold\n"
    kinds = [i.kind for i in check_emphasis(text)]
    assert kinds == ["unclosed-code-span"]


def test_check_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_emphasis(None)


def test_issue_is_immutable():
    (issue,) = check_emphasis("`bad\n")
    assert isinstance(issue, EmphasisIssue)
    with pytest.raises(AttributeError):
        issue.line = 9
