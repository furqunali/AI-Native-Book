from citation_report import build_citation_report

def test_report_calculates_valid_coverage():
    report=build_citation_report("[a] [b] [a]", {"a"})
    assert report.citations == ("a","b")
    assert report.unknown == ("b",)
    assert report.coverage == 0.5

def test_report_is_empty_when_no_citations_exist():
    assert build_citation_report("plain answer", {"a"}).coverage == 0.0
