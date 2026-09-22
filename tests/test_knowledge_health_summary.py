from knowledge_health import KnowledgeHealth
from knowledge_health_summary import summarize_health


def test_summary_marks_clean_health_healthy():
    health = KnowledgeHealth(4, 2, 300, 0, 0, 0, True)
    assert summarize_health(health) == summarize_health(health)
    assert summarize_health(health).status == "healthy"
    assert summarize_health(health).issues == ()


def test_summary_collects_quality_issues():
    health = KnowledgeHealth(4, 2, 300, 1, 2, 3, False)
    summary = summarize_health(health)
    assert summary.status == "attention"
    assert summary.issues == (
        "1 empty chunks",
        "2 duplicate chunk ids",
        "3 duplicate chunk texts",
        "quality report is invalid",
    )
