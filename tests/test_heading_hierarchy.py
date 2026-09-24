import pytest

from heading_hierarchy import (
    HierarchyIssue,
    check_hierarchy,
    is_well_formed,
)


def test_well_formed_document_has_no_issues():
    text = "# Title\n\n## Section\n\n### Detail\n\n## Another\n"
    assert check_hierarchy(text) == []
    assert is_well_formed(text) is True


def test_skipped_level_is_reported():
    text = "# Title\n\n## Section\n\n#### Too Deep\n"
    (issue,) = check_hierarchy(text)
    assert issue.kind == "skipped-level"
    assert issue.level == 4
    assert issue.line == 5
    assert is_well_formed(text) is False


def test_first_heading_not_top_level_is_reported():
    text = "## Starts Deep\n\n### Child\n"
    issues = check_hierarchy(text)
    # Top level is 2 here, so no skip; but the opening heading equals top level,
    # meaning first-not-top should NOT fire when the document simply starts at 2.
    assert all(i.kind != "first-not-top" for i in issues)


def test_first_not_top_fires_when_opening_below_top_level():
    # Opens at level 3, but a level-2 heading appears later, so top level is 2
    # and the first heading (level 3) is below it.
    text = "### Deep Intro\n\n## Real Section\n"
    kinds = {i.kind for i in check_hierarchy(text)}
    assert "first-not-top" in kinds


def test_multiple_h1_reported_by_default():
    text = "# First Title\n\n# Second Title\n"
    issues = check_hierarchy(text)
    assert [i.kind for i in issues] == ["multiple-h1"]
    assert issues[0].line == 3


def test_multiple_h1_can_be_disabled():
    text = "# First Title\n\n# Second Title\n"
    assert check_hierarchy(text, require_single_h1=False) == []


def test_headings_in_code_fence_are_ignored():
    text = "# Title\n\n```\n#### fake deep heading\n```\n\n## Real\n"
    assert check_hierarchy(text) == []


def test_no_headings_is_well_formed():
    assert check_hierarchy("just prose, no headings\n") == []
    assert is_well_formed("") is True


def test_issues_are_sorted_by_line():
    text = "# T\n\n#### Deep\n\n# Second\n\n##### Deeper\n"
    lines = [i.line for i in check_hierarchy(text)]
    assert lines == sorted(lines)


def test_going_shallower_is_always_allowed():
    text = "# T\n\n## A\n\n### B\n\n## C\n"
    assert check_hierarchy(text) == []


def test_check_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_hierarchy(None)


def test_issue_is_immutable():
    text = "# Title\n\n#### Deep\n"
    (issue,) = check_hierarchy(text)
    assert isinstance(issue, HierarchyIssue)
    with pytest.raises(AttributeError):
        issue.line = 1
