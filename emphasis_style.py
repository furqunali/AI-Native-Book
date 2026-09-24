"""Detection of mixed emphasis markers in Markdown.

Markdown lets you italicise and bold text with either asterisks (``*em*``,
``**strong**``) or underscores (``_em_``, ``__strong__``). Mixing the two within
one document is legal but inconsistent, and most style guides ask authors to
pick one. This module counts each family of markers, decides which is dominant,
and reports the occurrences written in the deviating style so they can be
normalised.

Underscore emphasis is only counted when the underscores sit on word boundaries
so that ``snake_case`` identifiers and ``file_name`` tokens are not mistaken for
emphasis. Inline code spans and fenced code blocks are ignored entirely.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")

# Marker patterns, ordered so strong markers are matched before single ones.
_ASTERISK = re.compile(r"\*\*[^*]+\*\*|\*[^*\s][^*]*\*")
_UNDERSCORE = re.compile(
    r"(?<![A-Za-z0-9_])(?:__[^_]+__|_[^_\s][^_]*_)(?![A-Za-z0-9_])"
)


@dataclass(frozen=True)
class Deviation:
    """A single emphasis span written in the non-dominant style.

    ``line`` is the 1-based line number, ``marker`` is ``"*"`` or ``"_"`` and
    ``snippet`` is the matched emphasis text.
    """

    line: int
    marker: str
    snippet: str


@dataclass(frozen=True)
class EmphasisStyleReport:
    """The document-wide emphasis-marker summary.

    ``asterisk`` and ``underscore`` are the number of spans of each family,
    ``dominant`` is ``"asterisk"``, ``"underscore"`` or ``"none"`` (when no
    emphasis exists), and ``deviations`` lists every span in the minority style
    in document order. On a tie, asterisk is treated as dominant so the outcome
    is deterministic.
    """

    asterisk: int
    underscore: int
    dominant: str
    deviations: tuple[Deviation, ...]

    @property
    def is_consistent(self) -> bool:
        """Return ``True`` when at most one emphasis family is used."""
        return not self.deviations


def analyze_emphasis_style(text: str) -> EmphasisStyleReport:
    """Return the mixed-emphasis report for ``text``.

    Every asterisk and underscore emphasis span outside code is collected. The
    family with more spans is dominant (asterisk wins ties); spans of the other
    family become ``deviations``. When only one or neither family is present the
    report has no deviations.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    records: list[Deviation] = []
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
        for m in _ASTERISK.finditer(cleaned):
            records.append(Deviation(line=i + 1, marker="*", snippet=m.group(0)))
        for m in _UNDERSCORE.finditer(cleaned):
            records.append(Deviation(line=i + 1, marker="_", snippet=m.group(0)))

    asterisk = sum(1 for r in records if r.marker == "*")
    underscore = sum(1 for r in records if r.marker == "_")

    if asterisk == 0 and underscore == 0:
        dominant = "none"
        minority_marker = None
    elif asterisk >= underscore:
        dominant = "asterisk"
        minority_marker = "_"
    else:
        dominant = "underscore"
        minority_marker = "*"

    deviations = tuple(r for r in records if r.marker == minority_marker)
    return EmphasisStyleReport(
        asterisk=asterisk,
        underscore=underscore,
        dominant=dominant,
        deviations=deviations,
    )
