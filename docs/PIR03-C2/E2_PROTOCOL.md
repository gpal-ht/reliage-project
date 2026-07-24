# Experiment E2 — Implementation Sensitivity (PROTOCOL)

**Status:** protocol locked before results (per M1 discipline). Milestone 001 is a
frozen published-internal reference (`v0.3.1-scientific-baseline`) and is **not** touched
or reinterpreted by this experiment.

## Central question
**Does the scientific conclusion depend on the scoring implementation?**
Not "can we improve reliage?" Not "can we improve methylCIPHER?" — a different question.

## Hypotheses
- **Null (H0):** the observed reliability improvements are **implementation-dependent**.
- **Alternative (H1):** independent scoring implementations produce **materially similar
  scientific conclusions**.

Both "yes" and "no" are equally acceptable outcomes. The goal is truth, not confirmation.

## Design — a controlled single-variable experiment

**Independent variable (the ONLY thing that changes):** the scoring implementation.
```
methylCIPHER (M1)  →  pyaging (E2)
```

**Constants (must NOT change from M1):**
GSE55763 betas · replicate map · subject IDs · extraction pipeline · Versioned Score
Table schema · reliage analysis engine · bootstrap procedure (seed=0, 2000 iters) ·
robustness methods · reporting format.

**Method:**
1. Score the *same* `betas.csv` (72 replicate samples) with pyaging → `scores_pyaging.csv`,
   emitted in the **identical Versioned Score Table schema** as M1.
2. Run the **identical** reliage pipeline (`run_analysis` + `age_accel_icc` + `robustness`)
   on the pyaging table → `RESULTS_E2.md` and companion outputs, in a **separate** output
   directory (`datasets/GSE55763/out_E2/`) so M1's `out/` is untouched.
3. Compare the two implementations' scientific conclusions.

## Clock mapping (PINNED — pyaging 0.3.1, inspected 2026-07-25)

Inspected pyaging's installed catalog directly (not assumed). All 8 M1 clocks have a
pyaging equivalent, and — importantly — the GrimAge **variant matches**: pyaging exposes
both `grimage` (V1) and `grimage2` (V2), so M1's locked V1 maps cleanly with no variant
confound.

| M1 `clock_id` | `variant` | pyaging clock | note |
|---|---|---|---|
| Horvath1 | original | `horvath2013` | Horvath1 == Horvath 2013 pan-tissue |
| Horvath1 | PC | `pchorvath2013` | |
| Hannum | original | `hannum` | |
| Hannum | PC | `pchannum` | |
| PhenoAge | original | `dnamphenoage` | **DNAm Levine 2018 (513 CpGs)** — see correction below |
| PhenoAge | PC | `pcphenoage` | |
| GrimAge | original | `grimage` | **V1** — matches M1 (`grimage2` = V2, not used) |
| GrimAge | PC | `pcgrimage` | |

**Pre-results correction (2026-07-25):** the first pin used pyaging `phenoage`, but a
feature-inspection before scoring revealed `phenoage` is pyaging's **clinical** PhenoAge
(features: albumin, creatinine, glucose, …), *not* the DNAm clock. The methylation Levine
PhenoAge (513 CpGs, matches methylCIPHER `calcPhenoAge`) is pyaging **`dnamphenoage`**. Pin
corrected to `dnamphenoage` before any scores were produced — the "introspect, don't assume"
discipline caught it. Feature-overlap confirmed against our betas: Horvath1 353/353,
Hannum 71/71, DNAmPhenoAge 513/513, GrimAge(V1) 960/1032 (7% imputed ≈ M1 coverage),
PC clocks 78,464/78,464.

Notes:
- pyaging performs its **own** preprocessing + imputation per clock (KNN/mean, quantile
  normalization to a gold standard) — different from methylCIPHER's. This difference is
  *inside* the independent variable ("scoring implementation") and is exactly what E2 tests.
- `grimage`/`pcgrimage` require age + sex in `adata.obs` (as GrimAge does in methylCIPHER).
- `phenoage` vs `dnamphenoage`: `phenoage` is the canonical Levine clock; the assertion is
  validated post-hoc by score concordance against methylCIPHER `calcPhenoAge` (if wrong, the
  comparison surfaces it — which is E2's purpose).
- The pyaging score table uses the **same** `clock_id`/`variant` labels so the identical
  reliage pipeline ingests it unchanged.

## Prespecified comparison criteria (locked before results)

Primary is the **scientific conclusion**, not raw-score identity. For each overlapping clock
/ pair, compute and pre-commit thresholds:

| Comparison | Metric | "Concordant" if |
|---|---|---|
| Per-sample score agreement | Pearson r (72 samples) + bias + RMSD | r ≥ 0.90 (diagnostic; low r localizes divergence) |
| Subject ranking | Spearman ρ of subject means | ρ ≥ 0.85 |
| Reliability ranking | Spearman ρ of clocks ordered by ICC(2,1) | ρ ≥ 0.80 |
| Variance-ratio ordering | Spearman ρ of pairs ordered by VR | ρ ≥ 0.80 |
| **Per-pair verdict (PRIMARY)** | direction (VR<1) + supported/not | same in both implementations |

**Overall E2 verdict (prespecified):**
- **Implementation-robust (H1 supported)** if the per-pair verdicts and directions agree for
  all comparable pairs AND reliability/VR orderings are concordant (ρ ≥ 0.80).
- **Implementation-sensitive (H0 not rejected)** otherwise — with the divergence localized.

## Questions to answer
1. Do both implementations produce similar scores?
2. Do they preserve clock rankings?
3. Do they produce the same ICC ordering?
4. Do they produce the same variance-ratio ordering?
5. Do they produce the same scientific verdict?
6. If not, where do they diverge? → classify each divergence as:
   preprocessing · coefficients · imputation · implementation · missing CpGs · scaling · unknown.

## Deliverables
1. `E2_PROTOCOL.md` (this document)
2. `scores_pyaging.csv` — versioned score table (identical schema, pyaging provenance)
3. `RESULTS_E2.md` — identical reliage pipeline on the pyaging table
4. `IMPLEMENTATION_COMPARISON.md` — agreements · disagreements · explanations · remaining uncertainty
5. `POSTMORTEM_E2.md`

## Explicitly out of scope (belong to future milestones)
Do NOT: redesign reliage · redesign the Versioned Score Table · add new datasets · add
biological reliability · add new clocks · improve M1 figures · rewrite Milestone 001.

## Success criteria
E2 succeeds if it **honestly answers** whether the scientific conclusion depends on the
scoring implementation. A "yes" (implementation-sensitive) is as valuable as a "no"
(robust). Do not discuss v1.0 until E2 completes; after E2, evaluate Tier-3 formal
comparison and an independent third-party rerun before considering a stable public v1.0.

## Provenance (pyaging run — to fill at scoring time)
pyaging version · clock weights source/version · preprocessing · imputation policy · CpG
coverage per clock · exact clock IDs used · environment. Emitted alongside `scores_pyaging.csv`.
