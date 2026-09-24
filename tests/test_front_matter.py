import pytest

from front_matter import (
    FrontMatterIssue,
    parse_front_matter,
    validate_front_matter,
)


def test_valid_front_matter_parses_cleanly():
    text = "---\ntitle: Intro\nauthor: Furqan\norder: 1\n---\n\n# Body\n"
    metadata, issues = parse_front_matter(text)
    assert metadata == {"title": "Intro", "author": "Furqan", "order": "1"}
    assert issues == []


def test_no_block_returns_none_metadata():
    metadata, issues = parse_front_matter("# Just a heading\n")
    assert metadata is None
    assert issues == []


def test_unterminated_block_is_reported():
    text = "---\ntitle: Intro\n\n# Body without closing fence\n"
    metadata, issues = parse_front_matter(text)
    assert any(i.kind == "unterminated" for i in issues)
    assert metadata == {"title": "Intro"}


def test_malformed_line_reported():
    text = "---\ntitle: Intro\nthis has no colon\n---\n"
    _, issues = parse_front_matter(text)
    assert [i.kind for i in issues] == ["malformed-line"]
    assert issues[0].line == 3


def test_duplicate_key_reported_and_last_wins():
    text = "---\ntitle: One\ntitle: Two\n---\n"
    metadata, issues = parse_front_matter(text)
    assert metadata["title"] == "Two"
    assert any(i.kind == "duplicate-key" for i in issues)


def test_empty_value_reported():
    text = "---\ntitle:\n---\n"
    _, issues = parse_front_matter(text)
    assert any(i.kind == "empty-value" for i in issues)


def test_comments_and_blank_lines_ignored():
    text = "---\n# a comment\n\ntitle: Intro\n---\n"
    metadata, issues = parse_front_matter(text)
    assert metadata == {"title": "Intro"}
    assert issues == []


def test_value_may_contain_colons():
    text = "---\nsummary: see this: a note\n---\n"
    metadata, _ = parse_front_matter(text)
    assert metadata["summary"] == "see this: a note"


def test_validate_missing_required_key():
    text = "---\ntitle: Intro\n---\n"
    issues = validate_front_matter(text, required=("title", "author"))
    assert [i.kind for i in issues] == ["missing-key"]
    assert "author" in issues[0].message


def test_validate_missing_block_when_required():
    issues = validate_front_matter("# No front matter\n", required=("title",))
    assert [i.kind for i in issues] == ["missing-block"]


def test_validate_no_required_and_no_block_is_clean():
    assert validate_front_matter("# No front matter\n") == []


def test_validate_all_required_present():
    text = "---\ntitle: Intro\nauthor: F\n---\n"
    assert validate_front_matter(text, required=("title", "author")) == []


def test_parse_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        parse_front_matter(None)


def test_issue_is_immutable():
    _, issues = parse_front_matter("---\nbad line\n---\n")
    assert isinstance(issues[0], FrontMatterIssue)
    with pytest.raises(AttributeError):
        issues[0].kind = "other"
