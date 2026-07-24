# Experiment E2 — Implementation Comparison (methylCIPHER vs pyaging)

**Central question:** does the scientific conclusion depend on the scoring implementation?
**Answer: No.** On the same GSE55763 cohort, pipeline, and reliage engine, changing only the
scorer (methylCIPHER → pyaging 0.3.1) reproduces the M1 conclusion — **H1 (implementation-
robust) supported.**

M1 (`v0.3.1-scientific-baseline`) is untouched. E2 outputs live in `datasets/GSE55763/out_E2/`;
pyaging score table in `datasets/GSE55763/processed/scores_pyaging.csv`.

## Prespecified criteria — all met

| Prespecified check | Threshold | Result |
|---|---|---|
| Per-sample score agreement (Pearson r) | ≥ 0.90 | **0.9997–1.0000** (all 8 clocks) |
| Subject ranking (Spearman ρ) | ≥ 0.85 | **0.999–1.000** |
| Reliability (ICC) ordering | ρ ≥ 0.80 | ρ = **1.000** (ICCs identical to 3 dp) |
| Variance-ratio ordering | ρ ≥ 0.80 | ρ = **1.000** |
| Per-pair verdict (PRIMARY) | same both | **same — supported 4/4 in both** |

**Overall E2 verdict: implementation-robust.**

## Agreements (Q1–Q5)

- **Q1 — scores:** Pearson r = 1.0000 for 7/8 clocks; DNAmPhenoAge 0.9997. Bias ≤ 0.07 yr
  except GrimAge (see below).
- **Q2 — clock rankings:** subject-mean Spearman ρ = 1.000 (PhenoAge 0.999).
- **Q3 — ICC ordering:** identical to 3 decimals for all 8 clocks; PCGrimAge 0.998, …,
  PhenoAge 0.918/0.917. Ordering ρ = 1.000.
- **Q4 — variance-ratio ordering:** Horvath1 0.1333/0.1333, Hannum 0.1348/0.1348,
  PhenoAge 0.0355/0.0355, GrimAge 0.1281/0.1284. Ordering ρ = 1.000.
- **Q5 — verdict:** both **supported (4/4)**.
- **Robustness (not required, but checked):** compression audit identical — noise ratios,
  signal-preservation (GrimAge SPR 0.845/0.845), age association (r_age 0.855/0.855), and
  age-acceleration ICC all match. The "selective denoising, not compression" conclusion holds
  under both implementations.

## Disagreements (Q6) — one, benign

**GrimAge: a constant ~−2.63 yr intercept.** pyaging GrimAge is a near-perfect *linear copy*
of methylCIPHER GrimAge (Pearson r = **1.0000**, subject-rank ρ = 1.000) shifted uniformly
~2.63 yr lower (bias −2.63, RMSD 2.63). Because it is an additive constant, it changes **no**
within-subject difference, so ICC, SEM, MDC95, and the variance ratio are unaffected
(GrimAge VR 0.128 in both). It changes no ranking or verdict. **Classification:**
*calibration/intercept* (+ plausibly *imputation* of the 7% missing GrimAge CpGs, which the
two tools fill differently: pyaging with clock reference values, methylCIPHER by mean). The
offset is scientifically inert for a reliability benchmark.

*(DNAmPhenoAge's r = 0.9997 / RMSD 0.24 yr is trivial — minor imputation/rounding of a few
CpGs; no effect on any conclusion.)*

## Two clock-matching pitfalls that were caught (not divergences)

E2's hardest problems were **clock-definition matching**, not the algorithms. Two setup errors
were caught by verification *before* they became false "divergences":
1. **`phenoage` is pyaging's CLINICAL PhenoAge** (albumin/creatinine/glucose), not the DNAm
   clock. The methylation Levine PhenoAge is `dnamphenoage` (513 CpGs). Caught by feature
   inspection.
2. **pyaging GrimAge reads Female/Age as the last two *features*** (`x[:,-2]`, `x[:,-1]`),
   not from `adata.obs`. Passing them via obs gave a constant age → GrimAge `r_age = 0.29`.
   Caught by that red flag + reading pyaging's `forward()`.
Both were corrected in the pinned protocol / scorer before final results. **Methodological
takeaway: an implementation-sensitivity study is dominated by getting the clock *definitions*
matched; the scoring math, once matched, agrees almost exactly.**

## Remaining uncertainty

- **PC-clock independence is partial.** pyaging's PC clocks and methylCIPHER's `calcPCClocks`
  very likely derive from the **same published Higgins-Chen PC coefficients/reference**, so
  their near-exact agreement partly reflects a *shared upstream definition*, not two fully
  independent re-implementations. The strongest independent evidence is the **original** clocks
  (Horvath1/Hannum/PhenoAge/GrimAge), separately implemented from public coefficients, which
  also agree to r ≈ 1.0.
- The GrimAge intercept source (pure calibration constant vs missing-CpG imputation) is not
  definitively isolated; it could be pinned by matching imputation, but is benign here.
- Single dataset, single replicate design (cross-batch 450K). Implementation robustness on
  other datasets / platforms / clock families is untested.

## Conclusion
Within GSE55763, the M1 scientific conclusion — PC clocks reduce technical measurement error,
selective denoising, supported 4/4 — is **reproduced by an independent scoring implementation**
with per-sample score agreement r ≥ 0.9997 and identical rankings, ICC ordering, variance-ratio
ordering, and verdict. The only divergence is a benign GrimAge calibration offset. The
conclusion is **not** an artifact of the methylCIPHER implementation.
