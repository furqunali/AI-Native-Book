"""Acronym extraction for book chapters.

Technical books lean on acronyms (``API``, ``LLM``, ``RAG``), and a glossary or
index needs to know which appear and where each is first introduced. This module
extracts all-caps acronyms and records the 1-based line on which each is first
seen, along with how many times it occurs.

An acronym is a token of two or more upper-case letters, optionally carrying
embedded digits (``GPT4``, ``S3``) and an optional trailing plural ``s``
(``APIs``). Fenced code blocks and inline code spans are skipped so identifiers
from code examples do not pollute the glossary, and a small stop set of common
all-caps words (``I``, ``OK``, ``TODO`` …) can be excluded.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")
_ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]*[A-Z0-9](?:s)?\b")

_DEFAULT_STOP = frozenset({"A", "I", "OK", "TODO", "FIXME", "TBD", "XXX"})


@dataclass(frozen=True)
class Acronym:
    """A distinct acronym and where it first appears.

    ``text`` is the acronym as written (its first-seen form), ``first_line`` the
    1-based line of that first occurrence, and ``count`` the total number of
    occurrences across the chapter.
    """

    text: str
    first_line: int
    count: int


def extract_acronyms(
    text: str,
    *,
    stop_words: frozenset[str] = _DEFAULT_STOP,
) -> list[Acronym]:
    """Return the acronyms in ``text`` ordered by first appearance.

    An acronym is two or more upper-case characters (letters or digits, starting
    with a letter and ending in a letter or digit) with an optional trailing
    plural ``s``. Any acronym in ``stop_words`` is ignored. Distinct casings such
    as ``APIs`` and ``API`` are counted separately. Inline code and fenced code
    blocks are skipped. The list is ordered by the line of first appearance.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(stop_words, (set, frozenset)):
        raise TypeError("stop_words must be a set or frozenset")

    order: list[str] = []
    first_line: dict[str, int] = {}
    counts: dict[str, int] = {}

    fence: str | None = None
    for i, raw in enumerate(text.splitlines()):
        match = _FENCE.match(raw)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
        else:
            if raw.lstrip().startswith(fence):
                fence = None
            continue

        line = _CODE_SPAN.sub(" ", raw)
        for token in _ACRONYM.findall(line):
            if token in stop_words:
                continue
            if token not in counts:
                order.append(token)
                first_line[token] = i + 1
                counts[token] = 0
            counts[token] += 1

    return [
        Acronym(text=token, first_line=first_line[token], count=counts[token])
        for token in order
    ]


def acronym_set(text: str, *, stop_words: frozenset[str] = _DEFAULT_STOP) -> set[str]:
    """Return the distinct acronyms in ``text`` as a set of strings."""
    return {a.text for a in extract_acronyms(text, stop_words=stop_words)}
