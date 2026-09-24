"""Jaccard similarity between the keyword sets of two chapters.

Comparing chapters by their vocabulary surfaces accidental overlap (two chapters
that cover almost the same ground) and structural gaps (a chapter that shares
nothing with the rest of the book). The metric used is the Jaccard index -- the
size of the intersection of the two keyword sets divided by the size of their
union -- computed over lowercased, stopword-filtered word sets so markup and
common English do not distort the score.

The module is self-contained: it derives keyword sets with its own lightweight
tokeniser rather than depending on other modules.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")

_DEFAULT_MIN_LENGTH = 3

# Small stopword list; shared shape with the rest of the toolkit but local so
# this module carries no dependencies.
STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can",
        "could", "did", "do", "does", "for", "from", "had", "has", "have", "he",
        "her", "here", "his", "how", "if", "in", "into", "is", "it", "its",
        "not", "of", "on", "or", "our", "out", "over", "she", "should", "so",
        "some", "such", "than", "that", "the", "their", "them", "then", "there",
        "these", "they", "this", "those", "to", "too", "under", "up", "was",
        "we", "were", "what", "when", "where", "which", "while", "who", "will",
        "with", "would", "you", "your",
    }
)


@dataclass(frozen=True)
class SimilarityResult:
    """The outcome of comparing two chapters' keyword sets.

    ``jaccard`` is the Jaccard index in ``[0, 1]`` rounded to six places,
    ``intersection`` and ``union`` are the respective set sizes, and ``shared``
    is the sorted tuple of keywords common to both chapters.
    """

    jaccard: float
    intersection: int
    union: int
    shared: tuple[str, ...]


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


def keyword_set(
    text: str,
    *,
    min_length: int = _DEFAULT_MIN_LENGTH,
    stopwords: frozenset[str] | set[str] = STOPWORDS,
) -> frozenset[str]:
    """Return the set of distinct keywords in chapter ``text``.

    Words are lowercased, apostrophe-folded and filtered by ``min_length``, pure
    digits, and the ``stopwords`` set. Fenced code and markdown markup are
    ignored. The result is a frozen set suitable for set arithmetic.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(min_length, int) or isinstance(min_length, bool):
        raise TypeError("min_length must be an int")
    if min_length < 1:
        raise ValueError("min_length must be positive")

    prose = _strip_markup(text)
    words: set[str] = set()
    for raw in _WORD.findall(prose):
        word = raw.lower().replace("’", "'")
        if len(word) < min_length or word.isdigit() or word in stopwords:
            continue
        words.add(word)
    return frozenset(words)


def chapter_similarity(
    first: str,
    second: str,
    *,
    min_length: int = _DEFAULT_MIN_LENGTH,
    stopwords: frozenset[str] | set[str] = STOPWORDS,
) -> SimilarityResult:
    """Return the Jaccard similarity between chapters ``first`` and ``second``.

    Each chapter is reduced to its keyword set and the Jaccard index is computed
    over the two sets. Two empty chapters are defined to have a similarity of
    ``0.0`` (there is no shared vocabulary to speak of) rather than raising, so
    callers can score every chapter pair uniformly.
    """
    a = keyword_set(first, min_length=min_length, stopwords=stopwords)
    b = keyword_set(second, min_length=min_length, stopwords=stopwords)

    intersection = a & b
    union = a | b
    score = 0.0 if not union else len(intersection) / len(union)
    return SimilarityResult(
        jaccard=round(score, 6),
        intersection=len(intersection),
        union=len(union),
        shared=tuple(sorted(intersection)),
    )
