"""Detection of inconsistent thousands formatting for large numbers.

A document that writes "1,000" in one place and "1000" in another looks
careless. This module finds integers at or above a configurable threshold,
classifies each as *grouped* (digits separated by commas, ``1,000``) or *plain*
(no separators, ``1000``), decides which style dominates, and reports the
numbers written in the minority style so they can be normalised.

Numbers that are part of a decimal, a version string or a longer digit run are
not matched, and numbers inside inline code spans and fenced code blocks are
ignored so code samples do not trigger false positives.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")

# A trailing sentence '.' or ',' is allowed, but a '.' or ',' that is followed
# by a digit (a decimal fraction or another group) means the token is part of a
# larger number and must not be matched.
_GROUPED = re.compile(r"(?<![\d.,])\d{1,3}(?:,\d{3})+(?!\d)(?!\.\d)(?!,\d)")
_PLAIN = re.compile(r"(?<![\d.,])\d{4,}(?!\d)(?!\.\d)(?!,\d)")

_DEFAULT_MIN_VALUE = 1000


@dataclass(frozen=True)
class NumberRef:
    """A large number found in the text.

    ``line`` is the 1-based line number, ``text`` the number as written,
    ``value`` its integer value and ``style`` either ``"grouped"`` or
    ``"plain"``.
    """

    line: int
    text: str
    value: int
    style: str


@dataclass(frozen=True)
class NumberFormatReport:
    """The document-wide thousands-formatting summary.

    ``grouped`` and ``plain`` are the counts of each style, ``dominant`` is
    ``"grouped"``, ``"plain"`` or ``"none"``, and ``deviations`` lists the
    numbers written in the minority style in document order. Grouped wins ties.
    """

    grouped: int
    plain: int
    dominant: str
    deviations: tuple[NumberRef, ...]

    @property
    def is_consistent(self) -> bool:
        """Return ``True`` when at most one thousands style is in use."""
        return not self.deviations


def find_numbers(text: str, *, min_value: int = _DEFAULT_MIN_VALUE) -> list[NumberRef]:
    """Return the large numbers in ``text`` in document order.

    A number qualifies when its integer value is at least ``min_value``. Each is
    classified as grouped or plain. Numbers inside code are ignored. The
    ordering is by line, then by position within the line (grouped and plain
    matches on one line are merged in column order).
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(min_value, int) or isinstance(min_value, bool):
        raise TypeError("min_value must be an int")
    if min_value < 1:
        raise ValueError("min_value must be positive")

    refs: list[NumberRef] = []
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

        cleaned = _CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line)
        found: list[tuple[int, str, int, str]] = []
        for m in _GROUPED.finditer(cleaned):
            value = int(m.group(0).replace(",", ""))
            if value >= min_value:
                found.append((m.start(), m.group(0), value, "grouped"))
        for m in _PLAIN.finditer(cleaned):
            value = int(m.group(0))
            if value >= min_value:
                found.append((m.start(), m.group(0), value, "plain"))
        found.sort(key=lambda item: item[0])
        for _col, token, value, style in found:
            refs.append(NumberRef(line=i + 1, text=token, value=value, style=style))

    return refs


def check_number_format(
    text: str,
    *,
    min_value: int = _DEFAULT_MIN_VALUE,
) -> NumberFormatReport:
    """Return the thousands-formatting report for ``text``.

    The dominant style is the one with more numbers (grouped wins a tie); the
    numbers in the other style become ``deviations``. When only one or neither
    style appears, there are no deviations.
    """
    refs = find_numbers(text, min_value=min_value)
    grouped = sum(1 for r in refs if r.style == "grouped")
    plain = sum(1 for r in refs if r.style == "plain")

    if grouped == 0 and plain == 0:
        dominant = "none"
        minority = None
    elif grouped >= plain:
        dominant = "grouped"
        minority = "plain"
    else:
        dominant = "plain"
        minority = "grouped"

    deviations = tuple(r for r in refs if r.style == minority)
    return NumberFormatReport(
        grouped=grouped,
        plain=plain,
        dominant=dominant,
        deviations=deviations,
    )
