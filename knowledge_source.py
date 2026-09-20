from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    source: str
    title: str
    text: str
    index: int


def _clean(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"!?\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip()


def chunk_markdown(path: Path, max_chars: int = 1600) -> list[KnowledgeChunk]:
    text = path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[KnowledgeChunk] = []
    buffer = ""
    index = 0
    title = path.stem

    for paragraph in paragraphs:
        heading = re.match(r"^#\s+(.+)$", paragraph)
        if heading:
            title = _clean(heading.group(1))
        clean = _clean(paragraph)
        if not clean:
            continue
        candidate = f"{buffer}\n\n{clean}".strip()
        if buffer and len(candidate) > max_chars:
            digest = hashlib.sha256(f"{path.name}:{index}:{buffer}".encode()).hexdigest()[:16]
            chunks.append(KnowledgeChunk(digest, path.as_posix(), title, buffer, index))
            index += 1
            buffer = clean
        else:
            buffer = candidate

    if buffer:
        digest = hashlib.sha256(f"{path.as_posix()}:{index}:{buffer}".encode()).hexdigest()[:16]
        chunks.append(KnowledgeChunk(digest, path.as_posix(), title, buffer, index))
    return chunks


def build_knowledge_source(root: Path) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for path in sorted(root.glob("Chapter*.md")):
        chunks.extend(chunk_markdown(path))
    return chunks


def write_jsonl(chunks: list[KnowledgeChunk], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "".join(json.dumps(asdict(chunk), ensure_ascii=False) + "\n" for chunk in chunks),
        encoding="utf-8",
    )
