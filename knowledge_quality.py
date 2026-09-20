"""Quality checks for the AI-Native Book knowledge corpus."""
from __future__ import annotations
from dataclasses import dataclass
from knowledge_source import KnowledgeChunk

@dataclass(frozen=True)
class QualityReport:
    chunks: int
    empty: int
    duplicate_ids: int
    duplicate_texts: int
    valid: bool

def inspect_chunks(chunks: list[KnowledgeChunk]) -> QualityReport:
    ids=[chunk.id for chunk in chunks]
    texts=[chunk.text.strip() for chunk in chunks]
    duplicate_ids=len(ids)-len(set(ids))
    duplicate_texts=len(texts)-len(set(texts))
    empty=sum(not text for text in texts)
    return QualityReport(len(chunks),empty,duplicate_ids,duplicate_texts,
                         empty == 0 and duplicate_ids == 0 and duplicate_texts == 0)
