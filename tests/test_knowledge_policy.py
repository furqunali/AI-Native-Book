from knowledge_health import KnowledgeHealth
from knowledge_policy import evaluate_health

def test_policy_reports_duplicate_content():
    findings = evaluate_health(KnowledgeHealth(4, 2, 100, 0, 0, 2, False))
    assert [item.code for item in findings] == ["DUPLICATE_TEXTS"]

def test_policy_reports_healthy_corpus():
    findings = evaluate_health(KnowledgeHealth(4, 2, 100, 0, 0, 0, True))
    assert findings[0].code == "HEALTHY"
