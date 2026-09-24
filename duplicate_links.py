"""Detection of inconsistent link text for the same URL.

When one destination is linked under several different anchor texts -- ``[the
docs](x)`` in one place and ``[click here](x)`` in another -- readers cannot
tell the links point to the same page, and the inconsistency looks careless.
This module collects every inline markdown link, groups them by destination
URL, and reports any URL that is linked under two or more distinct texts.

Only inline links (``[text](url)``) are parsed. Reference-style links and
autolinks are out of scope. Links inside fenced code blocks are ignored.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_LINK = re.compile(r"\[([^\]]+)\]\(\s*(\S+?)(?:\s+\"[^\"]*\")?\s*\)")


@dataclass(frozen=True)
class LinkUse:
    """A single inline link occurrence.

    ``text`` is the anchor text, ``url`` the destination, and ``line`` the
    1-based line number.
    """

    text: str
    url: str
    line: int


@dataclass(frozen=True)
class DuplicateLink:
    """A URL linked under two or more distinct anchor texts.

    ``url`` is the shared destination, ``texts`` the distinct anchor texts in
    first-seen order, and ``uses`` every occurrence contributing to the group.
    """

    url: str
    texts: tuple[str, ...]
    uses: tuple[LinkUse, ...]


def extract_links(text: str) -> list[LinkUse]:
    """Return every inline markdown link in ``text``, in document order.

    Anchor text and destination are trimmed of surrounding whitespace, and an
    optional link title (``(url "title")``) is discarded. Links inside fenced
    code blocks are skipped.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    uses: list[LinkUse] = []
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
        for m in _LINK.finditer(line):
            uses.append(
                LinkUse(text=m.group(1).strip(), url=m.group(2).strip(), line=i + 1)
            )
    return uses


def find_duplicate_links(text: str) -> list[DuplicateLink]:
    """Return URLs in ``text`` linked under two or more distinct anchor texts.

    Links are grouped by exact destination URL. A group is reported only when it
    contains at least two *different* anchor texts (repeating the same text for
    the same URL is fine). Groups are ordered by the line of the URL's first
    occurrence; within a group ``texts`` preserves first-seen order. An empty
    list means all links to a given URL agree on their text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    groups: dict[str, list[LinkUse]] = {}
    order: list[str] = []
    for use in extract_links(text):
        if use.url not in groups:
            groups[use.url] = []
            order.append(use.url)
        groups[use.url].append(use)

    duplicates: list[DuplicateLink] = []
    for url in order:
        uses = groups[url]
        distinct: list[str] = []
        for use in uses:
            if use.text not in distinct:
                distinct.append(use.text)
        if len(distinct) >= 2:
            duplicates.append(
                DuplicateLink(
                    url=url, texts=tuple(distinct), uses=tuple(uses)
                )
            )
    return duplicates


def has_duplicate_links(text: str) -> bool:
    """Return ``True`` when some URL is linked under multiple distinct texts."""
    return bool(find_duplicate_links(text))
