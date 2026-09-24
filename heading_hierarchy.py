"""Heading-hierarchy validation for book chapters.

A well-structured chapter uses heading levels like an outline: it starts at a
single top level and never jumps past a level (``##`` should not be followed
directly by ``####``). Skipped levels break document outlines, screen-reader
navigation and generated tables of contents, so they are a real accessibility
and quality defect worth catching in CI.

The heading list is obtained from :func:`chapter_outline.extract_outline`, which
already understands ATX and setext headings and ignores headings inside fenced
code blocks, so this module reuses that logic rather than re-parsing markdown.
"""
from __future__ import annotations

from dataclasses import dataclass

from chapter_outline import extract_outline


@dataclass(frozen=True)
class HierarchyIssue:
    """A single heading-hierarchy problem.

    ``line`` is the 1-based line of the offending heading, ``level`` its heading
    level, ``kind`` a short machine-readable code, and ``message`` a
    human-readable explanation.
    """

    line: int
    level: int
    kind: str
    message: str


def check_hierarchy(text: str, *, require_single_h1: bool = True) -> list[HierarchyIssue]:
    """Return the ordered heading-hierarchy issues in chapter ``text``.

    The following problems are reported:

    * ``first-not-top`` -- the first heading is not the shallowest level used,
      i.e. the chapter opens on a heading deeper than its own top level.
    * ``skipped-level`` -- a heading is more than one level deeper than the
      previous heading (for example ``##`` followed by ``####``).
    * ``multiple-h1`` -- more than one top-level heading exists and
      ``require_single_h1`` is true (a chapter should have one title).

    An empty list means the heading hierarchy is well-formed.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    headings = extract_outline(text)
    if not headings:
        return []

    issues: list[HierarchyIssue] = []
    top = min(h.level for h in headings)

    first = headings[0]
    if first.level != top:
        issues.append(
            HierarchyIssue(
                line=first.line,
                level=first.level,
                kind="first-not-top",
                message=(
                    f"first heading is level {first.level} but the chapter's "
                    f"top level is {top}"
                ),
            )
        )

    if require_single_h1:
        top_headings = [h for h in headings if h.level == top]
        for extra in top_headings[1:]:
            issues.append(
                HierarchyIssue(
                    line=extra.line,
                    level=extra.level,
                    kind="multiple-h1",
                    message=(
                        f"additional top-level (level {top}) heading "
                        f"'{extra.title}'; expected a single chapter title"
                    ),
                )
            )

    previous = headings[0].level
    for heading in headings[1:]:
        if heading.level > previous + 1:
            issues.append(
                HierarchyIssue(
                    line=heading.line,
                    level=heading.level,
                    kind="skipped-level",
                    message=(
                        f"heading '{heading.title}' jumps from level "
                        f"{previous} to {heading.level}"
                    ),
                )
            )
        previous = heading.level

    issues.sort(key=lambda issue: issue.line)
    return issues


def is_well_formed(text: str, *, require_single_h1: bool = True) -> bool:
    """Return ``True`` when ``text`` has no heading-hierarchy issues."""
    return not check_hierarchy(text, require_single_h1=require_single_h1)
