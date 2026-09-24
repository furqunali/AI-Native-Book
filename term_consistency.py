"""Capitalisation-consistency checking for a chosen term.

Technical books frequently disagree with themselves about how a term is
capitalised -- ``JavaScript`` vs ``Javascript`` vs ``javascript``, or ``API`` vs
``Api``. This module finds every occurrence of a given term (matched
case-insensitively on word boundaries) and reports the distinct surface forms it
appears in. When an ``expected`` spelling is supplied, every other form is
treated as a deviation; otherwise the module simply reports whether more than
one spelling is in use.

Occurrences inside fenced code blocks and inline code spans are ignored so code
identifiers do not pollute the prose analysis.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")


@dataclass(frozen=True)
class TermVariant:
    """One surface spelling of the searched term.

    ``form`` is the exact text as it appears, ``count`` how many times it
    occurs, and ``lines`` the sorted tuple of 1-based line numbers where it is
    found.
    """

    form: str
    count: int
    lines: tuple[int, ...]


def term_variants(text: str, term: str) -> list[TermVariant]:
    """Return the distinct spellings of ``term`` found in ``text``.

    Matching is case-insensitive and bounded by non-word characters, so
    ``agent`` does not match ``agents`` or ``reagent``. Variants are ordered by
    descending count with ties broken alphabetically (case-insensitively) so
    the result is deterministic. Code spans and fenced code are ignored. An
    empty list means the term does not appear in the prose.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(term, str):
        raise TypeError("term must be a string")
    if term.strip() == "":
        raise ValueError("term must not be empty")

    pattern = re.compile(
        r"(?<![\w])" + re.escape(term.strip()) + r"(?![\w])",
        re.IGNORECASE,
    )

    counts: dict[str, int] = {}
    line_map: dict[str, set[int]] = {}
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
        for m in pattern.finditer(cleaned):
            form = m.group(0)
            counts[form] = counts.get(form, 0) + 1
            line_map.setdefault(form, set()).add(i + 1)

    variants = [
        TermVariant(form=form, count=count, lines=tuple(sorted(line_map[form])))
        for form, count in counts.items()
    ]
    variants.sort(key=lambda v: (-v.count, v.form.lower(), v.form))
    return variants


def is_consistent(text: str, term: str, *, expected: str | None = None) -> bool:
    """Return whether ``term`` is capitalised consistently in ``text``.

    Without ``expected``, the term is consistent when it appears in at most one
    spelling (including not appearing at all). With ``expected``, it is
    consistent only when every occurrence matches ``expected`` exactly.
    """
    variants = term_variants(text, term)
    if expected is None:
        return len(variants) <= 1
    return all(v.form == expected for v in variants)


def deviations(text: str, term: str, *, expected: str) -> list[TermVariant]:
    """Return the variants of ``term`` that differ from ``expected``.

    The result is ordered like :func:`term_variants`. An empty list means every
    occurrence already matches ``expected``.
    """
    if not isinstance(expected, str) or expected.strip() == "":
        raise ValueError("expected must be a non-empty string")
    return [v for v in term_variants(text, term) if v.form != expected]
