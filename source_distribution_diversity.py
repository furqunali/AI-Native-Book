"""Deterministic diversity metrics for knowledge-source distribution."""
from __future__ import annotations
from dataclasses import dataclass
from knowledge_distribution import SourceDistribution

@dataclass(frozen=True)
class DistributionDiversity:
    source_count: int
    chunk_count: int
    ideal_share: float
    concentration_gap: float

def measure_distribution_diversity(distribution: SourceDistribution) -> DistributionDiversity:
    if distribution.sources < 0 or distribution.chunks < 0:
        raise ValueError("distribution counts must be non-negative")
    if distribution.sources == 0 or distribution.chunks == 0:
        return DistributionDiversity(0, distribution.chunks, 0.0, 0.0)
    ideal = 1.0 / distribution.sources
    return DistributionDiversity(
        distribution.sources,
        distribution.chunks,
        round(ideal, 4),
        round(max(distribution.concentration - ideal, 0.0), 4),
    )
