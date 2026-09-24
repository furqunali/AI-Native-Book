"""Trailing-punctuation checking for ATX headings.

Headings are labels, not sentences, so they should not end in sentence
punctuation. A stray ``.``, ``,``, ``:``, ``;`` or ``!`` at the end of a heading
looks like a typo and is inconsistent with the rest of a book's headings. This
module flags ATX headings whose (inline-stripped) text ends with such a
character.

A trailing question mark is allowed by default, because rhetorical-question
headings are a legitimate style; the trailing character set is configurable if a
project wants to forbid it too. Optional ATX closing hashes (``## Title ##``)
are stripped before the check, and headings in fenced code blocks are ignored.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^\s{0,3}(#{1,6})(?:\s+(.*?))?\s*$")
_ATX_CLOSING = re.compile(r"\s+#+\s*$")

_DEFAULT_PUNCT = ".,:;!"


@dataclass(frozen=True)
class TrailingPunctIssue:
    """A heading that ends with disallowed punctuation.

    ``line`` is the 1-based line number, ``heading`` the inline-stripped heading
    text, ``char`` the offending trailing character, and ``message`` a
    human-readable explanation.
    """

    line: int
    heading: str
    char: str
    message: str


def _strip_inline(raw: str) -> str:
    """Reduce heading inline markdown to plain text."""
    raw = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", raw)
    raw = re.sub(r"`([^`]*)`", r"\1", raw)
    raw = re.sub(r"[*_~]", "", raw)
    return raw.strip()


def check_trailing_punct(
    text: str,
    *,
    punctuation: str = _DEFAULT_PUNCT,
) -> list[TrailingPunctIssue]:
    """Return ATX headings in ``text`` that end with disallowed punctuation.

    ``punctuation`` is the set of characters that must not appear as a heading's
    final character (default ``.,:;!``; a trailing ``?`` is allowed unless added
    here). Inline markdown and optional closing hashes are stripped before the
    final character is examined. Results are ordered by line; an empty list means
    no heading ends with disallowed punctuation.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(punctuation, str):
        raise TypeError("punctuation must be a string")
    if not punctuation:
        raise ValueError("punctuation must not be empty")

    forbidden = set(punctuation)
    issues: list[TrailingPunctIssue] = []
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
        if not heading:
            continue

        last = heading[-1]
        if last in forbidden:
            issues.append(
                TrailingPunctIssue(
                    line=i + 1,
                    heading=heading,
                    char=last,
                    message=(
                        f"heading '{heading}' ends with '{last}'"
                    ),
                )
            )
    return issues


def has_trailing_punct(text: str, *, punctuation: str = _DEFAULT_PUNCT) -> bool:
    """Return ``True`` when any ATX heading ends with disallowed punctuation."""
    return bool(check_trailing_punct(text, punctuation=punctuation))
