import pytest

from code_fence_close import (
    FenceIssue,
    check_fences,
    is_balanced,
)


def test_closed_block_passes():
    text = "```python\nx = 1\n```\n"
    assert check_fences(text) == []
    assert is_balanced(text) is True


def test_no_fences_passes():
    assert check_fences("just prose\nmore prose\n") == []


def test_unclosed_block_reported():
    text = "intro\n\n```python\nx = 1\n"
    (issue,) = check_fences(text)
    assert issue.kind == "unclosed-fence"
    assert issue.line == 3
    assert is_balanced(text) is False


def test_tilde_block_closes():
    text = "~~~\ncode\n~~~\n"
    assert check_fences(text) == []


def test_mismatched_fence_char_reported():
    text = "```\ncode\n~~~\n"
    (issue,) = check_fences(text)
    assert issue.kind == "mismatched-fence"
    assert issue.line == 3


def test_shorter_closing_fence_reported():
    text = "````\ncode\n```\n"
    (issue,) = check_fences(text)
    assert issue.kind == "mismatched-fence"
    assert issue.line == 3


def test_longer_closing_fence_allowed():
    # Closing fence may be longer than the opener.
    text = "```\ncode\n`````\n"
    assert check_fences(text) == []


def test_info_string_on_opener_only():
    # A "```lang" line while a block is open is content, not a close.
    text = "```\n```python\n```\n"
    assert check_fences(text) == []


def test_two_blocks_pass():
    text = "```\na\n```\n\n```\nb\n```\n"
    assert check_fences(text) == []


def test_backticks_inside_open_block_are_content():
    text = "```\nnot a `inline` close\n```\n"
    assert check_fences(text) == []


def test_multiple_blocks_second_unclosed():
    text = "```\na\n```\n\n```\nb\n"
    (issue,) = check_fences(text)
    assert issue.kind == "unclosed-fence"
    assert issue.line == 5


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_fences(None)


def test_issue_is_immutable():
    (issue,) = check_fences("```\nx\n")
    assert isinstance(issue, FenceIssue)
    with pytest.raises(AttributeError):
        issue.line = 1
