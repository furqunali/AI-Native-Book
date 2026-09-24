import pytest

from link_text_quality import (
    LinkTextIssue,
    check_link_text,
    is_descriptive,
)


def test_descriptive_link_passes():
    text = "See the [CommonMark specification](https://spec.commonmark.org).\n"
    assert check_link_text(text) == []
    assert is_descriptive(text) is True


def test_click_here_flagged():
    text = "To continue [click here](https://example.com).\n"
    (issue,) = check_link_text(text)
    assert issue.text == "click here"
    assert issue.target == "https://example.com"
    assert is_descriptive(text) is False


def test_bare_here_flagged():
    text = "Docs are [here](d.md).\n"
    (issue,) = check_link_text(text)
    assert issue.line == 1


def test_this_and_link_flagged():
    text = "[this](a) and [link](b)\n"
    assert len(check_link_text(text)) == 2


def test_normalisation_handles_case_and_punctuation():
    text = "[Click Here!](x)\n"
    assert len(check_link_text(text)) == 1


def test_image_link_ignored():
    text = "![here](img.png)\n"
    assert check_link_text(text) == []


def test_code_span_link_ignored():
    text = "inline `[here](x)` sample\n"
    assert check_link_text(text) == []


def test_fenced_code_ignored():
    text = "```\n[click here](x)\n```\n"
    assert check_link_text(text) == []


def test_multiple_issues_ordered_by_line():
    text = "[here](a)\ngood [real docs](b)\n[this](c)\n"
    lines = [i.line for i in check_link_text(text)]
    assert lines == [1, 3]


def test_custom_bad_phrases():
    text = "[details](x)\n"
    assert check_link_text(text, bad_phrases={"details"}) != []
    assert check_link_text(text) == []


def test_two_links_on_one_line():
    text = "[here](a) and [read more](b)\n"
    assert len(check_link_text(text)) == 2


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_link_text(3.14)


def test_issue_is_immutable():
    (issue,) = check_link_text("[here](a)\n")
    assert isinstance(issue, LinkTextIssue)
    with pytest.raises(AttributeError):
        issue.line = 2
