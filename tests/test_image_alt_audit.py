import pytest

from image_alt_audit import (
    AltIssue,
    all_images_have_alt,
    audit_alt_text,
)


def test_image_with_good_alt_passes():
    text = "![A neural network diagram](net.png)\n"
    assert audit_alt_text(text) == []
    assert all_images_have_alt(text) is True


def test_empty_markdown_alt_is_reported():
    text = "![](figure1.png)\n"
    (issue,) = audit_alt_text(text)
    assert issue.kind == "empty"
    assert issue.src == "figure1.png"
    assert issue.line == 1
    assert all_images_have_alt(text) is False


def test_whitespace_only_alt_is_empty():
    (issue,) = audit_alt_text("![   ](x.png)\n")
    assert issue.kind == "empty"


def test_placeholder_alt_is_reported():
    for word in ("image", "Screenshot", "FIGURE"):
        (issue,) = audit_alt_text(f"![{word}](x.png)\n")
        assert issue.kind == "placeholder"


def test_reference_style_image_is_audited():
    text = "![][logo]\n\n[logo]: logo.png\n"
    (issue,) = audit_alt_text(text)
    assert issue.kind == "empty"
    assert issue.src == "[logo]"


def test_html_img_without_alt_is_missing():
    (issue,) = audit_alt_text('<img src="diagram.png">\n')
    assert issue.kind == "missing"
    assert issue.src == "diagram.png"


def test_html_img_with_alt_passes():
    assert audit_alt_text('<img src="d.png" alt="A useful diagram">\n') == []


def test_html_img_empty_alt_is_reported():
    (issue,) = audit_alt_text("<img src='d.png' alt=''>\n")
    assert issue.kind == "empty"


def test_images_inside_code_fence_are_ignored():
    text = "```\n![](inside.png)\n<img src='x.png'>\n```\n"
    assert audit_alt_text(text) == []


def test_multiple_images_on_one_line():
    text = "![](a.png) and ![ok](b.png) and ![](c.png)\n"
    srcs = [i.src for i in audit_alt_text(text)]
    assert srcs == ["a.png", "c.png"]


def test_issues_sorted_by_line():
    text = "![](a.png)\n\ntext\n\n![](b.png)\n"
    lines = [i.line for i in audit_alt_text(text)]
    assert lines == [1, 5]


def test_audit_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        audit_alt_text(None)


def test_issue_is_immutable():
    (issue,) = audit_alt_text("![](a.png)\n")
    assert isinstance(issue, AltIssue)
    with pytest.raises(AttributeError):
        issue.src = "b.png"
