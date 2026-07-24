"""Dependency-light verification (no pytest required).

Run with:  python -m reliage.selfcheck

Covers two independent correctness checks:

1. ICC engine vs. the Shrout & Fleiss (1979) canonical published values.
2. End-to-end: the benchmark recovers, within tolerance, the known target ICCs
   that the synthetic generator was told to produce.

Exit code is non-zero on any failure, so this doubles as a CI smoke test in
environments where pytest is unavailable.
"""

from __future__ import annotations

import sys

import numpy as np

from .icc import compute_icc
from .benchmark import run_reliability_benchmark
from .datasets import simulate_replicate_scores

_SHROUT_FLEISS = np.array(
    [[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8],
     [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]], dtype=float
)
_EXPECTED = {"ICC1": 0.17, "ICC2": 0.29, "ICC3": 0.71}


def check_icc_engine() -> list[str]:
    failures = []
    for form, expected in _EXPECTED.items():
        got = compute_icc(_SHROUT_FLEISS, form=form).icc
        ok = abs(got - expected) <= 0.005
        print(f"  [{'ok' if ok else 'FAIL'}] {form}: {got:.4f} (expected {expected})")
        if not ok:
            failures.append(f"{form}: {got:.4f} != {expected}")
    return failures


def check_end_to_end() -> list[str]:
    failures = []
    targets = {"ClockA": 0.95, "ClockB": 0.80, "ClockC": 0.55, "ClockD": 0.25}
    scores, groups = simulate_replicate_scores(
        n_subjects=4000, k=2, clock_iccs=targets, seed=1
    )
    board = run_reliability_benchmark(scores, groups, form="ICC2", k=2)
    frame = board.frame.set_index("clock")
    # Ranking must match the true ordering of reliability.
    ranked = list(board.frame["clock"])
    expected_order = ["ClockA", "ClockB", "ClockC", "ClockD"]
    if ranked != expected_order:
        failures.append(f"ranking {ranked} != {expected_order}")
    print(f"  ranking recovered: {ranked}")
    # Recovered ICC must be close to the target (large-N tolerance).
    for clock, target in targets.items():
        got = frame.loc[clock, "icc"]
        ok = abs(got - target) <= 0.04
        print(f"  [{'ok' if ok else 'FAIL'}] {clock}: recovered ICC {got:.3f} (target {target})")
        if not ok:
            failures.append(f"{clock}: recovered {got:.3f} vs target {target}")
    return failures


def check_variance_ratio() -> list[str]:
    """A transformed clock with HALF the noise SD => variance ratio ~0.25, CI < 1."""
    import numpy as np
    from .contrast import variance_ratio_contrast
    rng = np.random.default_rng(4)
    n = 400
    true = rng.normal(50.0, 8.0, size=n)
    so = 4.0                       # original within-subject SD
    orig = np.column_stack([true + rng.normal(0, so, n), true + rng.normal(0, so, n)])
    pc = np.column_stack([true + rng.normal(0, so / 2, n), true + rng.normal(0, so / 2, n)])
    res = variance_ratio_contrast(orig, pc, "orig", "pc", n_boot=500, seed=1)
    failures = []
    ok_ratio = abs(res.variance_ratio - 0.25) <= 0.08
    ok_verdict = res.verdict == "supported" and res.ci_high < 1.0
    print(f"  variance_ratio={res.variance_ratio:.3f} (target ~0.25), CI=({res.ci_low:.2f},{res.ci_high:.2f}), verdict={res.verdict}")
    if not ok_ratio:
        failures.append(f"variance ratio {res.variance_ratio:.3f} != ~0.25")
    if not ok_verdict:
        failures.append(f"verdict/CI wrong: {res.verdict}, ci_high={res.ci_high:.3f}")
    return failures


def check_detectability() -> list[str]:
    """Individual detectability bands for SEM=1: MDC95=2.77, MDC68=1.41."""
    from .detectability import effect_detectable
    cases = {5.0: "detectable", 2.0: "marginal", 1.0: "not_detectable"}
    failures = []
    for effect, expected in cases.items():
        got = effect_detectable(1.0, effect)["verdict"]
        print(f"  effect {effect} (SEM=1) -> {got} (expected {expected})")
        if got != expected:
            failures.append(f"detectability {effect}: {got} != {expected}")
    return failures


def main() -> int:
    print("1) ICC engine vs. Shrout & Fleiss (1979):")
    f1 = check_icc_engine()
    print("2) End-to-end benchmark recovers known ICCs:")
    f2 = check_end_to_end()
    print("3) Variance-ratio contrast recovers a known ratio:")
    f3 = check_variance_ratio()
    print("4) Experimental detectability bands:")
    f4 = check_detectability()
    failures = f1 + f2 + f3 + f4
    print()
    if failures:
        print(f"SELFCHECK FAILED ({len(failures)} issue(s)):")
        for f in failures:
            print("  -", f)
        return 1
    print("SELFCHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
