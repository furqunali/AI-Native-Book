"""Detection of bare (unwrapped) URLs in Markdown documents.

A bare URL is an ``http``/``https`` address pasted into prose as plain text
rather than wrapped in markdown link syntax (``[text](url)``) or an autolink
(``<url>``). Bare URLs render inconsistently, cannot carry descriptive link
text, and often break when a trailing sentence period is glued onto them, so
flagging them keeps a book's links tidy and accessible.

Inline code spans and fenced code blocks are ignored, because a URL shown in a
command example is meant to be literal text, not a link.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")
_URL = re.compile(r"https?://[^\s<>()\[\]]+")


@dataclass(frozen=True)
class BareURL:
    """A bare URL occurrence.

    ``line`` is the 1-based line number, ``column`` the 1-based column where the
    URL starts, and ``url`` the matched address with any trailing sentence
    punctuation removed.
    """

    line: int
    column: int
    url: str


def _blank_code_spans(line: str) -> str:
    """Replace inline code spans with spaces, preserving column positions."""
    return _CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line)


def find_bare_urls(text: str) -> list[BareURL]:
    """Return the bare URLs in ``text``, ordered by line then column.

    A URL is considered bare unless it is the destination of a markdown link
    (immediately preceded by ``](``) or enclosed in an autolink (``<url>``).
    Trailing ``.,;:!?`` and a single closing paren are trimmed from the reported
    URL so a sentence-final address is not reported with its period. URLs in
    inline code or fenced code blocks are not reported. An empty list means the
    document has no bare URLs.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    results: list[BareURL] = []
    fence: str | None = None
    for i, raw in enumerate(text.splitlines()):
        match = _FENCE.match(raw)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
        else:
            if raw.lstrip().startswith(fence):
                fence = None
            continue

        line = _blank_code_spans(raw)
        for m in _URL.finditer(line):
            start = m.start()
            url = m.group(0).rstrip(".,;:!?").rstrip(")")

            # Autolink: <https://...>
            if start > 0 and line[start - 1] == "<":
                continue
            # Markdown link destination: ](https://...)
            if start >= 2 and line[start - 2:start] == "](":
                continue

            results.append(BareURL(line=i + 1, column=start + 1, url=url))
    return results


def has_bare_urls(text: str) -> bool:
    """Return ``True`` when ``text`` contains at least one bare URL."""
    return bool(find_bare_urls(text))
