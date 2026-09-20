"""Validate citations against the knowledge-source IDs."""
from __future__ import annotations
import re
_CITATION = re.compile(r"(?<!\!)\[([^\]\n]+)\](?!\()")
def extract_citations(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(match.strip() for match in _CITATION.findall(text) if match.strip()))
def validate_citations(text: str, known_ids: set[str]) -> tuple[str, ...]:
    return tuple(citation for citation in extract_citations(text) if citation not in known_ids)
