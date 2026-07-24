# Robustness audit — GSE55763 PC-vs-original reliability

Purpose: the directional result (PC lowers within-subject technical variance, 4/4,
all CIs < 1) is not in doubt. This audit tests the one live objection —
**did PC improve reliability by genuinely denoising, or partly by compressing the
score range?** — plus influence, outliers, and batch structure.

CSVs: `robustness/`. Figures: `figures/`.

## 1 · Signal-preservation / compression audit  → answered: denoising, not compression

| Pair | Noise removed (1−VR) | Between-subj signal retained | Age r  orig → PC | Subject-rank ρ (orig,PC) |
|---|---|---|---|---|
| PhenoAge | **96.4%** | 0.79 | 0.831 → 0.827 | 0.874 |
| Horvath1 | 86.7% | 0.76 | 0.846 → 0.805 | 0.928 |
| Hannum | 86.5% | 0.74 | 0.929 → 0.832 | 0.954 |
| GrimAge | 87.2% | 0.85 | 0.855 → **0.915** | 0.958 |

Define **Signal Preservation Ratio** SPR = Var_between(PC)/Var_between(original) and
**Noise Ratio** NR = σ²_within(PC)/σ²_within(original) (= the primary variance ratio).
Pure compression gives SPR = NR; denoising gives NR ≪ SPR. Here SPR = 0.74–0.85 while
NR = 0.036–0.135.

**Interpretation.** Within-subject noise falls **87–96%** (NR) while between-subject
variation is **retained at 74–85%** (SPR) — the two do *not* shrink together. If PC were
mere range compression (multiply scores by a constant), within and between variance
would shrink by the same factor and ICC would be unchanged; instead noise is removed
**3–6× more** than signal is lost (Fig 4, all points far above the equal-shrinkage
line). Chronological-age association is preserved (and *improves* for GrimAge), and
subject ranking is preserved (Spearman **0.87–0.96**). There is a real but modest
between-subject compression (~15–26%); it does not explain the reliability gain.

## 2 · Leave-one-subject-out influence  → no verdict is fragile

| Pair | Full VR | LOO min–max | Verdict flips (VR ≥ 1) |
|---|---|---|---|
| Horvath1 | 0.133 | 0.104 – 0.147 | 0 / 36 |
| Hannum | 0.135 | 0.091 – 0.156 | 0 / 36 |
| PhenoAge | 0.036 | 0.031 – 0.039 | 0 / 36 |
| GrimAge | 0.128 | 0.116 – 0.144 | 0 / 36 |

**All 144 leave-one-out analyses keep VR far below 1 — no reversals.** Hannum's
wider *bootstrap* CI (0.058–0.329) is **not** driven by one influential subject:
removing any single subject leaves VR in [0.091, 0.156]. The width is small-cohort
(n=36) resampling variability, not a dominant outlier (Fig 5).

## 3 · Pair-level outlier audit

Subjects extreme (top-5 |replicate diff|) across **multiple** original clocks, and
their PC differences:

| Subject | Extreme in | Original |diff| (yr) | Same subject under PC (yr) |
|---|---|---|---|
| indiv_05 | 3 / 4 | Horvath1 4.60 · PhenoAge 7.45 · GrimAge 2.36 | 0.00 · 0.10 · 1.29 |
| indiv_09 | 2 / 4 | Horvath1 5.45 · Hannum 4.56 | 0.89 · 0.39 |
| indiv_35 | 2 / 4 | Horvath1 5.40 · PhenoAge 4.91 | 1.05 · 0.85 |
| indiv_24 | 2 / 4 | PhenoAge 8.58 · Horvath1 4.53 | 0.89 · 0.20 |

**Read (observation, not established mechanism):** the recurrence of the same
subjects among large discrepancies across multiple clocks is **consistent with shared
sample/array-level technical variation** (rather than clock-specific error), and PC
transformation reduces those discrepancies (indiv_05's PhenoAge replicate gap
7.45 → 0.10 yr). This is consistent with PC removing shared technical, rather than
biological, variation — but the recurrence pattern alone does not independently
establish the causal mechanism.

**`cg00017157`** (the value flagged in the raw display): **not a member of any of the
five clock CpG sets** (Horvath1/Hannum/PhenoAge/GrimAgeV1/PCClocks), so it has zero
effect on any score. In our 72 samples it is fully present (0 NA). The `0.067` seen
earlier was in a *non-cohort* sample. Conclusion: a display artifact of the raw matrix,
**not** a scoring or data-quality issue — no action needed.

## 4 · Bland–Altman diagnostics

| Clock | Batch bias (yr) | Limits of agreement | Proportional bias r(|diff|,mean) |
|---|---|---|---|
| Horvath1 → PC | −0.16 → +0.09 | ±5.4 → **±2.0** | 0.22 (ns) → 0.14 (ns) |
| Hannum → PC | +0.28 → −0.21 | ±3.6 → **±1.3** | 0.29 (p=.09) → 0.10 (ns) |
| PhenoAge → PC | **−0.53** → +0.01 | ±7.7 → **±1.5** | −0.14 (ns) → 0.19 (ns) |
| GrimAge → PC | −0.19 → −0.21 | ±2.5 → **±0.9** | 0.04 (ns) → −0.04 (ns) |

**Interpretation.** Systematic batch bias is small everywhere (|bias| ≤ 0.53 yr) and
essentially removed by PC (PhenoAge −0.53 → +0.01). Limits of agreement tighten
2.5–5× under PC. **No clear evidence of magnitude-dependent absolute error was
detected** — the correlation between |difference| and pair mean is non-significant for
all clocks (all p ≥ 0.09); this is a diagnostic, not a definitive test of
homoscedasticity. The variance-ratio endpoint (random within-subject residual) is not
confounded by the (small) batch drift.

## Figures
1. `figures/1_forest.png` — variance ratios + 95% CI, null at 1
2. `figures/2_paired_error.png` — per-subject |replicate diff|, original → PC
3. `figures/3_bland_altman.png` — B-A panels, original vs PC
4. `figures/4_signal_vs_noise.png` — between-subject signal retained vs within-subject noise removed (**the compression-objection figure**)
5. `figures/5_loso.png` — variance ratio by omitted subject

## Robustness-qualified scientific claim

> Across four prespecified epigenetic-clock pairs in 36 cross-batch technical
> replicates from GSE55763, PC-transformed clocks showed substantially lower
> within-subject technical variance than their originals (noise removed 87–96%;
> paired-bootstrap CIs excluded the null for all four; no leave-one-subject-out
> reversal), **while retaining the large majority of between-subject variation
> (74–85%), chronological-age association, and subject ranking (Spearman 0.87–0.96).**
> The gain reflects selective denoising rather than range compression: within-subject
> noise fell 3–6× more than between-subject signal.

Calibration note: this supports "more repeatable **while retaining useful
between-person signal**" — but **not** an unqualified "without loss of signal," since
between-subject variance is modestly compressed (~15–26%). State the retention
figures, not a zero-loss claim.
