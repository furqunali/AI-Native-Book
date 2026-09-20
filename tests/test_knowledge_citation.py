from knowledge_citation import extract_citations, validate_citations
def test_extract_citations_is_unique_and_ordered():
    assert extract_citations("A [z] B [a] C [z]") == ("z", "a")
def test_validate_citations_reports_unknown_ids():
    assert validate_citations("A [known] [missing]", {"known"}) == ("missing",)
def test_empty_citations_are_ignored():
    assert extract_citations("A []") == ()


def test_extract_citations_ignores_markdown_links_and_images():
    text = "See [documentation](https://example.com) and ![diagram](image.png), then cite [source-1]."
    assert extract_citations(text) == ("source-1",)
