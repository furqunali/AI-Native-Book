"""Derived spread metrics for knowledge-source distribution."""
from __future__ import annotations

from dataclasses import dataclass

from knowledge_distribution import SourceDistribution


@dataclass(frozen=True)
class DistributionProfile:
    source_share: float
    chunk_share_gap: float
    balanced: bool
    smallest_source_share: float

def profile_distribution(distribution: SourceDistribution, *, balanced_threshold: float = 0.5) -> DistributionProfile:
    if not 0 < balanced_threshold <= 1:
        raise ValueError("balanced_threshold must be in (0, 1]")
    if distribution.chunks == 0:
        return DistributionProfile(0.0, 0.0, True, 0.0)
    share = distribution.largest_source_chunks / distribution.chunks
    smallest_share = distribution.smallest_source_chunks / distribution.chunks
    return DistributionProfile(
        round(share, 4),
        round(share - smallest_share, 4),
        share <= balanced_threshold,
        round(smallest_share, 4),
    )
