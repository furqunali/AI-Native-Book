from knowledge_distribution import SourceDistribution
from source_distribution_profile import profile_distribution
import pytest

def test_profile_reports_source_share_and_gap():
    p = profile_distribution(SourceDistribution(3, 10, 5, 2, 0.5))
    assert p.source_share == 0.5
    assert p.chunk_share_gap == 0.3
    assert p.balanced

def test_profile_marks_concentrated_distribution():
    assert not profile_distribution(SourceDistribution(2, 10, 9, 1, 0.9)).balanced

def test_profile_rejects_invalid_threshold():
    with pytest.raises(ValueError, match="threshold"):
        profile_distribution(SourceDistribution(1, 1, 1, 1, 1.0), balanced_threshold=0)
