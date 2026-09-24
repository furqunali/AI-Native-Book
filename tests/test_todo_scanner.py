import pytest

from todo_scanner import (
    TodoMarker,
    has_todos,
    scan_todos,
)


def test_finds_todo_with_line_number():
    text = "intro\nTODO: write this section\nmore\n"
    (marker,) = scan_todos(text)
    assert marker.line == 2
    assert marker.marker == "TODO"
    assert marker.note == "write this section"


def test_all_default_markers_detected():
    text = "TODO a\nFIXME b\nTBD c\nXXX d\n"
    markers = [m.marker for m in scan_todos(text)]
    assert markers == ["TODO", "FIXME", "TBD", "XXX"]


def test_case_sensitive_lowercase_ignored():
    assert scan_todos("this is my todo list for tbd items\n") == []


def test_marker_must_be_whole_word():
    # "TODONE" should not match the TODO marker.
    assert scan_todos("TODONE is not a marker\n") == []


def test_note_separator_stripped():
    (marker,) = scan_todos("FIXME - broken link\n")
    assert marker.note == "broken link"


def test_marker_without_note_has_empty_note():
    (marker,) = scan_todos("here XXX\n")
    assert marker.note == ""


def test_full_line_text_preserved():
    (marker,) = scan_todos("    TODO indent kept\n")
    assert marker.text == "    TODO indent kept"


def test_one_marker_per_line():
    (marker,) = scan_todos("TODO first FIXME second\n")
    assert marker.marker == "TODO"


def test_markers_in_code_still_flagged():
    text = "```\n# TODO fix the example\n```\n"
    (marker,) = scan_todos(text)
    assert marker.marker == "TODO"


def test_custom_markers():
    (marker,) = scan_todos("REVIEW this later\n", markers=("REVIEW",))
    assert marker.marker == "REVIEW"


def test_has_todos_boolean():
    assert has_todos("TODO x\n") is True
    assert has_todos("all clean\n") is False


def test_result_is_immutable():
    (marker,) = scan_todos("TODO x\n")
    assert isinstance(marker, TodoMarker)
    with pytest.raises(AttributeError):
        marker.line = 9


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        scan_todos(None)


def test_rejects_empty_markers():
    with pytest.raises(ValueError, match="markers must not be empty"):
        scan_todos("TODO x\n", markers=())


def test_rejects_non_tuple_markers():
    with pytest.raises(TypeError, match="markers must be a tuple"):
        scan_todos("TODO x\n", markers=["TODO"])
