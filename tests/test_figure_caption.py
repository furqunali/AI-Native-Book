import pytest

from figure_caption import (
    CaptionIssue,
    find_uncaptioned,
    is_fully_captioned,
)


def test_image_with_italic_caption_passes():
    text = "![alt](img.png)\n*Figure 1. A diagram.*\n"
    assert find_uncaptioned(text) == []
    assert is_fully_captioned(text) is True


def test_image_with_figure_prefix_caption_passes():
    text = "![alt](img.png)\nFigure 2 shows the loop.\n"
    assert find_uncaptioned(text) == []


def test_image_with_blank_then_caption_passes():
    text = "![alt](img.png)\n\n*A caption below a blank line.*\n"
    assert find_uncaptioned(text) == []


def test_image_without_caption_flagged():
    text = "![alt](img.png)\nJust some ordinary prose.\n"
    (issue,) = find_uncaptioned(text)
    assert issue.line == 1
    assert issue.alt == "alt"
    assert issue.target == "img.png"
    assert is_fully_captioned(text) is False


def test_image_at_end_of_document_flagged():
    text = "intro\n\n![alt](img.png)\n"
    (issue,) = find_uncaptioned(text)
    assert issue.line == 3


def test_image_followed_by_only_blanks_flagged():
    text = "![alt](img.png)\n\n\n"
    (issue,) = find_uncaptioned(text)
    assert issue.line == 1


def test_inline_image_is_ignored():
    text = "See this ![alt](img.png) in a sentence.\n"
    assert find_uncaptioned(text) == []


def test_image_followed_by_another_image_flagged():
    text = "![one](a.png)\n![two](b.png)\n*Caption for two.*\n"
    lines = [i.line for i in find_uncaptioned(text)]
    assert lines == [1]


def test_image_inside_code_fence_ignored():
    text = "```\n![alt](img.png)\n```\n"
    assert find_uncaptioned(text) == []


def test_custom_prefix():
    text = "![alt](img.png)\nExhibit A: the result.\n"
    assert find_uncaptioned(text, caption_prefixes=("exhibit",)) == []
    assert len(find_uncaptioned(text)) == 1


def test_multiple_issues_ordered_by_line():
    text = "![a](a.png)\ntext\n\n![b](b.png)\nmore text\n"
    lines = [i.line for i in find_uncaptioned(text)]
    assert lines == [1, 4]


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        find_uncaptioned(42)


def test_issue_is_immutable():
    (issue,) = find_uncaptioned("![a](a.png)\nprose\n")
    assert isinstance(issue, CaptionIssue)
    with pytest.raises(AttributeError):
        issue.line = 9
