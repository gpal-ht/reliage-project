"""Paired original-vs-transformed contrasts — the primary endpoint.

The headline scientific question for PIR03-C2 is not "is clock X reliable?" but
"does the PC transformation reduce a clock's technical noise?". The cleanest
metric for that is the within-subject variance ratio

    variance_ratio = var_within(transformed) / var_within(original)

computed on the SAME subjects (paired), so between-person spread cancels. A ratio
below 1 favours the transformed (PC) clock. Uncertainty comes from a paired
bootstrap that resamples *subjects* (the clustering unit), never individual
measurements.

This is deliberately separate from ICC: ICC depends on between-person
heterogeneity, the variance ratio does not, which is why the review named it the
portable primary endpoint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from .icc import _anova_mean_squares
from .benchmark import ReplicateGroups


def _var_within(matrix: np.ndarray) -> float:
    """Random within-subject variance (two-way ANOVA residual MSE), >= 0."""
    _msr, _msc, mse, _msw = _anova_mean_squares(np.asarray(matrix, dtype=float))
    return max(float(mse), 0.0)


@dataclass(frozen=True)
class ContrastResult:
    original: str
    transformed: str
    var_within_original: float
    var_within_transformed: float
    variance_ratio: float          # transformed / original; < 1 favours transformed
    ci_low: float
    ci_high: float
    confidence: float
    n_subjects: int
    n_boot: int
    verdict: str                   # supported / directionally_supported / not_supported / inconclusive

    def to_row(self) -> dict:
        return {
            "original": self.original,
            "transformed": self.transformed,
            "variance_ratio": self.variance_ratio,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "verdict": self.verdict,
            "n_subjects": self.n_subjects,
        }


def variance_ratio_contrast(
    matrix_original: np.ndarray,
    matrix_transformed: np.ndarray,
    original: str = "original",
    transformed: str = "transformed",
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> ContrastResult:
    """Within-subject variance ratio (transformed/original) with paired bootstrap CI.

    ``matrix_original`` and ``matrix_transformed`` must be the SAME shape and
    row-aligned by subject (row i = subject i's k replicate scores for each clock).
    """
    a = np.asarray(matrix_original, dtype=float)
    b = np.asarray(matrix_transformed, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"matrices must be identical shape and subject-aligned; got {a.shape} vs {b.shape}")
    if a.ndim != 2 or a.shape[0] < 2 or a.shape[1] < 2:
        raise ValueError("need a 2-D (subjects x measurements) matrix with >=2 subjects and >=2 measurements")
    n = a.shape[0]

    v_o = _var_within(a)
    v_t = _var_within(b)
    ratio = (v_t / v_o) if v_o > 0 else float("nan")

    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)          # resample SUBJECTS with replacement
        vo = _var_within(a[idx])
        vt = _var_within(b[idx])
        if vo > 0:
            boots.append(vt / vo)
    if boots:
        alpha = 1.0 - confidence
        lo, hi = np.nanpercentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    else:
        lo = hi = float("nan")

    if not np.isfinite(ratio):
        verdict = "inconclusive"
    elif np.isfinite(hi) and hi < 1.0:
        verdict = "supported"              # whole CI below 1
    elif ratio < 1.0:
        verdict = "directionally_supported"  # point < 1 but CI includes 1
    else:
        verdict = "not_supported"          # point >= 1

    return ContrastResult(
        original=original,
        transformed=transformed,
        var_within_original=v_o,
        var_within_transformed=v_t,
        variance_ratio=float(ratio),
        ci_low=float(lo),
        ci_high=float(hi),
        confidence=confidence,
        n_subjects=n,
        n_boot=len(boots),
        verdict=verdict,
    )


def _aligned_matrices(scores: pd.DataFrame, groups: ReplicateGroups,
                      original: str, transformed: str, k: int):
    """Build row-aligned n x k matrices for two clocks over subjects complete in BOTH."""
    rows_o, rows_t = [], []
    for _subject, sample_ids in groups.items():
        present = [s for s in sample_ids if s in scores.index]
        o = [scores.loc[s, original] for s in present]
        t = [scores.loc[s, transformed] for s in present]
        o = [v for v in o if pd.notna(v)]
        t = [v for v in t if pd.notna(v)]
        if len(o) >= k and len(t) >= k:
            rows_o.append(o[:k])
            rows_t.append(t[:k])
    return np.asarray(rows_o, dtype=float), np.asarray(rows_t, dtype=float)


def run_paired_contrast(
    scores: pd.DataFrame,
    groups: ReplicateGroups,
    original: str,
    transformed: str,
    k: int = 2,
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> ContrastResult:
    """Convenience: variance-ratio contrast for one original->transformed clock pair
    from a scores table + replicate map (subjects complete in both clocks)."""
    a, b = _aligned_matrices(scores, groups, original, transformed, k)
    return variance_ratio_contrast(
        a, b, original=original, transformed=transformed,
        n_boot=n_boot, confidence=confidence, seed=seed,
    )


def run_paired_contrasts(
    scores: pd.DataFrame,
    groups: ReplicateGroups,
    pairs: Sequence[tuple[str, str]],
    k: int = 2,
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> pd.DataFrame:
    """Run several (original, transformed) contrasts; return a tidy table."""
    rows = []
    for original, transformed in pairs:
        rows.append(run_paired_contrast(
            scores, groups, original, transformed, k=k,
            n_boot=n_boot, confidence=confidence, seed=seed,
        ).to_row())
    return pd.DataFrame(rows)
