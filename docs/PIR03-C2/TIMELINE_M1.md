# Milestone 001 — Timeline

A one-page record of how the project actually evolved — not how it will later be
remembered. Kept for the team, not for publication.

```
IDEA
 │   "Can we reproduce Higgins-Chen?" → "Can we build an open benchmark?"
 │   → the real question: can we independently evaluate measurement reliability
 │     for any biomarker?
 ▼
ARCHITECTURE
 │   Scorer-agnostic design. reliage consumes a score table + replicate map — never
 │   betas or clock formulas. Two independent engines joined by one interface.
 ▼
PROTOCOL LOCK
 │   Analytic decisions frozen before results: 4 clock pairs, ICC(2,1) primary with
 │   absolute error, variance ratio as primary endpoint, per-clock units, evidence
 │   & claim gates. GrimAge locked to V1 in the manifest.
 ▼
FIRST SCORER
 │   methylCIPHER pinned @9e8c1e5. Discovered the committed R script targeted an
 │   OLDER API — rewrote against 0.2.0 (V1 GrimAge, capitalized pheno, PC via Zenodo
 │   reference). Fast-path Box data was dead → pivoted to canonical GEO.
 ▼
FIRST VERSIONED SCORE TABLE
 │   72 cross-batch replicate samples (36 pairs) reconstructed from GEO metadata;
 │   472k-CpG betas extracted (integrity-checked); scores.csv — 576 rows, per-row
 │   provenance. 4 all-NA CpGs dropped and recorded.
 ▼
FIRST RESULTS.md
 │   Primary endpoint: PC reduces within-subject technical variance, 4/4 pairs, all
 │   bootstrap CIs < 1. Gate 3 crossed — first real scientific result.
 ▼
ROBUSTNESS  (attempted refutations, not support)
 │   Compression audit → denoising, not compression (SPR 0.74–0.85, NR 0.036–0.135).
 │   Leave-one-subject-out → 0/144 flips. Outlier audit → cg00017157 dismissed.
 │   Bland–Altman → small bias, tighter LoA, no clear heteroscedasticity.
 ▼
TECHNICAL REPORT v0.1
 │   14 sections, 5 figures, evidence layers, calibrated claim, remaining-uncertainties
 │   table. PIPELINE.md + VST design notes alongside.
 ▼
SCIENTIFIC BASELINE TAG   v0.3.1-scientific-baseline  (frozen @61cacf0)
 │   Immutable snapshot of exactly what was known when the milestone was declared.
 │   Editorial polish committed AFTER, never into it.
 ▼
POSTMORTEM
     What worked, what was wrong, what nearly went wrong, what becomes standard.
     Written while fresh, as a template for future Foundry contributions.
```

**Elapsed:** conceived, executed, hardened, and frozen in a single working arc
(2026-07-24). Longest single step: the 9.7 GB GSE55763 download.

**The principle this milestone earned:**
> **Believe the result only after trying to disprove it.**

Every robustness analysis here was an attempt to show the effect *might not be real*.
The claim is what survived them. Worth institutionalizing across Foundry.

---
*Next: Experiment E2 — Implementation Sensitivity. New question, same everything else.*
