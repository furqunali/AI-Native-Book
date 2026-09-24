"""Duplicate-heading detection for book chapters.

Repeated heading titles make a document harder to navigate: a table of contents
shows two identical entries, and GitHub silently disambiguates their anchors
(``#setup`` vs ``#setup-1``), so a hand-written link to the second one is easy
to get wrong. This module groups headings whose titles are effectively the same
and reports every group that occurs more than once.

Headings are read via :func:`chapter_outline.extract_outline`, so fenced code
blocks are ignored and both ATX and setext headings are recognised.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from chapter_outline import extract_outline

_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class DuplicateGroup:
    """A set of headings that share a normalised title.

    ``title`` is the display title of the first occurrence, ``normalized`` the
    comparison key, ``lines`` the 1-based line numbers of every occurrence (in
    document order) and ``levels`` the corresponding heading levels.
    """

    title: str
    normalized: str
    lines: tuple[int, ...]
    levels: tuple[int, ...]

    @property
    def count(self) -> int:
        """Number of times the heading appears."""
        return len(self.lines)


def _normalize(title: str) -> str:
    """Return the case- and whitespace-insensitive comparison key for a title."""
    return _WHITESPACE.sub(" ", title.strip().lower())


def find_duplicate_headings(
    text: str, *, within_level: bool = False
) -> list[DuplicateGroup]:
    """Return the groups of duplicate headings in ``text``.

    Titles are compared case-insensitively with surrounding and repeated
    whitespace normalised. When ``within_level`` is true, headings only collide
    if they also share the same level, so a level-2 ``Overview`` and a level-3
    ``Overview`` are treated as distinct. Groups are returned in order of first
    appearance, and only titles that occur more than once are included.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    order: list[tuple[str, int]] = []
    groups: dict[tuple[str, int], dict] = {}

    for heading in extract_outline(text):
        norm = _normalize(heading.title)
        key = (norm, heading.level if within_level else 0)
        if key not in groups:
            groups[key] = {
                "title": heading.title,
                "normalized": norm,
                "lines": [],
                "levels": [],
            }
            order.append(key)
        groups[key]["lines"].append(heading.line)
        groups[key]["levels"].append(heading.level)

    result: list[DuplicateGroup] = []
    for key in order:
        data = groups[key]
        if len(data["lines"]) > 1:
            result.append(
                DuplicateGroup(
                    title=data["title"],
                    normalized=data["normalized"],
                    lines=tuple(data["lines"]),
                    levels=tuple(data["levels"]),
                )
            )
    return result


def has_duplicate_headings(text: str, *, within_level: bool = False) -> bool:
    """Return ``True`` when any heading title is used more than once."""
    return bool(find_duplicate_headings(text, within_level=within_level))
