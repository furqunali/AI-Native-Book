"""List-marker consistency checking for Markdown documents.

Markdown allows unordered lists to use ``-``, ``*`` or ``+`` interchangeably,
and ordered lists to use ``1.`` or ``1)``. Mixing these within one book reads as
sloppy and produces noisy diffs. This module finds list items and flags any that
use a marker other than the expected one, either an explicitly requested style
or, by default, the first marker seen in the document.

Fenced code blocks are skipped so list-like lines in a shell transcript are not
treated as prose lists.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_BULLET = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*+])\s+\S")
_ORDERED = re.compile(r"^(?P<indent>\s*)(?P<num>\d+)(?P<delim>[.)])\s+\S")

_VALID_BULLETS = frozenset({"-", "*", "+"})
_VALID_DELIMS = frozenset({".", ")"})


@dataclass(frozen=True)
class ListStyleIssue:
    """A list item whose marker differs from the expected style.

    ``line`` is the 1-based line number, ``kind`` is ``bullet`` or ``ordered``,
    ``found`` the marker actually used, ``expected`` the marker that was expected
    and ``message`` a human-readable explanation.
    """

    line: int
    kind: str
    found: str
    expected: str
    message: str


def check_list_style(
    text: str,
    *,
    bullet: str | None = None,
    ordered: str | None = None,
) -> list[ListStyleIssue]:
    """Return the ordered list-marker inconsistencies in ``text``.

    ``bullet`` fixes the expected unordered marker (one of ``-``, ``*``, ``+``);
    ``ordered`` fixes the expected ordered delimiter (``.`` or ``)``). When
    either is ``None`` the expectation is inferred from the first matching list
    item in the document, so a self-consistent file always passes. An empty list
    means every list item uses a consistent marker.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if bullet is not None and bullet not in _VALID_BULLETS:
        raise ValueError("bullet must be one of '-', '*', '+'")
    if ordered is not None and ordered not in _VALID_DELIMS:
        raise ValueError("ordered must be '.' or ')'")

    issues: list[ListStyleIssue] = []
    expected_bullet = bullet
    expected_delim = ordered
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

        bullet_match = _BULLET.match(line)
        if bullet_match:
            marker = bullet_match.group("marker")
            if expected_bullet is None:
                expected_bullet = marker
            elif marker != expected_bullet:
                issues.append(
                    ListStyleIssue(
                        line=i + 1,
                        kind="bullet",
                        found=marker,
                        expected=expected_bullet,
                        message=(
                            f"bullet uses '{marker}' but '{expected_bullet}' "
                            f"is expected"
                        ),
                    )
                )
            continue

        ordered_match = _ORDERED.match(line)
        if ordered_match:
            delim = ordered_match.group("delim")
            if expected_delim is None:
                expected_delim = delim
            elif delim != expected_delim:
                issues.append(
                    ListStyleIssue(
                        line=i + 1,
                        kind="ordered",
                        found=delim,
                        expected=expected_delim,
                        message=(
                            f"ordered item uses '{delim}' but '{expected_delim}'"
                            f" is expected"
                        ),
                    )
                )

    return issues


def is_consistent(
    text: str,
    *,
    bullet: str | None = None,
    ordered: str | None = None,
) -> bool:
    """Return ``True`` when all list markers in ``text`` are consistent."""
    return not check_list_style(text, bullet=bullet, ordered=ordered)
