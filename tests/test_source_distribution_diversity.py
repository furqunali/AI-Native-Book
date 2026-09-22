import pytest

from knowledge_distribution import SourceDistribution
from source_distribution_diversity import measure_distribution_diversity


def test_diversity_reports_ideal_share_and_gap():
    d = measure_distribution_diversity(SourceDistribution(4, 20, 10, 2, .5))
    assert (d.source_count, d.chunk_count, d.ideal_share, d.concentration_gap) == (4,20,.25,.25)

def test_diversity_handles_empty_distribution():
    assert measure_distribution_diversity(SourceDistribution(0,0,0,0,0)).ideal_share == 0.0

def test_diversity_rejects_negative_counts():
    with pytest.raises(ValueError, match="counts"):
        measure_distribution_diversity(SourceDistribution(-1,2,1,1,.5))
