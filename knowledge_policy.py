"""Policy findings derived from deterministic knowledge health reports."""
from __future__ import annotations
from dataclasses import dataclass
from knowledge_health import KnowledgeHealth

@dataclass(frozen=True)
class HealthFinding:
    code: str
    severity: str
    message: str

def evaluate_health(health: KnowledgeHealth) -> tuple[HealthFinding, ...]:
    findings: list[HealthFinding] = []
    if health.chunks == 0:
        findings.append(HealthFinding("NO_CHUNKS", "error", "knowledge corpus contains no chunks"))
    if health.empty:
        findings.append(HealthFinding("EMPTY_CHUNKS", "error", f"{health.empty} chunks have empty content"))
    if health.duplicate_ids:
        findings.append(HealthFinding("DUPLICATE_IDS", "warning", f"{health.duplicate_ids} duplicate chunk ids detected"))
    if health.duplicate_texts:
        findings.append(HealthFinding("DUPLICATE_TEXTS", "warning", f"{health.duplicate_texts} duplicate chunk texts detected"))
    if health.valid and not findings:
        findings.append(HealthFinding("HEALTHY", "info", "knowledge corpus passed all health checks"))
    return tuple(findings)
