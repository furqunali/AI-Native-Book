"""Deterministic distribution metrics for the knowledge corpus."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_source import KnowledgeChunk


@dataclass(frozen=True)
class SourceDistribution:
    sources: int
    chunks: int
    largest_source_chunks: int
    smallest_source_chunks: int
    concentration: float


def summarize_source_distribution(chunks: list[KnowledgeChunk]) -> SourceDistribution:
    """Measure how evenly chunks are distributed across sources.

    Concentration is the largest source's share of all chunks. Empty corpora
    return zeroed metrics so callers can safely include the result in health
    reports.
    """
    if any(not isinstance(chunk, KnowledgeChunk) for chunk in chunks):
        raise TypeError("chunks must contain KnowledgeChunk values")
    counts: dict[str, int] = {}
    for chunk in chunks:
        counts[chunk.source] = counts.get(chunk.source, 0) + 1
    values = list(counts.values())
    if not values:
        return SourceDistribution(0, 0, 0, 0, 0.0)
    largest = max(values)
    return SourceDistribution(
        sources=len(values),
        chunks=len(chunks),
        largest_source_chunks=largest,
        smallest_source_chunks=min(values),
        concentration=round(largest / len(chunks), 4),
    )
