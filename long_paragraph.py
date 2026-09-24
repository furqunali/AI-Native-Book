"""Long-paragraph detection for chapter prose.

Walls of text tire readers and usually signal an idea that should be split.
This module groups a chapter into prose paragraphs -- runs of non-blank lines
separated by blank lines -- and flags any whose word count exceeds a
configurable threshold, reporting the paragraph's starting line so an editor can
find it quickly.

Fenced code blocks are skipped entirely, and non-prose blocks (headings, list
items, blockquotes and table rows) are not treated as paragraphs, so only real
running prose is measured.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_WORD = re.compile(r"[0-9A-Za-z][0-9A-Za-z'’\-]*")
_NON_PROSE_PREFIX = ("#", "-", "*", "+", ">", "|")
_ORDERED = re.compile(r"^\s*\d+[.)]\s")


@dataclass(frozen=True)
class LongParagraph:
    """A paragraph that exceeds the word threshold.

    ``start_line`` is the 1-based line where the paragraph begins, ``words`` its
    word count, and ``preview`` the first few words of the paragraph for
    identification.
    """

    start_line: int
    words: int
    preview: str


def _is_prose_start(line: str) -> bool:
    """Return ``True`` when ``line`` begins an ordinary prose paragraph."""
    stripped = line.strip()
    if not stripped:
        return False
    if stripped[0] in _NON_PROSE_PREFIX:
        return False
    if _ORDERED.match(line):
        return False
    return True


def find_long_paragraphs(text: str, *, max_words: int = 150) -> list[LongParagraph]:
    """Return prose paragraphs in ``text`` whose length exceeds ``max_words``.

    Paragraphs are maximal runs of non-blank lines. A run is treated as prose
    only when its first line is not a heading, list item, blockquote or table
    row. Lines inside fenced code blocks are ignored. A paragraph is flagged when
    its word count is strictly greater than ``max_words``. Results are ordered by
    starting line.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(max_words, int) or isinstance(max_words, bool):
        raise TypeError("max_words must be an int")
    if max_words < 1:
        raise ValueError("max_words must be at least 1")

    results: list[LongParagraph] = []
    lines = text.splitlines()
    fence: str | None = None
    buffer: list[str] = []
    start = 0

    def flush() -> None:
        if not buffer:
            return
        block = " ".join(buffer)
        if _is_prose_start(buffer[0]):
            words = _WORD.findall(block)
            if len(words) > max_words:
                preview = " ".join(words[:8])
                results.append(
                    LongParagraph(
                        start_line=start, words=len(words), preview=preview
                    )
                )

    for i, line in enumerate(lines):
        match = _FENCE.match(line)
        if fence is None and match:
            flush()
            buffer = []
            fence = match.group(1)
            continue
        if fence is not None:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        if line.strip() == "":
            flush()
            buffer = []
        else:
            if not buffer:
                start = i + 1
            buffer.append(line)

    flush()
    return results


def has_long_paragraphs(text: str, *, max_words: int = 150) -> bool:
    """Return ``True`` when any prose paragraph exceeds ``max_words`` words."""
    return bool(find_long_paragraphs(text, max_words=max_words))
