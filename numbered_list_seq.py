"""Ordered-list numbering validation for Markdown documents.

An ordered list should be numbered ``1, 2, 3, …`` with no gaps or accidental
restarts. Although many renderers renumber automatically, an out-of-sequence
source list (``1, 2, 4`` or ``1, 2, 1``) is almost always an editing mistake and
reads wrong in any renderer that respects the written numbers. This module
groups ordered-list items by indentation and flags items whose number does not
follow its predecessor.

Nested lists are tracked independently by indent width. A run is considered
broken -- so numbering may legitimately restart -- by a heading, a fenced code
block, or a blank-line gap of two or more lines. Fenced code blocks are skipped.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_HEADING = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
_ORDERED = re.compile(r"^(?P<indent>\s*)(?P<num>\d+)[.)]\s+\S")


@dataclass(frozen=True)
class SequenceIssue:
    """An ordered-list item whose number is out of sequence.

    ``line`` is the 1-based line number, ``kind`` a short code (``bad-start`` or
    ``out-of-sequence``), ``found`` the number written, ``expected`` the number
    that was expected, and ``message`` a human-readable explanation.
    """

    line: int
    kind: str
    found: int
    expected: int
    message: str


def check_numbering(text: str, *, start_at: int = 1) -> list[SequenceIssue]:
    """Return ordered-list items in ``text`` that break numbering sequence.

    Each ordered item is grouped by its indentation width. The first item of a
    run must equal ``start_at`` (else ``bad-start``); every later item must be
    exactly one more than its predecessor (else ``out-of-sequence``). A run ends
    -- allowing the count to restart -- at a heading, a fenced code block, or two
    or more consecutive blank lines. Results are ordered by line; an empty list
    means every ordered list counts correctly.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(start_at, int) or isinstance(start_at, bool):
        raise TypeError("start_at must be an int")

    issues: list[SequenceIssue] = []
    # indent width -> last number seen in the active run at that indent.
    active: dict[int, int] = {}
    fence: str | None = None
    blank_streak = 0

    for i, line in enumerate(text.splitlines()):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                active.clear()
                fence = match.group(1)
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        if line.strip() == "":
            blank_streak += 1
            if blank_streak >= 2:
                active.clear()
            continue
        blank_streak = 0

        if _HEADING.match(line):
            active.clear()
            continue

        ordered = _ORDERED.match(line)
        if not ordered:
            continue

        indent = len(ordered.group("indent").expandtabs(4))
        num = int(ordered.group("num"))

        if indent not in active:
            # Deeper nesting starting fresh clears shallower siblings' runs only
            # when a new outermost item appears.
            if indent == 0:
                active = {0: num}
            else:
                active[indent] = num
            if num != start_at:
                issues.append(
                    SequenceIssue(
                        line=i + 1,
                        kind="bad-start",
                        found=num,
                        expected=start_at,
                        message=(
                            f"ordered list starts at {num}; expected {start_at}"
                        ),
                    )
                )
            continue

        expected = active[indent] + 1
        if num != expected:
            issues.append(
                SequenceIssue(
                    line=i + 1,
                    kind="out-of-sequence",
                    found=num,
                    expected=expected,
                    message=(
                        f"ordered item is {num}; expected {expected}"
                    ),
                )
            )
        active[indent] = num

    return issues


def is_sequential(text: str, *, start_at: int = 1) -> bool:
    """Return ``True`` when every ordered list in ``text`` counts correctly."""
    return not check_numbering(text, start_at=start_at)
