"""Fenced code-block extraction and language tallies for book chapters.

Code fences are read the way CommonMark (and GitHub) render them: an opening
fence is three or more backticks or tildes, indented up to three spaces; the
matching closing fence uses the same character, is at least as long, and carries
no info string. The first token of the opening info string is treated as the
language and normalised to lowercase, so the tooling can report which languages a
chapter demonstrates and aggregate that tally across the whole book.

Backtick fences never contain a backtick in their info string (a CommonMark
rule that prevents inline code from being mistaken for a fence); tilde fences may.
An unclosed fence runs to the end of the chapter, matching how renderers recover.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

#: Language key used for a fenced block that carries no info string.
UNLABELED = ""

_FENCE_CHARS = ("`", "~")
_MAX_INDENT = 3


@dataclass(frozen=True)
class CodeBlock:
    """A single fenced code block found in a chapter.

    ``language`` is the lowercased first token of the info string (``""`` when
    the fence has no info string); ``info`` is the full info string as written
    (stripped of surrounding whitespace); ``content`` is the block body with the
    fence lines removed and the opening fence's indentation stripped;
    ``start_line``/``end_line`` are 1-based line numbers of the opening and
    closing fences (``end_line`` is the last body line when the fence is never
    closed); ``line_count`` is the number of body lines; and ``closed`` records
    whether a matching closing fence was found.
    """

    language: str
    info: str
    content: str
    start_line: int
    end_line: int
    line_count: int
    closed: bool


def _fence_open(line: str) -> tuple[str, int, int, str] | None:
    """Inspect ``line`` as a possible opening fence.

    Returns ``(char, length, indent, info)`` when ``line`` opens a fence, or
    ``None`` otherwise. Backtick fences whose info string contains a backtick
    are rejected per CommonMark.
    """
    indent = len(line) - len(line.lstrip(" "))
    if indent > _MAX_INDENT:
        return None
    stripped = line[indent:]
    if not stripped:
        return None
    char = stripped[0]
    if char not in _FENCE_CHARS:
        return None
    length = len(stripped) - len(stripped.lstrip(char))
    if length < 3:
        return None
    info = stripped[length:].strip()
    if char == "`" and "`" in info:
        return None
    return char, length, indent, info


def _fence_close(line: str, char: str, length: int) -> bool:
    """Return whether ``line`` closes a fence opened with ``char`` * ``length``.

    A closing fence is the same character repeated at least ``length`` times,
    indented up to three spaces, with nothing but optional trailing whitespace
    after it.
    """
    indent = len(line) - len(line.lstrip(" "))
    if indent > _MAX_INDENT:
        return False
    stripped = line[indent:]
    run = len(stripped) - len(stripped.lstrip(char))
    if run < length:
        return False
    return stripped[run:].strip() == ""


def _language_of(info: str) -> str:
    """Return the normalised language token for an info string."""
    if not info:
        return UNLABELED
    return info.split()[0].lower()


def extract_code_blocks(text: str) -> list[CodeBlock]:
    """Extract every fenced code block from chapter ``text`` in order.

    Both backtick (```` ``` ````) and tilde (``~~~``) fences are recognised.
    Fences of one character appearing inside a block opened by the other are
    treated as ordinary content, so an embedded example fence is not mistaken
    for a real one. An opening fence that is never closed captures the remainder
    of the chapter and is reported with ``closed=False``.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    blocks: list[CodeBlock] = []
    lines = text.splitlines()
    i = 0
    total = len(lines)
    while i < total:
        opened = _fence_open(lines[i])
        if opened is None:
            i += 1
            continue
        char, length, indent, info = opened
        start_line = i + 1
        body: list[str] = []
        j = i + 1
        closed = False
        while j < total:
            if _fence_close(lines[j], char, length):
                closed = True
                break
            # Strip the opening fence's indentation from each body line.
            body_line = lines[j]
            strip = min(indent, len(body_line) - len(body_line.lstrip(" ")))
            body.append(body_line[strip:])
            j += 1
        if closed:
            end_line = j + 1
        else:
            # Unclosed: the block ran to end of file; no closing-fence line.
            end_line = total
        blocks.append(
            CodeBlock(
                language=_language_of(info),
                info=info,
                content="\n".join(body),
                start_line=start_line,
                end_line=end_line,
                line_count=len(body),
                closed=closed,
            )
        )
        i = j + 1 if closed else total
    return blocks


def _blocks_from(source: str | Iterable[CodeBlock]) -> list[CodeBlock]:
    """Coerce ``source`` (chapter text or code blocks) into a block list."""
    if isinstance(source, str):
        return extract_code_blocks(source)
    blocks = list(source)
    for block in blocks:
        if not isinstance(block, CodeBlock):
            raise TypeError("source must be text or an iterable of CodeBlock")
    return blocks


def tally_languages(
    source: str | Iterable[CodeBlock], *, include_unlabeled: bool = True
) -> Counter[str]:
    """Count fenced code blocks per language in a single chapter.

    ``source`` may be chapter text or an already-extracted iterable of
    :class:`CodeBlock`. Languages are the normalised info-string tokens; blocks
    with no info string are counted under :data:`UNLABELED` unless
    ``include_unlabeled`` is ``False``.
    """
    blocks = _blocks_from(source)
    tally: Counter[str] = Counter()
    for block in blocks:
        if block.language == UNLABELED and not include_unlabeled:
            continue
        tally[block.language] += 1
    return tally


@dataclass(frozen=True)
class LanguageTally:
    """Aggregate language usage across several chapters.

    ``total`` is the book-wide count of blocks per language; ``per_chapter``
    maps each chapter name to its own per-language :class:`~collections.Counter`;
    ``block_count`` is the total number of code blocks seen.
    """

    total: Counter[str]
    per_chapter: dict[str, Counter[str]]
    block_count: int


def tally_languages_across(
    chapters: Mapping[str, str], *, include_unlabeled: bool = True
) -> LanguageTally:
    """Tally code-block languages across a mapping of chapter name to text.

    Each value is parsed independently, so a stray unclosed fence in one chapter
    cannot bleed into another. The returned :class:`LanguageTally` carries both
    the book-wide totals and the per-chapter breakdown.
    """
    if not isinstance(chapters, Mapping):
        raise TypeError("chapters must be a mapping of name to text")

    total: Counter[str] = Counter()
    per_chapter: dict[str, Counter[str]] = {}
    block_count = 0
    for name, text in chapters.items():
        chapter_tally = tally_languages(text, include_unlabeled=include_unlabeled)
        per_chapter[name] = chapter_tally
        total.update(chapter_tally)
        block_count += sum(chapter_tally.values())
    return LanguageTally(
        total=total, per_chapter=per_chapter, block_count=block_count
    )
