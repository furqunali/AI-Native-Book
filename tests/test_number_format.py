import pytest

from number_format import (
    NumberFormatReport,
    NumberRef,
    check_number_format,
    find_numbers,
)


def test_consistent_grouped_passes():
    text = "We saw 1,000 and 2,500 and 12,345 items.\n"
    report = check_number_format(text)
    assert report.dominant == "grouped"
    assert report.grouped == 3
    assert report.plain == 0
    assert report.is_consistent is True


def test_consistent_plain_passes():
    text = "We saw 1000 and 2500 items.\n"
    report = check_number_format(text)
    assert report.dominant == "plain"
    assert report.is_consistent is True


def test_mixed_flags_minority():
    text = "First 1,000 then 2,000 then 3000.\n"
    report = check_number_format(text)
    assert report.dominant == "grouped"
    assert len(report.deviations) == 1
    assert report.deviations[0].text == "3000"
    assert report.deviations[0].style == "plain"


def test_small_numbers_ignored():
    text = "There were 42 and 999 of them.\n"
    assert find_numbers(text) == []


def test_min_value_threshold():
    text = "Values 1500 and 20000.\n"
    # Raise threshold so only the larger qualifies.
    refs = find_numbers(text, min_value=10000)
    assert [r.text for r in refs] == ["20000"]


def test_grouped_value_parsed():
    (ref,) = find_numbers("Total 1,234,567 dollars.\n")
    assert ref.value == 1234567
    assert ref.style == "grouped"


def test_decimal_not_matched():
    text = "The ratio was 3.14159 exactly.\n"
    assert find_numbers(text) == []


def test_code_span_ignored():
    text = "Set `timeout=5000` in config; the limit is 1,000.\n"
    refs = find_numbers(text)
    assert [r.text for r in refs] == ["1,000"]


def test_fenced_code_ignored():
    text = "Budget is 1,000.\n```\nx = 9999999\n```\n"
    refs = find_numbers(text)
    assert [r.text for r in refs] == ["1,000"]


def test_no_large_numbers_is_none():
    report = check_number_format("no big numbers here, only 12 and 7\n")
    assert report.dominant == "none"
    assert report.is_consistent is True


def test_order_within_line():
    (a, b) = find_numbers("Compare 5000 with 1,000 here.\n")
    assert a.text == "5000"
    assert b.text == "1,000"


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        find_numbers(None)


def test_rejects_bad_min_value():
    with pytest.raises(ValueError, match="min_value must be positive"):
        find_numbers("1000", min_value=0)


def test_report_and_ref_immutable():
    report = check_number_format("1,000 and 2000\n")
    assert isinstance(report, NumberFormatReport)
    (ref,) = report.deviations
    assert isinstance(ref, NumberRef)
    with pytest.raises(AttributeError):
        ref.value = 0
