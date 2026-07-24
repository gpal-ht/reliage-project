"""Replicate-dataset loaders and a synthetic generator.

Reliability benchmarking needs *technical replicates*: the same biological
sample measured more than once. ComputAgeBench's benchmark data is built from
unique biological samples and therefore cannot be used here — a different,
replicate-bearing dataset is required.

Confirmed public anchor dataset
-------------------------------
**GSE55763** (Lehne et al., Genome Biol. 2015) — Illumina HumanMethylation450,
2,711 samples of which **36 are measured in duplicate**. Public since 2015,
already used as the example replicate set shipped with PC-Clocks. This is the
recommended first real dataset for the benchmark.

Other public options to widen coverage later: SATSA (ArrayExpress E-MTAB-7309)
and EPIC-array reproducibility series in the EPIC v2 validation literature.

This module provides:

* :func:`simulate_replicate_scores` — a synthetic generator with *known* target
  ICCs, used to verify end-to-end that the benchmark recovers the reliability it
  was given (see ``selfcheck``/tests).
* :func:`replicate_groups_from_metadata` — build the subject -> [sample ids]
  mapping from a GEO-style metadata table.
* :func:`load_gse55763` — documented loader for the anchor dataset (requires the
  downloaded series; see its docstring for the one-liner to fetch it).
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
import pandas as pd


def simulate_replicate_scores(
    n_subjects: int = 200,
    k: int = 2,
    clock_iccs: Mapping[str, float] | None = None,
    between_subject_sd: float = 6.0,
    seed: int = 0,
    measurement_bias: Mapping[str, float] | None = None,
):
    """Generate a synthetic (scores, replicate_groups) pair with known ICCs.

    Each clock's scores are drawn as ``subject_effect + measurement_noise`` where
    the noise SD is set so the population ICC(2,1) equals the requested target.
    This lets a test assert that the benchmark *recovers* the reliability it was
    handed — an end-to-end correctness check independent of the ICC unit tests.

    Parameters
    ----------
    n_subjects, k:
        Number of subjects and replicates per subject.
    clock_iccs:
        Mapping clock name -> target ICC in (0, 1). Defaults to a spread of
        excellent/good/moderate/poor clocks.
    between_subject_sd:
        SD of the (biological) between-subject age signal, in years.
    seed:
        RNG seed.
    measurement_bias:
        Optional clock -> per-measurement systematic offset magnitude. When set,
        replicate m gets a fixed offset, which lowers absolute-agreement ICC(2,1)
        while leaving consistency ICC(3,1) unchanged — useful for exercising the
        distinction between the two forms.

    Returns
    -------
    (scores, replicate_groups):
        ``scores`` is a DataFrame indexed by sample id (``S{subj}_{rep}``) with
        one column per clock; ``replicate_groups`` maps subject id -> sample ids.
    """
    if clock_iccs is None:
        clock_iccs = {
            "ClockExcellent": 0.95,
            "ClockGood": 0.80,
            "ClockModerate": 0.60,
            "ClockPoor": 0.30,
        }
    rng = np.random.default_rng(seed)
    sample_ids: list[str] = []
    subject_of: list[str] = []
    rep_of: list[int] = []
    replicate_groups: dict[str, list[str]] = {}
    for i in range(n_subjects):
        subj = f"S{i}"
        ids = []
        for m in range(k):
            sid = f"{subj}_{m}"
            ids.append(sid)
            sample_ids.append(sid)
            subject_of.append(subj)
            rep_of.append(m)
        replicate_groups[subj] = ids

    subject_of = np.array(subject_of)
    rep_of = np.array(rep_of)
    data = {}
    for clock, icc in clock_iccs.items():
        if not (0.0 < icc < 1.0):
            raise ValueError(f"target ICC for {clock} must be in (0,1); got {icc}")
        sigma_b = between_subject_sd
        sigma_e = sigma_b * np.sqrt((1.0 - icc) / icc)
        # One true effect per subject, shared across that subject's replicates.
        subj_index = {s: j for j, s in enumerate(replicate_groups)}
        true_effect = rng.normal(50.0, sigma_b, size=len(replicate_groups))
        vals = np.array([true_effect[subj_index[s]] for s in subject_of])
        vals = vals + rng.normal(0.0, sigma_e, size=len(subject_of))
        if measurement_bias and clock in measurement_bias:
            bias_mag = measurement_bias[clock]
            vals = vals + rep_of * bias_mag
        data[clock] = vals
    scores = pd.DataFrame(data, index=sample_ids)
    scores.index.name = "sample_id"
    return scores, replicate_groups


def replicate_groups_from_metadata(
    meta: pd.DataFrame,
    subject_col: str,
    sample_id_col: str | None = None,
    min_replicates: int = 2,
) -> dict[str, list[str]]:
    """Build subject -> [sample ids] from a metadata table.

    Only subjects with at least ``min_replicates`` samples are returned, so the
    result is exactly the replicate design usable for reliability.

    Parameters
    ----------
    meta:
        Metadata table; one row per sample.
    subject_col:
        Column identifying the biological subject (samples sharing a value are
        replicates of each other).
    sample_id_col:
        Column holding the sample id. If ``None``, the DataFrame index is used.
    min_replicates:
        Minimum replicates for a subject to be included.
    """
    ids = meta.index if sample_id_col is None else meta[sample_id_col]
    groups: dict[str, list[str]] = {}
    for sid, subj in zip(ids, meta[subject_col]):
        groups.setdefault(str(subj), []).append(str(sid))
    return {s: v for s, v in groups.items() if len(v) >= min_replicates}


def load_gse55763(betas_path: str, meta_path: str, subject_col: str = "subject"):
    """Load the GSE55763 anchor dataset (betas + replicate groups).

    This does not download anything — it parses files you have already fetched,
    keeping the benchmark reproducible from a clean environment with an explicit
    provenance trail.

    To fetch (once, ~a few GB):

    ```bash
    # Series matrix / processed betas + metadata from GEO:
    #   https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE55763
    # e.g. via GEOparse:
    #   python -c "import GEOparse; GEOparse.get_GEO('GSE55763', destdir='data/gse55763')"
    ```

    The 36 duplicate samples are identifiable from the series metadata (their
    titles/characteristics mark them as technical replicates of a base sample);
    map those to a shared ``subject`` value in ``meta`` so that
    :func:`replicate_groups_from_metadata` pairs them.

    Parameters
    ----------
    betas_path:
        Path to a samples x CpGs beta matrix (parquet or csv), index = sample id.
    meta_path:
        Path to a per-sample metadata table (parquet or csv), index = sample id,
        containing ``subject_col``.
    subject_col:
        Column grouping technical replicates.

    Returns
    -------
    (betas, replicate_groups)
    """
    betas = _read_table(betas_path)
    meta = _read_table(meta_path)
    groups = replicate_groups_from_metadata(meta, subject_col=subject_col)
    return betas, groups


def _read_table(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    if path.endswith((".csv", ".csv.gz")):
        return pd.read_csv(path, index_col=0)
    if path.endswith((".tsv", ".tsv.gz", ".txt")):
        return pd.read_csv(path, sep="\t", index_col=0)
    raise ValueError(f"unsupported file type: {path}")
