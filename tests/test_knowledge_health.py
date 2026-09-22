from knowledge_health import build_health
from knowledge_manifest import KnowledgeManifest
from knowledge_quality import QualityReport


def test_build_health_combines_manifest_and_quality():
    manifest = KnowledgeManifest(3, 2, 120, (), "digest")
    quality = QualityReport(3, 0, 0, 0, True)
    assert build_health(manifest, quality).valid
    assert build_health(manifest, quality).sources == 2
