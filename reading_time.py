"""Reading-time estimation for book chapters.

A useful piece of chapter metadata is how long it takes an average reader to get
through it. This module counts the words in a chapter and divides by a
configurable words-per-minute rate to produce a deterministic estimate. Fenced
code blocks are, by default, counted at a slower rate because code is read more
slowly than prose, but that behaviour can be disabled.

The word count deliberately ignores markdown punctuation-only tokens (a bare
``#`` or ``-`` marker) so heading hashes and list bullets do not inflate the
estimate.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_WORD = re.compile(r"[0-9A-Za-z][0-9A-Za-z'’\-]*")


@dataclass(frozen=True)
class ReadingTime:
    """An estimate of how long a chapter takes to read.

    ``label`` identifies the chapter, ``words`` is the prose word count,
    ``code_words`` the word count inside fenced code blocks, and ``minutes`` the
    rounded-up whole-minute estimate (always at least 1 when any words exist).
    """

    label: str
    words: int
    code_words: int
    minutes: int


def count_words(text: str, *, include_code: bool = True) -> int:
    """Return the number of prose words in ``text``.

    Words are runs beginning with a letter or digit; markdown markers made only
    of punctuation are not counted. When ``include_code`` is false, words inside
    fenced code blocks are excluded from the total.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    total = 0
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
        total += len(_WORD.findall(line))

    if include_code:
        total += _count_code_words(text)
    return total


def _count_code_words(text: str) -> int:
    """Return the number of words appearing inside fenced code blocks."""
    total = 0
    fence: str | None = None
    for line in text.splitlines():
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
            continue
        if line.lstrip().startswith(fence):
            fence = None
            continue
        total += len(_WORD.findall(line))
    return total


def estimate_reading_time(
    text: str,
    *,
    label: str = "chapter",
    words_per_minute: float = 200.0,
    code_words_per_minute: float | None = None,
) -> ReadingTime:
    """Return a :class:`ReadingTime` estimate for chapter ``text``.

    Prose words are read at ``words_per_minute``. Words inside fenced code blocks
    are read at ``code_words_per_minute`` when that is given (typically slower);
    when it is ``None`` code words are read at the same ``words_per_minute`` rate.
    The reported ``minutes`` is rounded up to a whole minute and is at least 1
    whenever the chapter contains any words.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    if words_per_minute <= 0:
        raise ValueError("words_per_minute must be positive")
    if code_words_per_minute is not None and code_words_per_minute <= 0:
        raise ValueError("code_words_per_minute must be positive")

    code_words = _count_code_words(text)
    prose_words = count_words(text, include_code=False)

    prose_minutes = prose_words / words_per_minute
    if code_words_per_minute is None:
        code_minutes = code_words / words_per_minute
    else:
        code_minutes = code_words / code_words_per_minute

    raw = prose_minutes + code_minutes
    total_words = prose_words + code_words
    minutes = max(1, _ceil(raw)) if total_words else 0

    return ReadingTime(
        label=label,
        words=prose_words,
        code_words=code_words,
        minutes=minutes,
    )


def _ceil(value: float) -> int:
    """Return the smallest integer not less than ``value`` (round up)."""
    whole = int(value)
    return whole if whole == value else whole + 1
