import pytest

from emphasis_style import (
    Deviation,
    EmphasisStyleReport,
    analyze_emphasis_style,
)


def test_no_emphasis_is_consistent():
    report = analyze_emphasis_style("plain text with no markers\n")
    assert report.dominant == "none"
    assert report.is_consistent is True
    assert report.deviations == ()


def test_all_asterisk_is_consistent():
    report = analyze_emphasis_style("*one* and **two** and *three*\n")
    assert report.dominant == "asterisk"
    assert report.asterisk == 3
    assert report.underscore == 0
    assert report.is_consistent is True


def test_all_underscore_is_consistent():
    report = analyze_emphasis_style("_one_ and __two__\n")
    assert report.dominant == "underscore"
    assert report.underscore == 2
    assert report.is_consistent is True


def test_mixed_reports_minority_as_deviation():
    report = analyze_emphasis_style("*a* *b* *c* and _d_\n")
    assert report.dominant == "asterisk"
    assert len(report.deviations) == 1
    assert report.deviations[0].marker == "_"
    assert report.deviations[0].snippet == "_d_"


def test_underscore_dominant_flags_asterisk():
    report = analyze_emphasis_style("_a_ _b_ _c_ and *d*\n")
    assert report.dominant == "underscore"
    assert report.deviations[0].marker == "*"


def test_tie_prefers_asterisk_dominant():
    report = analyze_emphasis_style("*a* _b_\n")
    assert report.dominant == "asterisk"
    assert [d.marker for d in report.deviations] == ["_"]


def test_snake_case_not_counted():
    report = analyze_emphasis_style("the variable file_name and long_identifier\n")
    assert report.underscore == 0
    assert report.dominant == "none"


def test_strong_underscore_counted():
    report = analyze_emphasis_style("__bold__ text\n")
    assert report.underscore == 1


def test_code_span_emphasis_ignored():
    report = analyze_emphasis_style("use `a_b_c` and `x*y*z` here\n")
    assert report.dominant == "none"


def test_fenced_code_ignored():
    text = "*real*\n```\n_not_ *counted*\n```\n"
    report = analyze_emphasis_style(text)
    assert report.asterisk == 1
    assert report.underscore == 0


def test_deviation_line_numbers():
    text = "*a*\n*b*\n_c_\n"
    report = analyze_emphasis_style(text)
    assert report.deviations[0].line == 3


def test_rejects_non_string():
    with pytest.raises(TypeError, match="text must be a string"):
        analyze_emphasis_style(None)


def test_report_is_immutable():
    report = analyze_emphasis_style("*a*\n")
    assert isinstance(report, EmphasisStyleReport)
    with pytest.raises(AttributeError):
        report.asterisk = 0


def test_deviation_is_immutable():
    report = analyze_emphasis_style("*a* *b* _c_\n")
    (dev,) = report.deviations
    assert isinstance(dev, Deviation)
    with pytest.raises(AttributeError):
        dev.line = 1
