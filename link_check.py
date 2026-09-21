"""Deterministic, offline Markdown link and cross-reference validation.

The book ships as a set of Markdown chapters plus a README. Broken internal
links and stale section anchors are a real quality defect for a published
handbook, but nothing in the toolchain checked for them. This module fills that
gap using only the local filesystem, so it is safe and reproducible in CI (no
network access, no external services).

Inline links of the form ``[text](target)`` are extracted, classified, and
validated:

* External links (``http://``, ``https://``, ``mailto:`` and other schemes, or
  protocol-relative ``//host``) are recorded but never fetched, keeping the
  check offline and deterministic.
* Internal file links are resolved relative to the linking document and flagged
  when the target file does not exist inside the project root.
* Anchor links (``#section`` in the same document, or ``file.md#section`` into
  another) are validated against the GitHub-style heading slugs of the target
  document.

Fenced code blocks are stripped before extraction (reusing
``chapter_validation._strip_fenced_code``) so link-like syntax inside code
samples never produces false positives.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from chapter_validation import _strip_fenced_code

# Inline link: [label](target "optional title"). The label is non-greedy and
# must not be an image (no leading '!'). The target is the first whitespace-
# delimited token, so an optional title is ignored.
_INLINE_LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(\s*([^)\s]*)(?:\s+\"[^\"]*\")?\s*\)")
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
# A scheme-qualified target (``https:``, ``mailto:``, ...) or a protocol-
# relative URL (``//host``) is treated as external.
_EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|//)")


@dataclass(frozen=True)
class Link:
    """A single inline Markdown link discovered in a document."""

    source: str
    target: str
    path: str
    anchor: str
    external: bool


@dataclass(frozen=True)
class LinkIssue:
    """A broken or invalid link finding."""

    source: str
    target: str
    code: str
    message: str


@dataclass(frozen=True)
class LinkReport:
    """Aggregated result of scanning one or more Markdown documents."""

    documents: int
    links: int
    external: int
    internal: int
    issues: tuple[LinkIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict:
        data = asdict(self)
        data["valid"] = self.valid
        return data


def slugify(heading: str) -> str:
    """Return the GitHub-style anchor slug for a heading's text.

    Inline code backticks and link wrappers are stripped first so a heading such
    as ``` ## The `RAG` Pattern ``` slugs to ``the-rag-pattern``. Matching
    GitHub: lowercase, drop characters that are not word characters, spaces or
    hyphens, then collapse whitespace to single hyphens.
    """
    text = heading.strip()
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    # GitHub replaces each whitespace character with a hyphen and does not
    # collapse runs, so "a — b" (with the em dash removed) slugs to "a--b".
    return re.sub(r"\s", "-", text)


def extract_headings(text: str) -> tuple[str, ...]:
    """Return the ordered heading slugs for a Markdown document.

    Fenced code is removed first so ``#`` inside code samples is not mistaken
    for a heading. Duplicate slugs are de-duplicated in document order.
    """
    body = _strip_fenced_code(text)
    slugs: list[str] = []
    for line in body.splitlines():
        match = _HEADING.match(line)
        if not match:
            continue
        slug = slugify(match.group(2))
        if slug:
            slugs.append(slug)
    return tuple(dict.fromkeys(slugs))


def parse_target(target: str) -> tuple[str, str]:
    """Split a link target into its file path and anchor (without ``#``)."""
    path, _, anchor = target.partition("#")
    return path, anchor


def parse_links(source: str, text: str) -> tuple[Link, ...]:
    """Extract and classify every inline link in a document's text."""
    body = _strip_fenced_code(text)
    links: list[Link] = []
    for target in _INLINE_LINK.findall(body):
        external = bool(_EXTERNAL.match(target))
        path, anchor = parse_target(target)
        links.append(Link(source=source, target=target, path=path, anchor=anchor, external=external))
    return tuple(links)


def _load_headings(path: Path, cache: dict[Path, tuple[str, ...]]) -> tuple[str, ...] | None:
    if path in cache:
        return cache[path]
    try:
        headings = extract_headings(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None
    cache[path] = headings
    return headings


def check_document(
    path: Path,
    root: Path,
    *,
    text: str | None = None,
    _cache: dict[Path, tuple[str, ...]] | None = None,
) -> tuple[tuple[Link, ...], tuple[LinkIssue, ...]]:
    """Validate the links in a single document.

    ``path`` is the document on disk; ``root`` is the project root that internal
    links are confined to. Returns the parsed links and any issues found, both
    in document order.
    """
    root = root.resolve()
    if text is None:
        text = path.read_text(encoding="utf-8")
    try:
        source = str(path.resolve().relative_to(root)).replace("\\", "/")
    except ValueError:
        source = path.name
    cache = _cache if _cache is not None else {}
    cache[path.resolve()] = extract_headings(text)

    links = parse_links(source, text)
    issues: list[LinkIssue] = []
    for link in links:
        if link.external:
            continue
        if not link.path and not link.anchor:
            issues.append(LinkIssue(source, link.target, "EMPTY_TARGET", "link target is empty"))
            continue

        if link.path:
            target_path = (path.parent / link.path).resolve()
            if not target_path.exists():
                issues.append(
                    LinkIssue(source, link.target, "MISSING_FILE", f"linked file does not exist: {link.path}")
                )
                continue
        else:
            target_path = path.resolve()

        if link.anchor:
            if target_path.is_dir() or target_path.suffix.lower() not in {".md", ".markdown"}:
                # Anchors are only meaningful for Markdown targets; skip others.
                continue
            headings = _load_headings(target_path, cache)
            if headings is None:
                issues.append(
                    LinkIssue(source, link.target, "MISSING_FILE", f"linked file does not exist: {link.path}")
                )
            elif link.anchor.lower() not in {slug.lower() for slug in headings}:
                issues.append(
                    LinkIssue(source, link.target, "MISSING_ANCHOR", f"no heading matches anchor: #{link.anchor}")
                )

    return links, tuple(issues)


def _iter_documents(root: Path) -> list[Path]:
    docs = sorted(root.glob("Chapter*.md"))
    readme = root / "README.md"
    if readme.exists():
        docs.append(readme)
    return docs


def check_links(root: Path, documents: list[Path] | None = None) -> LinkReport:
    """Scan the book's Markdown documents and aggregate link findings.

    By default this covers ``Chapter*.md`` and ``README.md`` under ``root``. Pass
    ``documents`` to scan an explicit set of files instead.
    """
    root = root.resolve()
    paths = documents if documents is not None else _iter_documents(root)
    cache: dict[Path, tuple[str, ...]] = {}

    total_links = 0
    external = 0
    all_issues: list[LinkIssue] = []
    for path in paths:
        links, issues = check_document(path, root, _cache=cache)
        total_links += len(links)
        external += sum(1 for link in links if link.external)
        all_issues.extend(issues)

    return LinkReport(
        documents=len(paths),
        links=total_links,
        external=external,
        internal=total_links - external,
        issues=tuple(all_issues),
    )


def to_json(report: LinkReport) -> str:
    """Stable JSON contract for a link report."""
    return json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":"))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate Markdown links and cross-references")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true", help="emit the report as stable JSON")
    args = parser.parse_args(argv)

    report = check_links(args.root.resolve())
    if args.json:
        print(to_json(report))
    else:
        print(
            f"documents={report.documents} links={report.links} "
            f"external={report.external} internal={report.internal} issues={len(report.issues)}"
        )
        for issue in report.issues:
            print(f"  [{issue.code}] {issue.source} -> {issue.target}: {issue.message}")
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
