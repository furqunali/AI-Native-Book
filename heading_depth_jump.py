"""Flagging of headings nested deeper than a configured maximum level.

Deeply nested headings (``#####`` and beyond) are a sign that a section has
grown too complex or that the author is using headings for emphasis rather than
structure. Most books cap their outline at three or four levels. This module
parses ATX headings and reports any whose level exceeds a configurable maximum,
so an editor can flatten or restructure the offending sections.

Headings inside fenced code blocks are ignored, and a leading ``#`` sequence
must be followed by a space to count as a heading (so ``#hashtag`` is not one).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.*?)\s*#*\s*$")

_DEFAULT_MAX_LEVEL = 3


@dataclass(frozen=True)
class DepthIssue:
    """A heading nested deeper than the allowed maximum.

    ``line`` is the 1-based line number, ``level`` the heading level, ``title``
    the heading text and ``message`` a human-readable explanation.
    """

    line: int
    level: int
    title: str
    message: str


def check_depth(text: str, *, max_level: int = _DEFAULT_MAX_LEVEL) -> list[DepthIssue]:
    """Return the headings in ``text`` deeper than ``max_level``.

    Every ATX heading whose level is greater than ``max_level`` is reported in
    document order. ``max_level`` must be between 1 and 6. Headings inside
    fenced code blocks are ignored. An empty list means the document respects
    the depth limit.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(max_level, int) or isinstance(max_level, bool):
        raise TypeError("max_level must be an int")
    if not 1 <= max_level <= 6:
        raise ValueError("max_level must be between 1 and 6")

    issues: list[DepthIssue] = []
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

        heading = _ATX.match(line)
        if heading is None:
            continue
        level = len(heading.group("hashes"))
        if level > max_level:
            title = heading.group("title").strip()
            issues.append(
                DepthIssue(
                    line=i + 1,
                    level=level,
                    title=title,
                    message=(
                        f"heading '{title}' is at level {level}, deeper than "
                        f"the maximum of {max_level}"
                    ),
                )
            )

    return issues


def deepest_level(text: str) -> int:
    """Return the deepest ATX heading level in ``text`` (0 if there are none)."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    deepest = 0
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
        heading = _ATX.match(line)
        if heading is not None:
            deepest = max(deepest, len(heading.group("hashes")))
    return deepest
