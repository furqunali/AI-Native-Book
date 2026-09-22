"""Section-balance analysis for book chapters.

A well-structured chapter spreads its prose reasonably evenly across its
sections; a chapter where one section carries most of the words (or where
several sections are near-empty stubs) reads as lopsided and usually wants
restructuring. This module measures that balance.

Prose is counted the way a reader reads it: fenced code blocks are skipped so a
``#`` in a shell snippet is never mistaken for a heading and a code-heavy
section is not credited with inflated word counts, heading lines themselves are
excluded from their section's word total, and inline markdown (links, inline
code, emphasis) is reduced to plain text before words are counted.

The chapter is partitioned at headings of a chosen ``section_level`` (``##`` by
default). Content that appears before the first such heading -- or under a
heading shallower than ``section_level`` -- is attributed to the *preamble* and
kept separate from the balance statistics, which describe only the peer
sections themselves.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^\s{0,3}(#{1,6})(?:\s+(.*?))?\s*$")
_ATX_CLOSING = re.compile(r"\s+#+\s*$")
_WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")

_DEFAULT_THRESHOLD = 0.5


@dataclass(frozen=True)
class Section:
    """A single top-level section of a chapter.

    ``title`` is the plain-text heading, ``level`` is its heading level,
    ``start_line`` is the 1-based line of the heading, and ``word_count`` is the
    number of prose words in the section, including any nested subsections but
    excluding heading text and fenced code.
    """

    title: str
    level: int
    start_line: int
    word_count: int


@dataclass(frozen=True)
class BalanceReport:
    """Deterministic section-balance metrics for a single chapter.

    ``sections`` holds the peer sections in order of appearance.
    ``preamble_words`` counts prose that precedes the first section (or sits
    under a shallower heading). ``mean_words``, ``min_words`` and ``max_words``
    describe the section word counts. ``imbalance_ratio`` is the largest
    section's word count divided by the smallest's (``inf`` when the smallest
    is empty, ``0.0`` when there are no sections). ``coefficient_of_variation``
    is the population standard deviation of the counts divided by the mean, a
    scale-free spread measure that is ``0.0`` for a single or perfectly even
    set of sections. ``balanced`` is ``True`` when the chapter has fewer than
    two sections or its coefficient of variation is at or below the threshold.
    """

    section_count: int
    total_words: int
    preamble_words: int
    sections: tuple[Section, ...]
    mean_words: float
    min_words: int
    max_words: int
    imbalance_ratio: float
    coefficient_of_variation: float
    balanced: bool


def _strip_inline(text: str) -> str:
    """Reduce a line's inline markdown to plain text for word counting."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    return text


def _count_words(line: str) -> int:
    """Count prose words on a single (already de-fenced) markdown line."""
    return len(_WORD.findall(_strip_inline(line)))


def analyze_balance(text: str, *, section_level: int = 2) -> BalanceReport:
    """Analyse how evenly chapter ``text`` distributes prose across sections.

    Sections are opened by ATX headings of exactly ``section_level``. A heading
    shallower than ``section_level`` closes the current section and returns
    following prose to the preamble; deeper headings are treated as subsections
    and their prose is folded into the enclosing section. Headings and fenced
    code blocks never contribute to any word count.

    A chapter with no section-level headings yields an empty ``sections`` tuple
    with all prose recorded as ``preamble_words``; such a chapter is reported as
    ``balanced`` because there are no peers to compare.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(section_level, int) or isinstance(section_level, bool):
        raise TypeError("section_level must be an int")
    if not 1 <= section_level <= 6:
        raise ValueError("section_level must be between 1 and 6")

    sections: list[Section] = []
    preamble_words = 0
    current: int | None = None  # index into ``counts`` of the open section
    counts: list[int] = []
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

        atx = _ATX.match(line)
        if atx:
            level = len(atx.group(1))
            if level == section_level:
                raw = _ATX_CLOSING.sub("", atx.group(2) or "").strip()
                counts.append(0)
                current = len(counts) - 1
                sections.append(
                    Section(title=raw, level=level, start_line=i + 1, word_count=0)
                )
            elif level < section_level:
                current = None
            # A deeper heading stays inside the current section; its title text
            # is not prose and is therefore not counted.
            continue

        words = _count_words(line)
        if not words:
            continue
        if current is None:
            preamble_words += words
        else:
            counts[current] += words

    # Fold the accumulated per-section counts back into the Section records.
    sections = [
        Section(
            title=s.title,
            level=s.level,
            start_line=s.start_line,
            word_count=counts[idx],
        )
        for idx, s in enumerate(sections)
    ]

    section_count = len(sections)
    total_words = sum(counts)

    if section_count == 0:
        return BalanceReport(
            section_count=0,
            total_words=0,
            preamble_words=preamble_words,
            sections=(),
            mean_words=0.0,
            min_words=0,
            max_words=0,
            imbalance_ratio=0.0,
            coefficient_of_variation=0.0,
            balanced=True,
        )

    min_words = min(counts)
    max_words = max(counts)
    mean = total_words / section_count

    if section_count == 1 or mean == 0:
        cv = 0.0
    else:
        variance = sum((c - mean) ** 2 for c in counts) / section_count
        cv = round((variance**0.5) / mean, 4)

    if min_words == 0:
        imbalance_ratio = 0.0 if max_words == 0 else float("inf")
    else:
        imbalance_ratio = round(max_words / min_words, 4)

    balanced = section_count < 2 or cv <= _DEFAULT_THRESHOLD

    return BalanceReport(
        section_count=section_count,
        total_words=total_words,
        preamble_words=preamble_words,
        sections=tuple(sections),
        mean_words=round(mean, 2),
        min_words=min_words,
        max_words=max_words,
        imbalance_ratio=imbalance_ratio,
        coefficient_of_variation=cv,
        balanced=balanced,
    )


def format_balance_report(report: BalanceReport) -> str:
    """Render a ``BalanceReport`` as a compact markdown summary table.

    The table lists each section with its word count and share of the chapter's
    section prose, followed by a summary line noting whether the chapter is
    balanced. A chapter with no sections returns a single explanatory line so
    the output can be dropped straight into an aggregate health report.
    """
    if not isinstance(report, BalanceReport):
        raise TypeError("report must be a BalanceReport")

    if report.section_count == 0:
        return "_No sections found._"

    lines = ["| Section | Words | Share |", "| --- | ---: | ---: |"]
    for section in report.sections:
        share = (
            section.word_count / report.total_words if report.total_words else 0.0
        )
        lines.append(
            f"| {section.title or '(untitled)'} | {section.word_count} | {share:.0%} |"
        )

    verdict = "balanced" if report.balanced else "imbalanced"
    lines.append("")
    lines.append(
        f"**{report.section_count} sections**, {report.total_words} words, "
        f"CV {report.coefficient_of_variation:.2f} -- {verdict}."
    )
    return "\n".join(lines)
