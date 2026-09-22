"""Heading-outline and table-of-contents extraction for book chapters.

Headings are read the way a reader (and GitHub) sees them: fenced code blocks
are skipped so a ``#`` in a shell snippet is never mistaken for a heading, both
ATX (``## Heading``) and setext (underlined) headings are recognised, inline
markdown in a heading title is reduced to plain text, and each heading is given
a GitHub-style anchor slug with duplicate titles disambiguated by a numeric
suffix.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^\s{0,3}(#{1,6})(?:\s+(.*?))?\s*$")
_ATX_CLOSING = re.compile(r"\s+#+\s*$")
_SETEXT_UNDERLINE = re.compile(r"^\s{0,3}(=+|-+)\s*$")
_SLUG_STRIP = re.compile(r"[^\w\s-]")
_SLUG_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class Heading:
    """A single heading found in a chapter.

    ``level`` is 1-6, ``title`` is the plain-text heading with markdown removed,
    ``slug`` is the GitHub-style anchor, and ``line`` is the 1-based line number
    of the heading (the text line for setext headings).
    """

    level: int
    title: str
    slug: str
    line: int


def _strip_inline(text: str) -> str:
    """Reduce a heading's inline markdown to plain text.

    Link/image targets are dropped while their visible text is kept, and inline
    code and emphasis markers are removed.
    """
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    return text.strip()


def slugify(title: str) -> str:
    """Return a GitHub-style anchor slug for a heading ``title``.

    The title is lowercased, punctuation other than word characters, spaces and
    hyphens is removed, and internal whitespace is collapsed to single hyphens.
    """
    slug = _SLUG_STRIP.sub("", title.lower())
    slug = _SLUG_SPACE.sub("-", slug.strip())
    return slug


def extract_outline(text: str) -> list[Heading]:
    """Extract the ordered heading outline from chapter ``text``.

    Both ATX (``# Heading``) and setext (a text line underlined with ``===`` or
    ``---``) headings are recognised. Headings inside fenced code blocks are
    ignored. Duplicate slugs are disambiguated with ``-1``, ``-2`` suffixes in
    order of appearance, matching GitHub's anchor generation.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    headings: list[Heading] = []
    seen: dict[str, int] = {}
    lines = text.splitlines()
    fence: str | None = None

    def _record(level: int, raw_title: str, line_no: int) -> None:
        title = _strip_inline(raw_title)
        if not title:
            return
        base = slugify(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        slug = base if count == 0 else f"{base}-{count}"
        headings.append(Heading(level=level, title=title, slug=slug, line=line_no))

    for i, line in enumerate(lines):
        fence_match = _FENCE.match(line)
        if fence is None:
            if fence_match:
                fence = fence_match.group(1)
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        atx = _ATX.match(line)
        if atx:
            level = len(atx.group(1))
            raw = atx.group(2) or ""
            raw = _ATX_CLOSING.sub("", raw).strip()
            _record(level, raw, i + 1)
            continue

        # Setext: a non-blank text line followed by an underline of = or -.
        underline = _SETEXT_UNDERLINE.match(line)
        if underline and i > 0:
            prev = lines[i - 1]
            prev_stripped = prev.strip()
            if (
                prev_stripped
                and not _ATX.match(prev)
                and not _FENCE.match(prev)
                and not _SETEXT_UNDERLINE.match(prev)
                and not prev_stripped.startswith(("-", "*", "+", ">"))
            ):
                level = 1 if underline.group(1).startswith("=") else 2
                _record(level, prev_stripped, i)

    return headings


def render_toc(text: str, *, min_level: int = 1, max_level: int = 6) -> str:
    """Render a markdown table of contents for chapter ``text``.

    Only headings whose level is between ``min_level`` and ``max_level``
    (inclusive) are included. The list is indented relative to the shallowest
    included heading so a chapter that starts at ``##`` is not over-indented,
    and each entry links to the heading's anchor slug. An empty string is
    returned when no headings fall in range.
    """
    if not isinstance(min_level, int) or isinstance(min_level, bool):
        raise TypeError("min_level must be an int")
    if not isinstance(max_level, int) or isinstance(max_level, bool):
        raise TypeError("max_level must be an int")
    if not 1 <= min_level <= 6:
        raise ValueError("min_level must be between 1 and 6")
    if not 1 <= max_level <= 6:
        raise ValueError("max_level must be between 1 and 6")
    if min_level > max_level:
        raise ValueError("min_level must not exceed max_level")

    selected = [
        h for h in extract_outline(text) if min_level <= h.level <= max_level
    ]
    if not selected:
        return ""

    base = min(h.level for h in selected)
    lines = [
        f"{'  ' * (h.level - base)}- [{h.title}](#{h.slug})" for h in selected
    ]
    return "\n".join(lines)
