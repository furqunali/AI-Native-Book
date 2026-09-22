import json
from pathlib import Path

import pytest

from anchor_audit import (
    AnchorReport,
    audit_anchors,
    check_document,
    collect_anchors,
    find_anchor_links,
    parse_definitions,
    to_json,
)


def _issue_codes(issues):
    return [i.code for i in issues]


def test_collect_anchors_covers_slugs_attrs_and_html():
    text = (
        "# Getting Started\n"
        "## Install {#install-guide}\n"
        '<a name="legacy"></a>\n'
        '<div id="Sidebar"></div>\n'
    )
    anchors, duplicates = collect_anchors(text)
    assert "getting-started" in anchors  # auto-slug
    # A {#id} heading keeps BOTH its auto-slug (from the remaining text) and id.
    assert "install" in anchors
    assert "install-guide" in anchors  # explicit attr id
    assert "legacy" in anchors  # <a name>
    assert "sidebar" in anchors  # id=, lower-cased
    assert duplicates == frozenset()


def test_collect_anchors_dedupes_repeated_slugs_like_github():
    anchors, _ = collect_anchors("# Repeat\n## Repeat\n### Repeat\n")
    assert {"repeat", "repeat-1", "repeat-2"} <= anchors


def test_collect_anchors_flags_duplicate_explicit_ids_only():
    text = (
        "# One {#dup}\n"
        '<a id="dup"></a>\n'
        "# Repeat\n## Repeat\n"  # slug collision must NOT be a duplicate
    )
    anchors, duplicates = collect_anchors(text)
    assert "dup" in anchors
    assert duplicates == frozenset({"dup"})


def test_code_is_blanked_so_no_false_anchors_or_links():
    text = (
        "# Real\n\n"
        "```\n# Fake Heading\n[x](#real)\n```\n\n"
        "Inline `[y](#nope)` and `# not a heading` stay inert.\n"
    )
    anchors, _ = collect_anchors(text)
    assert anchors == {"real"}
    links = find_anchor_links("d.md", text)
    assert links == ()  # both the fenced and inline-code links are ignored


def test_inline_same_document_anchor_resolution(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n## Section One\n\n[ok](#section-one) [bad](#missing)\n", encoding="utf-8")
    links, issues = check_document(doc, tmp_path)
    assert len(links) == 2
    assert _issue_codes(issues) == ["MISSING_ANCHOR"]
    assert issues[0].anchor == "missing"


def test_cross_file_and_external_anchors_are_out_of_scope(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text(
        "# A\n\n[f](Chapter2.md#evolution) [e](https://x.com#frag) [rel](other.md)\n",
        encoding="utf-8",
    )
    links, issues = check_document(doc, tmp_path)
    assert links == ()  # none are bare same-document #anchors
    assert issues == ()


def test_reference_and_collapsed_links_resolve_via_definitions(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text(
        "# A\n\n"
        "## Deep Dive\n\n"
        "See [the deep dive][dd] and [deep-dive][].\n\n"
        "[dd]: #deep-dive\n"
        "[deep-dive]: #deep-dive\n",
        encoding="utf-8",
    )
    links, issues = check_document(doc, tmp_path)
    assert issues == ()
    kinds = sorted(link.kind for link in links)
    assert kinds == ["collapsed", "reference"]


def test_reference_link_to_missing_anchor_is_reported(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text(
        "# A\n\nJump to [it][x].\n\n[x]: #does-not-exist\n",
        encoding="utf-8",
    )
    _, issues = check_document(doc, tmp_path)
    assert _issue_codes(issues) == ["MISSING_ANCHOR"]
    assert issues[0].anchor == "does-not-exist"


def test_undefined_reference_is_reported(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\nBroken [label][ghost] here.\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert _issue_codes(issues) == ["UNDEFINED_REFERENCE"]
    assert issues[0].anchor == "ghost"


def test_shortcut_reference_link_resolves(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text(
        "# A\n\n## Glossary\n\nSee [glossary] for terms.\n\n[glossary]: #glossary\n",
        encoding="utf-8",
    )
    links, issues = check_document(doc, tmp_path)
    assert issues == ()
    assert [link.kind for link in links] == ["shortcut"]


def test_shortcut_bracket_without_definition_is_ignored(tmp_path):
    doc = tmp_path / "a.md"
    # Plain bracketed prose with no matching definition must not be a link.
    doc.write_text("# A\n\nThis is [just some text] in brackets.\n", encoding="utf-8")
    links, issues = check_document(doc, tmp_path)
    assert links == ()
    assert issues == ()


def test_empty_anchor_target_is_reported(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n[void](#)\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert _issue_codes(issues) == ["EMPTY_ANCHOR"]


def test_explicit_attr_and_html_anchor_targets_resolve(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text(
        "# Setup {#install}\n\n"
        '<a name="appendix"></a>\n\n'
        "[go](#install) and [end](#appendix) and [caps](#APPENDIX)\n",
        encoding="utf-8",
    )
    _, issues = check_document(doc, tmp_path)
    assert issues == ()  # third link proves case-insensitive matching


def test_ambiguous_anchor_is_reported(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text(
        "# A\n\n## Notes {#note}\n\n## More {#note}\n\n[j](#note)\n",
        encoding="utf-8",
    )
    _, issues = check_document(doc, tmp_path)
    assert _issue_codes(issues) == ["AMBIGUOUS_ANCHOR"]


def test_line_numbers_are_reported(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n\n\n[bad](#nope)\n", encoding="utf-8")
    _, issues = check_document(doc, tmp_path)
    assert len(issues) == 1
    assert issues[0].line == 4


def test_parse_definitions_last_wins_and_case_insensitive():
    text = "[Ref]: #first\n[ref]: #second\n"
    defs = parse_definitions(text)
    assert defs["ref"] == "#second"


def test_audit_anchors_aggregates_and_round_trips_json(tmp_path):
    (tmp_path / "Chapter1.md").write_text(
        "# One\n\n## Intro\n\n[ok](#intro) [bad](#gone)\n", encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("# Readme\n\n[self](#readme)\n", encoding="utf-8")
    report = audit_anchors(tmp_path)
    assert isinstance(report, AnchorReport)
    assert report.documents == 2
    assert report.links == 3
    assert report.valid is False
    assert _issue_codes(report.issues) == ["MISSING_ANCHOR"]

    payload = json.loads(to_json(report))
    assert payload["valid"] is False
    assert payload["links"] == 3
    assert payload["issues"][0]["code"] == "MISSING_ANCHOR"
    assert payload["issues"][0]["line"] == 5


def test_check_document_rejects_non_string_text(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("# A\n", encoding="utf-8")
    with pytest.raises(TypeError, match="text must be a string"):
        check_document(doc, tmp_path, text=123)  # type: ignore[arg-type]


def test_collect_anchors_rejects_non_string_text():
    with pytest.raises(TypeError, match="text must be a string"):
        collect_anchors(None)  # type: ignore[arg-type]


def test_real_book_has_no_broken_internal_anchors():
    """Regression guard: shipped chapters must have clean intra-doc anchors."""
    report = audit_anchors(Path("."))
    assert report.documents >= 14
    assert report.valid, [
        f"{i.source}:{i.line} #{i.anchor} ({i.code})" for i in report.issues
    ]
