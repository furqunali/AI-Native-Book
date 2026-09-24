"""Detection of figures that are missing a caption.

A standalone image in a book should be followed by a caption so the reader knows
what they are looking at and so print/PDF renderers can label the figure. This
module finds images that sit on their own line and checks the next non-blank
line: a caption is recognised when it is fully italicised (``*text*`` or
``_text_``) or begins with a configurable prefix such as ``Figure`` or
``Caption``. Images that appear inline within a sentence are ignored, since they
are decorative rather than figures.

Images inside fenced code blocks are skipped so example markdown in a code
sample is never flagged.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]*)\)")
_ITALIC = re.compile(r"^(?:\*[^*]+\*|_[^_]+_)$")

_DEFAULT_PREFIXES: tuple[str, ...] = ("figure", "fig.", "fig ", "caption", "table")


@dataclass(frozen=True)
class CaptionIssue:
    """An image that lacks a recognisable caption.

    ``line`` is the 1-based line of the image, ``alt`` its alt text, ``target``
    its link target and ``message`` a human-readable explanation.
    """

    line: int
    alt: str
    target: str
    message: str


def _is_caption(line: str, prefixes: tuple[str, ...]) -> bool:
    """Return ``True`` when ``line`` reads as a figure caption."""
    stripped = line.strip()
    if not stripped:
        return False
    if _ITALIC.match(stripped):
        return True
    lowered = stripped.lower()
    return any(lowered.startswith(prefix) for prefix in prefixes)


def find_uncaptioned(
    text: str,
    *,
    caption_prefixes: tuple[str, ...] = _DEFAULT_PREFIXES,
) -> list[CaptionIssue]:
    """Return the standalone images in ``text`` that lack a caption.

    An image is considered standalone when it is the only content on its line.
    The first non-blank line after it must be a caption -- italicised text or a
    line starting with one of ``caption_prefixes`` (matched case-insensitively).
    A standalone image at end of document, or followed only by blank lines,
    ordinary prose or another image, is reported. Inline images (embedded in a
    sentence) and images inside fenced code are never reported. The result is
    ordered by line number.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    prefixes = tuple(p.lower() for p in caption_prefixes)

    lines = text.splitlines()
    fence: str | None = None
    issues: list[CaptionIssue] = []

    for i, line in enumerate(lines):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        stripped = line.strip()
        image = _IMAGE.fullmatch(stripped)
        if image is None:
            continue  # not a standalone image line

        # Find the next non-blank line after the image.
        caption_line = None
        for follow in lines[i + 1:]:
            if follow.strip() == "":
                continue
            caption_line = follow
            break

        if caption_line is None or not _is_caption(caption_line, prefixes):
            issues.append(
                CaptionIssue(
                    line=i + 1,
                    alt=image.group("alt"),
                    target=image.group("target"),
                    message="image is not followed by a caption",
                )
            )

    return issues


def is_fully_captioned(
    text: str,
    *,
    caption_prefixes: tuple[str, ...] = _DEFAULT_PREFIXES,
) -> bool:
    """Return ``True`` when every standalone image in ``text`` has a caption."""
    return not find_uncaptioned(text, caption_prefixes=caption_prefixes)
