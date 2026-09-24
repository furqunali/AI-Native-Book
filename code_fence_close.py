"""Detection of unclosed or mismatched fenced code blocks.

A fenced code block opens with a run of three or more backticks or tildes and
must be closed by a line using the *same* character and at least as many of
them, with nothing but whitespace after. When the closing fence is forgotten,
the rest of the document is swallowed into a code block; when the author closes
with the wrong character (``~~~`` after a ``` ``` opener), the block also never
closes. Both mistakes are easy to make and hard to see, so this module reports
them explicitly.

The parser follows the CommonMark rule that an opening fence may carry an info
string (`````python``) but a closing fence may not.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^(?P<indent>\s{0,3})(?P<marker>`{3,}|~{3,})(?P<rest>.*)$")


@dataclass(frozen=True)
class FenceIssue:
    """A problem with a fenced code block.

    ``line`` is the 1-based line of the fence at fault, ``kind`` a short code
    (``"unclosed-fence"`` or ``"mismatched-fence"``) and ``message`` a
    human-readable explanation.
    """

    line: int
    kind: str
    message: str


def check_fences(text: str) -> list[FenceIssue]:
    """Return the fence problems in ``text`` in document order.

    Two problems are reported:

    * ``mismatched-fence`` -- while a block is open, a pure-marker line uses a
      different fence character than the opener, or too few characters to close
      it. The author almost certainly meant to close the block, so the parser
      treats it as a (faulty) close and continues.
    * ``unclosed-fence`` -- a block is opened but never closed before the end of
      the document; reported against the opening line.

    An empty list means every fenced code block is well-formed.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    issues: list[FenceIssue] = []
    open_char: str | None = None
    open_len = 0
    open_line = 0

    for i, line in enumerate(text.splitlines()):
        match = _FENCE.match(line)
        if match is None:
            continue

        marker = match.group("marker")
        rest = match.group("rest")
        char = marker[0]
        length = len(marker)

        if open_char is None:
            # A fence line while closed always opens a new block (info allowed).
            open_char = char
            open_len = length
            open_line = i + 1
            continue

        # Inside a block: does this line look like an attempt to close it?
        is_pure_marker = rest.strip() == ""
        if not is_pure_marker:
            # A line like "```python" inside a block is just content.
            continue

        if char == open_char and length >= open_len:
            # A proper close.
            open_char = None
            continue

        # Pure-marker line that cannot legally close the block: report and,
        # assuming the author intended to close, recover so we do not cascade.
        if char != open_char:
            reason = (
                f"code block opened with '{open_char * open_len}' is closed "
                f"with '{marker}' (mismatched fence character)"
            )
        else:
            reason = (
                f"closing fence '{marker}' is shorter than the opening "
                f"'{open_char * open_len}'"
            )
        issues.append(
            FenceIssue(line=i + 1, kind="mismatched-fence", message=reason)
        )
        open_char = None

    if open_char is not None:
        issues.append(
            FenceIssue(
                line=open_line,
                kind="unclosed-fence",
                message="fenced code block is opened but never closed",
            )
        )

    issues.sort(key=lambda issue: issue.line)
    return issues


def is_balanced(text: str) -> bool:
    """Return ``True`` when ``text`` has no fence problems."""
    return not check_fences(text)
