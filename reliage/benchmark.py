"""Reliability benchmark runner and leaderboard.

The benchmark takes, for a set of subjects each measured >= k times (technical
replicates), a table of clock *scores* (one age estimate per sample per clock),
and produces a per-clock test-retest ICC leaderboard.

Two ways to supply scores:

1. **Score-based (default, no methylation data required).** You already have a
   ``scores`` table indexed by sample id with one column per clock. This is the
   path the minimal reproducible slice uses, and the path you use when clock
   values were computed elsewhere (e.g. by ComputAgeBench or methylCIPHER).

2. **Clock-based.** You supply a beta matrix and a set of clock callables; the
   runner computes scores first via :func:`score_samples`. See
   :mod:`reliage.clocks`.

The separation matters: the reliability question is about the *scores*, so the
benchmark's verified core never needs to touch a multi-gigabyte methylation
matrix. Whatever produced the scores, reliability is computed identically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from .icc import ICCForm, compute_icc, koo_li_band

# A replicate design maps subject_id -> ordered list of that subject's sample ids.
ReplicateGroups = Mapping[str, Sequence[str]]


def build_replicate_matrix(
    scores: pd.Series,
    replicate_groups: ReplicateGroups,
    k: int,
) -> np.ndarray:
    """Assemble a balanced (n_subjects x k) matrix for one clock.

    Parameters
    ----------
    scores:
        Series of clock scores indexed by sample id.
    replicate_groups:
        subject_id -> list of that subject's replicate sample ids.
    k:
        Number of measurements per subject to use. Subjects with fewer than
        ``k`` non-missing replicates are dropped; subjects with more use their
        first ``k`` (in the order given).

    Returns
    -------
    np.ndarray of shape (n_kept_subjects, k). May have 0 rows if nothing
    qualifies (the caller reports that as an undefined ICC rather than raising).
    """
    rows = []
    for _subject, sample_ids in replicate_groups.items():
        vals = [scores[s] for s in sample_ids if s in scores.index]
        vals = [v for v in vals if pd.notna(v)]
        if len(vals) >= k:
            rows.append(vals[:k])
    if not rows:
        return np.empty((0, k), dtype=float)
    return np.asarray(rows, dtype=float)


@dataclass(frozen=True)
class ClockReliability:
    clock: str
    icc: float
    ci_low: float
    ci_high: float
    band: str
    n_subjects: int
    k: int
    form: ICCForm
    sem: float = float("nan")       # within-subject SD (clock's own unit)
    mean_abs_diff: float = float("nan")  # mean |rep1 - rep2| across subjects (k=2)
    mdc95: float = float("nan")     # individual smallest detectable change (95%)


class ReliabilityLeaderboard:
    """A ranked table of per-clock reliability results."""

    def __init__(self, rows: Iterable[ClockReliability], form: ICCForm):
        self._df = pd.DataFrame([r.__dict__ for r in rows])
        if not self._df.empty:
            self._df = self._df.sort_values(
                "icc", ascending=False, na_position="last"
            ).reset_index(drop=True)
        self.form = form

    @property
    def frame(self) -> pd.DataFrame:
        return self._df

    def to_markdown(self) -> str:
        if self._df.empty:
            return "_(no clocks with a computable ICC)_"
        d = self._df.copy()
        d["ICC"] = d["icc"].map(lambda x: f"{x:.3f}")
        d["95% CI"] = [
            f"({lo:.3f}, {hi:.3f})" if pd.notna(lo) else "—"
            for lo, hi in zip(d["ci_low"], d["ci_high"])
        ]
        # NOTE: within-subject SD, mean abs diff and Individual MDC95 are in each
        # clock's OWN unit (years for age clocks, PACE units for DunedinPACE, kb for
        # DNAmTL). Units come from the versioned clock manifest, never inferred from
        # the clock name. These three are DIFFERENT quantities:
        #   within-subject SD  = SD of technical error on ONE measurement
        #   mean abs diff      = typical |rep1 - rep2|  (= ~sqrt(2)*SD in expectation)
        #   Individual MDC95   = 1.96*sqrt(2)*SD, the per-person change exceeding noise
        d["Within-subject SD"] = d["sem"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
        d["Mean abs diff"] = d["mean_abs_diff"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
        d["Individual MDC95"] = d["mdc95"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
        d = d.rename(
            columns={
                "clock": "Clock",
                "band": "Reliability",
                "n_subjects": "n",
                "k": "k",
            }
        )
        cols = ["Clock", "ICC", "95% CI", "Within-subject SD", "Mean abs diff",
                "Individual MDC95", "Reliability", "n", "k"]
        lines = ["| " + " | ".join(cols) + " |",
                 "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in d.iterrows():
            lines.append(
                "| " + " | ".join(str(r[c]) for c in cols) + " |"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<ReliabilityLeaderboard form={self.form} clocks={len(self._df)}>\n" + self.to_markdown()


def run_reliability_benchmark(
    scores: pd.DataFrame,
    replicate_groups: ReplicateGroups,
    clocks: Sequence[str] | None = None,
    form: ICCForm = "ICC2",
    k: int = 2,
    confidence: float = 0.95,
) -> ReliabilityLeaderboard:
    """Compute a per-clock test-retest reliability leaderboard.

    Parameters
    ----------
    scores:
        DataFrame indexed by sample id, one column per clock, values are age
        (or pace) estimates.
    replicate_groups:
        subject_id -> ordered list of replicate sample ids for that subject.
    clocks:
        Which columns of ``scores`` to evaluate. Defaults to all columns.
    form:
        ICC form (default ``"ICC2"`` — absolute-agreement two-way random, the
        appropriate choice for test-retest reliability).
    k:
        Replicates per subject to use (default 2, i.e. duplicate pairs such as
        the 36 in GSE55763).
    confidence:
        Confidence level for the reported intervals.

    Returns
    -------
    ReliabilityLeaderboard, ranked by ICC descending.
    """
    if clocks is None:
        clocks = list(scores.columns)
    results: list[ClockReliability] = []
    for clock in clocks:
        matrix = build_replicate_matrix(scores[clock], replicate_groups, k=k)
        if matrix.shape[0] < 2:
            results.append(
                ClockReliability(clock, float("nan"), float("nan"),
                                 float("nan"), "undefined", matrix.shape[0], k, form)
            )
            continue
        res = compute_icc(matrix, form=form, confidence=confidence)
        # Mean absolute replicate difference (the intuitive paired quantity): for
        # duplicate designs uses the two replicates. Distinct from within-subject
        # SD, since SD(rep1-rep2) = sqrt(2)*within-subject SD.
        if matrix.shape[1] >= 2:
            diffs = np.abs(matrix[:, 0] - matrix[:, 1])
            mean_abs_diff = float(np.mean(diffs))
        else:
            mean_abs_diff = float("nan")
        results.append(
            ClockReliability(
                clock=clock,
                icc=res.icc,
                ci_low=res.ci_low,
                ci_high=res.ci_high,
                band=koo_li_band(res.icc),
                n_subjects=res.n_subjects,
                k=k,
                form=form,
                sem=res.sem,
                mean_abs_diff=mean_abs_diff,
                mdc95=res.mdc95,
            )
        )
    return ReliabilityLeaderboard(results, form=form)


def score_samples(
    betas: pd.DataFrame,
    clocks: Mapping[str, Callable[[pd.DataFrame], pd.Series]],
) -> pd.DataFrame:
    """Compute a scores table from a beta matrix and clock callables.

    Parameters
    ----------
    betas:
        DataFrame of methylation beta values, samples (rows) x CpGs (columns).
    clocks:
        Mapping of clock name -> callable(betas) -> Series of scores indexed by
        sample id. See :mod:`reliage.clocks` for adapters (incl. ComputAgeBench).

    Returns
    -------
    DataFrame indexed by sample id, one column per clock.
    """
    out = {}
    for name, fn in clocks.items():
        out[name] = fn(betas)
    return pd.DataFrame(out)
