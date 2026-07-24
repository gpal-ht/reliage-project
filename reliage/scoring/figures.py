"""Figures for the robustness-qualified GSE55763 result. Writes PNGs to out/figures/.

1 forest.png            variance ratios + 95% CI, null at 1
2 paired_error.png      per-subject |replicate diff|, original -> PC, by clock family
3 bland_altman.png      original vs PC B-A panels (mean vs signed diff, bias + LoA)
4 signal_vs_noise.png   between-subject signal retained vs within-subject noise removed
5 loso.png              variance ratio by omitted subject
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out, fig = sys.argv[1], sys.argv[2]
os.makedirs(fig, exist_ok=True)
C_O, C_P = "#B5651D", "#0B6E63"   # original (amber) / PC (teal)
PAIRS = ["Horvath1", "Hannum", "PhenoAge", "GrimAge"]

contr = pd.read_csv(f"{out}/contrasts.csv")
diffs = pd.read_csv(f"{out}/robustness/pair_diffs.csv")
comp  = pd.read_csv(f"{out}/robustness/compression_summary.csv")
loso  = pd.read_csv(f"{out}/robustness/loso.csv")
ba    = pd.read_csv(f"{out}/robustness/bland_altman.csv")

# 1 -- forest -----------------------------------------------------------------
f, ax = plt.subplots(figsize=(7, 3.2))
y = np.arange(len(contr))[::-1]
ax.errorbar(contr.variance_ratio, y,
            xerr=[contr.variance_ratio - contr.ci_low, contr.ci_high - contr.variance_ratio],
            fmt="o", color=C_P, ecolor=C_P, capsize=4, ms=7)
ax.axvline(1.0, color="#c0392b", ls="--", lw=1.2, label="null (no improvement)")
for yi, r in zip(y, contr.itertuples()):
    ax.text(r.ci_high + 0.02, yi, f"{r.variance_ratio:.3f}  [{r.ci_low:.3f}, {r.ci_high:.3f}]",
            va="center", fontsize=9)
ax.set_yticks(y); ax.set_yticklabels([f"{o}→PC{o}" for o in contr.original])
ax.set_xlabel("within-subject variance ratio  (PC / original)")
ax.set_xlim(0, 1.15)
ax.set_title("PC clocks reduce technical variance across all four pairs", fontsize=11)
ax.legend(loc="lower right", fontsize=8)
f.text(0.5, 0.005, "All four 95% bootstrap CIs exclude 1 (no improvement).",
       ha="center", fontsize=8, style="italic")
f.tight_layout(rect=[0, 0.05, 1, 1]); f.savefig(f"{fig}/1_forest.png", dpi=150); plt.close(f)

# 2 -- paired error (|diff| per subject, original -> PC) -----------------------
f, axes = plt.subplots(1, 4, figsize=(12, 3.6), sharey=False)
for ax, p in zip(axes, PAIRS):
    o = diffs[diffs.clock == p].set_index("subject").absdiff
    pc = diffs[diffs.clock == "PC"+p].set_index("subject").absdiff
    for s in o.index:
        ax.plot([0, 1], [o[s], pc[s]], color="#999", lw=0.6, alpha=0.6, zorder=1)
    ax.scatter(np.zeros(len(o)), o, color=C_O, s=18, zorder=2)
    ax.scatter(np.ones(len(pc)), pc, color=C_P, s=18, zorder=2)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["original", "PC"])
    ax.set_title(p); ax.set_xlim(-0.3, 1.3)
    if ax is axes[0]: ax.set_ylabel("|replicate difference|  (years)")
f.suptitle("Per-subject technical error collapses under PC transformation", y=1.02)
f.tight_layout(); f.savefig(f"{fig}/2_paired_error.png", dpi=150, bbox_inches="tight"); plt.close(f)

# 3 -- Bland-Altman panels ----------------------------------------------------
f, axes = plt.subplots(2, 4, figsize=(13, 6), sharex="col", sharey="col")  # share y per clock -> PC row visibly compresses
for col, p in enumerate(PAIRS):
    for row, name in enumerate([p, "PC"+p]):
        ax = axes[row, col]; sub = diffs[diffs.clock == name]
        b = ba[ba.clock == name].iloc[0]
        ax.scatter(sub.pair_mean, sub.signed, s=16, color=(C_O if row == 0 else C_P))
        ax.axhline(b.batch_bias, color="k", lw=1)
        ax.axhline(b.loa_low, color="#c0392b", ls="--", lw=0.9)
        ax.axhline(b.loa_high, color="#c0392b", ls="--", lw=0.9)
        ax.axhline(0, color="#bbb", lw=0.6, zorder=0)
        ax.set_title(f"{name}  bias={b.batch_bias:+.2f}  LoA±{1.96*b.sd_diff:.1f}", fontsize=9)
        if col == 0: ax.set_ylabel("batch1 − batch2 (yr)")
        if row == 1: ax.set_xlabel("pair mean (yr)")
f.suptitle("Bland–Altman: small batch bias, dramatically tighter limits of agreement under PC", y=1.01)
f.tight_layout(); f.savefig(f"{fig}/3_bland_altman.png", dpi=150, bbox_inches="tight"); plt.close(f)

# 4 -- signal vs noise (the compression-objection figure) ---------------------
f, ax = plt.subplots(figsize=(6.4, 5.4))
x = comp.signal_preservation_ratio.values          # between-subject signal retained
ynr = 1 - comp.noise_ratio.values                  # within-subject noise removed
xs = np.linspace(0, 1, 50)
ax.plot(xs, 1 - xs, color="#c0392b", ls="--", lw=1.3,
        label="equal proportional shrinkage of signal and noise")
ax.fill_between(xs, 1 - xs, 1, color=C_P, alpha=0.06)
ax.scatter(x, ynr, color=C_P, s=90, zorder=3)
_offs = {"Horvath1": (9, 11), "Hannum": (9, -15), "PhenoAge": (10, -4), "GrimAge": (10, 6)}
for xi, yi, lab in zip(x, ynr, comp.pair):
    ax.annotate(lab, (xi, yi), textcoords="offset points",
                xytext=_offs.get(lab, (8, -4)), fontsize=9)
ax.set_xlabel("between-subject signal retained   Var(PC means) / Var(orig means)")
ax.set_ylabel("within-subject noise removed   1 − (PC/orig within-var)")
ax.set_xlim(0, 1), ax.set_ylim(0, 1)
ax.set_title("Denoising, not compression:\nnoise removed ≫ signal lost for every clock", fontsize=11)
ax.legend(loc="lower left", fontsize=8); f.tight_layout(); f.savefig(f"{fig}/4_signal_vs_noise.png", dpi=150); plt.close(f)

# 5 -- leave-one-subject-out --------------------------------------------------
f, ax = plt.subplots(figsize=(9, 3.8))
xo = np.arange(36)
for i, p in enumerate(PAIRS):
    sub = loso[loso.pair == p].reset_index()
    ax.plot(xo, sub.variance_ratio, marker="o", ms=3, lw=1, label=p)
ax.axhline(1.0, color="#c0392b", ls="--", lw=1.2)
ax.set_xlabel("omitted subject (index)"); ax.set_ylabel("variance ratio (PC/orig)")
ax.set_ylim(0, 1.05); ax.set_title("Leave-one-subject-out: every VR stays far below 1 (no verdict flips)")
ax.legend(ncol=4, fontsize=8, loc="upper center"); f.tight_layout(); f.savefig(f"{fig}/5_loso.png", dpi=150); plt.close(f)

print("wrote 5 figures to", fig)
