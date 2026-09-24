"""Heuristic passive-voice detection for chapter prose.

Passive constructions ("the model was trained", "results are shown") are not
wrong, but a high density of them makes technical writing feel evasive and
harder to follow. This module flags sentences that contain a form of *to be*
immediately followed (allowing an optional adverb) by a past participle, which
catches the most common passive patterns without a part-of-speech tagger.

The detection is intentionally conservative: it only fires on the be-verb +
participle adjacency, so it will miss some passives and occasionally flag a
predicate adjective, but it is deterministic and dependency-free. Fenced code
blocks and headings are ignored so only running prose is examined.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE = re.compile(r"^\s*(```|~~~)")
_ATX = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
_TERMINATOR = re.compile(r"[.!?]+")
_WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")

_BE_VERBS = frozenset(
    {"be", "been", "being", "am", "is", "are", "was", "were", "get", "gets", "got"}
)

# Irregular past participles that do not end in the usual suffixes below.
_IRREGULAR_PARTICIPLES = frozenset(
    {
        "done", "made", "seen", "shown", "given", "taken", "written", "known",
        "found", "held", "built", "sent", "kept", "told", "read", "set", "put",
        "run", "cut", "led", "met", "paid", "said", "left", "lost", "meant",
        "drawn", "grown", "thrown", "chosen", "broken", "spoken", "driven",
        "hidden", "beaten", "bound", "brought", "caught", "taught", "sought",
        "bought", "understood",
    }
)

# Words that look like participles but are almost always something else here.
_STOP_PARTICIPLES = frozenset({"used", "based", "supposed", "aged", "naked"})


def _looks_like_participle(word: str) -> bool:
    """Return ``True`` when ``word`` is plausibly a past participle."""
    lowered = word.lower()
    if lowered in _STOP_PARTICIPLES:
        return False
    if lowered in _IRREGULAR_PARTICIPLES:
        return True
    return lowered.endswith(("ed", "en")) and len(lowered) > 3


@dataclass(frozen=True)
class PassiveSentence:
    """A sentence flagged as likely passive.

    ``index`` is the 0-based position of the sentence within the chapter,
    ``sentence`` the trimmed sentence text, and ``trigger`` the ``be-verb
    participle`` pair that caused the flag.
    """

    index: int
    sentence: str
    trigger: str


def _prose_sentences(text: str) -> list[str]:
    """Split chapter prose into sentences, ignoring code and headings."""
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
        else:
            if line.lstrip().startswith(fence):
                fence = None
            continue
        if _ATX.match(line):
            continue
        kept.append(line)

    flat = re.sub(r"\s+", " ", "\n".join(kept)).strip()
    if not flat:
        return []

    sentences: list[str] = []
    start = 0
    for m in _TERMINATOR.finditer(flat):
        end = m.end()
        if end < len(flat) and not flat[end].isspace():
            continue
        chunk = flat[start:end].strip()
        if chunk:
            sentences.append(chunk)
        start = end
    tail = flat[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def _find_trigger(sentence: str) -> str | None:
    """Return the ``be-verb participle`` trigger in ``sentence`` if any."""
    tokens = _WORD.findall(sentence)
    for i, token in enumerate(tokens[:-1]):
        if token.lower() not in _BE_VERBS:
            continue
        nxt = tokens[i + 1]
        # Allow one intervening adverb (typically ``-ly``).
        if nxt.lower().endswith("ly") and i + 2 < len(tokens):
            participle = tokens[i + 2]
        else:
            participle = nxt
        if _looks_like_participle(participle):
            return f"{token} {participle}"
    return None


def find_passive_sentences(text: str) -> list[PassiveSentence]:
    """Return the sentences in ``text`` that look passive, in order.

    A sentence is flagged when it contains a form of *to be* (or ``get``)
    directly followed by a likely past participle, optionally with an adverb in
    between. An empty list means no passive constructions were detected.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    flagged: list[PassiveSentence] = []
    for index, sentence in enumerate(_prose_sentences(text)):
        trigger = _find_trigger(sentence)
        if trigger is not None:
            flagged.append(
                PassiveSentence(index=index, sentence=sentence, trigger=trigger)
            )
    return flagged


def passive_ratio(text: str) -> float:
    """Return the fraction of sentences flagged as passive (0.0-1.0).

    Returns 0.0 when the chapter contains no sentences.
    """
    sentences = _prose_sentences(text)
    if not sentences:
        return 0.0
    return len(find_passive_sentences(text)) / len(sentences)
