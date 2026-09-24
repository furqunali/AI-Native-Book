"""Blockquote-marker style checking for Markdown documents.

Blockquotes should use a consistent ``> `` marker: a greater-than sign followed
by a single space before the quoted text. Writers frequently forget the space
(``>quote``) or add several (``>   quote``), which renders inconsistently across
markdown engines. This module flags blockquote lines whose marker does not match
the ``> `` convention, supporting nested quotes where each ``>`` level must be
spaced.

A bare ``>`` on an otherwise empty line is allowed, since it is the idiomatic
way to separate paragraphs within one blockquote. Fenced code blocks are
ignored.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
# Leading blockquote markers, e.g. "> ", ">>", "  > ".
_QUOTE_LINE = re.compile(r"^\s*>")


@dataclass(frozen=True)
class BlockquoteIssue:
    """A blockquote line whose marker style is inconsistent.

    ``line`` is the 1-based line number, ``kind`` a short code
    (``missing-space`` or ``extra-space``), ``text`` the original line and
    ``message`` a human-readable explanation.
    """

    line: int
    kind: str
    text: str
    message: str


def _classify(line: str) -> str | None:
    """Return an issue kind for a blockquote ``line`` or ``None`` if it is clean.

    Each ``>`` marker must be followed by exactly one space, unless it is the
    final marker on an empty quote line (``>`` alone) or immediately nests
    another ``>``.
    """
    i = 0
    n = len(line)
    # Skip leading indentation.
    while i < n and line[i] in " \t":
        i += 1
    while i < n and line[i] == ">":
        i += 1  # consume the '>'
        if i >= n:
            return None  # trailing '>' with nothing after: empty quote line, OK
        if line[i] == ">":
            continue  # nested marker, check the next '>'
        if line[i] != " ":
            return "missing-space"
        # Exactly one space then content is ideal; two or more is extra-space
        # unless the rest of the line is blank (an empty quote line).
        spaces = 0
        while i < n and line[i] == " ":
            spaces += 1
            i += 1
        if i >= n:
            return None  # "> " with nothing after is an empty quote line
        if spaces >= 2:
            return "extra-space"
        return None
    return None


def check_blockquote_style(text: str) -> list[BlockquoteIssue]:
    """Return blockquote lines in ``text`` whose marker style is inconsistent.

    A line is checked only when it begins (after optional indentation) with
    ``>``. ``missing-space`` is reported when a ``>`` marker is glued to its
    content, and ``extra-space`` when two or more spaces follow a marker before
    non-blank content. Bare ``>`` lines and lines inside fenced code blocks are
    not flagged. Results are ordered by line.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    issues: list[BlockquoteIssue] = []
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

        if not _QUOTE_LINE.match(line):
            continue
        kind = _classify(line)
        if kind is None:
            continue
        message = (
            "blockquote marker '>' is not followed by a space"
            if kind == "missing-space"
            else "blockquote marker '>' is followed by more than one space"
        )
        issues.append(
            BlockquoteIssue(line=i + 1, kind=kind, text=line, message=message)
        )
    return issues


def is_consistent(text: str) -> bool:
    """Return ``True`` when every blockquote line uses the ``> `` marker."""
    return not check_blockquote_style(text)
