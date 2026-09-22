"""Actionable summary helpers for AI-Native Book corpus health."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_health import KnowledgeHealth


@dataclass(frozen=True)
class HealthSummary:
    status: str
    issues: tuple[str, ...]


def summarize_health(health: KnowledgeHealth) -> HealthSummary:
    """Classify corpus health without changing the underlying report."""
    issues: list[str] = []
    if health.empty:
        issues.append(f"{health.empty} empty chunks")
    if health.duplicate_ids:
        issues.append(f"{health.duplicate_ids} duplicate chunk ids")
    if health.duplicate_texts:
        issues.append(f"{health.duplicate_texts} duplicate chunk texts")
    if not health.valid:
        issues.append("quality report is invalid")
    return HealthSummary("healthy" if not issues else "attention", tuple(issues))
