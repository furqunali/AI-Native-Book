import pytest

from chapter_outline import (
    Heading,
    extract_outline,
    render_toc,
    slugify,
)


def test_extracts_atx_headings_in_order():
    text = "# Intro\n\nsome prose\n\n## Details\n\n### Deeper\n"
    outline = extract_outline(text)
    assert [(h.level, h.title) for h in outline] == [
        (1, "Intro"),
        (2, "Details"),
        (3, "Deeper"),
    ]


def test_line_numbers_are_one_based():
    text = "intro line\n\n## Heading\n"
    (heading,) = extract_outline(text)
    assert heading.line == 3


def test_headings_inside_fenced_code_are_ignored():
    text = "# Real\n\n```bash\n# not a heading\n## also not\n```\n\n## Also Real\n"
    outline = extract_outline(text)
    assert [h.title for h in outline] == ["Real", "Also Real"]


def test_tilde_fences_are_handled():
    text = "# Real\n\n~~~\n# hidden\n~~~\n"
    assert [h.title for h in extract_outline(text)] == ["Real"]


def test_atx_closing_hashes_are_stripped():
    (heading,) = extract_outline("## Heading ##\n")
    assert heading.title == "Heading"
    assert heading.slug == "heading"


def test_inline_markdown_in_title_is_reduced_to_text():
    (heading,) = extract_outline("# The **Bold** `code` and [link](http://x.com)\n")
    assert heading.title == "The Bold code and link"


def test_slug_matches_github_style():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("Spaces   and--dashes") == "spaces-and--dashes"
    assert slugify("Trailing punctuation?") == "trailing-punctuation"


def test_duplicate_slugs_are_disambiguated():
    text = "# Setup\n\n## Setup\n\n### Setup\n"
    slugs = [h.slug for h in extract_outline(text)]
    assert slugs == ["setup", "setup-1", "setup-2"]


def test_setext_headings_are_recognised():
    text = "Title Here\n=========\n\nSubsection\n----------\n"
    outline = extract_outline(text)
    assert [(h.level, h.title) for h in outline] == [
        (1, "Title Here"),
        (2, "Subsection"),
    ]


def test_setext_line_number_points_at_text_line():
    text = "Title Here\n=========\n"
    (heading,) = extract_outline(text)
    assert heading.line == 1


def test_thematic_break_is_not_a_setext_heading():
    # A blank line before "---" means there is no heading text above it.
    text = "some paragraph\n\n---\n\nmore text\n"
    assert extract_outline(text) == []


def test_list_item_above_dashes_is_not_a_setext_heading():
    text = "- a list item\n---\n"
    assert extract_outline(text) == []


def test_atx_requires_space_after_hashes():
    # "#Heading" without a space is not an ATX heading.
    assert extract_outline("#NoSpace\n") == []


def test_more_than_six_hashes_is_not_a_heading():
    assert extract_outline("####### too deep\n") == []


def test_empty_atx_heading_is_skipped():
    assert extract_outline("##\n\n## Real\n") == [
        Heading(level=2, title="Real", slug="real", line=3)
    ]


def test_render_toc_nests_by_relative_level():
    text = "# Top\n\n## Middle\n\n### Leaf\n\n## Second\n"
    toc = render_toc(text)
    assert toc == (
        "- [Top](#top)\n"
        "  - [Middle](#middle)\n"
        "    - [Leaf](#leaf)\n"
        "  - [Second](#second)"
    )


def test_render_toc_rebases_indentation_when_starting_deep():
    text = "## Alpha\n\n### Beta\n"
    toc = render_toc(text)
    assert toc == "- [Alpha](#alpha)\n  - [Beta](#beta)"


def test_render_toc_level_filtering():
    text = "# Top\n\n## Middle\n\n### Leaf\n"
    toc = render_toc(text, min_level=2, max_level=2)
    assert toc == "- [Middle](#middle)"


def test_render_toc_empty_when_no_headings_in_range():
    assert render_toc("# Only H1\n", min_level=2, max_level=3) == ""


def test_render_toc_links_use_disambiguated_slugs():
    text = "# Setup\n\n## Setup\n"
    toc = render_toc(text)
    assert "(#setup)" in toc
    assert "(#setup-1)" in toc


def test_extract_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        extract_outline(None)


def test_render_toc_rejects_bad_level_bounds():
    with pytest.raises(ValueError, match="must not exceed"):
        render_toc("# H\n", min_level=3, max_level=2)
    with pytest.raises(ValueError, match="between 1 and 6"):
        render_toc("# H\n", min_level=0)
    with pytest.raises(TypeError, match="must be an int"):
        render_toc("# H\n", max_level=True)


def test_heading_is_immutable():
    (heading,) = extract_outline("# H\n")
    with pytest.raises(AttributeError):
        heading.level = 2
