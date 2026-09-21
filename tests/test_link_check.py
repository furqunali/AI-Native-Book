import json
from pathlib import Path

from link_check import (
    Link,
    LinkReport,
    check_document,
    check_links,
    extract_headings,
    parse_links,
    parse_target,
    slugify,
    to_json,
)


def test_slugify_matches_github_style():
    assert slugify("The Building Blocks") == "the-building-blocks"
    assert slugify("The `RAG` Pattern!") == "the-rag-pattern"
    # GitHub removes the em dash but does not collapse the surrounding spaces.
    assert slugify("Data — The Fuel") == "data--the-fuel"


def test_extract_headings_ignores_fenced_code():
    text = "# Real Heading\n\n```\n# not a heading\n```\n\n## Second Heading\n"
    assert extract_headings(text) == ("real-heading", "second-heading")


def test_parse_links_classifies_external_and_anchors():
    text = "See [site](https://example.com) and [top](#intro) and [lic](LICENSE)."
    links = parse_links("doc.md", text)
    by_target = {link.target: link for link in links}
    assert by_target["https://example.com"].external is True
    assert by_target["#intro"].external is False
    assert by_target["#intro"].anchor == "intro"
    assert by_target["LICENSE"].path == "LICENSE"
    assert by_target["LICENSE"].external is False


def test_parse_links_skips_images_and_fenced_code():
    text = "![alt](img.png)\n\n```\n[fenced](y)\n```\n\n[ok](z.md)\n"
    targets = {link.target for link in parse_links("d.md", text)}
    assert "img.png" not in targets  # image, not a link
    assert "y" not in targets  # inside a fenced code block
    assert targets == {"z.md"}


def test_parse_target_splits_path_and_anchor():
    assert parse_target("Chapter2.md#evolution") == ("Chapter2.md", "evolution")
    assert parse_target("#local") == ("", "local")
    assert parse_target("file.md") == ("file.md", "")


def test_missing_file_is_reported(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n[gone](does-not-exist.md)\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert len(issues) == 1
    assert issues[0].code == "MISSING_FILE"
    assert issues[0].source == "a.md"


def test_valid_cross_file_anchor_passes(tmp_path):
    (tmp_path / "target.md").write_text("# Target\n\n## Deep Dive\n", encoding="utf-8")
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n[go](target.md#deep-dive)\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert issues == ()


def test_missing_anchor_is_reported(tmp_path):
    (tmp_path / "target.md").write_text("# Target\n\n## Present\n", encoding="utf-8")
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n[go](target.md#absent)\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert len(issues) == 1
    assert issues[0].code == "MISSING_ANCHOR"


def test_same_document_anchor_is_resolved(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n## Section One\n\n[jump](#section-one) [bad](#nope)\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert [i.code for i in issues] == ["MISSING_ANCHOR"]
    assert issues[0].target == "#nope"


def test_empty_target_is_reported(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n[nothing]()\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert [i.code for i in issues] == ["EMPTY_TARGET"]


def test_external_links_are_never_fetched_or_flagged(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text(
        "# A\n\n[x](https://nope.invalid/does/not/resolve) [m](mailto:a@b.com)\n",
        encoding="utf-8",
    )
    links, issues = check_document(doc, tmp_path)
    assert issues == ()
    assert sum(1 for link in links if link.external) == 2


def test_anchor_into_non_markdown_target_is_ignored(tmp_path):
    (tmp_path / "data.json").write_text("{}", encoding="utf-8")
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n[d](data.json#whatever)\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert issues == ()


def test_check_links_aggregates_and_round_trips_json(tmp_path):
    (tmp_path / "Chapter1.md").write_text(
        "# One\n\n[ext](https://example.com) [bad](missing.md)\n", encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("# Readme\n\n[c1](Chapter1.md#one)\n", encoding="utf-8")
    report = check_links(tmp_path)
    assert isinstance(report, LinkReport)
    assert report.documents == 2
    assert report.external == 1
    assert report.internal == 2
    assert report.valid is False
    assert [i.code for i in report.issues] == ["MISSING_FILE"]

    payload = json.loads(to_json(report))
    assert payload["valid"] is False
    assert payload["links"] == 3
    assert payload["issues"][0]["code"] == "MISSING_FILE"


def test_real_book_has_no_broken_internal_links():
    """Regression guard: the shipped book must have clean internal links."""
    report = check_links(Path("."))
    assert report.documents >= 14  # 13 chapters + README
    assert report.valid, [f"{i.source} -> {i.target} ({i.code})" for i in report.issues]
