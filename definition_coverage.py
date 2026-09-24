"""Coverage of glossary terms in the body text.

A glossary should define terms the book actually uses. A term that is defined but
never referenced in the prose is dead weight -- either the definition is
redundant or the author dropped the discussion that needed it. Given the list of
glossary terms and the body text, this module reports which terms are used and
which are never mentioned.

Matching is case-insensitive and bounded so ``agent`` is found in "the agent
runs" but not inside ``agents`` or ``reagent`` (multi-word terms are matched as a
whole phrase with flexible internal whitespace). References inside inline code
spans and fenced code blocks are ignored so a term that only appears in a code
identifier still counts as unused prose.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")


@dataclass(frozen=True)
class TermCoverage:
    """Whether a single glossary term is used in the body.

    ``term`` is the glossary term as supplied, ``count`` how many times it
    appears in the prose and ``used`` whether ``count`` is greater than zero.
    """

    term: str
    count: int
    used: bool


def _prose(text: str) -> str:
    """Return ``text`` with fenced code and inline code spans removed."""
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            kept.append(_CODE_SPAN.sub(" ", line))
        elif line.lstrip().startswith(fence):
            fence = None
    return "\n".join(kept)


def _pattern(term: str) -> re.Pattern[str]:
    """Build a case-insensitive, boundary-aware pattern for ``term``.

    Internal runs of whitespace in a multi-word term are allowed to match any
    whitespace (including a line break) in the body.
    """
    parts = term.split()
    body = r"\s+".join(re.escape(part) for part in parts)
    return re.compile(r"(?<![\w])" + body + r"(?![\w])", re.IGNORECASE)


def check_coverage(terms: list[str], text: str) -> list[TermCoverage]:
    """Return the body-text coverage of each term in ``terms``.

    The result preserves the order of ``terms`` (de-duplicated case-insensitively
    on first occurrence). Each term is counted with case-insensitive,
    word-boundary matching against the prose, ignoring code. Terms that are empty
    or whitespace-only are rejected.
    """
    if not isinstance(terms, (list, tuple)):
        raise TypeError("terms must be a list of strings")
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    prose = _prose(text)
    seen: set[str] = set()
    coverage: list[TermCoverage] = []
    for term in terms:
        if not isinstance(term, str):
            raise TypeError("each term must be a string")
        if term.strip() == "":
            raise ValueError("terms must not be empty")
        key = term.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        count = len(_pattern(term.strip()).findall(prose))
        coverage.append(TermCoverage(term=term, count=count, used=count > 0))
    return coverage


def unused_terms(terms: list[str], text: str) -> list[str]:
    """Return the terms from ``terms`` that never appear in the body prose.

    Order follows :func:`check_coverage`. An empty list means every term is
    referenced at least once.
    """
    return [cov.term for cov in check_coverage(terms, text) if not cov.used]


def coverage_ratio(terms: list[str], text: str) -> float:
    """Return the fraction of distinct terms that are used, in ``[0, 1]``.

    Rounded to six places. An empty term list returns ``0.0``.
    """
    coverage = check_coverage(terms, text)
    if not coverage:
        return 0.0
    used = sum(1 for cov in coverage if cov.used)
    return round(used / len(coverage), 6)
