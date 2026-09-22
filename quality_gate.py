"""Deterministic corpus quality gate built on existing quality inspection."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_quality import QualityReport, inspect_chunks


@dataclass(frozen=True)
class QualityGate:
    report: QualityReport
    passed: bool

def evaluate_quality_gate(chunks, *, max_duplicate_texts: int = 0) -> QualityGate:
    if max_duplicate_texts < 0:
        raise ValueError("max_duplicate_texts must be non-negative")
    report = inspect_chunks(chunks)
    passed = report.empty == 0 and report.duplicate_ids == 0 and report.duplicate_texts <= max_duplicate_texts
    return QualityGate(report, passed)
