"""Aggregate deterministic knowledge policy findings."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_policy import HealthFinding


@dataclass(frozen=True)
class PolicySummary:
    total: int
    errors: int
    warnings: int
    infos: int
    healthy: bool

def summarize_findings(findings: tuple[HealthFinding, ...]) -> PolicySummary:
    errors = sum(f.severity == "error" for f in findings)
    warnings = sum(f.severity == "warning" for f in findings)
    infos = sum(f.severity == "info" for f in findings)
    return PolicySummary(
        total=len(findings),
        errors=errors,
        warnings=warnings,
        infos=infos,
        healthy=errors == 0,
    )
