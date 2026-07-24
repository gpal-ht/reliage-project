"""Correctness tests for the ICC engine.

The canonical reference is the worked example in Shrout & Fleiss (1979),
Table 1: 6 subjects (targets) rated by 4 judges (measurements). The published
ICC values for that table are:

    ICC(1,1) = 0.17
    ICC(2,1) = 0.29
    ICC(3,1) = 0.71

Reproducing those three numbers to two decimals is an independent,
literature-anchored verification that the two-way ANOVA decomposition and all
three ICC forms are implemented correctly.
"""

import numpy as np
import pytest

from reliage.icc import compute_icc, koo_li_band

# Shrout & Fleiss (1979), Table 1.  rows = subjects, cols = judges/measurements.
SHROUT_FLEISS = np.array(
    [
        [9, 2, 5, 8],
        [6, 1, 3, 2],
        [8, 4, 6, 8],
        [7, 1, 2, 6],
        [10, 5, 6, 9],
        [6, 2, 4, 7],
    ],
    dtype=float,
)


@pytest.mark.parametrize(
    "form,expected",
    [("ICC1", 0.17), ("ICC2", 0.29), ("ICC3", 0.71)],
)
def test_icc_matches_shrout_fleiss(form, expected):
    res = compute_icc(SHROUT_FLEISS, form=form)
    assert res.icc == pytest.approx(expected, abs=0.005), (
        f"{form}: got {res.icc:.4f}, expected {expected}"
    )


def test_ci_brackets_point_estimate():
    res = compute_icc(SHROUT_FLEISS, form="ICC2")
    assert res.ci_low <= res.icc <= res.ci_high
    assert -1.0 <= res.ci_low <= res.ci_high <= 1.0


def test_perfect_agreement_is_one():
    # Identical repeated measurements => ICC = 1.
    data = np.array([[10.0, 10.0], [20.0, 20.0], [30.0, 30.0], [40.0, 40.0]])
    res = compute_icc(data, form="ICC2")
    assert res.icc == pytest.approx(1.0, abs=1e-9)
    assert res.band == "excellent"


def test_rejects_nan():
    data = np.array([[1.0, np.nan], [2.0, 3.0]])
    with pytest.raises(ValueError):
        compute_icc(data)


def test_rejects_degenerate_shape():
    with pytest.raises(ValueError):
        compute_icc(np.array([[1.0, 2.0]]))  # only 1 subject


def test_koo_li_bands():
    assert koo_li_band(0.95) == "excellent"
    assert koo_li_band(0.80) == "good"
    assert koo_li_band(0.60) == "moderate"
    assert koo_li_band(0.30) == "poor"
