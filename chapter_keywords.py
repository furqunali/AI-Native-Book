"""Stopword-aware word-frequency and keyword extraction for book chapters.

Keywords are drawn from the prose a reader actually reads: fenced code blocks,
markdown syntax and link targets are stripped before counting so a code-heavy
chapter is not credited with keywords lifted from its snippets. Words are
lowercased and folded, a curated English stopword list and short tokens are
discarded, and the surviving terms are ranked by frequency with ties broken
alphabetically so results are fully deterministic.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")

_DEFAULT_MIN_LENGTH = 3

# A compact, general-purpose English stopword list. Kept intentionally small so
# domain terms (model, agent, prompt, context, …) survive as keywords.
STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "about", "above", "after", "again", "against", "all", "am", "an",
        "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
        "before", "being", "below", "between", "both", "but", "by", "can",
        "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
        "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
        "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
        "having", "he", "her", "here", "hers", "herself", "him", "himself",
        "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its",
        "itself", "just", "let", "me", "more", "most", "must", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
        "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
        "shan't", "she", "should", "shouldn't", "so", "some", "such", "than",
        "that", "the", "their", "theirs", "them", "themselves", "then",
        "there", "these", "they", "this", "those", "through", "to", "too",
        "under", "until", "up", "very", "was", "wasn't", "we", "were",
        "weren't", "what", "when", "where", "which", "while", "who", "whom",
        "why", "will", "with", "won't", "would", "wouldn't", "you", "your",
        "yours", "yourself", "yourselves",
    }
)


@dataclass(frozen=True)
class Keyword:
    """A single ranked keyword extracted from a chapter.

    ``term`` is the normalised (lowercased) token, ``count`` is how many times
    it appears in the chapter's prose, and ``frequency`` is that count divided
    by the total number of counted tokens, rounded to six places.
    """

    term: str
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
    """Lowercase a token and fold the curly apostrophe to a straight one.

    Folding keeps ``don't`` and ``don’t`` as the same stopword regardless of
    which apostrophe the source markdown used.
    """
    return word.lower().replace("’", "'")


def tokenize(
    text: str,
    *,
    min_length: int = _DEFAULT_MIN_LENGTH,
    stopwords: frozenset[str] | set[str] = STOPWORDS,
) -> list[str]:
    """Return the ordered, filtered keyword tokens for chapter ``text``.

    Markdown markup and fenced code are stripped, remaining words are
    lowercased and apostrophe-folded, then tokens that are pure numbers, are
    shorter than ``min_length``, or appear in ``stopwords`` are dropped. The
    surviving tokens are returned in reading order (duplicates preserved).
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(min_length, int) or isinstance(min_length, bool):
        raise TypeError("min_length must be an int")
    if min_length < 1:
        raise ValueError("min_length must be positive")

    prose = _strip_markup(text)
    tokens: list[str] = []
    for raw in _WORD.findall(prose):
        word = _normalise(raw)
        if len(word) < min_length:
            continue
        if word.isdigit():
            continue
        if word in stopwords:
            continue
        tokens.append(word)
    return tokens


def extract_keywords(
    text: str,
    *,
    top_n: int | None = None,
    min_length: int = _DEFAULT_MIN_LENGTH,
    min_count: int = 1,
    stopwords: frozenset[str] | set[str] = STOPWORDS,
) -> list[Keyword]:
    """Extract ranked keywords from chapter ``text``.

    Tokens are counted after stopword and short-word filtering. Keywords are
    ranked by descending count with ties broken alphabetically so the result is
    deterministic. ``min_count`` drops rare terms, and ``top_n`` (when given)
    limits the result to the highest-ranked keywords. An empty list is returned
    for text with no qualifying tokens so callers can fold the result into
    aggregate reports without special casing.
    """
    if top_n is not None:
        if not isinstance(top_n, int) or isinstance(top_n, bool):
            raise TypeError("top_n must be an int or None")
        if top_n < 1:
            raise ValueError("top_n must be positive")
    if not isinstance(min_count, int) or isinstance(min_count, bool):
        raise TypeError("min_count must be an int")
    if min_count < 1:
        raise ValueError("min_count must be positive")

    tokens = tokenize(text, min_length=min_length, stopwords=stopwords)
    total = len(tokens)
    if total == 0:
        return []

    counts = Counter(tokens)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    keywords = [
        Keyword(term=term, count=count, frequency=round(count / total, 6))
        for term, count in ranked
        if count >= min_count
    ]
    if top_n is not None:
        keywords = keywords[:top_n]
    return keywords
