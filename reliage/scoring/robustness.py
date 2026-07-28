"""Robustness audit for the GSE55763 PC-vs-original reliability result.

Parts (per the analysis plan):
  1. Signal-preservation / compression audit  (between vs within variance, age
     association, ranking preservation) -> compression_audit.csv
  2. Leave-one-subject-out influence          (VR, ICC, SEM, MDC95 per omission) -> loso.csv
  3. Pair-level replicate-difference audit     (largest discrepancies, batch bias) -> pair_diffs.csv
  4. Bland-Altman diagnostics                  (bias, LoA, proportional bias)     -> bland_altman.csv

Uses reliage's own engine (compute_icc, variance_ratio_contrast, build_replicate_matrix)
so every recomputation matches the headline analysis.
"""
import os, sys, numpy as np, pandas as pd
from scipy import stats
from reliage.scoring.run_analysis import load_scores_wide, load_map, DEFAULT_PAIRS
from reliage.scoring.generated_manifest import require_csv
from reliage.benchmark import build_replicate_matrix
from reliage.icc import compute_icc, smallest_detectable_change
from reliage.contrast import variance_ratio_contrast, _var_within

scores_csv, map_csv, pheno_csv, outdir = sys.argv[1:5]
os.makedirs(outdir, exist_ok=True)
wide = load_scores_wide(scores_csv)                # guarded
groups = load_map(map_csv)                          # guarded
subjects = list(groups.keys())
pheno = require_csv(pheno_csv, "pheno")
age_by_sample = pheno.set_index("sample_id")["age"].astype(float)
subj_age = np.array([age_by_sample[groups[s][0]] for s in subjects])  # both batches share age

def mat(label):
    return build_replicate_matrix(wide[label], groups, k=2)  # (36,2), row=subject, col0=batch1

# ---------- Part 1: signal-preservation / compression audit ----------
rows1 = []
for orig, pc in DEFAULT_PAIRS:
    mo, mp = mat(orig), mat(pc)
    for name, m in ((orig, mo), (pc, mp)):
        means = m.mean(axis=1)
        d = m[:, 0] - m[:, 1]
        within = _var_within(m)                       # two-way residual MSE (batch-drift removed)
        between = float(np.var(means, ddof=1))        # between-subject variance of subject means
        total = float(np.var(m.ravel(), ddof=1))
        r_age, _ = stats.pearsonr(means, subj_age)
        slope = np.polyfit(subj_age, means, 1)[0]
        std_slope = slope * subj_age.std(ddof=1) / means.std(ddof=1)
        rows1.append(dict(clock=name, is_pc=name.startswith("PC"), pair=orig,
                          within_var=within, between_var=between, total_var=total,
                          r_age=r_age, slope_age=slope, std_slope=std_slope,
                          score_range=float(means.max()-means.min()),
                          iqr=float(np.subtract(*np.percentile(means, [75, 25])))))
aud = pd.DataFrame(rows1)
# pair-level ratios + rank preservation between original and PC subject means
comp = []
for orig, pc in DEFAULT_PAIRS:
    o = aud[aud.clock == orig].iloc[0]; p = aud[aud.clock == pc].iloc[0]
    mo_means = mat(orig).mean(axis=1); mp_means = mat(pc).mean(axis=1)
    pear, _ = stats.pearsonr(mo_means, mp_means)
    spear, _ = stats.spearmanr(mo_means, mp_means)
    comp.append(dict(pair=orig,
        noise_ratio=p.within_var/o.within_var,                 # PC/orig within (= variance_ratio)
        signal_preservation_ratio=p.between_var/o.between_var,  # PC/orig between (subject means)
        total_var_ratio=p.total_var/o.total_var,
        r_age_orig=o.r_age, r_age_pc=p.r_age,
        std_slope_orig=o.std_slope, std_slope_pc=p.std_slope,
        subjmean_pearson=pear, subjmean_spearman=spear))
comp = pd.DataFrame(comp)
aud.round(4).to_csv(f"{outdir}/compression_audit.csv", index=False)
comp.round(4).to_csv(f"{outdir}/compression_summary.csv", index=False)

# ---------- Part 2: leave-one-subject-out ----------
full_vr = {}
loso_rows = []
idx_all = np.arange(len(subjects))
for orig, pc in DEFAULT_PAIRS:
    mo, mp = mat(orig), mat(pc)
    full = variance_ratio_contrast(mo, mp, n_boot=0).variance_ratio
    full_vr[orig] = full
    for j, s in enumerate(subjects):
        keep = idx_all != j
        vr = _var_within(mp[keep]) / _var_within(mo[keep])
        icc_o = compute_icc(mo[keep], "ICC2"); icc_p = compute_icc(mp[keep], "ICC2")
        loso_rows.append(dict(pair=orig, omitted=s, variance_ratio=vr,
                              d_vr=vr-full,
                              icc_orig=icc_o.icc, icc_pc=icc_p.icc,
                              sem_orig=icc_o.sem, sem_pc=icc_p.sem,
                              mdc95_orig=smallest_detectable_change(icc_o.sem),
                              mdc95_pc=smallest_detectable_change(icc_p.sem)))
loso = pd.DataFrame(loso_rows)
loso.round(4).to_csv(f"{outdir}/loso.csv", index=False)

# ---------- Part 3: pair-level replicate differences ----------
diff_rows = []
for orig, pc in DEFAULT_PAIRS:
    for name in (orig, pc):
        m = mat(name)
        for j, s in enumerate(subjects):
            diff_rows.append(dict(clock=name, subject=s,
                                  batch1=m[j, 0], batch2=m[j, 1],
                                  signed=m[j, 0]-m[j, 1], absdiff=abs(m[j, 0]-m[j, 1]),
                                  pair_mean=m[j].mean()))
diffs = pd.DataFrame(diff_rows)
diffs.round(4).to_csv(f"{outdir}/pair_diffs.csv", index=False)

# ---------- Part 4: Bland-Altman ----------
ba_rows = []
for orig, pc in DEFAULT_PAIRS:
    for name in (orig, pc):
        sub = diffs[diffs.clock == name]
        d = sub.signed.values; a = sub.absdiff.values; mn = sub.pair_mean.values
        bias = d.mean(); sd = d.std(ddof=1)
        r_prop, p_prop = stats.pearsonr(a, mn)     # |diff| vs mean -> heteroscedasticity
        ba_rows.append(dict(clock=name, is_pc=name.startswith("PC"), pair=orig,
                            batch_bias=bias, sd_diff=sd,
                            loa_low=bias-1.96*sd, loa_high=bias+1.96*sd,
                            r_absdiff_mean=r_prop, p_absdiff_mean=p_prop))
ba = pd.DataFrame(ba_rows)
ba.round(4).to_csv(f"{outdir}/bland_altman.csv", index=False)

# ---------- console summary ----------
pd.set_option("display.width", 160, "display.max_columns", 30)
print("=== PART 1: compression / signal-preservation summary ===")
print(comp.round(3).to_string(index=False))
print("\n=== PART 2: leave-one-subject-out (VR range per pair) ===")
g = loso.groupby("pair")
for orig, _ in DEFAULT_PAIRS:
    sub = g.get_group(orig)
    worst = sub.loc[sub.variance_ratio.idxmax()]
    flips = (sub.variance_ratio >= 1).sum()
    print(f"  {orig:<9} full VR={full_vr[orig]:.3f}  LOO min={sub.variance_ratio.min():.3f} "
          f"max={sub.variance_ratio.max():.3f}  worst-omit={worst.omitted}({worst.variance_ratio:.3f})  "
          f"flips(VR>=1)={flips}")
print("\n=== PART 4: Bland-Altman (batch bias & proportional bias) ===")
print(ba.round(3).to_string(index=False))
print(f"\nwrote CSVs to {outdir}/")
