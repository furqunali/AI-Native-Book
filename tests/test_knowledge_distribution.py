import pytest

from knowledge_distribution import summarize_source_distribution
from knowledge_source import KnowledgeChunk


def test_distribution_reports_source_concentration():
    chunks = [
        KnowledgeChunk("a", "one.md", "One", "x", 0),
        KnowledgeChunk("b", "one.md", "One", "y", 1),
        KnowledgeChunk("c", "two.md", "Two", "z", 0),
    ]
    result = summarize_source_distribution(chunks)
    assert result.concentration == 0.6667
    assert result.largest_source_chunks == 2

def test_distribution_handles_empty_corpus():
    assert summarize_source_distribution([]).sources == 0

def test_distribution_rejects_wrong_values():
    with pytest.raises(TypeError, match="KnowledgeChunk"):
        summarize_source_distribution(["bad"])
