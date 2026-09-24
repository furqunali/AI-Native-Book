"""Extraction and range-checking of four-digit years.

Books cite years -- publication dates, historical events, "as of 2024". A typo
that turns 2024 into 2042, or a stale "1899", is easy to miss. This module
extracts every four-digit year in the ``19xx``/``20xx`` range and flags those
outside a configurable valid range so an editor can review them.

The valid range defaults to 1900-2099 rather than "the current year" on purpose:
the function is pure and deterministic and never reads the wall clock, so its
output depends only on its inputs. Years inside inline code spans and fenced
code blocks are ignored, and a year must stand as its own token (not part of a
longer number) to be extracted.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")
_YEAR = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")

_DEFAULT_MIN_YEAR = 1900
_DEFAULT_MAX_YEAR = 2099


@dataclass(frozen=True)
class YearRef:
    """A four-digit year found in the text.

    ``line`` is the 1-based line number, ``year`` the integer value and
    ``in_range`` whether it falls within the configured valid range.
    """

    line: int
    year: int
    in_range: bool


def extract_years(text: str) -> list[YearRef]:
    """Return every ``19xx``/``20xx`` year in ``text`` in document order.

    ``in_range`` is computed against the default range and is only meaningful
    when the default is what you want; :func:`check_years` recomputes it for a
    custom range. Years inside code are ignored. Numbers like ``1234`` or
    ``2500`` are not matched because they fall outside the ``19``/``20`` prefix.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    refs: list[YearRef] = []
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

        cleaned = _CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line)
        for m in _YEAR.finditer(cleaned):
            year = int(m.group(0))
            in_range = _DEFAULT_MIN_YEAR <= year <= _DEFAULT_MAX_YEAR
            refs.append(YearRef(line=i + 1, year=year, in_range=in_range))

    return refs


def check_years(
    text: str,
    *,
    min_year: int = _DEFAULT_MIN_YEAR,
    max_year: int = _DEFAULT_MAX_YEAR,
) -> list[YearRef]:
    """Return the years in ``text`` that fall outside ``[min_year, max_year]``.

    Only out-of-range years are returned, each with ``in_range`` set to
    ``False``, in document order. ``min_year`` must not exceed ``max_year``. An
    empty list means every year cited is within range.
    """
    if not isinstance(min_year, int) or isinstance(min_year, bool):
        raise TypeError("min_year must be an int")
    if not isinstance(max_year, int) or isinstance(max_year, bool):
        raise TypeError("max_year must be an int")
    if min_year > max_year:
        raise ValueError("min_year must not exceed max_year")

    out_of_range: list[YearRef] = []
    for ref in extract_years(text):
        if not (min_year <= ref.year <= max_year):
            out_of_range.append(
                YearRef(line=ref.line, year=ref.year, in_range=False)
            )
    return out_of_range


def all_in_range(
    text: str,
    *,
    min_year: int = _DEFAULT_MIN_YEAR,
    max_year: int = _DEFAULT_MAX_YEAR,
) -> bool:
    """Return ``True`` when every year in ``text`` is within the valid range."""
    return not check_years(text, min_year=min_year, max_year=max_year)
