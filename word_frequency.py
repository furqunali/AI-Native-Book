"""Stopword-aware word-frequency analysis for Markdown documents.

Word-frequency counts are a fast way to sanity-check what a chapter is actually
about and to spot filler words that dominate the prose. Counting is done on the
words a reader reads: fenced code blocks, link targets and markdown markers are
stripped before words are tallied so a code snippet cannot inflate a term's
count. Words are lowercased, a compact built-in English stopword list is removed
by default, and results are ranked by descending count with ties broken
alphabetically so the output is fully deterministic.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")

_DEFAULT_MIN_LENGTH = 1

# A compact, general-purpose English stopword list shipped with the module so it
# has no external dependencies. Kept small so domain terms survive as content.
STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
        "can", "could", "did", "do", "does", "for", "from", "had", "has", "have",
        "he", "her", "here", "his", "how", "i", "if", "in", "into", "is", "it",
        "its", "me", "my", "no", "nor", "not", "of", "on", "or", "our", "out",
        "over", "she", "should", "so", "some", "such", "than", "that", "the",
        "their", "them", "then", "there", "these", "they", "this", "those", "to",
        "too", "under", "up", "was", "we", "were", "what", "when", "where",
        "which", "while", "who", "will", "with", "would", "you", "your",
    }
)


@dataclass(frozen=True)
class WordCount:
    """A single word and how often it occurs in a document.

    ``word`` is the normalised (lowercased) form, ``count`` the number of
    occurrences and ``frequency`` that count divided by the total number of
    counted words, rounded to six places.
    """

    word: str
    count: int
    frequency: float


def _strip_markup(text: str) -> str:
    """Reduce markdown to plain prose for counting.

    Fenced code blocks are removed entirely, link/image targets are dropped
    while their visible text is kept, and inline code, emphasis and heading
    markers are discarded.
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


def _normalise(word: str) -> str:
    """Lowercase a token and fold the curly apostrophe to a straight one."""
    return word.lower().replace("’", "'")


def word_frequencies(
    text: str,
    *,
    top_n: int | None = None,
    min_length: int = _DEFAULT_MIN_LENGTH,
    include_stopwords: bool = False,
    stopwords: frozenset[str] | set[str] = STOPWORDS,
) -> list[WordCount]:
    """Return the ranked word frequencies for ``text``.

    Counting is case-insensitive and ignores fenced code and markdown markup.
    Tokens shorter than ``min_length`` are discarded. Unless
    ``include_stopwords`` is true, words in ``stopwords`` are removed. Results
    are ordered by descending count then alphabetically, and limited to the
    ``top_n`` highest-ranked words when ``top_n`` is given. An empty list is
    returned when no words qualify.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(min_length, int) or isinstance(min_length, bool):
        raise TypeError("min_length must be an int")
    if min_length < 1:
        raise ValueError("min_length must be positive")
    if top_n is not None:
        if not isinstance(top_n, int) or isinstance(top_n, bool):
            raise TypeError("top_n must be an int or None")
        if top_n < 1:
            raise ValueError("top_n must be positive")

    prose = _strip_markup(text)
    tokens: list[str] = []
    for raw in _WORD.findall(prose):
        word = _normalise(raw)
        if len(word) < min_length:
            continue
        if not include_stopwords and word in stopwords:
            continue
        tokens.append(word)

    total = len(tokens)
    if total == 0:
        return []

    counts = Counter(tokens)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    result = [
        WordCount(word=word, count=count, frequency=round(count / total, 6))
        for word, count in ranked
    ]
    if top_n is not None:
        result = result[:top_n]
    return result


def total_words(
    text: str,
    *,
    min_length: int = _DEFAULT_MIN_LENGTH,
    include_stopwords: bool = False,
    stopwords: frozenset[str] | set[str] = STOPWORDS,
) -> int:
    """Return the total number of counted words in ``text``.

    The same filtering as :func:`word_frequencies` is applied, so this equals
    the sum of every returned :class:`WordCount`'s ``count``.
    """
    return sum(
        wc.count
        for wc in word_frequencies(
            text,
            min_length=min_length,
            include_stopwords=include_stopwords,
            stopwords=stopwords,
        )
    )
