"""reliage — an open, reproducible test-retest reliability benchmark for epigenetic aging clocks.

Companion to ComputAgeBench (which benchmarks clock *accuracy*): reliage
benchmarks clock *reliability* — how stable a clock's estimate is across
technical replicates of the same sample — as an ICC leaderboard on public
replicate data.
"""

from .icc import (
    ICCResult,
    compute_icc,
    koo_li_band,
    smallest_detectable_change,
    min_detectable_effect,
)
from .benchmark import (
    ClockReliability,
    ReliabilityLeaderboard,
    build_replicate_matrix,
    run_reliability_benchmark,
    score_samples,
)
from .datasets import (
    load_gse55763,
    replicate_groups_from_metadata,
    simulate_replicate_scores,
)
from .clocks import computage_clock, linear_clock
from .contrast import (
    ContrastResult,
    variance_ratio_contrast,
    run_paired_contrast,
    run_paired_contrasts,
)
from .detectability import (
    effect_detectable,
    detectability_table,
    recommend_for_effect,
)

__version__ = "0.3.1"

__all__ = [
    "compute_icc",
    "ICCResult",
    "koo_li_band",
    "smallest_detectable_change",
    "min_detectable_effect",
    "run_reliability_benchmark",
    "ReliabilityLeaderboard",
    "ClockReliability",
    "build_replicate_matrix",
    "score_samples",
    "simulate_replicate_scores",
    "replicate_groups_from_metadata",
    "load_gse55763",
    "linear_clock",
    "computage_clock",
    "variance_ratio_contrast",
    "run_paired_contrast",
    "run_paired_contrasts",
    "ContrastResult",
    "effect_detectable",
    "detectability_table",
    "recommend_for_effect",
]
