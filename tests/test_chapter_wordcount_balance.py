import pytest

from chapter_wordcount_balance import (
    BalanceIssue,
    check_balance,
    is_balanced,
)


def test_balanced_book_passes():
    counts = {"c1": 1000, "c2": 1100, "c3": 900}
    assert check_balance(counts) == []
    assert is_balanced(counts) is True


def test_short_chapter_flagged():
    counts = {"c1": 1000, "c2": 1000, "c3": 100}
    (issue,) = check_balance(counts, tolerance=0.5)
    assert issue.chapter == "c3"
    assert issue.direction == "short"
    assert issue.count == 100


def test_long_chapter_flagged():
    counts = {"c1": 1000, "c2": 1000, "c3": 5000}
    (issue,) = check_balance(counts, tolerance=0.5)
    assert issue.chapter == "c3"
    assert issue.direction == "long"


def test_deviation_value():
    counts = {"a": 100, "b": 100, "c": 200}
    (issue,) = check_balance(counts, tolerance=0.5)
    # median is 100, c deviates by (200-100)/100 = 1.0
    assert issue.median == 100.0
    assert issue.deviation == 1.0


def test_tolerance_boundary_exclusive():
    counts = {"a": 100, "b": 100, "c": 150}
    # exactly +0.5 deviation is NOT beyond a tolerance of 0.5
    assert check_balance(counts, tolerance=0.5) == []
    # but a smaller tolerance flags it
    assert len(check_balance(counts, tolerance=0.4)) == 1


def test_results_sorted_by_abs_deviation():
    counts = {"a": 1000, "b": 1000, "short": 100, "long": 3000}
    issues = check_balance(counts, tolerance=0.5)
    # long deviates +2.0, short deviates -0.9 -> long first
    assert [i.chapter for i in issues] == ["long", "short"]


def test_empty_mapping():
    assert check_balance({}) == []


def test_all_zero_counts():
    assert check_balance({"a": 0, "b": 0}) == []


def test_rejects_non_dict():
    with pytest.raises(TypeError, match="counts must be a dict"):
        check_balance([("a", 1)])


def test_rejects_non_int_count():
    with pytest.raises(TypeError, match="word counts must be ints"):
        check_balance({"a": 1.5})


def test_rejects_negative_count():
    with pytest.raises(ValueError, match="non-negative"):
        check_balance({"a": -1})


def test_rejects_non_positive_tolerance():
    with pytest.raises(ValueError, match="tolerance must be positive"):
        check_balance({"a": 100}, tolerance=0)


def test_rejects_bool_tolerance():
    with pytest.raises(TypeError, match="tolerance must be a number"):
        check_balance({"a": 100}, tolerance=True)


def test_issue_is_immutable():
    (issue,) = check_balance({"a": 100, "b": 100, "c": 1000}, tolerance=0.5)
    assert isinstance(issue, BalanceIssue)
    with pytest.raises(AttributeError):
        issue.count = 0
