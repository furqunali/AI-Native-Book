"""Table-of-contents generation from ATX headings.

This module reads the ATX headings (``# Title``, ``## Section`` …) of a chapter
and produces a structured table of contents: for each heading it records the
level, the plain-text title (with inline markdown stripped) and a GitHub-style
anchor slug, disambiguating duplicate slugs with numeric suffixes exactly as
GitHub does. It can also render that structure as a nested markdown list.

Headings inside fenced code blocks are ignored so a ``#`` in a shell snippet is
never mistaken for a heading. Only ATX headings are recognised; setext
(underline) headings are out of scope for this generator.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^\s{0,3}(#{1,6})(?:\s+(.*?))?\s*$")
_ATX_CLOSING = re.compile(r"\s+#+\s*$")
_SLUG_STRIP = re.compile(r"[^\w\s-]")
_SLUG_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class TocEntry:
    """A single table-of-contents entry.

    ``level`` is the heading level (1-6), ``text`` the plain-text title,
    ``slug`` the GitHub-style anchor, and ``line`` the 1-based source line.
    """

    level: int
    text: str
    slug: str
    line: int


def _strip_inline(raw: str) -> str:
    """Reduce a heading's inline markdown to plain text."""
    raw = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", raw)
    raw = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", raw)
    raw = re.sub(r"`([^`]*)`", r"\1", raw)
    raw = re.sub(r"[*_~]", "", raw)
    return raw.strip()


def slugify(title: str) -> str:
    """Return a GitHub-style anchor slug for a heading ``title``."""
    slug = _SLUG_STRIP.sub("", title.lower())
    return _SLUG_SPACE.sub("-", slug.strip())


def generate_toc(
    text: str,
    *,
    min_level: int = 1,
    max_level: int = 6,
) -> list[TocEntry]:
    """Return the table-of-contents entries for chapter ``text``.

    Only ATX headings whose level is between ``min_level`` and ``max_level``
    (inclusive) are included, but slug disambiguation considers *all* headings so
    anchors match the ones GitHub actually generates. Headings inside fenced code
    blocks and headings with empty titles are skipped. Entries are returned in
    document order.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    for name, value in (("min_level", min_level), ("max_level", max_level)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an int")
        if not 1 <= value <= 6:
            raise ValueError(f"{name} must be between 1 and 6")
    if min_level > max_level:
        raise ValueError("min_level must not exceed max_level")

    entries: list[TocEntry] = []
    seen: dict[str, int] = {}
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

        atx = _ATX.match(line)
        if not atx:
            continue
        level = len(atx.group(1))
        title = _strip_inline(_ATX_CLOSING.sub("", atx.group(2) or "").strip())
        if not title:
            continue

        base = slugify(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        slug = base if count == 0 else f"{base}-{count}"

        if min_level <= level <= max_level:
            entries.append(
                TocEntry(level=level, text=title, slug=slug, line=i + 1)
            )
    return entries


def render_toc(text: str, *, min_level: int = 1, max_level: int = 6) -> str:
    """Render the chapter's table of contents as a nested markdown list.

    Indentation is relative to the shallowest included heading, and each entry
    links to its anchor slug. Returns an empty string when no headings fall in
    the requested level range.
    """
    entries = generate_toc(text, min_level=min_level, max_level=max_level)
    if not entries:
        return ""
    base = min(e.level for e in entries)
    lines = [
        f"{'  ' * (e.level - base)}- [{e.text}](#{e.slug})" for e in entries
    ]
    return "\n".join(lines)
