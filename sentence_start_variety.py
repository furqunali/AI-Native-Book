"""Monotony detection: sentences that all start with the same word.

Prose that opens sentence after sentence with the same word ("The system... The
model... The result...") reads as monotonous. This module splits a chapter into
sentences, takes the first word of each, and reports any opening word used to
start at least a configurable number of sentences, so an author can vary their
phrasing.

Markdown markup and fenced code are stripped before sentence splitting so code
and formatting do not create spurious "sentences". Matching is
case-insensitive.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n")

_DEFAULT_THRESHOLD = 3


@dataclass(frozen=True)
class StartRepeat:
    """An opening word used to start several sentences.

    ``word`` is the normalised (lowercased) opening word, ``count`` how many
    sentences begin with it, and ``sentences`` the sorted tuple of 1-based
    sentence indices where it opens.
    """

    word: str
    count: int
    sentences: tuple[int, ...]


def _strip_markup(text: str) -> str:
    """Reduce markdown to plain prose, dropping fenced code and link targets."""
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            # Drop heading and list markers so they are not read as openers.
            stripped = re.sub(r"^\s{0,3}(#{1,6}|[-*+]|\d+\.)\s+", "", line)
            kept.append(stripped)
        elif line.lstrip().startswith(fence):
            fence = None
    body = "\n".join(kept)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"`([^`]*)`", r"\1", body)
    body = re.sub(r"[*_~]", "", body)
    return body


def opening_words(text: str) -> list[str]:
    """Return the lowercased opening word of every sentence in ``text``.

    Sentences are split on ``.``, ``!`` or ``?`` followed by whitespace and on
    paragraph (blank-line) breaks, after markdown has been stripped. Splitting
    on blank lines means a heading or a bullet with no terminal punctuation is
    still treated as its own unit. Chunks with no word characters contribute
    nothing. The words are returned in reading order.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    prose = _strip_markup(text)
    words: list[str] = []
    for block in _PARAGRAPH_SPLIT.split(prose):
        for chunk in _SENTENCE_SPLIT.split(block):
            match = _WORD.search(chunk)
            if match is not None:
                words.append(match.group(0).lower().replace("’", "'"))
    return words


def check_start_variety(
    text: str,
    *,
    threshold: int = _DEFAULT_THRESHOLD,
) -> list[StartRepeat]:
    """Return opening words that start at least ``threshold`` sentences.

    ``threshold`` must be at least 2 (a single use is never a repetition).
    Results are ordered by descending count with ties broken alphabetically. An
    empty list means no opening word is over-used.
    """
    if not isinstance(threshold, int) or isinstance(threshold, bool):
        raise TypeError("threshold must be an int")
    if threshold < 2:
        raise ValueError("threshold must be at least 2")

    words = opening_words(text)
    positions: dict[str, list[int]] = {}
    for index, word in enumerate(words, start=1):
        positions.setdefault(word, []).append(index)

    repeats = [
        StartRepeat(word=word, count=len(where), sentences=tuple(where))
        for word, where in positions.items()
        if len(where) >= threshold
    ]
    repeats.sort(key=lambda r: (-r.count, r.word))
    return repeats


def is_varied(text: str, *, threshold: int = _DEFAULT_THRESHOLD) -> bool:
    """Return ``True`` when no opening word reaches ``threshold`` uses."""
    return not check_start_variety(text, threshold=threshold)
