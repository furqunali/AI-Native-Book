"""Glossary cross-reference checking for the book.

The glossary (``GLOSSARY.md``) defines the recurring terms used across the
chapters. This module answers two questions a reviewer keeps asking by hand:
which chapters actually *use* each defined term, and which glossary entries are
dead weight because no chapter references them.

Terms are parsed from the glossary's markdown table. Usage is counted against
the prose a reader actually reads: fenced code blocks, inline code and link
targets are stripped first so a term appearing only inside a code snippet or a
URL is never mistaken for genuine prose usage. Matching is whole-term and, by
default, case-insensitive, with internal whitespace in a multi-word term
treated flexibly so ``Vector database`` still matches ``vector  database``
across a line wrap.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{1,}:?\s*)+\|?\s*$")
_BOLD = re.compile(r"^\*\*(.+?)\*\*$")
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class GlossaryTerm:
    """A single term defined in the glossary.

    ``term`` is the plain-text term with surrounding bold markers removed and
    ``definition`` is the accompanying description. ``line`` is the 1-based line
    number of the table row the term was parsed from.
    """

    term: str
    definition: str
    line: int


@dataclass(frozen=True)
class TermUsage:
    """How a single defined term is used across the chapters.

    ``chapters`` is the sorted tuple of chapter names in which the term appears
    at least once, and ``total_uses`` is the summed number of occurrences.
    """

    term: str
    definition: str
    total_uses: int
    chapters: tuple[str, ...]


@dataclass(frozen=True)
class GlossaryReport:
    """The result of cross-referencing the glossary against the chapters.

    ``usages`` preserves glossary order. ``unused`` lists terms that are defined
    but never referenced in any chapter, and ``duplicates`` lists terms whose
    definition appears more than once in the glossary (comparison uses the
    same casefolding as usage matching).
    """

    usages: tuple[TermUsage, ...]
    unused: tuple[str, ...]
    duplicates: tuple[str, ...]

    @property
    def is_clean(self) -> bool:
        """True when every term is used exactly once-defined and referenced."""
        return not self.unused and not self.duplicates


def _split_row(line: str) -> list[str]:
    """Split a markdown table ``line`` into its trimmed cell values.

    Leading and trailing pipes are ignored so ``| a | b |`` and ``a | b`` both
    yield ``["a", "b"]``.
    """
    stripped = line.strip()
    stripped = stripped.removeprefix("|")
    stripped = stripped.removesuffix("|")
    return [cell.strip() for cell in stripped.split("|")]


def _clean_term(cell: str) -> str:
    """Reduce a term cell to plain text, dropping surrounding bold markers."""
    match = _BOLD.match(cell.strip())
    text = match.group(1) if match else cell.strip()
    return _WHITESPACE.sub(" ", text).strip()


def parse_glossary(text: str) -> list[GlossaryTerm]:
    """Parse the glossary markdown ``text`` into its defined terms.

    Terms are read from the first two columns of the glossary table. The header
    row (whose first cell is ``Term``) and the ``---`` separator row are
    skipped, as are rows inside fenced code blocks and rows without both a term
    and a definition. Terms are returned in document order; de-duplication is
    left to :func:`crossref_glossary` so callers can still see raw rows.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    terms: list[GlossaryTerm] = []
    fence: str | None = None
    for i, line in enumerate(text.splitlines()):
        fence_match = _FENCE.match(line)
        if fence is None:
            if fence_match:
                fence = fence_match.group(1)
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        if "|" not in line:
            continue
        if _TABLE_SEPARATOR.match(line):
            continue

        cells = _split_row(line)
        if len(cells) < 2:
            continue
        term = _clean_term(cells[0])
        definition = cells[1].strip()
        if not term or not definition:
            continue
        if term.casefold() == "term":
            continue
        terms.append(GlossaryTerm(term=term, definition=definition, line=i + 1))

    return terms


def _strip_markup(text: str) -> str:
    """Reduce chapter markdown to plain prose for term counting.

    Fenced code blocks are removed entirely, inline code spans and link/image
    targets are dropped (their visible text is kept), so a term is only counted
    where it appears in genuine prose rather than in code or a URL.
    """
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            kept.append(line)
        elif line.lstrip().startswith(fence):
            fence = None
    body = "\n".join(kept)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"`[^`]*`", "", body)
    return body


def _term_pattern(term: str, *, case_sensitive: bool) -> re.Pattern[str]:
    """Compile a whole-term matcher for ``term``.

    Regex metacharacters in the term are escaped, internal whitespace is made
    flexible so a term is still matched across a line wrap, and the term is
    bounded so it is only matched as a whole word (or phrase) rather than as a
    substring of a larger word.
    """
    parts = [re.escape(part) for part in term.split()]
    core = r"\s+".join(parts)
    left = r"(?<![0-9A-Za-z_])" if term[:1].isalnum() or term[:1] == "_" else ""
    right = r"(?![0-9A-Za-z_])" if term[-1:].isalnum() or term[-1:] == "_" else ""
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(left + core + right, flags)


def count_uses(term: str, text: str, *, case_sensitive: bool = False) -> int:
    """Count whole-term occurrences of ``term`` in chapter ``text``.

    Occurrences inside fenced code blocks, inline code spans and link targets
    are excluded. Matching is case-insensitive unless ``case_sensitive`` is set.
    """
    if not isinstance(term, str):
        raise TypeError("term must be a string")
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not term.strip():
        raise ValueError("term must not be empty")
    pattern = _term_pattern(term.strip(), case_sensitive=case_sensitive)
    return len(pattern.findall(_strip_markup(text)))


def crossref_glossary(
    glossary_text: str,
    chapters: dict[str, str],
    *,
    case_sensitive: bool = False,
) -> GlossaryReport:
    """Cross-reference the glossary against a mapping of chapter texts.

    ``chapters`` maps a chapter name (used in the report) to that chapter's
    markdown. For each glossary term the report records the chapters that use it
    and the total number of uses; terms used nowhere are collected in
    ``unused``. A term defined more than once (case-insensitively) is reported
    once in ``duplicates`` and cross-referenced only once in ``usages``.
    """
    if not isinstance(glossary_text, str):
        raise TypeError("glossary_text must be a string")
    if not isinstance(chapters, dict):
        raise TypeError("chapters must be a dict of name to text")
    for name, body in chapters.items():
        if not isinstance(name, str) or not isinstance(body, str):
            raise TypeError("chapters must map str names to str text")

    stripped = {name: _strip_markup(body) for name, body in chapters.items()}

    usages: list[TermUsage] = []
    unused: list[str] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    for entry in parse_glossary(glossary_text):
        key = entry.term.casefold()
        if key in seen:
            if entry.term not in duplicates:
                duplicates.append(entry.term)
            continue
        seen.add(key)

        pattern = _term_pattern(entry.term, case_sensitive=case_sensitive)
        used_in: list[str] = []
        total = 0
        for name in sorted(stripped):
            count = len(pattern.findall(stripped[name]))
            if count:
                used_in.append(name)
                total += count
        usages.append(
            TermUsage(
                term=entry.term,
                definition=entry.definition,
                total_uses=total,
                chapters=tuple(used_in),
            )
        )
        if total == 0:
            unused.append(entry.term)

    return GlossaryReport(
        usages=tuple(usages),
        unused=tuple(unused),
        duplicates=tuple(duplicates),
    )


def render_report(report: GlossaryReport) -> str:
    """Render a ``GlossaryReport`` as a human-readable markdown summary.

    The summary lists every term with its total usage and the chapters that
    reference it, followed by explicit sections for unused and duplicate terms.
    """
    if not isinstance(report, GlossaryReport):
        raise TypeError("report must be a GlossaryReport")

    lines = ["# Glossary cross-reference", ""]
    for usage in report.usages:
        where = ", ".join(usage.chapters) if usage.chapters else "—"
        lines.append(f"- **{usage.term}** — {usage.total_uses} use(s): {where}")

    lines.append("")
    if report.unused:
        lines.append("## Unused terms")
        lines.extend(f"- {term}" for term in report.unused)
    else:
        lines.append("## Unused terms")
        lines.append("- none")

    lines.append("")
    if report.duplicates:
        lines.append("## Duplicate definitions")
        lines.extend(f"- {term}" for term in report.duplicates)
    else:
        lines.append("## Duplicate definitions")
        lines.append("- none")

    return "\n".join(lines)
