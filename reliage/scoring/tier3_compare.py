"""Tier-3 published-reference comparison (reliage vs Higgins-Chen 2022).

Compares reliage's frozen M1 outputs to the pinned published anchors (from
docs/PIR03-C2/acceptance/published_reference_cases.yaml) within the tolerances locked in
docs/PIR03-C2/TIER3_PROTOCOL.md. GSE55763 is the same cohort the source study used, so
median/max |replicate diff| AND raw ICC are directly comparable.

Usage:
  python -m reliage.scoring.tier3_compare  <M1_out_dir>  [out_tier3_dir]
Primary verdict rests on the RESOLVED absolute-difference anchors (Horvath1, GrimAge).
"""
import os, sys, pandas as pd

out = sys.argv[1] if len(sys.argv) > 1 else "datasets/GSE55763/out"
t3 = sys.argv[2] if len(sys.argv) > 2 else "datasets/GSE55763/out_tier3"
os.makedirs(t3, exist_ok=True)

# --- pinned published anchors (Higgins-Chen 2022; see published_reference_cases.yaml) ---
PUB_ABSDIFF = {"Horvath1": (2.1, 5.4), "GrimAge": (0.9, 2.4)}          # (median, max) specific values
OTHERS_MED, OTHERS_MAX = (0.9, 2.4), (4.5, 8.6)                          # coarse ranges for Hannum/PhenoAge
PC_RAW_MIN, PC_ACCEL = 0.985, (0.94, 1.0)                               # PC raw >=0.985; accel 0.97+-0.03
HORV_RAW, HORV_ACCEL = (0.925, 0.965), (0.787, 0.847)                   # 0.945+-0.02, 0.817+-0.03
PC_FRAC_MIN = 0.75

d = pd.read_csv(f"{out}/robustness/pair_diffs.csv")
lb = pd.read_csv(f"{out}/leaderboard.csv").set_index("clock")
la = pd.read_csv(f"{out}/leaderboard_ageaccel.csv").set_index("clock")
me = (d.groupby("clock").absdiff
        .agg(median_abs="median", max_abs="max",
             frac_le_1p5=lambda s: (s <= 1.5).mean()).round(3))
me.reset_index().to_csv(f"{t3}/reliage_absdiff.csv", index=False)

def within(x, lo, hi):
    return bool(lo <= x <= hi)

primary, secondary = [], []
# PRIMARY: specific-value clocks, median +-0.5 / max +-1.5
for c, (pm, px) in PUB_ABSDIFF.items():
    primary.append(within(me.loc[c, "median_abs"], pm-0.5, pm+0.5))
    primary.append(within(me.loc[c, "max_abs"],    px-1.5, px+1.5))
# PC-ICC bands (part of the PASS condition)
pc = ["PCHorvath1", "PCHannum", "PCPhenoAge", "PCGrimAge"]
pc_icc_ok = all(lb.loc[p, "icc"] >= PC_RAW_MIN for p in pc) and \
            all(within(la.loc[p, "icc"], *PC_ACCEL) for p in pc)
# SECONDARY: others in coarse ranges; Horvath1 orig ICC; PC frac<=1.5
for c in ["Hannum", "PhenoAge"]:
    secondary.append(within(me.loc[c, "median_abs"], *OTHERS_MED))
    secondary.append(within(me.loc[c, "max_abs"], *OTHERS_MAX))
secondary.append(within(lb.loc["Horvath1", "icc"], *HORV_RAW))
secondary.append(within(la.loc["Horvath1", "icc"], *HORV_ACCEL))
secondary += [me.loc[p, "frac_le_1p5"] >= PC_FRAC_MIN for p in pc]

primary_pass = all(primary) and pc_icc_ok
verdict = ("PASS" if primary_pass and all(secondary)
           else "PARTIAL" if primary_pass else "NOT MET")

print("reliage median/max |diff| (original clocks):")
print(me.loc[["Horvath1", "Hannum", "PhenoAge", "GrimAge"], ["median_abs", "max_abs"]].to_string())
print(f"\nprimary (Horvath1/GrimAge median+max + PC-ICC bands): {'PASS' if primary_pass else 'FAIL'}")
print(f"secondary checks: {sum(secondary)}/{len(secondary)} pass")
print(f"TIER-3 VERDICT: {verdict}")
print(f"(primary rests on RESOLVED absolute-difference anchors; wrote {t3}/reliage_absdiff.csv)")
