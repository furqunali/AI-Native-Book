"""Reading-time and readability estimation for book chapters.

The metrics operate on the prose a reader actually reads: fenced code blocks,
markdown syntax and link targets are stripped before counting so that a
code-heavy chapter is not credited with inflated word or sentence counts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
_SENTENCE_END = re.compile(r"[.!?]+(?=\s|$)")
_VOWEL_GROUP = re.compile(r"[aeiouy]+")

_DEFAULT_WPM = 200


@dataclass(frozen=True)
class ReadabilityReport:
    """Deterministic readability metrics for a single chapter."""

    words: int
    sentences: int
    syllables: int
    reading_minutes: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float


def _strip_markup(text: str) -> str:
    """Reduce markdown to plain prose for counting.

    Fenced code blocks are removed entirely, link/image targets are dropped
    while their visible text is kept, and inline emphasis and heading markers
    are discarded.
    """
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            kept.append(line)
        elif line.lstrip().startswith(fence):
            fence = None
    body = "\n".join(kept)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"`([^`]*)`", r"\1", body)
    body = re.sub(r"^\s{0,3}#{1,6}\s+", "", body, flags=re.MULTILINE)
    body = re.sub(r"[*_~]", "", body)
    return body


def count_syllables(word: str) -> int:
    """Estimate the syllable count of a single word.

    Uses the common vowel-group heuristic: count runs of vowels, drop a
    trailing silent ``e``, and never return fewer than one syllable for a
    word that contains letters.
    """
    lowered = re.sub(r"[^a-z]", "", word.lower())
    if not lowered:
        return 0
    groups = _VOWEL_GROUP.findall(lowered)
    count = len(groups)
    if lowered.endswith("e") and not lowered.endswith(("le", "ee")) and count > 1:
        count -= 1
    return max(count, 1)


def estimate_readability(text: str, words_per_minute: int = _DEFAULT_WPM) -> ReadabilityReport:
    """Estimate reading time and readability for chapter ``text``.

    ``words_per_minute`` sets the reading pace used for the time estimate.
    Empty or whitespace-only chapters return a zeroed report so callers can
    fold the result into aggregate health reports without special casing.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(words_per_minute, int) or isinstance(words_per_minute, bool):
        raise TypeError("words_per_minute must be an int")
    if words_per_minute <= 0:
        raise ValueError("words_per_minute must be positive")

    prose = _strip_markup(text)
    words = _WORD.findall(prose)
    word_count = len(words)
    if word_count == 0:
        return ReadabilityReport(0, 0, 0, 0.0, 0.0, 0.0)

    # A chapter with words but no terminal punctuation still reads as one sentence.
    sentence_count = max(len(_SENTENCE_END.findall(prose)), 1)
    syllable_count = sum(count_syllables(word) for word in words)

    reading_minutes = round(word_count / words_per_minute, 2)
    words_per_sentence = word_count / sentence_count
    syllables_per_word = syllable_count / word_count
    reading_ease = round(
        206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word, 2
    )
    grade = round(
        0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59, 2
    )
    return ReadabilityReport(
        words=word_count,
        sentences=sentence_count,
        syllables=syllable_count,
        reading_minutes=reading_minutes,
        flesch_reading_ease=reading_ease,
        flesch_kincaid_grade=grade,
    )
