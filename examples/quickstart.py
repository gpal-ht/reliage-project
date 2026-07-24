"""Quickstart: produce a clock reliability leaderboard.

Runs entirely on synthetic scores so it works with no downloads. Swap
``simulate_replicate_scores`` for ``load_gse55763`` + ``score_samples`` to run on
the real public anchor dataset.

    python examples/quickstart.py
"""

from reliage import run_reliability_benchmark, simulate_replicate_scores

# Four synthetic clocks spanning the reliability spectrum. "ClockDriftGood" is
# a clock that is internally consistent but carries a systematic offset between
# the two measurement occasions (e.g. a batch/plate effect): it demonstrates why
# ICC(2,1) absolute agreement — not mere correlation — is the right metric.
targets = {
    "ClockExcellent": 0.95,
    "ClockDriftGood": 0.90,
    "ClockModerate": 0.60,
    "ClockPoor": 0.30,
}
scores, groups = simulate_replicate_scores(
    n_subjects=1000,
    k=2,
    clock_iccs=targets,
    seed=7,
    measurement_bias={"ClockDriftGood": 4.0},  # 4-year systematic drift between reps
)

print("Absolute agreement (ICC2,1) — the correct test-retest metric:")
board2 = run_reliability_benchmark(scores, groups, form="ICC2", k=2)
print(board2.to_markdown())

print("\nConsistency (ICC3,1) — blind to systematic drift, shown for contrast:")
board3 = run_reliability_benchmark(scores, groups, form="ICC3", k=2)
print(board3.to_markdown())

print(
    "\nNote how ClockDriftGood scores well on consistency but is downgraded by\n"
    "absolute agreement — exactly the failure mode a reliability benchmark must\n"
    "catch, and the reason ICC(2,1) is the default."
)
