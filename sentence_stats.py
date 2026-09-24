"""Sentence-level statistics for chapter prose.

Long, uniform sentences make technical writing hard to follow. This module
splits chapter prose into sentences and reports how many there are and their
average length in words, which is a simple, deterministic proxy for readability.

Sentence splitting is heuristic: text is broken on ``.``, ``!`` and ``?`` that
are followed by whitespace or the end of the text, while a curated set of common
abbreviations (``e.g.``, ``i.e.``, ``etc.`` and honorifics) is protected so they
do not end a sentence prematurely. Fenced code blocks and ATX headings are
skipped so only running prose is measured.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
_WORD = re.compile(r"[0-9A-Za-z][0-9A-Za-z'’\-]*")
_TERMINATOR = re.compile(r"[.!?]+")

_ABBREVIATIONS = frozenset(
    {"e.g.", "i.e.", "etc.", "vs.", "mr.", "mrs.", "ms.", "dr.", "st.", "cf.", "al."}
)


@dataclass(frozen=True)
class SentenceStats:
    """Aggregate sentence statistics for a chapter.

    ``label`` identifies the chapter, ``sentences`` is the number of sentences
    detected, ``words`` the total prose word count, and ``average_length`` the
    mean words per sentence (0.0 when there are no sentences).
    """

    label: str
    sentences: int
    words: int
    average_length: float


def _prose_text(text: str) -> str:
    """Return chapter ``text`` with fenced code blocks and headings removed."""
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue
        if _ATX.match(line):
            continue
        kept.append(line)
    return "\n".join(kept)


def split_sentences(text: str) -> list[str]:
    """Split chapter prose into a list of trimmed sentences.

    Sentences end at ``.``, ``!`` or ``?`` followed by whitespace or end-of-text.
    A short list of common abbreviations is protected so ``e.g.`` does not split
    a sentence. Fenced code blocks and headings are ignored, and empty fragments
    are dropped.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    prose = _prose_text(text)
    # Collapse all whitespace (including newlines) to single spaces.
    flat = re.sub(r"\s+", " ", prose).strip()
    if not flat:
        return []

    sentences: list[str] = []
    start = 0
    for match in _TERMINATOR.finditer(flat):
        end = match.end()
        # A real boundary is at end-of-text or followed by whitespace.
        if end < len(flat) and not flat[end].isspace():
            continue
        candidate = flat[start:end].strip()
        last_token = candidate.split()[-1].lower() if candidate.split() else ""
        if last_token in _ABBREVIATIONS:
            continue
        if candidate:
            sentences.append(candidate)
        start = end

    tail = flat[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def sentence_stats(text: str, *, label: str = "chapter") -> SentenceStats:
    """Return :class:`SentenceStats` for chapter ``text``.

    The result reports the sentence count, the total word count across those
    sentences and the average sentence length in words. An empty or
    prose-free chapter yields zero counts and a 0.0 average.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(label, str):
        raise TypeError("label must be a string")

    sentences = split_sentences(text)
    words = sum(len(_WORD.findall(s)) for s in sentences)
    average = words / len(sentences) if sentences else 0.0
    return SentenceStats(
        label=label,
        sentences=len(sentences),
        words=words,
        average_length=average,
    )
