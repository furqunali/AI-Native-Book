"""Whitespace and blank-line hygiene checks for Markdown documents.

Trailing spaces, hard tabs and long runs of blank lines create noisy diffs and
inconsistent rendering across editors. This module reports those defects with
precise line numbers so they can be fixed (or gated in CI). Checks that would
misfire on legitimate code are suppressed inside fenced code blocks, where tabs
and trailing spaces can be meaningful.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_TRAILING = re.compile(r"[ \t]+$")


@dataclass(frozen=True)
class WhitespaceIssue:
    """A whitespace-hygiene problem.

    ``line`` is the 1-based line number (0 for whole-file issues), ``kind`` a
    short code and ``message`` a human-readable explanation.
    """

    line: int
    kind: str
    message: str


def check_whitespace(text: str, *, max_blank_run: int = 1) -> list[WhitespaceIssue]:
    """Return the ordered whitespace issues in ``text``.

    The following are reported:

    * ``trailing-whitespace`` -- a line ends with spaces or tabs (outside code
      fences).
    * ``hard-tab`` -- a line contains a tab character (outside code fences).
    * ``consecutive-blanks`` -- more than ``max_blank_run`` blank lines appear in
      a row (outside code fences); the issue is attached to the first offending
      blank line.
    * ``missing-final-newline`` -- a non-empty document does not end with a
      newline.

    An empty list means the document is clean.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(max_blank_run, int) or isinstance(max_blank_run, bool):
        raise TypeError("max_blank_run must be an int")
    if max_blank_run < 0:
        raise ValueError("max_blank_run must not be negative")

    issues: list[WhitespaceIssue] = []
    lines = text.splitlines()
    fence: str | None = None
    blank_run = 0
    blank_run_start = 0

    for i, line in enumerate(lines):
        match = _FENCE.match(line)
        in_fence_boundary = match is not None
        if fence is None:
            if in_fence_boundary:
                fence = match.group(1)
                blank_run = 0
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            blank_run = 0
            continue

        if line.strip() == "":
            if blank_run == 0:
                blank_run_start = i + 1
            blank_run += 1
            if blank_run == max_blank_run + 1:
                issues.append(
                    WhitespaceIssue(
                        line=blank_run_start,
                        kind="consecutive-blanks",
                        message=(
                            f"more than {max_blank_run} consecutive blank "
                            f"line(s)"
                        ),
                    )
                )
            continue

        blank_run = 0
        if _TRAILING.search(line):
            issues.append(
                WhitespaceIssue(
                    line=i + 1,
                    kind="trailing-whitespace",
                    message="line has trailing whitespace",
                )
            )
        if "\t" in line:
            issues.append(
                WhitespaceIssue(
                    line=i + 1,
                    kind="hard-tab",
                    message="line contains a hard tab; use spaces",
                )
            )

    if text and not text.endswith(("\n", "\r")):
        issues.append(
            WhitespaceIssue(
                line=len(lines),
                kind="missing-final-newline",
                message="file does not end with a newline",
            )
        )

    issues.sort(key=lambda issue: (issue.line, issue.kind))
    return issues


def is_clean(text: str, *, max_blank_run: int = 1) -> bool:
    """Return ``True`` when ``text`` has no whitespace-hygiene issues."""
    return not check_whitespace(text, max_blank_run=max_blank_run)
