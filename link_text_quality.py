"""Detection of non-descriptive link text in Markdown.

Link text should describe the destination so it makes sense out of context --
this matters for screen-reader users, who often navigate by jumping between
links, and for skim-readers. Generic phrases such as "click here", "here",
"this" or "read more" fail that test. This module extracts inline links and
flags any whose visible text is one of a configurable set of low-quality
phrases.

Image links (``![alt](url)``) are ignored because their alt text is audited
elsewhere, and links inside fenced code blocks or inline code are skipped.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")
# A link that is not preceded by '!' (so images are excluded).
_LINK = re.compile(r"(?<!\!)\[(?P<text>[^\]]+)\]\((?P<target>[^)]*)\)")

# Phrases that carry no information about the destination.
DEFAULT_BAD_PHRASES: frozenset[str] = frozenset(
    {
        "click here", "here", "this", "link", "this link", "read more",
        "more", "learn more", "see here", "go here", "click", "this page",
        "page", "download",
    }
)


@dataclass(frozen=True)
class LinkTextIssue:
    """A link whose visible text is non-descriptive.

    ``line`` is the 1-based line number, ``text`` the visible link text,
    ``target`` the link destination and ``message`` a human-readable
    explanation.
    """

    line: int
    text: str
    target: str
    message: str


def _normalise(text: str) -> str:
    """Lowercase, strip surrounding punctuation/whitespace and collapse spaces."""
    stripped = text.strip().strip(".,!?:;\"'()")
    return re.sub(r"\s+", " ", stripped).lower()


def check_link_text(
    text: str,
    *,
    bad_phrases: frozenset[str] | set[str] = DEFAULT_BAD_PHRASES,
) -> list[LinkTextIssue]:
    """Return the links in ``text`` with non-descriptive visible text.

    The visible text of each inline link is normalised (lowercased, trimmed of
    surrounding punctuation, internal whitespace collapsed) and compared against
    ``bad_phrases``. Matches are reported in document order. Fenced code, inline
    code spans and image links are ignored. An empty list means every link has
    descriptive text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    phrases = {p.lower() for p in bad_phrases}

    issues: list[LinkTextIssue] = []
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

        cleaned = _CODE_SPAN.sub("", line)
        for m in _LINK.finditer(cleaned):
            visible = m.group("text")
            if _normalise(visible) in phrases:
                issues.append(
                    LinkTextIssue(
                        line=i + 1,
                        text=visible,
                        target=m.group("target"),
                        message=f"non-descriptive link text: {visible!r}",
                    )
                )

    return issues


def is_descriptive(
    text: str,
    *,
    bad_phrases: frozenset[str] | set[str] = DEFAULT_BAD_PHRASES,
) -> bool:
    """Return ``True`` when no link in ``text`` has non-descriptive text."""
    return not check_link_text(text, bad_phrases=bad_phrases)
