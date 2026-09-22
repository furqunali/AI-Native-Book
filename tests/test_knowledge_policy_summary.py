from knowledge_policy import HealthFinding
from knowledge_policy_summary import summarize_findings


def test_summary_counts_severity_and_health():
    findings = (
        HealthFinding("DUPLICATE_IDS", "warning", "duplicate ids"),
        HealthFinding("EMPTY_CHUNKS", "error", "empty chunks"),
        HealthFinding("NOTE", "info", "ok"),
    )
    summary = summarize_findings(findings)
    assert summary.total == 3
    assert summary.errors == 1
    assert summary.warnings == 1
    assert summary.infos == 1
    assert not summary.healthy
