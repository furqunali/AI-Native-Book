"""Scanner for editorial TODO markers in book chapters.

Draft manuscripts accumulate placeholder markers -- ``TODO``, ``FIXME``,
``TBD`` and ``XXX`` -- that must not survive into a published chapter. This
module finds those markers with their 1-based line numbers so they can be listed
in a report or fail a CI quality gate.

Markers are matched as whole, case-sensitive upper-case words (so the ordinary
word "todo" in prose is not flagged) and any trailing note on the same line is
captured. Fenced code blocks are scanned too, because a stray ``# TODO`` in an
example is just as much an unfinished note.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_DEFAULT_MARKERS = ("TODO", "FIXME", "TBD", "XXX")


@dataclass(frozen=True)
class TodoMarker:
    """A single TODO-style marker found in a chapter.

    ``line`` is the 1-based line number, ``marker`` the matched keyword,
    ``note`` the trailing text after the marker (stripped, may be empty) and
    ``text`` the full original line.
    """

    line: int
    marker: str
    note: str
    text: str


def scan_todos(
    text: str,
    *,
    markers: tuple[str, ...] = _DEFAULT_MARKERS,
) -> list[TodoMarker]:
    """Return the TODO-style markers in ``text``, ordered by line.

    ``markers`` is the tuple of keywords to search for; each must be a non-empty
    upper-case token and is matched case-sensitively on a word boundary. Each
    match records the line number, the keyword, and any note that follows it on
    the same line (a leading ``:`` or ``-`` separator is stripped). A line may
    contribute at most one marker (the earliest match on the line wins).
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(markers, tuple):
        raise TypeError("markers must be a tuple")
    if not markers:
        raise ValueError("markers must not be empty")
    for marker in markers:
        if not isinstance(marker, str) or not marker:
            raise ValueError("each marker must be a non-empty string")

    pattern = re.compile(r"\b(" + "|".join(re.escape(m) for m in markers) + r")\b")

    results: list[TodoMarker] = []
    for i, line in enumerate(text.splitlines()):
        match = pattern.search(line)
        if not match:
            continue
        note = line[match.end():].lstrip(" \t:-").rstrip()
        results.append(
            TodoMarker(
                line=i + 1,
                marker=match.group(1),
                note=note,
                text=line,
            )
        )
    return results


def has_todos(text: str, *, markers: tuple[str, ...] = _DEFAULT_MARKERS) -> bool:
    """Return ``True`` when ``text`` contains any TODO-style marker."""
    return bool(scan_todos(text, markers=markers))
