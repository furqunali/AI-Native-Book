import pytest

from reference_year import (
    YearRef,
    all_in_range,
    check_years,
    extract_years,
)


def test_extracts_years():
    refs = extract_years("Founded in 1998, updated in 2024.\n")
    assert [r.year for r in refs] == [1998, 2024]


def test_line_numbers():
    refs = extract_years("intro\n\nthe year 2020 mattered\n")
    assert refs[0].line == 3


def test_non_year_numbers_ignored():
    # 1234 and 2500 are four digits but not 19xx/20xx.
    assert extract_years("values 1234 and 2500 and 3000\n") == []


def test_year_in_longer_number_not_matched():
    assert extract_years("id 12019 and 20240101\n") == []


def test_default_range_marks_in_range():
    (ref,) = extract_years("year 2024\n")
    assert ref.in_range is True


def test_check_years_flags_out_of_range():
    text = "modern 2024 but stale 1998 here\n"
    flagged = check_years(text, min_year=2000, max_year=2099)
    assert [r.year for r in flagged] == [1998]
    assert flagged[0].in_range is False


def test_custom_range():
    text = "1995 2005 2015\n"
    flagged = check_years(text, min_year=2000, max_year=2010)
    assert [r.year for r in flagged] == [1995, 2015]


def test_all_in_range_true():
    assert all_in_range("2020 and 2021\n") is True


def test_all_in_range_false():
    assert all_in_range("1998 was long ago\n", min_year=2000) is False


def test_code_span_ignored():
    text = "the year 2024; the port `8080` and `year=1000`\n"
    refs = extract_years(text)
    assert [r.year for r in refs] == [2024]


def test_fenced_code_ignored():
    text = "2024 in prose\n```\n1999 2000 2001\n```\n"
    assert [r.year for r in extract_years(text)] == [2024]


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        extract_years(None)


def test_rejects_inverted_range():
    with pytest.raises(ValueError, match="must not exceed"):
        check_years("2024", min_year=2100, max_year=2000)


def test_rejects_bool_year():
    with pytest.raises(TypeError, match="min_year must be an int"):
        check_years("2024", min_year=True)


def test_ref_is_immutable():
    (ref,) = extract_years("2024\n")
    assert isinstance(ref, YearRef)
    with pytest.raises(AttributeError):
        ref.year = 0
