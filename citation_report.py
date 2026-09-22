"""Deterministic citation coverage metrics for generated answers."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_citation import extract_citations, validate_citations


@dataclass(frozen=True)
class CitationReport:
    citations: tuple[str, ...]
    unknown: tuple[str, ...]
    coverage: float

def build_citation_report(text: str, known_ids: set[str]) -> CitationReport:
    citations = extract_citations(text)
    unknown = validate_citations(text, known_ids)
    valid = len(citations) - len(unknown)
    coverage = round(valid / len(citations), 3) if citations else 0.0
    return CitationReport(citations, unknown, coverage)
