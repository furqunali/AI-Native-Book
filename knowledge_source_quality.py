"""Deterministic per-source quality diagnostics for the book corpus."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_source import KnowledgeChunk


@dataclass(frozen=True)
class SourceQuality:
    source: str
    chunks: int
    characters: int
    empty: int
    duplicate_texts: int
    average_length: float

def profile_source_quality(chunks: list[KnowledgeChunk]) -> tuple[SourceQuality, ...]:
    if any(not isinstance(chunk, KnowledgeChunk) for chunk in chunks):
        raise TypeError("chunks must contain KnowledgeChunk values")
    groups: dict[str, list[KnowledgeChunk]] = {}
    for chunk in chunks:
        groups.setdefault(chunk.source, []).append(chunk)
    result: list[SourceQuality] = []
    for source, items in sorted(groups.items()):
        texts = [item.text.strip() for item in items]
        result.append(SourceQuality(source, len(items), sum(len(i.text) for i in items),
            sum(not t for t in texts), len(texts) - len(set(texts)),
            round(sum(map(len, texts)) / len(texts), 2)))
    return tuple(result)
