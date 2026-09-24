"""Flagging of chapters whose length is far from the book's median.

A book reads more evenly when its chapters are roughly comparable in length. A
chapter that is a fraction of the median length may be a stub, and one several
times the median may need splitting. Given a mapping of chapter name to word
count, this module computes the median length and flags every chapter whose
count deviates from it by more than a configurable tolerance.

The tolerance is expressed as a fraction of the median: a tolerance of ``0.5``
flags chapters shorter than half the median or longer than 1.5x the median. The
function is pure -- it operates only on the counts it is given.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median

_DEFAULT_TOLERANCE = 0.5


@dataclass(frozen=True)
class BalanceIssue:
    """A chapter whose length deviates too far from the median.

    ``chapter`` is the chapter's name, ``count`` its word count, ``median`` the
    median across all chapters, ``deviation`` the signed relative deviation
    ``(count - median) / median`` rounded to six places, and ``direction``
    either ``"short"`` or ``"long"``.
    """

    chapter: str
    count: int
    median: float
    deviation: float
    direction: str


def check_balance(
    counts: dict[str, int],
    *,
    tolerance: float = _DEFAULT_TOLERANCE,
) -> list[BalanceIssue]:
    """Return the chapters in ``counts`` that are out of balance.

    ``counts`` maps chapter name to a non-negative word count. A chapter is
    flagged when the absolute value of its relative deviation from the median
    exceeds ``tolerance`` (a positive fraction). Results are ordered by
    descending absolute deviation, ties broken by chapter name, so the most
    lopsided chapters come first. An empty mapping, or a median of zero,
    produces an empty list.
    """
    if not isinstance(counts, dict):
        raise TypeError("counts must be a dict of chapter name to word count")
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        raise TypeError("tolerance must be a number")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    for name, value in counts.items():
        if not isinstance(name, str):
            raise TypeError("chapter names must be strings")
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("word counts must be ints")
        if value < 0:
            raise ValueError("word counts must be non-negative")

    if not counts:
        return []

    mid = median(counts.values())
    if mid == 0:
        return []

    issues: list[BalanceIssue] = []
    for name, value in counts.items():
        deviation = (value - mid) / mid
        if abs(deviation) > tolerance:
            issues.append(
                BalanceIssue(
                    chapter=name,
                    count=value,
                    median=float(mid),
                    deviation=round(deviation, 6),
                    direction="long" if deviation > 0 else "short",
                )
            )

    issues.sort(key=lambda issue: (-abs(issue.deviation), issue.chapter))
    return issues


def is_balanced(
    counts: dict[str, int],
    *,
    tolerance: float = _DEFAULT_TOLERANCE,
) -> bool:
    """Return ``True`` when no chapter deviates beyond ``tolerance``."""
    return not check_balance(counts, tolerance=tolerance)
