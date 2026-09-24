import pytest

from heading_depth_jump import (
    DepthIssue,
    check_depth,
    deepest_level,
)


def test_within_limit_passes():
    text = "# Title\n## Section\n### Subsection\n"
    assert check_depth(text, max_level=3) == []


def test_too_deep_flagged():
    text = "# Title\n## Section\n### Sub\n#### TooDeep\n"
    (issue,) = check_depth(text, max_level=3)
    assert issue.level == 4
    assert issue.title == "TooDeep"
    assert issue.line == 4


def test_default_max_level_is_three():
    text = "#### Deep\n"
    assert len(check_depth(text)) == 1


def test_multiple_deep_headings_ordered():
    text = "#### A\n## B\n##### C\n"
    lines = [i.line for i in check_depth(text, max_level=3)]
    assert lines == [1, 3]


def test_lower_max_level():
    text = "# One\n## Two\n"
    assert len(check_depth(text, max_level=1)) == 1


def test_hash_without_space_not_heading():
    text = "#### real\n####nothashtag\n"
    # Only the first line is a heading.
    assert len(check_depth(text, max_level=3)) == 1


def test_heading_inside_fence_ignored():
    text = "```\n###### deep in code\n```\n"
    assert check_depth(text, max_level=3) == []


def test_closing_hashes_stripped_from_title():
    text = "#### Deep ####\n"
    (issue,) = check_depth(text, max_level=3)
    assert issue.title == "Deep"


def test_deepest_level():
    text = "# a\n### b\n##### c\n"
    assert deepest_level(text) == 5


def test_deepest_level_no_headings():
    assert deepest_level("just prose\n") == 0


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        check_depth(None)


def test_rejects_out_of_range_max_level():
    with pytest.raises(ValueError, match="between 1 and 6"):
        check_depth("# x\n", max_level=7)


def test_rejects_bool_max_level():
    with pytest.raises(TypeError, match="max_level must be an int"):
        check_depth("# x\n", max_level=True)


def test_issue_is_immutable():
    (issue,) = check_depth("#### deep\n", max_level=3)
    assert isinstance(issue, DepthIssue)
    with pytest.raises(AttributeError):
        issue.level = 1
