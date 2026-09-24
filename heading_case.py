"""Title Case consistency checking for ATX headings.

Books read more professionally when headings follow a single capitalisation
convention. This module checks ATX headings against a Title Case rule: the first
and last words are always capitalised, "major" words are capitalised, and a
curated set of "minor" words (articles, coordinating conjunctions and short
prepositions) stay lower-case when they fall in the middle of the heading.

The check is deliberately forgiving of tokens it cannot judge: all-caps
acronyms (``API``), words that start with a digit, and words containing internal
capitals (``iPhone``) are left alone. Headings in fenced code blocks are
ignored.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^\s{0,3}(#{1,6})(?:\s+(.*?))?\s*$")
_ATX_CLOSING = re.compile(r"\s+#+\s*$")
_TOKEN = re.compile(r"[A-Za-z][A-Za-z'’]*")

_MINOR_WORDS = frozenset(
    {
        "a", "an", "and", "as", "at", "but", "by", "for", "from", "if", "in",
        "into", "nor", "of", "on", "onto", "or", "over", "per", "so", "the",
        "to", "up", "via", "vs", "with", "yet",
    }
)


@dataclass(frozen=True)
class HeadingCaseIssue:
    """A heading that deviates from Title Case.

    ``line`` is the 1-based line number, ``heading`` the heading text as written
    (inline markers stripped), ``words`` the list of offending words, and
    ``message`` a human-readable explanation.
    """

    line: int
    heading: str
    words: tuple[str, ...]
    message: str


def _strip_inline(raw: str) -> str:
    """Reduce heading inline markdown to plain text."""
    raw = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", raw)
    raw = re.sub(r"`([^`]*)`", r"\1", raw)
    raw = re.sub(r"[*_~]", "", raw)
    return raw.strip()


def _is_uncapitalisable(token: str) -> bool:
    """Return ``True`` for tokens whose casing should not be judged."""
    if token.isupper():  # acronym such as API, LLM
        return True
    # Internal capital after the first letter, e.g. iPhone, gRPC.
    return any(c.isupper() for c in token[1:])


def _should_be_capital(word: str, position: int, last_index: int) -> bool:
    """Return whether ``word`` at ``position`` must start with a capital."""
    if position == 0 or position == last_index:
        return True
    return word.lower() not in _MINOR_WORDS


def check_heading_case(text: str) -> list[HeadingCaseIssue]:
    """Return the ATX headings in ``text`` that deviate from Title Case.

    For each heading, the alphabetic words are extracted. A word that *should* be
    capitalised (the first word, the last word, or any non-minor word) but starts
    lower-case is an offender. Acronyms, digit-led words and internally
    capitalised words are ignored. Headings with no judgeable words pass. The
    result is ordered by line; an empty list means every heading is Title Case.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    issues: list[HeadingCaseIssue] = []
    fence: str | None = None
    for i, line in enumerate(text.splitlines()):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        atx = _ATX.match(line)
        if not atx:
            continue
        heading = _strip_inline(_ATX_CLOSING.sub("", atx.group(2) or "").strip())
        words = _TOKEN.findall(heading)
        if not words:
            continue

        last = len(words) - 1
        offenders: list[str] = []
        for pos, word in enumerate(words):
            if _is_uncapitalisable(word):
                continue
            if _should_be_capital(word, pos, last) and not word[0].isupper():
                offenders.append(word)

        if offenders:
            issues.append(
                HeadingCaseIssue(
                    line=i + 1,
                    heading=heading,
                    words=tuple(offenders),
                    message=(
                        f"heading '{heading}' is not Title Case; expected "
                        f"capitals on: {', '.join(offenders)}"
                    ),
                )
            )
    return issues


def is_title_case(text: str) -> bool:
    """Return ``True`` when every ATX heading in ``text`` is Title Case."""
    return not check_heading_case(text)
