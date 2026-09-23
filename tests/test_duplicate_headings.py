import pytest

from duplicate_headings import (
    DuplicateGroup,
    find_duplicate_headings,
    has_duplicate_headings,
)


def test_no_duplicates_returns_empty():
    text = "# Intro\n\n## Setup\n\n## Usage\n"
    assert find_duplicate_headings(text) == []
    assert has_duplicate_headings(text) is False


def test_exact_duplicate_is_grouped():
    text = "## Setup\n\ntext\n\n## Setup\n"
    (group,) = find_duplicate_headings(text)
    assert group.title == "Setup"
    assert group.lines == (1, 5)
    assert group.count == 2
    assert has_duplicate_headings(text) is True


def test_comparison_is_case_and_whitespace_insensitive():
    text = "## Getting  Started\n\n### getting started\n"
    (group,) = find_duplicate_headings(text)
    assert group.normalized == "getting started"
    assert group.count == 2


def test_within_level_separates_by_level():
    text = "## Overview\n\n### Overview\n"
    assert find_duplicate_headings(text, within_level=True) == []
    # Without the flag, they collide.
    assert len(find_duplicate_headings(text)) == 1


def test_within_level_groups_same_level_duplicates():
    text = "## Overview\n\n## Overview\n"
    (group,) = find_duplicate_headings(text, within_level=True)
    assert group.levels == (2, 2)


def test_headings_in_code_fence_are_ignored():
    text = "## Setup\n\n```\n## Setup\n```\n"
    assert find_duplicate_headings(text) == []


def test_three_occurrences_recorded_in_order():
    text = "# A\n\n# A\n\n# A\n"
    (group,) = find_duplicate_headings(text)
    assert group.lines == (1, 3, 5)
    assert group.levels == (1, 1, 1)


def test_multiple_distinct_groups_in_appearance_order():
    text = "# Foo\n\n# Bar\n\n# Foo\n\n# Bar\n"
    groups = find_duplicate_headings(text)
    assert [g.normalized for g in groups] == ["foo", "bar"]


def test_find_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        find_duplicate_headings(123)


def test_group_is_immutable():
    text = "# A\n\n# A\n"
    (group,) = find_duplicate_headings(text)
    assert isinstance(group, DuplicateGroup)
    with pytest.raises(AttributeError):
        group.title = "B"
