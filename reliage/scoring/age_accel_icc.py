"""Age-acceleration ICC for the GSE55763 run (companion to raw-age ICC).

Age acceleration = residual of clock score regressed on chronological age.
Because both technical replicates of a subject share the same age, residualizing
subtracts an identical value from each member of a pair -> within-subject
(technical) variance is UNCHANGED; only the between-subject variance shrinks, so
ICC drops. The variance-ratio primary endpoint and SEM/MDC95 are invariant.
Higgins-Chen report both raw-age and age-acceleration ICC; so do we.
"""
import sys, numpy as np, pandas as pd
from reliage.scoring.run_analysis import load_scores_wide, load_map, DEFAULT_PAIRS
from reliage.benchmark import run_reliability_benchmark
from reliage.contrast import run_paired_contrasts

scores_csv, map_csv, pheno_csv = sys.argv[1], sys.argv[2], sys.argv[3]
# optional 4th arg = output CSV path (default keeps M1 behaviour / reproduction intact)
out_csv = sys.argv[4] if len(sys.argv) > 4 else "generated/GSE55763/out/leaderboard_ageaccel.csv"
wide = load_scores_wide(scores_csv)               # index=sample_id, cols=clock labels
groups = load_map(map_csv)
pheno = pd.read_csv(pheno_csv).set_index("sample_id")
age = pheno["age"].reindex(wide.index).astype(float)

# Age-acceleration residuals: score - OLS(score ~ age) per clock label.
accel = wide.copy()
for c in wide.columns:
    y = wide[c].astype(float).values
    b1, b0 = np.polyfit(age.values, y, 1)
    accel[c] = y - (b0 + b1 * age.values)

raw_board   = run_reliability_benchmark(wide,  groups, form="ICC2", k=2).frame.set_index("clock")
accel_board = run_reliability_benchmark(accel, groups, form="ICC2", k=2).frame.set_index("clock")

print("=== ICC(2,1): raw-age vs age-acceleration (n=36 pairs) ===")
print(f"{'clock':<12}{'ICC_raw':>9}{'ICC_accel':>11}{'SEM_raw':>9}{'SEM_accel':>11}")
for c in raw_board.index:
    print(f"{c:<12}{raw_board.loc[c,'icc']:>9.3f}{accel_board.loc[c,'icc']:>11.3f}"
          f"{raw_board.loc[c,'sem']:>9.2f}{accel_board.loc[c,'sem']:>11.2f}")

pairs = [(o, t) for (o, t) in DEFAULT_PAIRS if o in accel.columns and t in accel.columns]
raw_ctr   = run_paired_contrasts(wide,  groups, pairs, n_boot=2000).set_index("original")
accel_ctr = run_paired_contrasts(accel, groups, pairs, n_boot=2000).set_index("original")
print("\n=== variance ratio (PC/original): raw vs age-accel (should be identical) ===")
print(f"{'pair':<12}{'VR_raw':>9}{'VR_accel':>10}")
for o in raw_ctr.index:
    print(f"{o:<12}{raw_ctr.loc[o,'variance_ratio']:>9.3f}{accel_ctr.loc[o,'variance_ratio']:>10.3f}")

# write a small companion artifact (all columns the benchmark provides)
import os as _os
_os.makedirs(_os.path.dirname(out_csv) or ".", exist_ok=True)
accel_board.reset_index().round(3).to_csv(out_csv, index=False)
print("\nwrote", out_csv, "| cols:", list(accel_board.columns))
