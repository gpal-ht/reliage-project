"""Tests for the reliability benchmark runner."""

import numpy as np
import pandas as pd
import pytest

from reliage import (
    build_replicate_matrix,
    run_reliability_benchmark,
    simulate_replicate_scores,
)


def test_recovers_known_iccs_and_ranking():
    targets = {"A": 0.95, "B": 0.80, "C": 0.55, "D": 0.25}
    scores, groups = simulate_replicate_scores(
        n_subjects=4000, k=2, clock_iccs=targets, seed=1
    )
    board = run_reliability_benchmark(scores, groups, form="ICC2", k=2)
    frame = board.frame.set_index("clock")
    for clock, target in targets.items():
        assert frame.loc[clock, "icc"] == pytest.approx(target, abs=0.04)
    assert list(board.frame["clock"]) == ["A", "B", "C", "D"]


def test_absolute_agreement_penalises_systematic_drift():
    # A clock with a big between-measurement offset should score much lower on
    # absolute agreement (ICC2) than on consistency (ICC3).
    scores, groups = simulate_replicate_scores(
        n_subjects=2000, k=2, clock_iccs={"Drift": 0.90}, seed=3,
        measurement_bias={"Drift": 8.0},
    )
    icc2 = run_reliability_benchmark(scores, groups, form="ICC2").frame.iloc[0]["icc"]
    icc3 = run_reliability_benchmark(scores, groups, form="ICC3").frame.iloc[0]["icc"]
    assert icc3 - icc2 > 0.1


def test_build_replicate_matrix_drops_incomplete_subjects():
    scores = pd.Series(
        {"s1a": 1.0, "s1b": 2.0, "s2a": 3.0, "s3a": 5.0, "s3b": 6.0},
    )
    groups = {"s1": ["s1a", "s1b"], "s2": ["s2a"], "s3": ["s3a", "s3b"]}
    m = build_replicate_matrix(scores, groups, k=2)
    assert m.shape == (2, 2)  # s2 dropped (only 1 replicate)


def test_undefined_when_no_replicates():
    scores = pd.DataFrame({"Clk": [1.0, 2.0]}, index=["a", "b"])
    groups = {"s1": ["a"], "s2": ["b"]}  # no subject has 2 replicates
    board = run_reliability_benchmark(scores, groups, k=2)
    row = board.frame.iloc[0]
    assert np.isnan(row["icc"]) and row["band"] == "undefined"
