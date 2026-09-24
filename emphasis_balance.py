"""Detection of unbalanced inline formatting in Markdown documents.

An unclosed code span or bold marker leaks formatting into the rest of a
paragraph and is a common, hard-to-spot editing mistake. This module flags two
high-signal, low-false-positive cases:

* an odd number of inline backticks on a line (an unclosed ``code`` span), and
* an odd number of ``**`` strong-emphasis markers on a line once code spans have
  been removed.

It also reports a fenced code block that is opened but never closed. Underscore
and single-asterisk emphasis are intentionally not checked because they collide
with identifiers, file names and arithmetic, which would produce noisy false
positives.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_CODE_SPAN = re.compile(r"`[^`]*`")
_STRONG = re.compile(r"\*\*")
_ESCAPED = re.compile(r"\\.")


@dataclass(frozen=True)
class EmphasisIssue:
    """An unbalanced-formatting problem.

    ``line`` is the 1-based line number, ``kind`` a short code and ``message`` a
    human-readable explanation.
    """

    line: int
    kind: str
    message: str


def check_emphasis(text: str) -> list[EmphasisIssue]:
    """Return the ordered inline-formatting balance issues in ``text``.

    Reported problems are ``unclosed-code-span`` (an odd count of backticks on a
    line), ``unbalanced-strong`` (an odd count of ``**`` markers on a line after
    code spans are removed) and ``unterminated-fence`` (a fenced code block that
    is never closed, attached to its opening line). Lines inside fenced code
    blocks are not checked. An empty list means the document's inline formatting
    is balanced.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    issues: list[EmphasisIssue] = []
    fence: str | None = None
    fence_line = 0

    for i, line in enumerate(text.splitlines()):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                fence_line = i + 1
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue

        # Drop escaped characters so "\`" and "\*" are not counted as markers.
        cleaned = _ESCAPED.sub("", line)

        backticks = cleaned.count("`")
        if backticks % 2 == 1:
            issues.append(
                EmphasisIssue(
                    line=i + 1,
                    kind="unclosed-code-span",
                    message="line has an odd number of backticks",
                )
            )
            # Skip strong check: unbalanced backticks make it unreliable.
            continue

        without_code = _CODE_SPAN.sub("", cleaned)
        if len(_STRONG.findall(without_code)) % 2 == 1:
            issues.append(
                EmphasisIssue(
                    line=i + 1,
                    kind="unbalanced-strong",
                    message="line has an odd number of '**' markers",
                )
            )

    if fence is not None:
        issues.append(
            EmphasisIssue(
                line=fence_line,
                kind="unterminated-fence",
                message="fenced code block is opened but never closed",
            )
        )

    issues.sort(key=lambda issue: issue.line)
    return issues


def is_balanced(text: str) -> bool:
    """Return ``True`` when ``text`` has no unbalanced-formatting issues."""
    return not check_emphasis(text)
