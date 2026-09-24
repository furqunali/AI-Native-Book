"""Front-matter (YAML metadata) parsing and validation for Markdown documents.

Many static-site and book toolchains expect each chapter to open with a
front-matter block delimited by ``---`` lines, carrying flat metadata such as
``title``, ``author`` and ``order``. Missing, malformed or incomplete metadata
breaks navigation and builds, so it is worth validating deterministically.

The parser targets the flat ``key: value`` scalar form that book front matter
almost always uses; it does not attempt full YAML (nested maps, lists, anchors),
and lines it cannot parse as ``key: value`` are reported rather than silently
dropped.
"""
from __future__ import annotations

from dataclasses import dataclass

_DELIMITER = "---"


@dataclass(frozen=True)
class FrontMatterIssue:
    """A problem found while validating a document's front matter.

    ``line`` is the 1-based line number the issue relates to (0 when it concerns
    the document as a whole), ``kind`` a short code and ``message`` a
    human-readable explanation.
    """

    line: int
    kind: str
    message: str


def parse_front_matter(text: str) -> tuple[dict[str, str] | None, list[FrontMatterIssue]]:
    """Parse the leading front-matter block of ``text``.

    Returns a ``(metadata, issues)`` pair. ``metadata`` is ``None`` when the
    document has no front-matter block at all, otherwise a dict of the parsed
    ``key: value`` entries (later duplicates overwrite earlier ones, and each
    duplicate is also reported as an issue). ``issues`` collects structural
    problems such as an unterminated block, malformed lines, duplicate keys and
    empty values.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    lines = text.splitlines()
    if not lines or lines[0].strip() != _DELIMITER:
        return None, []

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == _DELIMITER:
            end = i
            break

    issues: list[FrontMatterIssue] = []
    if end is None:
        issues.append(
            FrontMatterIssue(
                line=1,
                kind="unterminated",
                message="front-matter block is opened but never closed",
            )
        )
        end = len(lines)

    metadata: dict[str, str] = {}
    for i in range(1, end):
        raw = lines[i]
        if raw.strip() == "" or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            issues.append(
                FrontMatterIssue(
                    line=i + 1,
                    kind="malformed-line",
                    message=f"line is not 'key: value': {raw.strip()!r}",
                )
            )
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            issues.append(
                FrontMatterIssue(
                    line=i + 1,
                    kind="malformed-line",
                    message="empty key before ':'",
                )
            )
            continue
        if key in metadata:
            issues.append(
                FrontMatterIssue(
                    line=i + 1,
                    kind="duplicate-key",
                    message=f"duplicate key '{key}'",
                )
            )
        if value == "":
            issues.append(
                FrontMatterIssue(
                    line=i + 1,
                    kind="empty-value",
                    message=f"key '{key}' has an empty value",
                )
            )
        metadata[key] = value

    return metadata, issues


def validate_front_matter(
    text: str, *, required: tuple[str, ...] = ()
) -> list[FrontMatterIssue]:
    """Return the front-matter issues for ``text``, including missing required keys.

    In addition to the structural checks performed by :func:`parse_front_matter`,
    every name in ``required`` must be present as a key. If the document has no
    front-matter block at all and ``required`` is non-empty, a single
    ``missing-block`` issue is returned. An empty list means the front matter is
    valid and complete.
    """
    metadata, issues = parse_front_matter(text)
    if metadata is None:
        if required:
            return [
                FrontMatterIssue(
                    line=0,
                    kind="missing-block",
                    message="document has no front-matter block",
                )
            ]
        return []

    for key in required:
        if key not in metadata:
            issues.append(
                FrontMatterIssue(
                    line=0,
                    kind="missing-key",
                    message=f"required key '{key}' is missing",
                )
            )

    issues.sort(key=lambda issue: (issue.line, issue.kind))
    return issues
