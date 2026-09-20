from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from knowledge_source import KnowledgeChunk, build_knowledge_source


@dataclass(frozen=True)
class SourceSummary:
    source: str
    chunks: int
    characters: int


@dataclass(frozen=True)
class KnowledgeManifest:
    chunk_count: int
    source_count: int
    total_characters: int
    sources: tuple[SourceSummary, ...]
    digest: str

    def to_dict(self) -> dict:
        return asdict(self)


def summarize_chunks(chunks: list[KnowledgeChunk]) -> tuple[SourceSummary, ...]:
    totals: dict[str, list[int]] = {}
    for chunk in chunks:
        bucket = totals.setdefault(chunk.source, [0, 0])
        bucket[0] += 1
        bucket[1] += len(chunk.text)
    return tuple(
        SourceSummary(source=source, chunks=values[0], characters=values[1])
        for source, values in sorted(totals.items())
    )


def manifest_digest(chunks: list[KnowledgeChunk]) -> str:
    payload = [
        {
            "id": chunk.id,
            "source": chunk.source,
            "title": chunk.title,
            "text": chunk.text,
            "index": chunk.index,
        }
        for chunk in chunks
    ]
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_manifest(chunks: list[KnowledgeChunk]) -> KnowledgeManifest:
    sources = summarize_chunks(chunks)
    return KnowledgeManifest(
        chunk_count=len(chunks),
        source_count=len(sources),
        total_characters=sum(len(chunk.text) for chunk in chunks),
        sources=sources,
        digest=manifest_digest(chunks),
    )


def build_book_manifest(root: Path) -> KnowledgeManifest:
    return build_manifest(build_knowledge_source(root))


def write_manifest(manifest: KnowledgeManifest, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
