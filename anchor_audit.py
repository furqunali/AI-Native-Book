"""Deterministic, offline validation of *intra-document* Markdown anchors.

The book links heavily within a single chapter -- a table of contents, "see the
section below" jumps, and reference-style footnote-like links. When a heading is
renamed or removed, those same-document ``#anchor`` links rot silently: the page
still renders, but the link scrolls nowhere. GitHub never warns about it.

``link_check`` already validates inline ``[text](target)`` links (including
cross-file anchors), so this module deliberately stays in the gap it leaves:

* It resolves the link *syntaxes* ``link_check`` ignores -- full reference links
  ``[text][ref]``, collapsed ``[text][]`` and shortcut ``[ref]`` links -- via
  their ``[ref]: target`` definitions.
* It recognises the anchor *targets* GitHub's auto-slugger is not the only source
  of: explicit ``{#custom-id}`` heading attributes and HTML ``id=``/``name=``
  attributes embedded in the Markdown.
* It reports the 1-based **line number** of every finding, which the aggregate
  file-existence checker does not track.
* It flags **ambiguous anchors** -- the same explicit id defined twice -- because
  a jump link to a duplicated id is a latent defect.

Scope is limited on purpose to *same-document* anchors (targets of the bare form
``#anchor`` with no file component); cross-file anchors remain ``link_check``'s
job. Everything is computed from local text only: no network, fully reproducible
in CI. Fenced and inline code are blanked (preserving line numbers) so link- and
heading-like syntax inside code samples never produces a false positive.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from link_check import slugify

# A Markdown heading, capturing the level marker and the trailing text.
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
# An explicit heading id attribute, e.g. ``## Setup {#install}`` (kramdown /
# Python-Markdown attr_list style). Only a lone ``{#id}`` at end of line counts.
_HEADING_ATTR = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
# HTML ``id="..."`` / ``name='...'`` attributes embedded in the Markdown.
_HTML_ANCHOR = re.compile(r"(?:\bid|\bname)\s*=\s*[\"']([^\"']+)[\"']")
# A reference-link definition: ``[label]: target "optional title"`` (<=3 indent).
_LINK_DEF = re.compile(r"^ {0,3}\[([^\]\n]+)\]:\s*(\S+)")
# Inline link ``[label](target)`` -- not an image, title token discarded.
_INLINE_LINK = re.compile(r"(?<!!)\[([^\]\n]*)\]\(\s*([^)\s]*)(?:\s+\"[^\"]*\")?\s*\)")
# Full/collapsed reference link ``[label][ref]`` (``ref`` may be empty).
_REF_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\[([^\]\n]*)\]")
# Shortcut reference link ``[ref]`` -- resolved only against known definitions.
_SHORTCUT_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\](?![\[(:])")
# Inline code span, blanked so its contents are never parsed.
_INLINE_CODE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class AnchorLink:
    """An intra-document anchor reference discovered in a document."""

    source: str
    anchor: str
    line: int
    kind: str  # "inline" | "reference" | "collapsed" | "shortcut"


@dataclass(frozen=True)
class AnchorIssue:
    """A broken, empty, undefined or ambiguous anchor finding."""

    source: str
    anchor: str
    line: int
    code: str
    message: str


@dataclass(frozen=True)
class AnchorReport:
    """Aggregated result of auditing one or more Markdown documents."""

    documents: int
    links: int
    issues: tuple[AnchorIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict:
        data = asdict(self)
        data["valid"] = self.valid
        return data


def _blank_code(text: str) -> list[str]:
    """Return ``text`` split into lines with all code content blanked out.

    Fenced blocks (``` ``` ``` or ``~~~``) and inline code spans are replaced by
    empty content, but every original line is preserved so that reported line
    numbers stay accurate. Returns the list of processed lines (never ``None``).
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    out: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith(("```", "~~~")):
                fence = stripped[:3]
                out.append("")
                continue
            out.append(_INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line))
        else:
            if stripped.startswith(fence):
                fence = None
            out.append("")
    return out


def collect_anchors(text: str) -> tuple[frozenset[str], frozenset[str]]:
    """Return ``(anchors, duplicates)`` for a document, both lower-cased.

    ``anchors`` is every anchor a same-document link may legitimately target:

    * GitHub-style auto-slugs of headings (with the usual ``-1``, ``-2`` suffixes
      for repeated slugs),
    * explicit ``{#custom-id}`` heading attributes, and
    * HTML ``id``/``name`` attributes.

    ``duplicates`` is the subset of *explicit* ids (heading attrs and HTML
    attributes) that are defined more than once and are therefore ambiguous jump
    targets. Auto-slug collisions are excluded because GitHub disambiguates them
    deterministically via numeric suffixes.
    """
    lines = _blank_code(text)
    anchors: set[str] = set()
    explicit_counts: dict[str, int] = {}
    slug_counts: dict[str, int] = {}

    for line in lines:
        for attr in _HTML_ANCHOR.findall(line):
            key = attr.lower()
            anchors.add(key)
            explicit_counts[key] = explicit_counts.get(key, 0) + 1

        match = _HEADING.match(line)
        if not match:
            continue
        heading_text = match.group(2)
        attr = _HEADING_ATTR.search(heading_text)
        if attr:
            heading_text = heading_text[: attr.start()]
            key = attr.group(1).lower()
            anchors.add(key)
            explicit_counts[key] = explicit_counts.get(key, 0) + 1
        base = slugify(heading_text)
        if not base:
            continue
        occurrence = slug_counts.get(base, 0)
        slug_counts[base] = occurrence + 1
        anchors.add(base if occurrence == 0 else f"{base}-{occurrence}")

    duplicates = frozenset(k for k, n in explicit_counts.items() if n > 1)
    return frozenset(anchors), duplicates


def parse_definitions(text: str) -> dict[str, str]:
    """Map each reference-link label (case-folded) to its target string.

    Labels are compared case-insensitively. When a label is defined more than
    once the last definition wins, so a corrected redefinition later in the file
    is honoured.
    """
    definitions: dict[str, str] = {}
    for line in _blank_code(text):
        match = _LINK_DEF.match(line)
        if match:
            definitions[match.group(1).strip().lower()] = match.group(2)
    return definitions


def _internal_anchor(target: str) -> str | None:
    """Return the anchor (without ``#``) if ``target`` is a same-document anchor.

    ``#intro`` -> ``"intro"``; ``#`` -> ``""``; ``file.md#x`` / ``http...`` ->
    ``None`` (out of scope for this intra-document validator).
    """
    if not target.startswith("#"):
        return None
    return target[1:]


def find_anchor_links(source: str, text: str) -> tuple[AnchorLink, ...]:
    """Extract every intra-document anchor reference, in document order.

    Inline links are matched first; the spans they occupy are blanked before
    reference links are matched, and reference-link spans are blanked before
    shortcut links, so no fragment of text is counted twice.
    """
    definitions = parse_definitions(text)
    links: list[AnchorLink] = []

    for lineno, raw in enumerate(_blank_code(text), start=1):
        if _LINK_DEF.match(raw):
            # A definition line is not itself a link occurrence.
            continue
        work = raw

        for match in _INLINE_LINK.finditer(work):
            anchor = _internal_anchor(match.group(2))
            if anchor is not None:
                links.append(AnchorLink(source, anchor, lineno, "inline"))
        work = _INLINE_LINK.sub(lambda m: " " * len(m.group(0)), work)

        for match in _REF_LINK.finditer(work):
            label, ref = match.group(1), match.group(2).strip()
            key = (ref or label).strip().lower()
            kind = "reference" if ref else "collapsed"
            _resolve_reference(source, key, lineno, kind, definitions, links)
        work = _REF_LINK.sub(lambda m: " " * len(m.group(0)), work)

        for match in _SHORTCUT_LINK.finditer(work):
            key = match.group(1).strip().lower()
            if key in definitions:
                _resolve_reference(source, key, lineno, "shortcut", definitions, links)

    return tuple(links)


def _resolve_reference(
    source: str,
    key: str,
    lineno: int,
    kind: str,
    definitions: dict[str, str],
    links: list[AnchorLink],
) -> None:
    """Append an :class:`AnchorLink` for a reference link if it targets an anchor.

    Unresolvable references are recorded with a sentinel anchor of ``None`` via a
    special ``"<undefined>"`` marker so the caller can raise ``UNDEFINED_REFERENCE``
    without a second definition lookup.
    """
    target = definitions.get(key)
    if target is None:
        links.append(AnchorLink(source, "\x00undefined:" + key, lineno, kind))
        return
    anchor = _internal_anchor(target)
    if anchor is not None:
        links.append(AnchorLink(source, anchor, lineno, kind))


def check_document(
    path: Path,
    root: Path,
    *,
    text: str | None = None,
) -> tuple[tuple[AnchorLink, ...], tuple[AnchorIssue, ...]]:
    """Audit the intra-document anchors of a single Markdown file.

    ``path`` is the document on disk and ``root`` the project root used only to
    compute a stable, forward-slashed ``source`` label. Returns the discovered
    anchor links and any issues, both in document order.
    """
    root = root.resolve()
    if text is not None and not isinstance(text, str):
        raise TypeError("text must be a string")
    if text is None:
        text = path.read_text(encoding="utf-8")

    try:
        source = str(path.resolve().relative_to(root)).replace("\\", "/")
    except ValueError:
        source = path.name

    anchors, duplicates = collect_anchors(text)
    links = find_anchor_links(source, text)
    issues: list[AnchorIssue] = []

    for link in links:
        if link.anchor.startswith("\x00undefined:"):
            ref = link.anchor.split(":", 1)[1]
            issues.append(
                AnchorIssue(
                    source, ref, link.line, "UNDEFINED_REFERENCE",
                    f"reference link has no matching definition: [{ref}]",
                )
            )
            continue
        if link.anchor == "":
            issues.append(
                AnchorIssue(source, "", link.line, "EMPTY_ANCHOR", "anchor link target is empty")
            )
            continue
        key = link.anchor.lower()
        if key not in anchors:
            issues.append(
                AnchorIssue(
                    source, link.anchor, link.line, "MISSING_ANCHOR",
                    f"no heading or anchor matches: #{link.anchor}",
                )
            )
        elif key in duplicates:
            issues.append(
                AnchorIssue(
                    source, link.anchor, link.line, "AMBIGUOUS_ANCHOR",
                    f"anchor is defined more than once: #{link.anchor}",
                )
            )

    return links, tuple(issues)


def _iter_documents(root: Path) -> list[Path]:
    docs = sorted(root.glob("Chapter*.md"))
    readme = root / "README.md"
    if readme.exists():
        docs.append(readme)
    return docs


def audit_anchors(root: Path, documents: list[Path] | None = None) -> AnchorReport:
    """Audit intra-document anchors across the book's Markdown documents.

    By default this covers ``Chapter*.md`` and ``README.md`` under ``root``. Pass
    ``documents`` to audit an explicit list of files instead.
    """
    root = root.resolve()
    paths = documents if documents is not None else _iter_documents(root)

    total_links = 0
    all_issues: list[AnchorIssue] = []
    for path in paths:
        links, issues = check_document(path, root)
        total_links += len(links)
        all_issues.extend(issues)

    return AnchorReport(documents=len(paths), links=total_links, issues=tuple(all_issues))


def to_json(report: AnchorReport) -> str:
    """Stable JSON contract for an anchor report."""
    return json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":"))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate intra-document Markdown anchors")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true", help="emit the report as stable JSON")
    args = parser.parse_args(argv)

    report = audit_anchors(args.root.resolve())
    if args.json:
        print(to_json(report))
    else:
        print(f"documents={report.documents} anchor_links={report.links} issues={len(report.issues)}")
        for issue in report.issues:
            print(f"  [{issue.code}] {issue.source}:{issue.line} #{issue.anchor}: {issue.message}")
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
