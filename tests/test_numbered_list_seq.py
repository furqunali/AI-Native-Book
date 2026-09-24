import pytest

from numbered_list_seq import (
    SequenceIssue,
    check_numbering,
    is_sequential,
)


def test_correct_sequence_passes():
    text = "1. a\n2. b\n3. c\n"
    assert check_numbering(text) == []
    assert is_sequential(text) is True


def test_gap_flagged():
    text = "1. a\n2. b\n4. d\n"
    (issue,) = check_numbering(text)
    assert issue.kind == "out-of-sequence"
    assert issue.found == 4
    assert issue.expected == 3
    assert issue.line == 3


def test_bad_start_flagged():
    text = "2. a\n3. b\n"
    (issue,) = check_numbering(text)
    assert issue.kind == "bad-start"
    assert issue.found == 2
    assert issue.expected == 1


def test_restart_flagged():
    text = "1. a\n2. b\n1. x\n"
    (issue,) = check_numbering(text)
    assert issue.kind == "out-of-sequence"
    assert issue.found == 1
    assert issue.expected == 3


def test_single_blank_line_keeps_run():
    text = "1. a\n\n2. b\n"
    assert check_numbering(text) == []


def test_two_blank_lines_reset_run():
    text = "1. a\n\n\n1. b\n"
    assert check_numbering(text) == []


def test_heading_resets_run():
    text = "1. a\n\n# Section\n\n1. b\n"
    assert check_numbering(text) == []


def test_nested_lists_tracked_independently():
    text = "1. a\n   1. sub\n   2. sub2\n2. b\n"
    assert check_numbering(text) == []


def test_paren_delimiter_supported():
    text = "1) a\n3) c\n"
    (issue,) = check_numbering(text)
    assert issue.found == 3


def test_custom_start_at():
    text = "0. a\n1. b\n"
    assert check_numbering(text, start_at=0) == []


def test_fenced_code_ignored():
    text = "```\n1. a\n5. e\n```\n"
    assert check_numbering(text) == []


def test_result_is_immutable():
    (issue,) = check_numbering("2. a\n")
    assert isinstance(issue, SequenceIssue)
    with pytest.raises(AttributeError):
        issue.found = 1


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_numbering(None)


def test_rejects_non_int_start():
    with pytest.raises(TypeError, match="start_at must be an int"):
        check_numbering("1. a\n", start_at="1")
