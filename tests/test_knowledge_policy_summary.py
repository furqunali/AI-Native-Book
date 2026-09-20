from knowledge_policy import HealthFinding
from knowledge_policy_summary import summarize_findings

def test_summary_counts_severity_and_health():
    findings = (
        HealthFinding("DUPLICATE_IDS", "warning", "duplicate ids"),
        HealthFinding("EMPTY_CHUNKS", "error", "empty chunks"),
        HealthFinding("NOTE", "info", "ok"),
    )
    assert summarize_findings(findings) == (3, 1, 1, 1, False)
