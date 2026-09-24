"""Alt-text auditing for images in Markdown documents.

Every image in an accessible book needs meaningful alternative text so screen
readers can describe it and search indexes can label it. This module finds both
Markdown images (``![alt](src)`` and reference form ``![alt][id]``) and inline
HTML ``<img>`` tags, then flags the ones whose alt text is missing, empty, or a
low-value placeholder such as ``image`` or ``screenshot``.

Fenced code blocks are skipped so image syntax shown inside a code sample is not
audited as a real image.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_MD_IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]*)\)")
_MD_REF_IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\[(?P<ref>[^\]]*)\]")
_HTML_IMG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_HTML_ALT = re.compile(r"""\balt\s*=\s*("([^"]*)"|'([^']*)')""", re.IGNORECASE)
_HTML_SRC = re.compile(r"""\bsrc\s*=\s*("([^"]*)"|'([^']*)')""", re.IGNORECASE)

_PLACEHOLDERS = frozenset(
    {"image", "img", "picture", "photo", "screenshot", "figure", "graphic"}
)


@dataclass(frozen=True)
class AltIssue:
    """An image whose alt text fails the audit.

    ``line`` is the 1-based line of the image, ``src`` its source (best effort),
    ``kind`` one of ``missing``, ``empty`` or ``placeholder``, and ``message`` a
    human-readable explanation.
    """

    line: int
    src: str
    kind: str
    message: str


def _classify(alt: str | None, src: str) -> tuple[str, str] | None:
    """Return an ``(kind, message)`` for a bad alt value, or ``None`` if fine."""
    if alt is None:
        return "missing", f"image '{src}' has no alt attribute"
    if alt.strip() == "":
        return "empty", f"image '{src}' has empty alt text"
    if alt.strip().lower() in _PLACEHOLDERS:
        return "placeholder", (
            f"image '{src}' uses placeholder alt text '{alt.strip()}'"
        )
    return None


def _iter_content_lines(text: str):
    """Yield ``(line_no, line)`` for lines outside fenced code blocks."""
    fence: str | None = None
    for i, line in enumerate(text.splitlines()):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            yield i + 1, line
        elif line.lstrip().startswith(fence):
            fence = None


def audit_alt_text(text: str) -> list[AltIssue]:
    """Return the ordered alt-text issues for images in ``text``.

    Markdown inline images, Markdown reference images and inline HTML ``<img>``
    tags are all inspected. An image is reported when its alt text is missing
    (HTML only), empty, or a generic placeholder word. An empty list means every
    image has meaningful alt text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    issues: list[AltIssue] = []
    for line_no, line in _iter_content_lines(text):
        for match in _MD_IMAGE.finditer(line):
            src = match.group("src").strip()
            result = _classify(match.group("alt"), src or "(no src)")
            if result:
                issues.append(AltIssue(line_no, src, result[0], result[1]))
        for match in _MD_REF_IMAGE.finditer(line):
            ref = match.group("ref").strip()
            result = _classify(match.group("alt"), f"[{ref}]")
            if result:
                issues.append(AltIssue(line_no, f"[{ref}]", result[0], result[1]))
        for match in _HTML_IMG.finditer(line):
            tag = match.group(0)
            src_match = _HTML_SRC.search(tag)
            src = ""
            if src_match:
                src = (src_match.group(2) or src_match.group(3) or "").strip()
            alt_match = _HTML_ALT.search(tag)
            alt = None
            if alt_match:
                double, single = alt_match.group(2), alt_match.group(3)
                alt = double if double is not None else single
            result = _classify(alt, src or "(no src)")
            if result:
                issues.append(AltIssue(line_no, src, result[0], result[1]))

    issues.sort(key=lambda issue: issue.line)
    return issues


def all_images_have_alt(text: str) -> bool:
    """Return ``True`` when every image in ``text`` passes the alt-text audit."""
    return not audit_alt_text(text)
