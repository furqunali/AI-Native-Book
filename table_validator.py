"""Validation for GitHub-Flavored-Markdown pipe tables.

A malformed table renders as a wall of pipe characters instead of a grid, which
is an obvious defect in a published book. This module finds pipe tables in a
document (skipping fenced code blocks so table-like ASCII art in a code sample
is ignored) and checks each one for the structural rules GitHub enforces:

* a header row must be followed by a delimiter row of ``---`` / ``:--:`` cells,
* the delimiter row must have the same number of columns as the header, and
* every body row must have the same number of columns as the header.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_DELIMITER_CELL = re.compile(r"^:?-+:?$")


@dataclass(frozen=True)
class TableIssue:
    """A structural problem with a markdown table.

    ``line`` is the 1-based line where the problem was detected, ``kind`` a short
    code and ``message`` a human-readable explanation.
    """

    line: int
    kind: str
    message: str


def _split_row(line: str) -> list[str]:
    """Split a pipe-table row into trimmed cell values.

    Leading and trailing pipes are optional in GFM, so a single leading and
    trailing empty cell (produced by an outer pipe) is discarded. Escaped pipes
    (``\\|``) are not treated as column separators.
    """
    placeholder = "\x00"
    protected = line.replace("\\|", placeholder)
    cells = protected.split("|")
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [cell.replace(placeholder, "|").strip() for cell in cells]


def _is_delimiter_row(cells: list[str]) -> bool:
    """Return ``True`` when every cell matches a table delimiter pattern."""
    return bool(cells) and all(_DELIMITER_CELL.match(cell) for cell in cells)


def _looks_like_table_row(line: str) -> bool:
    """Return ``True`` when a non-fenced line looks like a table row."""
    stripped = line.strip()
    return "|" in stripped and not stripped.startswith(">")


def validate_tables(text: str) -> list[TableIssue]:
    """Return the ordered structural issues for every pipe table in ``text``.

    Lines inside fenced code blocks are ignored. Runs of consecutive
    table-looking lines are treated as one table candidate; a candidate is only
    validated as a table when its second line is a delimiter row, which is how
    GitHub distinguishes a real table from prose that merely contains pipes.
    An empty list means all tables are well-formed.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    issues: list[TableIssue] = []
    lines = text.splitlines()
    fence: str | None = None
    block: list[tuple[int, str]] = []

    def _flush(block: list[tuple[int, str]]) -> None:
        if len(block) < 2:
            return
        _header_no, header_line = block[0]
        delim_no, delim_line = block[1]
        delim_cells = _split_row(delim_line)
        if not _is_delimiter_row(delim_cells):
            return  # not actually a table; just pipes in prose
        expected = len(_split_row(header_line))
        if len(delim_cells) != expected:
            issues.append(
                TableIssue(
                    line=delim_no,
                    kind="delimiter-column-mismatch",
                    message=(
                        f"delimiter row has {len(delim_cells)} columns but "
                        f"the header has {expected}"
                    ),
                )
            )
        for row_no, row_line in block[2:]:
            count = len(_split_row(row_line))
            if count != expected:
                issues.append(
                    TableIssue(
                        line=row_no,
                        kind="row-column-mismatch",
                        message=(
                            f"row has {count} columns but the header has "
                            f"{expected}"
                        ),
                    )
                )

    for i, line in enumerate(lines):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                _flush(block)
                block = []
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        if _looks_like_table_row(line):
            block.append((i + 1, line))
        else:
            _flush(block)
            block = []

    _flush(block)
    issues.sort(key=lambda issue: issue.line)
    return issues


def has_valid_tables(text: str) -> bool:
    """Return ``True`` when every table in ``text`` is structurally valid."""
    return not validate_tables(text)
