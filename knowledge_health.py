"""Deterministic health report for the AI-Native Book knowledge corpus."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_manifest import KnowledgeManifest
from knowledge_quality import QualityReport


@dataclass(frozen=True)
class KnowledgeHealth:
    chunks: int
    sources: int
    characters: int
    empty: int
    duplicate_ids: int
    duplicate_texts: int
    valid: bool

def build_health(manifest: KnowledgeManifest, quality: QualityReport) -> KnowledgeHealth:
    return KnowledgeHealth(
        chunks=manifest.chunk_count,
        sources=manifest.source_count,
        characters=manifest.total_characters,
        empty=quality.empty,
        duplicate_ids=quality.duplicate_ids,
        duplicate_texts=quality.duplicate_texts,
        valid=quality.valid,
    )
