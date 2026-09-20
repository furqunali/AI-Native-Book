from pathlib import Path

from knowledge_source import build_knowledge_source, chunk_markdown, write_jsonl


def test_chunk_ids_are_stable_and_citable(tmp_path):
    source = tmp_path / "Chapter1.md"
    source.write_text("# Intro\n\nAI-native systems are adaptive.\n\nMore detail.", encoding="utf-8")
    first = chunk_markdown(source, max_chars=80)
    second = chunk_markdown(source, max_chars=80)
    assert [c.id for c in first] == [c.id for c in second]
    assert first[0].source == "Chapter1.md"
    assert first[0].index == 0


def test_book_knowledge_source_is_sorted():
    chunks = build_knowledge_source(Path("."))
    assert chunks
    assert chunks[0].source.startswith("Chapter")


def test_jsonl_export(tmp_path):
    source = tmp_path / "Chapter1.md"
    source.write_text("# Intro\n\nGrounded answers need evidence.", encoding="utf-8")
    chunks = chunk_markdown(source)
    output = tmp_path / "knowledge.jsonl"
    write_jsonl(chunks, output)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(chunks)
