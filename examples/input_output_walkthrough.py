"""INPUT -> OUTPUT walkthrough for reliage.

Shows, on a tiny realistically-shaped example, exactly what the reliability
experiment consumes and produces. Run:

    python examples/input_output_walkthrough.py

Nothing here is real biology — the shapes and column meanings are what matter.
"""

import numpy as np
import pandas as pd

from reliage import run_reliability_benchmark, score_samples, linear_clock

rng = np.random.default_rng(0)
pd.set_option("display.width", 120)

# ---------------------------------------------------------------------------
# INPUT 1 — a DNA methylation beta matrix: rows = samples, cols = CpG sites.
# Each subject is measured TWICE (technical replicates: rep A and rep B).
# ---------------------------------------------------------------------------
subjects = {
    "P1": 41.0, "P2": 53.0, "P3": 62.0, "P4": 47.0, "P5": 69.0, "P6": 58.0,
}  # subject -> true chronological age (drives the "signal" CpGs)

cpgs_signal = [f"cg_sig{i}" for i in range(4)]   # track age tightly, low noise
cpgs_noisy  = [f"cg_noise{i}" for i in range(4)] # weak age signal, high noise
all_cpgs = cpgs_signal + cpgs_noisy

rows, sample_ids, subject_of = [], [], []
for subj, age in subjects.items():
    for rep in ("a", "b"):
        sid = f"{subj}_{rep}"
        sample_ids.append(sid); subject_of.append(subj)
        beta = {}
        for c in cpgs_signal:  # tight age relationship, small replicate noise
            beta[c] = np.clip(0.01 * age + rng.normal(0, 0.01), 0, 1)
        for c in cpgs_noisy:   # weak age signal, large replicate noise
            beta[c] = np.clip(0.005 * age + rng.normal(0, 0.06), 0, 1)
        rows.append(beta)
betas = pd.DataFrame(rows, index=sample_ids)[all_cpgs]
betas.index.name = "sample_id"

print("=" * 78)
print("INPUT 1 — methylation beta matrix  (samples x CpG sites), values in [0,1]")
print("=" * 78)
print(betas.round(3).to_string())

# ---------------------------------------------------------------------------
# INPUT 2 — the replicate map: which samples are repeats of the same subject.
# ---------------------------------------------------------------------------
replicate_groups = {}
for sid, subj in zip(sample_ids, subject_of):
    replicate_groups.setdefault(subj, []).append(sid)

print("\n" + "=" * 78)
print("INPUT 2 — replicate map  (subject -> its repeat sample ids)")
print("=" * 78)
for subj, ids in replicate_groups.items():
    print(f"  {subj}: {ids}")

# ---------------------------------------------------------------------------
# STEP — compute clock scores from betas. Two toy linear clocks:
#   GoodClock reads the stable signal CpGs; ShakyClock reads the noisy ones.
# (Real clocks: published CpG coefficients; here, illustrative weights.)
# ---------------------------------------------------------------------------
good = linear_clock(pd.Series({c: 90.0 for c in cpgs_signal}), intercept=5.0)
shaky = linear_clock(pd.Series({c: 180.0 for c in cpgs_noisy}), intercept=5.0)
scores = score_samples(betas, {"GoodClock": good, "ShakyClock": shaky})

print("\n" + "=" * 78)
print("INTERMEDIATE — clock scores  (samples x clocks), each value a biological age")
print("=" * 78)
print(scores.round(2).to_string())

# ---------------------------------------------------------------------------
# OUTPUT — the reliability leaderboard. This is the deliverable.
# ---------------------------------------------------------------------------
board = run_reliability_benchmark(scores, replicate_groups, form="ICC2", k=2)

print("\n" + "=" * 78)
print("OUTPUT — reliability leaderboard  (one row per clock)")
print("=" * 78)
print(board.to_markdown())
print(
    "\nReading it (each value is in the clock's OWN unit — years for age clocks):\n"
    "  ICC               - between-person variance / (between-person + error variance).\n"
    "                      Depends on the sample's between-person spread, so it is NOT a\n"
    "                      pure error measure; always read it WITH the absolute columns.\n"
    "  Within-subject SD - SD of technical error on ONE measurement.\n"
    "  Mean abs diff     - typical |rep1 - rep2| between two repeats. NOTE: this is a\n"
    "                      different quantity; SD(rep1-rep2) = sqrt(2) * within-subject SD.\n"
    "  Individual MDC95  - the change in ONE person's value that exceeds technical noise\n"
    "                      at 95% (= 1.96*sqrt(2)*SD). NOT a trial-level effect: a large\n"
    "                      trial can detect a group-average change far smaller than this.\n"
    "  Reliability       - Koo & Li band of the POINT estimate; read the CI too (see below).\n"
    "\nGoodClock is reliable with a small error; ShakyClock has a large within-subject SD.\n"
    "But note ShakyClock's CI (0.015-0.962): with n=6 the data are compatible with anything\n"
    "from poor to excellent, so the 'good' chip is misleading on its own. On the real data\n"
    "(n~36-72 pairs) precision improves. Whether PC clocks beat their originals is the\n"
    "prespecified HYPOTHESIS to evaluate (supported / partial / not / inconclusive) — not a\n"
    "required result."
)
