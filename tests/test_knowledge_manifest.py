from pathlib import Path

from knowledge_manifest import (
    build_book_manifest,
    build_manifest,
    manifest_digest,
    summarize_chunks,
    write_manifest,
)
from knowledge_source import KnowledgeChunk


def chunk(identifier: str, source: str, text: str, index: int) -> KnowledgeChunk:
    return KnowledgeChunk(identifier, source, "Title", text, index)


def test_source_summary_is_deterministic():
    chunks = [
        chunk("b", "Chapter2.md", "hello", 1),
        chunk("a", "Chapter1.md", "abc", 0),
        chunk("c", "Chapter2.md", "world!", 2),
    ]
    summary = summarize_chunks(chunks)
    assert summary[0].source == "Chapter1.md"
    assert summary[0].chunks == 1
    assert summary[0].characters == 3
    assert summary[1].chunks == 2
    assert summary[1].characters == 11


def test_manifest_digest_changes_when_evidence_changes():
    first = [chunk("a", "Chapter1.md", "alpha", 0)]
    second = [chunk("a", "Chapter1.md", "beta", 0)]
    assert manifest_digest(first) != manifest_digest(second)


def test_build_manifest_reports_totals():
    chunks = [
        chunk("a", "Chapter1.md", "alpha", 0),
        chunk("b", "Chapter1.md", "beta", 1),
    ]
    manifest = build_manifest(chunks)
    assert manifest.chunk_count == 2
    assert manifest.source_count == 1
    assert manifest.total_characters == 9
    assert manifest.digest == manifest_digest(chunks)


def test_write_manifest_round_trips_json(tmp_path):
    chunks = [chunk("a", "Chapter1.md", "alpha", 0)]
    destination = tmp_path / "manifest.json"
    manifest = build_manifest(chunks)
    write_manifest(manifest, destination)
    assert destination.exists()
    assert '"chunk_count": 1' in destination.read_text(encoding="utf-8")


def test_book_manifest_contains_all_chapters():
    manifest = build_book_manifest(Path("."))
    assert manifest.chunk_count > 0
    assert manifest.source_count >= 13
    assert all(source.source.startswith("Chapter") for source in manifest.sources)


def test_empty_manifest_is_valid():
    manifest = build_manifest([])
    assert manifest.chunk_count == 0
    assert manifest.source_count == 0
    assert manifest.total_characters == 0
    assert manifest.sources == ()
