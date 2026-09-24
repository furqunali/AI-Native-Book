import pytest

from toc_generator import (
    TocEntry,
    generate_toc,
    render_toc,
    slugify,
)


def test_basic_toc_extraction():
    text = "# Title\n\n## Section One\n\n## Section Two\n"
    entries = generate_toc(text)
    assert [(e.level, e.text) for e in entries] == [
        (1, "Title"),
        (2, "Section One"),
        (2, "Section Two"),
    ]


def test_slug_generation():
    (entry,) = generate_toc("# Hello, World!\n")
    assert entry.slug == "hello-world"


def test_duplicate_slugs_disambiguated():
    text = "## Setup\n\n## Setup\n"
    slugs = [e.slug for e in generate_toc(text)]
    assert slugs == ["setup", "setup-1"]


def test_line_numbers_recorded():
    text = "intro\n\n# Title\n\n## Sub\n"
    entries = generate_toc(text)
    assert [e.line for e in entries] == [3, 5]


def test_level_range_filters():
    text = "# One\n\n## Two\n\n### Three\n"
    entries = generate_toc(text, min_level=2, max_level=2)
    assert [e.text for e in entries] == ["Two"]


def test_slug_uses_all_headings_for_disambiguation():
    # The filtered-out h1 'Setup' still consumes the base slug, so the h2
    # gets '-1' to match GitHub's anchors.
    text = "# Setup\n\n## Setup\n"
    entries = generate_toc(text, min_level=2, max_level=2)
    assert entries[0].slug == "setup-1"


def test_inline_markdown_stripped_from_title():
    (entry,) = generate_toc("# The `code` and **bold**\n")
    assert entry.text == "The code and bold"


def test_code_fence_headings_ignored():
    text = "# Real\n\n```\n# Fake\n```\n"
    assert [e.text for e in generate_toc(text)] == ["Real"]


def test_render_nested_list():
    text = "# Title\n\n## Section\n"
    rendered = render_toc(text)
    assert rendered == "- [Title](#title)\n  - [Section](#section)"


def test_render_empty_when_no_headings():
    assert render_toc("just prose\n") == ""


def test_slugify_helper():
    assert slugify("A B C") == "a-b-c"


def test_result_is_immutable():
    (entry,) = generate_toc("# Title\n")
    assert isinstance(entry, TocEntry)
    with pytest.raises(AttributeError):
        entry.level = 3


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        generate_toc(None)


def test_rejects_bad_level_range():
    with pytest.raises(ValueError, match="min_level must not exceed max_level"):
        generate_toc("# T\n", min_level=3, max_level=2)


def test_rejects_out_of_bounds_level():
    with pytest.raises(ValueError, match="between 1 and 6"):
        generate_toc("# T\n", max_level=9)
